# NuGet release setup

The repository builds and tests candidates without a NuGet login. Public publication is a separate authorized action. The initial distributable is **NativeWeave.HelloWorld**, an experimental Linux x64 package. macOS packages are local development artifacts until a separate release profile is approved and tested.

## One-time account setup (maintainer interaction)

1. Sign in to [nuget.org](https://www.nuget.org/) and confirm the account email. Choose the individual or organization that will own `NativeWeave.HelloWorld`; GitHub organization membership does not automatically create a NuGet organization.
2. Under **Trusted Publishing**, create a GitHub policy with:

   | Field | Value |
   | --- | --- |
   | Repository owner | `IzuSharp` |
   | Repository | `NativeWeave` |
   | Workflow file | `release.yml` (filename only) |
   | Environment | `nuget` |
   | Package glob | `NativeWeave.*` |
   | Scopes | Push new packages and new versions |
   | Policy owner | The intended NuGet package owner |

3. In GitHub create the `nuget` environment and choose the desired reviewers/ref restrictions. Add repository variable `NUGET_USER` with the NuGet login/profile name (not email). Set repository variable `NUGET_PUBLISH_ENABLED=true` **only when ready for actual public publication**. Before then, a missing/false variable keeps publication disabled. Do not paste tokens into this repository or chat.
4. Configure private vulnerability reporting, dependency graph/push protection and required `Verify` checks as appropriate. These settings have not been changed by this bootstrap.

The workflow uses `NuGet/login` with `id-token: write` and receives a short-lived credential. A long-lived `NUGET_API_KEY` secret is not required for this OIDC path. See the official [Trusted Publishing documentation](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing).

**A publishing glob and a reserved prefix are different.** `NativeWeave.*` limits the publishing policy; it does not reserve that namespace. For prefix protection, separately apply through NuGet's [prefix reservation process](https://learn.microsoft.com/en-us/nuget/nuget-org/id-prefix-reservation). Availability/approval is not assumed. If a one-time manual API key is needed for account bootstrapping, scope it to `NativeWeave.*` and only the required push operations, expire/revoke it promptly, and keep it outside source. The committed workflow intentionally uses OIDC.

## Candidate and publication flow

1. Merge the reviewed bootstrap into `main` after actual Linux `Verify` passes and normal repository review rules are met.
2. For a non-publishing rehearsal, run **Release** on `main`, enter a version such as `0.1.0-preview.1`, and leave **publish** unchecked. This rebuilds and verifies a Linux candidate and security gates. Do not assume this rehearses authenticated registry publication.
3. For an authorized release, enable publishing and either run Release on `main` with **publish** checked or push a version tag such as `v0.1.0-preview.1` pointing to a commit on `main`.
4. The candidate job runs the full source/package/AOT loop and a Rust-free SDK container consumer. Security checks must also succeed. The publishing job downloads the exact artifact, checks SHA-256/native/source identities, exchanges OIDC credentials and uploads that package without rebuilding it.
5. It waits for registry availability, verifies the NuGet signature, compares all unsigned payload entries against the candidate, then restores those registry bytes into a fresh cache and executes both JIT and AOT consumers. `publication.json` records upload and registry digests separately because repository signing may change archive bytes.

The first version is deliberately a preview. NuGet versions are immutable: there is no automatic overwrite or `--skip-duplicate` success assumption. A duplicate/conflicting upload fails and requires an explicit investigation or a new version. If upload succeeded but later indexing/verification failed, the version may already be public; inspect the retained evidence before retrying. Do not advertise a release as verified until registry consumption succeeds.

CI uploads packages, manifests and logs as run artifacts; it does not create a GitHub Release or publish documentation automatically. Source/manifest checksums are consistency evidence, not an author-signing certificate or a completed supply-chain attestation policy. Production engines require the fuller Design release obligations.
