# Database candidate and release boundaries

DB-Scope-01 creates and tests local database NuGet candidates. The old HelloWorld automatic public publisher and its workflow have been removed. A merge does not publish a new database package to nuget.org.

## Candidate production

`eng/build.py verify` requires a clean committed source, builds the independent SQLite/PostgreSQL native profiles, and calls `src/Packaging.Domain/prepare.py`. Preparation derives the twelve-package graph from the retained implementation and records source, lockfile, tool, package, native and license identities.

The previous/candidate pair uses immutable local versions. Shared packages keep the same bytes; the database facade, provider facades and native leaves advance together. Candidate feeds and evidence are under `artifacts/db-scope/prepared/`. Ordinary external consumers execute typed Fluent queries and DTO mappings against actual databases in JIT and Native AOT.

## Required verification

The default CI retains source/workspace/API/format/lock/security gates, real database regressions and mixed database failure oracles. It then runs shared Core closure/minimum CPU checks, database package negative cases, interrupted publication/resume, complete-closure rollback, real unsigned-signature rejection, a no-Rust SDK container and a runtime-only AOT transfer.

The local release coordinator in `src/Packaging.Release/release.py` writes an immutable local test feed and advertises it only after complete destination consumption. It does not silently turn a failed upload or incomplete consumer into success. Its public-registry signature adapter remains available for a future separately authorized release; this batch does not invent a new signer.

## Public publication

A future public database release needs an explicit reviewed identity, package set, authorization and registry signature/consumption evidence. No NuGet credentials are obtained by the current candidate workflow. Existing public historical demo versions are historical artifacts; this task neither changes nor republishes them.

Final current batch PRs, source commits and observed CI runs are recorded in the Plan handoff.
