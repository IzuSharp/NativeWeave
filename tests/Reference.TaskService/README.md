# Direct database application regression

The historical `Reference.TaskService` path now contains a finite console fixture. It calls the existing C# application query methods directly through ordinary `NativeWeave.Database.Sqlite` and `NativeWeave.Database.PostgreSql` package references. It creates no HTTP, gRPC or MCP listener and installs no NativeWeave server package.

The fixture preserves explicit migrations, static entity and DTO metadata, strongly typed CRUD and keyset queries, scoped idempotency, optimistic concurrency, a separate durable outbox consumer, recovery after uncertain commits, cancellation/cleanup, and database references to staged files. The application and filesystem logic are internal regression fixtures, not a new public ORM or server API.

## Run the complete candidate matrix

From the repository, with .NET, a C compiler and PostgreSQL tools on PATH:

```bash
export NW_TEST_POSTGRES='postgresql://nativeweave@127.0.0.1:5432/postgres'
python3 tests/Reference.TaskService/package_probe.py \
  --feed /absolute/candidate/feed --version 0.1.0-db-scope.1.2 \
  --output /absolute/outside-source/database-reference
```

The default executes SQLite and PostgreSQL under JIT and Native AOT. Each row also executes every finite database fault scenario in `tests/Verification.EndToEnd/run.py`. The fault runner creates its own PostgreSQL cluster for restart tests; it never restarts the `NW_TEST_POSTGRES` instance. Both the PostgreSQL binaries and the output directory must be available to an unprivileged user.

Consumer builds are outside the source tree with an isolated NuGet cache and an exact local candidate package source. They resolve candidate-bound lock files and immediately verify locked restore. The feed may version shared packages separately from the provider facade specified by `--version`. The complete 12-package database closure and both native hashes are recorded. Cargo, rustc and rustup are replaced by rejecting traps in the consumer environment. Every runtime row checks `RuntimeFeature.IsDynamicCodeSupported` and independent SQLite/psql observations; no source project reference enters the consumer graph.

For an already-built executable, run the direct application checks:

```bash
python3 tests/Reference.TaskService/run.py --provider sqlite \
  --database /absolute/new/application.sqlite --mode jit \
  --output /absolute/new/receipt \
  -- dotnet /absolute/consumer/NativeWeave.Reference.TaskService.dll
```

PostgreSQL rows additionally pass `--postgres-oracles`. The standalone `run.py` tests application behavior; complete candidate acceptance uses `package_probe.py`, which also runs the fault matrix.

## Independent evidence

`golden.py` and `golden-v1.json` freeze durable version-1 framing and serialized response bytes. Persisted semantic strings such as `POST /v1/items` and numeric response statuses remain unchanged for this compatibility check; no routes are installed. Changing those strings would change existing durable hashes.

`run.py` reconciles operation/item/outbox atomicity, attachment version, stored replay bytes, consumer deduplication, SQLite integrity and foreign keys. It independently forces equal creation timestamps, traverses every two-row keyset page and compares the complete result with SQL ordering; valid-cursor tampering and cross-tenant/principal reuse must be rejected. It also restarts finite processes to check redelivery, the seven-day replay window, expired-key reuse, recovery markers, pending-outbox protection, orphan grace and protected content.

`postgres_oracles.py` preserves the actual concurrent lock-wait witness and the discarded COMMIT acknowledgment witness. See [postgres-oracles.md](postgres-oracles.md). Fresh output is mandatory for each matrix attempt. A nonzero exit, a missing receipt, an unavailable required prerequisite or an incomplete case fails acceptance. Earlier B21 delivery evidence remains at its original source identity and is not reused as a current pass.
