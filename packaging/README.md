# NativeWeave.HelloWorld

An experimental C# → Rust interop and Native AOT bootstrap for [NativeWeave](https://github.com/IzuSharp/NativeWeave). This is a working greeting demo, not the future Core, Database, ORM or Server engine.

```csharp
using NativeWeave.HelloWorld;

Console.WriteLine(RustGreeting.Greet());
// Hello, World! From Rust.
Console.WriteLine(RustGreeting.Greet("世界 🦀"));
// Hello, 世界 🦀! From Rust.
```

Requires .NET 11. Initial public candidates contain the Linux x64 native asset and are built/tested on Ubuntu 24.04. Local maintainer packages may instead contain macOS arm64 assets; inspect `nativeweave/manifest.json` for this archive's actual RID. No other platform is advertised.

Applications use ordinary `dotnet build` / `dotnet run`; Rust is precompiled and no Rust toolchain or consumer Cargo build hook is required. On Linux x64, publish with `dotnet publish -c Release -r linux-x64 -p:PublishAot=true`, then run the actual output executable. Native AOT requires the platform's C linker/development prerequisites.

`RustGreeting.Greet(string name = "World")` is synchronous and thread-safe. Names must be valid UTF-16 and fit in 4096 UTF-8 bytes; null, invalid or oversized names throw argument exceptions. Empty names and embedded NULs are preserved. No native allocation or pointer is retained; no disposal, callback or background runtime is involved. This demo makes no performance, zero-copy or production-engine safety claim.

See the [repository guide](https://github.com/IzuSharp/NativeWeave/blob/main/docs/getting-started.md), [API reference](https://github.com/IzuSharp/NativeWeave/blob/main/docs/api-reference.md), [security policy](https://github.com/IzuSharp/NativeWeave/blob/main/SECURITY.md), and [MIT license](https://github.com/IzuSharp/NativeWeave/blob/main/LICENSE).
