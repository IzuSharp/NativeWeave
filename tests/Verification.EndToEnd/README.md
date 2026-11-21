# Database end-to-end regression

This directory verifies the database product through ordinary C# package consumers. The previous mixed server/protocol fixture has been pruned. Current checks create no NativeWeave HTTP/gRPC/MCP host, and no timed workload is part of DB-Scope-01.

## API composition

```bash
python3 tests/Verification.EndToEnd/api_probe.py \
  --feed /absolute/candidate/feed --version 0.1.0-db-scope.1.2 \
  --output /absolute/outside-source/database-api
```

Set `NW_TEST_POSTGRES` to a live PostgreSQL URI and put `psql` on PATH. The default runs SQLite and PostgreSQL under both JIT and Native AOT. See [api-probe.md](api-probe.md) for its exact database lifecycle observations.

## Finite database failures

The reference package matrix invokes this runner automatically for every provider/runtime row. To investigate one already-built reference artifact independently:

```bash
python3 tests/Verification.EndToEnd/run.py \
  --artifact-directory /absolute/reference/artifacts/jit --mode jit \
  --provider postgresql --postgres-bin /absolute/postgresql/bin \
  --output /absolute/new/database-faults
```

The default executes every required case for the provider in [matrix.json](matrix.json). PostgreSQL gets an isolated disposable cluster because the tests include an actual immediate server stop and restart. SQLite runs against new local files. The `--cases` development selector explicitly records omitted cases; a selected prefix cannot be mistaken for the full matrix.

Retained cases cover BEGIN/write transport loss, COMMIT held before dispatch, COMMIT acknowledgment loss, physical retirement after failed pool-return drain, PostgreSQL restart, an independent SQLite writer lock, a real native SQLite WAL write returning ENOSPC, outbox worker death after consumer publication and before source acknowledgment, interruption before staged content is complete, interruption after rename and before the database reference commits, and interrupted orphan collection. Every case checks durable SQL or filesystem evidence after recovery.

The staged-write barrier replaces the old HTTP partial-upload input: it stops after the actual first write to the fixture's `.part` file. `FilesystemFaults/fs_fault.c` runs only in the disposable verification child. It forwards real calls and can inject one narrowly selected write failure or hold after an actual successful filesystem operation. Product native assets are not modified. `syscall_fault.py` retains the external Linux x64 syscall-level alternative; its result must prove a fault occurred to claim a pass.

Every case owns and joins its processes and proxy. A crash is verified as an actual SIGKILL; clean closure is verified separately by fixture receipts. Failed, interrupted, unavailable or missing required observations cannot pass. Historical B21/B22 delivery records remain at their original commits.
