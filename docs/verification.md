# Database verification

The current Linux x64 gate is `python3 eng/build.py verify`. It requires committed source, the pinned Rust/.NET toolchains, a disposable real PostgreSQL18 endpoint and PostgreSQL18 server tools. Existing SQLite tests use real SQLite.

It checks retained Cargo and .NET workspaces, locked dependencies, formatting, Clippy, compiled APIs/XML and the unchanged database executable suites. Provider component tests include actual PostgreSQL TLS/error cases, SQLite behavior, transactions, codecs, streaming and query binding. Composed suites cover Database Host, migrations and process recovery, Fluent queries, DTO mapping, relations/CRUD, cancellation and deterministic retirement.

Mixed reference/end-to-end fixtures directly invoke C# database business methods. Unique nullable/composite relationship, session/stream/transaction lifecycle, lock-conflict and lost-COMMIT-ack assertions remain. These fixtures create no NativeWeave listener or protocol host.

## Consumer acceptance

Candidate packages are produced from the pruned clean source. External ordinary PackageReference projects use separate caches and precompiled native assets. All four mandatory cells must execute and validate returned data:

| Database | JIT | Native AOT |
| --- | --- | --- |
| PostgreSQL | Required | Required |
| SQLite | Required | Required |

The package gate also checks provider independence, the combined graph, all nuspec edges, resolved assets, published assemblies and the application's actual mapped native libraries with matching SHA-256. Removed server/protocol/proof/demo products are rejected.

A local Rust invocation trap is recorded as local evidence, not a pristine machine. CI separately consumes the exact candidate in its pinned SDK image without Rust installed, then transfers AOT outputs to the pinned runtime-only image. Retained Core minimum-CPU, native ABI/lifecycle and package/release recovery checks remain required.

## Evidence

`artifacts/verification.json` and `artifacts/db-scope/` hold current source and artifact identities and command results. A failed or partial attempt stays failed; changed source requires a new candidate. Actual batch results, independent review, PR/merge commits and observed head/main CI are recorded in [Plan DB-Scope-01](https://github.com/IzuSharp/Plan/tree/main/ledger/evidence/batches/DB-Scope-01).

Historical acceptance in earlier Plan batches remains tied to its original commits. It does not establish acceptance of this changed candidate. Performance optimization and load testing are outside this batch.
