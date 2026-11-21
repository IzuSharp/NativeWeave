using System.Buffers.Binary;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;
using NativeWeave.Database.Sqlite;
using NativeWeave.Sqlite.Samples;

if (args.Contains("--aot") && RuntimeFeature.IsDynamicCodeSupported)
    throw new InvalidOperationException("The explicit Native AOT row must execute a native executable.");
string root = Path.GetFullPath(Environment.GetEnvironmentVariable("NATIVEWEAVE_B03_TEST_ROOT") ?? Path.Combine(Path.GetTempPath(), "nw-b03-" + Guid.NewGuid().ToString("N")));
Directory.CreateDirectory(root);
int assertions = 0;
void Check(bool value, string message)
{
    assertions++;
    if (!value) throw new InvalidOperationException(message);
}
void Throws<T>(Action action) where T : Exception
{
    assertions++;
    try { action(); } catch (T) { return; }
    throw new InvalidOperationException("Expected " + typeof(T).Name);
}

var defaults = SqliteExamples.Minimal();
Check(defaults.Mode == SqliteOpenMode.ReadWriteCreate && defaults.JournalMode == SqliteJournalMode.Wal && defaults.Synchronous == SqliteSynchronousMode.Full && defaults.BeginMode == SqliteBeginMode.Deferred && defaults.ForeignKeys && defaults.BusyTimeout == TimeSpan.FromSeconds(5), "exact SQLite defaults");
byte[] record = SqliteConfiguration.Snapshot(defaults);
Check(record.Length == 140 && BinaryPrimitives.ReadUInt16LittleEndian(record.AsSpan(2)) == 9, "canonical kind9 envelope");
for (int field = 0; field < 6; field++)
{
    int header = 16 + field * 16;
    Check(BinaryPrimitives.ReadUInt16LittleEndian(record.AsSpan(header)) == field + 1, "exact option field identity");
    Check(BinaryPrimitives.ReadUInt16LittleEndian(record.AsSpan(header + 2)) == (field == 4 ? 2 : 1), "exact option field type");
}
Check(BinaryPrimitives.ReadUInt64LittleEndian(record.AsSpan(128)) == 5_000_000_000UL, "nanosecond timeout encoding");
defaults.ForeignKeys = false;
Check(BinaryPrimitives.ReadUInt32LittleEndian(record.AsSpan(136)) == 1, "owned immutable-at-use option snapshot");
Probe(Path.Combine(root, "default.db"), record, (5000UL << 32) | (2UL << 8) | (1UL << 16));

var advanced = SqliteExamples.Advanced();
Probe(Path.Combine(root, "advanced.db"), SqliteConfiguration.Snapshot(advanced), (25UL << 32) | 1UL | (1UL << 8));
var memory = SqliteExamples.PrivateMemory();
Probe(":memory:", SqliteConfiguration.Snapshot(memory), (5000UL << 32) | 2UL | (2UL << 8) | (1UL << 16));
Throws<ArgumentNullException>(() => SqliteConfiguration.Snapshot(null!));
Throws<ArgumentOutOfRangeException>(() => SqliteConfiguration.Snapshot(new() { Mode = (SqliteOpenMode)99 }));
Throws<ArgumentOutOfRangeException>(() => SqliteConfiguration.Snapshot(new() { BusyTimeout = TimeSpan.FromTicks(1) }));
Throws<ArgumentOutOfRangeException>(() => SqliteConfiguration.Snapshot(new() { BusyTimeout = TimeSpan.FromMilliseconds(-1) }));
Throws<ArgumentOutOfRangeException>(() => SqliteConfiguration.Snapshot(new() { BusyTimeout = TimeSpan.FromDays(30) }));
Throws<ArgumentException>(() => SqliteConfiguration.Snapshot(new() { Mode = SqliteOpenMode.Memory }));
byte[] malformed = (byte[])record.Clone(); malformed[136] = 2;
Check(Native.Probe(Path.Combine(root, "invalid.db"), malformed, out _) == 1 && !File.Exists(Path.Combine(root, "invalid.db")), "native rejects noncanonical Boolean before file I/O");

uint runtimes = Native.RuntimeCount();
assertions += ProviderProfileChecks.Component("sqlite", Environment.GetEnvironmentVariable("NW_SQLITE_COMPONENT_ASSET"));
assertions += ProviderProfileChecks.Host(() => SqliteDataSource.Engine, "sqlite");
Check(Native.RuntimeCount() == runtimes, "metadata/inspect starts no fixture runtime");
Check(Native.RunSuite(Path.Combine(root, "native-suite")) == 0, "actual SQLite/B05 fourteen-scenario suite");
Check(Native.RuntimeCount() == runtimes + 1, "one explicit test suite runtime");
Console.WriteLine($"PASS B03 {assertions} assertions; actual SQLite 3.51.3; 14 native provider/B05 scenarios; NativeAOT={!RuntimeFeature.IsDynamicCodeSupported}.");

void Probe(string path, byte[] options, ulong expected)
{
    Check(Native.Probe(path, options, out ulong actual) == 0, "actual native option probe succeeds");
    Check(actual == expected, "actual independent SQLite PRAGMA oracle matches managed settings");
}

internal static partial class Native
{
    internal static unsafe uint Probe(string path, byte[] options, out ulong observed)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(path);
        fixed (byte* p = bytes)
        fixed (byte* o = options)
            return ProbeOptions(p, (uint)bytes.Length, o, (uint)options.Length, out observed);
    }
    internal static unsafe uint RunSuite(string path)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(path);
        fixed (byte* p = bytes) return Run(p, (uint)bytes.Length);
    }
    [LibraryImport("nativeweave_sqlite_fixture", EntryPoint = "nw_b03_runtime_count")]
    internal static partial uint RuntimeCount();
    [LibraryImport("nativeweave_sqlite_fixture", EntryPoint = "nw_b03_run_suite")]
    private static unsafe partial uint Run(byte* path, uint length);
    [LibraryImport("nativeweave_sqlite_fixture", EntryPoint = "nw_b03_probe_options")]
    private static unsafe partial uint ProbeOptions(byte* path, uint pathLength, byte* record, uint recordLength, out ulong observed);
}
