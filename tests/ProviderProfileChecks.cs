using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using NativeWeave.Interop;
using NativeWeave.Interop.Extensibility;

// Maintainer assertions only. The private component bootstrap and the public
// provider's complete Database Host are distinct native assets and contracts.
internal static class ProviderProfileChecks
{
    private static readonly string[] CommonCapabilities =
    [
        "db.metadata.v1", "db.query.v1", "db.transactions.v1", "db.savepoints.v1", "db.streaming.v1",
        "db.migrations.v1", "db.schema.read.v1", "db.returning.v1", "db.upsert.v1", "db.cte.v1",
        "db.window.v1", "db.null-safe-equality.v1", "db.json.v1", "db.fixed-money.v1",
        "db.relationships.explicit.v1", "db.prepared-shape.v1", "db.bulk-batches.v1", "db.dynamic-fields.v1",
        "db.recursive-cte.v1", "db.set-operations.v1", "db.scalar-codecs.v1", "db.sql.expert.v1"
    ];

    internal static int Component(string provider, string? asset)
    {
        string path = Path.GetFullPath(asset ?? throw new InvalidOperationException("An explicit private component asset is required."));
        (string engine, string bootstrap, string capability) = provider switch
        {
            "sqlite" => ("nativeweave.database.sqlite", "nw_sqlite_get_abi_v1", "db.sqlite.profile.v1"),
            "postgresql" => ("nativeweave.postgres.component", "nw_postgres_component_get_abi_v1", "postgres.component.v1"),
            _ => throw new ArgumentException("Unknown provider.", nameof(provider))
        };
        // This test-only descriptor preserves the standalone component ABI check;
        // it is never substituted for SqliteDataSource/PostgreSqlDataSource.Engine.
        var descriptor = EnginePackage.CreateDescriptor(new EnginePackageManifest(engine,
            typeof(ProviderProfileChecks).Assembly.GetName().Name!, "0.1.0", new(1, 0), bootstrap,
            EngineThreadingModel.Synchronous,
            [new("linux-x64", "runtimes/linux-x64/native/" + Path.GetFileName(path), Hash(path), "x86-64")],
            [new(new(capability), 0), new(new("db.query.v1"), 1)]), typeof(ProviderProfileChecks).Assembly);
        var info = descriptor.Inspect(new() { NativeAssetPath = path });
        Require(info.EngineId == engine && info.RuntimeIdentifier == "linux-x64" && info.AbiVersion == new AbiVersion(1, 0), "private component ABI identity");
        Require(info.Capabilities.Select(x => x.Name).SequenceEqual([capability]) && !info.Supports(new("db.query.v1")), "exact private component capability");
        Require(ReferenceEquals(info, descriptor.Inspect(new() { NativeAssetPath = path })), "cached private component preflight");
        Console.WriteLine($"PASS private {provider} component bootstrap; capability={capability}; sha256={Hash(path)}.");
        return 3;
    }

    internal static int Host(Func<EngineDescriptor> readDescriptor, string provider, string? overridePath = null)
    {
        string engine = "database." + provider;
        string package = provider == "sqlite" ? "NativeWeave.Database.Sqlite" : "NativeWeave.Database.PostgreSql";
        string file = "libnw_database_" + provider + ".so";
        Require(!Mapped(file) && NoHostThreads(), "fresh process has no Database Host before metadata access");
        var descriptor = readDescriptor();
        Require(descriptor.EngineId == engine && descriptor.PackageId == package
            && descriptor.SupportedRuntimeIdentifiers.SequenceEqual(["linux-x64"]), "exact integrated provider descriptor");
        Require(ReferenceEquals(descriptor, readDescriptor()) && !Mapped(file) && NoHostThreads(), "cached metadata starts no native load or Host executor");
        using var document = JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "NativeWeave." + engine + ".assets.json")));
        var record = document.RootElement;
        string relative = "runtimes/linux-x64/native/" + file;
        Require(record.GetProperty("schemaVersion").GetInt32() == 1 && record.GetProperty("engineId").GetString() == engine
            && record.GetProperty("packageId").GetString() == package && record.GetProperty("packageVersion").GetString() == descriptor.PackageVersion
            && record.GetProperty("rid").GetString() == "linux-x64" && record.GetProperty("sourcePath").GetString() == relative
            && record.GetProperty("outputPath").GetString() == relative, "exact current Host output record");
        string path = Path.Combine(AppContext.BaseDirectory, relative);
        Require(Hash(path) == record.GetProperty("sha256").GetString(), "actual packaged Host hash");
        var info = descriptor.Inspect();
        string[] providerCapabilities = provider == "sqlite" ? ["db.decimal.text.v1"] : ["db.row-lock.v1", "db.decimal.numeric.v1"];
        Require(info.EngineId == engine && info.PackageId == package && info.PackageVersion == descriptor.PackageVersion
            && info.RuntimeIdentifier == "linux-x64" && info.AbiVersion == new AbiVersion(1, 0)
            && info.ThreadingModel == EngineThreadingModel.EngineLocalAsync, "actual integrated Host ABI and threading profile");
        Require(info.Capabilities.Select(x => x.Name).SequenceEqual(CommonCapabilities.Concat(providerCapabilities).Order(StringComparer.Ordinal)), "exact provider Host capability closure");
        Require(ReferenceEquals(info, descriptor.Inspect(new() { NativeAssetPath = overridePath ?? path })), "explicit exact-asset override retains cached Host inspection");
        Require(Mapped(file) && NoHostThreads() && OwnersAreZero(path), "Host inspection loads metadata without executor or database owners");
        Console.WriteLine($"PASS integrated {engine} preflight; capabilities={info.Capabilities.Count}; sha256={Hash(path)}; database owners=0; Host threads=0.");
        return 9;
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static string Hash(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }

    private static bool Mapped(string file) => File.ReadLines("/proc/self/maps")
        .Any(line => line.EndsWith("/" + file, StringComparison.Ordinal));

    private static bool NoHostThreads()
    {
        foreach (string task in Directory.EnumerateDirectories("/proc/self/task"))
        {
            try
            {
                if (File.ReadAllText(Path.Combine(task, "comm")).Trim().StartsWith("nw-db-", StringComparison.Ordinal)) return false;
            }
            catch (FileNotFoundException) { } // A concurrent CLR thread may already have exited.
            catch (DirectoryNotFoundException) { }
        }
        return true;
    }

    private static unsafe bool OwnersAreZero(string path)
    {
        // Inspect already keeps this module resident. Release only this extra
        // diagnostic Load reference; never unload the Core-owned module handle.
        nint module = NativeLibrary.Load(path);
        try
        {
            var count = (delegate* unmanaged[Cdecl]<uint, ulong>)NativeLibrary.GetExport(module, "nw_db_diagnostic_count_v1");
            for (uint kind = 0; kind < 6; kind++) if (count(kind) != 0) return false;
            return true;
        }
        finally { NativeLibrary.Free(module); }
    }
}
