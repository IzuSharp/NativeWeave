# Use the database candidate from ordinary C#

The current candidate targets Linux x64 and .NET11, with JIT and Native AOT. Choose `NativeWeave.Database.Sqlite`, `NativeWeave.Database.PostgreSql`, or both. No NativeWeave server or protocol package is required.

## Restore outside the source tree

A maintainer first runs the verified candidate workflow described in the root README. It creates the exact local feed at `artifacts/db-scope/prepared/candidate/feed`; the manifest records facade/native and shared package versions. With the default version base, the provider version is `0.1.0-db-scope.1.2` and shared dependencies are pinned by the package.

Create an ordinary executable project outside the NativeWeave checkout:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net11.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="NativeWeave.Database.Sqlite" Version="[0.1.0-db-scope.1.2]" />
  </ItemGroup>
</Project>
```

Point a local NuGet.Config at the candidate feed and nuget.org; map `NativeWeave.*` to that exact feed. Add the PostgreSQL provider PackageReference when needed. Use the candidate manifest's version when the producer selected a different version base.

## Typed queries and DTOs

The executable [database package sample](../samples/api/packaging-domain/README.md) contains static table/model declarations, typed CRUD, a strongly typed Fluent projection into a DTO and actual returned-data checks for each provider. Its added-model template shows an ordinary C# entity/DTO edit without rebuilding native code.

`DataSource` owns the provider pool; open and dispose a `DataSession` for business work. Typed queries bind parameters and project through static mapping. Dispose sources, sessions, transactions and stream enumerators according to their API contracts. The component guides document provider-specific capabilities, transaction outcomes and cancellation semantics.

A business method can be called directly by a console app, a standard ASP.NET Core endpoint or a standard C# gRPC method. Install and configure the chosen host independently.

## Build and publish

```sh
dotnet restore
dotnet run -c Release
dotnet publish -c Release -r linux-x64 -p:PublishAot=true -o publish
./publish/YourApplication
```

Native AOT needs the platform C linker prerequisites. Applications use the restored precompiled provider library and do not install or invoke Rust. The strict package targets validate the exact restored graph and selected native bytes. Do not suppress a closure error or substitute a native binary.

The maintained consumer verifier runs SQLite-only, PostgreSQL-only and combined dependency graphs; it checks the actual mapped native modules and hashes as well as the package and publish directory. See [packaging](guides/packaging-domain.md) for reproducing those checks.
