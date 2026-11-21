# NativeWeave.Database.Sqlite API reference

Generated from the compiled product assembly and its XML comments by `tests/Data.Sqlite/ApiCheck`. Covers provider options, Engine preflight, and the integrated Create/UseSqlite data source factories. Exact declarations retain the pinned Design identity in `public-api.expected.json`; the historical B03/B04 ownership slice remains in `host-composition.expected.json`.

## `F:NativeWeave.Database.Sqlite.SqliteBeginMode.Deferred`

```csharp
NativeWeave.Database.Sqlite.SqliteBeginMode.Deferred = 0
```

**summary:** Defers writer admission until the transaction first writes.

## `F:NativeWeave.Database.Sqlite.SqliteBeginMode.Immediate`

```csharp
NativeWeave.Database.Sqlite.SqliteBeginMode.Immediate = 1
```

**summary:** Acquires SQLite writer admission when the tracked transaction begins.

## `F:NativeWeave.Database.Sqlite.SqliteJournalMode.Delete`

```csharp
NativeWeave.Database.Sqlite.SqliteJournalMode.Delete = 1
```

**summary:** Uses a rollback journal deleted after a completed transaction.

## `F:NativeWeave.Database.Sqlite.SqliteJournalMode.Memory`

```csharp
NativeWeave.Database.Sqlite.SqliteJournalMode.Memory = 2
```

**summary:** Stores the rollback journal in memory; file-backed crash durability is weaker.

## `F:NativeWeave.Database.Sqlite.SqliteJournalMode.Wal`

```csharp
NativeWeave.Database.Sqlite.SqliteJournalMode.Wal = 0
```

**summary:** Uses a write-ahead log for a file-backed database; it does not allow concurrent writers.

## `F:NativeWeave.Database.Sqlite.SqliteOpenMode.Memory`

```csharp
NativeWeave.Database.Sqlite.SqliteOpenMode.Memory = 3
```

**summary:** Uses a private in-memory database with Memory journal and one physical connection.

## `F:NativeWeave.Database.Sqlite.SqliteOpenMode.ReadOnly`

```csharp
NativeWeave.Database.Sqlite.SqliteOpenMode.ReadOnly = 2
```

**summary:** Opens an existing file without write permission.

## `F:NativeWeave.Database.Sqlite.SqliteOpenMode.ReadWrite`

```csharp
NativeWeave.Database.Sqlite.SqliteOpenMode.ReadWrite = 1
```

**summary:** Opens an existing writable file; a missing file fails.

## `F:NativeWeave.Database.Sqlite.SqliteOpenMode.ReadWriteCreate`

```csharp
NativeWeave.Database.Sqlite.SqliteOpenMode.ReadWriteCreate = 0
```

**summary:** Opens a writable file and creates it when absent.

## `F:NativeWeave.Database.Sqlite.SqliteSynchronousMode.Full`

```csharp
NativeWeave.Database.Sqlite.SqliteSynchronousMode.Full = 1
```

**summary:** Uses SQLite's full synchronization policy.

## `F:NativeWeave.Database.Sqlite.SqliteSynchronousMode.Normal`

```csharp
NativeWeave.Database.Sqlite.SqliteSynchronousMode.Normal = 0
```

**summary:** Uses SQLite's normal synchronization policy.

## `M:NativeWeave.Database.Sqlite.SqliteBeginMode.#ctor`

```csharp
public NativeWeave.Database.Sqlite.SqliteBeginMode.SqliteBeginMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.Sqlite.SqliteDataSource.Create(System.String,System.Action{NativeWeave.Database.Sqlite.SqliteOptions})`

```csharp
public static NativeWeave.Database.DataSource NativeWeave.Database.Sqlite.SqliteDataSource.Create(string path, System.Action<NativeWeave.Database.Sqlite.SqliteOptions>? configure = null)
```

**summary:** Creates one independently owned lazy native SQLite data source.

**param path:** The nonempty database path; no connection is opened during construction.

**param configure:** An optional synchronous options callback whose values are immediately snapshotted.

**returns:** A data source whose sessions and source should be asynchronously disposed.

**exception:** The path or options are invalid.

**exception:** is null.

**exception:** The exact packaged module cannot be negotiated.

## `M:NativeWeave.Database.Sqlite.SqliteDataSourceBuilderExtensions.UseSqlite(NativeWeave.Database.DataSourceBuilder,System.String,System.Action{NativeWeave.Database.Sqlite.SqliteOptions})`

```csharp
public static NativeWeave.Database.DataSourceBuilder NativeWeave.Database.Sqlite.SqliteDataSourceBuilderExtensions.UseSqlite(this NativeWeave.Database.DataSourceBuilder builder, string path, System.Action<NativeWeave.Database.Sqlite.SqliteOptions>? configure = null)
```

**summary:** Snapshots SQLite configuration without loading a module or opening a database.

**param builder:** The single-writer source builder.

**param path:** The nonempty database path.

**param configure:** Optional synchronous configuration; exceptions prevent builder mutation.

**returns:** The supplied builder.

**exception:** The builder or path is null.

**exception:** A provider setting or path is invalid.

## `M:NativeWeave.Database.Sqlite.SqliteJournalMode.#ctor`

```csharp
public NativeWeave.Database.Sqlite.SqliteJournalMode.SqliteJournalMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.Sqlite.SqliteOpenMode.#ctor`

```csharp
public NativeWeave.Database.Sqlite.SqliteOpenMode.SqliteOpenMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.Sqlite.SqliteOptions.#ctor`

```csharp
public NativeWeave.Database.Sqlite.SqliteOptions.SqliteOptions()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.Sqlite.SqliteSynchronousMode.#ctor`

```csharp
public NativeWeave.Database.Sqlite.SqliteSynchronousMode.SqliteSynchronousMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `P:NativeWeave.Database.Sqlite.SqliteDataSource.Engine`

```csharp
public static NativeWeave.Interop.EngineDescriptor NativeWeave.Database.Sqlite.SqliteDataSource.Engine { get; }
```

**summary:** Gets the immutable descriptor of the complete SQLite Database Host asset.

**remarks:** The canonical database bootstrap negotiates only capabilities implemented by this asset. Missing or mismatched assets fail inspection before runtime admission.

## `P:NativeWeave.Database.Sqlite.SqliteOptions.BeginMode`

```csharp
public NativeWeave.Database.Sqlite.SqliteBeginMode NativeWeave.Database.Sqlite.SqliteOptions.BeginMode { get; set; }
```

**summary:** Gets or sets Deferred or Immediate writer admission without changing the isolation level.

## `P:NativeWeave.Database.Sqlite.SqliteOptions.BusyTimeout`

```csharp
public System.TimeSpan NativeWeave.Database.Sqlite.SqliteOptions.BusyTimeout { get; set; }
```

**summary:** Gets or sets the native busy timeout, from zero through Int32.MaxValue milliseconds in whole milliseconds.

**remarks:** Zero fails immediately on lock contention. This is a SQLite busy-handler bound, not an operation deadline. Unsupported submillisecond precision rejects rather than truncating.

## `P:NativeWeave.Database.Sqlite.SqliteOptions.ForeignKeys`

```csharp
public bool NativeWeave.Database.Sqlite.SqliteOptions.ForeignKeys { get; set; }
```

**summary:** Gets or sets foreign-key enforcement on every physical connection; the default is true.

## `P:NativeWeave.Database.Sqlite.SqliteOptions.JournalMode`

```csharp
public NativeWeave.Database.Sqlite.SqliteJournalMode NativeWeave.Database.Sqlite.SqliteOptions.JournalMode { get; set; }
```

**summary:** Gets or sets the journal profile. Incompatible private-memory/WAL combinations reject before opening.

## `P:NativeWeave.Database.Sqlite.SqliteOptions.Mode`

```csharp
public NativeWeave.Database.Sqlite.SqliteOpenMode NativeWeave.Database.Sqlite.SqliteOptions.Mode { get; set; }
```

**summary:** Gets or sets file access. Memory requires Memory journal and a host limit of one connection.

## `P:NativeWeave.Database.Sqlite.SqliteOptions.Synchronous`

```csharp
public NativeWeave.Database.Sqlite.SqliteSynchronousMode NativeWeave.Database.Sqlite.SqliteOptions.Synchronous { get; set; }
```

**summary:** Gets or sets the synchronization profile applied to every physical connection.

## `T:NativeWeave.Database.Sqlite.SqliteBeginMode`

```csharp
public enum NativeWeave.Database.Sqlite.SqliteBeginMode : int
```

**summary:** Selects writer admission separately from transaction isolation.

## `T:NativeWeave.Database.Sqlite.SqliteDataSource`

```csharp
public static class NativeWeave.Database.Sqlite.SqliteDataSource
```

**summary:** Creates SQLite datasources backed by the maintainer-built Rust Database Host.

**remarks:** Descriptor access is pure metadata. Inspect verifies the packaged asset without creating a runtime or opening a connection; Create owns the configured runtime and datasource.

## `T:NativeWeave.Database.Sqlite.SqliteDataSourceBuilderExtensions`

```csharp
public static class NativeWeave.Database.Sqlite.SqliteDataSourceBuilderExtensions
```

**summary:** Configures the explicitly selected independently packaged SQLite engine.

**remarks:** The builder remains single-writer. Configuration snapshots managed values without I/O; Build negotiates the separately packaged native engine and creates the source owner.

## `T:NativeWeave.Database.Sqlite.SqliteJournalMode`

```csharp
public enum NativeWeave.Database.Sqlite.SqliteJournalMode : int
```

**summary:** Selects SQLite's explicitly configured journal profile on every physical connection.

## `T:NativeWeave.Database.Sqlite.SqliteOpenMode`

```csharp
public enum NativeWeave.Database.Sqlite.SqliteOpenMode : int
```

**summary:** Specifies how the Rust SQLite provider opens the configured database.

## `T:NativeWeave.Database.Sqlite.SqliteOptions`

```csharp
public sealed class NativeWeave.Database.Sqlite.SqliteOptions
```

**summary:** Configures the precompiled Rust SQLx SQLite provider.

**remarks:** Configure before source creation. A builder snapshots these mutable values once; concurrent mutation during snapshot is unsupported. Values do not create a connection, worker or runtime. Each physical connection receives this profile. Ordinary SQLite isolation is Serializable; BEGIN mode is independent. Progress cancellation is cooperative and cannot preempt every busy wait or native instruction.

## `T:NativeWeave.Database.Sqlite.SqliteSynchronousMode`

```csharp
public enum NativeWeave.Database.Sqlite.SqliteSynchronousMode : int
```

**summary:** Selects the SQLite synchronization policy without claiming a filesystem durability guarantee.

