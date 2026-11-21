# Direct database API composition

`src/Verification.EndToEnd/ApiProbe` is an ordinary console application referencing only the SQLite and PostgreSQL facade packages. The shared controller copies it outside the repository, freezes the exact candidate dependency graph, verifies locked restore and publishes real Linux x64 JIT and Native AOT executables with precompiled native assets and rejecting Rust tool traps.

The required case IDs live in `src/Verification.EndToEnd/ApiProbe/required-cases.json`. They cover:

- Cancellation before COMMIT admission and confirmed rollback, with no durable canceled row.
- Actual provider constraint failure, confirmed rollback and retained PostgreSQL physical-session identity.
- A positive streamed row, rejection of concurrent use while a cursor owns session admission, and successful reuse after early cursor disposal.
- Nullable composite foreign-key relation loading, `IS NULL`, and SQL equality-to-null behavior. These assertions were extracted from the deleted HTTP handler and now execute directly.
- Public session/source retirement, an explicit source weak-reference witness, and zero counts for all six database native owner classes in both selected provider modules.

After each process exits, CPython SQLite or psql independently confirms durable row counts, absence of the canceled insert, and composite-key/null fixtures. SQLite also runs integrity and foreign-key checks. Receipts verify actual `RuntimeFeature.IsDynamicCodeSupported`, exact required-case membership, immutable native hashes, isolated package-cache provenance and the absence of Rust invocations.

The weak-reference witness is not a total managed-root count. Native owner counters and disposal receipts have distinct meanings and are recorded independently. All four provider/runtime rows must pass for complete matrix acceptance; partial development selections remain incomplete. No HTTP/gRPC/MCP server, protocol limit, request permit or performance claim remains in this fixture.
