#!/usr/bin/env python3
"""Build two immutable, local-only twelve-package database closures."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

import inventory
from model import (CHANGED, COMMON, ENGINES, IDS, LEAVES, MANAGED, REPOSITORY, RID, ROOT, TASK,
                   graph, json_bytes, load_manifest, module, save, sha, subclosure, versions)

TASK_PROJECT = ROOT / "src/Packaging.Release/BuildTasks/NativeWeave.Packaging.Tasks.csproj"
FLAGS = ["-p:UseSharedCompilation=false", "-nr:false", "-m:1"]
PROJECT_FILES = {
    "NativeWeave.Interop.Abi": "Interop.Abi.csproj",
    "NativeWeave.Core": "NativeWeave.Core.csproj",
    "NativeWeave.Data": "NativeWeave.Data.csproj",
    "NativeWeave.Database.Transactions": "NativeWeave.Database.Transactions.csproj",
    "NativeWeave.Data.Streaming": "NativeWeave.Data.Streaming.csproj",
    "NativeWeave.Query.Binding": "NativeWeave.Query.Binding.csproj",
    "NativeWeave.Query.Generator": "NativeWeave.Query.Generator.csproj",
    "NativeWeave.Database": "NativeWeave.Database.csproj",
    "NativeWeave.Database.Sqlite": "NativeWeave.Database.Sqlite.csproj",
    "NativeWeave.Database.PostgreSql": "NativeWeave.Database.PostgreSql.csproj",
}


def managed_project(identity):
    """Resolve the checked-in project filename independently of its package ID."""
    return ROOT / MANAGED[identity][0] / PROJECT_FILES[identity]


class Commands:
    def __init__(self, output):
        self.output, self.records = Path(output), []
        (self.output / "logs").mkdir(parents=True, exist_ok=True)
        self.environment = os.environ.copy()
        self.environment.update(DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_CLI_USE_MSBUILD_SERVER="0",
                                MSBUILDDISABLENODEREUSE="1")

    def run(self, label, command, timeout=600):
        arguments = list(map(str, command))
        result = subprocess.run(arguments, cwd=ROOT, env=self.environment, capture_output=True, timeout=timeout)
        row = {"label": label, "argv": arguments, "exitCode": result.returncode}
        for suffix, data in (("stdout", result.stdout), ("stderr", result.stderr)):
            path = self.output / "logs" / (label + "." + suffix)
            path.write_bytes(data)
            row[suffix + "Sha256"] = sha(path)
        self.records.append(row)
        save(self.output / "commands.json", self.records)
        print(label, result.returncode, flush=True)
        if result.returncode:
            raise RuntimeError(label + ": " + (result.stdout + result.stderr).decode(errors="replace")[-6000:])
        return result.stdout.decode()


def managed_entries(identity):
    directory = ROOT / MANAGED[identity][0]
    result = {"LICENSE": ROOT / "LICENSE"}
    if identity == "NativeWeave.Query.Generator":
        result["tools/roslyn/" + identity + ".dll"] = directory / "bin/Release/netstandard2.0" / (identity + ".dll")
        result["buildTransitive/" + identity + ".targets"] = directory / "buildTransitive" / (identity + ".targets")
    else:
        for suffix in (".dll", ".xml"):
            result["lib/net11.0/" + identity + suffix] = directory / "bin/Release/net11.0" / (identity + suffix)
    return result


def build_managed(commands, version, native, candidate=False):
    asset_flags = ["-p:" + property_name + "=" + str(native[engine]["path"]) for property_name, engine in (
        ("NativeWeaveSqliteAssetPath", "database.sqlite"), ("NativeWeavePostgresAssetPath", "database.postgresql"))]
    selected = CHANGED if candidate else tuple(MANAGED)
    label = "candidate" if candidate else "previous"
    for identity in selected:
        project = managed_project(identity)
        commands.run(label + "-" + identity + "-build", ["dotnet", "build", project, "-c", "Release", "--no-restore",
                     "-p:Version=" + version, "-p:BuildProjectReferences=false", *asset_flags, *FLAGS])
    # This catches stale hardcoded profile versions before packaging, without
    # substituting the later actual runtime bootstrap/consumer checks.
    for engine, (facade, _, _, _) in ENGINES.items():
        record_path = ROOT / MANAGED[facade][0] / "obj/Release/net11.0" / ("NativeWeave." + engine + ".assets.json")
        record = json.loads(record_path.read_text())
        if record["packageId"] != facade or record["packageVersion"] != version or record["sha256"] != native[engine]["sha256"]:
            raise ValueError("Generated facade identity is stale: " + facade)


def compose(output, label, version_map, native_build, native, source_commit, previous=None):
    """Pack already-built bytes; the caller owns exact build/version ordering."""
    output = Path(output)
    folder, feed = output / label, output / label / "feed"
    feed.mkdir(parents=True, exist_ok=False)
    packing = module("domain_existing_packer", "src/Packaging.Linux/packages.py")
    compat = module("domain_existing_compatibility", "src/Verification.Compatibility/compatibility.py")
    closure = graph(version_map, native)
    rows = {item["id"]: item for item in closure["packages"]}
    records, packages = [], []
    for identity in IDS:
        version = version_map[identity]
        dependencies = rows[identity]["dependencies"]
        source = source_commit
        if previous is not None and identity in COMMON:
            original = next(item for item in previous["packages"] if item["id"] == identity)
            archive = feed / Path(original["path"]).name
            shutil.copyfile(output / original["path"], archive)
            if sha(archive) != original["sha256"]:
                raise ValueError("Common archive copy changed bytes")
        else:
            if identity in LEAVES:
                engine = LEAVES[identity]
                descriptor = rows[identity]["nativeAssets"][0]
                source = native_build["sourceCommit"]
                entries = {"LICENSE": ROOT / "LICENSE", **native[engine]["entries"],
                           descriptor["sourcePath"]: native[engine]["path"]}
                native_manifest = {"schemaVersion": 1, "packageId": identity, "packageVersion": version, "rid": RID,
                    "nativePath": descriptor["sourcePath"], "nativeSha256": descriptor["sha256"], "abiMajor": 1,
                    "abiMinor": 0, "sourceCommit": source, "sourceDirty": False,
                    "packagingProducerCommit": source_commit, "cpuBaseline": "x86-64",
                    "cargoLockSha256": native_build["cargoLockSha256"],
                    "dependencyInventorySha256": sha_bytes(entries["nativeweave/dependencies.json"]),
                    "scope": "local-only; signer authentication and public release are not asserted"}
                entries["nativeweave/manifest.json"] = json_bytes(native_manifest)
            else:
                entries = managed_entries(identity)
                if identity in CHANGED:
                    target = ROOT / "src/Packaging.Release/buildTransitive/NativeWeave.Packaging.targets"
                    entries["buildTransitive/" + identity + ".targets"] = target
                    entries["nativeweave/closure.json"] = json_bytes(subclosure(closure, identity))
                    for suffix in (".dll", ".xml"):
                        entries["tools/net11.0/NativeWeave.Packaging.Tasks" + suffix] = TASK_PROJECT.parent / "bin/Release/net11.0" / ("NativeWeave.Packaging.Tasks" + suffix)
            archive = packing.pack(feed, identity, version, entries, dependencies, (REPOSITORY, source))
        record = {"id": identity, "version": version, "dependencies": dependencies,
                  "unsigned_entries": compat.package_entries(archive), "upload_archive_sha256": sha(archive),
                  "source_commit": source, "repository": REPOSITORY}
        handoff = {"id": identity, "version": version, "dependencies": dependencies, "externalDependencies": {},
                   "path": archive.relative_to(output).as_posix(), "sha256": record["upload_archive_sha256"], "sourceCommit": source}
        if identity in LEAVES:
            descriptor = rows[identity]["nativeAssets"][0]
            record["native"] = {"path": descriptor["sourcePath"], "sha256": descriptor["sha256"], "rid": RID, "abi_major": 1}
            handoff["native"] = {key: value for key, value in descriptor.items() if key != "sourcePath"}
            handoff["native"]["path"] = descriptor["sourcePath"]
        records.append(record)
        packages.append(handoff)
    release = {"schema_version": 1, "source_commit": source_commit, "source_dirty": False, "rid": RID,
               "builder_identity": "nativeweave-local-reviewed-staging", "local_unsigned_only": True, "packages": records}
    compat.validate_closure(release, {item["id"]: output / item["path"] for item in packages})
    save(folder / "closure.json", closure)
    save(folder / "release.json", release)
    return {"version": version_map["NativeWeave.Database"], "feed": feed.relative_to(output).as_posix(),
            "buildClosure": (folder / "closure.json").relative_to(output).as_posix(),
            "releaseRecord": (folder / "release.json").relative_to(output).as_posix(), "packages": packages}


def sha_bytes(value):
    import hashlib
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous-version", required=True)
    parser.add_argument("--candidate-version", required=True)
    parser.add_argument("--native-manifest", type=Path, required=True)
    args = parser.parse_args()
    previous_versions = versions(args.previous_version)
    candidate_versions = versions(args.previous_version, args.candidate_version)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    commands = Commands(output)
    source = commands.run("source-commit", ["git", "rev-parse", "HEAD"]).strip()
    if commands.run("source-state", ["git", "status", "--porcelain", "--untracked-files=normal"]).strip():
        raise ValueError("Final database package provenance requires a clean committed source")
    names = commands.run("source-inventory", ["git", "ls-files", "--", "src", "Directory.Build.props", "Directory.Build.targets",
                         "Cargo.toml", "Cargo.lock", "global.json", "rust-toolchain.toml"]).splitlines()
    source_files = {name: sha(ROOT / name) for name in names}
    if commands.run("sdk", ["dotnet", "--version"]).strip() != "11.0.100":
        raise ValueError("Use the pinned .NET SDK 11.0.100")
    native_build, native = inventory.collect(args.native_manifest)
    save(output / "native-build-input.json", {key: value for key, value in native_build.items()
         if key not in ("cargoHome", "CargoHome", "rustSysroot", "assets", "builds")})
    for engine, value in native.items():
        save(output / "native" / (engine + ".json"), value["inventory"])
    # Restore the committed project graph at its existing project identities;
    # private facade Version changes are compiled later with --no-restore.
    projects = [managed_project(identity) for identity in MANAGED]
    for index, project in enumerate([*projects, TASK_PROJECT]):
        commands.run("restore-" + str(index), ["dotnet", "restore", project, "--locked-mode", *FLAGS])
    commands.run("packaging-task-build", ["dotnet", "build", TASK_PROJECT, "-c", "Release", "--no-restore", *FLAGS])
    build_managed(commands, args.previous_version, native)
    previous = compose(output, "previous", previous_versions, native_build, native, source)
    common_files = {str(path): sha(path) for identity in COMMON for path in managed_entries(identity).values()}
    build_managed(commands, args.candidate_version, native, candidate=True)
    if any(sha(Path(path)) != expected for path, expected in common_files.items()):
        raise ValueError("Candidate build unexpectedly rebuilt retained common bytes")
    candidate = compose(output, "candidate", candidate_versions, native_build, native, source, previous)
    final_source = commands.run("final-source-commit", ["git", "rev-parse", "HEAD"]).strip()
    if (commands.run("final-source-state", ["git", "status", "--porcelain", "--untracked-files=normal"]).strip()
            or final_source != source or {name: sha(ROOT / name) for name in names} != source_files):
        raise ValueError("Source changed while constructing database packages")
    save(output / "source-inventory.json", {"sourceCommit": source, "files": source_files})
    manifest = {"schemaVersion": 1, "task": TASK, "scope": "local-only", "rid": RID, "sourceCommit": source, "sourceDirty": False,
                "nativeSourceCommit": native_build["sourceCommit"], "nativeInputManifestSha256": sha(args.native_manifest),
                "sourceInventory": "source-inventory.json", "previous": previous, "candidate": candidate,
                "publicDomainReleaseAccepted": False, "newDomainSignerAuthenticated": False,
                "historicalMeasurementTransfer": False,
                "statement": "Fresh local CI candidate identities. Historical B22/B23 execution artifacts and numbers remain separate; source/build applicability is reviewed independently."}
    save(output / "manifest.json", manifest)
    load_manifest(output / "manifest.json")
    evidence = output / "evidence"
    evidence.mkdir()
    for name in ("manifest.json", "commands.json", "source-inventory.json", "native-build-input.json"):
        shutil.copyfile(output / name, evidence / name)
    for name in ("previous", "candidate"):
        (evidence / name).mkdir()
        for filename in ("closure.json", "release.json"):
            shutil.copyfile(output / name / filename, evidence / name / filename)
    for engine, value in native.items():
        save(evidence / "native" / (engine + ".json"), value["inventory"])
        for name, data in value["entries"].items():
            if name.startswith("nativeweave/licenses/"):
                path = evidence / "native" / engine / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    save(evidence / "evidence-index.json", {"schemaVersion": 1,
         "scope": "Source/closure/native/license audit only; excludes package payloads, test databases, private keys and consumer caches.",
         "files": {path.relative_to(evidence).as_posix(): sha(path) for path in sorted(evidence.rglob("*")) if path.is_file()}})
    print("Prepared two exact twelve-package database closures; actual destination/pristine/runtime consumption remains required.", flush=True)


if __name__ == "__main__":
    main()
