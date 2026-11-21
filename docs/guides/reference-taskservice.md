# Direct database business fixture

Reference.TaskService is a finite database verification fixture, not a server. Its C# business methods retain typed idempotent create/replay, pagination, recovery, optimistic CRUD and transactional outbox work over PostgreSQL and SQLite. Attachment/blob and cleanup scenarios retain database consistency assertions.

The fixture has no NativeWeave Server, HTTP/gRPC routing or protocol dependency. Ordinary hosts can call the same kind of C# business method using their own standard hosting stack.

Run the package driver against a current database candidate:

```sh
python3 tests/Reference.TaskService/package_probe.py \
  --feed /path/to/candidate/feed --version 0.1.0-db-scope.1.2 \
  --output /outside/the/source/database-business
```

Set NW_TEST_POSTGRES to a disposable PostgreSQL18 server and make its psql/server tools available. The driver uses ordinary PackageReference projects outside the source, isolated caches and Rust traps, then runs JIT/AOT for both providers.

The PostgreSQL wire fault proxy observes actual lock conflicts and lost COMMIT acknowledgements. Independent SQL checks establish the durable result and replay behavior. Finite database fault tests retain real restart, cancellation/drain and SQLite filesystem failure cases. No performance or soak workload is run.
