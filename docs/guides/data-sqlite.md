# SQLite database provider

`NativeWeave.Database.Sqlite` supplies the SQLite factory and builder extension for
the complete [Database Host](data-nativehost.md). Its candidate package depends on
the shared database facade and the independent `NativeWeave.Database.Sqlite.Native`
asset package. An ordinary C# application uses PackageReference and the precompiled
asset; it needs no Rust toolchain or NativeWeave server/protocol package.

The retained B03 Rust SQLite execution adapter uses SQLx **0.9.0**, Tokio
**1.54.1**, and bundled libsqlite3-sys **0.37.0** / SQLite **3.51.3**. C# owns
configuration and metadata. SQLx owns prepared statements, the physical pool,
transaction depth, and its dedicated SQLite worker. The adapter starts no global
runtime and contains no managed database driver or unconditional `Task.Run` path.

The unchanged declaration and component-oracle checks use NativeWeave-Design commit
[`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`](https://github.com/IzuSharp/NativeWeave-Design/tree/c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9),
especially D14 `docs/database/drivers.md`, D15
`docs/database/transactions-and-pooling.md`, and the exact public API inventory.
`tests/Data.Sqlite/design-inputs.json` retains every task-owned API input hash.

## Public API and Database Host profile

Import `NativeWeave.Database.Sqlite` for `SqliteOptions`, its four enums, and
`SqliteDataSource.Create` / `Engine`. The options are mutable during configuration, then
copied once into B01's canonical kind9 control record. The record has six exact
fields: open mode, journal mode, synchronous mode, BEGIN mode, busy timeout in
nanoseconds, and canonical foreign-key Boolean. No path, SQL, or parameter value
is put into provider error messages.

```csharp
using NativeWeave.Database.Sqlite;

var descriptor = SqliteDataSource.Engine;
var information = descriptor.Inspect();

await using var source = SqliteDataSource.Create("orders.db", options =>
{
    options.BeginMode = SqliteBeginMode.Immediate;
    options.BusyTimeout = TimeSpan.FromMilliseconds(25);
});
await using var session = await source.OpenSessionAsync();
```

`Engine` reads cached metadata and creates no connection or runtime. `Inspect()`
loads the exact precompiled Database Host asset, verifies its generated SHA-256,
architecture and canonical ABI, and reports the implemented capabilities. It
creates no source, worker runtime or database connection; the module remains
resident. `Create` snapshots options and builds a source-owned lazy pool/runtime.
It opens no connection until a session is acquired. Dispose sessions and the source
asynchronously so their retained native work can retire.

| Public profile property | SQLite value |
| --- | --- |
| Engine ID | `database.sqlite` |
| Threading model | `EngineLocalAsync` |
| Bootstrap | `nw_database_sqlite_get_abi_v1` |
| Linux x64 asset | `libnw_database_sqlite.so` |
| Generated output record | `NativeWeave.database.sqlite.assets.json` |

The bootstrap reports **23** capabilities: every name defined in
[`DatabaseEngineProfile`](../../src/Data.NativeHost/DatabaseOptions.cs) except
`db.row-lock.v1` and `db.decimal.numeric.v1`. This includes `db.query.v1`,
transactions/savepoints, streaming, migrations, schema reading, relations and
`db.decimal.text.v1`. The actual advertised mask is composed by the
[native query profile](../../native/database/host/src/query.rs) and
[Host bootstrap](../../native/database/host/src/abi.rs). The private B03 component's
`db.sqlite.profile.v1` bootstrap remains a component-test input; it is not the public
provider descriptor or the packaged Database Host.

The maintainer source project defaults to
`target/release/libnw_database_sqlite.so`, hashes that actual file, and generates
the immutable profile and output record under `obj`. Its ordinary/AOT outputs copy
the asset to `runtimes/linux-x64/native/libnw_database_sqlite.so`. A maintainer can
supply `NativeWeaveSqliteAssetPath`, `NativeWeaveSqliteRuntimeIdentifier`, and
`NativeWeaveSqliteAssetName` as explicit existing-asset inputs. Missing input is a
build error. Consumer MSBuild never invokes Cargo. Candidate NuGet native-leaf
selection and the actual SDK publish layout are checked separately by the
[package consumer gates](packaging-domain.md).

The current compiled inventory contains **32** exact symbols, including these
existing composition declarations:

| Public declaration | Implemented behavior |
| --- | --- |
| `SqliteDataSource.Create(string path, Action<SqliteOptions>? configure = null) : DataSource` | Snapshots options, selects the SQLite Host and calls `Build` with default source limits |
| `DataSourceBuilder.UseSqlite(string path, Action<SqliteOptions>? configure = null) : DataSourceBuilder` | Snapshots options and provider selection on the supplied single-writer builder, without native I/O |
| `SqliteDataSourceBuilderExtensions` | Declares the existing `UseSqlite` extension |

`src/Data.Sqlite/host-composition.expected.json` preserves the original ownership
of those three declarations; they are also included in the integrated
`public-api.expected.json` and [compiled API reference](../../src/Data.Sqlite/api-reference.md).
The builder supports explicit source limits before `Build`; SQLite private-memory
sources require `MaxConnections = 1`. These are existing compiled factories, and
their tests do not execute design stubs.

## Profile and limits

| Setting | Default and policy |
| --- | --- |
| Mode | `ReadWriteCreate`; existing-file `ReadWrite` and `ReadOnly` are explicit |
| Journal | `Wal`; file-backed `Delete` and `Memory` are explicit alternatives |
| Synchronous | `Full`; `Normal` is opt-in |
| Begin | `Deferred`; `Immediate` acquires writer admission before business statements |
| Busy timeout | Five seconds; zero through `Int32.MaxValue` whole milliseconds; finer precision rejects |
| Foreign keys | Enabled on every physical connection |

Plain file paths are UTF-8, nonempty, NUL-free and at most 4096 bytes. URI strings
starting with `file:` are rejected so query-string flags cannot silently override
the admitted provider profile. File-open failures preserve the SQLite extended
result code without echoing the path. Relative paths resolve in the host's current
directory; a deployment should choose its intended location explicitly.

Private memory requires `Mode=Memory`, `JournalMode=Memory`, and exactly one
host-owned physical connection. Shared-cache memory is not enabled. A connection
returned to this one-connection pool retains its private database; another pool
is a different database. Closing the physical connection destroys that database.
The explicit profile rejects WAL/private-memory and multi-connection private
memory combinations before file I/O.

SQLx connect options apply FK, journal, synchronous and busy settings whenever a
physical connection is created. A `Session` receives the original checked-out
`PoolConnection<Sqlite>` and an existing Tokio `Handle`. It does not create a
second pool or silently acquire a replacement connection.

Native `Admission` is shared by the engine. It reserves command count and input
bytes before argument conversion or queued ownership. The finite component
defaults are 32 active/queued commands, 4 MiB retained input reservations, a 64 KiB
SQL limit, one adapter row slot, and 32 cached statements. The host supplies the
acquisition timeout; zero or a duration that overflows the monotonic deadline
is rejected before configuring or opening the SQLx pool. B04 supplies the mapped
host limits; these values do not redefine `DatabaseLimits`' public defaults.
SQLx's native command buffer and row buffer are each explicitly one slot. A
separate one-slot transaction-control admission remains available while business
command capacity is full. Capacity errors return before dispatch; no unbounded
capacity waiters are created by this adapter.

The retained-input reservation covers SQL plus twice the B01 parameter-envelope
bytes: temporary decoded scalar copies and checked SQLx arguments may coexist.
B07 verifies argument expansion against the corresponding bound. This is a
logical owned-copy budget, not a process RSS ceiling. Metadata, allocator
overhead, SQLx/SQLite driver buffers, prepared statements, worker stacks and the
host's runtime are separate owners. B06 owns field and encoded-batch budgets.
A huge SQLite value may already exist in the driver before a B06 field limit
rejects it. `provider_rows_peak` reports adapter-held row objects. The producer
reserves channel capacity before fetching each row: the queue and pending producer
together retain at most one row, and the receiver may hold one more during delivery.
The two-row bound therefore includes the handoff interval after channel capacity
is freed but before the receiver accounts the ownership transfer. A counter guard
also accounts rows dropped after a reserved send races receiver closure. This is separate from SQLx's own
one-row channel and SQLite's current value allocations.

## Execution, cancellation and streams

One retained async actor exclusively owns the physical connection. SQLx's worker
performs native execution. Dropping a business waiter does not drop that actor's
SQLx future or release its input reservation. Public results are sent only after
the operation's native handle barrier and the command admission release.

Each `Cancellation` can be claimed by exactly one operation. Its request path sets
an atomic flag and wakes a native producer waiting on a full row channel. Before
dispatch, the actor installs a native-only progress handler through SQLx's public
`lock_handle` API. The callback only observes atomic state. It never calls managed
code, allocates a result, or waits on a SQLite lock. A late request from an old
generation cannot affect the next operation; reusing the old token rejects.

Progress interruption is cooperative. It cannot promise a deadline for every
SQLite instruction, busy wait, filesystem access, or extension function. After
execution or early row stop, the actor awaits exclusive handle ownership, removes
the handler, clears statements, and probes the tracked transaction state against
SQLite's public autocommit state on that same physical handle. A failed probe
closes admission and quarantines the connection. Statement-reset success is never
inferred merely from dropping the row stream.

`Session::describe` runs SQLx's public `prepare` through the same actor and returns
an owned `SqliteStatement`, including metadata for empty results. It does not add
SQLx's offline tooling feature. Declared columns have their real names/type
metadata; computed NULL/expression types can remain unknown. B06 checks the
admitted projection and then every actual row's storage classes with B07.

`RowStream` contains actual owned SQLx rows and exposes a separate `StopControl`
and `OperationReceipt`. Dropping the stream requests stop. `receipt.join()` waits
for the worker/handler facts; receiver drop alone is not retirement evidence.
`stop_requested` records intent, while `stopped` records the observed terminal
path. Stopping before the next fetch may end the row channel without a SQLx error;
the retirement receipt distinguishes that stopped EOF from natural completion.
The cancellation fixture separately controls a full row channel and an actual
SQLite comparison callback, so actor admission is never treated as proof that
the worker began execution. A fresh finite recursive query exercises progress
after an old generation requests cancellation again. Natural EOF wins a later
cancellation request. Errors retain the native extended code;
INTEGER/REAL/TEXT/BLOB/NULL conversions use B07 rather than
SQLite's permissive affinity coercion. Ordinary SQLite does not acquire PostgreSQL
numeric decimal, row-lock, or isolation semantics through this provider.

## Transactions and physical retirement

`SqliteTransactionDriver` implements B05's narrow Rust provider seam against the
same session actor. Ordinary isolation is Serializable; unsupported requests fail
before BEGIN. Read-only uses a transaction-scoped query-only setting, reset during
the separate recovery path. SQLx's tracked transaction manager implements the
outer BEGIN and nested savepoint admission/release. Rollback-to uses SQLx core's
public generated rollback statement at the current tracked depth without
decrementing it. This keeps the top savepoint available for repeated rollback or
later release and avoids creating hidden nested scopes.

An acknowledged outer COMMIT produces `Confirmation::Committed` immediately.
Later reset/probe errors belong to cleanup and cannot overwrite that durable
confirmation. B05 retains an admitted commit through its own independent timeout.
Unknown remains Unknown after a late successful response or cleanup rollback.
Connection reuse and local owner retirement are separate observations.

Transaction retirement releases the driver's parent session lease before checking
whether an independent parent remains. If that was the last parent, or close was
already requested, B05 waits for the actor's physical-close acknowledgement before
publishing local-resource release. The check occurs after the lease transfer;
checking the owner count before dropping the lease would race a concurrent parent
drop. A usable connection may remain owned by a live independent parent.

`request_close` only stops admission and wakes the retained actor. `close` joins
the SQLx physical-close future while its pool permit remains retained. The receipt
records worker shutdown acknowledgement and physical lease release separately
from OS-thread join. SQLx exposes no JoinHandle; **`os_thread_joined` is always
false**. A shutdown ACK occurs after SQLx drops its connection references but
before its thread closure returns. No hot native-module unloading is enabled.

`return_to_pool` explicitly rolls back any remaining tracked scopes, resets the
profile and probes the original connection, then awaits SQLx's public pool-return
future. This is a pool handoff, not worker destruction; subsequent reuse tests
require a persistent TEMP-table marker. A rejected BEGIN is conservatively
discarded by B05. A replacement worker is explicitly recorded as a replacement.
If SQLx fails to establish a close acknowledgement, B05's retirement future does
not claim safe release; it retains the transaction's cleanup evidence/budget. Host
shutdown must keep the runtime alive until its cleanup ledger is resolved.

## Host preflight and retained component verification

Build the actual SQLite Database Host with the repository's maintainer build first.
For Linux x64 provider preflight and component evidence, run the dedicated verifier
from a clean committed checkout against the pinned Design snapshot:

```sh
python3 tests/Data.Sqlite/verify.py --design /path/to/locked/NativeWeave-Design
```

The maintainer verifier separately builds the private native component and its
test-only ABI fixture. Managed builds consume the prebuilt complete Host asset,
restore with separate ordinary/AOT lock files in locked mode, and verify the exact
**32-symbol** API/XML/reference. Public preflight checks the actual Host engine ID,
capability set, bootstrap, native hash and cached inspection, including that
inspection creates no Host runtime or live owners. The private component bootstrap
is checked independently.

The component suite executes through its test-only ABI in JIT and an actual
`linux-x64` Native AOT executable. The fixture explicitly creates one test runtime
per suite; it is not a product synchronous host wrapper and is not distributed as
a Database engine. Host preflight and component execution remain distinct evidence.

The fourteen scenario groups exercise actual pinned SQLite product paths: every
physical profile, private memory isolation, B07 typed parameters/NULL, FK failure
and repeated savepoint recovery, progress cancellation/stale generations, empty
metadata and early bounded-stream stop, rollback and physical-marker pool reuse,
retained commit after waiter loss/Unknown, count/byte admission, file-backed WAL
read/write contention and atomic same-key conflict, native migration checksum and
failing transactional DDL, read-only/isolation limits, last-parent closure paused
inside actual SQLx connection destruction, and 40,000 real rows crossing the
bounded provider handoff. Migration probes use
SQLx's public tracked `BEGIN IMMEDIATE` outer transaction; they do not implement or
claim B08's migration administration API.

The result file binds source/lock/features, selected upstream source files,
toolchain/assembly/executable hashes, separate private-component and complete-Host
native identities, the generated asset profile/output record, and raw command
stdout/stderr. It verifies that the ordinary and AOT Host output records and copied
files match the staged Host hash, and checks unchanged source bytes after execution.

These fourteen component groups retain their unique provider assertions. Their
runtime results do not establish complete Host query execution or ordinary NuGet
consumption. The [repository verification gate](../verification.md) separately
exercises the assembled database APIs and out-of-tree PackageReference consumers,
including typed Fluent/DTO results in JIT and Native AOT and no-Rust consumption.
This scope targets Linux x64. No other-platform, measured speed, RSS or long-load
acceptance follows from these component tests.
