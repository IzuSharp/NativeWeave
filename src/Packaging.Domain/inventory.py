"""Bind native build inputs and preserve notices from checksum-verified sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib

from model import ENGINES, RID, ROOT, json_bytes, module, sha

SYSTEM_DEPENDENCIES = ["libc.so.6", "libgcc_s.so.1", "libm.so.6", "ld-linux-x86-64.so.2"]
NOTICE_NAMES = ("LICENSE", "LICENCE", "COPYING", "NOTICE", "COPYRIGHT")
NOTICE_DIRECTORIES = {"LICENSE", "LICENSES", "LICENCE", "LICENCES", "COPYING", "NOTICE", "NOTICES", "COPYRIGHT"}


def archive_notices(archive, checksum, name, version, license_file=None):
    """Read original text without extracting untrusted archive member paths."""
    archive = Path(archive)
    if sha(archive) != checksum:
        raise ValueError("Cargo archive checksum differs from Cargo.lock: " + name)
    prefix = name + "-" + version + "/"
    notices, sources = {}, {}
    with tarfile.open(archive, "r:*") as stream:
        members = {}
        for member in stream.getmembers():
            if member.isdir() and member.name.rstrip("/") == prefix.rstrip("/"):
                continue
            if not member.name.startswith(prefix):
                raise ValueError("Unexpected Cargo archive root: " + member.name)
            relative = member.name[len(prefix):]
            if member.isdir():
                relative = relative.rstrip("/")
            if not relative and member.isdir():
                continue
            if (not relative or "\\" in relative or ":" in relative
                    or any(part in ("", ".", "..") for part in relative.split("/"))):
                raise ValueError("Noncanonical Cargo archive path: " + member.name)
            if relative in members:
                raise ValueError("Duplicate Cargo archive member: " + relative)
            members[relative] = member
        def read(relative):
            member = members[relative]
            if not member.isfile() or member.size > 32 * 1024 * 1024:
                raise ValueError("Unbounded or linked Cargo license/source member: " + relative)
            return stream.extractfile(member).read()
        for relative in sorted(members):
            if members[relative].isdir():
                continue
            path = PurePosixPath(relative)
            basename = path.name.upper()
            in_notice_directory = any(part.upper() in NOTICE_DIRECTORIES for part in path.parts[:-1])
            if basename.startswith(NOTICE_NAMES) or in_notice_directory or relative == license_file:
                notices[relative] = read(relative)
        if license_file and license_file not in notices:
            raise ValueError("Declared Cargo license_file is missing: " + name)
        if name == "libsqlite3-sys":
            for relative in ("sqlite3/sqlite3.c", "sqlite3/sqlite3.h"):
                data = read(relative)
                sources[relative] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
                if relative.endswith(".h"):
                    end = data.index(b"*/") + 2
                    notices["sqlite3/original-header-notice.txt"] = data[:end]
                    sources[relative]["noticeExcerpt"] = {"offset": 0, "length": end}
                    for key in ("SQLITE_VERSION", "SQLITE_SOURCE_ID"):
                        match = re.search(rb'^#define\s+' + key.encode() + rb'\s+"([^"\r\n]+)"', data, re.M)
                        if match is None:
                            raise ValueError("Bundled SQLite source identity is missing")
                        sources[relative][key] = match[1].decode()
        if not notices:
            raise ValueError("Selected Cargo archive has no preserved license text: " + name)
    return notices, sources


def selected_packages(metadata, messages, root_name):
    """Separate selected compiler inputs from the wider metadata resolution graph."""
    packages = {item["id"]: item for item in metadata["packages"]}
    nodes = {item["id"]: item for item in metadata["resolve"]["nodes"]}
    roots = [key for key, item in packages.items() if item["name"] == root_name and item["source"] is None]
    if len(roots) != 1:
        raise ValueError("Native build metadata must identify one owned root: " + root_name)
    compiled = {}
    for item in messages:
        if item.get("reason") == "compiler-artifact":
            key = item["package_id"]
            if key not in packages:
                raise ValueError("Compiler artifact is absent from its metadata")
            selected = compiled.setdefault(key, {"features": set(), "kinds": set()})
            selected["features"].update(item.get("features", []))
            selected["kinds"].update(item["target"]["kind"])
    if roots[0] not in compiled:
        raise ValueError("Selected native root has no compiler-artifact record")
    roles, queue = {}, [(roots[0], "runtime-input")]
    while queue:
        key, role = queue.pop()
        if "proc-macro" in compiled.get(key, {}).get("kinds", set()):
            role = "build-input"
        if role in roles.setdefault(key, set()):
            continue
        roles[key].add(role)
        for edge in nodes[key]["deps"]:
            for kind in edge["dep_kinds"]:
                if kind["kind"] != "dev":
                    queue.append((edge["pkg"], "build-input" if kind["kind"] == "build" else role))
    selected = []
    for key in sorted(set(roles) & set(compiled)):
        selected.append({"package": packages[key], "roles": sorted(roles[key]),
                         "features": sorted(compiled[key]["features"]), "targetKinds": sorted(compiled[key]["kinds"])})
    return selected, sorted(set(roles) - set(compiled))


def crate_archive(cargo_home, name, version, checksum):
    matches = list((Path(cargo_home) / "registry/cache").glob("*/" + name + "-" + version + ".crate"))
    matching = [path for path in matches if sha(path) == checksum]
    if len(matching) != 1:
        raise ValueError("Expected one checksum-matching cached Cargo archive: " + name + "@" + version)
    return matching[0]


def collect(build_manifest_path):
    """Return exact native files and reusable per-engine inventory/package entries.

    The root's maintainer job owns Cargo execution. This function only reads its
    retained inputs/messages and inspects the resulting ELF files.
    """
    build_manifest_path = Path(build_manifest_path).resolve()
    build = json.loads(build_manifest_path.read_text())
    if ((build.get("schemaVersion"), build.get("rid"), build.get("target"), build.get("sourceDirty"))
            != (1, RID, "x86_64-unknown-linux-gnu", False)):
        raise ValueError("An exact clean Linux x64 native build is required")
    if not re.fullmatch(r"[0-9a-f]{40}", build.get("sourceCommit", "")):
        raise ValueError("Native source commit is missing")
    if build.get("cargoLockSha256") != sha(ROOT / "Cargo.lock"):
        raise ValueError("Native build uses a different Cargo.lock")
    if not build.get("inputSha256"):
        raise ValueError("Native source/profile input hashes are missing")
    for name, expected in build["inputSha256"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != expected:
            raise ValueError("Native source/profile input changed: " + name)
    builds = {item["label"]: item for item in build["builds"]}
    if len(builds) != len(build["builds"]) or set(builds) != {"sqlite", "postgresql"}:
        raise ValueError("Native build must preserve the two selected provider profiles")
    inputs = {}
    for label, item in builds.items():
        metadata_file = Path(item["metadataPath"])
        messages_file = Path(item["buildMessagesPath"])
        if sha(metadata_file) != item["metadataSha256"] or sha(messages_file) != item["buildMessagesSha256"]:
            raise ValueError("Native build metadata/messages changed: " + label)
        metadata = json.loads(metadata_file.read_text())
        messages = [json.loads(line) for line in messages_file.read_text().splitlines() if line.startswith("{")]
        if not any(item.get("reason") == "build-finished" and item.get("success") is True for item in messages):
            raise ValueError("Native build did not report successful completion: " + label)
        inputs[label] = metadata, messages
    lock = tomllib.loads((ROOT / "Cargo.lock").read_text())
    locked = {(item["name"], item["version"], item.get("source")): item for item in lock["package"]}
    cargo_home = Path(build.get("cargoHome", build.get("CargoHome", "")))
    if not cargo_home.is_dir():
        raise ValueError("Native build Cargo cache is unavailable")
    sysroot = Path(build["rustSysroot"])
    std_notice = sysroot / "share/doc/rust/COPYRIGHT-library.html"
    std_manifest = sysroot / "lib/rustlib/manifest-rust-std-x86_64-unknown-linux-gnu"
    channel_file = sysroot / "lib/rustlib/multirust-channel-manifest.toml"
    channel = tomllib.loads(channel_file.read_text())
    std_distribution = channel["pkg"]["rust-std"]["target"]["x86_64-unknown-linux-gnu"]
    std_origin = {"toolchain": "1.100.0", "target": build["target"], "noticeSha256": sha(std_notice),
                  "componentManifestSha256": sha(std_manifest), "channelManifestSha256": sha(channel_file),
                  "distribution": {key: std_distribution[key] for key in ("url", "hash", "xz_url", "xz_hash")}}
    assets = {item["engineId"]: item for item in build["assets"]}
    if set(assets) != set(ENGINES) or len(assets) != len(build["assets"]):
        raise ValueError("Exactly the two database native artifacts are required")
    profile = module("domain_linux_profile", "src/Packaging.Linux/linux_profile.py")
    result = {}
    notice_cache = {}
    for engine, asset in assets.items():
        facade, basename, root_name, _ = ENGINES[engine]
        binary = Path(asset["path"])
        if sha(binary) != asset["sha256"]:
            raise ValueError("Native output changed after build: " + engine)
        label = "postgresql" if engine == "database.postgresql" else "sqlite"
        if asset["buildLabel"] != label:
            raise ValueError("Native artifact was selected from the wrong provider profile")
        metadata, messages = inputs[label]
        selected, metadata_only = selected_packages(metadata, messages, root_name)
        selected_root = next(item["package"]["id"] for item in selected if item["package"]["name"] == root_name)
        output_records = [item for item in messages if item.get("reason") == "compiler-artifact"
                          and item.get("package_id") == selected_root and "cdylib" in item["target"]["crate_types"]]
        if len(output_records) != 1:
            raise ValueError("Native output is not bound to exactly one selected compiler artifact")
        compiler_path = Path(asset["compilerArtifactPath"]).resolve()
        selected_outputs = {Path(name).resolve() for name in output_records[0]["filenames"] if name.endswith(".so")}
        if selected_outputs != {compiler_path}:
            raise ValueError("Native frozen output was not selected from its recorded compiler artifact")
        native_audit = profile.inspect(binary, allowed_dependencies=SYSTEM_DEPENDENCIES)
        if "nw_database_get_abi_v1" not in native_audit["exports"]:
            raise ValueError("Required domain ABI bootstrap export is absent")
        entries = {"nativeweave/licenses/rust-standard-library/COPYRIGHT-library.html": std_notice.read_bytes()}
        records = []
        for item in selected:
            package = item["package"]
            if package["name"].startswith(("nativeweave-server", "nativeweave-protocol", "nativeweave-hello", "nativeweave-sync-proof", "nativeweave-async-proof", "nativeweave-extension-proof")):
                raise ValueError("Retired product entered the selected database native inputs: " + package["name"])
            record = {key: package.get(key) for key in ("id", "name", "version", "source", "license", "repository")}
            record.update({key: item[key] for key in ("roles", "features", "targetKinds")})
            if package["source"] is None:
                folder = Path(package["manifest_path"]).resolve().parent
                workspace = Path(metadata["workspace_root"]).resolve()
                if not folder.is_relative_to(workspace):
                    raise ValueError("Owned Cargo source is outside its recorded build checkout")
                source_path = folder.relative_to(workspace).as_posix()
                if source_path + "/Cargo.toml" not in build["inputSha256"]:
                    raise ValueError("Selected local Cargo manifest is not bound by the native source inventory")
                record.update(sourcePath=source_path, sourceCommit=build["sourceCommit"],
                              licenseFiles=[{"sourcePath": "LICENSE", "sha256": sha(ROOT / "LICENSE"), "packagePath": "LICENSE"}])
            else:
                key = (package["name"], package["version"], package["source"])
                locked_package = locked.get(key)
                if locked_package is None or not locked_package.get("checksum"):
                    raise ValueError("Selected Cargo source has no exact locked archive checksum: " + package["name"])
                checksum = locked_package["checksum"]
                if key not in notice_cache:
                    license_file = package.get("license_file")
                    if license_file and Path(license_file).is_absolute():
                        license_file = Path(license_file).relative_to(Path(package["manifest_path"]).parent).as_posix()
                    archive = crate_archive(cargo_home, package["name"], package["version"], checksum)
                    notice_cache[key] = archive_notices(archive, checksum, package["name"], package["version"], license_file)
                notices, bundled = notice_cache[key]
                record.update(cargoLockChecksum=checksum, archiveSha256=checksum, licenseFiles=[], bundledSources=bundled)
                for relative, data in notices.items():
                    destination = "nativeweave/licenses/" + package["name"] + "-" + package["version"] + "/" + relative
                    entries[destination] = data
                    record["licenseFiles"].append({"sourcePath": relative, "packagePath": destination,
                                                  "sha256": hashlib.sha256(data).hexdigest()})
                if package["name"] == "libsqlite3-sys":
                    record["bundledSelection"] = {"features": item["features"],
                        "sqlcipherSelected": any("sqlcipher" in value for value in item["features"]),
                        "noticeScope": "All upstream notice files retained; unused archive source is not asserted linked."}
            records.append(record)
        inventory = {"schemaVersion": 1, "engineId": engine, "nativeSha256": asset["sha256"],
                     "sourceCommit": build["sourceCommit"], "sourceDirty": False,
                     "cargoLockSha256": build["cargoLockSha256"], "buildLabel": label,
                     "command": builds[label]["command"], "tools": build["tools"],
                     "environment": build.get("environment", {}), "inputSha256": build["inputSha256"],
                     "metadataSha256": builds[label]["metadataSha256"],
                     "buildMessagesSha256": builds[label]["buildMessagesSha256"],
                     "compilerArtifact": {key: output_records[0][key] for key in ("package_id", "target", "profile", "features", "fresh")},
                     "cargoPackages": records, "metadataOnlyNotCompiled": metadata_only,
                     "rustStandardLibrary": std_origin, "elf": native_audit,
                     "scope": "Selected Cargo build inputs with roles; not a claim that every build/proc-macro input is linked. DT_NEEDED entries are platform-provided. No public distribution or signer authentication."}
        entries["nativeweave/dependencies.json"] = json_bytes(inventory)
        entries["NOTICE"] = ("NativeWeave domain native leaf; local-only candidate.\n"
            "NativeWeave-owned sources use the repository MIT LICENSE. Third-party terms remain their original terms.\n"
            "Exact selected Cargo build inputs, checksums, roles and original notices are indexed in nativeweave/dependencies.json.\n"
            "Original texts are preserved under nativeweave/licenses, including Rust standard-library notices.\n"
            "Build-only/proc-macro dependencies and unused source notices are not assertions of linked code.\n").encode()
        result[engine] = {**asset, "path": binary, "inventory": inventory, "entries": entries}
    return build, result
