using System.Runtime.CompilerServices;
using System.Text.Json;

namespace NativeWeave.Reference.TaskService;

/// <summary>Finite database regression scenarios using the ordinary application methods directly.</summary>
internal static class Program
{
    private static async Task<int> Main(string[] args)
    {
        try
        {
            if (args.Length == 1 && args[0] == "--golden-vectors") { Canonical.WriteGoldenVectors(Console.OpenStandardOutput()); return 0; }
            string? configPath = null;
            string mode = "--verify";
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--config" && i + 1 < args.Length) configPath = args[++i];
                else if (args[i] is "--verify" or "--migrate-only" or "--outbox-once" or "--maintenance-once" or
                    "--conflict-case" or "--unknown-case" or "--create-case" or "--retry-case" or "--failure-case" or "--attachment-case" or "--read-attachment-case" or "--keyset-case") mode = args[i];
                else throw new ArgumentException("Usage: --config <file> [--verify|--migrate-only|--outbox-once|--maintenance-once|--conflict-case|--unknown-case|--create-case|--retry-case], or --golden-vectors.");
            }
            if (configPath is null || new FileInfo(configPath).Length > 65_536) throw new ArgumentException("A bounded configuration file is required.");
            var configuration = JsonSerializer.Deserialize(await File.ReadAllBytesAsync(configPath).ConfigureAwait(false), AppJson.Default.ServiceConfiguration)
                ?? throw new ArgumentException("A configuration object is required.");
            configuration.Validate();
            Console.WriteLine("DATABASE_REFERENCE_RUNTIME dynamic=" + RuntimeFeature.IsDynamicCodeSupported);
            await using var database = configuration.CreateSource();
            await using var consumer = configuration.CreateConsumer();
            // Migration is an explicit fixture deployment step, never an automatic data-source side effect.
            if (!configuration.SkipMigrations)
            {
                await TaskService.MigrateAsync(database, configuration.Provider).ConfigureAwait(false);
                await TaskService.MigrateAsync(consumer, "consumer").ConfigureAwait(false);
            }
            if (mode == "--migrate-only") { Console.WriteLine("MIGRATED"); return 0; }
            using BlobStore blobs = new(configuration);
            TaskService service = new(database, new(Convert.FromBase64String(configuration.CursorKey)), blobs);
            FixtureCases cases = new(configuration, service, new OutboxWorker(database, consumer), blobs);
            try
            {
                using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(configuration.OperationTimeoutSeconds));
                await cases.RunAsync(mode, timeout.Token).ConfigureAwait(false);
            }
            finally
            {
                try { await Task.WhenAll(consumer.DisposeAsync().AsTask(), database.DisposeAsync().AsTask()).ConfigureAwait(false); }
                finally { await service.JoinProtectionRetirementAsync().ConfigureAwait(false); }
            }
            if (!database.Cleanup.LocalResourcesReleased || !consumer.Cleanup.LocalResourcesReleased)
                throw new InvalidOperationException("fixture:database-resources-not-released");
            var receipt = new FixtureReceipt(mode, RuntimeFeature.IsDynamicCodeSupported, cases.Replies, cases.Checks,
                database.Cleanup.LocalResourcesReleased, consumer.Cleanup.LocalResourcesReleased);
            Console.WriteLine("DATABASE_REFERENCE_RESULT " + JsonSerializer.Serialize(receipt, AppJson.Default.FixtureReceipt));
            return 0;
        }
        catch (Exception error)
        {
            // Connection strings and persisted request bytes never enter default diagnostics.
            Console.Error.WriteLine("database_reference_failed type=" + error.GetType().Name);
            if (error is InvalidOperationException && error.Message.StartsWith("fixture:", StringComparison.Ordinal)) Console.Error.WriteLine(error.Message);
            return 1;
        }
    }
}
