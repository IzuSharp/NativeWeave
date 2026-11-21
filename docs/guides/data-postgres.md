# PostgreSQL database provider

`NativeWeave.Database.PostgreSql` supplies the PostgreSQL factory and builder
extension for the complete [Database Host](data-nativehost.md). Its candidate
package depends on the shared database facade and the independent
`NativeWeave.Database.PostgreSql.Native` asset package. An ordinary C# application
uses PackageReference and the precompiled asset, without a Rust toolchain or
NativeWeave server/protocol package.

The retained B02 PostgreSQL adapter uses SQLx 0.9.0 and the canonical B01/B07
contracts. The native component accepts an existing SQLx pool lease and engine
runtime, executes and streams on that fixed physical session, and supplies the
same-session B05 transaction driver. It contains no managed PostgreSQL driver,
second physical pool, global Tokio runtime, or application-specific native model.

The unchanged declaration and component-oracle checks use NativeWeave-Design commit
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. Hashes and the exact current public
symbol inventory are in `src/Data.Postgres/design-inputs.json` and
`public-api.expected.json`. The compiled XML contribution is
[the PostgreSQL API reference](../../src/Data.Postgres/api-reference.md).

## Public API and Database Host profile

The provider exports `PostgreSqlTlsMode`, `PostgreSqlOptions`, and the complete
`PostgreSqlDataSource` factory and descriptor. Constructing options and reading
`Engine` perform no native load or database I/O. `Engine.Inspect()` loads the exact
precompiled Database Host asset, verifies its generated SHA-256, architecture and
canonical ABI, and reports the implemented capabilities. It creates no source,
worker runtime or database connection; the module remains resident.

| Public profile property | PostgreSQL value |
| --- | --- |
| Engine ID | `database.postgresql` |
| Threading model | `EngineLocalAsync` |
| Bootstrap | `nw_database_postgresql_get_abi_v1` |
| Linux x64 asset | `libnw_database_postgresql.so` |
| Generated output record | `NativeWeave.database.postgresql.assets.json` |

The bootstrap reports **24** capabilities: every name defined in
[`DatabaseEngineProfile`](../../src/Data.NativeHost/DatabaseOptions.cs) except
`db.decimal.text.v1`. This includes `db.query.v1`, transactions/savepoints,
streaming, migrations, schema reading, relations, `db.row-lock.v1` and
`db.decimal.numeric.v1`. The actual advertised mask is composed by the
[native query profile](../../native/database/host/src/query.rs) and
[Host bootstrap](../../native/database/host/src/abi.rs). The private B02 component's
`postgres.component.v1` bootstrap remains a component-test input; it is not the
public provider descriptor or the packaged Database Host.

The current compiled inventory contains **15** exact symbols, including these
existing factories:

```csharp
public static NativeWeave.Database.DataSource Create(
    string connectionString, Action<PostgreSqlOptions>? configure = null);

public static NativeWeave.Database.DataSourceBuilder UsePostgreSql(
    this NativeWeave.Database.DataSourceBuilder builder,
    string connectionString, Action<PostgreSqlOptions>? configure = null);
```

The first belongs to `PostgreSqlDataSource`; the second belongs to
`PostgreSqlDataSourceBuilderExtensions`. `UsePostgreSql` snapshots typed options
into the immutable kind8 record and selects the provider without native I/O. The
builder is single-writer and permits explicit source limits before `Build`.
`Create` uses default source limits and calls `Build`, which negotiates the Host
and creates a source-owned lazy pool/runtime without opening a connection or
running migrations. Acquire sessions through `OpenSessionAsync` and dispose both
sessions and source asynchronously.

`src/Data.Postgres/downstream-composition.json` preserves the original ownership
of these declarations; they are included in the integrated
`public-api.expected.json` and compiled reference. They are implemented factories,
not pending declarations or design stubs.

## Configuration and preflight

```csharp
using NativeWeave.Database.PostgreSql;
using NativeWeave.Interop;

// Inspection is optional and opens no database connection.
EngineDescriptor descriptor = PostgreSqlDataSource.Engine;
var information = descriptor.Inspect();

await using var source = PostgreSqlDataSource.Create(
    "postgresql://orders@db.example.test/orders", options =>
{
    options.RootCertificatePath = "/etc/nativeweave/postgres-root.pem";
    options.ApplicationName = "Orders";
    options.ConnectTimeout = TimeSpan.FromSeconds(15);
    // VerifyFull is already the default.
});
await using var session = await source.OpenSessionAsync();
```

The minimum and advanced executable examples live in
`samples/api/data-postgres`. Ordinary `Inspect()` consumes the bounded A02 output
record emitted beside the facade; the advanced example also supplies an explicit
Host asset path through `NW_PG_HOST_ASSET` while retaining hash, architecture, ABI
and `db.query.v1` capability verification.
The maintainer project hashes an actual precompiled native asset into its `obj`
compile input and emits its exact output-location record. The default source input
is `target/release/libnw_database_postgresql.so`. The maintainer properties
`NativeWeavePostgresAssetPath`, `NativeWeavePostgresRuntimeIdentifier`, and
`NativeWeavePostgresAssetName` select explicit existing-asset inputs. Its default
ordinary/AOT output path is
`runtimes/linux-x64/native/libnw_database_postgresql.so`. Missing
input is a build error, never a zero-hash placeholder. No machine-specific ELF hash
is committed or assumed reproducible on another linker/machine. The verifier binds
the generated identity, record, copied file and executable separately. The existing
maintainer build compiles Rust before the solution; an ordinary application
consuming the candidate provider package does not run Cargo. Candidate native-leaf
selection and the actual SDK publish layout are checked separately by the
[package consumer gates](packaging-domain.md).

`PostgreSqlOptions` is mutable configuration; the owning factory snapshots it
before admission. The snapshot validates defined enum values, strict UTF-8 text,
absolute root paths, and a positive connect timeout of at most one hour. The
application name has a 256-byte input cap; PostgreSQL can truncate its display.
Snapshot creation performs bounded copies; it does not open files or connections.

The native connect profile takes a PostgreSQL TCP URI with explicit username and
database. It rejects all query-string options, fragments, Unix-socket host escapes,
and ambient `PG*` connection-policy variables. SQLx's public connect options inherit
those variables, so the component rejects their presence instead of mutating the
process environment or accessing private fields. An absent URI password is made
explicitly empty to disable implicit `.pgpass` fallback. Supply credentials through
the transient outer source configuration; neither config nor provider errors
implement a secret-bearing debug display. Statement logging is disabled.

Production defaults require **VerifyFull**: an authenticated certificate chain and
matching hostname. A supplied absolute PEM root path selects the trusted root;
otherwise native system roots apply. There is no Prefer, Require, hostname bypass
or automatic downgrade mode. `DisableForLocalDevelopment` must be explicitly
selected for plaintext development. TLS failure does not switch modes.

The serialized provider options use the canonical B01 control envelope, kind8:

| Field | Exact type | Meaning |
| --- | --- | --- |
| 1 | u32/type1 | TLS: 0 VerifyFull, 1 explicit development plaintext |
| 2 | strict UTF-8/type4, optional | Absolute root-certificate path |
| 3 | strict UTF-8/type4 | Application name |
| 4 | timeout nanoseconds/type3 | Exact positive connect deadline |

The native adapter consumes the shared checked envelope parser, validates exact
field order/types/widths and allowed values, and copies the admitted fields. Unknown
kinds, duplicate/missing fields, overlaps, malformed UTF-8 and incompatible types
reject before opening. The JIT and AOT tests send the actual managed-produced record
across a narrow test-only ABI, then connect using that snapshot and verify the
actual server `application_name`.

## Session and command ownership

B04 owns pool size, waiter admission, parent/child ownership and runtime shutdown.
B02 accepts one `PoolConnection<Postgres>` and records its real backend PID. A
single atomic operation gate rejects concurrent use instead of serializing user
work in an unbounded queue. An admitted worker owns its connection and parameter
snapshot independently of the business waiter. Closing waits for admitted workers,
including workers that have not acquired the connection mutex yet. It cannot
return a permit ahead of their native accessors.

The fixed session profile sets a finite server `statement_timeout` (30 seconds by
default); cleanup has an independent five-second deadline. SQLx's statement cache
is explicitly bounded (64 entries by default; zero disables it). Configured SQL
input and B07 parameter limits are checked before submission. The B07 `Parameters`
owner is the only scalar binder; every statement builds fresh fallible SQLx
arguments. There is no alternate unchecked binder or managed query implementation.

`Command::generated` is a Rust-local trusted boundary for already capability/type-
checked native SQL. SQLx `AssertSqlSafe` is used only at that boundary; it is not SQL
sanitization. Audited expert SQL carries an explicit `SessionMutating` category.
That category rejects inside a framework-owned transaction and requires physical
closure when its session ends. Ordinary generated operations must not smuggle
transaction control or session mutation into the ordinary category. B04/B11 own
public command admission and this classification; no raw SQLx connection escapes
to managed callers.

Native errors retain a bounded SQLSTATE, category and correlation ID. Raw SQLx
error text, SQL, parameter values and connection strings are not retained. Ordinary
SQLSTATE errors are separate from transport/protocol damage. A failed PostgreSQL
transaction produces `25P02` until rollback; a completed business Task is not
permission to reuse it.

## Streams, stop and retirement

`Session::stream` returns a Rust-local `Stream<Item=Result<PgRow,ProviderError>>`
with an independent cloneable stop/join control. The producer reserves its one-row
channel slot **before** requesting the next SQLx row. The channel holds at most one
row. Receiving releases that slot before the accounting handoff finishes, so one
new queued row and the prior handoff can overlap; the conservative retained-row
counter is bounded by **two**. A single receiver subtracts the previous charge
before it can poll again. This distinction was observed in actual B06 composition.
B06 separately owns decoded rows, wire batches, byte budgets and result-shape
validation. `Session::describe` uses
SQLx's public prepare/statement metadata API, so B06 can validate empty results.

Dropping the business receiver or calling `request_stop` performs an atomic store
and notification. It does not block, send on a bounded I/O channel, acquire a
connection mutex or manufacture a PostgreSQL cancel request from private keys.
The native worker remains responsible for dropping the cursor, sending SQLx Sync
and draining through ReadyForQuery. The retirement receipt follows that cleanup.
A drain deadline closes the session to new work, quarantines it, and awaits physical
closure while `PoolConnection::close` retains its pool permit. Unknown protocol
state never returns to the pool. `detach` and `close_on_drop` are not used as proof
of retirement. Closing a socket is local retirement; it does not prove a remote
transaction's effect or immediate server cancellation.

For clean sessions, the provider explicitly awaits SQLx return-to-pool maintenance;
B04 retains the pool/runtime until all session and operation receipts are joined.
A returned connection is tested by its backend PID, not merely by a successful
query on a possible replacement. A session-mutating command instead requires
physical closure and a replacement lease.

SQLx Execute limit0 requests the full result from the server. The one-row channel
is application backpressure, not server fetch batching or an RSS cap. SQLx protocol
buffers, the caller's current row, B06 wire buffers and CLR DTO copies may coexist.
This component makes no throughput, memory superiority or zero-allocation claim.

## Transactions and Unknown

The B05 `TransactionDriver` implementation uses the same retained session and
SQLx's public tracked transaction manager. PostgreSQL supports ReadCommitted,
RepeatableRead, Serializable and read-only transactions; unsupported isolation
rejects before BEGIN. Savepoint begin/release update tracked depth. Rollback-to uses
SQLx's public `rollback_ansi_transaction_sql(current_depth)` on the same connection
**without decrementing depth**, so the later tracked release addresses the correct
savepoint.

SQLx does not expose the COMMIT-versus-ROLLBACK command tag through its public
transaction-manager result. Before COMMIT, a harmless same-session query verifies
that the transaction is usable. A `25P02` result invokes tracked rollback and
returns explicit `Confirmation::RolledBack`; it cannot be reported as committed.
The ordinary operation gate prevents another application command between the probe
and COMMIT. Missing trustworthy COMMIT confirmation is passed to B05 as an error;
B05 preserves Unknown independently of subsequent cleanup. Successful local
rollback/closure never overwrites that original Unknown business outcome.

The response-loss regression forwards COMMIT through a controlled **test-only**
proxy, observes server `CommandComplete(COMMIT)` and `ReadyForQuery(Idle)`, discards
them, and checks durable state over another connection. The real B05 coordinator
reports Unknown while the observer sees one committed row. This is exercised by
both the JIT and actual Native AOT component consumer.

Migration execution belongs to B08. The B02 regression runs SQLx's real migrator on
a dedicated lease, observes the advisory lock retained after checksum mismatch,
then transfers that lease to the provider's session-mutating retirement path and
joins physical closure. The observer verifies zero advisory locks afterwards. A
failed close does not prove the remote lock disappeared.

## Host preflight and retained component verification

Run from a Linux x64 maintainer checkout with the pinned Rust/.NET toolchains and
PostgreSQL18 binaries available. Build the actual PostgreSQL Database Host with
the repository's maintainer build first, then run against the pinned Design snapshot:

```sh
python3 tests/Data.Postgres/verify.py \
  --output artifacts/B02/attempt-001 \
  --design-root /path/to/locked/NativeWeave-Design \
  --postgres-bin /path/to/postgres18/bin
```

Offline SDK/AOT packages can be selected with `--offline-config /path/to/NuGet.Config`.
The verifier separately builds the private native component and test-only fixture.
It supplies the exact precompiled complete Host asset to the C# build and checks
the integrated **15-symbol** API/XML/reference. Generated asset metadata stays under `obj`; source
files remain unchanged. `--write-reference` regenerates the compiled reference
before the final unchanged-source run; `--update-locks` is an explicit preparation
step, while normal verification requires locked restores. No test silently succeeds when PostgreSQL or TLS inputs are
missing. The verifier owns three disposable TCP server instances (verified TLS,
expired certificate and plaintext) and shuts them down in its own process lifetime.

The real regression groups cover all six Design PostgreSQL oracles: timeout and
rollback; early stream drop; codecs; durable COMMIT response loss; conflict CTE old
snapshot requiring the next SELECT; and migration advisory-lock cleanup. Additional
rows cover TLS wrong hostname/untrusted root/expired certificate/plaintext opt-in,
B05 savepoint rollback-to/release, cancellation before commit dispatch, unsupported
isolation, bounded admission, empty-result metadata, drain-timeout retirement,
server-terminated sessions and restored pool permits. Managed tests add exact option
snapshots and malformed native records. Public preflight checks the actual Host
engine ID, capability set, bootstrap, native hash and cached inspection, including
that inspection creates no Host runtime or live owners. The private component
bootstrap is checked independently. The same real provider suite executes through
a separate test-only ABI in JIT and Linux Native AOT; these provider assertions do
not depend on replacing the component fixture with a Host-only smoke test.

Evidence binds exact source, locks, features, toolchains, native and managed artifact
hashes, server identity, certificate identities, commands, outcomes and cleanup.
Private-component and complete-Host native identities are recorded separately.
Ordinary and AOT Host output records and copied files must match the staged Host
hash. The test ABI is not shipped as an application-facing provider surface.

Host preflight and component execution remain distinct evidence. Their results do
not establish complete Host query execution or ordinary NuGet consumption. The
[repository verification gate](../verification.md) separately exercises assembled
database APIs and out-of-tree PackageReference consumers, including typed
Fluent/DTO results in JIT and Native AOT and no-Rust consumption. This scope targets
Linux x64; these component tests imply no Windows, long-load or performance
acceptance. Independent review and final batch acceptance remain separate.

### Transaction parent retirement

The B05 provider retirement hook consumes its own Session lease before it returns.
A retained driver value is inert afterward. An independent live Session may keep
its clean lease; if no such owner remains or close has already been requested, the
hook joins the actual pool-return or physical-close receipt. The last-owner check
occurs after releasing the driver parent, avoiding a concurrent parent-drop window.
The real-provider oracle checks both an already-dropped parent and a parent dropped
after driver retirement while the driver value remains alive.
