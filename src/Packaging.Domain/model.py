"""The database-only package graph and portable local handoff contract.

Internal maintainer orchestration only. Application builds use the existing
packaging task; this module neither runs Cargo nor publishes to a registry.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "https://github.com/IzuSharp/NativeWeave"
RID = "linux-x64"
TASK = "DB-Scope-01"
COMMON = (
    "NativeWeave.Interop.Abi", "NativeWeave.Core", "NativeWeave.Data",
    "NativeWeave.Database.Transactions", "NativeWeave.Data.Streaming",
    "NativeWeave.Query.Binding", "NativeWeave.Query.Generator",
)
MANAGED = {
    "NativeWeave.Interop.Abi": ("src/Interop.Abi", []),
    "NativeWeave.Core": ("src/NativeWeave.Core", ["NativeWeave.Interop.Abi"]),
    "NativeWeave.Data": ("src/Data.Abstractions", []),
    "NativeWeave.Database.Transactions": ("src/Data.Transactions", ["NativeWeave.Data"]),
    "NativeWeave.Data.Streaming": ("src/Data.Streaming", ["NativeWeave.Data"]),
    "NativeWeave.Query.Binding": ("src/Query.Binding", ["NativeWeave.Data", "NativeWeave.Interop.Abi"]),
    "NativeWeave.Query.Generator": ("src/Query.Generator", []),
    "NativeWeave.Database": ("src/Data.NativeHost", ["NativeWeave.Core", "NativeWeave.Data", "NativeWeave.Database.Transactions", "NativeWeave.Data.Streaming", "NativeWeave.Query.Binding"]),
    "NativeWeave.Database.Sqlite": ("src/Data.Sqlite", ["NativeWeave.Core", "NativeWeave.Data", "NativeWeave.Database", "NativeWeave.Query.Generator", "NativeWeave.Database.Sqlite.Native"]),
    "NativeWeave.Database.PostgreSql": ("src/Data.Postgres", ["NativeWeave.Core", "NativeWeave.Data", "NativeWeave.Database", "NativeWeave.Query.Generator", "NativeWeave.Database.PostgreSql.Native"]),
}
DATABASE_CAPABILITIES = [
    "db.metadata.v1", "db.query.v1", "db.transactions.v1", "db.savepoints.v1", "db.streaming.v1",
    "db.migrations.v1", "db.schema.read.v1", "db.returning.v1", "db.upsert.v1", "db.cte.v1",
    "db.window.v1", "db.row-lock.v1", "db.null-safe-equality.v1", "db.json.v1", "db.decimal.numeric.v1",
    "db.decimal.text.v1", "db.fixed-money.v1", "db.relationships.explicit.v1", "db.prepared-shape.v1",
    "db.bulk-batches.v1", "db.dynamic-fields.v1", "db.recursive-cte.v1", "db.set-operations.v1",
    "db.scalar-codecs.v1", "db.sql.expert.v1",
]
ENGINES = {
    "database.sqlite": ("NativeWeave.Database.Sqlite", "libnw_database_sqlite.so", "nativeweave-database-host", DATABASE_CAPABILITIES),
    "database.postgresql": ("NativeWeave.Database.PostgreSql", "libnw_database_postgresql.so", "nativeweave-database-host", DATABASE_CAPABILITIES),
}
LEAVES = {value[0] + ".Native": engine for engine, value in ENGINES.items()}
IDS = tuple(sorted(set(MANAGED) | set(LEAVES)))
CHANGED = tuple(identity for identity in MANAGED if identity not in COMMON)
RETIRED_PACKAGE_PREFIXES = (
    "nativeweave.server", "nativeweave.protocols", "nativeweave.engines",
    "nativeweave.helloworld", "nativeweave.conformance", "nativeweave.verification.extensionproof",
    "grpc.", "google.protobuf", "modelcontextprotocol",
)


def require_database_package(identity):
    """Reject retired products even if an otherwise valid graph includes one."""
    name = identity.lower()
    if name.startswith(RETIRED_PACKAGE_PREFIXES):
        raise ValueError("Retired non-database package is present: " + identity)
    if name.startswith("nativeweave.") and name not in {item.lower() for item in IDS}:
        raise ValueError("Undeclared NativeWeave database package: " + identity)


def validate_database_payload(package, expected):
    """Check the whole nuspec, not only the owned subset of dependency edges."""
    require_database_package(expected["id"])
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        metadata = ET.fromstring(archive.read(expected["id"] + ".nuspec")).find("{*}metadata")
        dependencies = {}
        for item in metadata.findall(".//{*}dependency"):
            identity = item.attrib["id"]
            require_database_package(identity)
            if identity in dependencies:
                raise ValueError("Duplicate database package dependency: " + identity)
            dependencies[identity] = item.attrib["version"]
        if dependencies != {name: "[" + version + "]" for name, version in expected["dependencies"].items()}:
            raise ValueError("Database nuspec has undeclared dependencies")
        if metadata.findall(".//{*}frameworkReference") or metadata.findall(".//{*}frameworkAssembly"):
            raise ValueError("Database packages must not add a shared server framework")
        native = {name for name in names if name.endswith((".so", ".dylib")) or name.startswith("runtimes/")}
        expected_native = {expected["native"]["path"]} if expected.get("native") else set()
        if native != expected_native:
            raise ValueError("Database package contains an undeclared native asset")
        libraries = {Path(name).name for name in names if name.startswith("lib/") and name.endswith(".dll")}
        expected_libraries = ({expected["id"] + ".dll"}
                              if expected["id"] in MANAGED and expected["id"] != "NativeWeave.Query.Generator" else set())
        if libraries != expected_libraries:
            raise ValueError("Database package contains an undeclared runtime assembly")
    return {"dependencies": dependencies, "managedRuntimeAssemblies": sorted(libraries), "nativeAssets": sorted(native)}


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def relative_file(base, name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("Expected a canonical relative artifact path")
    if Path(name).is_absolute() or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("Artifact path escapes the manifest")
    path = Path(base) / name
    if not path.resolve().is_relative_to(Path(base).resolve()):
        raise ValueError("Artifact symlink escapes the manifest")
    return path


def versions(previous, candidate=None):
    for value in (previous, candidate or previous):
        if not re.fullmatch(r"\d+\.\d+\.\d+-[0-9A-Za-z.-]+", value):
            raise ValueError("Database candidates require an exact, fresh prerelease version")
        if value == "0.1.0-preview.1":
            raise ValueError("Historical preview.1 identities must remain immutable")
    if candidate is not None and previous == candidate:
        raise ValueError("Previous and candidate versions must differ")
    return {identity: previous if identity in COMMON or candidate is None else candidate for identity in IDS}


def graph(version_map, native):
    result = []
    for identity in IDS:
        item = {"id": identity, "version": version_map[identity], "dependencies": {}}
        if identity in MANAGED:
            item["dependencies"] = {child: version_map[child] for child in MANAGED[identity][1]}
        else:
            engine = LEAVES[identity]
            facade, basename, _, capabilities = ENGINES[engine]
            item["nativeAssets"] = [{
                "engineId": engine, "facadePackageId": facade, "facadePackageVersion": version_map[facade],
                "rid": RID, "sourcePath": "runtimes/" + RID + "/native/" + basename,
                "sha256": native[engine]["sha256"], "abiMajor": 1, "abiMinor": 0,
                "capabilities": {name: bit for bit, name in enumerate(capabilities)}, "cpuBaseline": "x86-64",
            }]
        result.append(item)
    return {"schemaVersion": 1, "packages": result}


def subclosure(closure, identity):
    index = {item["id"]: item for item in closure["packages"]}
    visited = set()
    def visit(name):
        if name not in visited:
            visited.add(name)
            for child in index[name]["dependencies"]:
                visit(child)
    visit(identity)
    return {"schemaVersion": 1, "packages": [index[name] for name in sorted(visited)]}


def load_manifest(path):
    path = Path(path).resolve()
    manifest = json.loads(path.read_text())
    if (manifest.get("schemaVersion"), manifest.get("task"), manifest.get("scope"), manifest.get("rid")) != (1, TASK, "local-only", RID):
        raise ValueError("Unknown database manifest, task or scope")
    if manifest.get("sourceDirty") is not False or not re.fullmatch(r"[0-9a-f]{40}", manifest.get("sourceCommit", "")):
        raise ValueError("Database candidates need a clean, exact producer source")
    compat = module("domain_compatibility", "src/Verification.Compatibility/compatibility.py")
    for name in ("previous", "candidate"):
        closure = manifest[name]
        items = closure["packages"]
        if sorted(item["id"] for item in items) != list(IDS):
            raise ValueError("Database candidates require exactly the twelve owned package IDs")
        record = json.loads(relative_file(path.parent, closure["releaseRecord"]).read_text())
        packages = {item["id"]: relative_file(path.parent, item["path"]) for item in items}
        if record["source_commit"] != manifest["sourceCommit"] or record["source_dirty"] is not False:
            raise ValueError("Producer and release source disagree")
        expected = {item["id"]: item for item in record["packages"]}
        for item in items:
            require_database_package(item["id"])
            if item.get("externalDependencies"):
                raise ValueError("The database closure has no external managed runtime dependencies")
            release_item = expected[item["id"]]
            if any(item[key] != release_item[key] for key in ("id", "version", "dependencies")):
                raise ValueError("Handoff and release package graphs disagree")
            if sha(packages[item["id"]]) != item["sha256"] or item["sha256"] != release_item["upload_archive_sha256"]:
                raise ValueError("Database archive identity changed")
        compat.validate_closure(record, packages)
        for item in record["packages"]:
            validate_database_payload(packages[item["id"]], item)
    previous = {item["id"]: item for item in manifest["previous"]["packages"]}
    candidate = {item["id"]: item for item in manifest["candidate"]["packages"]}
    expected_previous = versions(manifest["previous"]["version"])
    expected_candidate = versions(manifest["previous"]["version"], manifest["candidate"]["version"])
    for identity in IDS:
        if previous[identity]["version"] != expected_previous[identity] or candidate[identity]["version"] != expected_candidate[identity]:
            raise ValueError("Database version split differs from seven common and five changed packages")
        if identity in COMMON and previous[identity]["sha256"] != candidate[identity]["sha256"]:
            raise ValueError("A retained common archive was rebuilt or changed")
    return manifest
