# Maintainer database API documentation tools

The retained toolchain validates actual compiled database/Core declarations and XML. It is not included in application runtime packages.

| Entry point | Purpose |
| --- | --- |
| `ApiReference/ApiReference.csproj` | Inspect a compiled assembly and XML against the exact reviewed symbol/signature baseline; produce the component reference |
| `compose_docs.py --config CONFIG --output artifacts/PATH` | Run the API gate and pinned DocFX build over copied accepted inputs; no source modification or public publication |
| `tests/Build.Integration/verify_docs.py --output artifacts/PATH` | Exercise signature, default/nullability and XML rejection controls against the actual shared tool |

Current database maintainers build native provider assets through `eng/task07_native.py`. The generic proof-profile native builder, its consumer hook and sample are retired. Ordinary applications use the precompiled NuGet provider assets.

The frozen historical `design-inputs.json` remains a provenance record for the original tooling delivery. Current authority is the DB-Scope-01 Plan and Design scope.
