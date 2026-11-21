using NativeWeave.Database;

namespace NativeWeave.Reference.TaskService;

internal sealed partial class TaskService
{
    private readonly SemaphoreSlim _protectionSlots = new(32, 32);
    private readonly object _protectionGate = new();
    private readonly List<Task> _protectionTasks = [];

    private ProtectionReservation ReserveProtectionRetirement()
    {
        // Reserve before DB admission; finished native cleanup cannot admit unbounded filesystem continuations.
        if (!_protectionSlots.Wait(0)) throw new ApplicationProblem(503, "recovery_cleanup_capacity");
        return new(this);
    }

    private void TrackRetirement(DataTransaction transaction, Action removeConfirmedRollbackProtection)
    {
        // No request context, request token, body buffer or DI scope is retained.
        Task cleanup = RetireProtectionAsync(transaction, removeConfirmedRollbackProtection);
        lock (_protectionGate)
        {
            _protectionTasks.RemoveAll(task => task.IsCompleted);
            _protectionTasks.Add(cleanup);
        }
    }

    private async Task RetireProtectionAsync(DataTransaction transaction, Action removeConfirmedRollbackProtection)
    {
        try
        {
            await transaction.DisposeAsync().ConfigureAwait(false);
            if (transaction.Outcome == TransactionOutcome.RolledBack) removeConfirmedRollbackProtection();
        }
        catch (Exception error) { Console.Error.WriteLine("recovery_protection_retained type=" + error.GetType().Name); }
        finally { _protectionSlots.Release(); }
    }

    /// <summary>Called after fixture operations end and native source retirement joins, on every exit path.</summary>
    internal async Task JoinProtectionRetirementAsync()
    {
        while (true)
        {
            Task[] pending;
            lock (_protectionGate)
            {
                _protectionTasks.RemoveAll(task => task.IsCompleted);
                pending = _protectionTasks.ToArray();
            }
            if (pending.Length == 0) return;
            await Task.WhenAll(pending).ConfigureAwait(false);
        }
    }

    private sealed class ProtectionReservation(TaskService owner) : IDisposable
    {
        private TaskService? _owner = owner;

        internal void Transfer(DataTransaction transaction, Action removeConfirmedRollbackProtection)
        {
            TaskService current = Interlocked.Exchange(ref _owner, null)
                ?? throw new InvalidOperationException("Protection retirement ownership was transferred twice.");
            current.TrackRetirement(transaction, removeConfirmedRollbackProtection);
        }

        public void Dispose() => Interlocked.Exchange(ref _owner, null)?._protectionSlots.Release();
    }
}
