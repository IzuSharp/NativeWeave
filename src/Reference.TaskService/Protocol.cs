using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace NativeWeave.Reference.TaskService;

/// <summary>Internal database application values; these types introduce no framework API or transport.</summary>
internal sealed record CreateItem(string Title);
internal sealed record ItemView(string ItemId, string Title, long CreatedAt, long Version);
internal sealed record CreatedItem(long ResponseVersion, string OperationId, string ItemId, string Title, long CreatedAt, long Version);
internal sealed record AttachedItem(long ResponseVersion, string OperationId, string ItemId, string ContentHash, long ContentLength, long Version);
internal sealed record ItemPage(ItemView[] Items, string? NextCursor);
internal sealed record Problem(string Code, string? OperationId = null, string? RecoveryUri = null, ulong? CorrelationId = null);
internal sealed record AuthIdentity(string Tenant, string Principal, bool CanWrite);
internal sealed record Replay(int Status, byte[] Bytes, string OperationId, string? ProviderCode = null);
internal sealed class ApplicationProblem(int status, string code) : Exception(code)
{
    internal int Status { get; } = status;
    internal string Code { get; } = code;
}

[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
    RespectNullableAnnotations = true, RespectRequiredConstructorParameters = true)]
[JsonSerializable(typeof(CreateItem)), JsonSerializable(typeof(CreatedItem)), JsonSerializable(typeof(AttachedItem))]
[JsonSerializable(typeof(ItemPage)), JsonSerializable(typeof(Problem)), JsonSerializable(typeof(ServiceConfiguration))]
[JsonSerializable(typeof(UploadManifest)), JsonSerializable(typeof(RecoveryManifest)), JsonSerializable(typeof(MaintenanceReport))]
[JsonSerializable(typeof(FixtureReceipt)), JsonSerializable(typeof(MaintenanceProgress))]
internal partial class AppJson : JsonSerializerContext { }

internal sealed record MaintenanceReport(int DeletedOutbox, int DeletedOperations, int DeletedBlobs, int DeletedStaging);
internal sealed record FixtureReply(int Status, string BytesHex, string OperationId, string? ErrorKind = null, string? ProviderCode = null);
internal sealed record FixtureReceipt(string Case, bool DynamicCodeSupported, List<FixtureReply> Replies,
    Dictionary<string, string> Checks, bool DatabaseResourcesReleased, bool ConsumerResourcesReleased);

/// <summary>Fixed v1 byte framing, independent of JSON serialization, locale and Unicode normalization.</summary>
internal static class Canonical
{
    internal const string CreateSemantic = "POST /v1/items";
    internal const string AttachSemantic = "PUT /v1/items/{id}/attachment";
    internal static readonly UTF8Encoding Utf8 = new(false, true);

    internal static byte[] Frame(string[] fields, params long[] integers)
    {
        int length = checked(4 + fields.Sum(field => checked(4 + Utf8.GetByteCount(field))) + 8 * integers.Length);
        byte[] bytes = new byte[length];
        BinaryPrimitives.WriteUInt32LittleEndian(bytes, 1);
        int offset = 4;
        foreach (string field in fields)
        {
            int count = Utf8.GetByteCount(field);
            BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(offset), checked((uint)count));
            offset += 4; offset += Utf8.GetBytes(field, bytes.AsSpan(offset));
        }
        foreach (long value in integers) { BinaryPrimitives.WriteInt64LittleEndian(bytes.AsSpan(offset), value); offset += 8; }
        return bytes;
    }

    internal static string Hash(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    internal static string Scope(AuthIdentity identity, string semantic) => Hash(Frame(["scope.v1", identity.Tenant, identity.Principal, semantic]));
    internal static string CreateHash(AuthIdentity identity, string title) => Hash(Frame([CreateSemantic, identity.Tenant, identity.Principal, title]));
    internal static string AttachmentHash(AuthIdentity identity, string item, string hash, long length, long version) =>
        Hash(Frame([AttachSemantic, identity.Tenant, identity.Principal, item, hash], length, version));

    internal static void ValidateTitle(string title)
    {
        if (string.IsNullOrWhiteSpace(title) || Utf8.GetByteCount(title) > 1024 || title.Contains('\0'))
            throw new ApplicationProblem(400, "invalid_title");
    }

    internal static string Key(string? key)
    {
        if (key is null || key.Length is < 1 or > 128 || key.Any(c => c < '!' || c > '~'))
            throw new ApplicationProblem(400, "invalid_idempotency_key");
        return key;
    }

    internal static string Id(string value) => Guid.TryParseExact(value, "D", out var id) && id.ToString("D") == value
        ? value : throw new ApplicationProblem(400, "invalid_identifier");

    internal static void WriteGoldenVectors(Stream output)
    {
        using Utf8JsonWriter writer = new(output, new() { Indented = true });
        writer.WriteStartObject(); writer.WriteNumber("version", 1); writer.WriteStartArray("create");
        (string Name, string Tenant, string Principal, string Title)[] inputs =
        [("ascii", "tenant-a", "alice", "hello"), ("unicode", "tenant-a", "alice", "世界 🦀"),
         ("composed", "tenant-a", "alice", "é"), ("decomposed", "tenant-a", "alice", "e\u0301"),
         ("field-boundary-a", "ab", "c", "title"), ("field-boundary-b", "a", "bc", "title")];
        foreach (var input in inputs)
        {
            byte[] bytes = Frame([CreateSemantic, input.Tenant, input.Principal, input.Title]);
            writer.WriteStartObject(); writer.WriteString("name", input.Name); writer.WriteString("tenant", input.Tenant);
            writer.WriteString("principal", input.Principal); writer.WriteString("title", input.Title);
            writer.WriteString("bytes", Convert.ToHexStringLower(bytes)); writer.WriteString("sha256", Hash(bytes)); writer.WriteEndObject();
        }
        writer.WriteEndArray(); writer.WriteStartObject("attachment");
        const string item = "00112233-4455-6677-8899-aabbccddeeff";
        string contentHash = Hash("abc"u8.ToArray());
        writer.WriteString("tenant", "tenant-a"); writer.WriteString("principal", "alice"); writer.WriteString("itemId", item);
        writer.WriteString("contentSha256", contentHash); writer.WriteNumber("contentLength", 3); writer.WriteNumber("expectedVersion", 7);
        writer.WriteString("sha256", AttachmentHash(new("tenant-a", "alice", true), item, contentHash, 3, 7));
        writer.WriteEndObject();
        const string responseItem = "11223344-5566-7788-99aa-bbccddeeff00";
        WriteResponseVector(writer, "responseCreate", JsonSerializer.SerializeToUtf8Bytes(
            new CreatedItem(1, item, responseItem, "世界 🦀", 1_700_000_000_123, 1), AppJson.Default.CreatedItem));
        WriteResponseVector(writer, "responseAttachment", JsonSerializer.SerializeToUtf8Bytes(
            new AttachedItem(1, "22334455-6677-8899-aabb-ccddeeff0011", responseItem, contentHash, 3, 2), AppJson.Default.AttachedItem));
        writer.WriteEndObject(); writer.Flush();
    }

    private static void WriteResponseVector(Utf8JsonWriter writer, string name, byte[] bytes)
    {
        writer.WriteStartObject(name);
        writer.WriteString("bytes", Convert.ToHexStringLower(bytes)); writer.WriteString("sha256", Hash(bytes));
        writer.WriteEndObject();
    }
}

/// <summary>Authenticated and versioned keyset cursors; no cross-page snapshot guarantee.</summary>
internal sealed class CursorCodec(byte[] key)
{
    internal string Encode(AuthIdentity identity, long createdAt, string itemId)
    {
        byte[] data = Canonical.Frame(["cursor.v1", identity.Tenant, identity.Principal, itemId], createdAt);
        byte[] mac = HMACSHA256.HashData(key, data);
        return Base64(data.Concat(mac).ToArray());
    }

    internal (long CreatedAt, string ItemId) Decode(AuthIdentity identity, string cursor)
    {
        try
        {
            if (cursor.Length > 2048) throw new FormatException();
            byte[] bytes = Convert.FromBase64String(cursor.Replace('-', '+').Replace('_', '/').PadRight((cursor.Length + 3) / 4 * 4, '='));
            if (bytes.Length < 36) throw new FormatException();
            ReadOnlySpan<byte> data = bytes.AsSpan(0, bytes.Length - 32);
            if (!CryptographicOperations.FixedTimeEquals(HMACSHA256.HashData(key, data), bytes.AsSpan(bytes.Length - 32))) throw new FormatException();
            if (BinaryPrimitives.ReadUInt32LittleEndian(data) != 1) throw new FormatException();
            int offset = 4;
            string ReadField()
            {
                if (offset > bytes.Length - 36) throw new FormatException();
                int length = checked((int)BinaryPrimitives.ReadUInt32LittleEndian(bytes.AsSpan(offset)));
                offset += 4;
                if (length < 0 || length > bytes.Length - 32 - offset) throw new FormatException();
                string result = Canonical.Utf8.GetString(bytes, offset, length); offset += length; return result;
            }
            if (ReadField() != "cursor.v1" || ReadField() != identity.Tenant || ReadField() != identity.Principal) throw new FormatException();
            string item = Canonical.Id(ReadField());
            if (offset + 8 != data.Length) throw new FormatException();
            return (BinaryPrimitives.ReadInt64LittleEndian(bytes.AsSpan(offset)), item);
        }
        catch (Exception error) when (error is FormatException or OverflowException or DecoderFallbackException or ApplicationProblem)
        { throw new ApplicationProblem(400, "invalid_cursor"); }
    }

    private static string Base64(byte[] data) => Convert.ToBase64String(data).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}
