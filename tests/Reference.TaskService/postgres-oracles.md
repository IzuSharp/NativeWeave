# Independent PostgreSQL transaction oracles

These checks exercise the actual C# application methods and SQLx-backed Database Host using a bounded transparent PostgreSQL test proxy. The proxy preserves SQL, bind bytes and provider responses. It changes only dispatch scheduling or connection delivery, records backend PIDs and statement categories, and never records credentials, cancellation secrets or bound values.

## Conflicting idempotent operations

The fixed `--conflict-case` console scenario starts two calls to the existing `CreateAsync` method with the same scope, key and input. The proxy holds the winning transaction immediately before COMMIT reaches PostgreSQL. An independent psql connection must observe the other backend blocked by that exact winner through `pg_blocking_pids`, an ungranted `pg_locks` row and a real lock wait. This establishes the actual conflict before the barrier is released.

The losing `INSERT ... DO NOTHING RETURNING` must complete with `INSERT 0 0`. The next business statement must be a separate operations SELECT returning one row. The existing exact SQLx column-origin metadata query is allowed at most once before that SELECT and its hash is recorded. Both application calls must return identical durable replay bytes. Independent SQL must observe one operation, one item and one outbox event, with matching scope, request hash and identities.

## Lost COMMIT acknowledgment

The fixed `--unknown-case` scenario performs a create, identity-scoped recovery and same-key replay. The proxy forwards COMMIT to PostgreSQL, observes actual `CommandComplete(COMMIT)` followed by idle `ReadyForQuery`, then discards those frames and closes the connection. The initial application result must remain `outcome_unknown`, including its canonical recovery identity and persistent protection marker.

Independent psql must observe the committed operation/item/outbox singleton. Recovery must return its stored original bytes and the same-key create must replay those bytes without another effect. The proxy event record proves the failure happened after actual commit confirmation reached the proxy.

Neither check needs an HTTP listener. Historical durable semantic strings and response status numbers remain unchanged because they are part of the existing versioned persisted fixture format. Each run writes its own `result.json` and bounded event logs. An absent barrier, framing failure, timeout or mismatched independent SQL result is a failure.
