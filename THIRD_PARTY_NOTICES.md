# Third-party notices

NativeWeave remains MIT licensed under LICENSE.

The retained database implementation uses Rust SeaQuery, SQLx, Tokio and their resolved dependencies. Each candidate native leaf carries the exact Cargo build closure, upstream license texts and notices, source identities and native SHA-256. The inventory is derived from actual Cargo compiler-artifact messages and locked metadata for that provider profile; unused workspace nodes are not reported as linked dependencies.

The packager also records the selected official Rust standard-library license material and native ELF dependencies. .NET/Native AOT runtime and toolchain components retain their upstream licensing and SDK-produced notices.

See `src/Packaging.Domain/inventory.py` and the candidate `nativeweave/` manifests and NOTICE entries. This source-level note does not replace the generated per-artifact license inventory. A changed native dependency or patch requires a new reviewed inventory before distribution.
