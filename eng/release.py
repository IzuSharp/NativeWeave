#!/usr/bin/env python3
"""Validate a retained Linux candidate, publish it, then verify registry consumption."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

from build import ARTIFACTS, ROOT, consume, digest


def validate_version(version):
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9a-z-]+(?:\.[0-9a-z-]+)*)?", version):
        raise ValueError("Use a canonical lowercase major.minor.patch[-prerelease] version")
    if "-" in version and any(part.isdigit() and len(part) > 1 and part.startswith("0") for part in version.split("-", 1)[1].split(".")):
        raise ValueError("Numeric prerelease identifiers cannot have leading zeroes")
    return version


def validate_candidate(version):
    directory = ARTIFACTS / "packages"
    package = directory / f"NativeWeave.HelloWorld.{version}.nupkg"
    expected_names = {package.name, "manifest.json"}
    checksums = {}
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        checksum, name = line.split("  ", 1)
        if name not in expected_names or name in checksums or not re.fullmatch("[0-9a-f]{64}", checksum):
            raise ValueError("Unexpected, duplicate or malformed candidate checksum entry")
        checksums[name] = checksum
    if set(checksums) != expected_names:
        raise ValueError("Incomplete candidate checksum manifest")
    for name, expected in checksums.items():
        if digest(directory / name) != expected:
            raise ValueError(f"Candidate hash mismatch: {name}")
    metadata = json.loads((directory / "manifest.json").read_text())
    if metadata["packageId"] != "NativeWeave.HelloWorld" or metadata["packageVersion"] != version or metadata["rid"] != "linux-x64":
        raise ValueError("Wrong package identity or platform")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if metadata["sourceDirty"] or metadata["sourceCommit"] != head:
        raise ValueError("Release requires a clean candidate built from the publishing commit")
    with zipfile.ZipFile(package) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("Duplicate archive entries")
        if json.loads(archive.read("nativeweave/manifest.json")) != metadata:
            raise ValueError("Embedded and external manifests differ")
        if hashlib.sha256(archive.read(metadata["nativePath"])).hexdigest() != metadata["nativeSha256"]:
            raise ValueError("Native payload hash mismatch")
    return package


def entries(package):
    with zipfile.ZipFile(package) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("Duplicate registry archive entries")
        return {name: hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist() if name != ".signature.p7s"}


def publish(version):
    package = validate_candidate(version)
    if not os.environ.get("NUGET_API_KEY"):
        raise ValueError("NuGet/login must supply NUGET_API_KEY")
    # .NET 11 reads the credential from the environment. Do not log it or put it in argv.
    subprocess.run(["dotnet", "nuget", "push", str(package), "--source", "https://api.nuget.org/v3/index.json"], check=True)
    registry = ARTIFACTS / "registry"
    registry.mkdir(exist_ok=True)
    downloaded = registry / package.name
    url = f"https://api.nuget.org/v3-flatcontainer/nativeweave.helloworld/{version}/nativeweave.helloworld.{version}.nupkg"
    deadline = time.monotonic() + 300
    while True:
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                downloaded.write_bytes(response.read())
            break
        except urllib.error.HTTPError as error:
            if error.code != 404 or time.monotonic() >= deadline:
                raise
            print("Waiting for NuGet indexing...", flush=True)
            time.sleep(10)
    subprocess.run(["dotnet", "nuget", "verify", str(downloaded), "--all"], check=True)
    if entries(package) != entries(downloaded):
        raise ValueError("Registry payload differs from the tested candidate (excluding the verified signature only)")
    # Restore the exact registry bytes in an empty cache, then run both JIT and AOT.
    consume(version, registry)
    result = {"status": "published-and-consumed", "version": version,
              "uploadSha256": digest(package), "registrySha256": digest(downloaded),
              "signatureVerified": True, "unsignedPayloadEntriesEqual": True,
              "registryPackageJitAndAotExecuted": True}
    (ARTIFACTS / "publication.json").write_text(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["identity", "validate", "publish"])
    parser.add_argument("--version", default=os.environ.get("RELEASE_VERSION", ""))
    args = parser.parse_args()
    version = validate_version(args.version)
    if args.command == "identity":
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with open(output, "a", encoding="utf-8") as stream:
                stream.write(f"version={version}\n")
        print(version)
    elif args.command == "validate":
        print(validate_candidate(version).name)
    else:
        publish(version)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
