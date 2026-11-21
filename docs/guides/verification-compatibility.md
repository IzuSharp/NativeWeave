# Compatibility and immutable updates

The A22 maintainer tool checks an explicitly selected update and its immutable
evidence. It does not discover updates, change dependencies, publish packages,
or run in an application. Run it from an isolated maintainer checkout with the
repository's fixed Python/.NET/Rust toolchain. Its CLI is
`src/Verification.Compatibility/compatibility.py`.

This retained verifier covers Linux x64 Core ABI/API compatibility. Controlled native fixtures exercise old/new contracts and rejection paths. Current package identity, provenance, signature rejection and complete-closure rollback are tested against the actual database candidate by Packaging.Domain. Historical signed demo observations remain in the original Plan evidence and do not substitute for current database consumption.

## Run the checks

```sh
python3 tests/Verification.Compatibility/verify.py \
  --evidence artifacts/task03/A22/formal-1

python3 src/Verification.Compatibility/compatibility.py compare \
  previous.json candidate.json /absolute/evidence-root reviewed-update.json

python3 src/Verification.Compatibility/compatibility.py api \
  previous-compiled-api.json candidate-compiled-api.json

python3 src/Verification.Compatibility/compatibility.py closure \
  accepted-closure.json package-paths.json signing-policy.json signature-logs \
  --assets consumer/obj/project.assets.json
```

The full verifier requires the A13 compiled API tool in the same checkout. During
parallel development `--api-tool-root /absolute/A13/worktree` selects that exact
tool without copying its implementation. `--prepare` permits new lockfiles and
records development evidence; formal execution requires a clean committed tree,
locked restores and an unchanged source commit. Use a new evidence directory for
every run. Records and failure logs are retained, not overwritten by a retry.

The package command always performs signature checks. There is no skip-signature
or permissive-identity switch. Package paths are explicit local inputs. Network
fetches in the test runner retrieve only the two pinned existing package versions;
the tool itself performs no package download or upload. NuGet signature validation
can contact certificate revocation services using the installed SDK trust roots.

## Component records and update review

A component manifest has schema version 1 and identifies the component, RID, version,
full source commit and first availability time. Its artifact records contain
canonical paths relative to one evidence root and exact SHA-256 values for the
managed driver assembly, native binary, compiled API inventory and its actual
public API assembly, Cargo.lock, source
inventory and executed behavior receipt. Source inventory entries bind actual
files; the behavior receipt binds both executed managed and native hashes.
Traversal, substituted files and stale receipts are rejected before comparison.
The complete review and security-exception receipts must both report success,
bind the compared API assembly/snapshot hashes and enumerate all eight old/new
JIT/AOT cross-pairs for that RID. Each row binds the actual executable, managed
source profile and native file; AOT rows must observe dynamic code disabled.
Failed, empty or unrelated receipts remain failures even when their file hash is
correct. The Core API snapshot and the separate controlled API-evolution fixtures
are kept distinct.

The ABI section records major/minor, a digest of the existing wire layout,
capability-to-bit assignments and required capabilities. The domain section
separately identifies schema, operation/error and cancellation semantics. An
optional minor addition preserves all existing assignments and layouts. New
required features, removed/reassigned capabilities, a changed existing layout,
incompatible major or changed domain semantics fail the compatible-update gate.
Changing an ABI or package number does not establish behavior compatibility.

The upstream section includes exact commit, public/private source seam records,
features, MSRV, dependency checksums/licenses and an ordered patch queue. The
review must enumerate precisely which of those fields changed. Every patch binds
its exact upstream, patch bytes, differential receipt, owner, upstream issue and
exit condition. A known public replacement prevents silently retaining a private
fork. Current NativeWeave component fixtures use no real upstream fork; the patch
queue negatives are labeled controlled tests and are not evidence of a production
dependency upgrade or license audit.

The default dependency update cooldown is seven days. Missing availability data
is a failure, not implicit age. A younger security update requires a named review
with an advisory, rationale, risk decision, exact lock diff and regression
receipt. A separate update review binds the old and candidate manifest digests;
it is not embedded in either manifest, avoiding circular hashes. The tool checks
that evidence is present and bound; it does not authenticate a human approval.
The repository's review and protected-branch process remains the approval gate.
Controlled test reviews explicitly identify themselves as fixtures.

This tool consumes an already trusted release/component record. A package's
self-reported commit or workflow string is not independent builder attestation.
The present preview route authenticates the NuGet repository signature and exact
accepted payload, owner, source commit and repository. It does not claim a
separately verified SLSA/transparency attestation or introduce a new signing
service. Any additional provenance route needs its own verified subject digest,
allowed repository/workflow/ref, trust-root policy and negative fixtures.

## C# source, binary, defaults and behavior

A13 exports compiled declarations as `{ assembly, symbols: [{ id, signature,
implicit_member }] }`. A22 compares existing symbol IDs and exact declarations,
including nullability, optional defaults, parameter names, generic constraints
and attributes. Removing or changing an existing declaration fails. Additions
are reported; an additive snapshot alone does not prove source compatibility.

The executable fixtures demonstrate why the checks are separate:

| Change | Observed gate |
| --- | --- |
| Optional new API member | Existing source and existing binary execute successfully |
| Removed method | Source fails with CS0117; the old binary fails with MissingMethodException |
| Changed optional default | Snapshot rejects; recompiled source changes result while the old call site retains its baked default |
| Narrowed nullability | Snapshot rejects; the actual nullable consumer fails with CS8625 |
| Changed generic constraint | Compiled declaration comparison rejects |
| Added `Uri?` overload beside `string?` | Existing `null` call fails with CS0121 although the old declarations remain |
| Same signatures, changed result | Snapshot remains compatible; the old consumer rejects changed behavior |
| Obsolete migration | Old source observes NWCOMP001; the explicit replacement compiles and executes |

For a real API migration, preserve the old implementation and semantics, document
the replacement and release window, and first add a non-error `Obsolete` warning
with a stable diagnostic. A warnings-as-errors application will need a source
change, so adding the attribute itself is a reviewed compatibility event. Removal
or an error-level obsolete transition requires an explicitly breaking release.
Never silently change an optional default or rely only on assembly versioning.
The fixture's `NWCOMP001` is not added to a product API.

## Existing public API and consumer experience

A22 adds no runtime assembly, package, public types, managed options duplicate,
global update runtime or application initialization API. It reuses the exact
`NativeWeave.Interop.EngineLoadOptions` declaration and XML from A02 in
`NativeWeave.Core`. The compiled four-symbol policy (type, constructor, two
properties) is checked against the accepted A02 inventory; runtime rows check
that a new options object has a null path and an empty required-capability list.
The generated reference remains owned by
[Interop negotiation](../../src/Interop.Negotiation/api-reference.md). The A13
tool also checks actual compiled Core XML while producing the evidence reference.

The minimal and advanced executable consumer is
[Program.cs](../../samples/api/verification-compatibility/Program.cs). It imports
`NativeWeave.Interop` and `NativeWeave.Interop.Extensibility`, creates an explicit
maintainer fixture descriptor and calls `Inspect` with the expected native digest.
The explicit path is a fixture/advanced override; normal package consumers use
their package-owned asset selection and need neither Rust nor a native path.

The advanced row checks `EngineInfo.Supports` before an optional operation. An old
managed profile deliberately knows only the original bit even when the new native
binary has more features. A new profile can still use the old native binary for
the original operation; requiring the optional capability fails before domain
work. There is no silent reflection or managed execution fallback.

All component calls here are bounded and synchronous. Inspection hashes and loads
one native file and allocates a metadata snapshot; it starts no executor or domain
resource. The domain fixture passes a single `uint` across one FFI call, performs
wrapping arithmetic in Rust and returns a scalar with no buffer allocation or
copy. A test-only native counter proves incompatible bootstrap/hash/capability
rows perform zero domain calls. ABI metadata and domain semantics are checked
separately. No performance or memory improvement claim is made; broader workload
comparisons retain D13's same-workload/hardware and uncertainty requirements.

The actual A02 module is process resident. There is no disposable domain owner or
async retirement in this fixture, so native/managed owner reclamation tests are
not applicable to A22. A different package identity in the same process is
rejected. Rollback starts a fresh process; it never frees a module with callbacks
or resources still alive.

## Exact package closure and signatures

An accepted closure enumerates every NativeWeave-owned ID/version and direct owned
dependency edge. Nuspec edges must be `[exact-version]`; bare versions are minimum
ranges and fail. A local restore fixture deliberately adds a direct reference
that overrides a transitive exact constraint with NU1608 suppressed. The resolved
`project.assets.json` graph still fails with NWPKG016. This is the A22 maintainer
check; A16 owns automatic build-transitive consumer enforcement. Unrelated
ecosystem packages are not subjected to this owned-version rule.

Each accepted package record contains all unsigned entry hashes, repository/source
identity, internal native manifest and payload hashes, and the observed registry
archive hash. The archive parser rejects duplicate paths, traversal and symlinks
and bounds entry count/expanded size. All entries except `.signature.p7s` participate
in payload equality. The exception is permitted only alongside real cryptographic
verification of the downloaded package; it does not ignore arbitrary zip changes.

The initial tested trust route is a repository-primary signature from
`https://api.nuget.org/v3/index.json`, signed owner `dekueon`, the exact repository
certificate subject and the SHA-256 fingerprint in
[signature-policy.json](../../tests/Verification.Compatibility/signature-policy.json).
These facts are read from successful SDK `dotnet nuget verify --all` output and
the repository-signatures endpoint. The nuspec authors string is not the signed
owner identity. Wrong owner, wrong repository, wrong leaf certificate, unsigned
packages and changed payloads fail independently. Author-primary/countersign
routes fail closed until their separate policy and real signed fixtures are
reviewed; the current delivery makes no claim to have tested them. Certificate
rotation requires reviewing the exact replacement identity and updating fixtures.

After a same-version conflict, read back the existing package, verify its allowed
identity and compare accepted unsigned bytes, nuspec, internal manifest and native
hashes. Record upload and registry archive hashes separately, since repository
signing can alter the signature envelope. Matching read-back can resume an
interrupted release. A payload or identity mismatch requires a new version; the
tool never overwrites a published item and a skip-duplicate response is not proof.

The test restores two existing signed one-package bootstrap closures and runs
each in a separate process, then restores and executes the prior complete closure.
The richer facade/native graph tests use explicitly unsigned local conformance
packages and are not reported as cryptographic release acceptance. Missing leaves,
incorrect ranges and direct overrides fail. No actual NuGet package is published,
deleted or unlisted by the verifier.

The local catalog fixture removes the old version from advertised adoption while
an exact-version restore still succeeds from the retained signed package/cache.
This models unlist semantics without mutating the real registry: unlisting is
discovery/adoption guidance, not a kill switch for known versions or deployed code.
Rollback verifies the whole previous immutable set and requires zero active
processes before deployment. Existing live modules are never hot-swapped.

## Evidence and diagnostic categories

The verifier writes commands, stdout/stderr, source/tool identities, native and
managed hashes, compiled API snapshots, exact diagnostic failures, real JIT/AOT
matrix receipts, signed-package checks and restore graphs under its evidence
directory. The final receipt distinguishes clean formal execution from prepare
runs. New AOT rows require `RuntimeFeature.IsDynamicCodeSupported == false`.

`NWCMP001`–`NWCMP008` identify manifest, artifact, semantics, ABI, fork, API, review
and cooldown failures. `NWPKG010`–`NWPKG017` identify archive, closure, dependency,
payload, native provenance, signature, resolved graph and live rollback failures.
Errors identify the failed gate; retrying must preserve the same trust policy.
The Plan A22 evidence adds independent technical review and the batch integration
records. This guide does not substitute fixture results for that review, full
pristine-machine A16/B24 acceptance or unexecuted platform rows.
