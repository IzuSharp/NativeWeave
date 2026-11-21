# Database package consumer matrix

`package_probe.py` invokes the shared controller in `tests/Verification.EndToEnd/api_probe.py` with the reference fixture. Its default matrix is SQLite/JIT, SQLite/Native AOT, PostgreSQL/JIT and PostgreSQL/Native AOT. Each row runs the direct application oracles followed by the complete provider-specific database fault suite.

The `--feed` directory must contain exactly the retained NativeWeave package closure. `--version` pins both direct provider facades; exact transitive versions come from the candidate nuspecs and are frozen in generated lock files. Restoring a different NativeWeave package version, using a source project, using a global cache, introducing a removed package/native asset or invoking a Rust tool fails the attempt.

The output records source inventories, candidate archive hashes, dependencies, generated lock files, resolved package archives, build/publish inventories, JIT/AOT runtime observations, direct database receipts, independent SQL, proxy event witnesses and finite filesystem/crash receipts. The consumer's native bytes must match the producer packages before and after execution. The final matrix is complete only when all four rows pass.

No timed workload, benchmark, server/protocol adapter, bearer credential or HTTP client is used. `--providers` and `--modes` can select development subsets; their receipts explicitly leave the full four-row matrix incomplete.
