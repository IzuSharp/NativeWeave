# NativeWeave.Database.PostgreSql API reference

Generated from the compiled product assembly and its XML comments by `tests/Data.Postgres/ApiCheck`. Covers provider options, Engine preflight, and the integrated Create/UsePostgreSql data source factories. Exact declarations retain the pinned Design identity in `public-api.expected.json`; the historical B02/B04 ownership slice remains in `downstream-composition.json`.

## `F:NativeWeave.Database.PostgreSql.PostgreSqlTlsMode.DisableForLocalDevelopment`

```csharp
NativeWeave.Database.PostgreSql.PostgreSqlTlsMode.DisableForLocalDevelopment = 1
```

**summary:** Disables TLS only when the application explicitly opts into local development.

## `F:NativeWeave.Database.PostgreSql.PostgreSqlTlsMode.VerifyFull`

```csharp
NativeWeave.Database.PostgreSql.PostgreSqlTlsMode.VerifyFull = 0
```

**summary:** Requires TLS, a trusted root and a matching server hostname; the default.

## `M:NativeWeave.Database.PostgreSql.PostgreSqlDataSource.Create(System.String,System.Action{NativeWeave.Database.PostgreSql.PostgreSqlOptions})`

```csharp
public static NativeWeave.Database.DataSource NativeWeave.Database.PostgreSql.PostgreSqlDataSource.Create(string connectionString, System.Action<NativeWeave.Database.PostgreSql.PostgreSqlOptions>? configure = null)
```

**summary:** Creates one independently owned lazy SQLx PostgreSQL data source.

**param connectionString:** An explicit TCP PostgreSQL URI; ambient connection policy is rejected.

**param configure:** An optional synchronous options callback, snapshotted before native admission.

**returns:** A data source to dispose after its sessions finish.

**exception:** is null.

**exception:** The connection or typed security policy is invalid.

**exception:** The exact packaged module fails negotiation.

## `M:NativeWeave.Database.PostgreSql.PostgreSqlDataSourceBuilderExtensions.UsePostgreSql(NativeWeave.Database.DataSourceBuilder,System.String,System.Action{NativeWeave.Database.PostgreSql.PostgreSqlOptions})`

```csharp
public static NativeWeave.Database.DataSourceBuilder NativeWeave.Database.PostgreSql.PostgreSqlDataSourceBuilderExtensions.UsePostgreSql(this NativeWeave.Database.DataSourceBuilder builder, string connectionString, System.Action<NativeWeave.Database.PostgreSql.PostgreSqlOptions>? configure = null)
```

**summary:** Snapshots explicit connection and TLS policy without opening a connection.

**param builder:** The single-writer builder.

**param connectionString:** A nonempty explicit PostgreSQL TCP URI.

**param configure:** Optional synchronous configuration; failure leaves the builder unchanged.

**returns:** The supplied builder.

**exception:** The builder or connection is null.

**exception:** A setting is invalid.

## `M:NativeWeave.Database.PostgreSql.PostgreSqlOptions.#ctor`

```csharp
public NativeWeave.Database.PostgreSql.PostgreSqlOptions.PostgreSqlOptions()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.PostgreSql.PostgreSqlTlsMode.#ctor`

```csharp
public NativeWeave.Database.PostgreSql.PostgreSqlTlsMode.PostgreSqlTlsMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `P:NativeWeave.Database.PostgreSql.PostgreSqlDataSource.Engine`

```csharp
public static NativeWeave.Interop.EngineDescriptor NativeWeave.Database.PostgreSql.PostgreSqlDataSource.Engine { get; }
```

**summary:** Gets the immutable descriptor of the complete PostgreSQL Database Host asset.

**remarks:** The canonical database bootstrap reports only implemented capabilities. The inspected module remains resident; datasource disposal joins its runtime rather than unloading code.

## `P:NativeWeave.Database.PostgreSql.PostgreSqlOptions.ApplicationName`

```csharp
public string NativeWeave.Database.PostgreSql.PostgreSqlOptions.ApplicationName { get; set; }
```

**summary:** Gets or sets the PostgreSQL application name; defaults to NativeWeave.

**remarks:** Requires 1–256 valid UTF-8 bytes without NUL. The immutable UTF-8 snapshot is copied once into the bounded native option record. PostgreSQL can truncate the displayed application_name to its server limit.

## `P:NativeWeave.Database.PostgreSql.PostgreSqlOptions.ConnectTimeout`

```csharp
public System.TimeSpan NativeWeave.Database.PostgreSql.PostgreSqlOptions.ConnectTimeout { get; set; }
```

**summary:** Gets or sets a positive connect deadline of at most one hour; defaults to 15 seconds.

**remarks:** The serialized duration is exact unsigned nanoseconds. The host applies it to opening/admission; an expired caller wait is distinct from retiring a dispatched native connection operation. No network I/O occurs while setting it.

## `P:NativeWeave.Database.PostgreSql.PostgreSqlOptions.RootCertificatePath`

```csharp
public string? NativeWeave.Database.PostgreSql.PostgreSqlOptions.RootCertificatePath { get; set; }
```

**summary:** Gets or sets the optional absolute PEM root-certificate path.

**remarks:** Null uses the native TLS system trust roots. The native provider validates the file before connection; hostname verification remains required. The path and certificate are configuration, not a password; no certificate contents are copied into diagnostics.

## `P:NativeWeave.Database.PostgreSql.PostgreSqlOptions.TlsMode`

```csharp
public NativeWeave.Database.PostgreSql.PostgreSqlTlsMode NativeWeave.Database.PostgreSql.PostgreSqlOptions.TlsMode { get; set; }
```

**summary:** Gets or sets the TLS policy; defaults to VerifyFull.

**remarks:** Unknown enum values reject. DisableForLocalDevelopment is an explicit insecure development selection, never an automatic fallback after certificate failure.

## `T:NativeWeave.Database.PostgreSql.PostgreSqlDataSource`

```csharp
public static class NativeWeave.Database.PostgreSql.PostgreSqlDataSource
```

**summary:** Creates PostgreSQL datasources backed by the maintainer-built Rust Database Host.

**remarks:** Reading Engine is pure metadata. Inspect verifies the asset and starts no runtime or connection. Create snapshots typed options before native admission.

## `T:NativeWeave.Database.PostgreSql.PostgreSqlDataSourceBuilderExtensions`

```csharp
public static class NativeWeave.Database.PostgreSql.PostgreSqlDataSourceBuilderExtensions
```

**summary:** Configures the independently packaged SQLx PostgreSQL engine.

**remarks:** The builder remains single-writer. Configuration snapshots managed values without I/O; Build negotiates the separately packaged native engine and creates the source owner.

## `T:NativeWeave.Database.PostgreSql.PostgreSqlOptions`

```csharp
public sealed class NativeWeave.Database.PostgreSql.PostgreSqlOptions
```

**summary:** Configures the SQLx PostgreSQL provider before a datasource is opened.

**remarks:** Mutable configuration is snapshotted by the owning B04 factory before native admission. Do not mutate it during configuration. It starts no runtime and opens no connection. Invalid values fail before opening. Connection strings use a PostgreSQL TCP URI with explicit user and database; query-string options and ambient PG* policy variables are rejected, so they cannot weaken this typed TLS policy. The component has no managed database fallback.

## `T:NativeWeave.Database.PostgreSql.PostgreSqlTlsMode`

```csharp
public enum NativeWeave.Database.PostgreSql.PostgreSqlTlsMode : int
```

**summary:** Chooses certificate and hostname verification or explicit development plaintext.

**remarks:** The ordinal values are the native kind8 TLS policy. There is no Prefer, Require or certificate-validation bypass mode.
