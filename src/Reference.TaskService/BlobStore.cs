using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;

namespace NativeWeave.Reference.TaskService;

internal sealed record UploadManifest(long Version, string OperationId, string Tenant, string Principal, string ItemId,
    string RequestKey, long ExpectedVersion, string? ContentHash, long ContentLength, string State, long CreatedAt);
internal sealed record RecoveryManifest(long Version, string OperationId, string Scope, string RequestKey, string RequestHash, long CreatedAt);
internal sealed record MaintenancePosition(long CompletedAt, string Id);
internal sealed record MaintenanceProgress(long Version, MaintenancePosition? Outbox, MaintenancePosition? Operations, string? Recovery, string? Uploads);

/// <summary>One process owns this finite local filesystem profile; blobs precede database references.</summary>
internal sealed class BlobStore : IDisposable
{
    internal const long MaximumAttachment = 64L * 1024 * 1024;
    private const long MaintenanceReserve = 8192; // Complete and temporary progress records, each bounded to 4KiB.
    private readonly ServiceConfiguration _configuration;
    private readonly FileStream _processLock;
    private readonly object _gate = new();
    private readonly HashSet<string> _active = new(StringComparer.Ordinal);
    private long _reserved;
    internal string Root { get; }
    internal string Staging { get; }
    internal string Blobs { get; }
    internal string Recovery { get; }

    internal BlobStore(ServiceConfiguration configuration)
    {
        _configuration = configuration; Root = Path.GetFullPath(configuration.BlobDirectory);
        Directory.CreateDirectory(Root);
        _processLock = new FileStream(Path.Combine(Root, "owner.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
        Staging = Path.Combine(Root, "staging"); Blobs = Path.Combine(Root, "blobs"); Recovery = Path.Combine(Root, "recovery");
        Directory.CreateDirectory(Staging); Directory.CreateDirectory(Blobs); Directory.CreateDirectory(Recovery);
        DurableDirectory.Flush(Root);
    }

    internal UploadLease Begin(AuthIdentity identity, string itemId, string key, long version, long length)
    {
        if (length < 0 || length > MaximumAttachment) throw new ApplicationProblem(413, "attachment_limit");
        string operation = Guid.NewGuid().ToString("D");
        long reservation = checked(length + 16_384);
        lock (_gate)
        {
            long stored = StoredBytes();
            if (_active.Count >= _configuration.MaxUploads || stored + _reserved + reservation + MaintenanceReserve > _configuration.MaxBlobBytes ||
                Directory.EnumerateFiles(Staging, "*.json").Take(8192).Count() >= 8192)
                throw new ApplicationProblem(503, "upload_capacity");
            _active.Add(operation); _reserved += reservation;
        }
        var manifest = new UploadManifest(1, operation, identity.Tenant, identity.Principal, itemId, key, version, null, length, "uploading", TaskService.Now());
        try { WriteManifest(manifest); return new(this, manifest, reservation); }
        catch { Release(operation, reservation); throw; }
    }

    internal FileStream Open(Attachment attachment)
    {
        string path = BlobPath(attachment.ContentHash);
        var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read, 32_768, FileOptions.Asynchronous | FileOptions.SequentialScan);
        if (stream.Length != attachment.ContentLength) { stream.Dispose(); throw new InvalidOperationException("A database reference does not match the immutable blob."); }
        return stream;
    }

    internal IReadOnlyList<UploadManifest> Manifests()
    { lock (_gate) return Directory.EnumerateFiles(Staging, "*.json").Select(ReadManifest).ToArray(); }

    internal IReadOnlyList<RecoveryManifest> RecoveryManifests()
    {
        lock (_gate)
        {
            return Directory.EnumerateFiles(Recovery, "*.json").Select(path =>
            {
                if (new FileInfo(path).Length > 8192) throw new InvalidOperationException("Recovery record is too large.");
                var value = JsonSerializer.Deserialize(File.ReadAllBytes(path), AppJson.Default.RecoveryManifest)
                    ?? throw new InvalidOperationException("Invalid recovery record.");
                if (value.Version != 1 || Path.GetFileName(path) != Canonical.Id(value.OperationId) + ".json")
                    throw new InvalidOperationException("Recovery identity mismatch.");
                return value;
            }).ToArray();
        }
    }

    internal HashSet<string> ProtectedOperations()
    {
        lock (_gate) return Manifests().Where(x => x.ContentHash is not null || _active.Contains(x.OperationId)).Select(x => x.OperationId)
            .Concat(Directory.EnumerateFiles(Recovery, "*.json").Select(path => Canonical.Id(Path.GetFileNameWithoutExtension(path)))).ToHashSet(StringComparer.Ordinal);
    }

    internal void ProtectCommit(OperationResult operation)
    {
        lock (_gate)
        {
            if (Directory.EnumerateFiles(Recovery, "*.json").Take(8192).Count() >= 8192 ||
                StoredBytes() + _reserved + 8192 + MaintenanceReserve > _configuration.MaxBlobBytes)
                throw new ApplicationProblem(503, "recovery_capacity");
            var manifest = new RecoveryManifest(1, operation.OperationId, operation.Scope, operation.RequestKey, operation.RequestHash, operation.CompletedAt);
            string path = Path.Combine(Recovery, operation.OperationId + ".json");
            byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(manifest, AppJson.Default.RecoveryManifest);
            using (var file = new FileStream(path + ".new", FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
            { file.Write(bytes); file.Flush(true); }
            File.Move(path + ".new", path);
            DurableDirectory.Flush(Recovery);
        }
    }

    internal void ConfirmCommit(string operationId)
    {
        try
        {
            lock (_gate)
            {
                string path = Path.Combine(Recovery, Canonical.Id(operationId) + ".json");
                File.Delete(path); File.Delete(path + ".new"); DurableDirectory.Flush(Recovery);
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException) { Console.Error.WriteLine("confirmed_commit_protection_cleanup_pending"); }
    }

    internal void ConfirmRecoveredUpload(string operationId)
    {
        try
        {
            lock (_gate)
            {
                string path = ManifestPath(operationId);
                File.Delete(path); File.Delete(path + ".new"); DurableDirectory.Flush(Staging);
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException) { Console.Error.WriteLine("confirmed_upload_protection_cleanup_pending"); }
    }

    internal async Task<(int Blobs, int Staging)> CollectAsync(Func<string, CancellationToken, Task<bool>> referenced, CancellationToken token)
    {
        long cutoff = TaskService.Now() - checked(_configuration.OrphanGraceSeconds * 1000L);
        var manifests = Manifests();
        var protectedHashes = manifests.Where(manifest => manifest.ContentHash is not null).Select(manifest => manifest.ContentHash!).ToHashSet(StringComparer.Ordinal);
        int deletedStaging = 0; int deletedBlobs = 0;
        foreach (var manifest in manifests)
        {
            token.ThrowIfCancellationRequested();
            if (manifest.ContentHash is not null || manifest.CreatedAt >= cutoff || IsActive(manifest.OperationId)) continue;
            // An upload with no recorded content hash cannot have entered blob rename or database binding.
            string part = PartPath(manifest.OperationId);
            if (File.Exists(part)) File.Delete(part);
            File.Delete(ManifestPath(manifest.OperationId)); deletedStaging++;
        }
        foreach (string path in Directory.EnumerateFiles(Staging).Where(path => path.EndsWith(".part", StringComparison.Ordinal) || path.EndsWith(".json.new", StringComparison.Ordinal)))
        {
            string fileName = Path.GetFileName(path);
            if (fileName.Length < 36) continue;
            string id = fileName[..36];
            if (!Guid.TryParseExact(id, "D", out _) || IsActive(id) || path.EndsWith(".part", StringComparison.Ordinal) && File.Exists(ManifestPath(id)) ||
                new DateTimeOffset(File.GetLastWriteTimeUtc(path)).ToUnixTimeMilliseconds() >= cutoff) continue;
            File.Delete(path); deletedStaging++;
        }
        foreach (string path in Directory.EnumerateFiles(Recovery, "*.json.new"))
        {
            token.ThrowIfCancellationRequested();
            // A temporary record cannot authorize COMMIT: publication and directory fsync precede dispatch.
            if (new DateTimeOffset(File.GetLastWriteTimeUtc(path)).ToUnixTimeMilliseconds() >= cutoff) continue;
            File.Delete(path); deletedStaging++;
        }
        foreach (string path in Directory.EnumerateFiles(Blobs))
        {
            token.ThrowIfCancellationRequested();
            string hash = Path.GetFileName(path);
            if (!ValidHash(hash) || protectedHashes.Contains(hash) || new DateTimeOffset(File.GetLastWriteTimeUtc(path)).ToUnixTimeMilliseconds() >= cutoff) continue;
            if (await referenced(hash, token).ConfigureAwait(false)) continue;
            // One process owns Root. Active uploads always persist their hash before a rename.
            lock (_gate)
            {
                if (Manifests().Any(manifest => manifest.ContentHash == hash)) continue;
                try { File.Delete(path); deletedBlobs++; }
                catch (IOException) { /* A failed local deletion remains eligible for a later collection. */ }
            }
        }
        DurableDirectory.Flush(Staging); DurableDirectory.Flush(Blobs); DurableDirectory.Flush(Recovery);
        return (deletedBlobs, deletedStaging);
    }

    private bool IsActive(string id) { lock (_gate) return _active.Contains(id); }
    private string ManifestPath(string id) => Path.Combine(Staging, Canonical.Id(id) + ".json");
    private string PartPath(string id) => Path.Combine(Staging, Canonical.Id(id) + ".part");
    private string BlobPath(string hash) => ValidHash(hash) ? Path.Combine(Blobs, hash) : throw new InvalidOperationException("Invalid stored content hash.");
    private static bool ValidHash(string hash) => hash.Length == 64 && hash.All(c => char.IsAsciiDigit(c) || c is >= 'a' and <= 'f');

    private UploadManifest ReadManifest(string path)
    {
        if (new FileInfo(path).Length > 8192) throw new InvalidOperationException("Recovery manifest exceeds its bound.");
        var value = JsonSerializer.Deserialize(File.ReadAllBytes(path), AppJson.Default.UploadManifest) ?? throw new InvalidOperationException("Invalid recovery manifest.");
        if (value.Version != 1 || Path.GetFileName(path) != Canonical.Id(value.OperationId) + ".json" || value.ContentLength is < 0 or > MaximumAttachment ||
            value.ContentHash is not null && !ValidHash(value.ContentHash)) throw new InvalidOperationException("Invalid recovery manifest identity.");
        return value;
    }

    private void WriteManifest(UploadManifest value)
    {
        byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(value, AppJson.Default.UploadManifest);
        if (bytes.Length > 8192) throw new InvalidOperationException("Recovery manifest exceeds its bound.");
        string path = ManifestPath(value.OperationId); string temporary = path + ".new";
        lock (_gate)
        {
            using (var stream = new FileStream(temporary, FileMode.Create, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
            { stream.Write(bytes); stream.Flush(true); }
            File.Move(temporary, path, true); DurableDirectory.Flush(Staging);
        }
    }

    internal MaintenanceProgress ReadMaintenanceProgress()
    {
        string path = Path.Combine(Root, "maintenance.json");
        if (!File.Exists(path)) return new(1, null, null, null, null);
        if (new FileInfo(path).Length > 4096) throw new InvalidOperationException("Maintenance progress exceeds its bound.");
        var value = JsonSerializer.Deserialize(File.ReadAllBytes(path), AppJson.Default.MaintenanceProgress)
            ?? throw new InvalidOperationException("Invalid maintenance progress.");
        if (value.Version != 1) throw new InvalidOperationException("Unsupported maintenance progress version.");
        return value;
    }

    internal void WriteMaintenanceProgress(MaintenanceProgress value)
    {
        byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(value, AppJson.Default.MaintenanceProgress);
        if (bytes.Length > 4096) throw new InvalidOperationException("Maintenance progress exceeds its bound.");
        string path = Path.Combine(Root, "maintenance.json");
        lock (_gate)
        {
            using (var file = new FileStream(path + ".new", FileMode.Create, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
            { file.Write(bytes); file.Flush(true); }
            File.Move(path + ".new", path, true); DurableDirectory.Flush(Root);
        }
    }

    private long StoredBytes()
    {
        long total = 0;
        foreach (string path in Directory.EnumerateFiles(Root, "*", SearchOption.AllDirectories))
        {
            try { total = checked(total + new FileInfo(path).Length); }
            catch (FileNotFoundException) { /* A retired temporary contributes no retained bytes. */ }
            catch (DirectoryNotFoundException) { /* A concurrent local deletion contributes no retained bytes. */ }
        }
        // Active upload bytes are additionally covered in full by _reserved, including not-yet-written bytes.
        return total;
    }

    private void Release(string operation, long reservation)
    { lock (_gate) { if (!_active.Remove(operation)) throw new InvalidOperationException("Upload reservation released twice."); _reserved -= reservation; } }

    public void Dispose() => _processLock.Dispose();

    internal sealed class UploadLease : IAsyncDisposable
    {
        private readonly BlobStore _owner;
        private readonly long _reservation;
        private bool _released;
        private bool _databaseBinding;
        internal UploadManifest Manifest { get; private set; }
        internal UploadLease(BlobStore owner, UploadManifest manifest, long reservation) { _owner = owner; Manifest = manifest; _reservation = reservation; }
        internal void BeginDatabaseBinding() => _databaseBinding = true;

        internal async Task StageAsync(Stream input, CancellationToken token)
        {
            string part = _owner.PartPath(Manifest.OperationId);
            string hash;
            await using (var file = new FileStream(part, FileMode.CreateNew, FileAccess.Write, FileShare.None, 32_768, FileOptions.Asynchronous | FileOptions.SequentialScan))
            using (var digest = IncrementalHash.CreateHash(HashAlgorithmName.SHA256))
            {
                var sink = new HashingSink(file, digest, Manifest.ContentLength);
                // Stream.CopyToAsync overrides may ignore the requested buffer size (for example MemoryStream).
                // Preserve the fixture's existing 32KiB bound for every ordinary application Stream.
                byte[] buffer = new byte[32_768];
                int read;
                while ((read = await input.ReadAsync(buffer, token).ConfigureAwait(false)) != 0)
                    await sink.WriteAsync(buffer.AsMemory(0, read), token).ConfigureAwait(false);
                if (sink.Count != Manifest.ContentLength) throw new ApplicationProblem(400, "attachment_length_mismatch");
                await file.FlushAsync(token).ConfigureAwait(false); file.Flush(true);
                hash = Convert.ToHexStringLower(digest.GetHashAndReset());
            }
            // Persist the recovery hash before rename; a crash at every later point keeps the blob protected.
            Manifest = Manifest with { ContentHash = hash, State = "renaming" };
            _owner.WriteManifest(Manifest);
            lock (_owner._gate)
            {
                string destination = _owner.BlobPath(hash);
                if (File.Exists(destination))
                {
                    if (new FileInfo(destination).Length != Manifest.ContentLength) throw new InvalidOperationException("Immutable content identity collision.");
                    using var existing = File.OpenRead(destination);
                    if (Convert.ToHexStringLower(SHA256.HashData(existing)) != hash) throw new InvalidOperationException("Immutable blob corruption.");
                    File.Delete(part);
                }
                else File.Move(part, destination);
                DurableDirectory.Flush(_owner.Blobs); DurableDirectory.Flush(_owner.Staging);
            }
            Manifest = Manifest with { State = "prepared" }; _owner.WriteManifest(Manifest);
        }

        internal void Complete(Replay result)
        {
            if (result.Status == 503) { Manifest = Manifest with { State = "recovery" }; _owner.WriteManifest(Manifest); }
            else _owner.ConfirmRecoveredUpload(Manifest.OperationId);
        }

        public ValueTask DisposeAsync()
        {
            if (_released) return ValueTask.CompletedTask;
            _released = true;
            try
            {
                if (Manifest.ContentHash is null)
                {
                    // No database operation was admitted; the incomplete stage remains visible for grace cleanup.
                    Manifest = Manifest with { State = "abandoned" }; _owner.WriteManifest(Manifest);
                }
                else if (!_databaseBinding) _owner.ConfirmRecoveredUpload(Manifest.OperationId);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException) { Console.Error.WriteLine("upload_manifest_cleanup_pending"); }
            finally { _owner.Release(Manifest.OperationId, _reservation); }
            return ValueTask.CompletedTask;
        }
    }

    private sealed class HashingSink(FileStream file, IncrementalHash hash, long maximum) : Stream
    {
        internal long Count { get; private set; }
        public override bool CanRead => false;
        public override bool CanSeek => false;
        public override bool CanWrite => true;
        public override long Length => Count;
        public override long Position { get => Count; set => throw new NotSupportedException(); }
        public override async ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default)
        {
            if (buffer.Length > 32_768 || buffer.Length > maximum - Count) throw new ApplicationProblem(413, "attachment_limit");
            await file.WriteAsync(buffer, cancellationToken).ConfigureAwait(false); hash.AppendData(buffer.Span); Count += buffer.Length;
        }
        public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken) => WriteAsync(buffer.AsMemory(offset, count), cancellationToken).AsTask();
        public override void Flush() => file.Flush();
        public override Task FlushAsync(CancellationToken cancellationToken) => file.FlushAsync(cancellationToken);
        public override int Read(byte[] buffer, int offset, int count) => throw new NotSupportedException();
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();
    }
}

/// <summary>Platform-local directory durability after immutable renames; no claim of power-loss testing.</summary>
internal static partial class DurableDirectory
{
    internal static void Flush(string directory)
    {
        if (OperatingSystem.IsLinux())
        {
            int descriptor = Open(directory, 0x10000 | 0x80000); // O_DIRECTORY | O_CLOEXEC, read-only.
            if (descriptor < 0) throw new IOException("Directory open failed for durability.");
            try { if (Fsync(descriptor) != 0) throw new IOException("Directory fsync failed."); }
            finally { _ = Close(descriptor); }
        }
        else throw new PlatformNotSupportedException("The reference blob persistence profile is implemented and validated for Linux only.");
    }

    [LibraryImport("libc", EntryPoint = "open", StringMarshalling = StringMarshalling.Utf8, SetLastError = true)] private static partial int Open(string path, int flags);
    [LibraryImport("libc", EntryPoint = "fsync", SetLastError = true)] private static partial int Fsync(int fd);
    [LibraryImport("libc", EntryPoint = "close")] private static partial int Close(int fd);
}
