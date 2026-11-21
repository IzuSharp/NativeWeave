# NativeWeave

**Strongly typed C# Fluent ORM for PostgreSQL and SQLite, backed by Rust SeaQuery and SQLx.**

NativeWeave lets ordinary C# applications use data sources, connection pools, sessions, transactions, migrations, parameter binding, typed Fluent queries, static model/DTO mappings, relations and CRUD, and streaming results. The Rust Database Host executes database operations and owns their native resources. Core and the required interop bindings connect the two languages with explicit cancellation, errors and disposal.

The current validation target is **Linux x64, .NET11/C#15, Rust1.100.0 and Native AOT**. Candidate packages contain precompiled provider libraries. Application builds use normal PackageReference, restore, build and publish operations; they require no Rust toolchain.

## Application hosting

A database business method is ordinary C#. A standard ASP.NET Core HTTP endpoint or a standard C# gRPC method can call that same method. The application chooses and installs its host independently.

The database product does not include NativeWeave HTTP/gRPC servers, routing or protocol packages, MCP, independent compression engines or the former HelloWorld demo package. Database Host remains part of the database execution layer.

## Database packages

| Selection | Public provider package | Independent native leaf |
| --- | --- | --- |
| SQLite | NativeWeave.Database.Sqlite | NativeWeave.Database.Sqlite.Native |
| PostgreSQL | NativeWeave.Database.PostgreSql | NativeWeave.Database.PostgreSql.Native |
| Both | Both provider packages | Exactly the two database native leaves |

The complete candidate graph has twelve NativeWeave package IDs, including shared Core, ABI, Data, transaction/streaming and query components. A provider-only application does not restore the other provider's native package. The existing optional database dependency-injection source project is retained separately; this batch does not introduce a new package feature.

See [getting started](docs/getting-started.md), the [package guide](docs/guides/packaging-domain.md), and the [API index](docs/api-reference.md).

## Maintainer validation

Use the pinned SDK11.0.100, Rust/Cargo1.100.0 with rustfmt/clippy, Python3.11+, clang, zlib/OpenSSL development files and PostgreSQL18 tools. The database account must be able to create/drop disposable databases and roles. Regression tests deliberately exercise failures and recovery; use an isolated test server.

Obtain the unchanged historical API inventory used by existing declaration checks:

```sh
git clone https://github.com/IzuSharp/NativeWeave-Design artifacts/frozen-design
git -C artifacts/frozen-design checkout c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9
git clone https://github.com/IzuSharp/Plan artifacts/frozen-plan
git -C artifacts/frozen-plan checkout 8afa0311f45ab8a8157fc45c51e95a0b17dd09f2
export NW_TEST_POSTGRES=postgresql://nativeweave@127.0.0.1:5432/postgres
export NW_POSTGRES_BIN=/path/to/postgresql18/bin
python3 eng/build.py verify
```

Run from a committed clean source tree. Each candidate output is immutable; use a fresh checkout/output for a new identity. The gate builds/tests retained workspaces, checks compiled APIs, runs real PostgreSQL/SQLite and migrated database failure scenarios, packs the database candidate, and executes out-of-tree strong typed Fluent/DTO consumers in JIT and Native AOT. Logs and source/package/native identities are in `artifacts/db-scope/`.

Linux CI also runs the retained Core packaging/minimum-CPU checks, a pinned SDK container with no Rust installed, immutable database release/recovery tests, and a runtime-only transfer. Security checks remain required. Configuration is not evidence of a passing run; actual results are recorded in the [DB-Scope-01 Plan handoff](https://github.com/IzuSharp/Plan/blob/main/ledger/evidence/batches/DB-Scope-01/handoff-linux.md).

## Status and history

The database packages produced by this workflow are local candidates, not a new public NuGet release. [Release boundaries](docs/releasing.md) describe this distinction. Performance optimization is deferred; no performance advantage is claimed by this scope change.

- [Background](docs/background.md) and [verification](docs/verification.md)
- [Contributing](CONTRIBUTING.md) and [security policy](SECURITY.md)
- [Current product design](https://github.com/IzuSharp/NativeWeave-Design/blob/main/docs/database/current-product.md)
- [Plan and acceptance](https://github.com/IzuSharp/Plan)

The existing [MIT license](LICENSE) is unchanged. Candidate native leaves include their actual dependency license inventory and notices; see [third-party notices](THIRD_PARTY_NOTICES.md).
