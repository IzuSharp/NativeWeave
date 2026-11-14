# Product background and bootstrap boundary

## Sources read for this bootstrap

The user authorized initial implementation on 2026-11-14 after the research/design phase. All three local repositories were fast-forwarded before work:

| Repository | Starting commit |
| --- | --- |
| NativeWeave | `658ed6a410783de356a7b9b2cd6601336fff5148` |
| NativeWeave-Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |
| Plan | `050d54cc2433901cbe896f7490af0e94ba631415` |

Read scope includes Design/Plan README and collaboration rules; requirements charter; architecture boundaries; build/package/release specification; public API standard and index; NuGet consumption and documentation-system specifications; Plan A01/A13/A19/A21 and the existing phase boundaries. The repositories contain much broader research; this list does not claim every source or evidence file was re-reviewed.

The existing design assigns domain work to the 34 Research / 32 Documentation / 48 Delivery graph. This bootstrap supplies only an initial integration and distribution path. It neither updates those acceptance records nor implements their full ABI, ownership/async system, loader, metadata generators, Database, ORM or Server contracts.

## Reference conventions

References were inspected on 2026-11-14. These are format and workflow references, not imported business architecture or license policy:

- [ArcForges/ArcForges](https://github.com/ArcForges/ArcForges/tree/10f692224f94916cfc93fbad971f80ec340c5edf): `NuGet.Config`, `.gitignore`, `.gitattributes`, `Directory.Build.props`, `SECURITY.md`.
- [ArcForges/Contracts](https://github.com/ArcForges/Contracts/tree/de3dba76266e89654be9b4d29d097d525a281c6a): `.github/workflows/ci.yml`, `.github/workflows/security.yml`. Reuse the idea of a tested candidate and separate OIDC publishing; NativeWeave has no author-specific validation bypass.
- [rust-lang/rust](https://github.com/rust-lang/rust/blob/5f4effd579500175af844241eb179e756190f1e7/.gitattributes): Rust text/diff and binary attributes.
- [tokio-rs/tokio](https://github.com/tokio-rs/tokio/blob/f3e855fa55d6c1cc3e7a28e115a421b8ee5860bd/.gitignore): target-directory convention. NativeWeave intentionally commits Cargo.lock because it distributes reproducible native build inputs.

Stable versions were checked against the installed SDK/compiler and official [.NET 11 release notes](https://github.com/dotnet/core/blob/main/release-notes/11.0/11.0.0/11.0.0.md) and [Rust 1.100 announcement](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/). No preview features are required.

## Minimum closed loop

`Rust source → cdylib → C# LibraryImport facade → NuGet runtime asset → isolated PackageReference consumer → dotnet run → Native AOT publish → actual executable`.

A stateless greeting intentionally avoids introducing an artificial resource owner, async runtime or binding generator. It validates string encoding, bounded caller-owned buffers, C ABI status handling and package deployment. It does not prove deep engine integration, deterministic engine teardown, hot replacement or performance benefits. Those require the actual future engines and their accepted contracts.

Repository documents retain the complete product goal in README.md. `NativeWeave.HelloWorld` is a disposable bootstrap package, not the naming or ABI decision for future Core/Engine packages. The pinned standard is adopted for this surface with compiled signature/nullability/default checks, required XML, generated reference, natural consumers and real AOT checks. Full DocFX site, released-package compatibility history, production asset manifests and independent API review remain future delivery obligations.

## Web development handoff

The repository carries its build instructions, exact versions, architecture boundaries, security/release guide and verification command. A web-hosted development environment should install the pinned SDK/Rust toolchain for maintainer work, use Python 3.9+, and run `python3 eng/build.py verify` on Linux x64 with `clang` and `zlib1g-dev`. Application consumers only require .NET and, for AOT publication, the C linker prerequisites. No machine-specific absolute path or credential belongs in the repository.
