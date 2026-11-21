# Transaction outcomes and retained cleanup

B05 implements native transaction admission, effect knowledge, savepoints and
retained cleanup. The exact public scope is `DataTransaction`, `Savepoint`, their
options, result values and exceptions in `NativeWeave.Database`. The immutable
Design input is `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`, C-TX-001 0.4.0.

`src/Data.Transactions` is an unreleased build component. It adds no public
constructor, source factory, physical pool or runtime. B04 composes the internal
transport with the owning `DataSession` and Database facade. These files do not
replace Database Host, add another NuGet package, or publish a public package.
Actual component tests instantiate this internal seam through a test ABI and the
real native coordinator. Provider composition uses B02/B03; a controlled fixture
is not evidence of a real database or assembled host.

## Normal and advanced use

An owning DataSession supplies a transaction after native BEGIN confirms. Its
options are snapshotted before admission. `Isolation = null` means PostgreSQL
ReadCommitted or ordinary SQLite Serializable, with SQLite Deferred/Immediate
selected independently in the provider profile. Exact unsupported isolation and
read-only requests are rejected before BEGIN; no silent downgrade is allowed.
Defaults are a thirty-second commit deadline, five-second cleanup deadline,
`ReadOnly = false` and no recovery key. Native deadlines are finite and nonnegative.

The task-owned, compiled [examples](../../samples/api/data-transactions/TransactionExamples.cs)
accept that confirmed transaction. Minimal code commits and asynchronously joins
local safety. Advanced code catches `CommitOutcomeUnknownException`, retains the
application recovery key and uses an explicit bounded close. An application with
a finite response deadline should not immediately follow a Pending close result
with an unconditional `await using` join.

```csharp
try
{
    await transaction.CommitAsync(requestToken);
}
catch (CommitOutcomeUnknownException error)
{
    await recovery.RecordAsync(error.RecoveryKey, error.CorrelationId);
}
finally
{
    DatabaseCloseResult cleanup = await transaction.CloseAsync(TimeSpan.FromMilliseconds(20));
    // Pending means the engine still owns cleanup, parent leases and callbacks.
}
```

`recovery` above is application policy, not a framework retry service. Scope/tenant,
key and request hash must identify the same business request. The native recovery
value can retain those fields without retaining a physical connection. PostgreSQL
ReadCommitted conflict recovery uses a subsequent SELECT; one missing result in a
same-statement CTE or one cleanup response cannot prove the old transaction rolled
back. B21 owns the complete application idempotency flow.

## Four observations

| Dimension | Values | Meaning |
| --- | --- | --- |
| Transaction state | Active, Failed, CommitInFlight, RollbackInFlight, Closed | Admission of further business operations |
| Transaction outcome | InProgress, Committed, RolledBack, Unknown | Evidence about durable effects |
| Connection disposition | Usable, ProviderResetPending, Quarantined, Discarded | Same-session protocol and reuse safety |
| Native local lifetime | B01 Open, Closing, NativeRetired, Released | D15 Live, Closing, Quiescent, Reclaimed respectively |

The native coordinator reuses B01's outcome/disposition/lifetime types. It does
not define another wire model. Its command gate admits at most one driver operation.
A provider command/cursor holds its `CommandLease` until actual native accessors
retire, independently from cancellation of the caller's waiter. Raw session-mutating
commands are rejected by the framework-owned transaction admission path; the host
and query adapter must correctly classify expert SQL rather than promise a complete
static parser for arbitrary SQL.

### Commit and cancellation

Commit admission atomically checks Active, checks the caller token, enters
CommitInFlight and sets CommitAttempted. The conservative boundary is before the
provider commit method can begin sending. A token canceled earlier leaves Active
and does not call the provider. A request token canceled later cannot cancel that
commit or convert its result to RolledBack.

A separately configured timer runs alongside the pinned driver future. If it
expires, the public operation reports Unknown and closes business admission while
the original driver future keeps running under the retained cleanup owner. The
lease and operation count remain nonzero. The task does not drop a possibly active
SQLite worker future. A later local cleanup or late completion does not silently
replace the Unknown outcome that the application received.

Success requires a trustworthy Committed confirmation. A known Failed transaction
cannot enter commit. A trustworthy provider rollback at commit returns the original
provider failure and RolledBack. A missing confirmation after possible sending
returns `CommitOutcomeUnknownException`; no commit or business delegate is replayed.

### Rollback and close

Explicit RollbackAsync uses its token only for admission. If rollback is
unconfirmed with no COMMIT attempt, the transaction is Closed/InProgress,
CommitAttempted=false, and cleanup eventually records RollbackUnconfirmed.
The connection is quarantined until trusted recovery establishes reuse or physical
retirement completes. Unknown followed by cleanup rollback remains Unknown.

CloseAsync always requests closure before honoring cancellation of its wait. Zero
wait budget is valid. A bounded close can return Pending with
LocalResourcesReleased=false. Cleanup uses the original session and its independent
policy, not an already-canceled request token. Dispose only transfers responsibility;
DisposeAsync joins actual local safety. Ordinary cleanup failures remain in Cleanup
and do not mask an already reported business or Unknown exception. Explicit rollback
still throws its own `DatabaseCleanupException`.

The provider `retire` hook is a join. `close_on_drop` is not proof of completion;
no permit is released early by detaching a still-live connection or worker. The
coordinator marks NativeRetired only after the hook completes, the driver is dropped
and its retained obligations are zero. A remaining snapshot owner is immutable
recovery/observation storage; its final release maps to Released. The managed
transport copies the final observation and retires its native owner before its
DisposeAsync safety join completes. B04 must keep the engine runtime alive until
all such cleanup owners retire.

### Savepoints

Savepoints use native transaction generation and increasing sequence identities;
no user string becomes SQL. Only the top may Rollback/Release. Rollback-to retains
the top scope and restores Active only after provider confirmation. A failed
transaction may recover through the supported rollback-to path; release alone is
not recovery. Release never commits the caller-owned outer transaction.

Disposing an unreleased top savepoint rolls back and releases it. Repeated disposal
or disposal after the outer transaction closes is idempotent. Non-top disposal
records invalid-state cleanup and closes outer admission without reordering SQL.
Stale generations cannot touch a later session owner.

## Provider integration

`nativeweave-data-transactions::TransactionDriver` is an engine-internal Rust seam:

| Hook | Provider responsibility |
| --- | --- |
| capabilities / session_id | Exact profile and original physical identity |
| begin | Enforce exact options and use SQLx tracked transaction BEGIN |
| commit | Trusted Committed or RolledBack with original error; uncertain transport errors remain errors |
| rollback | Confirm rollback and classify protocol state on the original lease |
| savepoint methods | SQLx tracked same-connection nesting; rollback-to retains its top scope |
| recover | Drain/probe/reset only after earlier accessors stop; no blind business replay |
| retire | Join parent/callback/worker obligations and required physical closure before releasing ownership |

No driver object crosses a DLL. Transaction coordination starts no runtime; it uses
the caller's engine-local Tokio executor. Native provider fixtures and managed ABI
fixtures are separate from the eventual B04 native operation table and A06/A07
operation/callback integration. The managed internal `ITransactionTransport` must
preserve the same admission, error and retirement semantics when composed there.

## Costs, API and verification

There is one owned native coordinator/state gate per transaction and one cleanup
owner for admitted terminal work. Snapshot reads copy bounded diagnostic strings;
recovery identity remains separate from native owners. Savepoints retain one stack
entry and one managed wrapper each. Every control call crosses the owning engine
operation boundary; no managed SQL parser, second pool, reflection fallback or
automatic replay is added. Engine source limits/owner budgets remain the host's
responsibility; this component does not claim a process RSS bound.

The [generated API contribution](../../src/Data.Transactions/api-reference.md)
is checked against 79 exact symbols from the pinned Design inventory, including
record-generated members, nullability, defaults, XML and method signatures.

Run the component verifier with the pinned toolchains:

```sh
python3 tests/Data.Transactions/verify.py --output artifacts/B05/component-run
```

An optional `--offline-config` points to an explicitly local SDK-package feed.
That invocation disables unavailable audit refresh only for the local restore;
repository/CI policy remains unchanged. The runner retains raw command logs, exact
source/lock/artifact hashes, compiler/SDK identities, native tests, API checks,
actual JIT and Native AOT execution and honest failure results. Provider-composed
response loss, same-session recovery and pool lifetime tests are separately bound
to the actual B02/B03 implementations before B05 final Linux acceptance. No fixture,
model or historical Design result alone establishes those provider gates.
