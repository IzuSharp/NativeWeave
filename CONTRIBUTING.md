# Contributing

Read [AGENTS.md](AGENTS.md), the [background](docs/background.md), and the pinned API standard before changing an API or native boundary. Repository prose and code comments are English; discussions may use any language.

Use a topic branch and isolated worktree. Keep source, tests, XML documentation, generated reference, examples and ownership/cost explanations in the same change. Preserve the existing MIT license. Never commit credentials, build outputs or native binaries.

## Development

```sh
python3 eng/build.py native
dotnet run --project samples/HelloWorld
cargo fmt --all
dotnet format NativeWeave.slnx
python3 eng/build.py verify
```

When intentionally changing dependencies, run `dotnet restore --force-evaluate` and review all `packages.lock.json` changes. Source builds use a per-checkout `artifacts/nuget-packages` cache unless `NUGET_PACKAGES` is explicitly set; this avoids accepting a lock hash from an unrelated global cache. Cargo.lock is committed despite the crate being a library because maintainers distribute its native binary. Do not update dependencies or toolchains silently. The bootstrap has no third-party Cargo crates or managed runtime dependencies; introducing one requires license, security and native closure review.

For an intentional API/documentation change, update `docs/api-baseline.txt`, the compiled checks in `tools/ApiDocs`, XML and examples, then run `python3 eng/build.py verify --write-docs`. Review the generated `docs/api-reference.md` diff. Reflection is confined to the maintainer documentation tool; the product path is Native AOT compatible.

`verify` is the canonical gate, not `dotnet test`: the managed checks are a dependency-free executable that also runs as a real packaged Native AOT consumer. Native failure cases are tested with `cargo test`. Linux CI is the only hosted platform for now; local macOS arm64 is a separate development profile.

Use focused PRs that explain the behavior, why it changed, real commands/platforms tested, and limitations. Never present self-review as independent approval or bypass branch protections. Public publishing and repository settings follow [the release guide](docs/releasing.md).
