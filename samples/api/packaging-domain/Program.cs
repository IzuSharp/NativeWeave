using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using NativeWeave.Data;
using NativeWeave.Database;
using NativeWeave.Interop;
using NativeWeave.Interop.Extensibility;
using NativeWeave.Query;
#if SQLITE
using NativeWeave.Database.Sqlite;
#endif
#if POSTGRES
using NativeWeave.Database.PostgreSql;
#endif

// Ordinary C# application source, compiled against three independently restored
// database PackageReference graphs. The application chooses its own hosting.
internal static class Program
{
    private static readonly List<string> Checks = [];
    internal static void Check(string name, bool value)
    {
        if (!value) throw new InvalidOperationException(name);
        Checks.Add(name);
    }

    private static async Task<int> Main(string[] args)
    {
        try
        {
            if (args.Contains("--require-aot"))
                Check("actual-native-aot", !RuntimeFeature.IsDynamicCodeSupported);
            if (args.Contains("--reject-abi"))
            {
                RejectAbi();
                Console.WriteLine("B24_ABI_REJECTED_BEFORE_DOMAIN_OWNER");
                return 0;
            }
            string provider = Environment.GetEnvironmentVariable("B24_PROVIDER")
                ?? throw new InvalidOperationException("Explicit database provider required.");
            await using var database = await DatabaseFixture.Create(provider);
            Check("typed-native-database-roundtrip", await database.Count() == 5);
            // This business query method can be called unchanged by console,
            // standard ASP.NET Core HTTP, or standard C# gRPC application code.
            var rows = await database.QueryDtos();
            Check("typed-fluent-dto-query", rows.SequenceEqual([new ItemDto(2, "typed 2"), new ItemDto(3, "typed 3")]));
#if MANAGED_EDIT
            await AddedModels.Verify(database.Source);
            Check("ordinary-added-entity-dto-query", true);
#endif
            var nativeLibraries = ObserveNativeLibraries(provider);
            await database.DisposeAsync();
            var receipt = new ConsumerReceipt(1, "DB-Scope-01", provider,
                RuntimeFeature.IsDynamicCodeSupported, Checks.ToArray(), nativeLibraries);
            Console.WriteLine("B24_RESULT " + JsonSerializer.Serialize(receipt, ConsumerJson.Default.ConsumerReceipt));
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error);
            return 1;
        }
    }

    private static NativeLibraryReceipt[] ObserveNativeLibraries(string provider)
    {
        string expected = provider switch
        {
            "sqlite" => "libnw_database_sqlite.so",
            "postgresql" => "libnw_database_postgresql.so",
            _ => throw new ArgumentException("Unknown database provider.")
        };
        var mapped = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (string line in File.ReadLines("/proc/self/maps"))
        {
            string[] parts = line.Split(' ', 6, StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length != 6 || !Path.IsPathRooted(parts[5])) continue;
            string path = parts[5];
            string name = Path.GetFileName(path);
            if (!name.Contains(".so", StringComparison.Ordinal)) continue;
            if (!name.StartsWith("libnw_", StringComparison.Ordinal)
                && !name.Contains("nativeweave", StringComparison.OrdinalIgnoreCase)) continue;
            Check("only-selected-database-module", name == expected && File.Exists(path));
            if (mapped.TryGetValue(name, out string? previous))
                Check("single-database-module-path", previous == path);
            else mapped.Add(name, path);
        }
        Check("actual-database-native-mapping", mapped.Count == 1 && mapped.ContainsKey(expected));
        return mapped.Select(item =>
        {
            using var stream = File.OpenRead(item.Value);
            return new NativeLibraryReceipt(item.Key, Convert.ToHexStringLower(SHA256.HashData(stream)));
        }).ToArray();
    }

    private static void RejectAbi()
    {
        string file = Path.Combine(AppContext.BaseDirectory, "NativeWeave.database.sqlite.assets.json");
        using var json = JsonDocument.Parse(File.ReadAllText(file));
        var record = json.RootElement;
        string native = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, record.GetProperty("outputPath").GetString()!));
        var manifest = new EnginePackageManifest("database.sqlite", record.GetProperty("packageId").GetString()!,
            record.GetProperty("packageVersion").GetString()!, new AbiVersion(99, 0),
            "nw_database_sqlite_get_abi_v1", EngineThreadingModel.EngineLocalAsync,
            [new NativeAssetDescriptor("linux-x64", record.GetProperty("sourcePath").GetString()!,
                record.GetProperty("sha256").GetString()!, "x86-64")], []);
        var descriptor = EnginePackage.CreateDescriptor(manifest, typeof(Program).Assembly);
        try { descriptor.Inspect(new() { NativeAssetPath = native }); }
        catch (EngineLoadException error) when (error.Failure == EngineLoadFailure.IncompatibleAbi)
        { Check("actual-domain-bootstrap-incompatible-abi", true); return; }
        throw new InvalidOperationException("Expected actual incompatible domain bootstrap rejection.");
    }
}

internal sealed record ConsumerReceipt(int SchemaVersion, string Task, string Provider, bool DynamicCodeSupported,
    string[] Checks, NativeLibraryReceipt[] NativeLibraries);
internal sealed record NativeLibraryReceipt(string File, string Sha256);
[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase)]
[JsonSerializable(typeof(ConsumerReceipt))]
internal partial class ConsumerJson : JsonSerializerContext;

internal sealed record Item(long Id, string Name);
internal sealed record ItemDto(long Id, string Name);
internal sealed class DatabaseFixture : IAsyncDisposable
{
    internal DataSource Source { get; }
    private readonly string _name = "nw_db_scope_" + Guid.NewGuid().ToString("N");
    private readonly Column<Item, long> _id;
    private readonly Column<Item, string> _label;
    private readonly Table<Item> _table;
    private int _disposed;

    private DatabaseFixture(DataSource source)
    {
        Source = source;
        var builder = new TableBuilder<Item>(_name);
        _id = builder.Column("id", Codecs.Int64, new() { IsPrimaryKey = true });
        _label = builder.Column("name", Codecs.String);
        _table = builder.Build(row => new(row.Get(_id), row.Get(_label)),
            (row, value) => { row.Set(_id, value.Id); row.Set(_label, value.Name); });
    }

    internal static async Task<DatabaseFixture> Create(string provider)
    {
        string location = Environment.GetEnvironmentVariable("B24_DATABASE") ?? throw new InvalidOperationException("Explicit B24_DATABASE required.");
        DataSourceBuilder builder;
        switch (provider)
        {
#if SQLITE
            case "sqlite": builder = new DataSourceBuilder().UseSqlite(location, options => options.BeginMode = SqliteBeginMode.Immediate); break;
#endif
#if POSTGRES
            case "postgresql": builder = new DataSourceBuilder().UsePostgreSql(location, options => options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment); break;
#endif
            default: throw new ArgumentException("Provider is not part of this independent package graph.");
        }
        var result = new DatabaseFixture(builder.ConfigureLimits(new() { MaxConnections = 2, MaxBufferedRows = 32 }).Build());
        try
        {
            await using var session = await result.Source.OpenSessionAsync();
            await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE " + result._name + "(id BIGINT PRIMARY KEY,name TEXT NOT NULL)", kind: SqlCommandKind.Mutation));
            for (long i = 1; i <= 5; i++) await session.InsertAsync(result._table, new Item(i, "typed " + i));
            var read = await session.FindAsync(result._table, result._table.Key(result._id, 3L));
            Program.Check("typed-entity-materialization", read == new Item(3, "typed 3"));
            return result;
        }
        catch { await result.DisposeAsync(); throw; }
    }

    internal async Task<IReadOnlyList<ItemDto>> QueryDtos()
    {
        await using var session = await Source.OpenSessionAsync();
        using var query = session.From(_table);
        var projection = query.Projection<ItemDto>();
        var id = projection.Add(query.Column(_id), "id");
        var label = projection.Add(query.Column(_label), "name");
        return await query.WhereGreaterThanOrEqual(_id, 2L).OrderBy(_id).Take(2)
            .Select(projection.Build(row => new ItemDto(row.Get(id), row.Get(label)))).ToListAsync();
    }

    internal async Task<long> Count()
    {
        await using var session = await Source.OpenSessionAsync();
        return await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM " + _name), Codecs.Int64);
    }

    public async ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) != 0) return;
        try
        {
            await using var session = await Source.OpenSessionAsync();
            await session.ExecuteAsync(SqlCommand.Create("DROP TABLE IF EXISTS " + _name, kind: SqlCommandKind.Mutation));
        }
        finally
        {
            var closed = await Source.CloseAsync(TimeSpan.FromSeconds(5));
            await Source.DisposeAsync();
            Program.Check("database-local-owners-retired", closed.LocalResourcesReleased);
        }
    }
}
