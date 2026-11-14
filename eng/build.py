#!/usr/bin/env python3
"""Maintainer build and isolated NuGet/AOT verification; Python 3.9+, no pip dependencies."""
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
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
PROJECT = ROOT / "src/NativeWeave.HelloWorld/NativeWeave.HelloWorld.csproj"
LOGS = ARTIFACTS / "logs"


def run(args, label, cwd=ROOT, env=None):
    LOGS.mkdir(parents=True, exist_ok=True)
    print("+ " + " ".join(map(str, args)), flush=True)
    result = subprocess.run(list(map(str, args)), cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (LOGS / (label + ".log")).write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        print(result.stdout, flush=True)
        raise RuntimeError(f"{label} failed ({result.returncode}); see artifacts/logs/{label}.log")
    if "--message-format=json-render-diagnostics" not in args:
        print(result.stdout[-3000:], end="", flush=True)
    return result.stdout


def digest(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def host():
    pair = (platform.system(), platform.machine().lower())
    supported = {("Darwin", "arm64"): ("osx-arm64", ".dylib"),
                 ("Linux", "x86_64"): ("linux-x64", ".so")}
    if pair not in supported:
        raise RuntimeError(f"Bootstrap supports macOS arm64 development and Linux x64 only; found {pair}")
    return supported[pair]


def native():
    rid, extension = host()
    output = run(["cargo", "build", "--release", "--locked", "--message-format=json-render-diagnostics"], "native-build")
    libraries = []
    for line in output.splitlines():
        if not line.startswith("{"):
            continue
        item = json.loads(line)
        if item.get("reason") == "compiler-artifact" and item["target"]["name"] == "nativeweave_hello":
            libraries.extend(Path(file) for file in item["filenames"] if file.endswith(extension))
    if len(libraries) != 1:
        raise RuntimeError("Cargo did not return exactly one native library artifact")
    destination = ARTIFACTS / "native"
    if destination.exists():
        shutil.rmtree(destination)
    target = destination / rid / "native" / libraries[0].name
    target.parent.mkdir(parents=True)
    shutil.copy2(libraries[0], target)
    return target


def pack(version, library):
    tracked = run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], "source-inventory")
    files = {name: digest(ROOT / name) for name in sorted(set(tracked.splitlines())) if (ROOT / name).is_file()}
    metadata = {
        "schemaVersion": 1, "packageId": "NativeWeave.HelloWorld", "packageVersion": version,
        "status": "experimental-bootstrap", "abiMajor": 1, "rid": host()[0],
        "nativePath": "runtimes/" + library.relative_to(ARTIFACTS / "native").as_posix(),
        "nativeSha256": digest(library), "sourceCommit": run(["git", "rev-parse", "HEAD"], "source-commit").strip(),
        "sourceDirty": bool(run(["git", "status", "--porcelain"], "source-status").strip()),
        "sourceFilesSha256": files, "cargoLockSha256": digest(ROOT / "Cargo.lock"),
        "rustc": run(["rustc", "-Vv"], "rustc").strip(),
        "cargo": run(["cargo", "--version"], "cargo").strip(),
        "dotnetSdk": run(["dotnet", "--version"], "dotnet").strip(),
        "os": platform.platform(), "features": [], "thirdPartyCargoDependencies": [],
    }
    (ARTIFACTS / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    packages = ARTIFACTS / "packages"
    if packages.exists():
        shutil.rmtree(packages)
    packages.mkdir(parents=True)
    run(["dotnet", "pack", PROJECT, "-c", "Release", "--no-restore", "-o", packages,
         f"-p:PackageVersion={version}"], "pack")
    package = packages / f"NativeWeave.HelloWorld.{version}.nupkg"
    with zipfile.ZipFile(package) as archive:
        required = {metadata["nativePath"], "lib/net11.0/NativeWeave.HelloWorld.dll",
                    "lib/net11.0/NativeWeave.HelloWorld.xml", "README.md", "LICENSE",
                    "THIRD_PARTY_NOTICES.md", "nativeweave/manifest.json"}
        if not required.issubset(archive.namelist()):
            raise RuntimeError(f"Missing package entries: {required - set(archive.namelist())}")
        if hashlib.sha256(archive.read(metadata["nativePath"])).hexdigest() != metadata["nativeSha256"]:
            raise RuntimeError("Native package bytes differ from verified build")
        if any(name.startswith(("build/", "buildTransitive/", "contentFiles/")) for name in archive.namelist()):
            raise RuntimeError("Bootstrap must not ship consumer build hooks")
        nuspec = ET.fromstring(archive.read("NativeWeave.HelloWorld.nuspec"))
        if any(element.tag.rsplit("}", 1)[-1] == "dependency" for element in nuspec.iter()):
            raise RuntimeError("Bootstrap unexpectedly added a runtime package dependency")
    shutil.copy2(ARTIFACTS / "manifest.json", packages / "manifest.json")
    sums = "".join(f"{digest(file)}  {file.name}\n" for file in sorted(packages.iterdir()) if file.is_file())
    (packages / "SHA256SUMS").write_text(sums, encoding="utf-8")
    return package


def consume(version, feed):
    rid, extension = host()
    package = feed.resolve() / f"NativeWeave.HelloWorld.{version}.nupkg"
    with zipfile.ZipFile(package) as archive:
        metadata = json.loads(archive.read("nativeweave/manifest.json"))
    if metadata["rid"] != rid:
        raise RuntimeError("Package RID differs from consumer host")
    # Outside the checkout: no repository props, targets, source projects or native outputs.
    with tempfile.TemporaryDirectory(prefix="nativeweave-consumer-") as temporary:
        work = Path(temporary)
        shutil.copy2(ROOT / "global.json", work / "global.json")
        config = ET.Element("configuration")
        sources = ET.SubElement(config, "packageSources")
        ET.SubElement(sources, "clear")
        ET.SubElement(sources, "add", key="candidate", value=str(feed.resolve()))
        ET.SubElement(sources, "add", key="nuget.org", value="https://api.nuget.org/v3/index.json")
        mapping = ET.SubElement(config, "packageSourceMapping")
        local = ET.SubElement(mapping, "packageSource", key="candidate")
        ET.SubElement(local, "package", pattern="NativeWeave.*")
        public = ET.SubElement(mapping, "packageSource", key="nuget.org")
        ET.SubElement(public, "package", pattern="*")
        ET.ElementTree(config).write(work / "NuGet.Config", encoding="utf-8", xml_declaration=True)
        env = os.environ.copy()
        env["NUGET_PACKAGES"] = str(work / "packages")
        env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
        # Preserve the AOT C linker; hide Rust tool paths and fail any Rust invocation.
        trap = work / "no-rust"
        trap.mkdir()
        env["NATIVEWEAVE_RUST_INVOCATIONS"] = str(work / "rust-invocations")
        for name in ("cargo", "rustc", "rustup"):
            executable = trap / name
            executable.write_text('#!/bin/sh\necho "$0" >> "$NATIVEWEAVE_RUST_INVOCATIONS"\necho "Unexpected Rust invocation" >&2\nexit 97\n', encoding="utf-8")
            executable.chmod(0o755)
        entries = [entry for entry in env.get("PATH", "").split(os.pathsep)
                   if entry and not any((Path(entry) / name).exists() for name in ("cargo", "rustc", "rustup"))]
        env["PATH"] = os.pathsep.join([str(trap)] + entries)
        for key in ("CARGO_HOME", "RUSTUP_HOME", "RUSTFLAGS", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "NUGET_API_KEY"):
            env.pop(key, None)
        for name, source in (("HelloWorld", ROOT / "samples/PackageConsumer/Program.cs"),
                             ("InteropTests", ROOT / "tests/NativeWeave.HelloWorld.Tests/Program.cs")):
            app = work / name
            app.mkdir()
            project = app / f"{name}.csproj"
            project.write_text((ROOT / "samples/PackageConsumer/PackageConsumer.csproj").read_text().replace(
                "[$(NativeWeaveVersion)]", f"[{version}]"), encoding="utf-8")
            shutil.copy2(source, app / "Program.cs")
            run(["dotnet", "build", project, "-c", "Release"], name + "-package-build", cwd=work, env=env)
            output = run(["dotnet", "run", "--project", project, "-c", "Release", "--no-build"], name + "-package-run", cwd=work, env=env)
            if name == "HelloWorld" and output.strip() != "Hello, World! From Rust.":
                raise RuntimeError("Unexpected greeting from packaged native asset")
            publish = app / "publish"
            run(["dotnet", "publish", project, "-c", "Release", "-r", rid,
                 "-p:PublishAot=true", "-p:IlcTreatWarningsAsErrors=true", "-o", publish],
                name + "-aot-publish", cwd=work, env=env)
            native_file = publish / ("libnativeweave_hello" + extension)
            if digest(native_file) != metadata["nativeSha256"]:
                raise RuntimeError("Consumer native bytes changed")
            run([publish / name], name + "-aot-run", cwd=work, env=env)
            if (publish / f"{name}.dll").exists():
                raise RuntimeError("Expected a real native AOT application")
            retained = ARTIFACTS / "publish" / name
            if retained.exists():
                shutil.rmtree(retained)
            shutil.copytree(publish, retained)
        if (work / "rust-invocations").exists():
            raise RuntimeError("A consumer attempted to invoke Rust")
        report = {"status": "passed", "rid": rid, "package": package.name,
                  "packageSha256": digest(package), "nativeSha256": metadata["nativeSha256"],
                  "ridFreeBuildAndRun": True, "nativeAotExecuted": True,
                  "isolatedNugetCache": True, "outsideSourceTree": True,
                  "rustInvocationTrap": True, "pristineMachine": False}
        (ARTIFACTS / "consumer-result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def verify(version, write_docs=False):
    for filename in ("verification.json", "consumer-result.json"):
        (ARTIFACTS / filename).unlink(missing_ok=True)
    standard = json.loads((ROOT / "public-api-standard.json").read_text())
    if digest(ROOT / standard["localPath"]) != standard["sha256"]:
        raise RuntimeError("Pinned public API standard bytes changed; review adoption explicitly")
    closure = json.loads(run(["cargo", "metadata", "--format-version=1", "--locked"], "cargo-closure"))
    if len(closure["packages"]) != 1 or closure["packages"][0]["dependencies"]:
        raise RuntimeError("New Cargo dependencies require an advisory/license gate and a truthful package inventory")
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests/Tooling", "-v"], "release-tool-tests")
    run(["cargo", "fmt", "--all", "--", "--check"], "rust-format")
    run(["cargo", "clippy", "--workspace", "--all-targets", "--locked", "--", "-D", "warnings"], "clippy")
    run(["cargo", "test", "--workspace", "--release", "--locked"], "rust-tests")
    library = native()
    run(["dotnet", "restore", "NativeWeave.slnx", "--locked-mode"], "restore")
    run(["dotnet", "build", "NativeWeave.slnx", "-c", "Release", "--no-restore"], "build")
    run(["dotnet", "format", "NativeWeave.slnx", "--verify-no-changes", "--no-restore"], "dotnet-format")
    run(["dotnet", "run", "--project", "samples/HelloWorld", "-c", "Release", "--no-build"], "source-hello")
    run(["dotnet", "run", "--project", "tests/NativeWeave.HelloWorld.Tests", "-c", "Release", "--no-build"], "interop-tests")
    docs = ["dotnet", "run", "--project", "tools/ApiDocs", "-c", "Release", "--no-build", "--", str(ROOT)]
    if write_docs:
        docs.append("--write")
    run(docs, "api-docs")
    package = pack(version, library)
    consume(version, package.parent)
    run(["git", "diff", "--check"], "diff-check")
    report = {"status": "passed", "rid": host()[0], "version": version,
              "packageSha256": digest(package), "nativeSha256": digest(library),
              "checks": ["rustfmt", "clippy", "rust-tests", "locked-restore", "managed-build", "dotnet-format",
                         "source-interop-tests", "compiled-api-and-xml", "nuget-layout", "isolated-package-consumer", "native-aot-run"],
              "independentReview": False, "publiclyPublished": False}
    (ARTIFACTS / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS: verified source, package, isolated consumption and actual Native AOT execution.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["native", "pack", "verify", "consume"])
    parser.add_argument("--version", default="0.1.0-preview.1")
    parser.add_argument("--feed", type=Path, default=ARTIFACTS / "packages")
    parser.add_argument("--write-docs", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", args.version):
        parser.error("Use a canonical major.minor.patch[-prerelease] version without a leading v")
    ARTIFACTS.mkdir(exist_ok=True)
    if args.command == "native":
        native()
    elif args.command == "verify":
        verify(args.version, args.write_docs)
    elif args.command == "consume":
        consume(args.version, args.feed)
    else:
        library = native()
        run(["dotnet", "restore", PROJECT, "--locked-mode"], "pack-restore")
        pack(args.version, library)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
