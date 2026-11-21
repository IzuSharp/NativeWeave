# NativeWeave.Data explicit relationship and mutation API

Generated from the compiled product assembly and XML by `src/Build.Integration/ApiReference`.

Compiled product declarations compared to Design commit c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9. B14 owns explicit relation loading, native CRUD, optimistic concurrency and bounded bulk; docs/guides/orm-relations.md explains ownership, limits and cost.

## `F:NativeWeave.Data.DatabaseErrorKind.ConcurrentUse`

```csharp
NativeWeave.Data.DatabaseErrorKind.ConcurrentUse = 6
```

**summary:** A single-command owner already admits another operation.

## `F:NativeWeave.Data.DatabaseErrorKind.Constraint`

```csharp
NativeWeave.Data.DatabaseErrorKind.Constraint = 1
```

**summary:** A database constraint or expected affected-row condition failed.

## `F:NativeWeave.Data.DatabaseErrorKind.Conversion`

```csharp
NativeWeave.Data.DatabaseErrorKind.Conversion = 2
```

**summary:** A value cannot be represented exactly by its declared codec.

## `F:NativeWeave.Data.DatabaseErrorKind.InvalidState`

```csharp
NativeWeave.Data.DatabaseErrorKind.InvalidState = 7
```

**summary:** The operation is invalid for the owner's current state or metadata.

## `F:NativeWeave.Data.DatabaseErrorKind.Provider`

```csharp
NativeWeave.Data.DatabaseErrorKind.Provider = 0
```

**summary:** The provider reported a failure.

## `F:NativeWeave.Data.DatabaseErrorKind.ResourceLimit`

```csharp
NativeWeave.Data.DatabaseErrorKind.ResourceLimit = 5
```

**summary:** A configured finite resource limit was exceeded.

## `F:NativeWeave.Data.DatabaseErrorKind.ShapeMismatch`

```csharp
NativeWeave.Data.DatabaseErrorKind.ShapeMismatch = 3
```

**summary:** The complete result shape differs from the declared projection.

## `F:NativeWeave.Data.DatabaseErrorKind.UnknownOutcome`

```csharp
NativeWeave.Data.DatabaseErrorKind.UnknownOutcome = 8
```

**summary:** The external outcome cannot be established; automatic retry is unsafe.

## `F:NativeWeave.Data.DatabaseErrorKind.UnsupportedCapability`

```csharp
NativeWeave.Data.DatabaseErrorKind.UnsupportedCapability = 4
```

**summary:** The selected engine or provider cannot perform the requested operation.

## `F:NativeWeave.Data.SqlCommandKind.Mutation`

```csharp
NativeWeave.Data.SqlCommandKind.Mutation = 1
```

**summary:** A mutation whose affected-row count must be observed.

## `F:NativeWeave.Data.SqlCommandKind.Query`

```csharp
NativeWeave.Data.SqlCommandKind.Query = 0
```

**summary:** A result-bearing query.

## `F:NativeWeave.Data.SqlCommandKind.SessionMutating`

```csharp
NativeWeave.Data.SqlCommandKind.SessionMutating = 2
```

**summary:** Expert session-changing SQL requiring independent admission and connection retirement policy.

## `M:NativeWeave.Data.Changes`1.#ctor`

```csharp
public NativeWeave.Data.Changes<TEntity>.Changes()
```

**summary:** Creates an empty changeset; execution requires at least one assignment.

**Inherited type policy:** This is assignment data, not a SQL AST. Unset removes an assignment; Set with a nullable value assigns SQL NULL. Native execution snapshots the current changes independently and rejects an empty set.

## `M:NativeWeave.Data.Changes`1.Set``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Data.Changes<TEntity> NativeWeave.Data.Changes<TEntity>.Set<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Copies a value and adds or replaces one nonkey, nongenerated column assignment.

**typeparam T:** The exact column value type.

**param column:** A column from the changeset's single table.

**param value:** The value to snapshot.

**returns:** This changeset for fluent configuration.

**exception:** A required argument is null.

**exception:** The column is foreign, a key, generated, unbuilt or the value is invalid.

**Inherited type policy:** This is assignment data, not a SQL AST. Unset removes an assignment; Set with a nullable value assigns SQL NULL. Native execution snapshots the current changes independently and rejects an empty set.

## `M:NativeWeave.Data.Changes`1.Unset``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Data.Changes<TEntity> NativeWeave.Data.Changes<TEntity>.Unset<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Removes an assignment without assigning SQL NULL.

**typeparam T:** The exact column value type.

**param column:** A nonkey, nongenerated column from the same table.

**returns:** This changeset.

**exception:** is null.

**exception:** The column is foreign, a key, generated or unbuilt.

**Inherited type policy:** This is assignment data, not a SQL AST. Unset removes an assignment; Set with a nullable value assigns SQL NULL. Native execution snapshots the current changes independently and rejects an empty set.

## `M:NativeWeave.Data.Codecs.Decimal(System.Byte,System.Byte)`

```csharp
public static NativeWeave.Data.ValueCodec<decimal> NativeWeave.Data.Codecs.Decimal(byte precision, byte scale)
```

**summary:** Selects exact decimal numeric precision and scale; ordinary SQLite does not support this provider profile.

**param precision:** Total decimal precision from one through 29.

**param scale:** Scale from zero through the smaller of 28 and precision.

**returns:** An immutable configured logical codec.

**exception:** The precision or scale is outside the declared range.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `M:NativeWeave.Data.Codecs.EnumInt32``1`

```csharp
public static NativeWeave.Data.ValueCodec<TEnum> NativeWeave.Data.Codecs.EnumInt32<TEnum>() where TEnum : struct, System.Enum
```

**summary:** Selects a checked signed Int32 enum representation, preserving undefined numeric values.

**typeparam TEnum:** A statically known CLR enum.

**returns:** An immutable enum codec; values outside Int32 reject at snapshot.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `M:NativeWeave.Data.Codecs.FixedScaleMoney(System.Byte)`

```csharp
public static NativeWeave.Data.ValueCodec<decimal> NativeWeave.Data.Codecs.FixedScaleMoney(byte scale)
```

**summary:** Selects exact signed Int64 fixed-scale storage, without rounding.

**param scale:** The decimal scale from zero through 18.

**returns:** An immutable configured money codec.

**exception:** exceeds 18.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `M:NativeWeave.Data.Codecs.Json``1(System.Text.Json.Serialization.Metadata.JsonTypeInfo{``0})`

```csharp
public static NativeWeave.Data.ValueCodec<T> NativeWeave.Data.Codecs.Json<T>(System.Text.Json.Serialization.Metadata.JsonTypeInfo<T> typeInfo)
```

**summary:** Selects JSON serialization using explicit static metadata; JSON null is distinct from SQL NULL.

**typeparam T:** The statically serializable value.

**param typeInfo:** Explicit source-generated or manually authored JSON metadata.

**returns:** An immutable typed JSON codec that retains the supplied metadata.

**exception:** is null.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `M:NativeWeave.Data.Codecs.NullableReference``1(NativeWeave.Data.ValueCodec{``0})`

```csharp
public static NativeWeave.Data.ValueCodec<T?> NativeWeave.Data.Codecs.NullableReference<T>(NativeWeave.Data.ValueCodec<T> codec) where T : class
```

**summary:** Adds SQL NULL support to a reference codec while preserving its logical scalar identity.

**typeparam T:** The reference type.

**param codec:** The selected non-null scalar codec.

**returns:** A nullable reference codec.

**exception:** is null.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `M:NativeWeave.Data.Codecs.Nullable``1(NativeWeave.Data.ValueCodec{``0})`

```csharp
public static NativeWeave.Data.ValueCodec<T?> NativeWeave.Data.Codecs.Nullable<T>(NativeWeave.Data.ValueCodec<T> codec) where T : struct
```

**summary:** Adds SQL NULL support to a value codec without changing its logical scalar identity.

**typeparam T:** A non-nullable value type.

**param codec:** The selected non-null scalar codec.

**returns:** A typed nullable codec with the same configuration.

**exception:** is null.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `M:NativeWeave.Data.ColumnOptions.#ctor`

```csharp
public NativeWeave.Data.ColumnOptions.ColumnOptions()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.Equals(NativeWeave.Data.ColumnOptions)`

```csharp
public bool NativeWeave.Data.ColumnOptions.Equals(NativeWeave.Data.ColumnOptions? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.Equals(System.Object)`

```csharp
public override bool NativeWeave.Data.ColumnOptions.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.GetHashCode`

```csharp
public override int NativeWeave.Data.ColumnOptions.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.ToString`

```csharp
public override string NativeWeave.Data.ColumnOptions.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.op_Equality(NativeWeave.Data.ColumnOptions,NativeWeave.Data.ColumnOptions)`

```csharp
public static bool NativeWeave.Data.ColumnOptions.operator ==(NativeWeave.Data.ColumnOptions? left, NativeWeave.Data.ColumnOptions? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.op_Inequality(NativeWeave.Data.ColumnOptions,NativeWeave.Data.ColumnOptions)`

```csharp
public static bool NativeWeave.Data.ColumnOptions.operator !=(NativeWeave.Data.ColumnOptions? left, NativeWeave.Data.ColumnOptions? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ColumnOptions.{Clone}$`

```csharp
public NativeWeave.Data.ColumnOptions NativeWeave.Data.ColumnOptions.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `M:NativeWeave.Data.ConcurrencyCheck`1.#ctor`

```csharp
public NativeWeave.Data.ConcurrencyCheck<TEntity>.ConcurrencyCheck()
```

**summary:** Creates an empty check; execution requires all declared concurrency tokens.

**Inherited type policy:** Values are copied immediately. There is no identity map, implicit version increment or managed compare-and-swap.

## `M:NativeWeave.Data.ConcurrencyCheck`1.Expect``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Data.ConcurrencyCheck<TEntity> NativeWeave.Data.ConcurrencyCheck<TEntity>.Expect<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Snapshots one declared expected token.

**typeparam T:** The token value type.

**param column:** A declared concurrency token from one built table.

**param value:** The expected value.

**returns:** This check.

**exception:** A required argument is null.

**exception:** The token is foreign, repeated, unbuilt or not marked for concurrency.

**Inherited type policy:** Values are copied immediately. There is no identity map, implicit version increment or managed compare-and-swap.

## `M:NativeWeave.Data.ConcurrencyConflictException.#ctor(System.String,System.Int64,System.Int64)`

```csharp
public NativeWeave.Data.ConcurrencyConflictException.ConcurrencyConflictException(string message, long expectedRows, long actualRows)
```

**summary:** Creates an immutable expected/actual count diagnostic.

**param message:** The non-null diagnostic message.

**param expectedRows:** The nonnegative expected affected-row count.

**param actualRows:** The nonnegative actual affected-row count.

**exception:** is null.

**exception:** A count is negative.

**Inherited type policy:** The original key and expected token predicate ran once in the database. This exception never authorizes a write replay.

## `M:NativeWeave.Data.DatabaseCapabilityException.#ctor(System.String,System.String)`

```csharp
public NativeWeave.Data.DatabaseCapabilityException.DatabaseCapabilityException(string capability, string provider)
```

**summary:** Creates a failure that must be reported before a native business side effect.

**param capability:** The nonempty stable capability name.

**param provider:** The nonempty provider identity.

**exception:** An identity is empty or contains invalid Unicode.

**exception:** An identity is null.

**Inherited type policy:** The owned exception retains validated managed identity strings and no native handle. Constructing or reading it performs no provider call; capability admission rejects before business dispatch.

## `M:NativeWeave.Data.DatabaseErrorKind.#ctor`

```csharp
public NativeWeave.Data.DatabaseErrorKind.DatabaseErrorKind()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Data.DatabaseException.#ctor(System.String,NativeWeave.Data.DatabaseErrorKind,System.String,System.UInt64,System.Exception)`

```csharp
public NativeWeave.Data.DatabaseException.DatabaseException(string message, NativeWeave.Data.DatabaseErrorKind kind, string? providerCode = null, ulong correlationId = 0, System.Exception? innerException = null)
```

**summary:** Creates a database failure without inferring provider transience.

**param message:** The diagnostic message, without credentials or parameter values.

**param kind:** The provider-neutral category.

**param providerCode:** An optional provider error code.

**param correlationId:** The native diagnostic correlation, or zero when absent.

**param innerException:** The original cause, if available.

**exception:** is null.

**exception:** is undefined.

**Inherited type policy:** Diagnostic values are immutable and remain readable after cleanup. Construction loads no native engine. A transient cause is not permission to retry a write; outcome and application idempotency remain separate.

## `M:NativeWeave.Data.EntityKey`1.And``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Data.EntityKey<TEntity> NativeWeave.Data.EntityKey<TEntity>.And<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Returns a new snapshot with the next primary-key component appended.

**typeparam T:** The next component's value type.

**param column:** The next column in this table's primary-key declaration order.

**param value:** The non-null value, copied before return.

**returns:** A new immutable key; the current instance is unchanged.

**exception:** A required column or non-null value is null.

**exception:** The column is foreign, repeated, nullable, nonkey or out of key order.

**Inherited type policy:** Incomplete prefixes are construction values only; registration or execution requires the complete key.

## `M:NativeWeave.Data.EntityWriter`1.#ctor(System.Object,System.IntPtr)`

```csharp
public NativeWeave.Data.EntityWriter<T>.EntityWriter(object @object, nint method)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously during a finite input snapshot. Typed writes copy encoded values into owned buffers before native dispatch; the stack-only writer must not be retained.

## `M:NativeWeave.Data.EntityWriter`1.BeginInvoke(NativeWeave.Data.RowWriter,`0,System.AsyncCallback,System.Object)`

```csharp
public virtual System.IAsyncResult NativeWeave.Data.EntityWriter<T>.BeginInvoke(NativeWeave.Data.RowWriter row, T value, System.AsyncCallback callback, object @object)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously during a finite input snapshot. Typed writes copy encoded values into owned buffers before native dispatch; the stack-only writer must not be retained.

## `M:NativeWeave.Data.EntityWriter`1.EndInvoke(System.IAsyncResult)`

```csharp
public virtual void NativeWeave.Data.EntityWriter<T>.EndInvoke(System.IAsyncResult result)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously during a finite input snapshot. Typed writes copy encoded values into owned buffers before native dispatch; the stack-only writer must not be retained.

## `M:NativeWeave.Data.EntityWriter`1.Invoke(NativeWeave.Data.RowWriter,`0)`

```csharp
public virtual void NativeWeave.Data.EntityWriter<T>.Invoke(NativeWeave.Data.RowWriter row, T value)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously during a finite input snapshot. Typed writes copy encoded values into owned buffers before native dispatch; the stack-only writer must not be retained.

## `M:NativeWeave.Data.Projection`1.Create(System.ReadOnlySpan{NativeWeave.Data.ResultField},NativeWeave.Data.RowMaterializer{`0})`

```csharp
public static NativeWeave.Data.Projection<T> NativeWeave.Data.Projection<T>.Create(System.ReadOnlySpan<NativeWeave.Data.ResultField> fields, NativeWeave.Data.RowMaterializer<T> materializer)
```

**summary:** Copies a unique ordered field sequence and retains an AOT-visible materializer.

**param fields:** At least one non-null field with a unique exact alias.

**param materializer:** A synchronous typed constructor.

**returns:** An immutable projection.

**exception:** The materializer is null.

**exception:** Fields are empty, contain nulls or duplicate aliases.

**Inherited type policy:** Creation copies the field sequence and hashes canonical metadata. Materializers stay managed; no CLR delegate or function pointer is encoded in metadata. Instances are shareable if their delegates are.

## `M:NativeWeave.Data.Relation`2.AndOptionalReference``1(NativeWeave.Data.Column{`0,``0},NativeWeave.Data.Column{`1,``0})`

```csharp
public NativeWeave.Data.Relation<TParent, TChild> NativeWeave.Data.Relation<TParent, TChild>.AndOptionalReference<T>(NativeWeave.Data.Column<TParent, T> parentKey, NativeWeave.Data.Column<TChild, T?> foreignKey) where T : class
```

**summary:** Returns a new relation with the next optional reference-key pair.

**typeparam T:** The parent reference type.

**param parentKey:** The next parent key.

**param foreignKey:** The matching nullable child column.

**returns:** A new immutable relation.

**exception:** An argument is null.

**exception:** The pair violates identity, ordering or codec rules.

**Inherited type policy:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `M:NativeWeave.Data.Relation`2.AndOptional``1(NativeWeave.Data.Column{`0,``0},NativeWeave.Data.Column{`1,System.Nullable{``0}})`

```csharp
public NativeWeave.Data.Relation<TParent, TChild> NativeWeave.Data.Relation<TParent, TChild>.AndOptional<T>(NativeWeave.Data.Column<TParent, T> parentKey, NativeWeave.Data.Column<TChild, T?> foreignKey) where T : struct
```

**summary:** Returns a new relation with the next optional value-key pair.

**typeparam T:** The non-null parent value type.

**param parentKey:** The next parent key.

**param foreignKey:** The matching nullable child column.

**returns:** A new immutable relation.

**exception:** An argument is null.

**exception:** The pair violates identity, ordering or codec rules.

**Inherited type policy:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `M:NativeWeave.Data.Relation`2.And``1(NativeWeave.Data.Column{`0,``0},NativeWeave.Data.Column{`1,``0})`

```csharp
public NativeWeave.Data.Relation<TParent, TChild> NativeWeave.Data.Relation<TParent, TChild>.And<T>(NativeWeave.Data.Column<TParent, T> parentKey, NativeWeave.Data.Column<TChild, T> foreignKey)
```

**summary:** Returns a new relation with the next non-null key pair appended.

**typeparam T:** The common scalar value type.

**param parentKey:** The next parent primary-key component.

**param foreignKey:** A distinct compatible non-null child column.

**returns:** A new immutable relation.

**exception:** An argument is null.

**exception:** The pair violates identity, ordering or codec rules.

**Inherited type policy:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `M:NativeWeave.Data.Relation`2.CreateOptionalReference``1(NativeWeave.Data.Table{`0},NativeWeave.Data.Column{`0,``0},NativeWeave.Data.Table{`1},NativeWeave.Data.Column{`1,``0})`

```csharp
public static NativeWeave.Data.Relation<TParent, TChild> NativeWeave.Data.Relation<TParent, TChild>.CreateOptionalReference<T>(NativeWeave.Data.Table<TParent> parent, NativeWeave.Data.Column<TParent, T> parentKey, NativeWeave.Data.Table<TChild> child, NativeWeave.Data.Column<TChild, T?> foreignKey) where T : class
```

**summary:** Starts a relation from a non-null reference key to a nullable child reference.

**typeparam T:** The parent reference type.

**param parent:** The built parent table.

**param parentKey:** Its first primary-key component.

**param child:** The built child table.

**param foreignKey:** The compatible nullable child column.

**returns:** An immutable relation prefix.

**exception:** An argument is null.

**exception:** The pair violates identity, ordering or codec rules.

**Inherited type policy:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `M:NativeWeave.Data.Relation`2.CreateOptional``1(NativeWeave.Data.Table{`0},NativeWeave.Data.Column{`0,``0},NativeWeave.Data.Table{`1},NativeWeave.Data.Column{`1,System.Nullable{``0}})`

```csharp
public static NativeWeave.Data.Relation<TParent, TChild> NativeWeave.Data.Relation<TParent, TChild>.CreateOptional<T>(NativeWeave.Data.Table<TParent> parent, NativeWeave.Data.Column<TParent, T> parentKey, NativeWeave.Data.Table<TChild> child, NativeWeave.Data.Column<TChild, T?> foreignKey) where T : struct
```

**summary:** Starts a relation from a value key to a nullable child foreign key.

**typeparam T:** The non-null parent value type.

**param parent:** The built parent table.

**param parentKey:** Its first primary-key component.

**param child:** The built child table.

**param foreignKey:** The compatible nullable child column.

**returns:** An immutable relation prefix.

**exception:** An argument is null.

**exception:** The pair violates identity, ordering or codec rules.

**Inherited type policy:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `M:NativeWeave.Data.Relation`2.Create``1(NativeWeave.Data.Table{`0},NativeWeave.Data.Column{`0,``0},NativeWeave.Data.Table{`1},NativeWeave.Data.Column{`1,``0})`

```csharp
public static NativeWeave.Data.Relation<TParent, TChild> NativeWeave.Data.Relation<TParent, TChild>.Create<T>(NativeWeave.Data.Table<TParent> parent, NativeWeave.Data.Column<TParent, T> parentKey, NativeWeave.Data.Table<TChild> child, NativeWeave.Data.Column<TChild, T> foreignKey)
```

**summary:** Starts a relation at key ordinal zero with a non-null foreign key.

**typeparam T:** The common scalar value type.

**param parent:** The built parent table.

**param parentKey:** Its first non-null primary-key column.

**param child:** The built child table.

**param foreignKey:** A compatible non-null child column.

**returns:** An immutable relation prefix.

**exception:** An argument is null.

**exception:** Identity, key order, codec, configuration, collation or nullability differs.

**Inherited type policy:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `M:NativeWeave.Data.ResultColumn`1.#ctor`

```csharp
public NativeWeave.Data.ResultColumn<T>.ResultColumn()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The default token is invalid; no public constructor can forge projection ownership.

## `M:NativeWeave.Data.ResultField.Create``1(System.String,NativeWeave.Data.ValueCodec{``0})`

```csharp
public static NativeWeave.Data.ResultField NativeWeave.Data.ResultField.Create<T>(string name, NativeWeave.Data.ValueCodec<T> codec)
```

**summary:** Creates a field for a static projection.

**typeparam T:** The statically known CLR value type.

**param name:** The nonempty exact result alias.

**param codec:** The selected scalar codec, configuration and nullability.

**returns:** An immutable result-field definition.

**exception:** A required argument is null.

**exception:** The alias is empty or invalid Unicode.

**Inherited type policy:** Creating a field allocates one managed metadata object with no native resource. It can be retained in a static projection; source-specific codec binding occurs separately at registration.

## `M:NativeWeave.Data.RowMaterializer`1.#ctor(System.Object,System.IntPtr)`

```csharp
public NativeWeave.Data.RowMaterializer<T>.RowMaterializer(object @object, nint method)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously while its batch lease is live. Decoding and the application constructor create owned CLR values; borrowed reader state must not escape or cross an await.

## `M:NativeWeave.Data.RowMaterializer`1.BeginInvoke(NativeWeave.Data.RowReader,System.AsyncCallback,System.Object)`

```csharp
public virtual System.IAsyncResult NativeWeave.Data.RowMaterializer<T>.BeginInvoke(NativeWeave.Data.RowReader row, System.AsyncCallback callback, object @object)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously while its batch lease is live. Decoding and the application constructor create owned CLR values; borrowed reader state must not escape or cross an await.

## `M:NativeWeave.Data.RowMaterializer`1.EndInvoke(System.IAsyncResult)`

```csharp
public virtual T NativeWeave.Data.RowMaterializer<T>.EndInvoke(System.IAsyncResult result)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously while its batch lease is live. Decoding and the application constructor create owned CLR values; borrowed reader state must not escape or cross an await.

## `M:NativeWeave.Data.RowMaterializer`1.Invoke(NativeWeave.Data.RowReader)`

```csharp
public virtual T NativeWeave.Data.RowMaterializer<T>.Invoke(NativeWeave.Data.RowReader row)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The callback runs synchronously while its batch lease is live. Decoding and the application constructor create owned CLR values; borrowed reader state must not escape or cross an await.

## `M:NativeWeave.Data.RowReader.#ctor`

```csharp
public NativeWeave.Data.RowReader.RowReader()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Shape validation precedes NULL interpretation. Every read checks the lease; default readers reject. Values are owned CLR copies. Readers cannot be retained across await or stored in an ordinary heap object.

## `M:NativeWeave.Data.RowReader.Get``1(NativeWeave.Data.ResultColumn{``0})`

```csharp
public T NativeWeave.Data.RowReader.Get<T>(NativeWeave.Data.ResultColumn<T> column)
```

**summary:** Reads a typed token belonging to this exact projection.

**typeparam T:** The result value type.

**param column:** The projection-bound result token.

**returns:** An owned value, possibly SQL NULL when declared nullable.

**exception:** The token belongs to another projection or is default.

**exception:** The shape or value is incompatible.

**exception:** The reader is default.

**exception:** The row lease has retired.

**Inherited type policy:** Shape validation precedes NULL interpretation. Every read checks the lease; default readers reject. Values are owned CLR copies. Readers cannot be retained across await or stored in an ordinary heap object.

## `M:NativeWeave.Data.RowReader.Get``2(NativeWeave.Data.Column{``0,``1})`

```csharp
public T NativeWeave.Data.RowReader.Get<TEntity, T>(NativeWeave.Data.Column<TEntity, T> column) where TEntity : class
```

**summary:** Reads a typed token from this table's declared row projection.

**typeparam TEntity:** The application entity type.

**typeparam T:** The value type.

**param column:** The column from the exact table declaration.

**returns:** An owned value.

**exception:** is null.

**exception:** The token belongs to another table.

**exception:** The shape or value is incompatible.

**exception:** The row lease has retired.

**Inherited type policy:** Shape validation precedes NULL interpretation. Every read checks the lease; default readers reject. Values are owned CLR copies. Readers cannot be retained across await or stored in an ordinary heap object.

## `M:NativeWeave.Data.RowReader.IsNull(System.Int32)`

```csharp
public bool NativeWeave.Data.RowReader.IsNull(int ordinal)
```

**summary:** Tests SQL NULL after complete shape validation; missing fields never mean NULL.

**param ordinal:** A zero-based ordinal in the complete declared shape.

**returns:** True for a declared SQL NULL cell.

**exception:** The ordinal is outside the shape.

**exception:** The reader is default.

**exception:** The lease has retired.

**Inherited type policy:** Shape validation precedes NULL interpretation. Every read checks the lease; default readers reject. Values are owned CLR copies. Readers cannot be retained across await or stored in an ordinary heap object.

## `M:NativeWeave.Data.RowReader.Read``1(System.Int32,NativeWeave.Data.ValueCodec{``0})`

```csharp
public T NativeWeave.Data.RowReader.Read<T>(int ordinal, NativeWeave.Data.ValueCodec<T> codec)
```

**summary:** Reads an explicit ordinal with the exact declared scalar configuration and nullability.

**typeparam T:** The statically known value type.

**param ordinal:** A zero-based ordinal.

**param codec:** The exact scalar selection.

**returns:** An owned CLR value.

**exception:** is null.

**exception:** The ordinal is outside the shape.

**exception:** The codec or value does not match the validated shape.

**exception:** The lease has retired.

**Inherited type policy:** Shape validation precedes NULL interpretation. Every read checks the lease; default readers reject. Values are owned CLR copies. Readers cannot be retained across await or stored in an ordinary heap object.

## `M:NativeWeave.Data.RowWriter.#ctor`

```csharp
public NativeWeave.Data.RowWriter.RowWriter()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** A writer is valid only during EntityWriter invocation. Repeated assignment rejects. Insert policy omits generated columns. An exception publishes no partial row to a provider.

## `M:NativeWeave.Data.RowWriter.Set``2(NativeWeave.Data.Column{``0,``1},``1)`

```csharp
public void NativeWeave.Data.RowWriter.Set<TEntity, T>(NativeWeave.Data.Column<TEntity, T> column, T value) where TEntity : class
```

**summary:** Copies one typed value into the current row snapshot.

**typeparam TEntity:** The application entity type.

**typeparam T:** The exact column value type.

**param column:** The matching table's column.

**param value:** The value to snapshot; SQL NULL requires a nullable codec.

**exception:** A required argument or non-null value is null.

**exception:** The column belongs elsewhere or was assigned twice.

**exception:** The writer is default or the snapshot has completed.

**Inherited type policy:** A writer is valid only during EntityWriter invocation. Repeated assignment rejects. Insert policy omits generated columns. An exception publishes no partial row to a provider.

## `M:NativeWeave.Data.SqlCommand.Create(System.String,NativeWeave.Data.SqlParameters,NativeWeave.Data.SqlCommandKind,System.Nullable{System.TimeSpan})`

```csharp
public static NativeWeave.Data.SqlCommand NativeWeave.Data.SqlCommand.Create(string sql, NativeWeave.Data.SqlParameters? parameters = null, NativeWeave.Data.SqlCommandKind kind = NativeWeave.Data.SqlCommandKind.Query, System.TimeSpan? timeout = null)
```

**summary:** Snapshots trusted named SQL and typed parameters without provider work.

**param sql:** Nonempty strict-Unicode trusted SQL with logical @name placeholders.

**param parameters:** Typed parameters, or no parameters.

**param kind:** The explicit effect classification.

**param timeout:** A nonnegative finite timeout, or the source's configured default; zero expires before dispatch.

**returns:** An immutable command; subsequent collection changes do not affect it.

**exception:** is null.

**exception:** The SQL is empty or invalid Unicode.

**exception:** The kind or timeout is invalid.

**Inherited type policy:** This type does not parse SQL, choose dialects, prove safety or contact a provider. Rust transports placeholders and validates actual capability/effect policy before dispatch. Interpolated convenience has boxing costs.

## `M:NativeWeave.Data.SqlCommand.Parameterized(System.FormattableString,NativeWeave.Data.SqlCommandKind,System.Nullable{System.TimeSpan})`

```csharp
public static NativeWeave.Data.SqlCommand NativeWeave.Data.SqlCommand.Parameterized(System.FormattableString sql, NativeWeave.Data.SqlCommandKind kind = NativeWeave.Data.SqlCommandKind.Query, System.TimeSpan? timeout = null)
```

**summary:** Snapshots built-in scalar interpolation values and literal segments, without building SQL.

**param sql:** A composite format with unformatted, unaligned typed non-null scalar arguments.

**param kind:** The explicit effect classification.

**param timeout:** A nonnegative finite timeout, or the source's configured default; zero expires before dispatch.

**returns:** An immutable template whose value holes will be bound by Rust.

**exception:** is null.

**exception:** An argument is untyped null, requires an explicit codec, is unused, or a format/alignment is supplied.

**exception:** The kind or timeout is invalid.

**Inherited type policy:** This type does not parse SQL, choose dialects, prove safety or contact a provider. Rust transports placeholders and validates actual capability/effect policy before dispatch. Interpolated convenience has boxing costs.

## `M:NativeWeave.Data.SqlCommandKind.#ctor`

```csharp
public NativeWeave.Data.SqlCommandKind.SqlCommandKind()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Data.SqlParameters.#ctor`

```csharp
public NativeWeave.Data.SqlParameters.SqlParameters()
```

**summary:** Creates an empty ordered parameter collection.

**Inherited type policy:** Names are case-sensitive ASCII without @. Add copies mutable values immediately; command construction snapshots the collection. Provider placeholder scanning and missing/unused-hole checks remain native B02/B03 work.

## `M:NativeWeave.Data.SqlParameters.Add``1(System.String,``0,NativeWeave.Data.ValueCodec{``0})`

```csharp
public NativeWeave.Data.SqlParameters NativeWeave.Data.SqlParameters.Add<T>(string name, T value, NativeWeave.Data.ValueCodec<T> codec)
```

**summary:** Copies one value using an explicit scalar codec and a unique logical name.

**typeparam T:** The statically known value type.

**param name:** An ASCII name matching [A-Za-z_][A-Za-z0-9_]*, at most 128 bytes.

**param value:** The value; SQL NULL requires an explicit nullable codec.

**param codec:** The scalar codec and configuration.

**returns:** This collection.

**exception:** A required argument is null.

**exception:** The name is invalid/duplicate or the value cannot be encoded exactly.

**Inherited type policy:** Names are case-sensitive ASCII without @. Add copies mutable values immediately; command construction snapshots the collection. Provider placeholder scanning and missing/unused-hole checks remain native B02/B03 work.

## `M:NativeWeave.Data.TableBuilder`1.#ctor(System.String,System.String)`

```csharp
public NativeWeave.Data.TableBuilder<TEntity>.TableBuilder(string tableName, string? schema = null)
```

**summary:** Starts a declaration with exact store names.

**param tableName:** A nonempty strict-Unicode table name.

**param schema:** A nonempty explicit schema or null; null is not an empty string.

**exception:** A name or closed type identity is invalid.

**exception:** is null.

**Inherited type policy:** This single-writer startup builder is consumed by successful Build. It performs O(column count) managed work and loads no native engine. The known closed type is used only for its assembly/name identity.

## `M:NativeWeave.Data.TableBuilder`1.Build(NativeWeave.Data.RowMaterializer{`0},NativeWeave.Data.EntityWriter{`0})`

```csharp
public NativeWeave.Data.Table<TEntity> NativeWeave.Data.TableBuilder<TEntity>.Build(NativeWeave.Data.RowMaterializer<TEntity> materializer, NativeWeave.Data.EntityWriter<TEntity> writer)
```

**summary:** Validates and consumes the builder, retaining direct managed mapping delegates.

**param materializer:** The synchronous typed row constructor.

**param writer:** The synchronous typed entity writer.

**returns:** An immutable table with canonical metadata and row projection.

**exception:** A delegate is null.

**exception:** There are no columns or the builder was already consumed.

**Inherited type policy:** This single-writer startup builder is consumed by successful Build. It performs O(column count) managed work and loads no native engine. The known closed type is used only for its assembly/name identity.

## `M:NativeWeave.Data.TableBuilder`1.Column``1(System.String,NativeWeave.Data.ValueCodec{``0},NativeWeave.Data.ColumnOptions)`

```csharp
public NativeWeave.Data.Column<TEntity, T> NativeWeave.Data.TableBuilder<TEntity>.Column<T>(string name, NativeWeave.Data.ValueCodec<T> codec, NativeWeave.Data.ColumnOptions? options = null)
```

**summary:** Adds a typed column in projection and primary-key declaration order.

**typeparam T:** The exact CLR value type.

**param name:** The exact store column name.

**param codec:** The non-null supported scalar selection.

**param options:** Immutable flags, or default flags.

**returns:** A token tied to this declaration.

**exception:** A duplicate name/ID, nullable key or invalid option is supplied.

**exception:** A required argument is null.

**exception:** The builder was consumed.

**Inherited type policy:** This single-writer startup builder is consumed by successful Build. It performs O(column count) managed work and loads no native engine. The known closed type is used only for its assembly/name identity.

## `M:NativeWeave.Data.Table`1.Key``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Data.EntityKey<TEntity> NativeWeave.Data.Table<TEntity>.Key<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Starts a primary-key snapshot with key ordinal zero.

**typeparam T:** The key component's value type.

**param column:** This table's first non-null primary-key column.

**param value:** The typed value, copied into owned wire storage.

**returns:** An immutable key; append subsequent components with And.

**exception:** The column belongs elsewhere, is not ordinal zero, or the value is invalid.

**exception:** or a non-null value is null.

**Inherited type policy:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `M:NativeWeave.Data.Table`1.TryGetColumn``1(System.String,NativeWeave.Data.ValueCodec{``0},NativeWeave.Data.Column{`0,``0}@)`

```csharp
public bool NativeWeave.Data.Table<TEntity>.TryGetColumn<T>(string name, NativeWeave.Data.ValueCodec<T> codec, [System.Diagnostics.CodeAnalysis.NotNullWhenAttribute(true)] out NativeWeave.Data.Column<TEntity, T>? column)
```

**summary:** Resolves a declared exact store name and codec without inspecting entity members.

**typeparam T:** The requested value type.

**param name:** The exact case-sensitive store name.

**param codec:** The required logical codec, configuration and nullability.

**param column:** The matching token or null.

**returns:** True only for a complete typed and metadata match.

**exception:** is invalid.

**exception:** A required argument is null.

**Inherited type policy:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `M:NativeWeave.Data.WeaveColumnAttribute.#ctor(System.String)`

```csharp
public NativeWeave.Data.WeaveColumnAttribute.WeaveColumnAttribute(string name)
```

**summary:** Declares the exact store column name.

**param name:** A nonempty store identifier.

**exception:** The name is empty or whitespace.

**inheritdoc:**

**Inherited type policy:** Without this attribute the CLR property symbol name is used unchanged. The generated column member keeps its CLR spelling.

## `M:NativeWeave.Data.WeaveIgnoreAttribute.#ctor`

```csharp
public NativeWeave.Data.WeaveIgnoreAttribute.WeaveIgnoreAttribute()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Combining Ignore with another mapping annotation is inconsistent and rejected. Required constructor inputs still need a supported static mapping.

## `M:NativeWeave.Data.WeaveKeyAttribute.#ctor`

```csharp
public NativeWeave.Data.WeaveKeyAttribute.WeaveKeyAttribute()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Nullable keys are rejected at compilation and again by the static descriptor builder; there is no inferred key convention.

## `M:NativeWeave.Data.WeaveTableAttribute.#ctor(System.String)`

```csharp
public NativeWeave.Data.WeaveTableAttribute.WeaveTableAttribute(string name)
```

**summary:** Declares the exact store table name.

**param name:** A nonempty table identifier; casing is preserved.

**exception:** The name is empty or whitespace.

**inheritdoc:**

**Inherited type policy:** The generator reads source symbols and emits the same TableBuilder calls as manual metadata. It never opens a database, loads a native module, runs Cargo or discovers runtime model types.

## `M:NativeWeave.Data.WeaveVersionAttribute.#ctor`

```csharp
public NativeWeave.Data.WeaveVersionAttribute.WeaveVersionAttribute()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Generated metadata sets IsConcurrencyToken. The application supplies expected and changed values; no automatic version increment occurs.

## `P:NativeWeave.Data.Codecs.Boolean`

```csharp
public static NativeWeave.Data.ValueCodec<bool> NativeWeave.Data.Codecs.Boolean { get; }
```

**summary:** Gets the Boolean codec whose only wire bytes are zero and one.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Bytes`

```csharp
public static NativeWeave.Data.ValueCodec<byte[]> NativeWeave.Data.Codecs.Bytes { get; }
```

**summary:** Gets binary values; input and output arrays are copied at a snapshot boundary.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Date`

```csharp
public static NativeWeave.Data.ValueCodec<System.DateOnly> NativeWeave.Data.Codecs.Date { get; }
```

**summary:** Gets signed days since 1970-01-01 within the DateOnly domain.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.DecimalText`

```csharp
public static NativeWeave.Data.ValueCodec<decimal> NativeWeave.Data.Codecs.DecimalText { get; }
```

**summary:** Gets exact decimal text storage; provider arithmetic, range ordering and aggregation are not implied.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Double`

```csharp
public static NativeWeave.Data.ValueCodec<double> NativeWeave.Data.Codecs.Double { get; }
```

**summary:** Gets finite IEEE 754 binary64 values, preserving signed zero in the wire.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Guid`

```csharp
public static NativeWeave.Data.ValueCodec<System.Guid> NativeWeave.Data.Codecs.Guid { get; }
```

**summary:** Gets RFC 4122 network-order UUID encoding.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Int16`

```csharp
public static NativeWeave.Data.ValueCodec<short> NativeWeave.Data.Codecs.Int16 { get; }
```

**summary:** Gets the exact signed 16-bit codec.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Int32`

```csharp
public static NativeWeave.Data.ValueCodec<int> NativeWeave.Data.Codecs.Int32 { get; }
```

**summary:** Gets the exact signed 32-bit codec.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Int64`

```csharp
public static NativeWeave.Data.ValueCodec<long> NativeWeave.Data.Codecs.Int64 { get; }
```

**summary:** Gets the exact signed 64-bit codec.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Single`

```csharp
public static NativeWeave.Data.ValueCodec<float> NativeWeave.Data.Codecs.Single { get; }
```

**summary:** Gets finite IEEE 754 binary32 values, preserving signed zero in the wire.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.String`

```csharp
public static NativeWeave.Data.ValueCodec<string> NativeWeave.Data.Codecs.String { get; }
```

**summary:** Gets strict UTF-8 text with no normalization or implicit SQL collation.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.Time`

```csharp
public static NativeWeave.Data.ValueCodec<System.TimeOnly> NativeWeave.Data.Codecs.Time { get; }
```

**summary:** Gets microseconds since midnight; submicrosecond precision rejects.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.UtcDateTime`

```csharp
public static NativeWeave.Data.ValueCodec<System.DateTime> NativeWeave.Data.Codecs.UtcDateTime { get; }
```

**summary:** Gets UTC-only DateTime values; Local and Unspecified values reject.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.Codecs.UtcInstant`

```csharp
public static NativeWeave.Data.ValueCodec<System.DateTimeOffset> NativeWeave.Data.Codecs.UtcInstant { get; }
```

**summary:** Gets UTC-normalized instants in Unix microseconds; no precision loss is allowed.

**Inherited type policy:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `P:NativeWeave.Data.ColumnOptions.Collation`

```csharp
public string? NativeWeave.Data.ColumnOptions.Collation { get; init; }
```

**summary:** Gets the exact provider collation name, or no explicit collation.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `P:NativeWeave.Data.ColumnOptions.IsConcurrencyToken`

```csharp
public bool NativeWeave.Data.ColumnOptions.IsConcurrencyToken { get; init; }
```

**summary:** Gets whether the column is an explicit optimistic-concurrency token.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `P:NativeWeave.Data.ColumnOptions.IsGenerated`

```csharp
public bool NativeWeave.Data.ColumnOptions.IsGenerated { get; init; }
```

**summary:** Gets whether the database generates the value on insert.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `P:NativeWeave.Data.ColumnOptions.IsPrimaryKey`

```csharp
public bool NativeWeave.Data.ColumnOptions.IsPrimaryKey { get; init; }
```

**summary:** Gets whether the column participates in the primary key, ordered by declaration.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `P:NativeWeave.Data.ColumnOptions.MaxLength`

```csharp
public int? NativeWeave.Data.ColumnOptions.MaxLength { get; init; }
```

**summary:** Gets the positive maximum byte capacity, or no declared capacity.

**Inherited type policy:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `P:NativeWeave.Data.Column`2.Codec`

```csharp
public NativeWeave.Data.ValueCodec<T> NativeWeave.Data.Column<TEntity, T>.Codec { get; }
```

**summary:** Gets the exact logical codec and its configuration.

**Inherited type policy:** Tokens expose no native pointer. Equivalent metadata in another builder does not authorize using its token.

## `P:NativeWeave.Data.Column`2.Id`

```csharp
public uint NativeWeave.Data.Column<TEntity, T>.Id { get; }
```

**summary:** Gets the stable nonzero little-endian SHA-256-derived column ID.

**Inherited type policy:** Tokens expose no native pointer. Equivalent metadata in another builder does not authorize using its token.

## `P:NativeWeave.Data.Column`2.Name`

```csharp
public string NativeWeave.Data.Column<TEntity, T>.Name { get; }
```

**summary:** Gets the exact store name, preserving case and Unicode.

**Inherited type policy:** Tokens expose no native pointer. Equivalent metadata in another builder does not authorize using its token.

## `P:NativeWeave.Data.ConcurrencyConflictException.ActualRows`

```csharp
public long NativeWeave.Data.ConcurrencyConflictException.ActualRows { get; }
```

**summary:** Gets the actual affected-row count.

**Inherited type policy:** The original key and expected token predicate ran once in the database. This exception never authorizes a write replay.

## `P:NativeWeave.Data.ConcurrencyConflictException.ExpectedRows`

```csharp
public long NativeWeave.Data.ConcurrencyConflictException.ExpectedRows { get; }
```

**summary:** Gets the expected affected-row count.

**Inherited type policy:** The original key and expected token predicate ran once in the database. This exception never authorizes a write replay.

## `P:NativeWeave.Data.DatabaseCapabilityException.Capability`

```csharp
public string NativeWeave.Data.DatabaseCapabilityException.Capability { get; }
```

**summary:** Gets the exact required capability name.

**Inherited type policy:** The owned exception retains validated managed identity strings and no native handle. Constructing or reading it performs no provider call; capability admission rejects before business dispatch.

## `P:NativeWeave.Data.DatabaseCapabilityException.Provider`

```csharp
public string NativeWeave.Data.DatabaseCapabilityException.Provider { get; }
```

**summary:** Gets the provider identity.

**Inherited type policy:** The owned exception retains validated managed identity strings and no native handle. Constructing or reading it performs no provider call; capability admission rejects before business dispatch.

## `P:NativeWeave.Data.DatabaseException.CorrelationId`

```csharp
public ulong NativeWeave.Data.DatabaseException.CorrelationId { get; }
```

**summary:** Gets the native correlation identity, or zero when absent.

**Inherited type policy:** Diagnostic values are immutable and remain readable after cleanup. Construction loads no native engine. A transient cause is not permission to retry a write; outcome and application idempotency remain separate.

## `P:NativeWeave.Data.DatabaseException.IsTransient`

```csharp
public bool NativeWeave.Data.DatabaseException.IsTransient { get; }
```

**summary:** Gets the provider's explicit classification; unknown outcomes are always nontransient.

**Inherited type policy:** Diagnostic values are immutable and remain readable after cleanup. Construction loads no native engine. A transient cause is not permission to retry a write; outcome and application idempotency remain separate.

## `P:NativeWeave.Data.DatabaseException.Kind`

```csharp
public NativeWeave.Data.DatabaseErrorKind NativeWeave.Data.DatabaseException.Kind { get; }
```

**summary:** Gets the immutable provider-neutral category.

**Inherited type policy:** Diagnostic values are immutable and remain readable after cleanup. Construction loads no native engine. A transient cause is not permission to retry a write; outcome and application idempotency remain separate.

## `P:NativeWeave.Data.DatabaseException.ProviderCode`

```csharp
public string? NativeWeave.Data.DatabaseException.ProviderCode { get; }
```

**summary:** Gets the optional provider code without interpreting it as retry authorization.

**Inherited type policy:** Diagnostic values are immutable and remain readable after cleanup. Construction loads no native engine. A transient cause is not permission to retry a write; outcome and application idempotency remain separate.

## `P:NativeWeave.Data.Projection`1.ShapeHash`

```csharp
public string NativeWeave.Data.Projection<T>.ShapeHash { get; }
```

**summary:** Gets lowercase SHA-256 of the exact logical shape, excluding managed delegate and native IDs.

**Inherited type policy:** Creation copies the field sequence and hashes canonical metadata. Materializers stay managed; no CLR delegate or function pointer is encoded in metadata. Instances are shareable if their delegates are.

## `P:NativeWeave.Data.ResultColumn`1.Name`

```csharp
public string NativeWeave.Data.ResultColumn<T>.Name { get; }
```

**summary:** Gets the exact result alias; the default token rejects.

**exception:** This token is default.

**Inherited type policy:** The default token is invalid; no public constructor can forge projection ownership.

## `P:NativeWeave.Data.ResultColumn`1.Ordinal`

```csharp
public int NativeWeave.Data.ResultColumn<T>.Ordinal { get; }
```

**summary:** Gets the zero-based ordinal; the default token rejects.

**exception:** This token is default.

**Inherited type policy:** The default token is invalid; no public constructor can forge projection ownership.

## `P:NativeWeave.Data.ResultField.CodecId`

```csharp
public uint NativeWeave.Data.ResultField.CodecId { get; }
```

**summary:** Gets the logical codec ID, independent of source-bound configured IDs.

**Inherited type policy:** Creating a field allocates one managed metadata object with no native resource. It can be retained in a static projection; source-specific codec binding occurs separately at registration.

## `P:NativeWeave.Data.ResultField.IsNullable`

```csharp
public bool NativeWeave.Data.ResultField.IsNullable { get; }
```

**summary:** Gets whether the typed codec permits SQL NULL.

**Inherited type policy:** Creating a field allocates one managed metadata object with no native resource. It can be retained in a static projection; source-specific codec binding occurs separately at registration.

## `P:NativeWeave.Data.ResultField.Name`

```csharp
public string NativeWeave.Data.ResultField.Name { get; }
```

**summary:** Gets the exact result alias.

**Inherited type policy:** Creating a field allocates one managed metadata object with no native resource. It can be retained in a static projection; source-specific codec binding occurs separately at registration.

## `P:NativeWeave.Data.Table`1.MetadataHash`

```csharp
public string NativeWeave.Data.Table<TEntity>.MetadataHash { get; }
```

**summary:** Gets lowercase hexadecimal SHA-256 of the canonical model bytes.

**Inherited type policy:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `P:NativeWeave.Data.Table`1.Name`

```csharp
public string NativeWeave.Data.Table<TEntity>.Name { get; }
```

**summary:** Gets the exact table name.

**Inherited type policy:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `P:NativeWeave.Data.Table`1.Row`

```csharp
public NativeWeave.Data.Projection<TEntity> NativeWeave.Data.Table<TEntity>.Row { get; }
```

**summary:** Gets the immutable projection in declared constructor order.

**Inherited type policy:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `P:NativeWeave.Data.Table`1.Schema`

```csharp
public string? NativeWeave.Data.Table<TEntity>.Schema { get; }
```

**summary:** Gets the explicit schema or null.

**Inherited type policy:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `P:NativeWeave.Data.ValueCodec`1.Id`

```csharp
public uint NativeWeave.Data.ValueCodec<T>.Id { get; }
```

**summary:** Gets the logical db-wire scalar ID, independent of source-bound configured IDs.

**Inherited type policy:** Instances are immutable and shareable. IDs are logical metadata, not source-owned native handles. Nullable wrappers preserve the logical ID. Configured decimal identities include precision and scale. No native runtime is loaded; provider conversions and capability enforcement belong to B07.

## `P:NativeWeave.Data.ValueCodec`1.Name`

```csharp
public string NativeWeave.Data.ValueCodec<T>.Name { get; }
```

**summary:** Gets the descriptive scalar codec name.

**Inherited type policy:** Instances are immutable and shareable. IDs are logical metadata, not source-owned native handles. Nullable wrappers preserve the logical ID. Configured decimal identities include precision and scale. No native runtime is loaded; provider conversions and capability enforcement belong to B07.

## `P:NativeWeave.Data.WeaveColumnAttribute.Generated`

```csharp
public bool NativeWeave.Data.WeaveColumnAttribute.Generated { get; init; }
```

**summary:** Gets or initializes whether the database supplies the value on insertion.

**inheritdoc:**

**Inherited type policy:** Without this attribute the CLR property symbol name is used unchanged. The generated column member keeps its CLR spelling.

## `P:NativeWeave.Data.WeaveTableAttribute.DescriptorName`

```csharp
public string? NativeWeave.Data.WeaveTableAttribute.DescriptorName { get; init; }
```

**summary:** Gets or initializes the generated static descriptor class name; default is EntityNameMapping.

**inheritdoc:**

**Inherited type policy:** The generator reads source symbols and emits the same TableBuilder calls as manual metadata. It never opens a database, loads a native module, runs Cargo or discovers runtime model types.

## `P:NativeWeave.Data.WeaveTableAttribute.Schema`

```csharp
public string? NativeWeave.Data.WeaveTableAttribute.Schema { get; init; }
```

**summary:** Gets or initializes the optional exact schema name.

**inheritdoc:**

**Inherited type policy:** The generator reads source symbols and emits the same TableBuilder calls as manual metadata. It never opens a database, loads a native module, runs Cargo or discovers runtime model types.

## `T:NativeWeave.Data.Changes`1`

```csharp
public sealed class NativeWeave.Data.Changes<TEntity> where TEntity : class
```

**summary:** A single-writer explicit changeset containing owned value snapshots.

**typeparam TEntity:** The application entity class.

**remarks:** This is assignment data, not a SQL AST. Unset removes an assignment; Set with a nullable value assigns SQL NULL. Native execution snapshots the current changes independently and rejects an empty set.

## `T:NativeWeave.Data.Codecs`

```csharp
public static class NativeWeave.Data.Codecs
```

**summary:** Factories for the fixed db-wire/1 logical scalar registry.

**remarks:** Selections are immutable. Encoding snapshots strings, byte arrays and JSON into owned storage. No provider, native loader, reflection serializer or SQL semantics are installed by these factories.

## `T:NativeWeave.Data.ColumnOptions`

```csharp
public sealed record class NativeWeave.Data.ColumnOptions : System.IEquatable<NativeWeave.Data.ColumnOptions>
```

**summary:** Immutable declaration flags for one table column.

**remarks:** Null optional settings remain distinct from defaults. MaxLength is a positive byte capacity. The builder snapshots this record and validates key nullability before publishing a table.

## `T:NativeWeave.Data.Column`2`

```csharp
public sealed class NativeWeave.Data.Column<TEntity, T> where TEntity : class
```

**summary:** An immutable entity- and value-typed column token belonging to one table declaration.

**typeparam TEntity:** The application entity class.

**typeparam T:** The exact value type selected by the codec.

**remarks:** Tokens expose no native pointer. Equivalent metadata in another builder does not authorize using its token.

## `T:NativeWeave.Data.ConcurrencyCheck`1`

```csharp
public sealed class NativeWeave.Data.ConcurrencyCheck<TEntity> where TEntity : class
```

**summary:** A single-writer explicit set of expected concurrency-token values.

**typeparam TEntity:** The application entity class.

**remarks:** Values are copied immediately. There is no identity map, implicit version increment or managed compare-and-swap.

## `T:NativeWeave.Data.ConcurrencyConflictException`

```csharp
public sealed class NativeWeave.Data.ConcurrencyConflictException : NativeWeave.Data.DatabaseException
```

**summary:** A native optimistic write did not match its exact expected affected-row count.

**remarks:** The original key and expected token predicate ran once in the database. This exception never authorizes a write replay.

## `T:NativeWeave.Data.DatabaseCapabilityException`

```csharp
public sealed class NativeWeave.Data.DatabaseCapabilityException : NativeWeave.Data.DatabaseException
```

**summary:** Identifies a required capability missing from an engine or provider profile.

**remarks:** The owned exception retains validated managed identity strings and no native handle. Constructing or reading it performs no provider call; capability admission rejects before business dispatch.

## `T:NativeWeave.Data.DatabaseErrorKind`

```csharp
public enum NativeWeave.Data.DatabaseErrorKind : int
```

**summary:** Provider-neutral database failure categories; cancellation and timeouts use their standard CLR exceptions.

## `T:NativeWeave.Data.DatabaseException`

```csharp
public class NativeWeave.Data.DatabaseException : System.Exception
```

**summary:** Preserves a bounded provider-neutral failure and correlation identity.

**remarks:** Diagnostic values are immutable and remain readable after cleanup. Construction loads no native engine. A transient cause is not permission to retry a write; outcome and application idempotency remain separate.

## `T:NativeWeave.Data.EntityKey`1`

```csharp
public sealed class NativeWeave.Data.EntityKey<TEntity> where TEntity : class
```

**summary:** An immutable ordered snapshot of a table's non-null primary-key values.

**typeparam TEntity:** The application entity class.

**remarks:** Incomplete prefixes are construction values only; registration or execution requires the complete key.

## `T:NativeWeave.Data.EntityWriter`1`

```csharp
public delegate void NativeWeave.Data.EntityWriter<T>(NativeWeave.Data.RowWriter row, T value)
```

**summary:** Synchronously extracts typed entity values before native dispatch.

**typeparam T:** The application entity type.

**param row:** A stack-only writer valid only for this snapshot.

**param value:** The application entity.

**remarks:** The callback runs synchronously during a finite input snapshot. Typed writes copy encoded values into owned buffers before native dispatch; the stack-only writer must not be retained.

## `T:NativeWeave.Data.Projection`1`

```csharp
public sealed class NativeWeave.Data.Projection<T>
```

**summary:** An immutable ordered static row shape and direct materializer.

**typeparam T:** The owned result type; value types and reference types are supported.

**remarks:** Creation copies the field sequence and hashes canonical metadata. Materializers stay managed; no CLR delegate or function pointer is encoded in metadata. Instances are shareable if their delegates are.

## `T:NativeWeave.Data.Relation`2`

```csharp
public sealed class NativeWeave.Data.Relation<TParent, TChild> where TParent : class where TChild : class
```

**summary:** Immutable ordered primary-key/foreign-key metadata over two already-built tables.

**typeparam TParent:** The parent entity class.

**typeparam TChild:** The child entity class.

**remarks:** Creation loads no native engine. And methods return new descriptors and never alter either table hash. A complete key prefix is required for native registration; lazy loading and alternate-key inference are excluded.

## `T:NativeWeave.Data.ResultColumn`1`

```csharp
public readonly struct NativeWeave.Data.ResultColumn<T>
```

**summary:** An opaque result-column token created by the owning query projection.

**typeparam T:** The exact result type.

**remarks:** The default token is invalid; no public constructor can forge projection ownership.

## `T:NativeWeave.Data.ResultField`

```csharp
public sealed class NativeWeave.Data.ResultField
```

**summary:** An immutable exact result alias, logical codec configuration and SQL nullability.

**remarks:** Creating a field allocates one managed metadata object with no native resource. It can be retained in a static projection; source-specific codec binding occurs separately at registration.

## `T:NativeWeave.Data.RowMaterializer`1`

```csharp
public delegate T NativeWeave.Data.RowMaterializer<T>(NativeWeave.Data.RowReader row)
```

**summary:** Synchronously materializes one validated row into an owned CLR value.

**typeparam T:** The result value or entity type.

**param row:** A borrowed stack-only reader valid only for the call.

**returns:** The owned result; no row borrow may escape.

**remarks:** The callback runs synchronously while its batch lease is live. Decoding and the application constructor create owned CLR values; borrowed reader state must not escape or cross an await.

## `T:NativeWeave.Data.RowReader`

```csharp
public readonly ref struct NativeWeave.Data.RowReader
```

**summary:** A stack-only reader over a validated live row lease.

**remarks:** Shape validation precedes NULL interpretation. Every read checks the lease; default readers reject. Values are owned CLR copies. Readers cannot be retained across await or stored in an ordinary heap object.

## `T:NativeWeave.Data.RowWriter`

```csharp
public readonly ref struct NativeWeave.Data.RowWriter
```

**summary:** A stack-only writer that snapshots typed entity fields without invoking native code.

**remarks:** A writer is valid only during EntityWriter invocation. Repeated assignment rejects. Insert policy omits generated columns. An exception publishes no partial row to a provider.

## `T:NativeWeave.Data.SqlCommand`

```csharp
public sealed class NativeWeave.Data.SqlCommand
```

**summary:** An immutable, shareable trusted SQL template and owned typed parameter snapshot.

**remarks:** This type does not parse SQL, choose dialects, prove safety or contact a provider. Rust transports placeholders and validates actual capability/effect policy before dispatch. Interpolated convenience has boxing costs.

## `T:NativeWeave.Data.SqlCommandKind`

```csharp
public enum NativeWeave.Data.SqlCommandKind : int
```

**summary:** The explicit trusted command effect classification.

## `T:NativeWeave.Data.SqlParameters`

```csharp
public sealed class NativeWeave.Data.SqlParameters
```

**summary:** A single-writer ordered collection of typed owned parameter snapshots.

**remarks:** Names are case-sensitive ASCII without @. Add copies mutable values immediately; command construction snapshots the collection. Provider placeholder scanning and missing/unused-hole checks remain native B02/B03 work.

## `T:NativeWeave.Data.TableBuilder`1`

```csharp
public sealed class NativeWeave.Data.TableBuilder<TEntity> where TEntity : class
```

**summary:** Constructs one immutable table declaration using explicit AOT-visible delegates.

**typeparam TEntity:** The application entity class.

**remarks:** This single-writer startup builder is consumed by successful Build. It performs O(column count) managed work and loads no native engine. The known closed type is used only for its assembly/name identity.

## `T:NativeWeave.Data.Table`1`

```csharp
public sealed class NativeWeave.Data.Table<TEntity> where TEntity : class
```

**summary:** An immutable, shareable table declaration; first native registration belongs to the source owner.

**typeparam TEntity:** The application entity class.

**remarks:** Canonical metadata hashes are business schema identities, independent of ABI and package versions.

## `T:NativeWeave.Data.ValueCodec`1`

```csharp
public sealed class NativeWeave.Data.ValueCodec<T>
```

**summary:** A closed typed selection of one precompiled logical scalar codec.

**typeparam T:** The statically known CLR value type.

**remarks:** Instances are immutable and shareable. IDs are logical metadata, not source-owned native handles. Nullable wrappers preserve the logical ID. Configured decimal identities include precision and scale. No native runtime is loaded; provider conversions and capability enforcement belong to B07.

## `T:NativeWeave.Data.WeaveColumnAttribute`

```csharp
[System.AttributeUsageAttribute(System.AttributeTargets.Property, Inherited = false)]
public sealed class NativeWeave.Data.WeaveColumnAttribute : System.Attribute
```

**summary:** Overrides a property's exact store name and generated-value policy.

**remarks:** Without this attribute the CLR property symbol name is used unchanged. The generated column member keeps its CLR spelling.

## `T:NativeWeave.Data.WeaveIgnoreAttribute`

```csharp
[System.AttributeUsageAttribute(System.AttributeTargets.Property, Inherited = false)]
public sealed class NativeWeave.Data.WeaveIgnoreAttribute : System.Attribute
```

**summary:** Excludes a property from generated metadata and row serialization.

**remarks:** Combining Ignore with another mapping annotation is inconsistent and rejected. Required constructor inputs still need a supported static mapping.

## `T:NativeWeave.Data.WeaveKeyAttribute`

```csharp
[System.AttributeUsageAttribute(System.AttributeTargets.Property, Inherited = false)]
public sealed class NativeWeave.Data.WeaveKeyAttribute : System.Attribute
```

**summary:** Marks a non-null primary-key property in deterministic projection order.

**remarks:** Nullable keys are rejected at compilation and again by the static descriptor builder; there is no inferred key convention.

## `T:NativeWeave.Data.WeaveTableAttribute`

```csharp
[System.AttributeUsageAttribute(System.AttributeTargets.Class, Inherited = false)]
public sealed class NativeWeave.Data.WeaveTableAttribute : System.Attribute
```

**summary:** Opts a model into deterministic, static table and DTO mapping generation.

**remarks:** The generator reads source symbols and emits the same TableBuilder calls as manual metadata. It never opens a database, loads a native module, runs Cargo or discovers runtime model types.

## `T:NativeWeave.Data.WeaveVersionAttribute`

```csharp
[System.AttributeUsageAttribute(System.AttributeTargets.Property, Inherited = false)]
public sealed class NativeWeave.Data.WeaveVersionAttribute : System.Attribute
```

**summary:** Marks an explicit optimistic-concurrency token.

**remarks:** Generated metadata sets IsConcurrencyToken. The application supplies expected and changed values; no automatic version increment occurs.
