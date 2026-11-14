# Third-party notices

The NativeWeave source remains MIT licensed under the existing LICENSE. The initial Hello World native crate has no external Cargo dependencies and the managed facade has no third-party runtime PackageReference dependencies. Rust standard libraries and the .NET runtime/toolchain have their respective upstream licenses; Native AOT output may carry runtime components and SDK-produced notices.

Repository conventions were researched from ArcForges/ArcForges (NuGet sources, attributes, ignores and build hygiene), ArcForges/Contracts (separate candidate/verification/publication jobs and OIDC), rust-lang/rust (Rust text attributes), and tokio-rs/tokio (build-output ignore patterns). This is independently written scaffolding; no ArcForges application code, policy package or workflow implementation is incorporated. Exact reference identities and scope are recorded in docs/background.md.

Future engine packages must inventory their full Cargo/native dependency closure, preserve required license texts and NOTICE files, and document patches and source identities before distribution. This file is not a completed license inventory for future Database/ORM/Server engines.
