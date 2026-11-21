# Independent database package consumers

`Program.cs` is ordinary C# application source copied into a fresh SDK project by
`tests/Packaging.Domain/consumer_cases.py`. The controller selects exact versions
from the producer manifest. These are local database candidates; no public NuGet
release is claimed. Applications choose their own hosting and use normal
`PackageReference`, `dotnet build`, and Native AOT publishing.

| Graph | Compilation symbols | Direct packages |
| --- | --- | --- |
| SQLite | `SQLITE` | `NativeWeave.Database.Sqlite` |
| PostgreSQL | `POSTGRES` | `NativeWeave.Database.PostgreSql` |
| Both providers | `SQLITE;POSTGRES` | Both database provider packages |

Every process inserts and reads typed entities, executes a strongly typed Fluent
filter/order/limit query into independent DTOs, checks the expected row values,
and closes its database owners. `DatabaseFixture.QueryDtos` is a plain C# business
method that a console application, standard ASP.NET Core endpoint, or standard
C# gRPC method can call. The sample has no server or protocol dependency.

For a previous-candidate smoke check inside the pinned pristine SDK image:

```sh
python3 src/Packaging.Domain/consume.py \
  --manifest /prepared/manifest.json --closure previous \
  --feed /destination --output /results/previous-smoke --mode smoke
```

The complete candidate check uses three independent package graphs, actual JIT
and Native AOT executions, and focused dependency/asset failure cases:

```sh
python3 src/Packaging.Domain/consume.py \
  --manifest /prepared/manifest.json --closure candidate \
  --feed /destination --output /results/candidate-full --mode full
```

`NW_TEST_POSTGRES` must identify the explicitly configured isolated PostgreSQL
service. SQLite files are created outside the source tree. Each graph restores
into its own fresh cache with exact package source mapping. Ordinary consumers
use precompiled assets and never invoke Cargo.

The default `--consumer-environment pristine` requires the actual pinned SDK
container without Rust. Local maintainers may pass `--consumer-environment local`
to run the same database, package, AOT and negative checks with Rust commands
removed from the consumer PATH and trapped. Local receipts explicitly record
`pristine_machine: false`; a local run does not replace the required CI container
or runtime-only transfer. Do not set a container identity variable to describe a
local machine as pristine.

`AddedModels.cs.template` is copied only **after** the JIT and AOT restores. The
controller empties restore sources, rebuilds and runs the added typed entity and
Fluent DTO query, then publishes and executes Native AOT. The native assets must
retain their exact pre-edit bytes. The executable reads `/proc/self/maps` after
opening the real database and reports the basename and SHA256 of the database
library actually mapped. The controller compares this with the selected candidate
and rejects undeclared packages, runtime assemblies, native libraries, or compiler
tools in the output.

The same real database closure exercises the retained package task's malformed
metadata, exact dependency, CPU/RID, path traversal, duplicate asset, and hash
rejection checks. A bounded loopback NuGet V3 fixture also restores exact known
versions marked unlisted into a fresh cache. It serves the candidate archives
only; vulnerability auditing remains enabled against nuget.org. The release
coordinator verifies whole-closure upgrade and rollback, builder/provenance
identity, immutable versions, and refusal of unauthenticated registry signatures.

The inherited `B24_RESULT` transport prefix carries a `task: DB-Scope-01` receipt
only after database owners close successfully. `--require-aot` verifies actual
Native AOT execution. `--reject-abi` exercises the existing incompatible ABI gate
before any database owner is created.

See [the database package guide](../../../docs/guides/packaging-domain.md) for
producer/source identity, local closure versions, prerequisites, and transfer
boundaries. Source inspection is not execution evidence; receipts remain bound
to the exact new source, package, native, and executable identities.
