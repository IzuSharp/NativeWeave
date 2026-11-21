#!/usr/bin/env python3
"""B03 component verification: exact integrated provider API, SQLite/B05 composition and JIT/AOT."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OWNED = ["src/Data.Sqlite", "native/database/sqlite", "tests/Data.Sqlite", "samples/api/data-sqlite", "docs/guides/data-sqlite.md"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_identity():
    paths = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", *OWNED,
                                     "tests/ProviderProfileChecks.cs", "src/Data.NativeHost", "native/database/host", "src/Data.Abstractions", "src/NativeWeave.Core", "src/Interop.Abi", "src/Interop.Negotiation", "src/Interop.Errors", "native/database/interfaces", "native/database/codecs", "native/database/transactions", "native/interop/abi", "Cargo.toml", "Cargo.lock", "Directory.Build.props", "global.json", "rust-toolchain.toml"], cwd=ROOT, text=True).splitlines()
    return {p: sha(ROOT / p) for p in sorted(set(paths)) if (ROOT / p).is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/B03/component-run")
    parser.add_argument("--offline-config", type=Path)
    parser.add_argument("--dotnet", default="dotnet")
    parser.add_argument("--design", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update(DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1", DOTNET_CLI_USE_MSBUILD_SERVER="0")
    commands = []
    initial = source_identity()
    manifest = {"scope": "B03-linux-x64-component", "status": "running", "platform": platform.platform(),
                "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "sourceDirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
                "sourceSha256": initial, "commands": commands, "artifacts": {},
                "realProviderComposition": "actual SQLite 3.51.3 through SQLx 0.9.0; B05 transaction seam exercised in fourteen native scenario groups", "assembledHostAcceptance": False,
                "independentReview": False, "allPlatformAcceptance": False}

    def save():
        (output / "result.json").write_text(json.dumps(manifest, indent=2) + "\n")

    def run(label, command, custom_env=None, timeout=600):
        start = time.monotonic()
        result = subprocess.run(list(map(str, command)), cwd=ROOT, env=custom_env or env, capture_output=True, text=True, timeout=timeout)
        stdout = output / (label + ".stdout.log")
        stderr = output / (label + ".stderr.log")
        stdout.write_text(result.stdout)
        stderr.write_text(result.stderr)
        commands.append({"label": label, "command": list(map(str, command)), "exitCode": result.returncode,
                         "seconds": round(time.monotonic() - start, 3), "stdoutSha256": sha(stdout), "stderrSha256": sha(stderr)})
        save()
        print(label + ": " + str(result.returncode), flush=True)
        if result.returncode:
            raise RuntimeError(label + " failed; see retained raw logs")
        return result.stdout

    dotnet = shutil.which(args.dotnet) or str(Path(args.dotnet).resolve())
    sdk = Path(dotnet).resolve().parent
    host_native = ROOT / "target/release/libnw_database_sqlite.so"
    build_flags = ["-p:UseSharedCompilation=false", "-nr:false", "-m:1", f"-p:NativeWeaveSqliteAssetPath={host_native}"]
    ordinary = ["src/Data.Sqlite/NativeWeave.Database.Sqlite.csproj",
                "tests/Data.Sqlite/NativeWeave.Data.Sqlite.Tests.csproj",
                "tests/Data.Sqlite/ApiCheck/ApiCheck.csproj",
                "samples/api/data-sqlite/Data.Sqlite.Sample.csproj"]

    def restore(label, project, aot=False):
        command = [dotnet, "restore", project, "--locked-mode", *build_flags]
        if aot:
            command.extend(["-r", "linux-x64", "-p:PublishAot=true"])
        if args.offline_config:
            command.extend(["--configfile", args.offline_config.resolve(), "-p:NuGetAudit=false"])
        run(label, command)

    try:
        assert not manifest["sourceDirty"], "Formal acceptance requires a clean committed source tree"
        assert platform.system() == "Linux" and platform.machine() == "x86_64", "This run only accepts Linux x64"
        assert host_native.is_file(), "Build the actual SQLite Database Host before component/preflight verification"
        if args.design:
            pins = json.loads((ROOT / "tests/Data.Sqlite/design-inputs.json").read_text())
            assert subprocess.check_output(["git", "-C", str(args.design), "rev-parse", "HEAD"], text=True).strip() == pins["commit"]
            for path, expected in pins["sha256"].items():
                assert sha(args.design / path) == expected, path
            manifest["pinnedDesignInputs"] = {"commit": pins["commit"], "verifiedCount": len(pins["sha256"])}
        run("rustc", ["rustc", "-Vv"])
        run("cargo", ["cargo", "--version"])
        assert run("sdk", [dotnet, "--version"]).strip() == "11.0.100"
        run("sdk-info", [dotnet, "--info"])
        run("gcc", ["gcc", "--version"])
        run("linker", ["ld", "--version"])
        run("native-format", ["cargo", "fmt", "-p", "nativeweave-data-sqlite", "--", "--check"])
        run("native-clippy", ["cargo", "clippy", "-p", "nativeweave-data-sqlite", "--all-targets", "--locked", "--", "-D", "warnings"])
        native_tests = run("native-tests", ["cargo", "test", "-p", "nativeweave-data-sqlite", "--release", "--locked", "--", "--nocapture"])
        assert all(f"PASS B03 native scenario {i}" in native_tests for i in range(1, 15))
        run("native-features", ["cargo", "tree", "-p", "nativeweave-data-sqlite", "-e", "features", "--locked"])
        product_build = run("provider-build", ["cargo", "build", "-p", "nativeweave-data-sqlite", "--release", "--locked", "--message-format=json"])
        products = [Path(f) for line in product_build.splitlines() if line.startswith("{") for event in [json.loads(line)] if event.get("reason") == "compiler-artifact" and event["target"]["name"] == "nativeweave_data_sqlite" for f in event["filenames"] if f.endswith(".so")]
        assert len(products) == 1
        component_native = products[0]
        run("provider-elf-linker", ["readelf", "-p", ".comment", component_native])
        manifest["nativeInputs"] = {"privateComponentSha256": sha(component_native), "integratedHostSha256": sha(host_native)}
        fixture = "tests/Data.Sqlite/native-fixture/Cargo.toml"
        run("fixture-format", ["cargo", "fmt", "--manifest-path", fixture, "--", "--check"])
        run("fixture-clippy", ["cargo", "clippy", "--manifest-path", fixture, "--all-targets", "--locked", "--", "-D", "warnings"])
        metadata = json.loads(run("dependency-metadata", ["cargo", "metadata", "--manifest-path", fixture, "--format-version=1", "--locked", "--filter-platform", "x86_64-unknown-linux-gnu"]))
        (output / "dependency-licenses.json").write_text(json.dumps([{k: p[k] for k in ["name", "version", "license"]} for p in metadata["packages"]], indent=2) + "\n")
        selected = {p["name"]: p for p in metadata["packages"]}
        upstream = {}
        files = {"sqlx-core": ["src/transaction.rs", "src/pool/connection.rs"],
                 "sqlx-sqlite": ["src/connection/worker.rs", "src/connection/mod.rs", "src/connection/executor.rs", "src/transaction.rs", "src/options/mod.rs"],
                 "libsqlite3-sys": ["Cargo.toml", "build.rs", "sqlite3/sqlite3.c"]}
        for package, paths in files.items():
            base = Path(selected[package]["manifest_path"]).parent
            upstream[package] = {"version": selected[package]["version"], "registrySource": selected[package]["source"], "sha256": {path: sha(base / path) for path in paths}}
        manifest["upstreamCompiledSourceInputs"] = upstream
        built = run("fixture-build", ["cargo", "build", "--manifest-path", fixture, "--release", "--locked", "--message-format=json"])
        libraries = [Path(f) for line in built.splitlines() if line.startswith("{") for event in [json.loads(line)]
                     if event.get("reason") == "compiler-artifact" and event["target"]["name"] == "nativeweave_sqlite_fixture"
                     for f in event["filenames"] if f.endswith(".so")]
        assert len(libraries) == 1
        native = libraries[0]
        run("actual-rust-link", ["cargo", "rustc", "--manifest-path", fixture, "--release", "--locked", "--", "--print", "link-args"])
        run("native-elf-linker", ["readelf", "-p", ".comment", native])
        execution_env = env.copy()
        execution_env["LD_LIBRARY_PATH"] = str(native.parent)
        execution_env["NW_SQLITE_COMPONENT_ASSET"] = str(component_native)
        for index, project in enumerate(ordinary):
            restore("ordinary-restore-" + str(index), project)
            run("ordinary-build-" + str(index), [dotnet, "build", project, "-c", "Release", "--no-restore", *build_flags])
        run("managed-whitespace", [dotnet, "format", "whitespace", ".", "--folder", "--verify-no-changes", "--include",
                                    "src/Data.Sqlite/SqliteOptions.cs", "src/Data.Sqlite/SqliteConfiguration.cs", "src/Data.Sqlite/SqliteDataSource.cs", "tests/Data.Sqlite/Program.cs", "tests/ProviderProfileChecks.cs", "tests/Data.Sqlite/ApiCheck/Program.cs", "samples/api/data-sqlite/SqliteExamples.cs", "--verbosity", "quiet"])
        assembly = ROOT / "src/Data.Sqlite/bin/Release/net11.0/NativeWeave.Database.Sqlite.dll"
        api_result = json.loads(run("compiled-api-xml-reference", [dotnet, "tests/Data.Sqlite/ApiCheck/bin/Release/net11.0/NativeWeave.Sqlite.ApiCheck.dll", ROOT, sdk, assembly]))
        execution_env["NATIVEWEAVE_B03_TEST_ROOT"] = str(output / "jit-data")
        jit_output = run("jit", [dotnet, "tests/Data.Sqlite/bin/Release/net11.0/NativeWeave.Data.Sqlite.Tests.dll"], execution_env)
        assert "NativeAOT=False" in jit_output and all(f"PASS B03 native scenario {i}" in jit_output for i in range(1, 15))
        restore("aot-restore", ordinary[1], True)
        publish = output / "publish"
        run("aot-publish", [dotnet, "publish", ordinary[1], "-c", "Release", "-r", "linux-x64", "-p:PublishAot=true", "--no-restore", "-p:IlcTreatWarningsAsErrors=true", *build_flags, "-o", publish])
        executable = publish / "NativeWeave.Data.Sqlite.Tests"
        execution_env["NATIVEWEAVE_B03_TEST_ROOT"] = str(output / "aot-data")
        aot_output = run("aot-execution", [executable, "--aot"], execution_env)
        assert "NativeAOT=True" in aot_output and all(f"PASS B03 native scenario {i}" in aot_output for i in range(1, 15))
        run("aot-elf-linker", ["readelf", "-p", ".comment", executable])
        for artifact in [component_native, host_native, native, assembly, executable]:
            manifest["artifacts"][str(artifact)] = sha(artifact)
        for tool in [dotnet, shutil.which("gcc"), shutil.which("ld"), shutil.which("rustc")]:
            if tool and Path(tool).is_file():
                manifest.setdefault("toolHashes", {})[str(Path(tool).resolve())] = sha(Path(tool).resolve())
        generated = list((ROOT / "src/Data.Sqlite/obj").rglob("EngineProfile.g.cs"))
        generated += list((ROOT / "src/Data.Sqlite/obj").rglob("NativeWeave.database.sqlite.assets.json"))
        for artifact in generated:
            manifest.setdefault("generatedMaintainerProfileSha256", {})[str(artifact)] = sha(artifact)
        for location in [ROOT / "tests/Data.Sqlite/bin/Release/net11.0", publish]:
            record_path = location / "NativeWeave.database.sqlite.assets.json"
            record = json.loads(record_path.read_text())
            assert record["engineId"] == "database.sqlite" and record["packageId"] == "NativeWeave.Database.Sqlite"
            assert record["sourcePath"] == record["outputPath"] == "runtimes/linux-x64/native/libnw_database_sqlite.so"
            assert record["sha256"] == sha(host_native)
            assert sha(location / record["outputPath"]) == sha(host_native)
            manifest["artifacts"][str(record_path)] = sha(record_path)
        manifest["nativeScenarioGroups"] = 14
        manifest["hostPreflight"] = True
        manifest["compiledComponentSymbols"] = api_result["compiled_symbols"]
        manifest["compiledHostCompositionSymbols"] = len(json.loads((ROOT / "src/Data.Sqlite/host-composition.expected.json").read_text())["symbols"])
        manifest["workerShutdownEvidence"] = "SQLx shutdown ACK and pool-return separately observed; OS thread join is never claimed"
        final = source_identity()
        assert final == initial, "Implementation/lock bytes changed during verification"
        manifest["status"] = "passed"
        manifest["sourceStable"] = True
        manifest["actualNativeAotExecuted"] = True
        manifest["localRestoreAuditRefresh"] = "unavailable-local-feed" if args.offline_config else "normal-repository-policy"
        manifest["fullManagedFormatter"] = "existing-CI-required; local-folder-whitespace-check-only"
    except Exception as error:
        manifest["status"] = "failed"
        manifest["failure"] = str(error)
        save()
        raise
    save()
    print("PASS: B03 Linux x64 component oracles, integrated Host preflight, exact API, real SQLite/B05 composition, JIT and actual Native AOT; full Host execution is verified separately.")


if __name__ == "__main__":
    main()
