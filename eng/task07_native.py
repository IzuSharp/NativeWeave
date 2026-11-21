#!/usr/bin/env python3
"""Build the two independent Linux database native profiles and bind their inputs.

Maintainer-only entrypoint. Applications consume the resulting immutable NuGet
assets; this file is never called by a consumer target or source generator.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as stream:
        result = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def capture(argv, env=None):
    return subprocess.check_output(argv, cwd=ROOT, env=env, text=True).strip()


def run(argv, output, label, env):
    stdout = output / (label + ".jsonl")
    stderr = output / (label + ".stderr")
    print("+ " + " ".join(map(str, argv)), flush=True)
    with stdout.open("wb") as out, stderr.open("wb") as err:
        result = subprocess.run(argv, cwd=ROOT, env=env, stdout=out, stderr=err)
    if result.returncode:
        raise RuntimeError(f"{label} failed with exit {result.returncode}; inspect {stderr}")
    return stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if (platform.system(), platform.machine().lower()) != ("Linux", "x86_64"):
        raise RuntimeError("Database candidates currently verify only Linux x64")
    if output.exists():
        raise RuntimeError("Choose a fresh native build output; existing evidence is immutable")
    if capture(["git", "status", "--porcelain"]):
        raise RuntimeError("Commit the maintainer source before building a candidate")
    source = capture(["git", "rev-parse", "HEAD"])
    env = os.environ.copy()
    # Each database provider has an independent explicit native feature profile.
    # Do not inherit an unrecorded CPU, allocator or feature-affecting override.
    for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER",
                "CARGO_BUILD_RUSTFLAGS", "CARGO_BUILD_TARGET", "CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUSTFLAGS"):
        if env.get(key):
            raise RuntimeError("Unsupported build-profile override: " + key)
    target_dir = Path(env.get("CARGO_TARGET_DIR", str(ROOT / "target"))).resolve()
    env["CARGO_TARGET_DIR"] = str(target_dir)
    output.mkdir(parents=True)
    logs = output / "logs"
    logs.mkdir()
    tools = {}
    executables = {}
    rustup = shutil.which("rustup")
    for name, flags in (("rustc", ["-Vv"]), ("cargo", ["--version"]),
                        ("dotnet", ["--version"]), ("cc", ["--version"]),
                        ("ld", ["--version"]), ("readelf", ["--version"])):
        path = shutil.which(name)
        if path is None:
            raise RuntimeError("Missing maintainer tool: " + name)
        launcher = Path(path).resolve()
        # rustup's shims are not the compiler/Cargo binaries that build these
        # artifacts. Resolve, hash and invoke the selected toolchain executables.
        if name in ("rustc", "cargo") and rustup:
            path = capture([rustup, "which", name], env)
        executable = Path(path).resolve(strict=True)
        executables[name] = str(executable)
        tools[name] = {"version": capture([str(executable)] + flags, env),
                       "sha256": sha(executable), "launcherSha256": sha(launcher)}
    if (not tools["rustc"]["version"].startswith("rustc 1.100.0 ")
            or "host: x86_64-unknown-linux-gnu" not in tools["rustc"]["version"]
            or not tools["cargo"]["version"].startswith("cargo 1.100.0 ")
            or tools["dotnet"]["version"] != "11.0.100"):
        raise RuntimeError("Use the pinned Rust/Cargo 1.100.0 and SDK 11.0.100 Linux x64 toolchain")
    files = subprocess.check_output([
        "git", "ls-files", "-z", "--", "native", "Cargo.toml", "Cargo.lock",
        "rust-toolchain.toml", ".cargo"], cwd=ROOT).decode().split("\0")
    inputs = {name: sha(ROOT / name) for name in sorted(files) if name}
    env["RUSTC"] = executables["rustc"]
    rust_sysroot = Path(capture([executables["rustc"], "--print", "sysroot"], env)).resolve()
    manifest = {
        "schemaVersion": 1, "sourceCommit": source, "sourceDirty": False,
        "rid": "linux-x64", "target": "x86_64-unknown-linux-gnu", "profile": "release",
        "tools": tools, "inputSha256": inputs, "cargoLockSha256": sha(ROOT / "Cargo.lock"),
        "rustSysroot": str(rust_sysroot),
        "cargoHome": str(Path(env.get("CARGO_HOME", str(Path.home() / ".cargo"))).resolve()),
        "environment": {"CARGO_TARGET_DIR": str(target_dir),
                        "CARGO_BUILD_JOBS": env.get("CARGO_BUILD_JOBS"),
                        "RUSTC": executables["rustc"], "RUSTFLAGS": "", "CARGO_ENCODED_RUSTFLAGS": ""},
        "builds": [], "assets": [],
        "scope": "DB-Scope-01: exact newly built local database candidate inputs; historical evidence retains its original identities."
    }
    profiles = [
        ("sqlite", ["-p", "nativeweave-database-host"],
         "nativeweave-database-host/sqlite",
         [("database.sqlite", "nativeweave_database_host", "libnw_database_sqlite.so")]),
        ("postgresql", ["-p", "nativeweave-database-host"], "nativeweave-database-host/postgres",
         [("database.postgresql", "nativeweave_database_host", "libnw_database_postgresql.so")])
    ]
    for label, packages, feature, assets in profiles:
        command = [executables["cargo"], "build", "--locked", "--release"] + packages + [
            "--no-default-features", "--features", feature, "--message-format=json"]
        messages = run(command, logs, label + "-build", env)
        metadata_command = [executables["cargo"], "metadata", "--locked", "--format-version=1",
                            "--filter-platform", manifest["target"], "--no-default-features",
                            "--features", feature]
        metadata = run(metadata_command, logs, label + "-metadata", env)
        # Cargo metadata may include unused workspace nodes; the license inventory
        # joins it to these actual compiler-artifact package IDs and features.
        records = [json.loads(line) for line in messages.read_text().splitlines() if line]
        if not any(r.get("reason") == "build-finished" and r.get("success") is True for r in records):
            raise RuntimeError("Cargo did not confirm a successful build: " + label)
        manifest["builds"].append({
            "label": label, "command": command, "defaultFeatures": False, "features": [feature],
            "metadataCommand": metadata_command, "metadataPath": str(metadata),
            "metadataSha256": sha(metadata), "buildMessagesPath": str(messages),
            "buildMessagesSha256": sha(messages)})
        for engine, target, filename in assets:
            found = {Path(name).resolve() for r in records
                     if r.get("reason") == "compiler-artifact" and r.get("target", {}).get("name") == target
                     for name in r.get("filenames", []) if name.endswith(".so")}
            if len(found) != 1:
                raise RuntimeError(f"Expected one actual Cargo shared-library artifact for {engine}: {found}")
            built = found.pop()
            path = output / filename
            shutil.copy2(built, path)
            manifest["assets"].append({"engineId": engine, "path": str(path),
                                       "sha256": sha(path), "bytes": path.stat().st_size,
                                       "buildLabel": label, "compilerArtifactPath": str(built)})
    if source != capture(["git", "rev-parse", "HEAD"]) or capture(["git", "status", "--porcelain"]):
        raise RuntimeError("Source changed while producing the native candidate")
    if any(sha(ROOT / name) != expected for name, expected in inputs.items()):
        raise RuntimeError("A bound native source input changed during the build")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"manifest": str(output / "manifest.json"), "sha256": sha(output / "manifest.json")}))


if __name__ == "__main__":
    main()
