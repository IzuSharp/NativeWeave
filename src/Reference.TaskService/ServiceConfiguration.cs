using NativeWeave.Database;
#if !REFERENCE_SQLITE_ONLY
using NativeWeave.Database.PostgreSql;
#endif
using NativeWeave.Database.Sqlite;

namespace NativeWeave.Reference.TaskService;

internal sealed record PrincipalConfiguration(string Tenant, string Principal, bool CanWrite = true);

/// <summary>Explicit finite application settings, loaded once from a protected local JSON file.</summary>
internal sealed class ServiceConfiguration
{
    public required string Provider { get; init; }
    public required string Database { get; init; }
    public required string BlobDirectory { get; init; }
    public required string ConsumerDatabase { get; init; }
    public required string CursorKey { get; init; }
    public required PrincipalConfiguration[] Principals { get; init; }
    public bool AllowLocalDatabaseTlsDisable { get; init; }
    public int MaxUploads { get; init; } = 4;
    public long MaxBlobBytes { get; init; } = 256L * 1024 * 1024;
    public int OrphanGraceSeconds { get; init; } = 3600;
    public int OperationTimeoutSeconds { get; init; } = 90;
    public bool SkipMigrations { get; init; }
    public string CaseKey { get; init; } = "database-reference";
    public string CaseTitle { get; init; } = "Database reference fixture";

    internal void Validate()
    {
#if REFERENCE_SQLITE_ONLY
        if (Provider != "sqlite") throw new ArgumentException("The minimum sample includes only the SQLite provider package.");
#endif
        if (Provider is not ("sqlite" or "postgresql") || string.IsNullOrWhiteSpace(Database) || string.IsNullOrWhiteSpace(ConsumerDatabase) ||
            string.IsNullOrWhiteSpace(BlobDirectory) ||
            MaxUploads is < 1 or > 16 || MaxBlobBytes < BlobStore.MaximumAttachment || MaxBlobBytes > 1024L * 1024 * 1024 * 1024 ||
            OrphanGraceSeconds is < 60 or > 604800 || OperationTimeoutSeconds is < 1 or > 3600 ||
            Convert.FromBase64String(CursorKey).Length is < 32 or > 64 ||
            Principals.Length is < 1 or > 128)
            throw new ArgumentException("Invalid database fixture configuration.");
        foreach (var identity in Principals)
        {
            if (!ValidIdentity(identity.Tenant) || !ValidIdentity(identity.Principal)) throw new ArgumentException("Invalid fixture identity configuration.");
        }
        if (Provider == "sqlite" && Path.GetFullPath(Database) == Path.GetFullPath(ConsumerDatabase))
            throw new ArgumentException("The outbox consumer must use a separate persistent database.");
    }

    private static bool ValidIdentity(string value) => !string.IsNullOrWhiteSpace(value) && Canonical.Utf8.GetByteCount(value) <= 128 && !value.Any(char.IsControl);

    internal DataSource CreateSource()
    {
        DataSourceBuilder builder = new();
        if (Provider == "sqlite") builder.UseSqlite(Database, options => { options.BeginMode = SqliteBeginMode.Immediate; options.BusyTimeout = TimeSpan.FromSeconds(5); });
#if !REFERENCE_SQLITE_ONLY
        else builder.UsePostgreSql(Database, options => { if (AllowLocalDatabaseTlsDisable) options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment; });
#else
        else throw new ArgumentException("The minimum sample includes only the SQLite provider package.");
#endif
        return builder.ConfigureLimits(new DatabaseLimits
        {
            MaxConnections = 16,
            MaxWaiters = 64,
            AdmissionTimeout = TimeSpan.FromSeconds(5),
            CommandTimeout = TimeSpan.FromSeconds(15),
            MaxBufferedRows = 128,
            MaxBufferedBytes = 1024 * 1024,
            MaxBatchRows = 100,
            MaxBatchBytes = 512 * 1024,
            MaxFieldBytes = 1024 * 1024
        }).Build();
    }

    internal DataSource CreateConsumer() => new DataSourceBuilder()
        .UseSqlite(ConsumerDatabase, options => { options.BeginMode = SqliteBeginMode.Immediate; options.BusyTimeout = TimeSpan.FromSeconds(5); })
        .ConfigureLimits(new() { MaxConnections = 2, MaxWaiters = 4, MaxBufferedRows = 32, MaxBufferedBytes = 128 * 1024 }).Build();
}
