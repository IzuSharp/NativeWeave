# Security policy

## Supported versions

Before the first public release, security fixes target `main`. CI artifacts and experimental preview builds carry no long-term support or response-time guarantee. There is no stable engine release yet.

## Report privately

Use [GitHub private vulnerability reporting](https://github.com/IzuSharp/NativeWeave/security/advisories/new) when enabled. Include the affected version/commit, OS/architecture, impact and a minimal reproduction. Do not disclose credentials or vulnerability details in a public issue. If private reporting is unavailable, request a private maintainer contact in an issue without disclosing the issue itself.

## Current boundary

The bootstrap transforms a bounded name into a greeting. It opens no sockets, starts no native runtime or callbacks, retains no foreign pointer, and transfers no native allocation to C#. Strict UTF-8/UTF-16 and capacity checks cover the supported callers. The C ABI requires valid, non-overlapping memory; it cannot validate arbitrary foreign pointers or sandbox native code. Recoverable Rust panics are contained; abort, OOM and memory corruption are not recoverable guarantees.

Native libraries and their OS dependencies are trusted process code. The package manifest and SHA-256 records establish content consistency, not publisher authentication or a sandbox. Only install trusted packages in trusted application directories. No hot unloading, signature-verifying Engine loader or full production lifecycle system is implemented here.

CI checks source, locked dependencies, package layout, interop and AOT behavior. Security workflows add dependency review, redacted history secret scanning and CodeQL for C#/Python; they do not claim Rust CodeQL coverage. Rust uses compiler checks, Clippy, unit tests and an explicit no-external-dependency inventory. Any new Rust dependency requires adding an advisory/license gate before release. These checks supplement review; they do not prove security.

PR workflows receive no publishing credentials. Publication runs separately, is gated by a repository variable and uses short-lived NuGet OIDC credentials. Private reporting, push protection, environments and required checks are GitHub settings and are not enabled merely by committing these files.
