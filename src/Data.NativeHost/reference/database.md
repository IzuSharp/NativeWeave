# NativeWeave.Database compiled API

Generated from the compiled product assembly and XML by `src/Build.Integration/ApiReference`.

Current product declarations compared with Design commit c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9. Ownership, costs and Linux applicability are described in docs/guides/data-nativehost.md.

## `F:NativeWeave.Database.BulkAtomicity.All`

```csharp
NativeWeave.Database.BulkAtomicity.All = 0
```

**summary:** Owns a transaction, or an internal savepoint inside the caller's transaction.

## `F:NativeWeave.Database.BulkAtomicity.PerBatch`

```csharp
NativeWeave.Database.BulkAtomicity.PerBatch = 1
```

**summary:** Commits each complete batch independently; rejected inside a caller transaction.

## `F:NativeWeave.Database.DatabaseProvider.PostgreSql`

```csharp
NativeWeave.Database.DatabaseProvider.PostgreSql = 0
```

**summary:** The SQLx PostgreSQL provider.

## `F:NativeWeave.Database.DatabaseProvider.Sqlite`

```csharp
NativeWeave.Database.DatabaseProvider.Sqlite = 1
```

**summary:** The serialized SQLx SQLite provider.

## `F:NativeWeave.Database.MigrationTransactionMode.NonTransactional`

```csharp
NativeWeave.Database.MigrationTransactionMode.NonTransactional = 1
```

**summary:** Requires PostgreSQL and an explicit opt-in; partial effects can remain after failure.

## `F:NativeWeave.Database.MigrationTransactionMode.Transactional`

```csharp
NativeWeave.Database.MigrationTransactionMode.Transactional = 0
```

**summary:** Commits the script and its ledger atomically; SQLite also wraps the entire selected batch.

## `F:NativeWeave.Query.FrameBoundary.CurrentRow`

```csharp
NativeWeave.Query.FrameBoundary.CurrentRow = 1
```

**summary:** Uses the native CurrentRow policy.

**inheritdoc:**

**Inherited type policy:** Only these ROWS endpoints are supported. Reversed or unsupported bounds fail before native state publication; finite numeric PRECEDING/FOLLOWING frames are not declared.

## `F:NativeWeave.Query.FrameBoundary.UnboundedFollowing`

```csharp
NativeWeave.Query.FrameBoundary.UnboundedFollowing = 2
```

**summary:** Uses the native UnboundedFollowing policy.

**inheritdoc:**

**Inherited type policy:** Only these ROWS endpoints are supported. Reversed or unsupported bounds fail before native state publication; finite numeric PRECEDING/FOLLOWING frames are not declared.

## `F:NativeWeave.Query.FrameBoundary.UnboundedPreceding`

```csharp
NativeWeave.Query.FrameBoundary.UnboundedPreceding = 0
```

**summary:** Uses the native UnboundedPreceding policy.

**inheritdoc:**

**Inherited type policy:** Only these ROWS endpoints are supported. Reversed or unsupported bounds fail before native state publication; finite numeric PRECEDING/FOLLOWING frames are not declared.

## `F:NativeWeave.Query.LockWait.NoWait`

```csharp
NativeWeave.Query.LockWait.NoWait = 1
```

**summary:** Uses the native NoWait policy.

**inheritdoc:**

**Inherited type policy:** Controls PostgreSQL row-lock conflicts within the same transaction and total query deadline; it does not enable transparent retries.

## `F:NativeWeave.Query.LockWait.SkipLocked`

```csharp
NativeWeave.Query.LockWait.SkipLocked = 2
```

**summary:** Uses the native SkipLocked policy.

**inheritdoc:**

**Inherited type policy:** Controls PostgreSQL row-lock conflicts within the same transaction and total query deadline; it does not enable transparent retries.

## `F:NativeWeave.Query.LockWait.Wait`

```csharp
NativeWeave.Query.LockWait.Wait = 0
```

**summary:** Uses the native Wait policy.

**inheritdoc:**

**Inherited type policy:** Controls PostgreSQL row-lock conflicts within the same transaction and total query deadline; it does not enable transparent retries.

## `F:NativeWeave.Query.NullOrder.First`

```csharp
NativeWeave.Query.NullOrder.First = 0
```

**summary:** Uses the native First policy.

**inheritdoc:**

**Inherited type policy:** Both providers render explicit SQL NULL placement. Ordering alone supplies no uniqueness or snapshot guarantee.

## `F:NativeWeave.Query.NullOrder.Last`

```csharp
NativeWeave.Query.NullOrder.Last = 1
```

**summary:** Uses the native Last policy.

**inheritdoc:**

**Inherited type policy:** Both providers render explicit SQL NULL placement. Ordering alone supplies no uniqueness or snapshot guarantee.

## `F:NativeWeave.Query.RowLockMode.KeyShare`

```csharp
NativeWeave.Query.RowLockMode.KeyShare = 3
```

**summary:** Uses the native KeyShare policy.

**inheritdoc:**

**Inherited type policy:** Available only on PostgreSQL with an explicit live transaction. SQLite rejects the operation before provider dispatch.

## `F:NativeWeave.Query.RowLockMode.NoKeyUpdate`

```csharp
NativeWeave.Query.RowLockMode.NoKeyUpdate = 2
```

**summary:** Uses the native NoKeyUpdate policy.

**inheritdoc:**

**Inherited type policy:** Available only on PostgreSQL with an explicit live transaction. SQLite rejects the operation before provider dispatch.

## `F:NativeWeave.Query.RowLockMode.Share`

```csharp
NativeWeave.Query.RowLockMode.Share = 1
```

**summary:** Uses the native Share policy.

**inheritdoc:**

**Inherited type policy:** Available only on PostgreSQL with an explicit live transaction. SQLite rejects the operation before provider dispatch.

## `F:NativeWeave.Query.RowLockMode.Update`

```csharp
NativeWeave.Query.RowLockMode.Update = 0
```

**summary:** Uses the native Update policy.

**inheritdoc:**

**Inherited type policy:** Available only on PostgreSQL with an explicit live transaction. SQLite rejects the operation before provider dispatch.

## `F:NativeWeave.Query.SetOperation.Except`

```csharp
NativeWeave.Query.SetOperation.Except = 3
```

**summary:** Uses the native Except policy.

**inheritdoc:**

**Inherited type policy:** Operands must have the same source, field order, aliases, codecs and nullability. Rust snapshots the right operand; SQL duplicate and NULL semantics apply.

## `F:NativeWeave.Query.SetOperation.Intersect`

```csharp
NativeWeave.Query.SetOperation.Intersect = 2
```

**summary:** Uses the native Intersect policy.

**inheritdoc:**

**Inherited type policy:** Operands must have the same source, field order, aliases, codecs and nullability. Rust snapshots the right operand; SQL duplicate and NULL semantics apply.

## `F:NativeWeave.Query.SetOperation.Union`

```csharp
NativeWeave.Query.SetOperation.Union = 0
```

**summary:** Uses the native Union policy.

**inheritdoc:**

**Inherited type policy:** Operands must have the same source, field order, aliases, codecs and nullability. Rust snapshots the right operand; SQL duplicate and NULL semantics apply.

## `F:NativeWeave.Query.SetOperation.UnionAll`

```csharp
NativeWeave.Query.SetOperation.UnionAll = 1
```

**summary:** Uses the native UnionAll policy.

**inheritdoc:**

**Inherited type policy:** Operands must have the same source, field order, aliases, codecs and nullability. Rust snapshots the right operand; SQL duplicate and NULL semantics apply.

## `F:NativeWeave.Query.SortDirection.Ascending`

```csharp
NativeWeave.Query.SortDirection.Ascending = 0
```

**summary:** Uses the native Ascending policy.

**inheritdoc:**

**Inherited type policy:** The native query validates each enum value before mutation. Direction is explicit; it does not change SQL NULL ordering.

## `F:NativeWeave.Query.SortDirection.Descending`

```csharp
NativeWeave.Query.SortDirection.Descending = 1
```

**summary:** Uses the native Descending policy.

**inheritdoc:**

**Inherited type policy:** The native query validates each enum value before mutation. Direction is explicit; it does not change SQL NULL ordering.

## `M:NativeWeave.Database.BulkAtomicity.#ctor`

```csharp
public NativeWeave.Database.BulkAtomicity.BulkAtomicity()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.BulkFailure.TryGetProgress(System.Exception,NativeWeave.Database.BulkProgress@)`

```csharp
public static bool NativeWeave.Database.BulkFailure.TryGetProgress(System.Exception exception, [System.Diagnostics.CodeAnalysis.NotNullWhenAttribute(true)] out NativeWeave.Database.BulkProgress? progress)
```

**summary:** Reads only the exact bulk-progress entry on the supplied exception.

**param exception:** The original exception to inspect; inner exceptions are not traversed.

**param progress:** The immutable progress when present, otherwise null.

**returns:** True only when this exact exception carries a valid bulk-progress record.

**exception:** is null.

**Inherited type policy:** The helper reads one exact typed Exception.Data entry without native calls, allocation of a wrapper, recursive error traversal or inference from cancellation. The returned snapshot can outlive all native owners.

## `M:NativeWeave.Database.BulkOptions.#ctor`

```csharp
public NativeWeave.Database.BulkOptions.BulkOptions()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.Equals(NativeWeave.Database.BulkOptions)`

```csharp
public bool NativeWeave.Database.BulkOptions.Equals(NativeWeave.Database.BulkOptions? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.BulkOptions.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.GetHashCode`

```csharp
public override int NativeWeave.Database.BulkOptions.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.ToString`

```csharp
public override string NativeWeave.Database.BulkOptions.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.op_Equality(NativeWeave.Database.BulkOptions,NativeWeave.Database.BulkOptions)`

```csharp
public static bool NativeWeave.Database.BulkOptions.operator ==(NativeWeave.Database.BulkOptions? left, NativeWeave.Database.BulkOptions? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.op_Inequality(NativeWeave.Database.BulkOptions,NativeWeave.Database.BulkOptions)`

```csharp
public static bool NativeWeave.Database.BulkOptions.operator !=(NativeWeave.Database.BulkOptions? left, NativeWeave.Database.BulkOptions? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkOptions.{Clone}$`

```csharp
public NativeWeave.Database.BulkOptions NativeWeave.Database.BulkOptions.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `M:NativeWeave.Database.BulkProgress.#ctor(System.Int64,System.Int32,System.Boolean,NativeWeave.Database.TransactionOutcome)`

```csharp
public NativeWeave.Database.BulkProgress.BulkProgress(long RowsAffectedInCompletedBatches, int CompletedBatches, bool CompletedBatchesCommitted, NativeWeave.Database.TransactionOutcome CurrentTransactionOutcome)
```

**summary:** Immutable progress at failure, distinct from uncertain current-batch effects or later rollback.

**param RowsAffectedInCompletedBatches:** Affected rows only in fully acknowledged preceding batches.

**param CompletedBatches:** The fully acknowledged batch count.

**param CompletedBatchesCommitted:** True only for confirmed preceding PerBatch commits.

**param CurrentTransactionOutcome:** Actual transaction knowledge, retaining Unknown independently.

**remarks:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.Deconstruct(System.Int64@,System.Int32@,System.Boolean@,NativeWeave.Database.TransactionOutcome@)`

```csharp
public void NativeWeave.Database.BulkProgress.Deconstruct(out long RowsAffectedInCompletedBatches, out int CompletedBatches, out bool CompletedBatchesCommitted, out NativeWeave.Database.TransactionOutcome CurrentTransactionOutcome)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.Equals(NativeWeave.Database.BulkProgress)`

```csharp
public bool NativeWeave.Database.BulkProgress.Equals(NativeWeave.Database.BulkProgress? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.BulkProgress.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.GetHashCode`

```csharp
public override int NativeWeave.Database.BulkProgress.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.ToString`

```csharp
public override string NativeWeave.Database.BulkProgress.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.op_Equality(NativeWeave.Database.BulkProgress,NativeWeave.Database.BulkProgress)`

```csharp
public static bool NativeWeave.Database.BulkProgress.operator ==(NativeWeave.Database.BulkProgress? left, NativeWeave.Database.BulkProgress? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.op_Inequality(NativeWeave.Database.BulkProgress,NativeWeave.Database.BulkProgress)`

```csharp
public static bool NativeWeave.Database.BulkProgress.operator !=(NativeWeave.Database.BulkProgress? left, NativeWeave.Database.BulkProgress? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkProgress.{Clone}$`

```csharp
public NativeWeave.Database.BulkProgress NativeWeave.Database.BulkProgress.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `M:NativeWeave.Database.BulkResult.#ctor(System.Int64,System.Int32,System.Boolean)`

```csharp
public NativeWeave.Database.BulkResult.BulkResult(long RowsAffected, int Batches, bool CommittedByOperation)
```

**summary:** The acknowledged result of all admitted batches.

**param RowsAffected:** The sum of acknowledged provider counts.

**param Batches:** The number of fully acknowledged batches.

**param CommittedByOperation:** True only when this operation confirmed its own commit or commits.

**remarks:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.Deconstruct(System.Int64@,System.Int32@,System.Boolean@)`

```csharp
public void NativeWeave.Database.BulkResult.Deconstruct(out long RowsAffected, out int Batches, out bool CommittedByOperation)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.Equals(NativeWeave.Database.BulkResult)`

```csharp
public bool NativeWeave.Database.BulkResult.Equals(NativeWeave.Database.BulkResult? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.BulkResult.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.GetHashCode`

```csharp
public override int NativeWeave.Database.BulkResult.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.ToString`

```csharp
public override string NativeWeave.Database.BulkResult.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.op_Equality(NativeWeave.Database.BulkResult,NativeWeave.Database.BulkResult)`

```csharp
public static bool NativeWeave.Database.BulkResult.operator ==(NativeWeave.Database.BulkResult? left, NativeWeave.Database.BulkResult? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.op_Inequality(NativeWeave.Database.BulkResult,NativeWeave.Database.BulkResult)`

```csharp
public static bool NativeWeave.Database.BulkResult.operator !=(NativeWeave.Database.BulkResult? left, NativeWeave.Database.BulkResult? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.BulkResult.{Clone}$`

```csharp
public NativeWeave.Database.BulkResult NativeWeave.Database.BulkResult.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `M:NativeWeave.Database.ConflictTarget`1.#ctor(System.String)`

```csharp
public NativeWeave.Database.ConflictTarget<TEntity>.ConflictTarget(string constraintName)
```

**summary:** Creates an explicit named PostgreSQL constraint target.

**param constraintName:** A nonempty exact store constraint name.

**exception:** is null.

**exception:** The name is empty, invalid or exceeds its finite UTF8 capacity.

**Inherited type policy:** Construction performs no schema query. The native database checks that the selected unique constraint exists.

## `M:NativeWeave.Database.ConflictTarget`1.And``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Database.ConflictTarget<TEntity> NativeWeave.Database.ConflictTarget<TEntity>.And<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Returns a new target with an additional unique column in the stated order.

**typeparam T:** The column's exact value type.

**param column:** A new column of the same built table.

**returns:** A new immutable target; this instance is unchanged.

**exception:** is null.

**exception:** The target is named, or the column is foreign, repeated or unbuilt.

**Inherited type policy:** Construction performs no schema query. The native database checks that the selected unique constraint exists.

## `M:NativeWeave.Database.ConflictTarget`1.Columns``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public static NativeWeave.Database.ConflictTarget<TEntity> NativeWeave.Database.ConflictTarget<TEntity>.Columns<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Starts an immutable portable conflict target at one built table column.

**typeparam T:** The column's exact value type.

**param column:** A column from the target table.

**returns:** A new one-column target.

**exception:** is null.

**exception:** The table has not been built.

**Inherited type policy:** Construction performs no schema query. The native database checks that the selected unique constraint exists.

## `M:NativeWeave.Database.DataSession.BeginTransactionAsync(NativeWeave.Database.TransactionOptions,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.DataTransaction> NativeWeave.Database.DataSession.BeginTransactionAsync(NativeWeave.Database.TransactionOptions options, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Begins an exact native transaction without weakening unsupported isolation or read-only policy.

**param options:** Immutable isolation, effect and independent commit/cleanup deadline settings.

**param cancellationToken:** Controls admission before BEGIN dispatch.

**returns:** The transaction owner, whose outcome is independent from local cleanup.

**exception:** is null.

**exception:** An option is invalid.

**exception:** The provider or admission fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.BeginTransactionAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.DataTransaction> NativeWeave.Database.DataSession.BeginTransactionAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Begins a native transaction using the provider's default isolation.

**param cancellationToken:** Controls admission before BEGIN dispatch.

**returns:** The native transaction owner.

**exception:** Admission is closed.

**exception:** The provider or single-command admission rejects BEGIN.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.CloseAsync(System.TimeSpan,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.DatabaseCloseResult> NativeWeave.Database.DataSession.CloseAsync(System.TimeSpan waitBudget, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Starts closure, then waits within an independent finite caller budget.

**param waitBudget:** A nonnegative finite wait; zero observes without waiting.

**param cancellationToken:** Cancels only the wait after native cleanup starts.

**returns:** A truthful snapshot; timeout cannot imply native retirement.

**exception:** The budget is invalid.

**exception:** The caller stops waiting.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.DeleteAsync``1(NativeWeave.Data.Table{``0},NativeWeave.Data.EntityKey{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.DeleteAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, NativeWeave.Data.EntityKey<TEntity> key, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Deletes by the entire native primary-key predicate with no read-before-write query.

**typeparam TEntity:** The statically described entity class.

**param table:** The exact table.

**param key:** The complete ordered primary key.

**param cancellationToken:** Requests cancellation under the existing transaction policy.

**returns:** Zero or one affected row; multiple matches are a schema constraint failure.

**exception:** The key is invalid.

**exception:** Provider, constraint or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.DeleteCheckedAsync``1(NativeWeave.Data.Table{``0},NativeWeave.Data.EntityKey{``0},NativeWeave.Data.ConcurrencyCheck{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.DeleteCheckedAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, NativeWeave.Data.EntityKey<TEntity> key, NativeWeave.Data.ConcurrencyCheck<TEntity> concurrency, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Deletes once using the complete key and every explicit expected concurrency token.

**typeparam TEntity:** The statically described entity class.

**param table:** The exact table.

**param key:** The complete ordered primary key.

**param concurrency:** The complete expected-token snapshot.

**param cancellationToken:** Requests cancellation and waits for native retirement.

**returns:** Exactly one acknowledged affected row.

**exception:** No row matched the key and expected tokens.

**exception:** Provider, schema or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.Dispose`

```csharp
public void NativeWeave.Database.DataSession.Dispose()
```

**summary:** Closes admission and transfers cleanup to the bounded native owner without blocking.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.DisposeAsync`

```csharp
public System.Threading.Tasks.ValueTask NativeWeave.Database.DataSession.DisposeAsync()
```

**summary:** Closes admission and joins actual native local safety.

**returns:** The asynchronous safety join.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.ExecuteAsync(NativeWeave.Data.SqlCommand,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.ExecuteAsync(NativeWeave.Data.SqlCommand command, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Executes one trusted mutation or explicit session-changing command and observes its affected-row count.

**param command:** An immutable typed command with a nonquery effect classification.

**param cancellationToken:** Requests cancellation; accepted work retains resources until native retirement.

**returns:** The exact affected-row count.

**exception:** The command kind is incompatible.

**exception:** is null.

**exception:** Session or source admission is closed.

**exception:** The provider, capacity or concurrent-use policy rejects execution.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.FindAsync``1(NativeWeave.Data.Table{``0},NativeWeave.Data.EntityKey{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<TEntity?> NativeWeave.Database.DataSession.FindAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, NativeWeave.Data.EntityKey<TEntity> key, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Executes one native complete-key SELECT and returns the sole row or null.

**typeparam TEntity:** The statically mapped entity class.

**param table:** The exact immutable table descriptor.

**param key:** Every declared key component, including any tenant key.

**param cancellationToken:** Requests cancellation and joins native retirement.

**returns:** The owned row or null; duplicate key-shaped results throw.

**exception:** The key is incomplete or belongs to another table.

**exception:** The declared key matched multiple rows.

**exception:** Shape, codec, provider or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.From``1(NativeWeave.Data.Table{``0})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Database.DataSession.From<TEntity>(NativeWeave.Data.Table<TEntity> table) where TEntity : class
```

**summary:** Creates one mutable native SeaQuery arena bound to this session and exact static table.

**typeparam TEntity:** The statically described entity class.

**param table:** The immutable manual or generated table descriptor.

**returns:** A query to dispose after its terminal or enumeration completes.

**exception:** is null.

**exception:** Session or source admission is closed.

**exception:** The native metadata, capability or capacity rejects construction.

**remarks:** The returned query owns one native arena and borrows this session's admission. Composition copies values immediately; dispose the query after its terminal or stream has retired.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.InsertAsync``1(NativeWeave.Data.Table{``0},``0,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.InsertAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, TEntity entity, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Snapshots one entity, omits generated columns and executes one native insert.

**typeparam TEntity:** The entity class with its direct writer.

**param table:** The exact immutable table.

**param entity:** The entity to copy before dispatch; it is never mutated.

**param cancellationToken:** Requests cancellation without inferring rollback of a dispatched write.

**returns:** The provider's affected-row count.

**exception:** A required argument is null.

**exception:** The writer or value shape is invalid.

**exception:** A native constraint, provider or finite capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.InsertManyAsync``1(NativeWeave.Data.Table{``0},System.Collections.Generic.IAsyncEnumerable{``0},NativeWeave.Database.BulkOptions,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.BulkResult> NativeWeave.Database.DataSession.InsertManyAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, System.Collections.Generic.IAsyncEnumerable<TEntity> rows, NativeWeave.Database.BulkOptions? options = null, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Incrementally snapshots and writes finite native batches under explicit transaction ownership.

**typeparam TEntity:** The statically written entity class.

**param table:** The exact immutable table.

**param rows:** A one-pass input, snapshotted before its next MoveNext.

**param options:** Finite batch size and All or PerBatch ownership; null selects defaults.

**param cancellationToken:** Controls input and write admission; cleanup uses an independent token.

**returns:** Acknowledged rows and batches; caller-owned transactions are never reported as committed.

**exception:** A required argument is null.

**exception:** The option is invalid.

**exception:** PerBatch is requested inside a caller transaction.

**exception:** An owned commit crossed dispatch but its outcome is unknown.

**exception:** Cancellation is confirmed after bounded transaction cleanup.

**remarks:** All inside a caller transaction creates a tracked savepoint before input consumption. Every admitted failure preserves its original type and attaches BulkProgress. Prior PerBatch commits are not rolled back.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.InsertReturningAsync``2(NativeWeave.Data.Table{``0},``0,NativeWeave.Data.Projection{``1},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T> NativeWeave.Database.DataSession.InsertReturningAsync<TEntity, T>(NativeWeave.Data.Table<TEntity> table, TEntity entity, NativeWeave.Data.Projection<T> returning, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Snapshots one entity and materializes exactly one native INSERT RETURNING row.

**typeparam TEntity:** The statically written entity class.

**typeparam T:** The statically materialized return type.

**param table:** The exact table.

**param entity:** The entity snapshot; generated values are omitted.

**param returning:** Exact existing table columns and codecs in the desired output order.

**param cancellationToken:** Requests cancellation and joins the returned cursor.

**returns:** The single owned returned value.

**exception:** A required argument is null.

**exception:** The returned cardinality differs from one.

**exception:** Capability, output shape, provider or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.LoadRelatedAsync``2(NativeWeave.Data.EntityKey{``0},NativeWeave.Data.Relation{``0,``1},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<System.Collections.Generic.IReadOnlyList<TChild>> NativeWeave.Database.DataSession.LoadRelatedAsync<TParent, TChild>(NativeWeave.Data.EntityKey<TParent> parentKey, NativeWeave.Data.Relation<TParent, TChild> relation, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TParent : class where TChild : class
```

**summary:** Snapshots one complete parent key and runs one bounded native child foreign-key query.

**typeparam TParent:** The declared parent entity class.

**typeparam TChild:** The statically materialized child class.

**param parentKey:** Every non-null primary-key component in declaration order.

**param relation:** An immutable post-Build relationship description.

**param cancellationToken:** Requests cancellation and waits for actual cursor retirement.

**returns:** An owned bounded child list, without an implicit ordering or parent-existence query.

**exception:** A required argument is null.

**exception:** A key, model, codec or relation shape differs.

**exception:** Capability, capacity, provider or concurrent-use admission fails.

**exception:** Cancellation is confirmed after native cleanup.

**remarks:** NULL foreign-key components match no parent. Additional tenant filtering must be explicit in a Fluent query.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.QueryAsync``1(NativeWeave.Data.SqlCommand,NativeWeave.Data.Projection{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<System.Collections.Generic.IReadOnlyList<T>> NativeWeave.Database.DataSession.QueryAsync<T>(NativeWeave.Data.SqlCommand command, NativeWeave.Data.Projection<T> projection, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Materializes a bounded list using the complete declared row shape.

**typeparam T:** The statically mapped owned result type.

**param command:** An immutable query command.

**param projection:** Exact ordered aliases, codecs and a synchronous materializer.

**param cancellationToken:** The native execution cancellation token.

**returns:** An owned list within both row and encoded-byte budgets.

**exception:** A required argument is null.

**exception:** The command kind is incompatible.

**exception:** Shape, conversion, provider or configured capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.ScalarAsync``1(NativeWeave.Data.SqlCommand,NativeWeave.Data.ValueCodec{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T> NativeWeave.Database.DataSession.ScalarAsync<T>(NativeWeave.Data.SqlCommand command, NativeWeave.Data.ValueCodec<T> codec, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Reads exactly one row and column through an explicit scalar codec.

**typeparam T:** The owned scalar type, including an explicitly nullable codec.

**param command:** An immutable query command.

**param codec:** The exact scalar codec; no first-column truncation is performed.

**param cancellationToken:** The native execution cancellation token.

**returns:** The sole scalar value.

**exception:** The command or codec is null.

**exception:** The command kind is incompatible.

**exception:** Zero or multiple rows are returned.

**exception:** The complete shape, codec, provider or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.StreamAsync``1(NativeWeave.Data.SqlCommand,NativeWeave.Data.Projection{``0},System.Threading.CancellationToken)`

```csharp
public System.Collections.Generic.IAsyncEnumerable<T> NativeWeave.Database.DataSession.StreamAsync<T>(NativeWeave.Data.SqlCommand command, NativeWeave.Data.Projection<T> projection, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Creates a one-shot bounded stream; the first MoveNext admits native execution.

**typeparam T:** The statically mapped owned result type.

**param command:** An immutable query command.

**param projection:** Exact ordered result shape and synchronous materializer.

**param cancellationToken:** Combined with the enumeration token for native execution.

**returns:** A one-shot stream whose enumerator must be disposed, including on early exit.

**exception:** A required argument is null.

**exception:** The command kind is incompatible.

**exception:** Session or source admission is closed.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.UpdateAsync``1(NativeWeave.Data.Table{``0},NativeWeave.Data.EntityKey{``0},NativeWeave.Data.Changes{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.UpdateAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, NativeWeave.Data.EntityKey<TEntity> key, NativeWeave.Data.Changes<TEntity> changes, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Applies only explicit nonkey assignments under the entire native key predicate.

**typeparam TEntity:** The statically described entity class.

**param table:** The exact table.

**param key:** The complete ordered primary key.

**param changes:** Owned assignment snapshots; Unset is omitted and nullable Set assigns SQL NULL.

**param cancellationToken:** Requests cancellation under the existing write-outcome policy.

**returns:** Zero or one affected row; multiple matches are a schema constraint failure.

**exception:** The key or assignments are invalid.

**exception:** Provider, schema or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.UpdateCheckedAsync``1(NativeWeave.Data.Table{``0},NativeWeave.Data.EntityKey{``0},NativeWeave.Data.Changes{``0},NativeWeave.Data.ConcurrencyCheck{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.UpdateCheckedAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, NativeWeave.Data.EntityKey<TEntity> key, NativeWeave.Data.Changes<TEntity> changes, NativeWeave.Data.ConcurrencyCheck<TEntity> concurrency, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Executes one key-and-version compare-and-swap without an implicit version increment or replay.

**typeparam TEntity:** The statically described entity class.

**param table:** The exact table.

**param key:** Every primary-key component, retaining tenant scope.

**param changes:** Explicit assignments including a caller-supplied new version when desired.

**param concurrency:** Every declared expected concurrency token.

**param cancellationToken:** Requests cancellation without fabricating a write outcome.

**returns:** Exactly one acknowledged affected row.

**exception:** No row matched the exact key and expected tokens.

**exception:** The key, assignments or checks are invalid.

**exception:** The schema, provider or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSession.UpsertAsync``1(NativeWeave.Data.Table{``0},``0,NativeWeave.Database.ConflictTarget{``0},NativeWeave.Data.Changes{``0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Database.DataSession.UpsertAsync<TEntity>(NativeWeave.Data.Table<TEntity> table, TEntity entity, NativeWeave.Database.ConflictTarget<TEntity> conflict, NativeWeave.Data.Changes<TEntity> update, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken)) where TEntity : class
```

**summary:** Executes one atomic native upsert with independent insert and conflict-update snapshots.

**typeparam TEntity:** The statically described entity class.

**param table:** The exact table.

**param entity:** The insert row, excluding generated columns.

**param conflict:** An explicit column or PostgreSQL constraint target.

**param update:** A separate nonempty assignment snapshot; values may differ from the inserted row.

**param cancellationToken:** Requests cancellation under the existing write-outcome policy.

**returns:** The provider's affected-row count.

**exception:** A required argument is null.

**exception:** The target is unsupported by this provider.

**exception:** The actual unique constraint, provider or capacity fails.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `M:NativeWeave.Database.DataSource.CanConnectAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<bool> NativeWeave.Database.DataSource.CanConnectAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Opens and closes a real session, returning false only for provider connection failures.

**param cancellationToken:** The connection test cancellation token.

**returns:** True when a native session was established; false for a provider connection failure.

**exception:** Admission is closed.

**exception:** Cancellation is confirmed.

**remarks:** Configuration, loading, resource, panic and bridge failures retain their exception types.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `M:NativeWeave.Database.DataSource.CloseAsync(System.TimeSpan,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.DatabaseCloseResult> NativeWeave.Database.DataSource.CloseAsync(System.TimeSpan waitBudget, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Starts closure and waits only within the caller's independent budget.

**param waitBudget:** A finite nonnegative wait; zero returns the current observation.

**param cancellationToken:** Cancels this wait while native cleanup continues.

**returns:** A truthful cleanup observation; expired waits report Pending and unreleased local resources.

**exception:** The budget is invalid.

**exception:** The wait is canceled after closure starts.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `M:NativeWeave.Database.DataSource.Dispose`

```csharp
public void NativeWeave.Database.DataSource.Dispose()
```

**summary:** Closes admission and requests bounded native cleanup without blocking for I/O.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `M:NativeWeave.Database.DataSource.DisposeAsync`

```csharp
public System.Threading.Tasks.ValueTask NativeWeave.Database.DataSource.DisposeAsync()
```

**summary:** Closes admission and joins actual local safety, even beyond an application policy deadline.

**returns:** The native cleanup join.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `M:NativeWeave.Database.DataSource.OpenSessionAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.DataSession> NativeWeave.Database.DataSource.OpenSessionAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Acquires an independent physical session through bounded native pool admission.

**param cancellationToken:** Cancels admission or requests accepted native work to stop.

**returns:** A session that must be disposed; its ownership is independent from this operation.

**exception:** The source has closed admission.

**exception:** Admission or the provider fails.

**exception:** The native operation confirms cancellation.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `M:NativeWeave.Database.DataSourceBuilder.#ctor`

```csharp
public NativeWeave.Database.DataSourceBuilder.DataSourceBuilder()
```

**summary:** Creates an unconfigured builder without loading a module.

**Inherited type policy:** Configuration snapshots values. Build negotiates the packaged module and creates a lazy native pool; it opens no database connection. Independent builds create independent source generations.

## `M:NativeWeave.Database.DataSourceBuilder.Build`

```csharp
public NativeWeave.Database.DataSource NativeWeave.Database.DataSourceBuilder.Build()
```

**summary:** Negotiates the selected precompiled engine and creates an independently owned lazy pool.

**returns:** A source to dispose asynchronously when its sessions have finished.

**exception:** No provider was configured.

**exception:** The packaged module fails preflight.

**exception:** The native provider rejects its immutable configuration.

**remarks:** This call starts an engine-local runtime but performs no connection or migration I/O.

**Inherited type policy:** Configuration snapshots values. Build negotiates the packaged module and creates a lazy native pool; it opens no database connection. Independent builds create independent source generations.

## `M:NativeWeave.Database.DataSourceBuilder.ConfigureLimits(NativeWeave.Database.DatabaseLimits)`

```csharp
public NativeWeave.Database.DataSourceBuilder NativeWeave.Database.DataSourceBuilder.ConfigureLimits(NativeWeave.Database.DatabaseLimits limits)
```

**summary:** Copies and validates finite resource limits for subsequent builds.

**param limits:** The immutable limit settings.

**returns:** This builder.

**exception:** is null.

**exception:** A value exceeds the native finite profile.

**Inherited type policy:** Configuration snapshots values. Build negotiates the packaged module and creates a lazy native pool; it opens no database connection. Independent builds create independent source generations.

## `M:NativeWeave.Database.DataSourceBuilder.WithName(System.String)`

```csharp
public NativeWeave.Database.DataSourceBuilder NativeWeave.Database.DataSourceBuilder.WithName(string name)
```

**summary:** Sets the diagnostic source identity without including connection credentials.

**param name:** A nonempty strict-Unicode name of at most 256 UTF-8 bytes.

**returns:** This builder.

**exception:** The name is empty, contains NUL, or is invalid Unicode.

**exception:** is null.

**exception:** The name exceeds its byte limit.

**Inherited type policy:** Configuration snapshots values. Build negotiates the packaged module and creates a lazy native pool; it opens no database connection. Independent builds create independent source generations.

## `M:NativeWeave.Database.DatabaseAdministration.GetMigrationStatusAsync(NativeWeave.Database.MigrationBundle,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<System.Collections.Generic.IReadOnlyList<NativeWeave.Database.MigrationStatus>> NativeWeave.Database.DatabaseAdministration.GetMigrationStatusAsync(NativeWeave.Database.MigrationBundle bundle, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Reads an immutable comparison of this bundle and the successful native ledger.

**param bundle:** The exact provider-bound bundle, including previously applied entries.

**param cancellationToken:** The cancellation request retained through connection cleanup.

**returns:** Statuses in strictly ascending version order.

**exception:** The bundle/provider is invalid.

**exception:** History, checksum, provider or result limits fail.

**exception:** Cancellation is confirmed after cleanup.

**Inherited type policy:** One independent administrative connection executes at a time per source, with bounded waiting. Every outcome closes that connection before task retirement. It never uses a request session or request transaction. Result counts, strings and nested columns are charged to source buffering and field limits.

## `M:NativeWeave.Database.DatabaseAdministration.GetTablesAsync(System.String,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<System.Collections.Generic.IReadOnlyList<NativeWeave.Database.SchemaTable>> NativeWeave.Database.DatabaseAdministration.GetTablesAsync(string? schema = null, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Reads bounded table and column metadata with native parameterized catalog queries.

**param schema:** A user-schema identifier; null selects PostgreSQL current_schema or SQLite main.

**param cancellationToken:** The cancellation request retained through cleanup.

**returns:** Immutable tables with columns in catalog order.

**exception:** The schema scope is invalid or names a system/attached schema.

**exception:** Provider or nested buffering/field limits fail.

**exception:** Cancellation is confirmed after cleanup.

**remarks:** This reads catalog metadata only. It performs no schema difference inference or automatic model creation.

**Inherited type policy:** One independent administrative connection executes at a time per source, with bounded waiting. Every outcome closes that connection before task retirement. It never uses a request session or request transaction. Result counts, strings and nested columns are charged to source buffering and field limits.

## `M:NativeWeave.Database.DatabaseAdministration.MigrateAsync(NativeWeave.Database.MigrationBundle,NativeWeave.Database.MigrationOptions,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<NativeWeave.Database.MigrationReport> NativeWeave.Database.DatabaseAdministration.MigrateAsync(NativeWeave.Database.MigrationBundle bundle, NativeWeave.Database.MigrationOptions? options = null, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Applies the selected forward migration range using SQLx and its persisted checksum ledger.

**param bundle:** An immutable trusted bundle for this source's provider.

**param options:** Target and explicit nontransactional policy; null uses transactional defaults.

**param cancellationToken:** Requests cancellation while retained native work and connection closure complete.

**returns:** A confirmed completed report; a failed migration throws.

**exception:** The bundle/provider/options are invalid.

**exception:** Provider, checksum, dirty phase or finite result capacity fails.

**exception:** The native provider/profile does not support the requested migration mode.

**exception:** Cancellation is confirmed after native cleanup.

**remarks:** PostgreSQL commits each transactional entry independently. SQLite commits the entire selected batch in one tracked IMMEDIATE transaction. Nontransactional PostgreSQL preserves partial effects and an applying phase; only a new explicit identical call may resume a replay-safe script. Cancellation or connection closure never proves that a previously dispatched business commit did not happen.

**Inherited type policy:** One independent administrative connection executes at a time per source, with bounded waiting. Every outcome closes that connection before task retirement. It never uses a request session or request transaction. Result counts, strings and nested columns are charged to source buffering and field limits.

## `M:NativeWeave.Database.DatabaseAdministration.ValidateMigrationsAsync(NativeWeave.Database.MigrationBundle,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task NativeWeave.Database.DatabaseAdministration.ValidateMigrationsAsync(NativeWeave.Database.MigrationBundle bundle, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Validates checksum, missing/extra history and dirty execution phases without changing schema.

**param bundle:** The complete trusted manifest expected in the database.

**param cancellationToken:** The cancellation request retained through cleanup.

**returns:** A task completing only after validation and dedicated connection retirement.

**exception:** The manifest/provider is invalid.

**exception:** The ledger is incompatible, dirty, inaccessible or exceeds bounds.

**exception:** Cancellation is confirmed after cleanup.

**Inherited type policy:** One independent administrative connection executes at a time per source, with bounded waiting. Every outcome closes that connection before task retirement. It never uses a request session or request transaction. Result counts, strings and nested columns are charged to source buffering and field limits.

## `M:NativeWeave.Database.DatabaseCapabilities.Supports(System.String)`

```csharp
public bool NativeWeave.Database.DatabaseCapabilities.Supports(string capability)
```

**summary:** Tests one case-sensitive stable capability name without a native call.

**param capability:** The requested name; an unknown or empty name returns false.

**returns:** True only if the actual module advertised the capability.

**exception:** is null.

**Inherited type policy:** Unknown names return false. A capability name does not authorize a different provider or an arbitrary SQL feature.

## `M:NativeWeave.Database.DatabaseLimits.#ctor`

```csharp
public NativeWeave.Database.DatabaseLimits.DatabaseLimits()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.Equals(NativeWeave.Database.DatabaseLimits)`

```csharp
public bool NativeWeave.Database.DatabaseLimits.Equals(NativeWeave.Database.DatabaseLimits? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.DatabaseLimits.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.GetHashCode`

```csharp
public override int NativeWeave.Database.DatabaseLimits.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.ToString`

```csharp
public override string NativeWeave.Database.DatabaseLimits.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.op_Equality(NativeWeave.Database.DatabaseLimits,NativeWeave.Database.DatabaseLimits)`

```csharp
public static bool NativeWeave.Database.DatabaseLimits.operator ==(NativeWeave.Database.DatabaseLimits? left, NativeWeave.Database.DatabaseLimits? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.op_Inequality(NativeWeave.Database.DatabaseLimits,NativeWeave.Database.DatabaseLimits)`

```csharp
public static bool NativeWeave.Database.DatabaseLimits.operator !=(NativeWeave.Database.DatabaseLimits? left, NativeWeave.Database.DatabaseLimits? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseLimits.{Clone}$`

```csharp
public NativeWeave.Database.DatabaseLimits NativeWeave.Database.DatabaseLimits.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `M:NativeWeave.Database.DatabaseProvider.#ctor`

```csharp
public NativeWeave.Database.DatabaseProvider.DatabaseProvider()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.Migration.#ctor(System.Int64,System.String,System.String,NativeWeave.Database.MigrationTransactionMode)`

```csharp
public NativeWeave.Database.Migration.Migration(long Version, string Description, string Sql, NativeWeave.Database.MigrationTransactionMode TransactionMode = NativeWeave.Database.MigrationTransactionMode.Transactional)
```

**summary:** Defines one trusted, immutable SQL migration.

**remarks:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

**param Version:** A positive version, strictly ascending within its bundle.

**param Description:** A nonempty diagnostic description without credentials.

**param Sql:** Exact Unicode SQL; UTF-8 bytes are checksummed without newline normalization.

**param TransactionMode:** Transactional by default; explicit transaction-control statements are rejected.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.Deconstruct(System.Int64@,System.String@,System.String@,NativeWeave.Database.MigrationTransactionMode@)`

```csharp
public void NativeWeave.Database.Migration.Deconstruct(out long Version, out string Description, out string Sql, out NativeWeave.Database.MigrationTransactionMode TransactionMode)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.Equals(NativeWeave.Database.Migration)`

```csharp
public bool NativeWeave.Database.Migration.Equals(NativeWeave.Database.Migration? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.Migration.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.GetHashCode`

```csharp
public override int NativeWeave.Database.Migration.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.ToString`

```csharp
public override string NativeWeave.Database.Migration.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.op_Equality(NativeWeave.Database.Migration,NativeWeave.Database.Migration)`

```csharp
public static bool NativeWeave.Database.Migration.operator ==(NativeWeave.Database.Migration? left, NativeWeave.Database.Migration? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.op_Inequality(NativeWeave.Database.Migration,NativeWeave.Database.Migration)`

```csharp
public static bool NativeWeave.Database.Migration.operator !=(NativeWeave.Database.Migration? left, NativeWeave.Database.Migration? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.Migration.{Clone}$`

```csharp
public NativeWeave.Database.Migration NativeWeave.Database.Migration.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `M:NativeWeave.Database.MigrationBundle.#ctor(NativeWeave.Database.DatabaseProvider,System.Collections.Generic.IReadOnlyList{NativeWeave.Database.Migration})`

```csharp
public NativeWeave.Database.MigrationBundle.MigrationBundle(NativeWeave.Database.DatabaseProvider provider, System.Collections.Generic.IReadOnlyList<NativeWeave.Database.Migration> migrations)
```

**summary:** Creates an immutable snapshot and validates versions, strings, modes and finite encoding limits.

**param provider:** The exact provider that may consume the bundle.

**param migrations:** The trusted scripts in strictly ascending positive version order.

**exception:** The collection, an entry or a string is null.

**exception:** Versions, strings, modes or encoded limits are invalid.

**remarks:** The input collection may be changed after return; this instance retains its own snapshot.

**Inherited type policy:** Construction performs no native load or database I/O. Its SHA-256 identity covers the canonical kind12 provider and entry sequence before the hash field is added. Each entry separately contains SQL SHA-256; the native SQLx ledger retains SQLx's own SHA-384 checksum. Scripts must be trusted deployment artifacts.

## `M:NativeWeave.Database.MigrationOptions.#ctor`

```csharp
public NativeWeave.Database.MigrationOptions.MigrationOptions()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.Equals(NativeWeave.Database.MigrationOptions)`

```csharp
public bool NativeWeave.Database.MigrationOptions.Equals(NativeWeave.Database.MigrationOptions? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.MigrationOptions.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.GetHashCode`

```csharp
public override int NativeWeave.Database.MigrationOptions.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.ToString`

```csharp
public override string NativeWeave.Database.MigrationOptions.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.op_Equality(NativeWeave.Database.MigrationOptions,NativeWeave.Database.MigrationOptions)`

```csharp
public static bool NativeWeave.Database.MigrationOptions.operator ==(NativeWeave.Database.MigrationOptions? left, NativeWeave.Database.MigrationOptions? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.op_Inequality(NativeWeave.Database.MigrationOptions,NativeWeave.Database.MigrationOptions)`

```csharp
public static bool NativeWeave.Database.MigrationOptions.operator !=(NativeWeave.Database.MigrationOptions? left, NativeWeave.Database.MigrationOptions? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationOptions.{Clone}$`

```csharp
public NativeWeave.Database.MigrationOptions NativeWeave.Database.MigrationOptions.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `M:NativeWeave.Database.MigrationReport.#ctor(System.Int32,System.Nullable{System.Int64},System.Boolean)`

```csharp
public NativeWeave.Database.MigrationReport.MigrationReport(int AppliedCount, long? CurrentVersion, bool Completed)
```

**summary:** Reports a successfully completed explicit migration call.

**remarks:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

**param AppliedCount:** The number applied by this invocation.

**param CurrentVersion:** The last confirmed applied version, or null for an empty database.

**param Completed:** True on success; failures throw and retain their original error.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.Deconstruct(System.Int32@,System.Nullable{System.Int64}@,System.Boolean@)`

```csharp
public void NativeWeave.Database.MigrationReport.Deconstruct(out int AppliedCount, out long? CurrentVersion, out bool Completed)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.Equals(NativeWeave.Database.MigrationReport)`

```csharp
public bool NativeWeave.Database.MigrationReport.Equals(NativeWeave.Database.MigrationReport? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.MigrationReport.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.GetHashCode`

```csharp
public override int NativeWeave.Database.MigrationReport.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.ToString`

```csharp
public override string NativeWeave.Database.MigrationReport.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.op_Equality(NativeWeave.Database.MigrationReport,NativeWeave.Database.MigrationReport)`

```csharp
public static bool NativeWeave.Database.MigrationReport.operator ==(NativeWeave.Database.MigrationReport? left, NativeWeave.Database.MigrationReport? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.op_Inequality(NativeWeave.Database.MigrationReport,NativeWeave.Database.MigrationReport)`

```csharp
public static bool NativeWeave.Database.MigrationReport.operator !=(NativeWeave.Database.MigrationReport? left, NativeWeave.Database.MigrationReport? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationReport.{Clone}$`

```csharp
public NativeWeave.Database.MigrationReport NativeWeave.Database.MigrationReport.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `M:NativeWeave.Database.MigrationStatus.#ctor(System.Int64,System.String,System.String,System.Boolean)`

```csharp
public NativeWeave.Database.MigrationStatus.MigrationStatus(long Version, string Description, string Checksum, bool Applied)
```

**summary:** Describes one bounded immutable bundle/ledger comparison.

**remarks:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

**param Version:** The positive migration version.

**param Description:** The immutable bundle description.

**param Checksum:** The lowercase hexadecimal SQLx SHA-384 checksum, distinct from the bundle hash.

**param Applied:** True only when the successful SQLx ledger contains this exact migration.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.Deconstruct(System.Int64@,System.String@,System.String@,System.Boolean@)`

```csharp
public void NativeWeave.Database.MigrationStatus.Deconstruct(out long Version, out string Description, out string Checksum, out bool Applied)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.Equals(NativeWeave.Database.MigrationStatus)`

```csharp
public bool NativeWeave.Database.MigrationStatus.Equals(NativeWeave.Database.MigrationStatus? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.MigrationStatus.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.GetHashCode`

```csharp
public override int NativeWeave.Database.MigrationStatus.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.ToString`

```csharp
public override string NativeWeave.Database.MigrationStatus.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.op_Equality(NativeWeave.Database.MigrationStatus,NativeWeave.Database.MigrationStatus)`

```csharp
public static bool NativeWeave.Database.MigrationStatus.operator ==(NativeWeave.Database.MigrationStatus? left, NativeWeave.Database.MigrationStatus? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.op_Inequality(NativeWeave.Database.MigrationStatus,NativeWeave.Database.MigrationStatus)`

```csharp
public static bool NativeWeave.Database.MigrationStatus.operator !=(NativeWeave.Database.MigrationStatus? left, NativeWeave.Database.MigrationStatus? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationStatus.{Clone}$`

```csharp
public NativeWeave.Database.MigrationStatus NativeWeave.Database.MigrationStatus.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `M:NativeWeave.Database.MigrationTransactionMode.#ctor`

```csharp
public NativeWeave.Database.MigrationTransactionMode.MigrationTransactionMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

## `M:NativeWeave.Database.SchemaColumn.#ctor(System.String,System.String,System.Boolean,System.Boolean)`

```csharp
public NativeWeave.Database.SchemaColumn.SchemaColumn(string Name, string StoreType, bool IsNullable, bool IsPrimaryKey)
```

**summary:** Describes a provider catalog column without exposing a provider row object.

**remarks:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

**param Name:** The exact store column name.

**param StoreType:** The provider's declared/formatted type.

**param IsNullable:** Whether the provider permits SQL NULL.

**param IsPrimaryKey:** Whether the column participates in a primary key.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.Deconstruct(System.String@,System.String@,System.Boolean@,System.Boolean@)`

```csharp
public void NativeWeave.Database.SchemaColumn.Deconstruct(out string Name, out string StoreType, out bool IsNullable, out bool IsPrimaryKey)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.Equals(NativeWeave.Database.SchemaColumn)`

```csharp
public bool NativeWeave.Database.SchemaColumn.Equals(NativeWeave.Database.SchemaColumn? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.SchemaColumn.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.GetHashCode`

```csharp
public override int NativeWeave.Database.SchemaColumn.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.ToString`

```csharp
public override string NativeWeave.Database.SchemaColumn.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.op_Equality(NativeWeave.Database.SchemaColumn,NativeWeave.Database.SchemaColumn)`

```csharp
public static bool NativeWeave.Database.SchemaColumn.operator ==(NativeWeave.Database.SchemaColumn? left, NativeWeave.Database.SchemaColumn? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.op_Inequality(NativeWeave.Database.SchemaColumn,NativeWeave.Database.SchemaColumn)`

```csharp
public static bool NativeWeave.Database.SchemaColumn.operator !=(NativeWeave.Database.SchemaColumn? left, NativeWeave.Database.SchemaColumn? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaColumn.{Clone}$`

```csharp
public NativeWeave.Database.SchemaColumn NativeWeave.Database.SchemaColumn.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `M:NativeWeave.Database.SchemaTable.#ctor(System.String,System.String,System.Collections.Generic.IReadOnlyList{NativeWeave.Database.SchemaColumn})`

```csharp
public NativeWeave.Database.SchemaTable.SchemaTable(string? Schema, string Name, System.Collections.Generic.IReadOnlyList<NativeWeave.Database.SchemaColumn> Columns)
```

**summary:** Describes a table and an immutable, ordinally ordered column snapshot.

**remarks:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

**param Schema:** The admitted provider schema; SQLite reports main.

**param Name:** The exact table name.

**param Columns:** The bounded columns in native catalog ordinal order.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.Deconstruct(System.String@,System.String@,System.Collections.Generic.IReadOnlyList{NativeWeave.Database.SchemaColumn}@)`

```csharp
public void NativeWeave.Database.SchemaTable.Deconstruct(out string? Schema, out string Name, out System.Collections.Generic.IReadOnlyList<NativeWeave.Database.SchemaColumn> Columns)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.Equals(NativeWeave.Database.SchemaTable)`

```csharp
public bool NativeWeave.Database.SchemaTable.Equals(NativeWeave.Database.SchemaTable? other)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.Equals(System.Object)`

```csharp
public override bool NativeWeave.Database.SchemaTable.Equals(object? obj)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.GetHashCode`

```csharp
public override int NativeWeave.Database.SchemaTable.GetHashCode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.ToString`

```csharp
public override string NativeWeave.Database.SchemaTable.ToString()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.op_Equality(NativeWeave.Database.SchemaTable,NativeWeave.Database.SchemaTable)`

```csharp
public static bool NativeWeave.Database.SchemaTable.operator ==(NativeWeave.Database.SchemaTable? left, NativeWeave.Database.SchemaTable? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.op_Inequality(NativeWeave.Database.SchemaTable,NativeWeave.Database.SchemaTable)`

```csharp
public static bool NativeWeave.Database.SchemaTable.operator !=(NativeWeave.Database.SchemaTable? left, NativeWeave.Database.SchemaTable? right)
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Database.SchemaTable.{Clone}$`

```csharp
public NativeWeave.Database.SchemaTable NativeWeave.Database.SchemaTable.<Clone>$()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `M:NativeWeave.Query.CommonTable`1.Create(NativeWeave.Data.Table{`0},NativeWeave.Query.QuerySelection{`0},System.Boolean)`

```csharp
public static NativeWeave.Query.CommonTable<T> NativeWeave.Query.CommonTable<T>.Create(NativeWeave.Data.Table<T> declaredShape, NativeWeave.Query.QuerySelection<T> body, bool recursive = false)
```

**summary:** Clones a native selected body into the declared shape; recursive mode requires a validated anchor/member UNION.

**inheritdoc:**

**param declaredShape:** The static CTE row descriptor with an explicit logical table name and compatible fields.

**param body:** The selected native CTE body to freeze; later body mutations do not affect this snapshot.

**param recursive:** Whether the validated body is a recursive anchor/member UNION with one declared self-reference.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** The snapshot is bound to one source and a declared static row shape. With imports a native retained reference. Disposal prevents new imports and does not mutate previously imported snapshots. Recursive creation requires one validated anchor/member self-reference.

## `M:NativeWeave.Query.CommonTable`1.Dispose`

```csharp
public void NativeWeave.Query.CommonTable<T>.Dispose()
```

**summary:** Prevents new CTE imports and releases this native snapshot reference.

**inheritdoc:**

**Inherited type policy:** The snapshot is bound to one source and a declared static row shape. With imports a native retained reference. Disposal prevents new imports and does not mutate previously imported snapshots. Recursive creation requires one validated anchor/member self-reference.

## `M:NativeWeave.Query.FrameBoundary.#ctor`

```csharp
public NativeWeave.Query.FrameBoundary.FrameBoundary()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Only these ROWS endpoints are supported. Reversed or unsupported bounds fail before native state publication; finite numeric PRECEDING/FOLLOWING frames are not declared.

## `M:NativeWeave.Query.JoinPredicate`2.#ctor`

```csharp
public NativeWeave.Query.JoinPredicate<TLeft, TRight>.JoinPredicate()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Use only inside the synchronous JOIN callback. Provisional right-side expressions are invalidated on commit or abort. Values and nullability stay exact; explicitly lift a non-null parent key to compare a nullable foreign key.

## `M:NativeWeave.Query.JoinPredicate`2.Left``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.JoinPredicate<TLeft, TRight>.Left<T>(NativeWeave.Data.Column<TLeft, T> column)
```

**summary:** Reads a root-table column during the synchronous ON callback.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Use only inside the synchronous JOIN callback. Provisional right-side expressions are invalidated on commit or abort. Values and nullability stay exact; explicitly lift a non-null parent key to compare a nullable foreign key.

## `M:NativeWeave.Query.JoinPredicate`2.Right``1(NativeWeave.Data.Column{`1,``0})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.JoinPredicate<TLeft, TRight>.Right<T>(NativeWeave.Data.Column<TRight, T> column)
```

**summary:** Reads a provisional joined column; the resulting ON token expires on commit or abort.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Use only inside the synchronous JOIN callback. Provisional right-side expressions are invalidated on commit or abort. Values and nullability stay exact; explicitly lift a non-null parent key to compare a nullable foreign key.

## `M:NativeWeave.Query.JoinedTable`1.#ctor`

```csharp
public NativeWeave.Query.JoinedTable<TEntity>.JoinedTable()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The alias is a borrowed token, not an independently disposable query. Default aliases and aliases from another query reject, even if the CLR entity type matches.

## `M:NativeWeave.Query.LeftJoinedTable`1.#ctor`

```csharp
public NativeWeave.Query.LeftJoinedTable<TEntity>.LeftJoinedTable()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Use NullableValue or NullableReference to project its columns and HasMatch to distinguish absence. No default scalar sentinel or implicit object graph is introduced. Its query owns the alias lifetime.

## `M:NativeWeave.Query.LockWait.#ctor`

```csharp
public NativeWeave.Query.LockWait.LockWait()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Controls PostgreSQL row-lock conflicts within the same transaction and total query deadline; it does not enable transparent retries.

## `M:NativeWeave.Query.NullOrder.#ctor`

```csharp
public NativeWeave.Query.NullOrder.NullOrder()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Both providers render explicit SQL NULL placement. Ordering alone supplies no uniqueness or snapshot guarantee.

## `M:NativeWeave.Query.PreparedQuery`1.AsAsyncEnumerable(NativeWeave.Database.DataSession,NativeWeave.Query.QueryParameters,System.Threading.CancellationToken)`

```csharp
public System.Collections.Generic.IAsyncEnumerable<T> NativeWeave.Query.PreparedQuery<T>.AsAsyncEnumerable(NativeWeave.Database.DataSession session, NativeWeave.Query.QueryParameters? parameters = null, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Snapshots exact parameter values now and creates one independent lazy native stream.

**inheritdoc:**

**param session:** An open execution session belonging to this plan's exact source.

**param parameters:** The complete declared parameter set; null denotes an empty set and is valid only for a parameterless plan.

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** A one-shot lazy stream of owned results. Dispose its enumerator to request stop and await retirement on early exit.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Concurrent execution uses separate sessions from the same source. Disposing prevents new dispatch; accepted native operations retain their plan independently and complete safely.

## `M:NativeWeave.Query.PreparedQuery`1.Dispose`

```csharp
public void NativeWeave.Query.PreparedQuery<T>.Dispose()
```

**summary:** Prevents new execution and releases this plan reference without cancelling accepted operations.

**inheritdoc:**

**Inherited type policy:** Concurrent execution uses separate sessions from the same source. Disposing prevents new dispatch; accepted native operations retain their plan independently and complete safely.

## `M:NativeWeave.Query.PreparedQuery`1.ToListAsync(NativeWeave.Database.DataSession,NativeWeave.Query.QueryParameters,System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<System.Collections.Generic.IReadOnlyList<T>> NativeWeave.Query.PreparedQuery<T>.ToListAsync(NativeWeave.Database.DataSession session, NativeWeave.Query.QueryParameters? parameters = null, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Snapshots the exact declared parameter set before await and executes a bounded owned list.

**inheritdoc:**

**param session:** An open execution session belonging to this plan's exact source.

**param parameters:** The complete declared parameter set; null denotes an empty set and is valid only for a parameterless plan.

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Concurrent execution uses separate sessions from the same source. Disposing prevents new dispatch; accepted native operations retain their plan independently and complete safely.

## `M:NativeWeave.Query.ProjectionBuilder`1.Add``1(NativeWeave.Query.SqlExpression{``0},System.String)`

```csharp
public NativeWeave.Data.ResultColumn<TValue> NativeWeave.Query.ProjectionBuilder<T>.Add<TValue>(NativeWeave.Query.SqlExpression<TValue> expression, string alias)
```

**summary:** Adds an exact same-query scalar and unique result alias, returning its projection token.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param alias:** The bounded exact SQL/result alias; duplicate or invalid names reject.

**typeparam TValue:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed result token associated with this exact projection builder.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Fields must come from its exact live query. Build freezes field order, unique names, codec/nullability and the direct materializer; later Add or Build rejects. RowReader validates the full shape before the callback, and escaping DTO values own their data.

## `M:NativeWeave.Query.ProjectionBuilder`1.Build(NativeWeave.Data.RowMaterializer{`0})`

```csharp
public NativeWeave.Data.Projection<T> NativeWeave.Query.ProjectionBuilder<T>.Build(NativeWeave.Data.RowMaterializer<T> materializer)
```

**summary:** Consumes the builder and freezes a direct AOT-visible materializer; it does not execute SQL.

**inheritdoc:**

**param materializer:** The statically compiled direct constructor or field reader; runtime reflection is not used.

**returns:** An immutable projection with typed field tokens and the static direct materializer.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Fields must come from its exact live query. Build freezes field order, unique names, codec/nullability and the direct materializer; later Add or Build rejects. RowReader validates the full shape before the callback, and escaping DTO values own their data.

## `M:NativeWeave.Query.QueryParameter`1.#ctor`

```csharp
public NativeWeave.Query.QueryParameter<T>.QueryParameter()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Parameter IDs are monotonically allocated within a source generation, independently of query expression tokens. A copied parameter remains an identity; it owns no native arena or value, and only declared/imported plans may execute it.

## `M:NativeWeave.Query.QueryParameters.#ctor`

```csharp
public NativeWeave.Query.QueryParameters.QueryParameters()
```

**summary:** Creates an empty explicit parameter set.

**inheritdoc:**

**Inherited type policy:** Set snapshots each encoded value before returning. A terminal copies the complete finite set before its first await; later Set calls do not change admitted execution. Missing, extra, foreign or codec-incompatible identities reject before native dispatch. No global parameter dictionary exists.

## `M:NativeWeave.Query.QueryParameters.Set``1(NativeWeave.Query.QueryParameter{``0},``0)`

```csharp
public NativeWeave.Query.QueryParameters NativeWeave.Query.QueryParameters.Set<T>(NativeWeave.Query.QueryParameter<T> parameter, T value)
```

**summary:** Copies or replaces one typed parameter value; default or conflicting source identities reject.

**inheritdoc:**

**param parameter:** The declared source-generation parameter identity with its exact typed codec.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Set snapshots each encoded value before returning. A terminal copies the complete finite set before its first await; later Set calls do not change admitted execution. Missing, extra, foreign or codec-incompatible identities reject before native dispatch. No global parameter dictionary exists.

## `M:NativeWeave.Query.QueryRow`1.#ctor`

```csharp
public NativeWeave.Query.QueryRow<TEntity>.QueryRow()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `M:NativeWeave.Query.QueryRow`1.Equal``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.QueryRow<TEntity>.Equal<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Snapshots a typed value and creates native SQL equality.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `M:NativeWeave.Query.QueryRow`1.Get``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.QueryRow<TEntity>.Get<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Creates an immediate native expression for an exact root-table column.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `M:NativeWeave.Query.QueryRow`1.GreaterThanOrEqual``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.QueryRow<TEntity>.GreaterThanOrEqual<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Snapshots a typed lower bound and creates a native comparison.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `M:NativeWeave.Query.QueryRow`1.IsNotNull``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.QueryRow<TEntity>.IsNotNull<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Tests the exact root column for SQL non-NULL.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `M:NativeWeave.Query.QueryRow`1.IsNull``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.QueryRow<TEntity>.IsNull<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Tests the exact root column for SQL NULL.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `M:NativeWeave.Query.QuerySelection`1.#ctor`

```csharp
public NativeWeave.Query.QuerySelection<T>.QuerySelection()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.AsAsyncEnumerable(System.Threading.CancellationToken)`

```csharp
public System.Collections.Generic.IAsyncEnumerable<T> NativeWeave.Query.QuerySelection<T>.AsAsyncEnumerable(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Seals synchronously and creates a one-shot bounded stream whose first MoveNext dispatches.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** A one-shot lazy stream of owned results. Dispose its enumerator to request stop and await retirement on early exit.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.Combine(NativeWeave.Query.QuerySelection{`0},NativeWeave.Query.SetOperation)`

```csharp
public NativeWeave.Query.QuerySelection<T> NativeWeave.Query.QuerySelection<T>.Combine(NativeWeave.Query.QuerySelection<T> other, NativeWeave.Query.SetOperation operation = NativeWeave.Query.SetOperation.UnionAll)
```

**summary:** Appends a native set operation using a frozen same-source selection; the other query remains mutable.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**param operation:** The native SQL set operation with exact compatible row shapes.

**returns:** The borrowed current-selection view; its owning query retains the native arena.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.FirstAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T> NativeWeave.Query.QuerySelection<T>.FirstAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Reads at most one business row and retires the cursor; absence throws.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.FirstOrDefaultAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T?> NativeWeave.Query.QuerySelection<T>.FirstOrDefaultAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Reads at most one business row, returning default(T) on absence.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.Prepare`

```csharp
public NativeWeave.Query.PreparedQuery<T> NativeWeave.Query.QuerySelection<T>.Prepare()
```

**summary:** Seals and transfers an immutable source-bound native plan for independent parameter snapshots.

**inheritdoc:**

**returns:** An independently disposable immutable native plan bound to this source.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.SingleAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T> NativeWeave.Query.QuerySelection<T>.SingleAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Reads at most two business rows and requires exactly one, with cleanup on either cardinality failure.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.SingleOrDefaultAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T?> NativeWeave.Query.QuerySelection<T>.SingleOrDefaultAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Requires at most one business row and returns default(T) when absent.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.ToArrayAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<T[]> NativeWeave.Query.QuerySelection<T>.ToArrayAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Seals once and returns a bounded owned array after native cursor retirement.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.ToListAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<System.Collections.Generic.IReadOnlyList<T>> NativeWeave.Query.QuerySelection<T>.ToListAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Seals once and returns a bounded owned list after native cursor retirement.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.QuerySelection`1.ToSql`

```csharp
public string NativeWeave.Query.QuerySelection<T>.ToSql()
```

**summary:** Renders a bounded native clone with placeholders and no parameter values; does not execute or seal.

**inheritdoc:**

**returns:** A bounded native SQL rendering with placeholders and no bound values.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `M:NativeWeave.Query.Query`1.AnyAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<bool> NativeWeave.Query.Query<TEntity>.AnyAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Performs native EXISTS over the fully composed query.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Clone`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Clone()
```

**summary:** Creates an explicit deep native mutable clone; existing expression/alias proxies remain bound to this query.

**inheritdoc:**

**returns:** A new independently disposable native mutable clone; old proxies still belong to the old query.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Column``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.Query<TEntity>.Column<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Creates an immediate root-column native scalar token.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Column``2(NativeWeave.Query.JoinedTable{``0},NativeWeave.Data.Column{``0,``1})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.Query<TEntity>.Column<TJoin, T>(NativeWeave.Query.JoinedTable<TJoin> table, NativeWeave.Data.Column<TJoin, T> column) where TJoin : class
```

**summary:** Creates a scalar from an exact same-query inner-join alias and table.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.CountAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Query.Query<TEntity>.CountAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Counts the fully composed native result without fetching DTOs into managed memory.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.CountRows`

```csharp
public NativeWeave.Query.SqlExpression<long> NativeWeave.Query.Query<TEntity>.CountRows()
```

**summary:** Creates a native COUNT(*) aggregate with exact Int64 result metadata.

**inheritdoc:**

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.DeleteAsync(System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Query.Query<TEntity>.DeleteAsync(System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Executes a filtered native DELETE; missing filters and unsupported joined/grouped writes reject.

**inheritdoc:**

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Dispose`

```csharp
public void NativeWeave.Query.Query<TEntity>.Dispose()
```

**summary:** Closes query admission, requests any active cursor stop and releases the native arena reference.

**inheritdoc:**

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Distinct`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Distinct()
```

**summary:** Applies native SQL DISTINCT to the selected shape.

**inheritdoc:**

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Exists``1(NativeWeave.Query.QuerySelection{``0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.Query<TEntity>.Exists<T>(NativeWeave.Query.QuerySelection<T> subquery)
```

**summary:** Snapshots a same-source selection into a native EXISTS condition.

**inheritdoc:**

**param subquery:** A current same-source selection whose native plan is cloned under admission.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.ForUpdate(NativeWeave.Query.RowLockMode,NativeWeave.Query.LockWait)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.ForUpdate(NativeWeave.Query.RowLockMode mode = NativeWeave.Query.RowLockMode.Update, NativeWeave.Query.LockWait wait = NativeWeave.Query.LockWait.Wait)
```

**summary:** Applies an admitted PostgreSQL row lock; execution requires an explicit active transaction.

**inheritdoc:**

**param mode:** The PostgreSQL row-lock strength; an explicit transaction is required.

**param wait:** The PostgreSQL lock-conflict policy.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.GroupBy``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.GroupBy<T>(NativeWeave.Query.SqlExpression<T> expression)
```

**summary:** Appends a native grouping key.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.HasMatch``1(NativeWeave.Query.LeftJoinedTable{``0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.Query<TEntity>.HasMatch<TJoin>(NativeWeave.Query.LeftJoinedTable<TJoin> table) where TJoin : class
```

**summary:** Tests the native explicit LEFT JOIN match marker, independently from nullable child data.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Having(NativeWeave.Query.SqlPredicate)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Having(NativeWeave.Query.SqlPredicate predicate)
```

**summary:** Appends a same-query native group predicate.

**inheritdoc:**

**param predicate:** The compatible native condition or synchronous typed callback; callbacks are invoked at this call.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.InnerJoin``1(NativeWeave.Data.Table{``0},System.String,System.Func{NativeWeave.Query.JoinPredicate{`0,``0},NativeWeave.Query.SqlPredicate})`

```csharp
public NativeWeave.Query.JoinedTable<TJoin> NativeWeave.Query.Query<TEntity>.InnerJoin<TJoin>(NativeWeave.Data.Table<TJoin> table, string alias, System.Func<NativeWeave.Query.JoinPredicate<TEntity, TJoin>, NativeWeave.Query.SqlPredicate> on) where TJoin : class
```

**summary:** Reserves, builds and atomically commits an explicit native INNER JOIN ON clause.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**param alias:** The bounded exact SQL/result alias; duplicate or invalid names reject.

**param on:** The synchronous typed JOIN ON callback; it is neither stored nor invoked during row enumeration.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.LeftJoin``1(NativeWeave.Data.Table{``0},System.String,System.Func{NativeWeave.Query.JoinPredicate{`0,``0},NativeWeave.Query.SqlPredicate})`

```csharp
public NativeWeave.Query.LeftJoinedTable<TJoin> NativeWeave.Query.Query<TEntity>.LeftJoin<TJoin>(NativeWeave.Data.Table<TJoin> table, string alias, System.Func<NativeWeave.Query.JoinPredicate<TEntity, TJoin>, NativeWeave.Query.SqlPredicate> on) where TJoin : class
```

**summary:** Commits a native LEFT JOIN and returns a nullable-only projected alias.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**param alias:** The bounded exact SQL/result alias; duplicate or invalid names reject.

**param on:** The synchronous typed JOIN ON callback; it is neither stored nor invoked during row enumeration.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.NullableReference``2(NativeWeave.Query.LeftJoinedTable{``0},NativeWeave.Data.Column{``0,``1})`

```csharp
public NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.Query<TEntity>.NullableReference<TJoin, T>(NativeWeave.Query.LeftJoinedTable<TJoin> table, NativeWeave.Data.Column<TJoin, T> column) where TJoin : class where T : class?
```

**summary:** Reads a reference column through a LEFT JOIN with explicit nullable result metadata.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.NullableValue``2(NativeWeave.Query.LeftJoinedTable{``0},NativeWeave.Data.Column{``0,System.Nullable{``1}})`

```csharp
public NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.Query<TEntity>.NullableValue<TJoin, T>(NativeWeave.Query.LeftJoinedTable<TJoin> table, NativeWeave.Data.Column<TJoin, T?> column) where TJoin : class where T : struct
```

**summary:** Preserves an already nullable value column through a LEFT JOIN.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.NullableValue``2(NativeWeave.Query.LeftJoinedTable{``0},NativeWeave.Data.Column{``0,``1})`

```csharp
public NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.Query<TEntity>.NullableValue<TJoin, T>(NativeWeave.Query.LeftJoinedTable<TJoin> table, NativeWeave.Data.Column<TJoin, T> column) where TJoin : class where T : struct
```

**summary:** Reads a non-null value column through a LEFT JOIN as an explicitly nullable scalar.

**inheritdoc:**

**param table:** The exact static table descriptor or same-query joined alias required by this overload.

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam TJoin:** The statically known entity class with explicit table metadata.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.OrderBy``1(NativeWeave.Data.Column{`0,``0},NativeWeave.Query.SortDirection,NativeWeave.Query.NullOrder)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.OrderBy<T>(NativeWeave.Data.Column<TEntity, T> column, NativeWeave.Query.SortDirection direction = NativeWeave.Query.SortDirection.Ascending, NativeWeave.Query.NullOrder nullOrder = NativeWeave.Query.NullOrder.Last)
```

**summary:** Replaces native ordering with the exact root column and explicit NULL policy.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param direction:** Explicit ascending or descending SQL order.

**param nullOrder:** Explicit placement of SQL NULL values in this ordering key.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.OrderBy``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SortDirection,NativeWeave.Query.NullOrder)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.OrderBy<T>(NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SortDirection direction = NativeWeave.Query.SortDirection.Ascending, NativeWeave.Query.NullOrder nullOrder = NativeWeave.Query.NullOrder.Last)
```

**summary:** Replaces native ordering with the same-query expression and explicit NULL policy.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param direction:** Explicit ascending or descending SQL order.

**param nullOrder:** Explicit placement of SQL NULL values in this ordering key.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.ParameterValue``1(NativeWeave.Query.QueryParameter{``0})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.Query<TEntity>.ParameterValue<T>(NativeWeave.Query.QueryParameter<T> parameter)
```

**summary:** Creates a native reference to an identity already declared or imported into this query.

**inheritdoc:**

**param parameter:** The declared source-generation parameter identity with its exact typed codec.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Parameter``1(System.String,NativeWeave.Data.ValueCodec{``0})`

```csharp
public NativeWeave.Query.QueryParameter<T> NativeWeave.Query.Query<TEntity>.Parameter<T>(string name, NativeWeave.Data.ValueCodec<T> codec)
```

**summary:** Allocates one nonrecycled source-generation parameter identity and declares it in this query.

**inheritdoc:**

**param name:** The bounded exact parameter name; conflicting identities in composed plans reject.

**param codec:** The statically known codec and exact nullability/configuration for the value.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Projection``1`

```csharp
public NativeWeave.Query.ProjectionBuilder<T> NativeWeave.Query.Query<TEntity>.Projection<T>()
```

**summary:** Starts an explicit typed DTO projection in this query.

**inheritdoc:**

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.SeekAfter``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.SeekAfter<T>(NativeWeave.Data.Column<TEntity, T> uniqueOrderKey, T value)
```

**summary:** Appends strict keyset comparison for one non-null unique ascending root key.

**inheritdoc:**

**param uniqueOrderKey:** The sole non-null primary key already ordered ascending, with no conflicting offset.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.SelectAll`

```csharp
public NativeWeave.Query.QuerySelection<TEntity> NativeWeave.Query.Query<TEntity>.SelectAll()
```

**summary:** Selects only root-table columns in the static entity constructor order.

**inheritdoc:**

**returns:** The borrowed current-selection view; its owning query retains the native arena.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Select``1(NativeWeave.Data.Projection{``0})`

```csharp
public NativeWeave.Query.QuerySelection<T> NativeWeave.Query.Query<TEntity>.Select<T>(NativeWeave.Data.Projection<T> projection)
```

**summary:** Selects a projection built by this exact query, or the root table's static row descriptor.

**inheritdoc:**

**param projection:** The exact query-built projection or root table row descriptor to select.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The borrowed current-selection view; its owning query retains the native arena.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Select``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public NativeWeave.Query.QuerySelection<T> NativeWeave.Query.Query<TEntity>.Select<T>(NativeWeave.Query.SqlExpression<T> expression)
```

**summary:** Selects one same-query native expression through its exact static codec.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The borrowed current-selection view; its owning query retains the native arena.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Select``3(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SqlExpression{``1},System.Func{``0,``1,``2})`

```csharp
public NativeWeave.Query.QuerySelection<TOut> NativeWeave.Query.Query<TEntity>.Select<T1, T2, TOut>(NativeWeave.Query.SqlExpression<T1> first, NativeWeave.Query.SqlExpression<T2> second, System.Func<T1, T2, TOut> materializer)
```

**summary:** Selects two native expressions into an AOT-visible direct DTO factory.

**inheritdoc:**

**param first:** The first same-query native expression in result order.

**param second:** The second same-query native expression in result order.

**param materializer:** The statically compiled direct constructor or field reader; runtime reflection is not used.

**typeparam T1:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**typeparam T2:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**typeparam TOut:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The borrowed current-selection view; its owning query retains the native arena.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Skip(System.Int32)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Skip(int count)
```

**summary:** Sets a finite nonnegative offset only with known unique ordering.

**inheritdoc:**

**param count:** The nonnegative bounded row count.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Take(System.Int32)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Take(int count)
```

**summary:** Sets a finite nonnegative native row limit; without order the selected rows are nondeterministic.

**inheritdoc:**

**param count:** The nonnegative bounded row count.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.ThenBy``1(NativeWeave.Data.Column{`0,``0},NativeWeave.Query.SortDirection,NativeWeave.Query.NullOrder)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.ThenBy<T>(NativeWeave.Data.Column<TEntity, T> column, NativeWeave.Query.SortDirection direction = NativeWeave.Query.SortDirection.Ascending, NativeWeave.Query.NullOrder nullOrder = NativeWeave.Query.NullOrder.Last)
```

**summary:** Appends a root-column order after an existing order.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param direction:** Explicit ascending or descending SQL order.

**param nullOrder:** Explicit placement of SQL NULL values in this ordering key.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.ThenBy``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SortDirection,NativeWeave.Query.NullOrder)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.ThenBy<T>(NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SortDirection direction = NativeWeave.Query.SortDirection.Ascending, NativeWeave.Query.NullOrder nullOrder = NativeWeave.Query.NullOrder.Last)
```

**summary:** Appends a same-query expression after an existing order.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param direction:** Explicit ascending or descending SQL order.

**param nullOrder:** Explicit placement of SQL NULL values in this ordering key.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.UpdateAsync(NativeWeave.Data.Changes{`0},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Query.Query<TEntity>.UpdateAsync(NativeWeave.Data.Changes<TEntity> changes, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Snapshots explicit typed changes and performs a filtered native set-based UPDATE.

**inheritdoc:**

**param changes:** The explicit immutable snapshot of permitted typed root-column assignments.

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.UpdateAsync(System.Action{NativeWeave.Query.UpdateSetters{`0}},System.Threading.CancellationToken)`

```csharp
public System.Threading.Tasks.Task<long> NativeWeave.Query.Query<TEntity>.UpdateAsync(System.Action<NativeWeave.Query.UpdateSetters<TEntity>> setters, System.Threading.CancellationToken cancellationToken = default(System.Threading.CancellationToken))
```

**summary:** Runs a synchronous typed setter callback, then applies complete native assignments and a filtered UPDATE.

**inheritdoc:**

**param setters:** The synchronous callback that stages permitted typed assignments before submission.

**param cancellationToken:** Cancellation requests native stop; completion still waits for cursor and operation retirement.

**returns:** The typed terminal result after required native operation and cursor cleanup; cardinality, mapping, provider or cancellation failures propagate through the task.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**exception:** Cancellation requests termination and cleanup.

**exception:** The finite total query deadline expires; cleanup still completes.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Value``1(``0,NativeWeave.Data.ValueCodec{``0})`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.Query<TEntity>.Value<T>(T value, NativeWeave.Data.ValueCodec<T> codec)
```

**summary:** Immediately snapshots a typed literal into the native arena.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**param codec:** The statically known codec and exact nullability/configuration for the value.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Where(NativeWeave.Query.SqlPredicate)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Where(NativeWeave.Query.SqlPredicate predicate)
```

**summary:** Appends a same-query native predicate with AND.

**inheritdoc:**

**param predicate:** The compatible native condition or synchronous typed callback; callbacks are invoked at this call.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Where(System.Func{NativeWeave.Query.QueryRow{`0},NativeWeave.Query.SqlPredicate})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.Where(System.Func<NativeWeave.Query.QueryRow<TEntity>, NativeWeave.Query.SqlPredicate> predicate)
```

**summary:** Invokes the typed callback synchronously once, then attaches its complete native predicate.

**inheritdoc:**

**param predicate:** The compatible native condition or synchronous typed callback; callbacks are invoked at this call.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.WhereEqual``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.WhereEqual<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Snapshots the value and appends root-column equality without a predicate delegate.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.WhereGreaterThanOrEqual``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.WhereGreaterThanOrEqual<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Snapshots the value and appends an inclusive native lower bound.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.WhereIf(System.Boolean,System.Func{NativeWeave.Query.QueryRow{`0},NativeWeave.Query.SqlPredicate})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.WhereIf(bool condition, System.Func<NativeWeave.Query.QueryRow<TEntity>, NativeWeave.Query.SqlPredicate> predicate)
```

**summary:** Invokes and attaches the callback only when the condition is true; false binds no captured values.

**inheritdoc:**

**param condition:** The CLR branch condition, or same-query native CASE predicate required by this overload.

**param predicate:** The compatible native condition or synchronous typed callback; callbacks are invoked at this call.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.WhereIsNotNull``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.WhereIsNotNull<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Appends an explicit root-column IS NOT NULL predicate.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.WhereIsNull``1(NativeWeave.Data.Column{`0,``0})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.WhereIsNull<T>(NativeWeave.Data.Column<TEntity, T> column)
```

**summary:** Appends an explicit root-column IS NULL predicate.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.Window`

```csharp
public NativeWeave.Query.WindowDefinition NativeWeave.Query.Query<TEntity>.Window()
```

**summary:** Creates finite query-owned native window state.

**inheritdoc:**

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.WithTimeout(System.TimeSpan)`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.WithTimeout(System.TimeSpan timeout)
```

**summary:** Snapshots a finite total execution/cursor timeout; zero expires before dispatch.

**inheritdoc:**

**param timeout:** The finite nonnegative total execution and cursor deadline, snapshotted before dispatch.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.Query`1.With``1(NativeWeave.Query.CommonTable{``0})`

```csharp
public NativeWeave.Query.Query<TEntity> NativeWeave.Query.Query<TEntity>.With<TCte>(NativeWeave.Query.CommonTable<TCte> commonTable) where TCte : class
```

**summary:** Attaches a frozen same-source native CTE and its exact immutable parameter identities.

**inheritdoc:**

**param commonTable:** The immutable CTE from this exact source to retain in the query.

**typeparam TCte:** The statically known entity class with explicit table metadata.

**returns:** This mutable query for further synchronous composition before its first terminal.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `M:NativeWeave.Query.RowLockMode.#ctor`

```csharp
public NativeWeave.Query.RowLockMode.RowLockMode()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Available only on PostgreSQL with an explicit live transaction. SQLite rejects the operation before provider dispatch.

## `M:NativeWeave.Query.SetOperation.#ctor`

```csharp
public NativeWeave.Query.SetOperation.SetOperation()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Operands must have the same source, field order, aliases, codecs and nullability. Rust snapshots the right operand; SQL duplicate and NULL semantics apply.

## `M:NativeWeave.Query.SortDirection.#ctor`

```csharp
public NativeWeave.Query.SortDirection.SortDirection()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** The native query validates each enum value before mutation. Direction is explicit; it does not change SQL NULL ordering.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Add``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},NativeWeave.Query.SqlExpression{System.Nullable{``0}})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Add<T>(this NativeWeave.Query.SqlExpression<T?> expression, NativeWeave.Query.SqlExpression<T?> value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric add with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Add``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Add<T>(this NativeWeave.Query.SqlExpression<T?> expression, T value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric add with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Add``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Add<T>(this NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SqlExpression<T> value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric add with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Add``1(NativeWeave.Query.SqlExpression{``0},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Add<T>(this NativeWeave.Query.SqlExpression<T> expression, T value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric add with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Divide``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},NativeWeave.Query.SqlExpression{System.Nullable{``0}})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Divide<T>(this NativeWeave.Query.SqlExpression<T?> expression, NativeWeave.Query.SqlExpression<T?> value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric divide with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Divide``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Divide<T>(this NativeWeave.Query.SqlExpression<T?> expression, T value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric divide with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Divide``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Divide<T>(this NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SqlExpression<T> value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric divide with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Divide``1(NativeWeave.Query.SqlExpression{``0},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Divide<T>(this NativeWeave.Query.SqlExpression<T> expression, T value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric divide with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Multiply``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},NativeWeave.Query.SqlExpression{System.Nullable{``0}})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Multiply<T>(this NativeWeave.Query.SqlExpression<T?> expression, NativeWeave.Query.SqlExpression<T?> value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric multiply with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Multiply``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Multiply<T>(this NativeWeave.Query.SqlExpression<T?> expression, T value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric multiply with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Multiply``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Multiply<T>(this NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SqlExpression<T> value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric multiply with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Multiply``1(NativeWeave.Query.SqlExpression{``0},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Multiply<T>(this NativeWeave.Query.SqlExpression<T> expression, T value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric multiply with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Subtract``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},NativeWeave.Query.SqlExpression{System.Nullable{``0}})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Subtract<T>(this NativeWeave.Query.SqlExpression<T?> expression, NativeWeave.Query.SqlExpression<T?> value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric subtract with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Subtract``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlArithmeticExtensions.Subtract<T>(this NativeWeave.Query.SqlExpression<T?> expression, T value) where T : struct, System.Numerics.INumber<T>
```

**summary:** Performs native numeric subtract with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Subtract``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Subtract<T>(this NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SqlExpression<T> value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric subtract with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlArithmeticExtensions.Subtract``1(NativeWeave.Query.SqlExpression{``0},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlArithmeticExtensions.Subtract<T>(this NativeWeave.Query.SqlExpression<T> expression, T value) where T : System.Numerics.INumber<T>
```

**summary:** Performs native numeric subtract with explicit SQL NULL propagation.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `M:NativeWeave.Query.SqlExpression`1.#ctor`

```csharp
public NativeWeave.Query.SqlExpression<T>.SqlExpression()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.Between(`0,`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.Between(T lower, T upper)
```

**summary:** Snapshots two bounds and creates native inclusive BETWEEN.

**inheritdoc:**

**param lower:** The inclusive lower endpoint, copied before the method returns.

**param upper:** The inclusive upper endpoint, copied before the method returns.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.Equal(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.Equal(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native Equal with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.Equal(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.Equal(T value)
```

**summary:** Applies native Equal with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.GreaterThan(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.GreaterThan(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native GreaterThan with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.GreaterThan(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.GreaterThan(T value)
```

**summary:** Applies native GreaterThan with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.GreaterThanOrEqual(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.GreaterThanOrEqual(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native GreaterThanOrEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.GreaterThanOrEqual(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.GreaterThanOrEqual(T value)
```

**summary:** Applies native GreaterThanOrEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.In(NativeWeave.Query.QuerySelection{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.In(NativeWeave.Query.QuerySelection<T> subquery)
```

**summary:** Snapshots a compatible same-source single-column subquery into native IN.

**inheritdoc:**

**param subquery:** A current same-source selection whose native plan is cloned under admission.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.In(System.ReadOnlySpan{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.In(System.ReadOnlySpan<T> values)
```

**summary:** Snapshots a finite value span; an empty span yields native FALSE.

**inheritdoc:**

**param values:** The finite typed input values, copied before returning; the span is never retained.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.IsNotNull`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.IsNotNull()
```

**summary:** Tests SQL non-NULL explicitly.

**inheritdoc:**

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.IsNull`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.IsNull()
```

**summary:** Tests SQL NULL explicitly without substituting a sentinel.

**inheritdoc:**

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.LessThan(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.LessThan(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native LessThan with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.LessThan(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.LessThan(T value)
```

**summary:** Applies native LessThan with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.LessThanOrEqual(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.LessThanOrEqual(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native LessThanOrEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.LessThanOrEqual(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.LessThanOrEqual(T value)
```

**summary:** Applies native LessThanOrEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.NotEqual(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.NotEqual(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native NotEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.NotEqual(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.NotEqual(T value)
```

**summary:** Applies native NotEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.NotIn(System.ReadOnlySpan{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.NotIn(System.ReadOnlySpan<T> values)
```

**summary:** Snapshots a finite value span; an empty span yields native TRUE.

**inheritdoc:**

**param values:** The finite typed input values, copied before returning; the span is never retained.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.NullSafeEqual(NativeWeave.Query.SqlExpression{`0})`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.NullSafeEqual(NativeWeave.Query.SqlExpression<T> other)
```

**summary:** Applies native NullSafeEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.NullSafeEqual(`0)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlExpression<T>.NullSafeEqual(T value)
```

**summary:** Applies native NullSafeEqual with exact codec/source checks and SQL NULL semantics.

**inheritdoc:**

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlExpression`1.Over(NativeWeave.Query.WindowDefinition)`

```csharp
public NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlExpression<T>.Over(NativeWeave.Query.WindowDefinition window)
```

**summary:** Snapshots same-query native window state onto an eligible aggregate or rank expression.

**inheritdoc:**

**param window:** The same-query window definition to snapshot at this call.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Decimal})`

```csharp
public static NativeWeave.Query.SqlExpression<decimal?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<decimal> expression)
```

**summary:** Aggregates native decimal inputs to nullable decimal, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Double})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<double> expression)
```

**summary:** Aggregates native double inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Int32})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<int> expression)
```

**summary:** Aggregates native int inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Int64})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<long> expression)
```

**summary:** Aggregates native long inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Nullable{System.Decimal}})`

```csharp
public static NativeWeave.Query.SqlExpression<decimal?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<decimal?> expression)
```

**summary:** Aggregates native decimal? inputs to nullable decimal, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Nullable{System.Double}})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<double?> expression)
```

**summary:** Aggregates native double? inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Nullable{System.Int32}})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<int?> expression)
```

**summary:** Aggregates native int? inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Nullable{System.Int64}})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<long?> expression)
```

**summary:** Aggregates native long? inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Nullable{System.Single}})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<float?> expression)
```

**summary:** Aggregates native float? inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression{System.Single})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Average(NativeWeave.Query.SqlExpression<float> expression)
```

**summary:** Aggregates native float inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Case``1(NativeWeave.Query.SqlPredicate,NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlFunctions.Case<T>(NativeWeave.Query.SqlPredicate condition, NativeWeave.Query.SqlExpression<T> whenTrue, NativeWeave.Query.SqlExpression<T> whenFalse)
```

**summary:** Creates a native CASE with same-query compatible scalar alternatives.

**inheritdoc:**

**param condition:** The CLR branch condition, or same-query native CASE predicate required by this overload.

**param whenTrue:** The compatible same-query expression for a true SQL condition.

**param whenFalse:** The compatible same-query expression for false or unknown SQL condition.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.CoalesceReference``1(NativeWeave.Query.SqlExpression{``0},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlFunctions.CoalesceReference<T>(NativeWeave.Query.SqlExpression<T?> expression, T fallback) where T : class
```

**summary:** Produces a non-null reference scalar with native SQL COALESCE.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param fallback:** The non-null typed fallback, snapshotted now and used by native COALESCE.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Coalesce``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}},``0)`

```csharp
public static NativeWeave.Query.SqlExpression<T> NativeWeave.Query.SqlFunctions.Coalesce<T>(NativeWeave.Query.SqlExpression<T?> expression, T fallback) where T : struct
```

**summary:** Produces a non-null scalar with native SQL COALESCE and an explicitly copied fallback.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param fallback:** The non-null typed fallback, snapshotted now and used by native COALESCE.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Count``1(NativeWeave.Query.SqlExpression{``0},System.Boolean)`

```csharp
public static NativeWeave.Query.SqlExpression<long> NativeWeave.Query.SqlFunctions.Count<T>(NativeWeave.Query.SqlExpression<T> expression, bool distinct = false)
```

**summary:** Counts non-null native values, optionally using DISTINCT, with exact Int64 result metadata.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param distinct:** Whether native aggregate inputs apply DISTINCT with SQL equality semantics.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.MaxNullableText(NativeWeave.Query.SqlExpression{System.String})`

```csharp
public static NativeWeave.Query.SqlExpression<string?> NativeWeave.Query.SqlFunctions.MaxNullableText(NativeWeave.Query.SqlExpression<string?> expression)
```

**summary:** Returns native text maximum under SQL collation with empty-input NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.MaxText(NativeWeave.Query.SqlExpression{System.String})`

```csharp
public static NativeWeave.Query.SqlExpression<string?> NativeWeave.Query.SqlFunctions.MaxText(NativeWeave.Query.SqlExpression<string> expression)
```

**summary:** Returns native text maximum under SQL collation with empty-input NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Max``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlFunctions.Max<T>(NativeWeave.Query.SqlExpression<T?> expression) where T : struct
```

**summary:** Returns the native maximum with the exact scalar codec and empty-input SQL NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Max``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlFunctions.Max<T>(NativeWeave.Query.SqlExpression<T> expression) where T : struct
```

**summary:** Returns the native maximum with the exact scalar codec and empty-input SQL NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.MinNullableText(NativeWeave.Query.SqlExpression{System.String})`

```csharp
public static NativeWeave.Query.SqlExpression<string?> NativeWeave.Query.SqlFunctions.MinNullableText(NativeWeave.Query.SqlExpression<string?> expression)
```

**summary:** Returns native text minimum under SQL collation with empty-input NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.MinText(NativeWeave.Query.SqlExpression{System.String})`

```csharp
public static NativeWeave.Query.SqlExpression<string?> NativeWeave.Query.SqlFunctions.MinText(NativeWeave.Query.SqlExpression<string> expression)
```

**summary:** Returns native text minimum under SQL collation with empty-input NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Min``1(NativeWeave.Query.SqlExpression{System.Nullable{``0}})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlFunctions.Min<T>(NativeWeave.Query.SqlExpression<T?> expression) where T : struct
```

**summary:** Returns the native minimum with the exact scalar codec and empty-input SQL NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Min``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlFunctions.Min<T>(NativeWeave.Query.SqlExpression<T> expression) where T : struct
```

**summary:** Returns the native minimum with the exact scalar codec and empty-input SQL NULL.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Rank(NativeWeave.Query.WindowDefinition)`

```csharp
public static NativeWeave.Query.SqlExpression<long> NativeWeave.Query.SqlFunctions.Rank(NativeWeave.Query.WindowDefinition window)
```

**summary:** Snapshots a native window into an exact Int64 RANK expression.

**inheritdoc:**

**param window:** The same-query window definition to snapshot at this call.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.RowNumber(NativeWeave.Query.WindowDefinition)`

```csharp
public static NativeWeave.Query.SqlExpression<long> NativeWeave.Query.SqlFunctions.RowNumber(NativeWeave.Query.WindowDefinition window)
```

**summary:** Snapshots a native window into an exact Int64 ROW_NUMBER expression.

**inheritdoc:**

**param window:** The same-query window definition to snapshot at this call.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Decimal})`

```csharp
public static NativeWeave.Query.SqlExpression<decimal?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<decimal> expression)
```

**summary:** Aggregates native decimal inputs to nullable decimal, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Double})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<double> expression)
```

**summary:** Aggregates native double inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Int32})`

```csharp
public static NativeWeave.Query.SqlExpression<long?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<int> expression)
```

**summary:** Aggregates native int inputs to nullable long, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Int64})`

```csharp
public static NativeWeave.Query.SqlExpression<long?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<long> expression)
```

**summary:** Aggregates native long inputs to nullable long, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Nullable{System.Decimal}})`

```csharp
public static NativeWeave.Query.SqlExpression<decimal?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<decimal?> expression)
```

**summary:** Aggregates native decimal? inputs to nullable decimal, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Nullable{System.Double}})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<double?> expression)
```

**summary:** Aggregates native double? inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Nullable{System.Int32}})`

```csharp
public static NativeWeave.Query.SqlExpression<long?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<int?> expression)
```

**summary:** Aggregates native int? inputs to nullable long, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Nullable{System.Int64}})`

```csharp
public static NativeWeave.Query.SqlExpression<long?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<long?> expression)
```

**summary:** Aggregates native long? inputs to nullable long, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Nullable{System.Single}})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<float?> expression)
```

**summary:** Aggregates native float? inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression{System.Single})`

```csharp
public static NativeWeave.Query.SqlExpression<double?> NativeWeave.Query.SqlFunctions.Sum(NativeWeave.Query.SqlExpression<float> expression)
```

**summary:** Aggregates native float inputs to nullable double, preserving empty-input NULL and explicit conversion failures.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `M:NativeWeave.Query.SqlNullabilityExtensions.AsNullableReference``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlNullabilityExtensions.AsNullableReference<T>(this NativeWeave.Query.SqlExpression<T> expression) where T : class
```

**summary:** Returns a fresh same-query nullable reference token; already-nullable metadata rejects.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** These forward-only native metadata lifts preserve the SQL value and codec configuration. They do not emit a sentinel, COALESCE or reverse conversion. Default/foreign owners reject, and repeating a reference lift rejects its already nullable descriptor.

## `M:NativeWeave.Query.SqlNullabilityExtensions.AsNullable``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public static NativeWeave.Query.SqlExpression<T?> NativeWeave.Query.SqlNullabilityExtensions.AsNullable<T>(this NativeWeave.Query.SqlExpression<T> expression) where T : struct
```

**summary:** Returns a fresh same-query nullable scalar token, preserving the exact value and codec.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** These forward-only native metadata lifts preserve the SQL value and codec configuration. They do not emit a sentinel, COALESCE or reverse conversion. Default/foreign owners reject, and repeating a reference lift rejects its already nullable descriptor.

## `M:NativeWeave.Query.SqlPredicate.#ctor`

```csharp
public NativeWeave.Query.SqlPredicate.SqlPredicate()
```

Compiler-generated record/delegate member; inherits the documented type semantics.

**Inherited type policy:** Boolean composition uses SQL three-valued logic and performs one direct native operation.

## `M:NativeWeave.Query.SqlPredicate.And(NativeWeave.Query.SqlPredicate)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlPredicate.And(NativeWeave.Query.SqlPredicate other)
```

**summary:** Combines same-query conditions with native AND.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Boolean composition uses SQL three-valued logic and performs one direct native operation.

## `M:NativeWeave.Query.SqlPredicate.Not`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlPredicate.Not()
```

**summary:** Negates this condition using native SQL NOT.

**inheritdoc:**

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Boolean composition uses SQL three-valued logic and performs one direct native operation.

## `M:NativeWeave.Query.SqlPredicate.Or(NativeWeave.Query.SqlPredicate)`

```csharp
public NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlPredicate.Or(NativeWeave.Query.SqlPredicate other)
```

**summary:** Combines same-query conditions with native OR.

**inheritdoc:**

**param other:** The compatible same-source selection or same-query expression required by this operation.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Boolean composition uses SQL three-valued logic and performs one direct native operation.

## `M:NativeWeave.Query.SqlStringExtensions.Collate(NativeWeave.Query.SqlExpression{System.String},System.String)`

```csharp
public static NativeWeave.Query.SqlExpression<string> NativeWeave.Query.SqlStringExtensions.Collate(this NativeWeave.Query.SqlExpression<string> expression, string collation)
```

**summary:** Applies only a collation admitted by the provider's fixed allowlist.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param collation:** The exact collation name in the current provider's allowlist.

**returns:** A same-query borrowed native scalar token with exact typed codec and SQL nullability.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.SqlStringExtensions.ContainsLiteral(NativeWeave.Query.SqlExpression{System.String},System.String)`

```csharp
public static NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlStringExtensions.ContainsLiteral(this NativeWeave.Query.SqlExpression<string> expression, string value)
```

**summary:** Escapes wildcard characters and binds a literal contains pattern.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.SqlStringExtensions.ContainsNullableLiteral(NativeWeave.Query.SqlExpression{System.String},System.String)`

```csharp
public static NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlStringExtensions.ContainsNullableLiteral(this NativeWeave.Query.SqlExpression<string?> expression, string value)
```

**summary:** Escapes literal wildcard characters and searches nullable SQL text.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.SqlStringExtensions.EndsWithLiteral(NativeWeave.Query.SqlExpression{System.String},System.String)`

```csharp
public static NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlStringExtensions.EndsWithLiteral(this NativeWeave.Query.SqlExpression<string> expression, string value)
```

**summary:** Escapes wildcard characters and binds a literal suffix pattern.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.SqlStringExtensions.Like(NativeWeave.Query.SqlExpression{System.String},System.String,System.Char)`

```csharp
public static NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlStringExtensions.Like(this NativeWeave.Query.SqlExpression<string> expression, string pattern, char escape = '\\')
```

**summary:** Binds the supplied raw SQL LIKE pattern with an explicit escape character.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param pattern:** An explicit SQL LIKE pattern; percent and underscore retain wildcard meaning.

**param escape:** The explicit single escape character for the SQL LIKE pattern.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.SqlStringExtensions.LikeNullable(NativeWeave.Query.SqlExpression{System.String},System.String,System.Char)`

```csharp
public static NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlStringExtensions.LikeNullable(this NativeWeave.Query.SqlExpression<string?> expression, string pattern, char escape = '\\')
```

**summary:** Uses an explicit raw LIKE pattern against nullable SQL text.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param pattern:** An explicit SQL LIKE pattern; percent and underscore retain wildcard meaning.

**param escape:** The explicit single escape character for the SQL LIKE pattern.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.SqlStringExtensions.StartsWithLiteral(NativeWeave.Query.SqlExpression{System.String},System.String)`

```csharp
public static NativeWeave.Query.SqlPredicate NativeWeave.Query.SqlStringExtensions.StartsWithLiteral(this NativeWeave.Query.SqlExpression<string> expression, string value)
```

**summary:** Escapes wildcard characters and binds a literal prefix pattern.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**returns:** A same-query borrowed native predicate token with SQL three-valued semantics.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `M:NativeWeave.Query.UpdateSetters`1.Set``1(NativeWeave.Data.Column{`0,``0},NativeWeave.Query.SqlExpression{``0})`

```csharp
public NativeWeave.Query.UpdateSetters<TEntity> NativeWeave.Query.UpdateSetters<TEntity>.Set<T>(NativeWeave.Data.Column<TEntity, T> column, NativeWeave.Query.SqlExpression<T> value)
```

**summary:** Stages a compatible same-query expression; assignments attach only after the callback succeeds.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** The owner is valid only during the synchronous update callback. Each scalar is snapshotted immediately; duplicate, generated and primary-key assignments reject. Assignment clauses attach after callback success; no tracked entity or managed SQL expression tree is created.

## `M:NativeWeave.Query.UpdateSetters`1.Set``1(NativeWeave.Data.Column{`0,``0},``0)`

```csharp
public NativeWeave.Query.UpdateSetters<TEntity> NativeWeave.Query.UpdateSetters<TEntity>.Set<T>(NativeWeave.Data.Column<TEntity, T> column, T value)
```

**summary:** Copies a typed value for a nonkey, nongenerated root-column assignment.

**inheritdoc:**

**param column:** The strongly typed column from the declared table; foreign table identities reject.

**param value:** The typed value to snapshot now, or the compatible same-query native expression.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** The owner is valid only during the synchronous update callback. Each scalar is snapshotted immediately; duplicate, generated and primary-key assignments reject. Assignment clauses attach after callback success; no tracked entity or managed SQL expression tree is created.

## `M:NativeWeave.Query.WindowDefinition.OrderBy``1(NativeWeave.Query.SqlExpression{``0},NativeWeave.Query.SortDirection,NativeWeave.Query.NullOrder)`

```csharp
public NativeWeave.Query.WindowDefinition NativeWeave.Query.WindowDefinition.OrderBy<T>(NativeWeave.Query.SqlExpression<T> expression, NativeWeave.Query.SortDirection direction = NativeWeave.Query.SortDirection.Ascending, NativeWeave.Query.NullOrder nullOrder = NativeWeave.Query.NullOrder.Last)
```

**summary:** Appends native ordering with explicit direction and SQL NULL placement.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**param direction:** Explicit ascending or descending SQL order.

**param nullOrder:** Explicit placement of SQL NULL values in this ordering key.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** The owning query bounds lifetime and concurrent access. Rank, RowNumber and Over snapshot native window state immediately; subsequent mutation cannot change existing expressions. Defaults and limits follow the provider capability contract.

## `M:NativeWeave.Query.WindowDefinition.PartitionBy``1(NativeWeave.Query.SqlExpression{``0})`

```csharp
public NativeWeave.Query.WindowDefinition NativeWeave.Query.WindowDefinition.PartitionBy<T>(NativeWeave.Query.SqlExpression<T> expression)
```

**summary:** Appends a same-query native partition expression.

**inheritdoc:**

**param expression:** The compatible native scalar owned by the same live query.

**typeparam T:** The statically known CLR value or owned result type with the exact declared codec/nullability.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** The owning query bounds lifetime and concurrent access. Rank, RowNumber and Over snapshot native window state immediately; subsequent mutation cannot change existing expressions. Defaults and limits follow the provider capability contract.

## `M:NativeWeave.Query.WindowDefinition.RowsBetween(NativeWeave.Query.FrameBoundary,NativeWeave.Query.FrameBoundary)`

```csharp
public NativeWeave.Query.WindowDefinition NativeWeave.Query.WindowDefinition.RowsBetween(NativeWeave.Query.FrameBoundary start, NativeWeave.Query.FrameBoundary end)
```

**summary:** Sets one supported ROWS frame; invalid endpoints reject before publication.

**inheritdoc:**

**param start:** The supported starting ROWS frame endpoint.

**param end:** The supported ending ROWS frame endpoint.

**returns:** The typed owner or proxy described above, retaining its original source/query association.

**exception:** An argument, owner association or codec/nullability is incompatible.

**exception:** The owner, projection or one-shot terminal is in an invalid state.

**exception:** The required native owner or its parent has closed admission.

**exception:** Native capability, finite resource limits or provider execution rejects the operation.

**Inherited type policy:** The owning query bounds lifetime and concurrent access. Rank, RowNumber and Over snapshot native window state immediately; subsequent mutation cannot change existing expressions. Defaults and limits follow the provider capability contract.

## `P:NativeWeave.Database.BulkOptions.Atomicity`

```csharp
public NativeWeave.Database.BulkAtomicity NativeWeave.Database.BulkOptions.Atomicity { get; init; }
```

**summary:** Gets the atomicity policy; whole-operation atomicity is the default.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `P:NativeWeave.Database.BulkOptions.BatchSize`

```csharp
public int NativeWeave.Database.BulkOptions.BatchSize { get; init; }
```

**summary:** Gets the requested positive maximum rows per batch; byte, node and parameter limits can lower it.

**Inherited type policy:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `P:NativeWeave.Database.BulkProgress.CompletedBatches`

```csharp
public int NativeWeave.Database.BulkProgress.CompletedBatches { get; init; }
```

**summary:** The fully acknowledged batch count.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `P:NativeWeave.Database.BulkProgress.CompletedBatchesCommitted`

```csharp
public bool NativeWeave.Database.BulkProgress.CompletedBatchesCommitted { get; init; }
```

**summary:** True only for confirmed preceding PerBatch commits.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `P:NativeWeave.Database.BulkProgress.CurrentTransactionOutcome`

```csharp
public NativeWeave.Database.TransactionOutcome NativeWeave.Database.BulkProgress.CurrentTransactionOutcome { get; init; }
```

**summary:** Actual transaction knowledge, retaining Unknown independently.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `P:NativeWeave.Database.BulkProgress.RowsAffectedInCompletedBatches`

```csharp
public long NativeWeave.Database.BulkProgress.RowsAffectedInCompletedBatches { get; init; }
```

**summary:** Affected rows only in fully acknowledged preceding batches.

**Inherited type policy:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `P:NativeWeave.Database.BulkResult.Batches`

```csharp
public int NativeWeave.Database.BulkResult.Batches { get; init; }
```

**summary:** The number of fully acknowledged batches.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `P:NativeWeave.Database.BulkResult.CommittedByOperation`

```csharp
public bool NativeWeave.Database.BulkResult.CommittedByOperation { get; init; }
```

**summary:** True only when this operation confirmed its own commit or commits.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `P:NativeWeave.Database.BulkResult.RowsAffected`

```csharp
public long NativeWeave.Database.BulkResult.RowsAffected { get; init; }
```

**summary:** The sum of acknowledged provider counts.

**Inherited type policy:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `P:NativeWeave.Database.DataSession.Cleanup`

```csharp
public NativeWeave.Database.DatabaseCloseResult NativeWeave.Database.DataSession.Cleanup { get; }
```

**summary:** Gets the current cleanup observation, retained after disposal.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `P:NativeWeave.Database.DataSession.Source`

```csharp
public NativeWeave.Database.DataSource NativeWeave.Database.DataSession.Source { get; }
```

**summary:** Gets the creating data source, retained while this physical session remains owned.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `P:NativeWeave.Database.DataSession.Transaction`

```csharp
public NativeWeave.Database.DataTransaction? NativeWeave.Database.DataSession.Transaction { get; }
```

**summary:** Gets the last active transaction, or null after its native state has closed.

**Inherited type policy:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `P:NativeWeave.Database.DataSource.Administration`

```csharp
public NativeWeave.Database.DatabaseAdministration NativeWeave.Database.DataSource.Administration { get; }
```

**summary:** Gets the explicit administration facade without opening a database connection.

**remarks:** Each operation owns a separate, bounded administrative connection. Source creation and DI activation never apply migrations. Private in-memory SQLite cannot expose a separate administrative connection.

**exception:** Source admission is closed.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `P:NativeWeave.Database.DataSource.Capabilities`

```csharp
public NativeWeave.Database.DatabaseCapabilities NativeWeave.Database.DataSource.Capabilities { get; }
```

**summary:** Gets the actual negotiated provider capability snapshot.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `P:NativeWeave.Database.DataSource.Cleanup`

```csharp
public NativeWeave.Database.DatabaseCloseResult NativeWeave.Database.DataSource.Cleanup { get; }
```

**summary:** Gets the current cleanup observation, retained after disposal.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `P:NativeWeave.Database.DataSource.Limits`

```csharp
public NativeWeave.Database.DatabaseLimits NativeWeave.Database.DataSource.Limits { get; }
```

**summary:** Gets the immutable source limits.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `P:NativeWeave.Database.DataSource.Name`

```csharp
public string NativeWeave.Database.DataSource.Name { get; }
```

**summary:** Gets the immutable noncredential diagnostic name.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `P:NativeWeave.Database.DataSource.Provider`

```csharp
public NativeWeave.Database.DatabaseProvider NativeWeave.Database.DataSource.Provider { get; }
```

**summary:** Gets the selected native provider.

**Inherited type policy:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `P:NativeWeave.Database.DatabaseCapabilities.Names`

```csharp
public System.Collections.Generic.IReadOnlyList<string> NativeWeave.Database.DatabaseCapabilities.Names { get; }
```

**summary:** Gets the immutable ordinal capability-name snapshot.

**Inherited type policy:** Unknown names return false. A capability name does not authorize a different provider or an arbitrary SQL feature.

## `P:NativeWeave.Database.DatabaseCapabilities.Profile`

```csharp
public string NativeWeave.Database.DatabaseCapabilities.Profile { get; }
```

**summary:** Gets the stable selected semantic profile.

**Inherited type policy:** Unknown names return false. A capability name does not authorize a different provider or an arbitrary SQL feature.

## `P:NativeWeave.Database.DatabaseCapabilities.Provider`

```csharp
public NativeWeave.Database.DatabaseProvider NativeWeave.Database.DatabaseCapabilities.Provider { get; }
```

**summary:** Gets the selected provider.

**Inherited type policy:** Unknown names return false. A capability name does not authorize a different provider or an arbitrary SQL feature.

## `P:NativeWeave.Database.DatabaseLimits.AdmissionTimeout`

```csharp
public System.TimeSpan NativeWeave.Database.DatabaseLimits.AdmissionTimeout { get; init; }
```

**summary:** Gets the positive finite pool admission timeout; defaults to fifteen seconds.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.CommandTimeout`

```csharp
public System.TimeSpan NativeWeave.Database.DatabaseLimits.CommandTimeout { get; init; }
```

**summary:** Gets the positive default total command timeout; defaults to thirty seconds.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxBatchBytes`

```csharp
public long NativeWeave.Database.DatabaseLimits.MaxBatchBytes { get; init; }
```

**summary:** Gets the entire encoded batch budget including descriptors; defaults to 1 MiB.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxBatchRows`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxBatchRows { get; init; }
```

**summary:** Gets the maximum rows in one transferred batch; defaults to 256.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxBufferedBytes`

```csharp
public long NativeWeave.Database.DatabaseLimits.MaxBufferedBytes { get; init; }
```

**summary:** Gets the buffered encoded-byte budget; defaults to 16 MiB. Zero prohibits buffered demand.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxBufferedRows`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxBufferedRows { get; init; }
```

**summary:** Gets the maximum buffered result rows; defaults to 10,000. Zero prohibits buffered demand.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxConnections`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxConnections { get; init; }
```

**summary:** Gets the maximum simultaneous physical sessions; defaults to 32.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxFieldBytes`

```csharp
public long NativeWeave.Database.DatabaseLimits.MaxFieldBytes { get; init; }
```

**summary:** Gets the general field byte limit; defaults to 8 MiB. An inline field must also fit its batch.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxParameterBytes`

```csharp
public long NativeWeave.Database.DatabaseLimits.MaxParameterBytes { get; init; }
```

**summary:** Gets the total encoded parameter budget; defaults to 4 MiB.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxParameters`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxParameters { get; init; }
```

**summary:** Gets the maximum typed parameters per operation; defaults to 999.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxPreparedPlanBytes`

```csharp
public long NativeWeave.Database.DatabaseLimits.MaxPreparedPlanBytes { get; init; }
```

**summary:** Gets the source-owned prepared shape byte limit; defaults to 8 MiB.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxPreparedPlans`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxPreparedPlans { get; init; }
```

**summary:** Gets the source-owned prepared shape entry limit; defaults to 128.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxQueryDepth`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxQueryDepth { get; init; }
```

**summary:** Gets the maximum native query depth; defaults to 64.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxQueryNodes`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxQueryNodes { get; init; }
```

**summary:** Gets the maximum query and registration nodes; defaults to 4,096.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.DatabaseLimits.MaxWaiters`

```csharp
public int NativeWeave.Database.DatabaseLimits.MaxWaiters { get; init; }
```

**summary:** Gets the maximum bounded session waiters; defaults to 128.

**Inherited type policy:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `P:NativeWeave.Database.Migration.Description`

```csharp
public string NativeWeave.Database.Migration.Description { get; init; }
```

**summary:** A nonempty diagnostic description without credentials.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `P:NativeWeave.Database.Migration.Sql`

```csharp
public string NativeWeave.Database.Migration.Sql { get; init; }
```

**summary:** Exact Unicode SQL; UTF-8 bytes are checksummed without newline normalization.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `P:NativeWeave.Database.Migration.TransactionMode`

```csharp
public NativeWeave.Database.MigrationTransactionMode NativeWeave.Database.Migration.TransactionMode { get; init; }
```

**summary:** Transactional by default; explicit transaction-control statements are rejected.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `P:NativeWeave.Database.Migration.Version`

```csharp
public long NativeWeave.Database.Migration.Version { get; init; }
```

**summary:** A positive version, strictly ascending within its bundle.

**Inherited type policy:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

## `P:NativeWeave.Database.MigrationBundle.ContentHash`

```csharp
public string NativeWeave.Database.MigrationBundle.ContentHash { get; }
```

**summary:** Gets the lowercase SHA-256 of the canonical provider and immutable entry sequence.

**Inherited type policy:** Construction performs no native load or database I/O. Its SHA-256 identity covers the canonical kind12 provider and entry sequence before the hash field is added. Each entry separately contains SQL SHA-256; the native SQLx ledger retains SQLx's own SHA-384 checksum. Scripts must be trusted deployment artifacts.

## `P:NativeWeave.Database.MigrationOptions.AllowNonTransactional`

```csharp
public bool NativeWeave.Database.MigrationOptions.AllowNonTransactional { get; init; }
```

**summary:** Gets whether explicitly nontransactional PostgreSQL entries may execute or be resumed.

**remarks:** A new call is explicit replay of the identical script after an unfinished phase. The script must handle any previously completed effects. NativeWeave never retries a write within the call.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `P:NativeWeave.Database.MigrationOptions.LockTimeout`

```csharp
public System.TimeSpan NativeWeave.Database.MigrationOptions.LockTimeout { get; init; }
```

**summary:** Gets the positive finite administrative writer/advisory-lock wait, defaulting to thirty seconds.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `P:NativeWeave.Database.MigrationOptions.TargetVersion`

```csharp
public long? NativeWeave.Database.MigrationOptions.TargetVersion { get; init; }
```

**summary:** Gets the last version eligible for forward application; null selects the complete bundle.

**remarks:** A value below the applied current version is rejected; no downgrade is performed.

**Inherited type policy:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `P:NativeWeave.Database.MigrationReport.AppliedCount`

```csharp
public int NativeWeave.Database.MigrationReport.AppliedCount { get; init; }
```

**summary:** The number applied by this invocation.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `P:NativeWeave.Database.MigrationReport.Completed`

```csharp
public bool NativeWeave.Database.MigrationReport.Completed { get; init; }
```

**summary:** True on success; failures throw and retain their original error.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `P:NativeWeave.Database.MigrationReport.CurrentVersion`

```csharp
public long? NativeWeave.Database.MigrationReport.CurrentVersion { get; init; }
```

**summary:** The last confirmed applied version, or null for an empty database.

**Inherited type policy:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

## `P:NativeWeave.Database.MigrationStatus.Applied`

```csharp
public bool NativeWeave.Database.MigrationStatus.Applied { get; init; }
```

**summary:** True only when the successful SQLx ledger contains this exact migration.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `P:NativeWeave.Database.MigrationStatus.Checksum`

```csharp
public string NativeWeave.Database.MigrationStatus.Checksum { get; init; }
```

**summary:** The lowercase hexadecimal SQLx SHA-384 checksum, distinct from the bundle hash.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `P:NativeWeave.Database.MigrationStatus.Description`

```csharp
public string NativeWeave.Database.MigrationStatus.Description { get; init; }
```

**summary:** The immutable bundle description.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `P:NativeWeave.Database.MigrationStatus.Version`

```csharp
public long NativeWeave.Database.MigrationStatus.Version { get; init; }
```

**summary:** The positive migration version.

**Inherited type policy:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

## `P:NativeWeave.Database.SchemaColumn.IsNullable`

```csharp
public bool NativeWeave.Database.SchemaColumn.IsNullable { get; init; }
```

**summary:** Whether the provider permits SQL NULL.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `P:NativeWeave.Database.SchemaColumn.IsPrimaryKey`

```csharp
public bool NativeWeave.Database.SchemaColumn.IsPrimaryKey { get; init; }
```

**summary:** Whether the column participates in a primary key.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `P:NativeWeave.Database.SchemaColumn.Name`

```csharp
public string NativeWeave.Database.SchemaColumn.Name { get; init; }
```

**summary:** The exact store column name.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `P:NativeWeave.Database.SchemaColumn.StoreType`

```csharp
public string NativeWeave.Database.SchemaColumn.StoreType { get; init; }
```

**summary:** The provider's declared/formatted type.

**Inherited type policy:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

## `P:NativeWeave.Database.SchemaTable.Columns`

```csharp
public System.Collections.Generic.IReadOnlyList<NativeWeave.Database.SchemaColumn> NativeWeave.Database.SchemaTable.Columns { get; init; }
```

**summary:** The bounded columns in native catalog ordinal order.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `P:NativeWeave.Database.SchemaTable.Name`

```csharp
public string NativeWeave.Database.SchemaTable.Name { get; init; }
```

**summary:** The exact table name.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `P:NativeWeave.Database.SchemaTable.Schema`

```csharp
public string? NativeWeave.Database.SchemaTable.Schema { get; init; }
```

**summary:** The admitted provider schema; SQLite reports main.

**Inherited type policy:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

## `P:NativeWeave.Query.Query`1.Row`

```csharp
public NativeWeave.Query.QueryRow<TEntity> NativeWeave.Query.Query<TEntity>.Row { get; }
```

**summary:** Gets the live typed root-column proxy.

**inheritdoc:**

**Inherited type policy:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `T:NativeWeave.Database.BulkAtomicity`

```csharp
public enum NativeWeave.Database.BulkAtomicity : int
```

**summary:** Selects whole-operation atomicity or explicitly independent committed batches.

## `T:NativeWeave.Database.BulkFailure`

```csharp
public static class NativeWeave.Database.BulkFailure
```

**summary:** Reads immutable bulk progress without replacing or wrapping the original exception.

**remarks:** The helper reads one exact typed Exception.Data entry without native calls, allocation of a wrapper, recursive error traversal or inference from cancellation. The returned snapshot can outlive all native owners.

## `T:NativeWeave.Database.BulkOptions`

```csharp
public sealed record class NativeWeave.Database.BulkOptions : System.IEquatable<NativeWeave.Database.BulkOptions>
```

**summary:** Immutable finite input batching and explicit transaction ownership policy.

**remarks:** This managed configuration owns no native resource. A bulk operation reads its immutable values at admission, then lowers the requested row count to source byte, node and parameter limits.

## `T:NativeWeave.Database.BulkProgress`

```csharp
public sealed record class NativeWeave.Database.BulkProgress : System.IEquatable<NativeWeave.Database.BulkProgress>
```

**summary:** Immutable progress at failure, distinct from uncertain current-batch effects or later rollback.

**param RowsAffectedInCompletedBatches:** Affected rows only in fully acknowledged preceding batches.

**param CompletedBatches:** The fully acknowledged batch count.

**param CompletedBatchesCommitted:** True only for confirmed preceding PerBatch commits.

**param CurrentTransactionOutcome:** Actual transaction knowledge, retaining Unknown independently.

**remarks:** The original admitted bulk exception retains this managed snapshot after cleanup. Counts describe previously completed batches, which All may have rolled back; they do not prove current-batch effects or authorize replay. The record owns no native resource and remains readable after session/source disposal.

## `T:NativeWeave.Database.BulkResult`

```csharp
public sealed record class NativeWeave.Database.BulkResult : System.IEquatable<NativeWeave.Database.BulkResult>
```

**summary:** The acknowledged result of all admitted batches.

**param RowsAffected:** The sum of acknowledged provider counts.

**param Batches:** The number of fully acknowledged batches.

**param CommittedByOperation:** True only when this operation confirmed its own commit or commits.

**remarks:** The owned immutable result contains only acknowledged counts and an ownership observation. Constructing it allocates one managed record; it retains no session, transaction, cursor or native buffer.

## `T:NativeWeave.Database.ConflictTarget`1`

```csharp
public sealed class NativeWeave.Database.ConflictTarget<TEntity> where TEntity : class
```

**summary:** An immutable explicit unique-column or PostgreSQL constraint target for one atomic upsert.

**typeparam TEntity:** The statically described entity class.

**remarks:** Construction performs no schema query. The native database checks that the selected unique constraint exists.

## `T:NativeWeave.Database.DataSession`

```csharp
public sealed class NativeWeave.Database.DataSession : System.IDisposable, System.IAsyncDisposable
```

**summary:** Owns one physical native session with fail-fast single-command admission.

**remarks:** A cursor and transaction control retain the same session gate. A session is not a concurrent command queue. Every query maps synchronously into owned CLR values and joins cleanup before its public Task completes.

## `T:NativeWeave.Database.DataSource`

```csharp
public sealed class NativeWeave.Database.DataSource : System.IDisposable, System.IAsyncDisposable
```

**summary:** Owns one lazy Rust pool, bounded runtime and source-generation metadata registry.

**remarks:** Sources support concurrent independent session opens. Closing rejects new work and retains every admitted native operation until real retirement. Dispose requests cleanup; DisposeAsync joins local safety.

## `T:NativeWeave.Database.DataSourceBuilder`

```csharp
public sealed class NativeWeave.Database.DataSourceBuilder
```

**summary:** A single-writer builder for one explicitly selected native database engine.

**remarks:** Configuration snapshots values. Build negotiates the packaged module and creates a lazy native pool; it opens no database connection. Independent builds create independent source generations.

## `T:NativeWeave.Database.DatabaseAdministration`

```csharp
public sealed class NativeWeave.Database.DatabaseAdministration
```

**summary:** Runs explicit trusted migration and catalog operations through the native provider.

**remarks:** One independent administrative connection executes at a time per source, with bounded waiting. Every outcome closes that connection before task retirement. It never uses a request session or request transaction. Result counts, strings and nested columns are charged to source buffering and field limits.

## `T:NativeWeave.Database.DatabaseCapabilities`

```csharp
public sealed class NativeWeave.Database.DatabaseCapabilities
```

**summary:** An immutable snapshot of the capabilities actually negotiated for this provider module.

**remarks:** Unknown names return false. A capability name does not authorize a different provider or an arbitrary SQL feature.

## `T:NativeWeave.Database.DatabaseLimits`

```csharp
public sealed record class NativeWeave.Database.DatabaseLimits : System.IEquatable<NativeWeave.Database.DatabaseLimits>
```

**summary:** Immutable finite limits snapshotted by a data source before native creation.

**remarks:** These are admission and encoded-byte budgets, not measurements of CLR heap or process memory. Provider hard limits also apply. Increasing a value never selects an unbounded fallback.

## `T:NativeWeave.Database.DatabaseProvider`

```csharp
public enum NativeWeave.Database.DatabaseProvider : int
```

**summary:** The selected independently packaged Rust database provider.

## `T:NativeWeave.Database.Migration`

```csharp
public sealed record class NativeWeave.Database.Migration : System.IEquatable<NativeWeave.Database.Migration>
```

**summary:** Defines one trusted, immutable SQL migration.

**remarks:** This record retains its strings without native resources. Bundle construction snapshots the collection and performs bounded UTF-8 encoding and hashing; execution is explicit.

**param Version:** A positive version, strictly ascending within its bundle.

**param Description:** A nonempty diagnostic description without credentials.

**param Sql:** Exact Unicode SQL; UTF-8 bytes are checksummed without newline normalization.

**param TransactionMode:** Transactional by default; explicit transaction-control statements are rejected.

## `T:NativeWeave.Database.MigrationBundle`

```csharp
public sealed class NativeWeave.Database.MigrationBundle
```

**summary:** Snapshots a strictly ordered, provider-bound set of explicit SQL scripts.

**remarks:** Construction performs no native load or database I/O. Its SHA-256 identity covers the canonical kind12 provider and entry sequence before the hash field is added. Each entry separately contains SQL SHA-256; the native SQLx ledger retains SQLx's own SHA-384 checksum. Scripts must be trusted deployment artifacts.

## `T:NativeWeave.Database.MigrationOptions`

```csharp
public sealed record class NativeWeave.Database.MigrationOptions : System.IEquatable<NativeWeave.Database.MigrationOptions>
```

**summary:** Controls one explicit forward migration call.

**remarks:** This immutable managed value owns no connection or native resources. An administrative call snapshots its scalar settings before admission.

## `T:NativeWeave.Database.MigrationReport`

```csharp
public sealed record class NativeWeave.Database.MigrationReport : System.IEquatable<NativeWeave.Database.MigrationReport>
```

**summary:** Reports a successfully completed explicit migration call.

**remarks:** This detached managed value owns no native resource. The administrative connection has retired before task completion; earlier confirmed entries remain committed independently on PostgreSQL.

**param AppliedCount:** The number applied by this invocation.

**param CurrentVersion:** The last confirmed applied version, or null for an empty database.

**param Completed:** True on success; failures throw and retain their original error.

## `T:NativeWeave.Database.MigrationStatus`

```csharp
public sealed record class NativeWeave.Database.MigrationStatus : System.IEquatable<NativeWeave.Database.MigrationStatus>
```

**summary:** Describes one bounded immutable bundle/ledger comparison.

**remarks:** This detached managed record owns its immutable strings. Native result buffers are released before the task returns; the source bounds aggregate record and UTF-8 byte costs.

**param Version:** The positive migration version.

**param Description:** The immutable bundle description.

**param Checksum:** The lowercase hexadecimal SQLx SHA-384 checksum, distinct from the bundle hash.

**param Applied:** True only when the successful SQLx ledger contains this exact migration.

## `T:NativeWeave.Database.MigrationTransactionMode`

```csharp
public enum NativeWeave.Database.MigrationTransactionMode : int
```

**summary:** Selects SQLx transactional execution or explicitly resumable PostgreSQL execution.

## `T:NativeWeave.Database.SchemaColumn`

```csharp
public sealed record class NativeWeave.Database.SchemaColumn : System.IEquatable<NativeWeave.Database.SchemaColumn>
```

**summary:** Describes a provider catalog column without exposing a provider row object.

**remarks:** This detached immutable record retains its names and type strings. Each column counts toward the same source result-row and encoded-byte limits as its parent table.

**param Name:** The exact store column name.

**param StoreType:** The provider's declared/formatted type.

**param IsNullable:** Whether the provider permits SQL NULL.

**param IsPrimaryKey:** Whether the column participates in a primary key.

## `T:NativeWeave.Database.SchemaTable`

```csharp
public sealed record class NativeWeave.Database.SchemaTable : System.IEquatable<NativeWeave.Database.SchemaTable>
```

**summary:** Describes a table and an immutable, ordinally ordered column snapshot.

**remarks:** Administration returns a detached read-only column list with no native lease. Table names and all nested columns share the source buffering budget; no further database access is lazy.

**param Schema:** The admitted provider schema; SQLite reports main.

**param Name:** The exact table name.

**param Columns:** The bounded columns in native catalog ordinal order.

## `T:NativeWeave.Query.CommonTable`1`

```csharp
public sealed class NativeWeave.Query.CommonTable<T> : System.IDisposable where T : class
```

**summary:** A frozen native CTE with an explicit declared row shape and source identity.

**typeparam T:** The declared CTE row class.

**remarks:** The snapshot is bound to one source and a declared static row shape. With imports a native retained reference. Disposal prevents new imports and does not mutate previously imported snapshots. Recursive creation requires one validated anchor/member self-reference.

## `T:NativeWeave.Query.FrameBoundary`

```csharp
public enum NativeWeave.Query.FrameBoundary : int
```

**summary:** Supported finite window-frame endpoint choices.

**remarks:** Only these ROWS endpoints are supported. Reversed or unsupported bounds fail before native state publication; finite numeric PRECEDING/FOLLOWING frames are not declared.

## `T:NativeWeave.Query.JoinPredicate`2`

```csharp
public readonly struct NativeWeave.Query.JoinPredicate<TLeft, TRight> where TLeft : class where TRight : class
```

**summary:** A synchronous native JOIN ON proxy; both sides retain their declared nullability.

**typeparam TLeft:** The root entity class.

**typeparam TRight:** The explicitly joined entity class.

**remarks:** Use only inside the synchronous JOIN callback. Provisional right-side expressions are invalidated on commit or abort. Values and nullability stay exact; explicitly lift a non-null parent key to compare a nullable foreign key.

## `T:NativeWeave.Query.JoinedTable`1`

```csharp
public readonly struct NativeWeave.Query.JoinedTable<TEntity> where TEntity : class
```

**summary:** An opaque inner-join alias belonging to exactly one native query and table.

**typeparam TEntity:** The joined entity class.

**remarks:** The alias is a borrowed token, not an independently disposable query. Default aliases and aliases from another query reject, even if the CLR entity type matches.

## `T:NativeWeave.Query.LeftJoinedTable`1`

```csharp
public readonly struct NativeWeave.Query.LeftJoinedTable<TEntity> where TEntity : class
```

**summary:** An opaque left-join alias whose projected columns require explicit nullable reads.

**typeparam TEntity:** The joined entity class.

**remarks:** Use NullableValue or NullableReference to project its columns and HasMatch to distinguish absence. No default scalar sentinel or implicit object graph is introduced. Its query owns the alias lifetime.

## `T:NativeWeave.Query.LockWait`

```csharp
public enum NativeWeave.Query.LockWait : int
```

**summary:** PostgreSQL row-lock conflict behavior.

**remarks:** Controls PostgreSQL row-lock conflicts within the same transaction and total query deadline; it does not enable transparent retries.

## `T:NativeWeave.Query.NullOrder`

```csharp
public enum NativeWeave.Query.NullOrder : int
```

**summary:** Explicit SQL NULL placement.

**remarks:** Both providers render explicit SQL NULL placement. Ordering alone supplies no uniqueness or snapshot guarantee.

## `T:NativeWeave.Query.PreparedQuery`1`

```csharp
public sealed class NativeWeave.Query.PreparedQuery<T> : System.IDisposable
```

**summary:** An immutable source-bound native query plan with independent execution values and cursor owners.

**typeparam T:** The owned static result type.

**remarks:** Concurrent execution uses separate sessions from the same source. Disposing prevents new dispatch; accepted native operations retain their plan independently and complete safely.

## `T:NativeWeave.Query.ProjectionBuilder`1`

```csharp
public sealed class NativeWeave.Query.ProjectionBuilder<T>
```

**summary:** A query-scoped static projection builder that freezes typed result tokens and a direct constructor.

**typeparam T:** The statically known owned result type.

**remarks:** Fields must come from its exact live query. Build freezes field order, unique names, codec/nullability and the direct materializer; later Add or Build rejects. RowReader validates the full shape before the callback, and escaping DTO values own their data.

## `T:NativeWeave.Query.QueryParameter`1`

```csharp
public readonly struct NativeWeave.Query.QueryParameter<T>
```

**summary:** An immutable source-generation parameter identity, distinct from a query-arena expression.

**typeparam T:** The exact statically encoded parameter type.

**remarks:** Parameter IDs are monotonically allocated within a source generation, independently of query expression tokens. A copied parameter remains an identity; it owns no native arena or value, and only declared/imported plans may execute it.

## `T:NativeWeave.Query.QueryParameters`

```csharp
public sealed class NativeWeave.Query.QueryParameters
```

**summary:** A finite explicit parameter set; each Set copies its value and each execution takes a separate snapshot.

**remarks:** Set snapshots each encoded value before returning. A terminal copies the complete finite set before its first await; later Set calls do not change admitted execution. Missing, extra, foreign or codec-incompatible identities reject before native dispatch. No global parameter dictionary exists.

## `T:NativeWeave.Query.QueryRow`1`

```csharp
public readonly struct NativeWeave.Query.QueryRow<TEntity> where TEntity : class
```

**summary:** A stack-independent typed root-table proxy that belongs to one live native query.

**typeparam TEntity:** The declared root entity class.

**remarks:** This borrowed proxy retains its query association. Default, foreign, closed or sealed owners reject. Each operation forwards immediately to a finite native arena; no managed SQL tree or captured callback is retained.

## `T:NativeWeave.Query.QuerySelection`1`

```csharp
public readonly struct NativeWeave.Query.QuerySelection<T>
```

**summary:** A borrowed typed view of a native query's current selection; it owns no second arena.

**typeparam T:** The statically materialized owned result type.

**remarks:** This borrowed view is valid only while its projection remains current in the live query. The first execution or Prepare seals the owner synchronously. Dispose the owning query after enumeration; early exit, failure and cancellation await actual native retirement.

## `T:NativeWeave.Query.Query`1`

```csharp
public sealed class NativeWeave.Query.Query<TEntity> : System.IDisposable where TEntity : class
```

**summary:** One mutable, source-bound native SeaQuery arena with a strongly typed application facade.

**typeparam TEntity:** The explicitly described root entity class.

**remarks:** Composition is synchronous and fail-fast on concurrent writers. The first terminal seals the query; use Clone before a second execution. Keep this owner alive across streaming and dispose after use.

## `T:NativeWeave.Query.RowLockMode`

```csharp
public enum NativeWeave.Query.RowLockMode : int
```

**summary:** PostgreSQL row lock strength requiring an explicit transaction.

**remarks:** Available only on PostgreSQL with an explicit live transaction. SQLite rejects the operation before provider dispatch.

## `T:NativeWeave.Query.SetOperation`

```csharp
public enum NativeWeave.Query.SetOperation : int
```

**summary:** Native SQL set operation with exact compatible projection types.

**remarks:** Operands must have the same source, field order, aliases, codecs and nullability. Rust snapshots the right operand; SQL duplicate and NULL semantics apply.

## `T:NativeWeave.Query.SortDirection`

```csharp
public enum NativeWeave.Query.SortDirection : int
```

**summary:** Native SQL ordering direction.

**remarks:** The native query validates each enum value before mutation. Direction is explicit; it does not change SQL NULL ordering.

## `T:NativeWeave.Query.SqlArithmeticExtensions`

```csharp
public static class NativeWeave.Query.SqlArithmeticExtensions
```

**summary:** Statically numeric native SQL arithmetic; overflow, precision and division remain provider semantics.

**remarks:** Operators require compatible same-query numeric codecs and preserve declared SQL NULL propagation. Rust owns provider arithmetic and checked result conversion; unsupported codecs fail explicitly. No CLR arithmetic delegate is executed for database rows.

## `T:NativeWeave.Query.SqlExpression`1`

```csharp
public readonly struct NativeWeave.Query.SqlExpression<T>
```

**summary:** An opaque query-owned scalar token with its exact static codec and SQL nullability.

**typeparam T:** The statically known value type.

**remarks:** No SQL tree or delegate is retained. Values are snapshotted immediately; default and foreign tokens reject.

## `T:NativeWeave.Query.SqlFunctions`

```csharp
public static class NativeWeave.Query.SqlFunctions
```

**summary:** Static typed native aggregates, ranking and conditional scalar composition.

**remarks:** SQL NULL, collation, overflow and conversion semantics remain explicit provider behavior.

## `T:NativeWeave.Query.SqlNullabilityExtensions`

```csharp
public static class NativeWeave.Query.SqlNullabilityExtensions
```

**summary:** Explicit one-way SQL nullability lifts; no SQL cast, coalesce or new parameter is emitted.

**remarks:** These forward-only native metadata lifts preserve the SQL value and codec configuration. They do not emit a sentinel, COALESCE or reverse conversion. Default/foreign owners reject, and repeating a reference lift rejects its already nullable descriptor.

## `T:NativeWeave.Query.SqlPredicate`

```csharp
public readonly struct NativeWeave.Query.SqlPredicate
```

**summary:** An opaque same-query native SQL condition; default predicates reject.

**remarks:** Boolean composition uses SQL three-valued logic and performs one direct native operation.

## `T:NativeWeave.Query.SqlStringExtensions`

```csharp
public static class NativeWeave.Query.SqlStringExtensions
```

**summary:** Explicit SQL string pattern and allowlisted collation operations; no CLR culture comparison.

**remarks:** Literal-pattern methods snapshot and escape the supplied text before native SQL rendering; LikePattern deliberately accepts SQL wildcards. Collate resolves an exact provider allowlist, never arbitrary SQL. NULL behavior follows SQL three-valued logic.

## `T:NativeWeave.Query.UpdateSetters`1`

```csharp
public sealed class NativeWeave.Query.UpdateSetters<TEntity> where TEntity : class
```

**summary:** A callback-scoped typed assignment collector; scalar expressions are built natively immediately.

**typeparam TEntity:** The root entity class.

**remarks:** The owner is valid only during the synchronous update callback. Each scalar is snapshotted immediately; duplicate, generated and primary-key assignments reject. Assignment clauses attach after callback success; no tracked entity or managed SQL expression tree is created.

## `T:NativeWeave.Query.WindowDefinition`

```csharp
public sealed class NativeWeave.Query.WindowDefinition
```

**summary:** Finite mutable native window state; each Over/rank call snapshots its current definition.

**remarks:** The owning query bounds lifetime and concurrent access. Rank, RowNumber and Over snapshot native window state immediately; subsequent mutation cannot change existing expressions. Defaults and limits follow the provider capability contract.
