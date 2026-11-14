# NativeWeave

**C# productivity + Rust native performance and resource efficiency + modular extensibility.**

NativeWeave aims to let developers write complete applications in natural, strongly typed C# while deeply reusing mature Rust engines. Native AOT, low-overhead interop and precompiled NuGet assets connect the two ecosystems. Performance and memory improvements are engineering goals to measure against equivalent workloads, never unconditional claims of superiority over C# or Rust.

> **Current state: experimental bootstrap.** This repository implements a real C# → Rust Hello World, package consumption and Native AOT verification. Database, ORM, Server and the broader engine ecosystem remain planned. No public NuGet release is implied by this README.

## Product principles

1. **Deep native integration:** reuse mature engine algorithms, capabilities, lifecycles and resource management, beyond a thin collection of FFI calls.
2. **Developer productivity:** natural C# APIs, Fluent composition, generics and async/await; ordinary applications do not write Rust or FFI.
3. **Native performance:** minimize interop overhead and copying; validate Native AOT and compare against direct Rust and equivalent managed implementations.
4. **Memory efficiency:** explicit ownership, bounded allocation, deterministic cleanup and reduced GC pressure.
5. **Safety and reliability:** verify ownership, threads, async completion, cancellation, errors and cross-language lifetimes together.
6. **Modular extension:** independently integrate and upgrade engines. Ordinary C# Entity/DTO/Handler changes reuse precompiled native code. Runtime hot replacement requires a separate compatibility and lifecycle design.
7. **Native distribution:** maintainers build Rust; users restore NuGet and use normal `dotnet build`, `run` and `publish`, without a Rust toolchain. Native AOT still requires the platform's native linker prerequisites.
8. **Open engine ecosystem:** start with Rust-backed Database, ORM and Server; later explore GPU, GPUI, UI, mobile, SIMD, media and compute. Share necessary interop foundations without a mandatory global engine runtime.
9. **Modern stable technology:** current baseline is .NET 11 / C# 15 / Rust 1.100.0 (2026-11-14). Update deliberately with compatibility and regression evidence.
10. **Simple, efficient, elegant design:** use the minimum necessary abstractions, clear responsibilities and low overhead inside the framework as well as in its public API.

## Run the source demo

Maintainer prerequisites: .NET SDK 11.0.100, Rust 1.100.0 with rustfmt/clippy, Python 3.9+, and a C linker. On macOS use Xcode Command Line Tools; on Ubuntu install `clang` and `zlib1g-dev`.

```sh
python3 eng/build.py native
dotnet run --project samples/HelloWorld
# Hello, World! From Rust.
dotnet run --project samples/HelloWorld -- "世界 🦀"
# Hello, 世界 🦀! From Rust.
```

Application code is just:

```csharp
using NativeWeave.HelloWorld;

Console.WriteLine(RustGreeting.Greet());
```

`NativeWeave.HelloWorld` is a deliberately separate experimental package and bootstrap ABI. It does not establish or replace the designed Core, Database or Server APIs.

## Verify the complete local loop

```sh
python3 eng/build.py verify
```

This runs Rust formatting, Clippy and tests; locked .NET restore/build/formatting; managed interop checks; compiled API/XML/reference checks; NuGet packaging; and **real package-based JIT and Native AOT execution**. The consumer is generated outside the source tree with a separate NuGet cache and Rust invocation traps. Tests cover Unicode, embedded NUL, empty and invalid inputs, size bounds and concurrent calls. Logs, package/native hashes, manifests, packages and native executables are under `artifacts/`.

| Profile | Scope |
| --- | --- |
| `osx-arm64` | Local maintainer development and verification; local package contains this RID only |
| `linux-x64` | Ubuntu 24.04 CI and initial publication candidate; package contains this RID only |
| Windows, Linux arm64/musl, other macOS targets, mobile, WASM | Not implemented or advertised by this bootstrap |

Linux CI additionally consumes the package in a separate .NET SDK container without Rust installed. macOS success does not establish Linux success; workflow configuration alone does not establish a passed run. See [verification](docs/verification.md) for actual results and limitations.

## Consume the package without Rust

First build the local candidate with `python3 eng/build.py verify`. Copy `samples/PackageConsumer` outside this checkout, add `artifacts/packages` as a local NuGet source, and run normal `dotnet build` / `dotnet run`. The [getting-started guide](docs/getting-started.md) gives exact commands, source mapping and Native AOT publication. No consumer MSBuild target launches Cargo; native files use standard `runtimes/<rid>/native/` assets.

Public publication is configured separately and disabled until the maintainer finishes [NuGet setup](docs/releasing.md). Do not expect `dotnet add package NativeWeave.HelloWorld` from nuget.org to work before an actual release.

## Project context

- [Background and implementation boundaries](docs/background.md)
- [Getting started and troubleshooting](docs/getting-started.md)
- [Generated API reference](docs/api-reference.md) and [interop contract](docs/interop.md)
- [Contributing](CONTRIBUTING.md), [security policy](SECURITY.md), [release setup](docs/releasing.md)
- [NativeWeave-Design](https://github.com/IzuSharp/NativeWeave-Design): research, accepted specifications and API design
- [Plan](https://github.com/IzuSharp/Plan): the existing research, documentation and delivery task graph

The existing [MIT license](LICENSE) is preserved. This bootstrap ships no third-party Cargo crate or managed runtime package dependency; see [third-party notices](THIRD_PARTY_NOTICES.md).
