# Database integration and failure verification

The retained end-to-end surface now tests database calls directly. ApiProbe covers pre-admission commit cancellation with confirmed rollback and no durable row, failed transactions, same physical PostgreSQL sessions, stream admission/release, resource/reference retirement, and nullable/composite relationships formerly embedded in HTTP cases.

```sh
python3 tests/Verification.EndToEnd/api_probe.py \
  --feed /path/to/candidate/feed --version 0.1.0-db-scope.1.2 \
  --output /outside/the/source/database-lifecycle
```

The package driver executes both database providers in JIT and Native AOT. It preserves source/package identities and reports actual rows; it creates no NativeWeave server.

Finite fault cases use the reference database fixture's published artifacts, a PostgreSQL wire proxy and SQLite filesystem faults. These validate database begin/write/commit uncertainty, cancellation, pool return, restart/recovery and outbox consistency. The fixture owns disposable databases/processes and releases them after each case.

Historical HTTP transport/observer and 30-minute soak/performance checks are retired from current execution. Their earlier evidence remains historical. Current batch evidence is recorded in Plan DB-Scope-01.
