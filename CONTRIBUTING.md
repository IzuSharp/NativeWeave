# Contributing

Read [AGENTS.md](AGENTS.md), [background](docs/background.md), and the pinned C# API standard before changing a database API or native boundary. Repository prose and code comments are English.

Use a topic branch and isolated worktree. Keep source, tests, XML documentation, compiled API checks, examples and ownership/cost explanations together. Preserve the MIT license; never commit credentials, build outputs or native binaries.

## Development

```sh
cargo fmt --all
dotnet format NativeWeave.slnx
# Set a disposable PostgreSQL18 endpoint and server-tool path as described in README.
python3 eng/build.py verify --design /path/to/frozen-design
```

Formal verification requires a clean committed source. Source-only debugging may build the two explicit database provider profiles, but it does not create a passed candidate receipt. For intentional dependency changes, regenerate and review lockfiles; ordinary CI uses locked restore/build. Avoid unrelated dependency/toolchain upgrades during scope pruning.

Compiled API/XML checks live with their database and Core components. The shared maintainer tool is `src/Build.Integration/ApiReference`; unchanged signature inventories use the exact frozen Design input recorded by those tests. Update a public baseline only with reviewed API changes, never to conceal a regression.

The canonical gate executes console suites and real database package JIT/AOT applications. `dotnet test` alone does not run these executable suites. CI additionally enforces security, no-Rust consumer, minimum CPU and runtime transfer checks. Record the commands, actual platform, source identities and limitations.

Use focused PRs describing the problem, resulting behavior and evidence. Independent technical review is separate from self-review; preserve branch protections. This database scope batch creates candidates and does not publish new public packages.
