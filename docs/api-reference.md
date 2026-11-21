# Database API reference

Current application APIs are the compiled database and required Core surfaces. Their exact signatures and XML are checked by the component verifiers. Historical Server/protocol/demo specifications are not current product APIs.

| Area | Guide |
| --- | --- |
| Data sources, pools, sessions and Database Host | [Database Host](guides/data-nativehost.md) |
| PostgreSQL and SQLite | [PostgreSQL](guides/data-postgres.md), [SQLite](guides/data-sqlite.md) |
| Data contracts and parameter codecs | [Data abstractions](guides/data-abstractions.md), [codecs](guides/data-codecs.md) |
| Transactions and migrations | [Transactions](guides/data-transactions.md), [migrations](guides/data-migrations.md) |
| Fluent queries and static models | [Fluent](guides/query-fluent.md), [query generator](guides/query-generator.md) |
| DTO mapping, relations and CRUD | [Materialization](guides/data-materialization.md), [relations](guides/orm-relations.md) |
| Streaming and resource lifetime | [Streaming](guides/data-streaming.md), [lifetime](guides/interop-lifetime.md) |
| Errors and cancellation | [Errors](guides/interop-errors.md), [async](guides/interop-async.md), [execution](guides/interop-execution.md) |
| Package consumption and Native AOT | [Database packages](guides/packaging-domain.md), [Linux assets](guides/packaging-linux.md) |

The database facade lives in `src/Data.NativeHost` and compiles the existing query, materialization, migration and relation implementations. Providers live in `src/Data.Sqlite` and `src/Data.Postgres`. Detailed component reference files remain next to their implementation.

The maintainer `ApiReference` tool and component API checkers verify actual assemblies and XML. Unchanged historical declaration inventories are read from their pinned immutable Design checkout, while the current scope is defined by DB-Scope-01.
