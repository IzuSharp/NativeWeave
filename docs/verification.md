# Verification and evidence

Run `python3 eng/build.py verify` to reproduce the local source/package/JIT/AOT loop. The command fails at the first failed gate and removes the prior success marker before starting. `artifacts/logs/`, `verification.json`, `consumer-result.json`, `packages/manifest.json`, `packages/SHA256SUMS` and the retained native executables record the actual attempt. They are generated artifacts, not checked-in claims.

The source manifest records the starting commit, dirty flag and per-file SHA-256 values, locked native inputs, compiler identities, RID and native digest. A dirty local worktree is explicitly identified; its starting commit alone is not its source identity. CI artifacts are bound to the actual workflow run/commit.

Checks include Rust format/Clippy/release tests; locked .NET restore/build/format; source invocation; public assembly/XML/reference consistency; NuGet layout and unchanged native bytes; isolated package-cache consumption outside the checkout; RID-free build/run and real Native AOT publication/execution of both the sample and interop test consumer.

Local Rust invocation traps establish that the tested consumer commands do not call Rust. They do not claim Rust is absent from the physical machine. Linux CI builds on Ubuntu 24.04 and adds a separate Ubuntu 26.04 (Resolute) SDK container pinned by digest that checks Cargo/rustc/rustup are absent before consuming the candidate. System linker tools remain necessary. Container isolation is not a test of every clean physical machine or every Linux distribution.

No performance benchmark, long-running load, production-engine safety, Windows compatibility, hot replacement, full release signing policy or independent technical review is claimed. Public release success requires the release workflow, NuGet setup and registry consumption; a local `.nupkg` is not a published package.
