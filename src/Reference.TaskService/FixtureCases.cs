using System.Text;
using System.Text.Json;
using NativeWeave.Data;
using NativeWeave.Database;

namespace NativeWeave.Reference.TaskService;

/// <summary>Internal finite scenarios preserve application database invariants without a transport host.</summary>
internal sealed class FixtureCases(ServiceConfiguration configuration, TaskService service, OutboxWorker outbox, BlobStore blobs)
{
    internal List<FixtureReply> Replies { get; } = [];
    internal Dictionary<string, string> Checks { get; } = [];
    private AuthIdentity Identity => new(configuration.Principals[0].Tenant, configuration.Principals[0].Principal, configuration.Principals[0].CanWrite);

    private void Check(string name, bool passed, string observation = "passed")
    {
        if (!passed) throw new InvalidOperationException("fixture:" + name);
        Checks.Add(name, observation);
    }

    private void Add(Replay reply) => Replies.Add(new(reply.Status, Convert.ToHexStringLower(reply.Bytes), reply.OperationId, ProviderCode: reply.ProviderCode));

    internal async Task RunAsync(string mode, CancellationToken token)
    {
        var identity = Identity;
        switch (mode)
        {
            case "--conflict-case":
                var replies = await Task.WhenAll(service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token),
                    service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token)).ConfigureAwait(false);
                Check("concurrent-idempotency", replies.All(x => x.Status == 201) && replies[0].Bytes.AsSpan().SequenceEqual(replies[1].Bytes));
                foreach (var reply in replies) Add(reply);
                break;
            case "--unknown-case":
                var unknown = await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false);
                Add(unknown);
                var problem = JsonSerializer.Deserialize(unknown.Bytes, AppJson.Default.Problem);
                Check("commit-unknown-distinct", unknown.Status == 503 && problem?.Code == "outcome_unknown" && problem.OperationId == unknown.OperationId);
                try { Add(await service.RecoverAsync(identity, unknown.OperationId, token).ConfigureAwait(false)); }
                catch (ApplicationProblem error) when (error.Status == 404) { Replies.Add(new(404, "", unknown.OperationId, error.Code)); }
                var replay = await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false);
                Add(replay);
                Check("retry-after-unknown", replay.Status == 201);
                if (Replies[1].Status == 200) Check("recovery-matches-replay", Replies[1].BytesHex == Replies[2].BytesHex);
                Check("unknown-recovery-protected", File.Exists(Path.Combine(blobs.Recovery, unknown.OperationId + ".json")));
                break;
            case "--failure-case":
                bool failed = false;
                try { Add(await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false)); }
                catch (DatabaseException error) { Replies.Add(new(0, "", "", error.Kind.ToString(), error.ProviderCode)); failed = true; }
                Check("database-failure-observed", failed);
                break;
            case "--attachment-case":
                var parent = (await service.ListAsync(identity, 1, null, token).ConfigureAwait(false)).Items.Single();
                await using (var upload = blobs.Begin(identity, parent.ItemId, configuration.CaseKey, 1, AttachmentPayload.Length))
                {
                    using var input = new MemoryStream(AttachmentPayload, false);
                    await upload.StageAsync(input, token).ConfigureAwait(false);
                    var attached = await service.BindAttachmentAsync(identity, configuration.CaseKey, parent.ItemId, 1, upload, token).ConfigureAwait(false);
                    upload.Complete(attached); Add(attached);
                    Check("attachment-committed", attached.Status == 200);
                }
                await ReadAttachmentAsync(parent.ItemId, token).ConfigureAwait(false);
                break;
            case "--read-attachment-case":
                var selected = (await service.ListAsync(identity, 1, null, token).ConfigureAwait(false)).Items.Single();
                await ReadAttachmentAsync(selected.ItemId, token).ConfigureAwait(false);
                break;
            case "--create-case":
                Add(await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false));
                break;
            case "--retry-case":
                try { Add(await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false)); }
                catch (DatabaseException error) { Replies.Add(new(0, "", "", error.Kind.ToString(), error.ProviderCode)); }
                Add(await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false));
                Check("retry-succeeds", Replies[^1].Status == 201);
                break;
            case "--keyset-case":
                await KeysetAsync(token).ConfigureAwait(false);
                break;
            case "--outbox-once":
                Checks.Add("delivered", (await outbox.RunOnceAsync(token).ConfigureAwait(false)).ToString(System.Globalization.CultureInfo.InvariantCulture));
                break;
            case "--maintenance-once":
                Checks.Add("maintenance", JsonSerializer.Serialize(await service.MaintainAsync(token).ConfigureAwait(false), AppJson.Default.MaintenanceReport));
                break;
            default:
                await VerifyAsync(token).ConfigureAwait(false);
                break;
        }
    }

    private static readonly byte[] AttachmentPayload = Encoding.UTF8.GetBytes(string.Concat(Enumerable.Repeat("Database immutable attachment\n", 4096)));

    private async Task ReadAttachmentAsync(string itemId, CancellationToken token)
    {
        var attachment = await service.AttachmentAsync(Identity, itemId, token).ConfigureAwait(false);
        await using var content = blobs.Open(attachment);
        using var copied = new MemoryStream();
        await content.CopyToAsync(copied, token).ConfigureAwait(false);
        Check("reachable-attachment-content", attachment.Version == 2 && copied.ToArray().AsSpan().SequenceEqual(AttachmentPayload));
    }

    private async Task KeysetAsync(CancellationToken token)
    {
        List<string> collected = [];
        string? cursor = null, firstCursor = null;
        bool complete = false;
        for (int pageIndex = 0; pageIndex < 128; pageIndex++)
        {
            var page = await service.ListAsync(Identity, 2, cursor, token).ConfigureAwait(false);
            Check("keyset-page-bound-" + pageIndex, page.Items.Length <= 2);
            Check("keyset-real-tie-" + pageIndex, page.Items.All(item => item.CreatedAt == 1_790_000_000_000));
            collected.AddRange(page.Items.Select(item => item.ItemId));
            firstCursor ??= page.NextCursor;
            cursor = page.NextCursor;
            if (cursor is null) { complete = true; break; }
        }
        Check("keyset-complete-termination", complete);
        Check("keyset-multiple-tied-pages", collected.Count >= 8 && firstCursor is not null);
        Check("keyset-no-duplicate-ids", collected.Count == collected.Distinct(StringComparer.Ordinal).Count());
        Checks.Add("keyset-observed-item-order", string.Join(',', collected));
        string validCursor = firstCursor!;
        int position = validCursor.Length / 2;
        string tampered = validCursor[..position] + (validCursor[position] == 'A' ? 'B' : 'A') + validCursor[(position + 1)..];
        await RejectedCursorAsync("tampered-valid-cursor-rejected", Identity, tampered, token).ConfigureAwait(false);
        await RejectedCursorAsync("cross-tenant-valid-cursor-rejected",
            new(Identity.Tenant + "-other", Identity.Principal, true), validCursor, token).ConfigureAwait(false);
        await RejectedCursorAsync("cross-principal-valid-cursor-rejected",
            new(Identity.Tenant, Identity.Principal + "-other", true), validCursor, token).ConfigureAwait(false);
    }

    private async Task RejectedCursorAsync(string name, AuthIdentity identity, string cursor, CancellationToken token)
    {
        bool rejected = false;
        try { await service.ListAsync(identity, 2, cursor, token).ConfigureAwait(false); }
        catch (ApplicationProblem error) when (error.Status == 400) { rejected = true; }
        Check(name, rejected);
    }

    private async Task VerifyAsync(CancellationToken token)
    {
        var identity = Identity;
        var first = await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false);
        var replay = await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false);
        Add(first); Add(replay);
        Check("durable-idempotency-replay", first.Status == 201 && replay.Status == 201 && first.Bytes.AsSpan().SequenceEqual(replay.Bytes));
        bool conflict = false;
        try { await service.CreateAsync(identity, configuration.CaseKey, new(configuration.CaseTitle + " changed"), token).ConfigureAwait(false); }
        catch (ApplicationProblem error) when (error.Status == 409) { conflict = true; }
        Check("idempotency-conflict", conflict);
        AuthIdentity foreignTenant = new(identity.Tenant + "-other", identity.Principal, true);
        AuthIdentity foreignPrincipal = new(identity.Tenant, identity.Principal + "-other", true);
        Add(await service.CreateAsync(foreignTenant, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false));
        Add(await service.CreateAsync(foreignPrincipal, configuration.CaseKey, new(configuration.CaseTitle), token).ConfigureAwait(false));
        Check("tenant-principal-scopes", Replies.Skip(1).Select(x => x.OperationId).Distinct().Count() == 3);
        var firstPage = await service.ListAsync(identity, 1, null, token).ConfigureAwait(false);
        var secondPage = await service.ListAsync(identity, 1, firstPage.NextCursor, token).ConfigureAwait(false);
        Check("typed-keyset-pages", firstPage.Items.Length == 1 && secondPage.Items.Length == 1 && firstPage.Items[0].ItemId != secondPage.Items[0].ItemId);
        bool badCursor = false;
        try { await service.ListAsync(identity, 1, "invalid-cursor", token).ConfigureAwait(false); }
        catch (ApplicationProblem error) when (error.Status == 400) { badCursor = true; }
        Check("cursor-authentication", badCursor);
        var recovered = await service.RecoverAsync(identity, first.OperationId, token).ConfigureAwait(false);
        Check("typed-recovery", recovered.Status == 200 && recovered.Bytes.AsSpan().SequenceEqual(first.Bytes));
        bool foreignRecovery = false;
        try { await service.RecoverAsync(foreignPrincipal, first.OperationId, token).ConfigureAwait(false); }
        catch (ApplicationProblem error) when (error.Status == 404) { foreignRecovery = true; }
        Check("recovery-principal-scope", foreignRecovery);
        var item = JsonSerializer.Deserialize(first.Bytes, AppJson.Default.CreatedItem) ?? throw new InvalidOperationException("fixture:created-dto");
        byte[] payload = Encoding.UTF8.GetBytes("database fixture attachment 世界");
        await using (var upload = blobs.Begin(identity, item.ItemId, configuration.CaseKey + "-attachment", 1, payload.Length))
        {
            using var input = new MemoryStream(payload, false);
            await upload.StageAsync(input, token).ConfigureAwait(false);
            var attached = await service.BindAttachmentAsync(identity, configuration.CaseKey + "-attachment", item.ItemId, 1, upload, token).ConfigureAwait(false);
            upload.Complete(attached); Add(attached);
            Check("typed-optimistic-attachment", attached.Status == 200);
        }
        var attachment = await service.AttachmentAsync(identity, item.ItemId, token).ConfigureAwait(false);
        await using (var content = blobs.Open(attachment))
        using (var copied = new MemoryStream())
        {
            await content.CopyToAsync(copied, token).ConfigureAwait(false);
            Check("attachment-bytes-and-version", attachment.Version == 2 && copied.ToArray().AsSpan().SequenceEqual(payload));
        }
        bool stale = false;
        await using (var upload = blobs.Begin(identity, item.ItemId, configuration.CaseKey + "-stale", 1, payload.Length))
        {
            using var input = new MemoryStream(payload, false);
            await upload.StageAsync(input, token).ConfigureAwait(false);
            try { await service.BindAttachmentAsync(identity, configuration.CaseKey + "-stale", item.ItemId, 1, upload, token).ConfigureAwait(false); }
            catch (ConcurrencyConflictException) { stale = true; }
        }
        Check("optimistic-conflict-rolls-back", stale);
        Check("outbox-delivery", await outbox.RunOnceAsync(token).ConfigureAwait(false) == 4);
        Check("outbox-replay-no-duplicate", await outbox.RunOnceAsync(token).ConfigureAwait(false) == 0);
        var maintenance = await service.MaintainAsync(token).ConfigureAwait(false);
        Check("fresh-durable-records-retained", maintenance.DeletedOperations == 0 && maintenance.DeletedOutbox == 0);
    }
}
