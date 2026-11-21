using System.Text.Json;
using NativeWeave.Data;
using NativeWeave.Database;
using NativeWeave.Query;

namespace NativeWeave.Reference.TaskService;

/// <summary>Application transaction orchestration over the existing Rust DB/ORM engine.</summary>
internal sealed partial class TaskService(DataSource source, CursorCodec cursors, BlobStore blobs)
{
    internal static readonly TimeSpan CleanupWait = TimeSpan.FromMilliseconds(100);
    private static readonly Projection<string> ClaimedOperation = Projection<string>.Create(
        [ResultField.Create("operation_id", Codecs.String)], row => row.Read(0, Codecs.String));

    internal static async Task MigrateAsync(DataSource database, string name, CancellationToken token = default)
    {
        using Stream stream = typeof(TaskService).Assembly.GetManifestResourceStream($"NativeWeave.Reference.TaskService.Migrations.{name}.sql")
            ?? throw new InvalidOperationException("The explicit migration resource is missing.");
        using StreamReader reader = new(stream, Canonical.Utf8);
        var bundle = new MigrationBundle(database.Provider, [new Migration(1, "Reference service v1 " + name, await reader.ReadToEndAsync(token))]);
        await database.Administration.MigrateAsync(bundle, cancellationToken: token).ConfigureAwait(false);
    }

    internal async Task<Replay> CreateAsync(AuthIdentity identity, string key, CreateItem command, CancellationToken token)
    {
        Canonical.ValidateTitle(command.Title); key = Canonical.Key(key);
        string operation = Guid.NewGuid().ToString("D"); string itemId = Guid.NewGuid().ToString("D");
        long now = Now();
        byte[] response = JsonSerializer.SerializeToUtf8Bytes(new CreatedItem(1, operation, itemId, command.Title, now, 1), AppJson.Default.CreatedItem);
        var result = new OperationResult(Canonical.Scope(identity, Canonical.CreateSemantic), key, Canonical.CreateHash(identity, command.Title), operation,
            identity.Tenant, identity.Principal, Canonical.CreateSemantic, 1, 201, response, now);
        using var cleanup = ReserveProtectionRetirement();
        var session = await source.OpenSessionAsync(token).ConfigureAwait(false);
        DataTransaction? transaction = null;
        bool protectedCommit = false;
        try
        {
            transaction = await session.BeginTransactionAsync(new() { RecoveryKey = operation, CommitTimeout = TimeSpan.FromSeconds(15) }, token).ConfigureAwait(false);
            var existing = await ClaimAsync(session, result, token).ConfigureAwait(false);
            if (existing is not null) return existing;
            await session.InsertAsync(Items.Table, new Item(identity.Tenant, itemId, operation, command.Title, now, 1), token).ConfigureAwait(false);
            await session.InsertAsync(Outbox.Table, NewEvent(result), token).ConfigureAwait(false);
            protectedCommit = true;
            blobs.ProtectCommit(result);
            var committed = await CommitAsync(transaction, result, token).ConfigureAwait(false);
            if (committed.Status != 503) { blobs.ConfirmCommit(operation); protectedCommit = false; }
            return committed;
        }
        finally
        {
            await CloseSessionAsync(session).ConfigureAwait(false);
            if (protectedCommit && transaction is not null) cleanup.Transfer(transaction, () => blobs.ConfirmCommit(operation));
            else transaction?.Dispose();
        }
    }

    /// <summary>One explicit expert SQL claim; ordinary reads and business mutations use typed native-backed metadata.</summary>
    private static async Task<Replay?> ClaimAsync(DataSession session, OperationResult candidate, CancellationToken token)
    {
        // UpsertAsync intentionally requires DO UPDATE and is not a DO NOTHING claim.
        // Both providers accept this fixed trusted recipe. Rust owns placeholder binding and dispatch.
        var parameters = new SqlParameters().Add("scope", candidate.Scope, Codecs.String).Add("key", candidate.RequestKey, Codecs.String)
            .Add("hash", candidate.RequestHash, Codecs.String).Add("operation", candidate.OperationId, Codecs.String)
            .Add("tenant", candidate.Tenant, Codecs.String).Add("principal", candidate.Principal, Codecs.String)
            .Add("semantic", candidate.Semantic, Codecs.String).Add("version", candidate.ResponseVersion, Codecs.Int64)
            .Add("status", candidate.ResponseStatus, Codecs.Int64).Add("response", candidate.ResponseBytes, Codecs.Bytes).Add("completed", candidate.CompletedAt, Codecs.Int64);
        var claim = SqlCommand.Create("INSERT INTO operations(scope,request_key,request_hash,operation_id,tenant_id,principal_id,semantic,response_version,response_status,response_bytes,completed_at) VALUES (@scope,@key,@hash,@operation,@tenant,@principal,@semantic,@version,@status,@response,@completed) ON CONFLICT(scope,request_key) DO NOTHING RETURNING operation_id", parameters);
        IReadOnlyList<string> inserted = await session.QueryAsync(claim, ClaimedOperation, token).ConfigureAwait(false);
        if (inserted.Count == 1 && inserted[0] == candidate.OperationId) return null;
        if (inserted.Count != 0) throw new InvalidOperationException("The claim result violated its one-row invariant.");
        // Required next statement: a fresh PostgreSQL ReadCommitted snapshot after DO NOTHING.
        OperationResult? winner = await session.FindAsync(Operations.Table, Operations.Table.Key(Operations.Scope, candidate.Scope).And(Operations.RequestKey, candidate.RequestKey), token).ConfigureAwait(false);
        if (winner is null) throw new ApplicationProblem(503, "outcome_unconfirmed");
        if (winner.Scope != candidate.Scope || winner.Tenant != candidate.Tenant || winner.Principal != candidate.Principal || winner.Semantic != candidate.Semantic)
            throw new InvalidOperationException("A scoped operation violated its persisted identity.");
        if (winner.RequestHash != candidate.RequestHash) throw new ApplicationProblem(409, "idempotency_conflict");
        if (winner.ResponseVersion != 1 || winner.ResponseBytes.Length > 1_048_576) throw new InvalidOperationException("Unsupported durable response version or size.");
        return new(checked((int)winner.ResponseStatus), winner.ResponseBytes, winner.OperationId);
    }

    private static OutboxEvent NewEvent(OperationResult result) => new(Guid.NewGuid().ToString("D"), result.Tenant, result.OperationId, 1, result.ResponseBytes, 0, 0, result.CompletedAt, 0, 0);

    private static async Task<Replay> CommitAsync(DataTransaction transaction, OperationResult result, CancellationToken token)
    {
        try
        {
            await transaction.CommitAsync(token).ConfigureAwait(false);
            return new(checked((int)result.ResponseStatus), result.ResponseBytes, result.OperationId);
        }
        catch (CommitOutcomeUnknownException error)
        {
            return new(503, JsonSerializer.SerializeToUtf8Bytes(new Problem("outcome_unknown", result.OperationId,
                "/v1/operations/" + result.OperationId, error.CorrelationId), AppJson.Default.Problem), result.OperationId, error.ProviderCode);
        }
    }

    internal async Task<ItemPage> ListAsync(AuthIdentity identity, int limit, string? after, CancellationToken token)
    {
        if (limit is < 1 or > 100) throw new ApplicationProblem(400, "invalid_limit");
        var cursor = after is null ? ((long CreatedAt, string ItemId)?)null : cursors.Decode(identity, after);
        var session = await source.OpenSessionAsync(token).ConfigureAwait(false);
        try
        {
            using var query = session.From(Items.Table);
            query.WhereEqual(Items.Tenant, identity.Tenant);
            if (cursor is { } value)
                query.Where(query.Column(Items.CreatedAt).GreaterThan(value.CreatedAt)
                    .Or(query.Column(Items.CreatedAt).Equal(value.CreatedAt).And(query.Column(Items.ItemId).GreaterThan(value.ItemId))));
            var rows = await query.OrderBy(Items.CreatedAt).ThenBy(Items.ItemId).Take(limit).SelectAll().ToListAsync(token).ConfigureAwait(false);
            var items = rows.Select(row => new ItemView(row.ItemId, row.Title, row.CreatedAt, row.Version)).ToArray();
            string? next = rows.Count == limit ? cursors.Encode(identity, rows[^1].CreatedAt, rows[^1].ItemId) : null;
            return new(items, next);
        }
        finally { await CloseSessionAsync(session).ConfigureAwait(false); }
    }

    internal async Task<Replay> RecoverAsync(AuthIdentity identity, string operationId, CancellationToken token)
    {
        operationId = Canonical.Id(operationId);
        var session = await source.OpenSessionAsync(token).ConfigureAwait(false);
        try
        {
            using var query = session.From(Operations.Table);
            var result = await query.WhereEqual(Operations.OperationId, operationId).WhereEqual(Operations.Tenant, identity.Tenant)
                .WhereEqual(Operations.Principal, identity.Principal).SelectAll().SingleOrDefaultAsync(token).ConfigureAwait(false);
            if (result is null) throw new ApplicationProblem(404, "outcome_unconfirmed");
            if (result.Scope != Canonical.Scope(identity, result.Semantic) || result.ResponseVersion != 1) throw new InvalidOperationException("Operation scope/version mismatch.");
            return new(200, result.ResponseBytes, result.OperationId);
        }
        finally { await CloseSessionAsync(session).ConfigureAwait(false); }
    }

    internal async Task<Item> AuthorizeItemAsync(AuthIdentity identity, string itemId, CancellationToken token)
    {
        itemId = Canonical.Id(itemId);
        var session = await source.OpenSessionAsync(token).ConfigureAwait(false);
        try
        {
            return await session.FindAsync(Items.Table, Items.Table.Key(Items.Tenant, identity.Tenant).And(Items.ItemId, itemId), token).ConfigureAwait(false)
            ?? throw new ApplicationProblem(404, "not_found");
        }
        finally { await CloseSessionAsync(session).ConfigureAwait(false); }
    }

    internal async Task<Attachment> AttachmentAsync(AuthIdentity identity, string itemId, CancellationToken token)
    {
        itemId = Canonical.Id(itemId);
        var session = await source.OpenSessionAsync(token).ConfigureAwait(false);
        try
        {
            return await session.FindAsync(Attachments.Table, Attachments.Table.Key(Attachments.Tenant, identity.Tenant).And(Attachments.ItemId, itemId), token).ConfigureAwait(false)
            ?? throw new ApplicationProblem(404, "not_found");
        }
        finally { await CloseSessionAsync(session).ConfigureAwait(false); }
    }

    internal async Task<Replay> BindAttachmentAsync(AuthIdentity identity, string key, string itemId, long expectedVersion, BlobStore.UploadLease lease, CancellationToken token)
    {
        var upload = lease.Manifest;
        long nextVersion = checked(expectedVersion + 1); long now = Now();
        byte[] response = JsonSerializer.SerializeToUtf8Bytes(new AttachedItem(1, upload.OperationId, itemId, upload.ContentHash!, upload.ContentLength, nextVersion), AppJson.Default.AttachedItem);
        var result = new OperationResult(Canonical.Scope(identity, Canonical.AttachSemantic), key,
            Canonical.AttachmentHash(identity, itemId, upload.ContentHash!, upload.ContentLength, expectedVersion), upload.OperationId,
            identity.Tenant, identity.Principal, Canonical.AttachSemantic, 1, 200, response, now);
        using var cleanup = ReserveProtectionRetirement();
        var session = await source.OpenSessionAsync(token).ConfigureAwait(false);
        DataTransaction? transaction = null;
        try
        {
            transaction = await session.BeginTransactionAsync(new() { RecoveryKey = result.OperationId, CommitTimeout = TimeSpan.FromSeconds(15) }, token).ConfigureAwait(false);
            lease.BeginDatabaseBinding();
            var existing = await ClaimAsync(session, result, token).ConfigureAwait(false);
            if (existing is not null) return existing;
            var keyValue = Items.Table.Key(Items.Tenant, identity.Tenant).And(Items.ItemId, itemId);
            await session.UpdateCheckedAsync(Items.Table, keyValue, new Changes<Item>().Set(Items.Version, nextVersion), new ConcurrencyCheck<Item>().Expect(Items.Version, expectedVersion), token).ConfigureAwait(false);
            var attachment = new Attachment(identity.Tenant, itemId, upload.ContentHash!, upload.ContentLength, result.OperationId, nextVersion);
            await session.UpsertAsync(Attachments.Table, attachment,
                ConflictTarget<Attachment>.Columns(Attachments.Tenant).And(Attachments.ItemId),
                new Changes<Attachment>().Set(Attachments.ContentHash, attachment.ContentHash).Set(Attachments.ContentLength, attachment.ContentLength)
                    .Set(Attachments.OperationId, attachment.OperationId).Set(Attachments.Version, attachment.Version), token).ConfigureAwait(false);
            await session.InsertAsync(Outbox.Table, NewEvent(result), token).ConfigureAwait(false);
            return await CommitAsync(transaction, result, token).ConfigureAwait(false);
        }
        finally
        {
            await CloseSessionAsync(session).ConfigureAwait(false);
            if (transaction is not null) cleanup.Transfer(transaction, () => blobs.ConfirmRecoveredUpload(upload.OperationId));
        }
    }

    /// <summary>Finite application cleanup transfers unfinished obligations to the database engine.</summary>
    internal static async Task CloseSessionAsync(DataSession session)
    {
        try
        {
            var result = await session.CloseAsync(CleanupWait).ConfigureAwait(false);
            if (!result.LocalResourcesReleased) Console.Error.WriteLine($"database_cleanup status={result.Status} disposition={result.ConnectionDisposition} released=false");
        }
        catch (Exception error) { Console.Error.WriteLine("database_cleanup_failure type=" + error.GetType().Name); session.Dispose(); }
    }

    internal static long Now() => DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
}
