#!/usr/bin/env python3
"""Execute A01 Linux x64 conformance; preserve each attempt's commands and bytes."""
import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OWNED = ["native/interop/abi", "src/Interop.Abi", "tests/Interop.Abi", "samples/api/interop-abi"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(include_outputs=True):
    source = {}
    for directory in OWNED:
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and not any(part in ("bin", "obj", "__pycache__") for part in path.relative_to(ROOT).parts):
                if include_outputs or path.name != "api-reference.md":
                    source[str(path.relative_to(ROOT))] = digest(path)
    for name in ["global.json", "rust-toolchain.toml", "Directory.Build.props", "Cargo.lock", "docs/guides/interop-abi.md"]:
        source[name] = digest(ROOT / name)
    return source


def compare_layout(actual, expected):
    reference = {key: value for key, value in expected.items() if key != "oracle"}
    if actual != reference:
        raise ValueError("The actual complete layout differs from the checked-in target oracle")
    for record in actual["records"].values():
        occupied = set()
        for field in record["fields"].values():
            occupied.update(range(field["offset"], field["offset"] + field["width"]))
        if occupied != set(range(record["size"])):
            raise ValueError("Unexpected implicit padding in the shared v1 records")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-aot", action="store_true", help="Development only; never records AOT success")
    parser.add_argument("--offline-packages", type=Path,
                        help="Use only cached Microsoft SDK-tool nupkg files; all remote sources are removed")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/A01")
    args = parser.parse_args()
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise SystemExit("This invocation verifies only Linux x64; it makes no other platform claim.")
    args.output.mkdir(parents=True, exist_ok=True)
    index = 1
    while (args.output / f"attempt-{index:03d}").exists():
        index += 1
    out = (args.output / f"attempt-{index:03d}").resolve()
    out.mkdir()
    native = out / "native"
    native.mkdir()
    commands = []
    result = {"task": "A01", "platform": "linux-x64", "passed": False,
              "native_aot_executed": False, "test_engine_only": True, "commands": commands}
    initial_inputs = source_hashes(include_outputs=False)
    environment = os.environ.copy()
    environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    environment["DOTNET_CLI_USE_MSBUILD_SERVER"] = "0"
    environment["MSBUILDUSESERVER"] = "0"
    restore_options = []
    if args.offline_packages:
        feed = out / "offline-sdk-feed"
        feed.mkdir()
        allowed = {"microsoft.dotnet.ilcompiler", "microsoft.net.illink.tasks",
                   "microsoft.netcore.app.runtime.linux-x64", "microsoft.netcore.app.runtime.nativeaot.linux-x64",
                   "microsoft.aspnetcore.app.runtime.linux-x64", "runtime.linux-x64.microsoft.dotnet.ilcompiler"}
        for package in sorted(allowed):
            folder = args.offline_packages.resolve() / package / "11.0.0"
            for archive in folder.glob("*.nupkg"):
                (feed / archive.name).symlink_to(archive)
        if not list(feed.iterdir()):
            raise ValueError("No allowlisted .NET 11 SDK package archives were present in the offline cache")
        config = out / "NuGet.offline.config"
        configuration = ET.Element("configuration")
        sources = ET.SubElement(configuration, "packageSources")
        ET.SubElement(sources, "clear")
        ET.SubElement(sources, "add", key="local-sdk-tools", value=str(feed))
        ET.SubElement(ET.SubElement(configuration, "auditSources"), "clear")
        ET.ElementTree(configuration).write(config, encoding="utf-8", xml_declaration=True)
        restore_options = ["--configfile", config, "-p:NuGetAudit=false"]
        result["restore_mode"] = "local Microsoft SDK package feed only; vulnerability data refresh unavailable offline"

    def run(name, command):
        completed = subprocess.run([str(x) for x in command], cwd=ROOT, capture_output=True, env=environment)
        (out / f"{name}.stdout").write_bytes(completed.stdout)
        (out / f"{name}.stderr").write_bytes(completed.stderr)
        entry = {"name": name, "command": [str(x) for x in command], "exit_code": completed.returncode,
                 "stdout_sha256": digest(out / f"{name}.stdout"), "stderr_sha256": digest(out / f"{name}.stderr")}
        commands.append(entry)
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        if completed.returncode:
            raise RuntimeError(f"{name} failed ({completed.returncode}): " + completed.stderr.decode(errors="replace")[-3000:] + completed.stdout.decode(errors="replace")[-3000:])
        return completed.stdout.decode()

    try:
        result["source_commit"] = run("source-commit", ["git", "rev-parse", "HEAD"]).strip()
        result["toolchain"] = {
            "rustc": run("rustc-version", ["rustc", "--version", "--verbose"]),
            "dotnet": run("dotnet-info", ["dotnet", "--info"]),
            "cc": run("cc-version", ["cc", "--version"]),
            "kernel": platform.release(), "machine": platform.machine(),
            "native_isa": "x86-64-v2", "features": [], "cargo_dependencies": []}
        cc_path = Path(shutil.which("cc")).resolve()
        linker_name = run("cc-linker-selection", [cc_path, "-print-prog-name=ld"]).strip()
        linker_path = Path(shutil.which(linker_name) or linker_name).resolve()
        result["toolchain"]["c_compiler_path"] = str(cc_path)
        result["toolchain"]["c_compiler_sha256"] = digest(cc_path)
        result["toolchain"]["c_linker_path"] = str(linker_path)
        result["toolchain"]["c_linker_sha256"] = digest(linker_path)
        result["toolchain"]["c_linker_version"] = run("c-linker-version", [linker_path, "--version"])
        if not result["toolchain"]["rustc"].startswith("rustc 1.100.0 "):
            raise ValueError("Use the locked Rust 1.100.0 toolchain")
        if run("sdk-version", ["dotnet", "--version"]).strip() != "11.0.100":
            raise ValueError("Use the locked .NET SDK 11.0.100")
        run("generation", [sys.executable, "native/interop/abi/generate.py", "--check"])
        run("signature-generation-mutations", [sys.executable, "tests/Interop.Abi/test_generation.py"])
        rustflags = ["--edition=2024", "-Dwarnings", "-C", "target-cpu=x86-64-v2"]
        rlib = native / "libnativeweave_interop_abi.rlib"
        run("rust-library", ["rustc", *rustflags, "--crate-name", "nativeweave_interop_abi", "--crate-type", "rlib", "-C", "opt-level=3", "native/interop/abi/src/lib.rs", "-o", rlib])
        run("rust-tests-build", ["rustc", *rustflags, "--test", "native/interop/abi/src/lib.rs", "-o", native / "rust-tests"])
        run("rust-tests", [native / "rust-tests", "--nocapture"])
        external = ["--extern", f"nativeweave_interop_abi={rlib}"]
        library = native / "libnw_abi_conformance.so"
        link_args = shlex.split(run("test-engine-build", ["rustc", *rustflags, *external, "--crate-type", "cdylib", "-C", "opt-level=3", "tests/Interop.Abi/native/fixture.rs", "-o", library, "--print=link-args"]))
        while link_args and "=" in link_args[0]:
            link_args.pop(0)  # rustc prints its child-process environment before the driver.
        rust_driver = Path(shutil.which(link_args[0]) or link_args[0]).resolve()
        rust_search = [arg for arg in link_args[1:] if arg.startswith("-B")]
        rust_flavor = next((arg.split("=", 1)[1] for arg in link_args if arg.startswith("-fuse-ld=")), None)
        selected = "ld." + rust_flavor if rust_flavor else "ld"
        rust_linker_name = run("rust-driver-linker-selection", [rust_driver, *rust_search, "-print-prog-name=" + selected]).strip()
        rust_linker = Path(shutil.which(rust_linker_name) or rust_linker_name).resolve()
        result["toolchain"]["rust_linker"] = {"driver_path": str(rust_driver), "driver_sha256": digest(rust_driver),
            "search_arguments": rust_search, "flavor": rust_flavor, "linker_path": str(rust_linker),
            "linker_sha256": digest(rust_linker), "linker_version": run("rust-linker-version", [rust_linker, "--version"]),
            "artifact_comment": run("rust-artifact-comment", ["readelf", "-p", ".comment", library])}
        exported = run("symbol-inventory", ["nm", "-D", "--defined-only", library])
        symbols = [line.split()[-1] for line in exported.splitlines() if line.strip()]
        if symbols != ["nw_abi_conformance_get_abi_v1"]:
            raise ValueError("The test-only engine has unexpected exported symbols: " + repr(symbols))
        result["native_exports"] = symbols
        run("c-layout-build", ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", "native/interop/abi/include", "tests/Interop.Abi/native/layout.c", "-o", native / "layout-c"])
        expected = json.loads((ROOT / "tests/Interop.Abi/expected-linux-x64.json").read_text())
        compare_layout(json.loads(run("c-layout", [native / "layout-c"])), expected)
        run("rust-layout-build", ["rustc", *rustflags, *external, "tests/Interop.Abi/native/layout.rs", "-o", native / "layout-rust"])
        compare_layout(json.loads(run("rust-layout", [native / "layout-rust"])), expected)
        run("c-signatures-build", ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", "native/interop/abi/include", "tests/Interop.Abi/native/bootstrap.c", "-L", native, "-lnw_abi_conformance", "-Wl,-rpath,$ORIGIN", "-o", native / "bootstrap-c"])
        run("c-signatures", [native / "bootstrap-c"])
        mutation_results = []
        header = (ROOT / "native/interop/abi/include/nativeweave_abi_v1.h").read_text()
        mutations = {
            "offset": header.replace("uint32_t abi_major;\n    uint32_t abi_minor;", "uint32_t abi_minor;\n    uint32_t abi_major;"),
            "width": header.replace("uint64_t length;", "uint32_t length;")}
        for label, changed in mutations.items():
            if header == changed:
                raise ValueError("Mutation did not change the declaration")
            location = out / f"mutation-{label}"
            location.mkdir()
            (location / "nativeweave_abi_v1.h").write_text(changed)
            run(f"mutation-{label}-build", ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", location, "tests/Interop.Abi/native/layout.c", "-o", location / "layout"])
            actual = json.loads(run(f"mutation-{label}-layout", [location / "layout"]))
            try:
                compare_layout(actual, expected)
            except ValueError:
                mutation_results.append({"mutation": label, "detected": True, "actual": actual})
            else:
                raise ValueError("Real compiled field mutation was not detected")
        (out / "mutation-results.json").write_text(json.dumps(mutation_results, indent=2) + "\n")
        result["mutation_controls"] = [{"mutation": x["mutation"], "detected": x["detected"]} for x in mutation_results]
        prop = f"-p:A01NativeFixture={library}"
        project = "tests/Interop.Abi/Interop.Abi.Tests.csproj"
        sample = "samples/api/interop-abi/Interop.Abi.Sample.csproj"
        for name, path in [("tests", project), ("sample", sample)]:
            run(f"{name}-restore", ["dotnet", "restore", path, "--locked-mode", prop, *restore_options])
            run(f"{name}-build", ["dotnet", "build", path, "-c", "Release", "--no-restore", prop])
        testdll = ROOT / "tests/Interop.Abi/bin/Release/net11.0/NativeWeave.Interop.Abi.Tests.dll"
        sampledll = ROOT / "samples/api/interop-abi/bin/Release/net11.0/NativeWeave.Interop.Abi.Sample.dll"
        compare_layout(json.loads(run("managed-layout", ["dotnet", testdll, "--layout"])), expected)
        run("managed-tests", ["dotnet", testdll])
        assembly = ROOT / "src/Interop.Abi/bin/Release/net11.0/NativeWeave.Interop.Abi.dll"
        surface = json.loads(run("managed-api-surface", ["dotnet", testdll, "--surface", assembly]))
        xml = assembly.with_suffix(".xml")
        xml_members = list(ET.parse(xml).getroot().find("members"))
        if not xml_members or any(member.find("summary") is None for member in xml_members):
            raise ValueError("Internal boundary XML documentation is missing")
        reference = "# Generated ABI assembly API reference\n\nAssembly: `NativeWeave.Interop.Abi`.\n\nCompiled public types: **0**. Compiled public members: **0**.\n\nThis component exposes no application API. Its fixed wire records, status constants and validation are internal.\nApplication metadata/preflight types remain owned by A02/A24. The C ABI inventory is generated from `native/interop/abi/abi-v1.json`.\n"
        (ROOT / "src/Interop.Abi/api-reference.md").write_text(reference)
        (out / "api-surface.json").write_text(json.dumps({**surface, "internal_xml_members": len(xml_members), "reference_sha256": digest(ROOT / "src/Interop.Abi/api-reference.md")}, indent=2) + "\n")
        run("sample-minimal", ["dotnet", sampledll])
        run("sample-advanced", ["dotnet", sampledll, "--advanced"])
        artifacts = [library, rlib, assembly, xml, testdll, sampledll]
        if not args.skip_aot:
            for name, path, executable in [("tests", project, "NativeWeave.Interop.Abi.Tests"), ("sample", sample, "NativeWeave.Interop.Abi.Sample")]:
                destination = out / f"aot-{name}"
                run(f"{name}-aot-restore", ["dotnet", "restore", path, "-r", "linux-x64", "-p:PublishAot=true", "--locked-mode", prop, *restore_options])
                if name == "tests":
                    selection = json.loads(run("aot-linker-selection", ["dotnet", "msbuild", path, "-nologo", "-t:ResolveReferences,SetupOSSpecificProps",
                                               "-p:RuntimeIdentifier=linux-x64", "-p:PublishAot=true",
                                               "-getProperty:CppCompilerAndLinker,CppLinker,LinkerFlavor"]))["Properties"]
                    driver = Path(shutil.which(selection["CppLinker"]) or selection["CppLinker"]).resolve()
                    selected_linker = "ld." + selection["LinkerFlavor"] if selection["LinkerFlavor"] else "ld"
                    linker_name = run("aot-driver-linker", [driver, "-print-prog-name=" + selected_linker]).strip()
                    linker = Path(shutil.which(linker_name) or linker_name).resolve()
                    result["toolchain"]["aot_linker"] = {"sdk_selection": selection, "driver_path": str(driver),
                        "driver_sha256": digest(driver), "linker_path": str(linker), "linker_sha256": digest(linker),
                        "driver_version": run("aot-driver-version", [driver, "--version"]),
                        "linker_version": run("aot-linker-version", [linker, "--version"])}
                run(f"{name}-aot-publish", ["dotnet", "publish", path, "--no-restore", "-c", "Release", "-r", "linux-x64", "-p:PublishAot=true", prop, "-o", destination])
                run(f"{name}-aot-execute", [destination / executable, "--require-aot", "--advanced"])
                if name == "tests":
                    compare_layout(json.loads(run("aot-layout", [destination / executable, "--layout"])), expected)
                artifacts.append(destination / executable)
            result["native_aot_executed"] = True
        if source_hashes(include_outputs=False) != initial_inputs:
            raise RuntimeError("Implementation inputs changed during verification; this attempt is not acceptance evidence")
        source = source_hashes()
        result["source_sha256"] = source
        result["source_snapshot_sha256"] = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
        result["artifact_sha256"] = {str(path.relative_to(ROOT)): digest(path) for path in artifacts}
        result["passed"] = True
    except Exception as error:
        result["error"] = str(error)
        raise
    finally:
        (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(out / "result.json", flush=True)


if __name__ == "__main__":
    main()
