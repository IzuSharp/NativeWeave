#!/usr/bin/env python3
"""Maintainer Linux database build, regression and ordinary NuGet/AOT consumption."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
LOGS = ARTIFACTS / "logs"
OUTPUT = ARTIFACTS / "db-scope"


def run(args, label, cwd=ROOT, env=None, json_stdout=False):
    LOGS.mkdir(parents=True, exist_ok=True)
    print("+ " + " ".join(map(str, args)), flush=True)
    result = subprocess.run(list(map(str, args)), cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE if json_stdout else subprocess.STDOUT)
    logged = result.stdout + ("\n[stderr]\n" + result.stderr if json_stdout and result.stderr else "")
    (LOGS / (label + ".log")).write_text(logged, encoding="utf-8")
    if result.returncode:
        print(logged[-16000:], flush=True)
        raise RuntimeError(f"{label} failed ({result.returncode}); see artifacts/logs/{label}.log")
    if not json_stdout:
        print(result.stdout[-3000:], end="", flush=True)
    return result.stdout


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_fixture_results(external, destination):
    """Export bounded result JSON without private configuration or raw argv/logs."""
    allowed = {"progress.json", "receipt.json", "result.json", "summary.json", "status.json", "independent-sql.json",
               "resolved-archive-hashes.json"}
    private_keys = {"argv", "command", "config", "configuration", "database", "connectionstring",
                    "connection_string", "password", "secret", "cursorkey", "cursor_key"}

    def safe(value):
        if isinstance(value, dict):
            return {key: safe(item) for key, item in value.items() if key.lower() not in private_keys}
        if isinstance(value, list):
            return [safe(item) for item in value]
        if isinstance(value, str):
            return re.sub(r"postgres(?:ql)?://[^\s\"'<>]+", "<database-uri>", value)
        return value

    for path in external.rglob("*.json"):
        relative = path.relative_to(external)
        if path.name not in allowed or any(part in (
                "consumer-cache", "dotnet-home", "consumers", "metadata", "artifacts", "postgres-data")
                for part in relative.parts):
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"sanitized": True, "source_artifact_sha256": digest(path),
                                      "data": safe(json.loads(path.read_text()))}, indent=2) + "\n")


def source():
    return {"commit": run(["git", "rev-parse", "HEAD"], "source-commit").strip(),
            "tree": run(["git", "rev-parse", "HEAD^{tree}"], "source-tree").strip()}


def native():
    output = OUTPUT / "native-build"
    run([sys.executable, "eng/task07_native.py", "--output", output], "database-native")
    manifest = json.loads((output / "manifest.json").read_text())
    # Source project consumers use the same independently built provider bytes.
    target = ROOT / "target/release"
    target.mkdir(parents=True, exist_ok=True)
    for asset in manifest["assets"]:
        path = Path(asset["path"])
        if digest(path) != asset["sha256"]:
            raise RuntimeError("Native candidate changed before source staging")
        shutil.copy2(path, target / path.name)
    return output / "manifest.json"


def pack(version, manifest):
    run([sys.executable, "src/Packaging.Domain/prepare.py", "--output", OUTPUT / "prepared",
         "--previous-version", version + ".1", "--candidate-version", version + ".2",
         "--native-manifest", manifest], "database-packages")


def consume(environment):
    prepared = OUTPUT / "prepared"
    run([sys.executable, "tests/Packaging.Domain/consumer_cases.py", "--manifest", prepared / "manifest.json",
         "--closure", "candidate", "--feed", prepared / "candidate/feed",
         "--output", OUTPUT / (environment + "-consumer"), "--mode", "full",
         "--consumer-environment", environment], "database-" + environment + "-consumer")


def verify(version, design, plan):
    if not os.environ.get("NW_TEST_POSTGRES"):
        raise RuntimeError("Set NW_TEST_POSTGRES to a disposable real PostgreSQL 18 test server")
    os.environ["NATIVEWEAVE_TEST_POSTGRES_URL"] = os.environ["NW_TEST_POSTGRES"]
    if run(["git", "status", "--porcelain"], "initial-status").strip():
        raise RuntimeError("Commit a clean candidate before collecting source-bound evidence")
    initial = source()
    standard = json.loads((ROOT / "public-api-standard.json").read_text())
    if digest(ROOT / standard["localPath"]) != standard["sha256"]:
        raise RuntimeError("Pinned public API standard bytes changed; review adoption explicitly")
    run([sys.executable, "eng/verify_db_scope.py"], "database-scope")
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests/Tooling", "-v"], "build-tool-tests")
    run(["cargo", "fmt", "--all", "--", "--check"], "rust-format")
    run(["cargo", "clippy", "--workspace", "--all-targets", "--locked", "--", "-D", "warnings"], "clippy")
    run(["cargo", "test", "--workspace", "--release", "--locked"], "rust-tests")
    manifest = native()
    msbuild = ["-m:1", "-nr:false", "-p:UseSharedCompilation=false"]
    run(["dotnet", "restore", "NativeWeave.slnx", "--locked-mode", "--disable-parallel", *msbuild], "restore")
    run(["dotnet", "build", "NativeWeave.slnx", "-c", "Release", "--no-restore", *msbuild], "build")
    run(["dotnet", "format", "NativeWeave.slnx", "--verify-no-changes", "--no-restore"], "dotnet-format")
    for component in ("core",):
        run([sys.executable, "src/Build.Integration/compose_docs.py", "--config",
             f"src/Build.Integration/api/{component}.json", "--output", f"artifacts/docs/{component}-site"],
            component + "-api-docs")
    try:
        run([sys.executable, "eng/database_regressions.py", "--design", design, "--plan", plan,
             "--output", OUTPUT / "regressions"], "database-regressions")
    finally:
        export_fixture_results(OUTPUT / "regressions", OUTPUT / "regression-evidence")
    pack(version, manifest)
    for name, driver in (("database-lifecycle", "tests/Verification.EndToEnd/api_probe.py"),
                         ("database-business", "tests/Reference.TaskService/package_probe.py")):
        external = ROOT.parent / "_consumers" / name
        try:
            run([sys.executable, driver, "--feed", OUTPUT / "prepared/candidate/feed",
                 "--version", version + ".2", "--output", external], name)
        finally:
            export_fixture_results(external, OUTPUT / name)
    consume("local")
    run(["git", "diff", "--check"], "diff-check")
    if run(["git", "status", "--porcelain"], "final-status").strip() or source() != initial:
        raise RuntimeError("Source or dependency locks changed during verification")
    report = {"task": "DB-Scope-01", "status": "passed", "rid": "linux-x64", "source": initial,
              "versionBase": version, "nativeManifestSha256": digest(manifest),
              "candidateManifestSha256": digest(OUTPUT / "prepared/manifest.json"),
              "checks": ["scope", "rustfmt", "clippy", "rust-workspace-tests", "locked-restore",
                         "managed-workspace-build", "dotnet-format", "compiled-api-and-xml",
                         "postgresql-and-sqlite-regressions", "nuget-closure", "external-fluent-dto-jit-and-aot"],
              "pristineMachine": False, "independentReview": False, "publiclyPublished": False}
    (ARTIFACTS / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: retained database workspaces, actual PostgreSQL/SQLite, package Fluent DTO and Native AOT consumers.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["native", "pack", "verify", "consume"])
    parser.add_argument("--version", default="0.1.0-db-scope.1")
    parser.add_argument("--design", type=Path, default=ARTIFACTS / "frozen-design")
    parser.add_argument("--plan", type=Path, default=ARTIFACTS / "frozen-plan")
    parser.add_argument("--consumer-environment", choices=["local", "pristine"], default="pristine")
    args = parser.parse_args()
    if (platform.system(), platform.machine().lower()) != ("Linux", "x86_64"):
        parser.error("This database acceptance row is Linux x64 only")
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*", args.version):
        parser.error("Use a canonical prerelease version base")
    ARTIFACTS.mkdir(exist_ok=True)
    if args.command == "native":
        native()
    elif args.command == "verify":
        verify(args.version, args.design.resolve(), args.plan.resolve())
    elif args.command == "consume":
        consume(args.consumer_environment)
    else:
        pack(args.version, native())


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
