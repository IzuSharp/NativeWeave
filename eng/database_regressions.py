#!/usr/bin/env python3
"""Execute retained database tests against real providers; never accept a missing service."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

import build

ROOT = build.ROOT
FLAGS = ["-m:1", "-nr:false", "-p:UseSharedCompilation=false"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--postgres-bin", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    build.LOGS = output / "logs"
    pg = args.postgres_bin or Path(os.environ.get("NW_POSTGRES_BIN", ""))
    if not (pg / "postgres").is_file():
        found = shutil.which("postgres")
        if not found:
            raise RuntimeError("PostgreSQL 18 server tools are required for the retained TLS/failure oracles")
        pg = Path(found).resolve().parent
    pg = pg.resolve()
    design = args.design.resolve()
    if not os.environ.get("NW_TEST_POSTGRES"):
        raise RuntimeError("NW_TEST_POSTGRES is required")
    env = os.environ.copy()
    env["NATIVEWEAVE_TEST_POSTGRES_URL"] = env["NW_TEST_POSTGRES"]
    env.update(DOTNET_CLI_USE_MSBUILD_SERVER="0", MSBUILDDISABLENODEREUSE="1")
    records = []
    initial = build.source()

    def run(label, command):
        result = build.run(command, label, env=env)
        log = build.LOGS / (label + ".log")
        records.append({"name": label, "exitCode": 0, "log": str(log.relative_to(output)),
                        "sha256": build.digest(log)})
        (output / "commands.json").write_text(json.dumps(records, indent=2) + "\n")
        return result

    def component(name, *extra):
        run(name.lower(), [sys.executable, f"tests/{name}/verify.py", "--output", output / name, *extra])

    def run_isolated(label, command):
        # These full suites own fixed tables and migration ledgers. Preserve their
        # fresh-database precondition independently for each runtime/process cell.
        run(label, [sys.executable, "tests/Data.NativeHost/run.py", "--postgres-bin", pg,
                    "--output", output / "postgres" / label, "--", *command])

    version = run("postgres-version", [pg / "psql", env["NW_TEST_POSTGRES"], "-X", "-At", "-v", "ON_ERROR_STOP=1",
                                       "-c", "SHOW server_version"])
    if not version.strip().startswith("18."):
        raise RuntimeError("The actual regression server must be PostgreSQL 18")
    run("canonical-query-abi", [sys.executable, "tests/Query.Binding/generate.py", "--check", "--design", design])
    component("Interop.Negotiation", "--plan-root", args.plan.resolve(), "--design-root", design)
    component("Interop.Execution")
    run("api-tool-negative-contracts", [sys.executable, "tests/Build.Integration/verify_docs.py",
                                       "--output", output / "api-tool"])
    run("packaging-task-api", ["dotnet", "run", "--project", "tests/Packaging.Release/ApiCheck", "-c", "Release",
                               "--no-build", "--", output / "packaging-task-reference.md"])
    component("Data.Abstractions")
    component("Data.Sqlite", "--design", design)
    # Existing provider tests include real TLS policy and actual connection failures.
    run("postgres-fixture-fetch", ["cargo", "fetch", "--locked", "--manifest-path", "tests/Data.Postgres/native/Cargo.toml"])
    component("Data.Postgres", "--postgres-bin", pg, "--design-root", design)
    component("Data.Transactions", "--design", design)
    component("Data.Streaming", "--design-root", design)
    component("Data.Codecs")
    run("binding-fixture-fetch", ["cargo", "fetch", "--locked", "--manifest-path", "tests/Query.Binding/native/Cargo.toml"])
    component("Query.Binding", "--design", design)

    # The internal cross-provider query oracle uses a maintainer-only combined Host.
    # Its binary is never added to either provider package.
    run("query-fixture-fetch", ["cargo", "fetch", "--locked", "--manifest-path", "tests/Query.Native/native/Cargo.toml"])
    run("combined-host", ["cargo", "build", "--locked", "--release", "-p", "nativeweave-database-host"])
    component("Query.Native", "--design", design, "--postgres-bin", pg, "--host-source", ROOT,
              "--native-module", ROOT / "target/release/libnativeweave_database_host.so")

    # These are the unchanged full executable suites, not smoke-test substitutes.
    # Each ordinary managed build resolves the independently staged provider assets.
    suites = [
        ("Data.NativeHost", "NativeWeave.Data.NativeHost.Tests", []),
        ("Data.Migrations", "NativeWeave.Data.Migrations.Tests", []),
        ("Data.Materialization", "NativeWeave.Data.Materialization.Tests", ["results"]),
        ("Query.Fluent", "NativeWeave.Query.Fluent.Tests", ["results"]),
        ("Orm.Relations", "NativeWeave.Orm.Relations.Tests", []),
    ]
    for name, assembly, parameters in suites:
        project = ROOT / "tests" / name / (assembly + ".csproj")
        run(name + "-restore", ["dotnet", "restore", project, "--locked-mode", *FLAGS])
        run(name + "-build", ["dotnet", "build", project, "-c", "Release", "--no-restore", *FLAGS])
        jit_args = [output / name / "jit"] if parameters else []
        run_isolated(name + "-jit", ["dotnet", project.parent / "bin/Release/net11.0" / (assembly + ".dll"), *jit_args])
        publish = output / name / "aot"
        run(name + "-aot-restore", ["dotnet", "restore", project, "--locked-mode", "-r", "linux-x64", "-p:PublishAot=true", *FLAGS])
        run(name + "-aot-publish", ["dotnet", "publish", project, "-c", "Release", "-r", "linux-x64",
                                   "-p:PublishAot=true", "--no-restore", "-p:IlcTreatWarningsAsErrors=true", *FLAGS, "-o", publish])
        executable = publish / assembly
        if executable.read_bytes()[:4] != b"\x7fELF" or executable.with_suffix(".dll").exists():
            raise RuntimeError("Expected an actual standalone Native AOT executable")
        aot_args = [output / name / "aot-results", "--require-aot"] if parameters else (
            ["--require-aot"] if name == "Orm.Relations" else [])
        run_isolated(name + "-aot", [executable, *aot_args])
        if name == "Data.Migrations":
            for mode, command in [
                ("jit", ["dotnet", project.parent / "bin/Release/net11.0" / (assembly + ".dll")]),
                ("aot", [executable]),
            ]:
                run_isolated(name + "-process-" + mode, [sys.executable, "tests/Data.Migrations/cross_process.py",
                     "--postgres-bin", pg, "--output", output / name / ("process-" + mode), "--", *command])

    tool = ROOT / "src/Build.Integration/ApiReference/bin/Release/net11.0/NativeWeave.ApiReference.dll"
    # Read the declared assembly name rather than assuming the project filename.
    if not tool.is_file():
        directory = tool.parent
        tool = next(p for p in directory.glob("*.dll") if p.with_suffix(".runtimeconfig.json").is_file())
    for name in ("Data.Migrations", "Orm.Relations"):
        run(name + "-api", [sys.executable, f"tests/{name}/api.py", "--design", design, "--tool", tool])
    run("relations-type-errors", [sys.executable, "tests/Orm.Relations/compile_negative.py"])
    run("fluent-api", ["dotnet", "tests/Query.Fluent/ApiCheck/bin/Release/net11.0/NativeWeave.Query.Fluent.ApiCheck.dll",
                      ROOT, design, os.environ["DOTNET_ROOT"]])
    run("query-generator", ["dotnet", "tests/Query.Generator/bin/Release/net11.0/NativeWeave.Query.Generator.Tests.dll"])
    run("query-generator-api", ["dotnet", "tests/Query.Generator/ApiCheck/bin/Release/net11.0/NativeWeave.Query.Generator.ApiCheck.dll",
                               ROOT, design, os.environ["DOTNET_ROOT"]])
    if build.source() != initial:
        raise RuntimeError("Source identity changed during regression execution")
    (output / "result.json").write_text(json.dumps({"task": "DB-Scope-01", "status": "passed",
        "source": initial, "platform": "linux-x64", "postgresVersion": version.strip(),
        "providers": ["sqlite", "postgresql"], "modes": ["jit", "aot"], "commands": records,
        "performanceWork": False}, indent=2) + "\n")


if __name__ == "__main__":
    main()
