using System.Buffers.Binary;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;
using NativeWeave.Database.PostgreSql;

if (args.Contains("--require-aot") && RuntimeFeature.IsDynamicCodeSupported) throw new InvalidOperationException("Actual Native AOT required.");
int assertions = 0;
void Check(bool value) { assertions++; if (!value) throw new InvalidOperationException("Managed B02 assertion failed."); }
void Reject(Action action) { assertions++; try { action(); } catch (ArgumentException) { return; } throw new InvalidOperationException("Invalid option accepted."); }
var defaults = new PostgreSqlOptions();
Check(defaults.TlsMode == PostgreSqlTlsMode.VerifyFull);
Check(defaults.RootCertificatePath is null && defaults.ApplicationName == "NativeWeave" && defaults.ConnectTimeout == TimeSpan.FromSeconds(15));
var snapshot = PostgreSqlConfiguration.Snapshot(defaults);
Check(BinaryPrimitives.ReadUInt16LittleEndian(snapshot.Record.Span[2..]) == 8);
Check(BinaryPrimitives.ReadUInt32LittleEndian(snapshot.Record.Span[8..]) == 3);
defaults.ApplicationName = "Changed"; Check(!snapshot.Record.Span.SequenceEqual(PostgreSqlConfiguration.Snapshot(defaults).Record.Span));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { TlsMode = (PostgreSqlTlsMode)9 }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { ApplicationName = "" }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { ApplicationName = "bad\0name" }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { ApplicationName = "\ud800" }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { ApplicationName = new string('x', 257) }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { RootCertificatePath = "relative.pem" }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { ConnectTimeout = TimeSpan.Zero }));
Reject(() => PostgreSqlConfiguration.Snapshot(new() { ConnectTimeout = TimeSpan.MaxValue }));
var options = new PostgreSqlOptions { RootCertificatePath = Environment.GetEnvironmentVariable("NW_PG_ROOT")!, ApplicationName = "NativeWeave.B02.Consumer", ConnectTimeout = TimeSpan.FromSeconds(2) };
byte[] record = PostgreSqlConfiguration.Snapshot(options).Record.ToArray();
unsafe
{
    fixed (byte* bytes = record)
    {
        Check(Native.Options(bytes, (uint)record.Length) == 0);
        byte old = bytes[2]; bytes[2] = 9; Check(Native.Options(bytes, (uint)record.Length) != 0); bytes[2] = old;
        old = bytes[18]; bytes[18] = 4; Check(Native.Options(bytes, (uint)record.Length) != 0); bytes[18] = old;
        uint offset = checked((uint)BinaryPrimitives.ReadUInt64LittleEndian(record.AsSpan(24))); old = bytes[offset]; bytes[offset] = 8; Check(Native.Options(bytes, (uint)record.Length) != 0); bytes[offset] = old;
        Check(Native.Options(bytes, (uint)record.Length - 1) != 0);
    }
}
assertions += ProviderProfileChecks.Component("postgresql", Environment.GetEnvironmentVariable("NW_PG_COMPONENT_ASSET"));
assertions += ProviderProfileChecks.Host(() => PostgreSqlDataSource.Engine, "postgresql", Environment.GetEnvironmentVariable("NW_PG_HOST_ASSET"));
if (Environment.GetEnvironmentVariable("NW_PG_OPTION_RECORD") is string optionPath) File.WriteAllBytes(optionPath, record);
Check(Native.Run() == 0);
Console.WriteLine($"PASS managed B02 assertions={assertions}; dynamicCodeSupported={RuntimeFeature.IsDynamicCodeSupported}; actual PostgreSQL provider/TLS/transaction oracle suite completed; native owners retired before return.");

internal static partial class Native
{
    [LibraryImport("nativeweave_postgres_fixture", EntryPoint = "nw_postgres_fixture_run_v1")]
    [UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
    internal static partial uint Run();
    [LibraryImport("nativeweave_postgres_fixture", EntryPoint = "nw_postgres_fixture_options_v1")]
    [UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
    internal static unsafe partial uint Options(byte* record, uint length);
}
