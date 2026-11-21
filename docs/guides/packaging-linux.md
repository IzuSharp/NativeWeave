# Linux native packages and Native AOT

Task A14 supports the declared GNU Linux x64 packaging profile: Ubuntu 24.04,
glibc requirements no later than 2.39, and x86-64-v2 instructions. A local run on
a newer distribution is useful development evidence; it does not certify that
minimum distro. Windows, musl, other architectures, static linking and single-file
extraction retain their separate task/profile requirements.

The minimum CPU execution row uses the same published executable/native bytes
under `qemu-x86_64 -cpu Nehalem`. An actual compiled CPUID probe must report every
x86-64-v2 addition and no AVX, AVX2, AVX512F or FMA before any consumer is accepted.
The receipt identifies CPU emulation separately from the physical host, records
the actual host OS, and hashes the emulator, probe, transferred binaries and each
command output. It is not physical CPU certification.

After the complete package check, run this in the existing Ubuntu 24.04 Linux
verification row with `qemu-user` installed:

```sh
python3 tests/Packaging.Linux/minimum_cpu.py \
  artifacts/task04/A14/ci/runtime-transfer \
  --output artifacts/task04/A14/minimum-cpu --require-baseline
```

The entrypoint requires all A01/A03/A04/A05/A06/A07 consumers, checks their original
hashes, and executes each actual Native AOT program under the verified emulated
profile. This is separate from the matching runtime-only transfer check.

## Ordinary application path

Install the engine's validated facade package and use its typed factory. Restore
selects `runtimes/linux-x64/native/`; ordinary `dotnet build` and `dotnet run` need
no explicit RID and no Cargo. Publish with
`dotnet publish -c Release -r linux-x64 -p:PublishAot=true`; the resulting executable
needs the documented OS runtime dependencies, without an installed .NET runtime
or Rust compiler. Native AOT publishing itself still needs the .NET SDK and native
linker prerequisites.

Core contains the implemented descriptor, error, lifetime, buffer and async
components. It has no native asset and starts no runtime merely by being referenced.
The local `NativeWeave.Conformance.Core.Native` package is a test closure of real
component adapters; it is not a shipping domain engine or public preview package.
The current database candidate composes this retained Core packaging infrastructure; the former demo publisher is retired.

## Reproduce the actual package check

Run `python3 tests/Packaging.Linux/verify.py --require-baseline` on the declared
Linux profile with pinned SDK 11.0.100 and Rust 1.100.0. The verifier copies the
component consumer sources outside the checkout, replaces ProjectReferences with
actual nupkg references, uses a fresh cache, runs RID-free JIT, and publishes and
executes each component with Native AOT. Layout, lease, buffer, error, callback and
async behavior execute against the integrated product modules. These are package
composition rows, not rewritten historical component acceptance receipts.

`--components A01 A03 A04 A05` permits independent development while A06/A07 are
not yet integrated; the receipt explicitly records `complete_core_closure=false`.
Such a partial row cannot accept A14. `--offline-sdk-cache PATH` accepts cached
Microsoft .NET 11 tool packages, records offline audit limits, and uses a separate
consumer cache. A Rust invocation trap establishes that these commands did not
call Rust; pristine installation remains the distinct A16 clean-image gate.

The native ELF inventory records architecture, exported symbols, dynamic dependencies,
GLIBC versions, source locks, native/package/executable SHA-256 and actual command
results. Rust builds explicitly select x86-64-v2. Package SHA-256 stays outside the
package to avoid circular provenance. All attempted runs retain their own failures.

Transfer the produced `runtime-transfer/` directory to a matching runtime-only
environment. Run `python3 tests/Packaging.Linux/runtime.py TRANSFER --receipt RESULT
--require-tool-absence` using a separately copied verifier. It requires absent
.NET SDK/Rust/C compilers, compares the transferred native and executable hashes,
and actually executes each AOT consumer. Configuring this check is not a passed row.

## Diagnostics and documentation

`NWPKG003` identifies wrong architecture/ELF, an undeclared dependency, a GLIBC
requirement beyond the baseline or an incompatible ISA note. `NWPKG005` identifies
export drift when a reviewed inventory is supplied. Runtime first-use package
diagnostics are owned by Core's existing descriptor loader; A16 creates its bounded
SDK-selected asset record. Missing or tampered assets must fail before a domain
owner is published. Nothing downloads a compiler or selects an arbitrary library
from the current working directory.

The [tool reference](../../src/Packaging.Linux/api-reference.md) declares the
internal-only applicability. XML and compiled references of included Core APIs
remain the owning components' authoritative documentation. The
[minimal and advanced commands](../../samples/api/packaging-linux/README.md) use
real packages and keep their executed evidence in the verifier receipt.
