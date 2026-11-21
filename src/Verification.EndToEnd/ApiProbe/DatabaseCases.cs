using System.Runtime.CompilerServices;
using NativeWeave.Data;
using NativeWeave.Database;

namespace NativeWeave.Verification.EndToEnd;

internal static partial class Probe
{
    private static async Task DatabaseCases()
    {
        WeakReference sourceReference = await DatabaseScope();
        for (int i = 0; i < 5 && sourceReference.IsAlive; i++)
        { GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect(); await Task.Delay(20); }
        Check("closed-data-source-weak-reference-released", !sourceReference.IsAlive,
            ("observation", "one explicitly closed source, not total managed roots"));
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static async Task<WeakReference> DatabaseScope()
    {
        DataSource? source = Source(1); var weak = new WeakReference(source);
        var session = await source.OpenSessionAsync();
        await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE b22_api_tx(id BIGINT PRIMARY KEY, value TEXT NOT NULL)", kind: SqlCommandKind.Mutation));
        for (long i = 1; i <= 5; i++)
            await session.ExecuteAsync(SqlCommand.Create("INSERT INTO b22_api_tx(id,value) VALUES(@id,@value)",
                new SqlParameters().Add("id", i, Codecs.Int64).Add("value", "row " + i, Codecs.String), SqlCommandKind.Mutation));
        long? backend = Config.Provider == "postgresql"
            ? await session.ScalarAsync(SqlCommand.Create("SELECT CAST(pg_backend_pid() AS BIGINT)"), Codecs.Int64) : null;
        await using (var transaction = await session.BeginTransactionAsync())
        {
            await session.ExecuteAsync(SqlCommand.Create("INSERT INTO b22_api_tx VALUES(100,'must roll back')", kind: SqlCommandKind.Mutation));
            using var cancellation = new CancellationTokenSource(); cancellation.Cancel();
            var error = await Expect<OperationCanceledException>(() => transaction.CommitAsync(cancellation.Token));
            Check("commit-pre-admission-cancellation", !transaction.CommitAttempted && transaction.Outcome != TransactionOutcome.Committed
                && error.CancellationToken == cancellation.Token,
                ("commitAttempted", transaction.CommitAttempted), ("outcome", transaction.Outcome));
            await transaction.RollbackAsync();
            Check("pre-admission-cancel-confirmed-rollback", transaction.Outcome == TransactionOutcome.RolledBack);
        }
        Check("canceled-commit-no-durable-row", await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM b22_api_tx WHERE id=100"), Codecs.Int64) == 0);
        await using (var transaction = await session.BeginTransactionAsync())
        {
            var primary = await Expect<DatabaseException>(() => session.ExecuteAsync(SqlCommand.Create("INSERT INTO b22_api_tx VALUES(1,'duplicate')", kind: SqlCommandKind.Mutation)));
            Check("actual-failed-transaction-primary", primary.Kind == DatabaseErrorKind.Constraint, ("kind", primary.Kind));
            await transaction.RollbackAsync();
            Check("failed-transaction-confirmed-rollback", transaction.Outcome == TransactionOutcome.RolledBack);
        }
        if (backend is not null)
            Check("rollback-retains-same-physical-pg-session", await session.ScalarAsync(SqlCommand.Create("SELECT CAST(pg_backend_pid() AS BIGINT)"), Codecs.Int64) == backend);
        var projection = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], row => row.Read(0, Codecs.Int64));
        await using (var cursor = session.StreamAsync(SqlCommand.Create("SELECT id FROM b22_api_tx ORDER BY id"), projection).GetAsyncEnumerator())
        {
            Check("early-database-stream-positive-first-row", await cursor.MoveNextAsync() && cursor.Current == 1);
            var busy = await Expect<DatabaseException>(() => session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM b22_api_tx"), Codecs.Int64));
            Check("live-cursor-holds-session-admission", busy.Kind == DatabaseErrorKind.ConcurrentUse);
        }
        Check("early-database-stream-exit-releases-admission", await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM b22_api_tx"), Codecs.Int64) == 5);
        await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE b22_api_parents(tenant BIGINT NOT NULL,id BIGINT NOT NULL,PRIMARY KEY(tenant,id))", kind: SqlCommandKind.Mutation));
        await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE b22_api_children(id BIGINT PRIMARY KEY,tenant BIGINT NULL,parent_id BIGINT NULL,FOREIGN KEY(tenant,parent_id) REFERENCES b22_api_parents(tenant,id))", kind: SqlCommandKind.Mutation));
        await session.InsertAsync(Relations.Parents, new Parent(7, 1));
        foreach (var child in new[] { new Child(1, 7, 1), new Child(2, null, null), new Child(3, 7, null), new Child(4, null, 1) })
            await session.InsertAsync(Relations.Children, child);
        // These assertions were previously hidden inside a NativeWeave HTTP handler.
        // The same typed business query now executes directly in this ordinary C# consumer.
        var related = await session.LoadRelatedAsync(Relations.Parents.Key(Relations.Tenant, 7L).And(Relations.Id, 1L), Relations.Optional);
        using (var query = session.From(Relations.Children))
        using (var nullEquality = session.From(Relations.Children))
        {
            var missing = await query.WhereIsNull(Relations.ChildTenant).OrderBy(Relations.ChildId).SelectAll().ToListAsync();
            long equalNull = await nullEquality.WhereEqual(Relations.ChildTenant, (long?)null).CountAsync();
            string actual = string.Join(',', related.Select(item => item.Id)) + "|" + string.Join(',', missing.Select(item => item.Id)) + "|" + equalNull;
            Check("nullable-composite-foreign-key-direct-query", actual == "1|2,4|0", ("actual", actual));
        }
        await session.DisposeAsync();
        Check("public-session-safe-retirement", session.Cleanup.LocalResourcesReleased);
        var close = await source.CloseAsync(TimeSpan.FromSeconds(2));
        Check("public-source-safe-retirement", close.LocalResourcesReleased);
        await source.DisposeAsync(); source = null;
        return weak;
    }
}

internal sealed record Parent(long Tenant, long Id);
internal sealed record Child(long Id, long? Tenant, long? ParentId);
internal static class Relations
{
    private static readonly TableBuilder<Parent> P = new("b22_api_parents");
    internal static readonly Column<Parent, long> Tenant = P.Column("tenant", Codecs.Int64, new() { IsPrimaryKey = true });
    internal static readonly Column<Parent, long> Id = P.Column("id", Codecs.Int64, new() { IsPrimaryKey = true });
    internal static readonly Table<Parent> Parents = P.Build(row => new(row.Get(Tenant), row.Get(Id)), (row, value) => { row.Set(Tenant, value.Tenant); row.Set(Id, value.Id); });
    private static readonly TableBuilder<Child> C = new("b22_api_children");
    internal static readonly Column<Child, long> ChildId = C.Column("id", Codecs.Int64, new() { IsPrimaryKey = true });
    internal static readonly Column<Child, long?> ChildTenant = C.Column("tenant", Codecs.Nullable(Codecs.Int64));
    internal static readonly Column<Child, long?> ParentId = C.Column("parent_id", Codecs.Nullable(Codecs.Int64));
    internal static readonly Table<Child> Children = C.Build(row => new(row.Get(ChildId), row.Get(ChildTenant), row.Get(ParentId)),
        (row, value) => { row.Set(ChildId, value.Id); row.Set(ChildTenant, value.Tenant); row.Set(ParentId, value.ParentId); });
    internal static readonly Relation<Parent, Child> Optional = Relation<Parent, Child>.CreateOptional(Parents, Tenant, Children, ChildTenant).AndOptional(Id, ParentId);
}
