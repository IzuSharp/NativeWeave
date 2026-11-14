# NativeWeave implementation guidance

This repository is the implementation home. The current user-authorized scope is the initial C#/Rust Hello World, repository hygiene, documentation, Linux CI and release preparation. Read docs/background.md and README.md first. Do not mistake historical research-only phase text in the sibling repositories for a prohibition on this newly authorized bootstrap; do not mark their Delivery graph complete either.

Keep the core minimal. Mature Rust engines must own future Database/ORM/Server execution; ordinary C# Entity/DTO/Handler changes must reuse precompiled native assets. No default global Rust runtime, managed SQL/network substitute, or consumer Cargo invocation. Performance/memory benefits require comparable measurements.

## C# public API and documentation

This repository pins the NativeWeave API standard in public-api-standard.json and docs/standards/csharp-public-api-and-documentation.md. The bootstrap's local contract is docs/interop.md; it is deliberately separate from the future Engine ABI.

- Preserve exact signatures, defaults, nullability, ownership, bounds, errors, concurrency and cost explanations.
- Update XML, the compiled API baseline checker, generated reference and actual package consumers with each API change.
- Run `python3 eng/build.py verify`. It includes real JIT and Native AOT execution; compilation alone is not execution.
- Keep public API work scoped to the requested component. Independent technical review is a separate release acceptance obligation; record self-review honestly.
- Pin stable toolchains and lock dependencies. Do not inherit unrelated ArcForges policies or licensing.
- Keep credentials out of source and logs. Preserve LICENSE and repository protections. Publication configuration is documented in docs/releasing.md; never infer permission to release from a green build.

English is the repository documentation language. Prefer small, understandable changes; do not build future domain scaffolding to make the demo appear complete. Local worktrees belong in the parent project's `.worktree/` directory.
