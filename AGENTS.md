# NativeWeave implementation guidance

## Current authorized product — DB-Scope-01

The current product is a strongly typed C# Fluent ORM for PostgreSQL and SQLite, backed by Rust SeaQuery and SQLx, with Native AOT and precompiled NuGet native assets. Database Host is the database execution layer and must remain. The current task is Linux x64 scope pruning and regression verification; Perf-01 is terminated and performance work is deferred.

Read README.md, docs/background.md and the current Plan batch before editing. Preserve database sources, pools, sessions, transactions, migrations, parameter binding, static models/DTOs, relations/CRUD, streams and required cancellation, error, disposal and C#–Rust binding behavior. Applications choose their own standard ASP.NET Core or C# gRPC host and call ordinary business query methods. No NativeWeave server or protocol wrapper belongs in the database dependency graph.

## Implementation and verification

- Keep exact API signatures, defaults, nullability, ownership, bounds, errors and concurrency contracts. Do not add ORM features during pruning.
- Maintain compiled API/XML checks, actual database regressions, independent provider package closures and real package-based JIT/Native AOT execution.
- Run `python3 eng/build.py verify --design /path/to/frozen-design` from a committed clean tree with disposable PostgreSQL18 and its server tools available. Use the immutable Design c62cdb8 snapshot for unchanged historical signature checks; current Design scope is separate.
- Preserve locked toolchains/dependencies, formatting, analyzer, security, provenance, license and review gates. A missing provider or failed check must fail acceptance.
- Ordinary consumer builds never invoke Cargo. Maintain only native bindings, package tooling and shared components used by the database or its meaningful regression checks.
- Keep credentials and generated binaries out of Git. Preserve LICENSE, repository protections and normal review rules. Record independent technical review honestly.
- This batch creates candidates only. The old demo auto-publisher is retired; merging does not authorize public database publication.

English is the repository documentation language. Worktrees belong in the parent project's `.worktree/` directory. Progress and acceptance are recorded in Plan/ledger/evidence/batches/DB-Scope-01/handoff-linux.md. History remains available at its original commits and in the Plan ledger.
