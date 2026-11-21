# Direct database application sample

This sample links the finite internal application fixture in `src/Reference.TaskService`. It invokes strongly typed database business methods directly and creates no server or protocol listener. The default references only `NativeWeave.Database.Sqlite`; set `ReferenceIncludePostgreSql=true` to include the PostgreSQL facade as well.

The source demonstrates explicit migrations, static models and DTO mapping, typed CRUD and keyset queries, scoped idempotency, optimistic concurrency, transactions with uncertain-commit recovery, a separate durable outbox consumer, and bounded resource disposal. Filesystem attachment logic is internal application code used to verify database-reference safety, not an additional NativeWeave engine.

Use the current candidate version and feed through ordinary NuGet configuration. The following command creates an empty private SQLite fixture directory and writes a random 32-byte cursor-signing key directly into a mode-0600 configuration file. It prints only that file's path; the key is never echoed or committed.

```bash
db_scope_reference_config="$(python3 - <<'PY'
import base64
import json
import os
from pathlib import Path
import secrets
import tempfile

directory = Path(tempfile.mkdtemp(prefix="nativeweave-database-sample-"))
path = directory / "fixture.private.json"
configuration = {
    "provider": "sqlite",
    "database": str(directory / "application.sqlite"),
    "blobDirectory": str(directory / "blobs"),
    "consumerDatabase": str(directory / "consumer.sqlite"),
    "cursorKey": base64.b64encode(secrets.token_bytes(32)).decode("ascii"),
    "principals": [{"tenant": "tenant-a", "principal": "alice", "canWrite": True}],
}
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as stream:
    json.dump(configuration, stream)
    stream.write("\n")
print(path)
PY
)"
dotnet run --project samples/api/reference-taskservice \
  -p:NativeWeavePackageVersion=0.1.0-db-scope.1.2 \
  -- --config "$db_scope_reference_config" --verify
```

Each run receives a new private key. Keep the configuration private while using its database and cursors; never copy a fixed documentation/test key into an application. The finite `--verify` scenario checks actual data and exits after database cleanup. `--migrate-only`, `--outbox-once` and `--maintenance-once` are explicit finite operations. Package-based JIT/Native AOT acceptance runs outside the source tree through `tests/Reference.TaskService/package_probe.py`; it does not rely on this source-linked sample as proof of package independence.
