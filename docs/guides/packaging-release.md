# Exact database package closure and immutable release recovery

The retained release coordinator, MSBuild closure task and SDK native-output targets support the actual database candidate. Linux x64 is the current acceptance row. Public database publication is outside DB-Scope-01.

## Application build and native selection

Applications reference an exact provider facade package. Its transitive graph selects the database/Core dependencies and independent native leaf at exact versions. Normal restore, build, run and Native AOT publish consume those precompiled bytes; no compiler-host task invokes Rust.

Each facade carries the strict closure metadata, shared `NativeWeave.Packaging.targets` and `NativeWeave.Packaging.Tasks.dll`. The compiler-host assembly is not an application runtime dependency. The ten-symbol task API and XML remain verified by `tests/Packaging.Release/ApiCheck`.

The task compares the actual project.assets.json package set, normalized exact versions and dependency edges. It checks the SDK-selected native identity, RID, CPU/ABI metadata, canonical paths and SHA-256, then writes bounded native-output records. Build and publish records follow the SDK's actual output layout. Core validates those immutable records and performs runtime ABI negotiation before opening database owners.

Unknown or duplicate schema/package fields, invalid JSON, nonexact edges, unsupported RID/CPU/ABI, malformed engine identities, path traversal, missing/duplicate native outputs, duplicate basenames and changed bytes are hard errors. Dependency warning suppression cannot suppress these errors. These cases now execute against the real database closure in `tests/Packaging.Domain/negative_cases.py`.

## Maintainer candidate and recovery

`src/Packaging.Domain/prepare.py` stages the twelve actual database packages from a clean source-bound build. The old artificial packaging facade and orphan generic code generators have been removed; their unique strict guards were moved to database candidate tests.

`src/Packaging.Release/release.py` orders exact leaves before facades. The local immutable-feed adapter journals uploaded/existing versions, verifies readback and exact payload/closure identities, and promotes a catalog only after complete destination consumption. A partial upload remains unadvertised; a retry accepts matching immutable bytes and rejects conflicts.

Rollback selects a complete previously tested closure for a fresh process. Partial sets, wrong RID/source, active-process replacement, unknown builders and incorrect provenance subjects fail. The local unlisted-feed regression checks exact-version availability without changing any public registry.

The registry adapter preserves actual `dotnet nuget verify` and the reviewed service/owner/certificate policy. The current candidate is unsigned and local; tests prove rejection rather than claiming a public signer. Historical positive signature observations retain their original evidence identity.

Run the current full package/release checks through `eng/verify-task07-linux.sh` in CI, or `tests/Packaging.Domain/release_cases.py` with an explicit truthful local mode. CI uses the pinned SDK image without Rust and transfers the exact verified AOT outputs to a runtime-only image. No source, toolchain or database secrets enter that runtime transfer.
