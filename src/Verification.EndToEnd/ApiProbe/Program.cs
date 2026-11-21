using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using NativeWeave.Data;
using NativeWeave.Database;
using NativeWeave.Database.PostgreSql;
using NativeWeave.Database.Sqlite;

namespace NativeWeave.Verification.EndToEnd;

internal sealed record ProbeConfig(string Provider, string Database, string OutputDirectory,
    bool AllowLocalDatabaseTlsDisable = false);
internal sealed record CaseReceipt(string Id, string Status, Dictionary<string, string> Observations);
internal sealed record ProbeReceipt(int SchemaVersion, string Task, string Provider, bool DynamicCodeSupported,
    string StartedUtc, string EndedUtc, List<CaseReceipt> Cases, List<string> Failures,
    Dictionary<string, ulong[]> NativeDatabaseOwners, string ManagedRootObservation);

[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase, WriteIndented = true)]
[JsonSerializable(typeof(ProbeConfig)), JsonSerializable(typeof(ProbeReceipt))]
internal partial class ReceiptJson : JsonSerializerContext;

/// <summary>Direct database composition through ordinary packages; no application server is involved.</summary>
internal static partial class Probe
{
    private static readonly List<CaseReceipt> Cases = [];
    private static readonly List<string> Failures = [];
    private static readonly object Gate = new();
    internal static ProbeConfig Config = null!;

    private static async Task<int> Main(string[] args)
    {
        string started = DateTimeOffset.UtcNow.ToString("O");
        if (args.Length != 2 || args[0] != "--config") throw new ArgumentException("--config <private JSON>");
        Config = JsonSerializer.Deserialize(await File.ReadAllTextAsync(args[1]), ReceiptJson.Default.ProbeConfig)
            ?? throw new ArgumentException("Missing probe configuration.");
        if (Config.Provider is not ("sqlite" or "postgresql")) throw new ArgumentException("Unknown provider.");
        Directory.CreateDirectory(Config.OutputDirectory);
        Console.WriteLine("DATABASE_API_RUNTIME dynamic=" + RuntimeFeature.IsDynamicCodeSupported);
        try
        {
            await DatabaseCases();
        }
        catch (Exception failure)
        {
            Failures.Add(failure.GetType().Name + ":" + failure.Message);
            Console.Error.WriteLine("DATABASE_API_FAILED " + failure.GetType().Name + ":" + failure.Message);
            Console.Error.WriteLine(failure);
        }
        var owners = NativeCounts();
        try { Check("final-native-database-owners-zero", owners.Count == 2 && owners.Values.All(values => values.All(value => value == 0))); }
        catch (Exception failure) { Failures.Add(failure.Message); }
        var receipt = new ProbeReceipt(1, "DB-Scope-01", Config.Provider, RuntimeFeature.IsDynamicCodeSupported, started,
            DateTimeOffset.UtcNow.ToString("O"), Cases, Failures, owners,
            "Explicit weak-reference and scoped-disposal witnesses only; this executable does not claim a total managed GCHandle/root counter.");
        await File.WriteAllTextAsync(Path.Combine(Config.OutputDirectory, "receipt.json"),
            JsonSerializer.Serialize(receipt, ReceiptJson.Default.ProbeReceipt));
        Console.WriteLine("DATABASE_API_RESULT cases=" + Cases.Count + " failures=" + Failures.Count);
        return Failures.Count == 0 ? 0 : 1;
    }

    internal static void Check(string id, bool passed, params (string Key, object Value)[] details)
    {
        var row = new CaseReceipt(id, passed ? "passed" : "failed",
            details.ToDictionary(item => item.Key, item => Convert.ToString(item.Value, System.Globalization.CultureInfo.InvariantCulture) ?? "null"));
        lock (Gate) Cases.Add(row);
        Console.WriteLine((passed ? "PASS " : "FAIL ") + id);
        if (!passed) throw new InvalidOperationException(id);
    }

    internal static async Task<T> Expect<T>(Func<Task> action) where T : Exception
    {
        try { await action(); } catch (T error) { return error; }
        throw new InvalidOperationException("Expected " + typeof(T).Name);
    }

    internal static async Task Until(Func<bool> condition, string reason)
    {
        var clock = Stopwatch.StartNew();
        while (!condition()) { if (clock.Elapsed > TimeSpan.FromSeconds(10)) throw new TimeoutException(reason); await Task.Delay(10); }
    }

    internal static DataSource Source(int capacity = 2)
    {
        DataSourceBuilder builder = Config.Provider == "sqlite"
            ? new DataSourceBuilder().UseSqlite(Config.Database, options => options.BeginMode = SqliteBeginMode.Immediate)
            : new DataSourceBuilder().UsePostgreSql(Config.Database, options =>
                { if (Config.AllowLocalDatabaseTlsDisable) options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment; });
        return builder.ConfigureLimits(new() { MaxConnections = capacity, MaxWaiters = 4, MaxBatchRows = 2,
            MaxBufferedRows = 64, CommandTimeout = TimeSpan.FromSeconds(10) }).Build();
    }

    private static unsafe Dictionary<string, ulong[]> NativeCounts()
    {
        var result = new Dictionary<string, ulong[]>();
        foreach (string path in Directory.GetFiles(AppContext.BaseDirectory, "*.assets.json"))
        {
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            var root = document.RootElement;
            if (!root.TryGetProperty("outputPath", out var output)) continue;
            string file = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, output.GetString()!));
            if (!Path.GetFileName(file).StartsWith("libnw_database_", StringComparison.Ordinal)) continue;
            // Only the fixed counter export is read. No private owner pointer is fabricated,
            // and these already selected native modules remain loaded until process exit.
            nint module = NativeLibrary.Load(file);
            var counter = (delegate* unmanaged[Cdecl]<uint, ulong>)NativeLibrary.GetExport(module, "nw_db_diagnostic_count_v1");
            ulong[] counts = new ulong[6]; for (uint i = 0; i < counts.Length; i++) counts[i] = counter(i);
            result[Path.GetFileName(file)] = counts;
        }
        return result;
    }
}
