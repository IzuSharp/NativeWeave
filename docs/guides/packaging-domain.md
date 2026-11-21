# Database package closure

The current candidate contains twelve NativeWeave package IDs: Interop.Abi, Core, Data, Database.Transactions, Data.Streaming, Query.Binding, Query.Generator, Database, the SQLite/PostgreSQL provider facades, and their two independent Native leaves. No Server, gRPC, MCP, compression/proof or demo package belongs to the graph.

`src/Packaging.Domain/model.py` defines exact dependency edges. `prepare.py` composes a previous/candidate pair from actual compiled assemblies and source-bound provider binaries. The seven shared packages preserve their original local bytes within the pair. Native leaves carry actual compiler-artifact dependency/license inventories and selected platform/hash metadata.

## Ordinary applications

The [sample](../../samples/api/packaging-domain/README.md) uses normal PackageReference consumers with static entity mapping, typed Fluent projection and DTO result assertions. SQLite-only and PostgreSQL-only applications restore one native leaf. A combined application restores both; neither choice adds a host runtime.

The existing strict package task checks the actual restored closure and SDK-selected native outputs. The consumer gate checks all nuspec dependencies, project.assets.json, published assemblies and `/proc/self/maps` after real database work. Actual loaded native hashes must match the package. An added entity/DTO query is compiled after restore without changing native bytes or invoking Rust.

## Verification

```sh
python3 eng/build.py verify --design /path/to/frozen-design
python3 tests/Packaging.Domain/release_cases.py \
  --manifest artifacts/db-scope/prepared/manifest.json \
  --output /outside/the/source/release-check \
  --consumer-environment local
```

Local mode isolates Rust paths and records `pristine_machine=false`. The default pristine mode requires the pinned SDK image and absent Rust tools. CI executes that strict mode and a runtime-only transfer.

Fourteen release/recovery cases retain actual destination restore/execution, interrupted upload/resume, same-version conflict rejection, complete immutable rollback, and real signature rejection for unsigned local candidates. Negative package tests must fail for undeclared or retired dependencies/assets. Candidate success does not claim public registry publication or historical performance results.
