# Hello World API reference

Generated from the compiled bootstrap assembly and XML by `tools/ApiDocs`; do not hand-edit.

Package: `NativeWeave.HelloWorld` (experimental).

```csharp
public static class NativeWeave.HelloWorld.RustGreeting
public static string Greet(string name = "World");
```

## `T:NativeWeave.HelloWorld.RustGreeting`

- **summary:** Creates a greeting using the precompiled Rust bootstrap library.
- **remarks:** This stateless API is thread-safe. It owns no disposable resources and starts no runtime, worker, callback or asynchronous operation. It demonstrates packaging and interop only. Supported assets are listed in the package manifest; Linux x64 is the initial CI target.

## `M:NativeWeave.HelloWorld.RustGreeting.Greet(System.String)`

- **summary:** Returns a UTF-8 greeting constructed by Rust.
- **param name:** The name to greet, defaulting to World. Empty names and embedded NULs are preserved.
- **returns:** A managed string containing Hello, {name}! From Rust..
- **exception T:System.ArgumentNullException:** name is null.
- **exception T:System.ArgumentException:** The name is invalid UTF-16 or exceeds 4096 UTF-8 bytes.
- **exception T:System.DllNotFoundException:** No compatible native asset is installed for the current platform.
- **exception T:System.BadImageFormatException:** The native asset has an incompatible binary format.
- **exception T:System.EntryPointNotFoundException:** The installed native asset lacks a bootstrap export.
- **exception T:System.InvalidOperationException:** The native ABI, status, or returned length is incompatible.
- **remarks:** Synchronous and thread-safe; cancellation and timeouts do not apply. Buffers are borrowed only during each call. Rust allocates no greeting storage. Names up to 256 UTF-8 bytes and results up to 512 bytes use stack storage; larger values allocate bounded managed arrays. Each call performs ABI validation, a size query and one write (three FFI calls), UTF-8 encoding/decoding, and a result-string allocation. No zero-copy or speedup claim is made. Native libraries remain loaded for the process lifetime. This is an experimental bootstrap API.
