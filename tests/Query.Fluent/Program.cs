using System.Runtime.CompilerServices;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using NativeWeave.Data;
using NativeWeave.Database;
using NativeWeave.Database.PostgreSql;
using NativeWeave.Database.Sqlite;
using NativeWeave.Query;
using NativeWeave.Interop.Async;

await Suite.Run(args);

internal static class Suite
{
    private static int _assertions, _retirements;
    private static readonly List<string> Completed = [];
    private static readonly List<CompositionCost> Costs = [];
    internal static void Check(bool value, string message) { _assertions++; if (!value) throw new InvalidOperationException(message); }
    internal static T Throws<T>(Action action) where T : Exception
    { try { action(); } catch (T error) { _assertions++; return error; } throw new InvalidOperationException("Expected " + typeof(T).Name); }
    internal static async Task<T> ThrowsAsync<T>(Func<Task> action) where T : Exception
    { try { await action(); } catch (T error) { _assertions++; return error; } throw new InvalidOperationException("Expected " + typeof(T).Name); }
    internal static async Task Run(string[] args)
    {
        if (args.Length < 1) throw new ArgumentException("result-directory [--require-aot]");
        if (args.Contains("--require-aot")) Check(!RuntimeFeature.IsDynamicCodeSupported, "Actual Native AOT process");
        var pg = Environment.GetEnvironmentVariable("NW_TEST_POSTGRES") ?? throw new InvalidOperationException("Real PostgreSQL18 endpoint required.");
        var sqliteFile = Path.Combine(Path.GetTempPath(), "nw-b13-" + Guid.NewGuid().ToString("N") + ".db");
        var nativeFiles = new[] { "libnw_database_sqlite.so", "libnw_database_postgresql.so" }.Select(f => Path.Combine(AppContext.BaseDirectory, "runtimes", "linux-x64", "native", f)).ToArray();
        var hashes = nativeFiles.Select(f => Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(f)))).ToArray();
        foreach (var source in new[] { SqliteDataSource.Create(sqliteFile), PostgreSqlDataSource.Create(pg, o => o.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment) })
        {
            source.TestRetirement = snapshot =>
            {
                Check(snapshot.Released && !snapshot.RootLive && snapshot.Controls == 0 && snapshot.CallbackEntries == 0 && snapshot.RetainedInputBytes == 0, "Managed retirement released callback/root/control/input owners");
                Check(snapshot.Start is AsyncStartOutcome.Skipped or AsyncStartOutcome.Rejected or AsyncStartOutcome.NotStarted || snapshot.NativeQuiet, "Accepted native operation is quiet before managed result returns");
                Interlocked.Increment(ref _retirements);
            };
            using var diagnostic = new Diagnostic(nativeFiles[source.Provider == DatabaseProvider.Sqlite ? 0 : 1]);
            await using (source)
            await using (var session = await source.OpenSessionAsync()) await Provider(session, diagnostic);
            await diagnostic.WaitAllZero();
        }
        File.Delete(sqliteFile);
        Check(hashes.SequenceEqual(nativeFiles.Select(f => Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(f))))), "New C# DTOs and ordinary expressions reuse unchanged native assets");
        Directory.CreateDirectory(args[0]); File.WriteAllText(Path.Combine(args[0], "result.json"), JsonSerializer.Serialize(new Receipt(!RuntimeFeature.IsDynamicCodeSupported, _assertions, _retirements, Completed, hashes, Costs), ReceiptJson.Default.Receipt));
        Console.WriteLine($"PASS B13 actual two-provider Fluent: {_assertions} assertions; AOT={!RuntimeFeature.IsDynamicCodeSupported}");
    }
    private static async Task Provider(DataSession session, Diagnostic diagnostic)
    {
        Console.WriteLine("PROVIDER " + session.Source.Provider);
        await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE \"Parents\" (\"Id\" BIGINT PRIMARY KEY,\"Name\" TEXT NOT NULL,\"Age\" INTEGER NOT NULL,\"Optional\" BIGINT NULL)", kind: SqlCommandKind.Mutation));
        await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE \"Children\" (\"Id\" BIGINT PRIMARY KEY,\"ParentId\" BIGINT NULL)", kind: SqlCommandKind.Mutation));
        await session.ExecuteAsync(SqlCommand.Create("INSERT INTO \"Parents\" VALUES (0,'Zero',10,NULL),(1,'Alice',20,1),(2,'O''Reilly 🦀',30,NULL)", kind: SqlCommandKind.Mutation));
        await session.ExecuteAsync(SqlCommand.Create("INSERT INTO \"Children\" VALUES (10,1),(11,NULL)", kind: SqlCommandKind.Mutation));
        Query<Person> Q() => session.From(Models.People);
        async Task Done(string name) { Completed.Add(session.Source.Provider + "/" + name); Check(await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM \"Parents\""), Codecs.Int64) == 3, "Session usable after " + name); await diagnostic.WaitCursorZero(); Console.WriteLine("CASE " + name); }
        using (var q = Q())
        {
            var threshold = 18; var callbacks = 0;
            q.WhereIf(false, row => { callbacks++; return row.Equal(Models.Id, 0); }).Where(row => row.GreaterThanOrEqual(Models.Age, threshold)); threshold = 99;
            var rows = await q.OrderBy(Models.Id).Take(2).SelectAll().ToListAsync();
            Check(callbacks == 0 && rows.Select(r => r.Id).SequenceEqual([1L, 2L]), "Synchronous closure snapshot and false WhereIf");
            Throws<InvalidOperationException>(() => q.Take(1));
            Throws<InvalidOperationException>(() => q.SelectAll());
        }
        await Done("snapshot-filter-order-limit");
        using (var q = Q())
        {
            Throws<ArgumentException>(() => q.Skip(1)); Throws<InvalidOperationException>(() => q.ThenBy(Models.Id)); Throws<ArgumentOutOfRangeException>(() => q.Take(-1));
            Check((await q.OrderBy(Models.Name).ThenBy(Models.Id).Skip(1).Take(1).SelectAll().SingleAsync()).Id == 2, "Stable unique offset paging");
        }
        using (var q = Q()) Check((await q.OrderBy(Models.Id).SeekAfter(Models.Id, 1L).SelectAll().ToArrayAsync()).Single().Id == 2, "Unique ascending keyset paging");
        using (var q = Q()) { q.OrderBy(Models.Id, SortDirection.Descending); Throws<ArgumentException>(() => q.SeekAfter(Models.Id, 1L)); }
        await Done("pagination");
        using (var q = Q())
        {
            var child = q.LeftJoin(Models.Children, "c", on => on.Left(Models.Id).AsNullable().Equal(on.Right(Models.ParentId)));
            var builder = q.Projection<Joined>(); var id = builder.Add(q.Column(Models.Id), "id"); var childId = builder.Add(q.NullableValue(child, Models.ChildId), "child");
            var matched = builder.Add(SqlFunctions.Case(q.HasMatch(child), q.Value(true, Codecs.Boolean), q.Value(false, Codecs.Boolean)), "matched");
            var projection = builder.Build(row => new(row.Get(id), row.Get(childId), row.Get(matched)));
            var rows = await q.OrderBy(Models.Id).Select(projection).ToListAsync();
            Check(rows.SequenceEqual([new Joined(0, null, false), new Joined(1, 10, true), new Joined(2, null, false)]), "Nullable FK does not match parent key0; LEFT match marker independent");
        }
        using (var q = Q())
        {
            SqlExpression<long?> expired = default;
            JoinPredicate<Person, Child> expiredCallback = default;
            Throws<MappingFailure>(() => q.LeftJoin(Models.Children, "aborted", on => { expiredCallback = on; expired = on.Right(Models.ParentId); throw new MappingFailure(); }));
            Throws<ArgumentException>(() => expired.IsNull());
            Throws<InvalidOperationException>(() => expiredCallback.Left(Models.Id));
            Throws<InvalidOperationException>(() => expiredCallback.Right(Models.ParentId));
            var alias = q.InnerJoin(Models.Children, "good", on => { expiredCallback = on; return on.Left(Models.Id).AsNullable().Equal(on.Right(Models.ParentId)); });
            Throws<InvalidOperationException>(() => expiredCallback.Left(Models.Id));
            Throws<InvalidOperationException>(() => expiredCallback.Right(Models.ParentId));
            Check((await q.Select(q.Column(alias, Models.ChildId)).ToListAsync()).SequenceEqual([10L]), "JOIN abort leaves query usable");
        }
        await Done("joins-nullability-abort");
        using (var q = Q())
        {
            var original = q.Column(Models.Id); var lifted = original.AsNullable();
            Check((await q.OrderBy(Models.Id).Select(SqlFunctions.Coalesce(lifted, 99L)).ToArrayAsync()).SequenceEqual([0L, 1L, 2L]), "Nullable lift preserves original SQL values");
        }
        using (var q = Q())
        {
            var optional = q.Column(Models.Optional);
            Check((await q.OrderBy(Models.Id).Select(SqlFunctions.Coalesce(optional.Add(2L), -1L)).ToListAsync()).SequenceEqual([-1L, 3L, -1L]), "Nullable arithmetic propagates SQL NULL");
        }
        using (var q = Q())
        {
            var id = q.Column(Models.Id); var arithmetic = id.Add(2L).Subtract(1L).Multiply(2L).Divide(2L);
            Check((await q.OrderBy(Models.Id).Select(arithmetic).ToListAsync()).SequenceEqual([1L, 2L, 3L]), "All arithmetic operations");
        }
        using (var q = Q())
        {
            var id = q.Column(Models.Id); var predicate = id.NotEqual(0L).And(id.GreaterThan(0L)).And(id.LessThan(3L)).And(id.LessThanOrEqual(2L)).And(id.Between(1L, 2L)).And(id.In([1L, 2L])).And(id.NotIn([])).And(id.NullSafeEqual(id));
            Check((await q.Where(predicate.Or(id.Equal(9L))).OrderBy(Models.Id).Select(id).ToListAsync()).SequenceEqual([1L, 2L]), "Relational/boolean/membership operators");
        }
        using (var q = Q()) Check(await q.Where(q.Column(Models.Optional).IsNull().Not()).CountAsync() == 1, "Explicit null and NOT");
        using (var q = Q()) Check(await q.WhereIsNull(Models.Optional).CountAsync() == 2, "Direct nullable filter");
        using (var q = Q()) Check(await q.WhereIsNotNull(Models.Optional).AnyAsync(), "Native exists terminal");
        await Done("expressions-null-arithmetic");
        foreach (var pattern in new[] { "Reilly", "%", "_", "';DROP" })
        {
            using var q = Q(); var expected = pattern == "Reilly" ? 1L : 0L;
            Check(await q.Where(q.Column(Models.Name).ContainsLiteral(pattern)).CountAsync() == expected, "Escaped contains literal");
        }
        using (var q = Q()) Check(await q.Where(q.Column(Models.Name).StartsWithLiteral("Ali")).CountAsync() == 1, "StartsWithLiteral");
        using (var q = Q()) Check(await q.Where(q.Column(Models.Name).EndsWithLiteral("🦀")).CountAsync() == 1, "EndsWithLiteral");
        using (var q = Q()) Check(await q.Where(q.Column(Models.Name).Like("O%")).CountAsync() == 1, "Raw LIKE pattern");
        using (var q = Q()) Check(await q.Where(q.Column(Models.Name).AsNullableReference().ContainsNullableLiteral("Ali")).CountAsync() == 1, "Nullable text pattern");
        using (var q = Q()) Check(await q.Where(q.Column(Models.Name).Collate(session.Source.Provider == DatabaseProvider.Sqlite ? "BINARY" : "C").Equal("Alice")).CountAsync() == 1, "Allowlisted collation");
        using (var q = Q()) Check(Throws<DatabaseException>(() => q.Column(Models.Name).Collate("injected")).Kind == DatabaseErrorKind.UnsupportedCapability, "Unregistered collation structured rejection");
        await Done("text-pattern-collation");
        using (var q = Q())
        {
            var b = q.Projection<Aggregates>(); var count = b.Add(q.CountRows(), "count"); var sum = b.Add(SqlFunctions.Sum(q.Column(Models.Age)), "sum");
            var average = b.Add(SqlFunctions.Average(q.Column(Models.Age)), "average"); var min = b.Add(SqlFunctions.Min(q.Column(Models.Id)), "min"); var max = b.Add(SqlFunctions.Max(q.Column(Models.Optional)), "max");
            var projection = b.Build(r => new(r.Get(count), r.Get(sum), r.Get(average), r.Get(min), r.Get(max)));
            Check(await q.Select(projection).SingleAsync() == new Aggregates(3, 60, 20, 0, 1), "Native aggregate widening/nullability");
        }
        using (var q = Q()) { var id = q.Column(Models.Id); q.GroupBy(id).Having(q.CountRows().GreaterThan(0L)); Check((await q.OrderBy(Models.Id).Select(id, q.CountRows(), (a, b) => (a, b)).ToListAsync()).Count == 3, "Group/Having/static factory"); }
        using (var q = Q()) { q.GroupBy(q.Column(Models.Id)); Throws<ArgumentException>(() => q.SelectAll().Prepare()); Check((await q.Select(q.Column(Models.Id)).ToListAsync()).Count == 3, "Invalid grouped projection rejects before sealing and recovers"); }
        using (var q = Q()) { var window = q.Window().OrderBy(q.Column(Models.Id)).RowsBetween(FrameBoundary.UnboundedPreceding, FrameBoundary.CurrentRow); var rank = SqlFunctions.RowNumber(window); window.PartitionBy(q.Column(Models.Id)); Check((await q.OrderBy(Models.Id).Select(rank).ToListAsync()).SequenceEqual([1L, 2L, 3L]), "Window snapshot survives later mutation"); }
        using (var q = Q()) { var window = q.Window().OrderBy(q.Column(Models.Id)).RowsBetween(FrameBoundary.UnboundedPreceding, FrameBoundary.CurrentRow); Check((await q.OrderBy(Models.Id).Select(SqlFunctions.Sum(q.Column(Models.Id)).Over(window)).ToListAsync()).SequenceEqual(new long?[] { 0L, 1L, 3L }), "Aggregate OVER cast after window"); }
        using (var q = Q()) { var id = q.Column(Models.Id); Check((await q.OrderBy(Models.Id).Select(SqlFunctions.Case(id.GreaterThan(0L), q.Value(1L, Codecs.Int64), q.Value(0L, Codecs.Int64))).ToListAsync()).SequenceEqual([0L, 1L, 1L]), "Typed CASE prepare metadata"); }
        await Done("aggregate-window-case");
        using (var q = Q()) Check((await q.Distinct().Select(q.Value(1L, Codecs.Int64)).ToListAsync()).SequenceEqual([1L]), "Native DISTINCT typed scalar");
        foreach (var operation in Enum.GetValues<SetOperation>())
        {
            using var a = Q(); using var b = Q(); var first = a.WhereGreaterThanOrEqual(Models.Id, 1L).Select(a.Column(Models.Id)); var second = b.WhereEqual(Models.Id, 0L).Select(b.Column(Models.Id));
            var rows = await first.Combine(second, operation).ToListAsync(); Check(rows.Count == (operation == SetOperation.Intersect ? 0 : operation == SetOperation.Except ? 2 : 3), "Native set operation " + operation);
        }
        using (var source = Q())
        using (var q = Q()) { var selection = source.WhereEqual(Models.Id, 1L).Select(source.Column(Models.Id)); Check((await q.Where(q.Column(Models.Id).In(selection)).SelectAll().ToListAsync()).Single().Id == 1, "IN native subquery"); }
        using (var source = Q())
        using (var q = Q()) { var selection = source.WhereEqual(Models.Id, 99L).Select(source.Column(Models.Id)); Check(!await q.Where(q.Exists(selection)).AnyAsync(), "EXISTS native subquery"); }
        using (var body = Q())
        {
            var builder = body.Projection<IdRow>(); var id = builder.Add(body.Column(Models.Id), "Id"); var selection = body.WhereGreaterThanOrEqual(Models.Id, 1L).Select(builder.Build(r => new(r.Get(id))));
            using var cte = CommonTable<IdRow>.Create(Models.Cte, selection); body.WhereEqual(Models.Id, 99L);
            using var q = session.From(Models.Cte); Check((await q.With(cte).OrderBy(Models.CteId).SelectAll().ToListAsync()).Select(r => r.Id).SequenceEqual([1L, 2L]), "Explicit CTE immutable body");
        }
        using (var anchor = Q())
        using (var member = session.From(Models.Cte))
        {
            var anchorBuilder = anchor.Projection<IdRow>(); var anchorId = anchorBuilder.Add(anchor.Column(Models.Id), "Id");
            var seed = anchor.WhereEqual(Models.Id, 0L).Select(anchorBuilder.Build(row => new(row.Get(anchorId))));
            var memberBuilder = member.Projection<IdRow>(); var next = memberBuilder.Add(member.Column(Models.CteId).Add(1L), "Id");
            var recursive = member.Where(member.Column(Models.CteId).LessThan(2L)).Select(memberBuilder.Build(row => new(row.Get(next))));
            using var cte = CommonTable<IdRow>.Create(Models.Cte, seed.Combine(recursive, SetOperation.UnionAll), recursive: true);
            using var q = session.From(Models.Cte);
            Check((await q.With(cte).OrderBy(Models.CteId).SelectAll().ToListAsync()).Select(row => row.Id).SequenceEqual([0L, 1L, 2L]), "Validated bounded recursive CTE");
        }
        await Done("set-subquery-cte");
        using (var query = Q())
        {
            var minimum = query.Parameter("minimum", Codecs.Int64); query.Where(query.Column(Models.Id).GreaterThanOrEqual(query.ParameterValue(minimum))).OrderBy(Models.Id);
            using var prepared = query.SelectAll().Prepare(); query.Dispose();
            var values = new QueryParameters().Set(minimum, 1L); var first = prepared.ToListAsync(session, values); values.Set(minimum, 2L);
            Check((await first).Count == 2 && (await prepared.ToListAsync(session, values)).Single().Id == 2, "Independent prepare-time execution snapshot");
            await using (var a = await session.Source.OpenSessionAsync())
            await using (var b = await session.Source.OpenSessionAsync())
            {
                var parallel = await Task.WhenAll(prepared.ToListAsync(a, new QueryParameters().Set(minimum, 0L)), prepared.ToListAsync(b, new QueryParameters().Set(minimum, 2L)));
                Check(parallel[0].Count == 3 && parallel[1].Single().Id == 2, "Concurrent immutable plan executions use independent sessions and values");
            }
            Throws<ArgumentException>(() => prepared.ToListAsync(session));
            using var second = Q(); var extra = second.Parameter("extra", Codecs.Int64); Throws<ArgumentException>(() => prepared.ToListAsync(session, values.Set(extra, 0L)));
        }
        using (var q = Q())
        using (var other = Q())
        {
            var one = q.Parameter("same", Codecs.Int64); var two = other.Parameter("same", Codecs.Int64);
            q.Select(q.ParameterValue(one)); var right = other.Select(other.ParameterValue(two));
            Throws<ArgumentException>(() => q.Select(q.ParameterValue(one)).Combine(right));
        }
        await Done("prepared-isolation");
        using (var q = Q())
        using (var other = Q())
        {
            Throws<ArgumentException>(() => q.Where(other.Column(Models.Id).Equal(0L)));
            Throws<InvalidOperationException>(() => default(SqlExpression<long>).Equal(0L));
            Throws<InvalidOperationException>(() => default(QuerySelection<long>).ToSql());
            q.Where(row =>
            {
                Exception? observed = null;
                var thread = new Thread(() => { try { q.Take(1); } catch (Exception error) { observed = error; } });
                thread.Start(); Check(thread.Join(TimeSpan.FromSeconds(5)), "Foreign-thread composition completes without waiting on owner");
                Check(observed is DatabaseException { Kind: DatabaseErrorKind.ConcurrentUse }, "Concurrent callback composition fails fast");
                return row.Equal(Models.Id, 1L);
            });
            using var clone = q.Clone(); Check(await clone.CountAsync() == 1, "Explicit independent native clone");
            Check((await q.SelectAll().FirstAsync()).Id == 1, "First owns one row and retires");
        }
        using (var q = Q()) { await ThrowsAsync<InvalidOperationException>(() => q.SelectAll().SingleAsync()); }
        using (var q = Q()) { Check(await q.WhereEqual(Models.Id, 99L).SelectAll().SingleOrDefaultAsync() is null, "Reference default cardinality"); }
        using (var q = Q()) { Check(await q.WhereEqual(Models.Id, 99L).Select(q.Column(Models.Id)).FirstOrDefaultAsync() == 0L, "Value type default cardinality"); }
        using (var q = Q()) { var sequence = q.OrderBy(Models.Id).SelectAll().AsAsyncEnumerable(); await using var e = sequence.GetAsyncEnumerator(); Check(await e.MoveNextAsync(), "One-shot lazy enumeration"); Throws<InvalidOperationException>(() => sequence.GetAsyncEnumerator()); }
        using (var q = Q()) { using var canceled = new CancellationTokenSource(); canceled.Cancel(); await ThrowsAsync<OperationCanceledException>(() => q.SelectAll().ToListAsync(canceled.Token)); }
        using (var q = Q()) { q.Dispose(); Throws<ObjectDisposedException>(() => q.Take(1)); }
        using (var q = Q()) await ThrowsAsync<TimeoutException>(() => q.WithTimeout(TimeSpan.Zero).SelectAll().ToListAsync());
        using (var q = Q())
        {
            var failure = new MappingFailure();
            var builder = q.Projection<Person>(); builder.Add(q.Column(Models.Id), "id");
            var projection = builder.Build(_ => throw failure);
            Check(ReferenceEquals(failure, await ThrowsAsync<MappingFailure>(() => q.Select(projection).ToListAsync())), "Fluent constructor error retains original exception after retirement");
        }
        using (var q = Q())
        {
            await using var stream = q.SelectAll().AsAsyncEnumerable().GetAsyncEnumerator();
            Check(await stream.MoveNextAsync(), "Active query row before query disposal"); q.Dispose();
        }
        // Deterministic interleavings of actual native plan publication and Dispose.
        // No fake executor or timing-sensitive thread race supplies these owners.
        using (var q = Q())
        {
            q.SelectAll(); var plan = q.Context.Seal(0); q.Dispose();
            Throws<ObjectDisposedException>(() => q.Context.PublishPlan(plan));
            Check(plan.IsClosed, "Seal/Dispose/Publish releases late native plan");
        }
        using (var q = Q())
        {
            q.SelectAll(); var plan = q.Context.Seal(0); q.Context.PublishPlan(plan); q.Dispose();
            Check(plan.IsClosed, "Seal/Publish/Dispose releases published native plan");
        }
        await Done("owners-streaming-cardinality");
        MeasureComposition(session);
        await Done("direct-composition-cost-input");
        if (session.Source.Provider == DatabaseProvider.Sqlite)
        { using var q = Q(); Throws<DatabaseCapabilityException>(() => q.ForUpdate()); }
        else
        {
            using (var withoutTransaction = Q()) await ThrowsAsync<InvalidOperationException>(() => withoutTransaction.ForUpdate().SelectAll().ToListAsync());
            await using var transaction = await session.BeginTransactionAsync();
            using var q = Q(); Check((await q.WhereEqual(Models.Id, 1L).ForUpdate(RowLockMode.Share, LockWait.NoWait).SelectAll().ToListAsync()).Count == 1, "PostgreSQL explicit transaction row lock");
            await transaction.RollbackAsync();
        }
        using (var q = Q()) Check(Throws<DatabaseException>(() => q.DeleteAsync()).Kind == DatabaseErrorKind.UnsupportedCapability, "Unfiltered native DELETE rejection");
        using (var q = Q()) Check(await q.WhereEqual(Models.Id, 1L).UpdateAsync(setters => setters.Set(Models.Age, q.Column(Models.Age).Add(1))) == 1, "Native filtered setters UPDATE");
        using (var q = Q()) Check(await q.WhereEqual(Models.Id, 1L).UpdateAsync(new Changes<Person>().Set(Models.Name, "Changed")) == 1, "Explicit Changes UPDATE");
        using (var q = Q()) Check((await q.WhereEqual(Models.Id, 1L).SelectAll().SingleAsync()) is { Name: "Changed", Age: 21 }, "Update actual effect");
        using (var q = Q()) Check(await q.WhereEqual(Models.Id, 99L).DeleteAsync() == 0, "Filtered DELETE affected count");
        await Done("mutation-row-lock");
        await session.ExecuteAsync(SqlCommand.Create("DROP TABLE \"Children\"", kind: SqlCommandKind.Mutation));
        await session.ExecuteAsync(SqlCommand.Create("DROP TABLE \"Parents\"", kind: SqlCommandKind.Mutation));
    }
    private static void MeasureComposition(DataSession session)
    {
        void Compose(long value)
        {
            using var query = session.From(Models.People);
            _ = query.WhereEqual(Models.Id, value).Take(1).SelectAll().ToSql();
        }
        Compose(0);
        const int iterations = 64;
        var before = GC.GetAllocatedBytesForCurrentThread(); var started = Stopwatch.GetTimestamp();
        for (var i = 0; i < iterations; i++) Compose(i % 3);
        var elapsed = Stopwatch.GetTimestamp() - started; var allocated = GC.GetAllocatedBytesForCurrentThread() - before;
        int encoded = NativeWeave.Query.Internal.OperandEncoding.Value(session.Source.Binding.SemanticProfile, Codecs.Int64, 3, 1L).Length;
        Check(encoded > sizeof(long) && allocated > 0, "Direct boundary allocations and encoded copies are explicit");
        Costs.Add(new(session.Source.Provider.ToString(), iterations, allocated, elapsed, Stopwatch.Frequency, encoded, 15));
    }
    private sealed class MappingFailure : Exception;
    private sealed record Joined(long Id, long? Child, bool Matched);
    private sealed record Aggregates(long Count, long? Sum, double? Average, long? Min, long? Max);
}
internal sealed record Person(long Id, string Name, int Age, long? Optional);
internal sealed record Child(long Id, long? ParentId);
internal sealed record IdRow(long Id);
internal static class Models
{
    internal static readonly Table<Person> People;
    internal static readonly Column<Person, long> Id;
    internal static readonly Column<Person, string> Name;
    internal static readonly Column<Person, int> Age;
    internal static readonly Column<Person, long?> Optional;
    internal static readonly Table<Child> Children;
    internal static readonly Column<Child, long> ChildId;
    internal static readonly Column<Child, long?> ParentId;
    internal static readonly Table<IdRow> Cte;
    internal static readonly Column<IdRow, long> CteId;
    static Models()
    {
        var p = new TableBuilder<Person>("Parents"); Id = p.Column("Id", Codecs.Int64, new() { IsPrimaryKey = true }); Name = p.Column("Name", Codecs.String); Age = p.Column("Age", Codecs.Int32); Optional = p.Column("Optional", Codecs.Nullable(Codecs.Int64));
        People = p.Build(r => new(r.Get(Id), r.Get(Name), r.Get(Age), r.Get(Optional)), (r, v) => { r.Set(Id, v.Id); r.Set(Name, v.Name); r.Set(Age, v.Age); r.Set(Optional, v.Optional); });
        var c = new TableBuilder<Child>("Children"); ChildId = c.Column("Id", Codecs.Int64, new() { IsPrimaryKey = true }); ParentId = c.Column("ParentId", Codecs.Nullable(Codecs.Int64));
        Children = c.Build(r => new(r.Get(ChildId), r.Get(ParentId)), (r, v) => { r.Set(ChildId, v.Id); r.Set(ParentId, v.ParentId); });
        var cte = new TableBuilder<IdRow>("ChosenParents"); CteId = cte.Column("Id", Codecs.Int64); Cte = cte.Build(r => new(r.Get(CteId)), (r, v) => r.Set(CteId, v.Id));
    }
}
internal sealed record CompositionCost(string Provider, int Iterations, long ManagedAllocatedBytes, long StopwatchTicks, long StopwatchFrequency, int OneInt64WireBytes, int InspectedDirectAbiCallsPerIteration);
internal sealed record Receipt(bool NativeAot, int Assertions, int ManagedRetirements, List<string> Cases, string[] NativeSha256, List<CompositionCost> CompositionCosts);
[JsonSerializable(typeof(Receipt))]
internal partial class ReceiptJson : JsonSerializerContext { }
