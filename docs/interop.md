# Hello World bootstrap contract

This experimental surface is separate from the designed production Core/Engine ABI. Its owner is the initial repository bootstrap, with future build and compatibility work belonging to A13/A16/A22. It does not mark those tasks accepted.

## Mapping and ownership

`RustGreeting.Greet(string name = "World")` → bounded strict UTF-8 encoding → `nw_hello_abi_version` → `nw_hello_greet` size query → `nw_hello_greet` write → Rust `str::from_utf8` and byte copies → strict managed UTF-8 decoding.

Input is at most 4096 UTF-8 bytes. Empty strings, Unicode and embedded NULs are data. Invalid UTF-16/null/oversized input fails before the first native call. The ABI uses fixed `uint32_t` status and native-width `size_t` byte lengths; the checked-in C header is the authority for native callers. There is no Rust layout, bool, string, exception or allocator object in the ABI.

C# owns both input and output buffers. Rust borrows only during the synchronous call and keeps nothing. Small buffers use stack storage; larger buffers use bounded managed arrays. The result is a managed string. There is no native resource requiring Dispose, no callback, shared mutable state, cancellation, timeout or background runtime. Calls from different threads are independent. Libraries stay loaded for the process lifetime.

Each call has three FFI transitions, one encoding, one decoding, native byte copies and one result-string allocation; larger inputs add two managed arrays. This is an explicit cost description, not a benchmark or zero-copy claim. Rust's greeting path allocates no result buffer.

## Failures and bounds

| Native status | Meaning |
| --- | --- |
| 0 | Complete output written; written length excludes a NUL terminator |
| 1 | Insufficient capacity; required length returned; output untouched |
| 2 | Null/inconsistent arguments; written zero when provided |
| 3 | Invalid UTF-8; output untouched, written zero |
| 4 | Input exceeds 4096 bytes; output untouched, written zero |
| 255 | Recoverable Rust panic contained; result length must be ignored |

Non-null native pointers must address valid, disjoint live regions with the stated capacities. Foreign-pointer validity is a caller obligation. The bounded native path has no intentionally panicking operation; the unwind guard is defense in depth and does not recover from abort/OOM/memory corruption. Managed code checks ABI major, expected status and a bounded exact write length. Native loader errors propagate as standard .NET exceptions; unexpected native status/ABI is InvalidOperationException. The generated API reference lists public exception semantics.

## Verification

Rust tests cover UTF-8, null arguments, exact and insufficient capacity, untouched failure output and size limits. Managed JIT and package-based Native AOT tests cover optional/named/delegate calls, Unicode/NUL/empty values, malformed UTF-16, size boundaries and 1000 parallel greetings. The maintainer API tool checks the actual compiled surface, nullability/defaults, required XML and generated reference.

Native loading uses .NET runtime asset resolution and a restricted import search policy. This is not the full production hash/identity/capability-verifying loader from Design. Package hashes are checked during verification; no claim of runtime signature enforcement, safe untrusted plugins, single-file deployment or hot unloading is made.
