#!/usr/bin/env python3
"""Verify the current product build graph keeps Database Host and excludes retired products."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "native/database/host", "native/database/postgres", "native/database/sqlite",
    "native/database/query", "native/database/relations", "native/database/migrations",
    "src/Data.NativeHost", "src/Data.Postgres", "src/Data.Sqlite", "src/Data.Transactions",
    "src/Data.Streaming", "src/Data.Materialization", "src/Query.Fluent", "src/Query.Generator",
    "src/Query.Binding", "src/Orm.Relations", "src/NativeWeave.Core", "src/Interop.Abi",
]
REMOVED = [
    "native/server", "native/protocols", "native/engines", "native/hello-world",
    "src/Server.Application", "src/Server.Diagnostics", "src/Server.Native", "src/Server.Streaming",
    "src/Protocols.Grpc", "src/Protocols.Mcp", "src/Engines.SyncProof", "src/Engines.AsyncProof",
    "src/Verification.ExtensionProof", "src/NativeWeave.HelloWorld", "tools/ApiDocs",
    "src/Generators.Model", "src/Generators.CSharp", "src/Generators.Rust", "src/Analyzers",
    "src/Benchmarks.Harness", "src/Benchmarks.Domain", "src/Tooling.EngineScaffold",
]
FORBIDDEN = ("NativeWeave.Server", "NativeWeave.Protocols", "NativeWeave.HelloWorld",
             "NativeWeave.Engines", "NativeWeave.Mcp", "NativeWeave.Grpc")
EXPECTED_PACKAGES = {
    "NativeWeave.Interop.Abi", "NativeWeave.Core", "NativeWeave.Data",
    "NativeWeave.Database.Transactions", "NativeWeave.Data.Streaming", "NativeWeave.Query.Binding",
    "NativeWeave.Query.Generator", "NativeWeave.Database", "NativeWeave.Database.Sqlite",
    "NativeWeave.Database.PostgreSql", "NativeWeave.Database.Sqlite.Native", "NativeWeave.Database.PostgreSql.Native",
}


def check():
    for name in REQUIRED:
        assert (ROOT / name).is_dir(), "Retained database dependency is missing: " + name
    for name in REMOVED:
        assert not (ROOT / name).exists(), "Retired product still exists: " + name
    cargo = tomllib.loads((ROOT / "Cargo.toml").read_text())
    for member in cargo["workspace"]["members"]:
        assert member.startswith(("native/database/", "native/interop/")) or member in (
            "tests/Interop.Errors/native", "src/Verification.Interop/native"), member
        assert (ROOT / member / "Cargo.toml").is_file(), member
    solution = ET.parse(ROOT / "NativeWeave.slnx").getroot()
    for node in solution.iter("Project"):
        assert (ROOT / node.attrib["Path"]).is_file(), node.attrib
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "*.csproj"], cwd=ROOT).decode().split("\0")
    count = 0
    for name in tracked:
        path = ROOT / name
        if not name or not path.is_file():
            continue
        for node in ET.parse(path).iter():
            if node.tag in ("PackageReference", "ProjectReference"):
                include = node.get("Include", "")
                assert not any(x in include for x in FORBIDDEN), (name, include)
                if node.tag == "ProjectReference" and "$(" not in include:
                    assert (path.parent / include).resolve().is_file(), (name, include)
        count += 1
    sys.path.insert(0, str(ROOT / "src/Packaging.Domain"))
    spec = importlib.util.spec_from_file_location("database_package_model", ROOT / "src/Packaging.Domain/model.py")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    assert set(model.MANAGED) | set(model.LEAVES) == EXPECTED_PACKAGES
    assert set(model.ENGINES) == {"database.sqlite", "database.postgresql"}
    print(json.dumps({"task": "DB-Scope-01", "status": "passed", "databaseHostRetained": True,
                      "cargoMembers": len(cargo["workspace"]["members"]), "managedProjects": count,
                      "databasePackages": sorted(EXPECTED_PACKAGES)}, indent=2))


if __name__ == "__main__":
    check()
