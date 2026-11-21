#!/usr/bin/env python3
"""Execute transferred database AOT outputs in the runtime-only Linux image."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

RUNTIME_IMAGE = "mcr.microsoft.com/dotnet/runtime-deps:10.0.15-noble-amd64@sha256:ebb73a172b49758c6de2462305e872ea0cb37ad3ca27cc0d86bc48b6271eaace"
TASK = "DB-Scope-01"
PROVIDERS = {"sqlite": ["sqlite"], "postgresql": ["postgresql"], "combined": ["sqlite", "postgresql"]}


def required(graph):
    if graph not in PROVIDERS:
        raise ValueError("Unknown database transfer graph")
    result = {"actual-native-aot", "typed-entity-materialization", "typed-native-database-roundtrip",
              "typed-fluent-dto-query", "database-local-owners-retired", "actual-database-native-mapping"}
    if graph == "combined":
        result.add("ordinary-added-entity-dto-query")
    return result


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def relative(root, name):
    if not name or "\\" in name or ":" in name or Path(name).is_absolute() or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("Invalid transferred relative path")
    result = root / name
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError("Transfer symlink escapes the runtime bundle")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bundle, output = args.bundle.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if os.environ.get("B24_RUNTIME_IMAGE") != RUNTIME_IMAGE:
        raise ValueError("Runtime execution requires the existing pinned runtime-only image")
    absence = {tool: shutil.which(tool) is None for tool in ("dotnet", "cargo", "rustc", "rustup", "clang", "cc")}
    if not all(absence.values()):
        raise ValueError("Runtime-only image contains a managed/native build tool")
    manifest = json.loads((bundle / "manifest.json").read_text())
    if manifest.get("rid") != "linux-x64" or manifest.get("task") != TASK or set(manifest.get("graphs", {})) != set(PROVIDERS):
        raise ValueError("Incomplete actual database AOT transfer")
    result = {"schemaVersion": 1, "task": TASK, "passed": False, "image": RUNTIME_IMAGE,
              "source_commit": manifest["source_commit"], "packages": manifest["packages"],
              "manifestSha256": sha(bundle / "manifest.json"), "toolAbsence": absence, "cases": []}
    work = Path(tempfile.mkdtemp(prefix="nativeweave-b24-runtime-"))
    try:
        for graph, row in manifest["graphs"].items():
            if row.get("providers") != PROVIDERS[graph]:
                raise ValueError("Transferred graph omits or changes required provider rows")
            directory = relative(bundle, graph)
            actual_files = {path.relative_to(directory).as_posix() for path in directory.rglob("*")
                            if path.is_file() and path.suffix not in (".dbg", ".pdb", ".xml")}
            if actual_files != set(row["files"]):
                raise ValueError("Runtime bundle contains missing or undeclared output files")
            for name, digest in row["files"].items():
                if sha(relative(directory, name)) != digest:
                    raise ValueError("Transferred artifact identity differs")
            executable = relative(bundle, row["executable"])
            if executable.parent != directory or executable.name not in row["files"]:
                raise ValueError("Transferred executable is not bound by its graph inventory")
            if row.get("aotElfAudit", {}).get("sha256") != sha(executable) or row["aotElfAudit"].get("executable") is not True:
                raise ValueError("Transferred executable lacks its bound Linux profile audit")
            for provider in row["providers"]:
                env = os.environ.copy()
                env.pop("LD_LIBRARY_PATH", None)
                env["B24_PROVIDER"] = provider
                if provider == "postgresql":
                    env["B24_DATABASE"] = env.get("NW_TEST_POSTGRES") or ""
                    if not env["B24_DATABASE"]:
                        raise ValueError("Real PostgreSQL requires NW_TEST_POSTGRES in the runtime image")
                elif provider == "sqlite":
                    env["B24_DATABASE"] = str(work / (graph + ".sqlite.db"))
                else:
                    env.pop("B24_DATABASE", None)
                process = subprocess.run([str(executable), "--require-aot"], cwd=work, env=env, capture_output=True, timeout=120)
                text = process.stdout.decode(errors="replace")
                receipts = [json.loads(line[len("B24_RESULT "):]) for line in text.splitlines() if line.startswith("B24_RESULT ")]
                if process.returncode or len(receipts) != 1 or receipts[0].get("dynamicCodeSupported") is not False:
                    raise ValueError("Transferred AOT domain process did not pass")
                receipt = receipts[0]
                expected = set(row["expectedChecks"]) | required(graph)
                if receipt.get("task") != TASK or receipt.get("provider") != provider or not expected.issubset(receipt.get("checks", [])):
                    raise ValueError("Transferred process omitted required domain operations")
                native = row["native"]["database." + provider]
                expected_mapping = [{"file": Path(native["relativePath"]).name, "sha256": native["sha256"]}]
                if receipt.get("nativeLibraries") != expected_mapping:
                    raise ValueError("Runtime-only process mapped different native database bytes")
                result["cases"].append({"graph": graph, "provider": provider, "passed": True,
                    "processExited": True, "executableSha256": sha(executable), "receipt": receipt,
                    "stdoutSha256": hashlib.sha256(process.stdout).hexdigest(), "stderrSha256": hashlib.sha256(process.stderr).hexdigest()})
                print(graph, provider, "passed", flush=True)
            for name, digest in row["files"].items():
                if sha(relative(directory, name)) != digest:
                    raise ValueError("Transferred artifact changed during actual execution")
        result["passed"] = True
    finally:
        (output / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
