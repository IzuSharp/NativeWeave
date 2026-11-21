# Compiled database API documentation

The retained maintainer tools check actual database/Core assemblies and XML documentation. They do not enter application packages or runtime dependencies.

Use `src/Build.Integration/ApiReference` to compare the compiled public surface with its exact reviewed baseline. `compose_docs.py` runs that gate and pinned DocFX over copied inputs under artifacts; it does not publish or modify source documentation.

```sh
python3 src/Build.Integration/compose_docs.py \
  --config src/Build.Integration/api/core.json --output artifacts/docs/core-site
python3 tests/Build.Integration/verify_docs.py --output artifacts/docs/contract-tests
```

The fixture exercises signature, default value, nullability and XML failures against the real shared tool. Normal execution rejects drift; a proposed snapshot is a review artifact, not acceptance.

Native database assets are produced by the explicit `eng/task07_native.py` maintainer entry point from clean committed source and current Cargo compiler-artifact outputs. The old generic native proof builder, its MSBuild hook and demonstration sample are removed. Ordinary database applications restore precompiled NuGet native assets and never invoke Rust.
