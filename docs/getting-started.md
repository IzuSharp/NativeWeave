# Getting started

## Maintainer source development

Install the versions in global.json and rust-toolchain.toml, Python 3.9+ and native linker prerequisites. macOS arm64 uses Xcode Command Line Tools. Linux CI uses Ubuntu 24.04 x64 with `clang` and `zlib1g-dev`.

```sh
python3 eng/build.py native
dotnet run --project samples/HelloWorld
python3 eng/build.py verify
```

The source sample uses ProjectReference and explicitly staged native output. `dotnet build/run` do not secretly invoke Cargo. Rebuild the native asset explicitly after Rust changes.

## Independent NuGet consumer

After `python3 eng/build.py verify`, copy `samples/PackageConsumer` to a directory outside the repository. In that directory create `NuGet.Config`, replacing `/absolute/path/to/artifacts/packages` with the actual local feed:

```xml
<configuration>
  <packageSources>
    <clear />
    <add key="candidate" value="/absolute/path/to/artifacts/packages" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
  <packageSourceMapping>
    <packageSource key="candidate"><package pattern="NativeWeave.*" /></packageSource>
    <packageSource key="nuget.org"><package pattern="*" /></packageSource>
  </packageSourceMapping>
</configuration>
```

Use the package version you built (default `0.1.0-preview.1`):

```sh
dotnet build
dotnet run
# Hello, World! From Rust.
dotnet run -- "世界 🦀"
dotnet publish -c Release -r osx-arm64 -p:PublishAot=true -o publish
./publish/PackageConsumer
```

Use `-r linux-x64` on Linux with a Linux-built candidate. Each candidate contains only the RID actually built and verified; an osx-arm64 local package and a linux-x64 CI package are separate local candidates and must not both be published as the same immutable NuGet version. Initial public release artifacts are Linux x64 only. No Rust toolchain is needed in the consumer. AOT needs the C linker and system development libraries.

## Troubleshooting

- **Missing local asset in a source build:** run `python3 eng/build.py native`.
- **Package not found:** this scaffold does not imply public publication. Configure the local feed, matching version and source mapping.
- **DllNotFoundException / BadImageFormatException:** verify the package RID, architecture and output native asset. Do not copy a binary from another OS.
- **ABI/version error:** reinstall the complete matching package. Do not swap its native library manually.
- **AOT linker failure:** check Xcode Command Line Tools or Linux clang/zlib development prerequisites. A JIT run is not an AOT test.
- **Invalid name:** pass valid UTF-16 that fits within 4096 UTF-8 bytes. Empty strings are allowed.

See the [API reference](api-reference.md) for the complete public surface and [interop contract](interop.md) for the boundary and costs.
