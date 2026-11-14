# Verification and evidence

Run `python3 eng/build.py verify` to reproduce the local source/package/JIT/AOT loop. The command fails at the first failed gate and removes the prior success marker before starting. `artifacts/logs/`, `verification.json`, `consumer-result.json`, `packages/manifest.json`, `packages/SHA256SUMS` and the retained native executables record the actual attempt. They are generated artifacts, not checked-in claims.

The source manifest records the starting commit, dirty flag and per-file SHA-256 values, locked native inputs, compiler identities, RID and native digest. A dirty local worktree is explicitly identified; its starting commit alone is not its source identity. CI artifacts are bound to the actual workflow run/commit.

Checks include Rust format/Clippy/release tests; locked .NET restore/build/format; source invocation; public assembly/XML/reference consistency; NuGet layout and unchanged native bytes; isolated package-cache consumption outside the checkout; RID-free build/run and real Native AOT publication/execution of both the sample and interop test consumer.

Local Rust invocation traps establish that the tested consumer commands do not call Rust. They do not claim Rust is absent from the physical machine. Linux CI builds on Ubuntu 24.04 and adds a separate Ubuntu 26.04 (Resolute) SDK container pinned by digest that checks Cargo/rustc/rustup are absent before consuming the candidate. System linker tools remain necessary. Container isolation is not a test of every clean physical machine or every Linux distribution.

No performance benchmark, long-running load, production-engine safety, Windows compatibility, hot replacement, full release signing policy or independent technical review is claimed. Public release success requires the release workflow, NuGet setup and registry consumption; a local `.nupkg` is not a published package.

## Bootstrap failure history

- Local package inspection initially rejected a duplicated `runtimes/<rid>/native/` path. Explicit full package-entry metadata corrected it; isolated package/JIT/AOT consumption then passed.
- [First Linux run](https://github.com/IzuSharp/NativeWeave/actions/runs/43613017889) rejected the ILLink lock hash with NU1403. The pre-existing local global cache differed from the official feed. Regenerating the lock from an isolated official-source cache and using a per-checkout maintainer cache corrected the input; hash checking remains enabled.
- The first PR dependency review reported that the repository's dependency graph was disabled. Enablement is a repository prerequisite, not a reason to skip or weaken the review gate.
- Local macOS AOT emitted an Xcode probe diagnostic and a duplicate debug-map warning with Command Line Tools. Both native executables were still produced and successfully executed. Preserve the logs; do not describe the full native toolchain output as warning-free.
