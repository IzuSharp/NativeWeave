#!/usr/bin/env python3
"""Linux A22 component evidence. No publishing, deletion, unlisting or auto-update."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import time
import zipfile

from test_policy import ROOT, compat, record, run as policy_cases, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--api-tool-root", type=Path, default=ROOT)
    parser.add_argument("--design-root", type=Path)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    if (evidence / "result.json").exists():
        raise SystemExit("Use a new evidence directory; previous receipts are immutable.")
    assert platform.system() == "Linux" and platform.machine() == "x86_64"
    started = time.time()
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    initial_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    if not args.prepare and initial_status:
        raise SystemExit("Formal evidence requires a committed clean source tree. Use --prepare only for development.")
    commands, hashes, matrix = [], {}, []
    def run(name, command, *, cwd=ROOT, expected=0, contains=(), env=None):
        command = [str(x) for x in command]
        began = time.time()
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, env=env, timeout=360)
        (evidence / f"{name}.stdout").write_text(result.stdout)
        (evidence / f"{name}.stderr").write_text(result.stderr)
        passed = (result.returncode == expected if expected is not None else result.returncode != 0)
        passed = passed and all(text in result.stdout + result.stderr for text in contains)
        commands.append({"name": name, "command": command, "cwd": str(cwd), "exit_code": result.returncode,
                         "expected_exit": expected, "passed": passed, "seconds": round(time.time()-began, 3)})
        write(evidence / "commands.json", commands)
        if not passed:
            raise AssertionError(f"{name} failed; see retained stdout/stderr")
        return result.stdout

    common = ["-p:UseSharedCompilation=false", "-nr:false", "-m:1"]
    locked = [] if args.prepare else ["--locked-mode"]
    sample = ROOT / "samples/api/verification-compatibility/CompatibilitySample.csproj"
    try:
        design = args.design_root or next((p for p in [ROOT.parent / "NativeWeave-Design", ROOT.parents[2] / "NativeWeave-Design"] if p.is_dir()), None)
        assert design is not None, "Use --design-root for the locked read-only Design checkout"
        design_inputs = compat.read_json(ROOT / "src/Verification.Compatibility/design-inputs.json")
        design_commit = subprocess.check_output(["git", "-C", str(design), "rev-parse", "HEAD"], text=True).strip()
        assert design_commit == design_inputs["design_commit"]
        for name, expected in design_inputs["inputs"].items():
            assert compat.file_hash(design / name.split(":", 1)[1]) == expected, name
        write(evidence / "design-inputs.json", {"commit": design_commit, "checked_inputs": len(design_inputs["inputs"]),
            "manifest_sha256": compat.file_hash(ROOT / "src/Verification.Compatibility/design-inputs.json")})
        run("dotnet-version", ["dotnet", "--info"])
        run("rust-version", ["rustc", "-Vv"])
        cargo = run("abi-compile", ["cargo", "build", "--locked", "-p", "nativeweave-interop-abi", "--message-format=json"])
        rlib = None
        for line in cargo.splitlines():
            message = json.loads(line)
            if message.get("reason") == "compiler-artifact" and message.get("target", {}).get("name") == "nativeweave_interop_abi":
                rlib = next(Path(x) for x in message["filenames"] if x.endswith(".rlib"))
        assert rlib is not None
        fixture_source = ROOT / "tests/Verification.Compatibility/native/fixture.rs"
        natives = {}
        for name, cfg in [("old", None), ("new", "new_native"), ("major", "bad_major"), ("layout", "bad_layout"), ("semantics", "bad_semantics")]:
            out = evidence / "native" / name / "libnw_compat.so"
            out.parent.mkdir(parents=True, exist_ok=True)
            flags = ["--cfg", cfg] if cfg else []
            base = ["rustc", fixture_source, "--edition=2024", "--extern", f"nativeweave_interop_abi={rlib}", "-L", f"dependency={rlib.parent}", *flags]
            run(f"native-{name}", [*base, "--crate-type=cdylib", "-C", "opt-level=2", "-C", "panic=abort", "-o", out])
            natives[name] = out
            hashes[f"native-{name}"] = record(out, ROOT)
            if name in ("old", "new", "semantics"):
                test = out.parent / "direct-rust"
                run(f"rust-test-build-{name}", [*base, "--test", "-o", test])
                run(f"rust-direct-{name}", [test], expected=None if name == "semantics" else 0,
                    contains=("FAILED",) if name == "semantics" else ("test result: ok",))

        run("sample-restore", ["dotnet", "restore", sample, *locked, *common])
        managed = {}
        for generation in ("old", "new"):
            output = evidence / "managed" / generation
            run(f"managed-{generation}", ["dotnet", "build", sample, "--no-restore", "-c", "Release", "-o", output,
                f"-p:CompatibilityGeneration={generation}", *common])
            managed[generation] = output / "NativeWeave.Compatibility.Sample.dll"
            hashes[f"managed-{generation}"] = record(managed[generation], ROOT)
        def matrix_rows(mode, consumers):
            for generation in ("old", "new"):
                for native_generation in ("old", "new"):
                    native = natives[native_generation]
                    command = (["dotnet", consumers[generation]] if mode == "jit" else [consumers[generation]])
                    output = run(f"{mode}-{generation}-managed-{native_generation}-native", [*command, native, compat.file_hash(native), "pass", *([] if mode == "jit" else ["--require-aot"])])
                    row = json.loads(output.strip().splitlines()[-1]); row.update(mode=mode, native=native_generation,
                        managed_profile=record(managed[generation], ROOT), managed_artifact=record(consumers[generation], ROOT), native_artifact=record(native, ROOT))
                    matrix.append(row)
            for case, native_name in [("major", "major"), ("layout", "layout"), ("capability", "old"), ("hash", "new"), ("semantics", "semantics"), ("conflict", "new")]:
                native = natives[native_name]
                command = ["dotnet", consumers["new"]] if mode == "jit" else [consumers["new"]]
                output = run(f"{mode}-negative-{case}", [*command, native, "0" * 64 if case == "hash" else compat.file_hash(native), case,
                    *([] if mode == "jit" else ["--require-aot"])])
                row = json.loads(output.strip().splitlines()[-1]); row.update(mode=mode, native=native_name)
                matrix.append(row)
        matrix_rows("jit", managed)
        run("sample-aot-restore", ["dotnet", "restore", sample, "-r", "linux-x64", "-p:PublishAot=true", *locked, *common])
        aot = {}
        for generation in ("old", "new"):
            output = evidence / "aot" / generation
            run(f"sample-aot-{generation}", ["dotnet", "publish", sample, "--no-restore", "-c", "Release", "-r", "linux-x64",
                "-p:PublishAot=true", f"-p:CompatibilityGeneration={generation}", "-o", output, *common])
            aot[generation] = output / "NativeWeave.Compatibility.Sample"
            hashes[f"aot-{generation}"] = record(aot[generation], ROOT)
        matrix_rows("aot", aot)
        matrix_record = {"passed": True, "source_commit": source_commit, "rid": "linux-x64", "rows": matrix,
            "scope": "Prior accepted A01/A02 source components and current controlled native profiles, not released Core packages"}
        write(evidence / "matrix.json", matrix_record)

        api_tool_project = args.api_tool_root.resolve() / "src/Build.Integration/ApiReference/ApiReference.csproj"
        api_tool_source_before = compat.file_hash(api_tool_project.parent / "Program.cs")
        run("api-tool-build", ["dotnet", "build", api_tool_project, "-c", "Release", *common])
        api_tool = api_tool_project.parent / "bin/Release/net11.0/ApiReference.dll"
        # Respect the tool's actual assembly name if it differs from the project basename.
        if not api_tool.exists():
            api_tool = next(p for p in api_tool.parent.glob("*.dll") if p.with_suffix(".runtimeconfig.json").exists())
        api_tool_inputs = {"project_path": str(api_tool_project), "project_sha256": compat.file_hash(api_tool_project),
            "source_path": str(api_tool_project.parent / "Program.cs"),
            "source_sha256": compat.file_hash(api_tool_project.parent / "Program.cs"),
            "assembly_sha256": compat.file_hash(api_tool)}
        assert api_tool_inputs["source_sha256"] == api_tool_source_before, "Shared API tool changed while compiling"
        write(evidence / "a13-tool.json", api_tool_inputs)
        dotnet_root = Path(os.environ["DOTNET_ROOT"])
        api_project = ROOT / "tests/Verification.Compatibility/ApiFixture/ApiFixture.csproj"
        consumer_project = ROOT / "tests/Verification.Compatibility/ApiConsumer/ApiConsumer.csproj"
        run("api-fixture-restore", ["dotnet", "restore", api_project, *locked, *common])
        run("api-consumer-restore", ["dotnet", "restore", consumer_project, *locked, *common])
        api_snapshots, fixture_dlls = {}, {}
        for generation in ("OLD", "NEW", "DEFAULT", "NULLABILITY", "GENERIC", "REMOVED", "OBSOLETE", "AMBIGUOUS", "BEHAVIOR"):
            output = evidence / "api" / generation.lower()
            run(f"api-{generation.lower()}-build", ["dotnet", "build", api_project, "--no-restore", "-c", "Release", "-o", output,
                f"-p:FixtureGeneration={generation}", *common])
            dll = output / "NativeWeave.Compatibility.ApiFixture.dll"
            fixture_dlls[generation] = dll
            config = write(output / "config.json", {"assembly": str(dll), "sources": [str(api_project.parent)], "baselines": [],
                "title": "A22 controlled compiled API evolution fixture", "scope": "Unpublished compatibility fixture; not a product API",
                "output": str(output / "reference.md"), "guides": ["docs/guides/verification-compatibility.md"]})
            run(f"api-{generation.lower()}-snapshot", ["dotnet", api_tool, ROOT, dotnet_root, config, "--snapshot"])
            api_snapshots[generation] = output / "reference.json"
        api_results = []
        for generation in fixture_dlls:
            try:
                result = compat.compare_api(compat.read_json(api_snapshots["OLD"]), compat.read_json(api_snapshots[generation]))
                assert generation in ("OLD", "NEW", "AMBIGUOUS", "BEHAVIOR")
                api_results.append({"generation": generation, "snapshot": "retained", **result})
            except compat.Rejected as error:
                assert generation in ("DEFAULT", "NULLABILITY", "GENERIC", "REMOVED", "OBSOLETE") and "NWCMP006:" in str(error)
                api_results.append({"generation": generation, "snapshot": "rejected", "diagnostic": str(error)})
        binaries = {}
        for generation in ("OLD", "NEW", "DEFAULT", "NULLABILITY", "REMOVED", "OBSOLETE", "AMBIGUOUS"):
            output = evidence / "api-consumers" / generation.lower()
            negative = {"NULLABILITY": "CS8625", "REMOVED": "CS0117", "OBSOLETE": "NWCOMP001", "AMBIGUOUS": "CS0121"}.get(generation)
            run(f"source-{generation.lower()}", ["dotnet", "build", consumer_project, "--no-restore", "-c", "Release", "-o", output,
                f"-p:FixtureAssembly={fixture_dlls[generation]}", *common], expected=None if negative else 0, contains=(negative,) if negative else ())
            if negative is None:
                binaries[generation] = output / "NativeWeave.Compatibility.ApiConsumer.dll"
                run(f"source-run-{generation.lower()}", ["dotnet", binaries[generation]], expected=None if generation == "DEFAULT" else 0,
                    contains=("compatibility changed",) if generation == "DEFAULT" else ("consumer passed",))
        migrated = evidence / "api-consumers" / "migrated"
        run("obsolete-migration-build", ["dotnet", "build", consumer_project, "--no-restore", "-c", "Release", "-o", migrated,
            f"-p:FixtureAssembly={fixture_dlls['OBSOLETE']}", "-p:ConsumerGeneration=MIGRATED", *common])
        run("obsolete-migration-run", ["dotnet", migrated / "NativeWeave.Compatibility.ApiConsumer.dll"], contains=("consumer passed",))
        original_consumer = binaries["OLD"].parent
        for generation in ("NEW", "DEFAULT", "REMOVED", "BEHAVIOR"):
            output = evidence / "binary-consumers" / generation.lower()
            shutil.copytree(original_consumer, output)
            shutil.copy2(fixture_dlls[generation], output / fixture_dlls[generation].name)
            negative = {"REMOVED": "MissingMethodException", "BEHAVIOR": "compatibility changed"}.get(generation)
            run(f"binary-{generation.lower()}", ["dotnet", output / binaries["OLD"].name], expected=None if negative else 0,
                contains=(negative,) if negative else ("consumer passed",))
        write(evidence / "api-cases.json", api_results)

        # Compile the actual product Core and its existing exact EngineLoadOptions policy.
        core_dll = managed["new"].parent / "NativeWeave.Core.dll"
        core_config = write(evidence / "core-api-config.json", {"assembly": str(core_dll),
            "sources": [str(ROOT / "src/Interop.Negotiation"), str(ROOT / "src/Interop.Errors")], "baselines": [],
            "title": "Actual Core API used by A22", "scope": "Product component API; no new A22 runtime surface",
            "output": str(evidence / "core-reference.md"), "guides": ["docs/guides/verification-compatibility.md"]})
        run("core-api-snapshot", ["dotnet", api_tool, ROOT, dotnet_root, core_config, "--snapshot"])
        current = compat.read_json(evidence / "core-reference.json")
        baseline = compat.read_json(ROOT / "src/Interop.Negotiation/public-api.expected.json")
        select = lambda x: {"symbols": [s for s in x["symbols"] if "NativeWeave.Interop.EngineLoadOptions" in s["id"]
            and (s["id"].startswith("T:") or s["id"].startswith("P:") or s["id"].startswith("M:NativeWeave.Interop.EngineLoadOptions."))]}
        checked = compat.compare_api(select(baseline), select(current))
        assert checked["retained"] == 4 and not checked["added"]
        write(evidence / "engine-load-options-api.json", checked)
        # Both controlled driver generations use the actual existing Core API.
        # The independent ApiFixture evolution negatives do not describe Core.
        old_core = managed["old"].parent / "NativeWeave.Core.dll"
        assert compat.file_hash(old_core) == compat.file_hash(core_dll)
        matrix_record["api"] = {"previous_assembly_sha256": compat.file_hash(old_core), "candidate_assembly_sha256": compat.file_hash(core_dll),
            "previous_snapshot_sha256": compat.file_hash(evidence / "core-reference.json"),
            "candidate_snapshot_sha256": compat.file_hash(evidence / "core-reference.json")}
        write(evidence / "matrix.json", matrix_record)
        policies = policy_cases(ROOT, evidence, managed["old"], managed["new"], natives["old"], natives["new"],
                                evidence / "core-reference.json", evidence / "core-reference.json", {"source_commit": source_commit})
        closure_cases = local_closure(run, evidence, common)
        for path in [ROOT / "Cargo.lock", fixture_source, sample.parent / "Program.cs", core_dll,
                     *api_snapshots.values()]:
            hashes[str(path.relative_to(ROOT))] = {"sha256": compat.file_hash(path)}
        final_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
        final_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        result = {"passed": True, "prepare_only": args.prepare, "source_commit": source_commit,
            "source_dirty": bool(initial_status), "source_stable": initial_status == final_status and source_commit == final_commit,
            "platform": "linux-x64", "matrix_rows": len(matrix), "policy_cases": len(policies),
            "local_closure_cases": closure_cases, "commands": len(commands), "artifact_hashes": hashes,
            "a13_tool": api_tool_inputs,
            "seconds": round(time.time()-started, 3), "scope": "Retained Core ABI/API compatibility; database package release identity and signature rejection are exercised by Packaging.Domain"}
        assert args.prepare or result["source_stable"]
        write(evidence / "result.json", result)
        print(json.dumps(result, indent=2))
    except BaseException as error:
        write(evidence / "failure.json", {"passed": False, "source_commit": source_commit, "error": repr(error), "commands": commands})
        raise


def local_closure(run, evidence, common):
    """Real local NuGet restores, with deliberately unsigned graph-only packages."""
    feed = evidence / "local-feed"; feed.mkdir()
    config = evidence / "local-feed.config"
    config.write_text(f'<configuration><packageSources><clear/><add key="a22-fixtures" value="{feed}"/></packageSources><packageSourceMapping><clear/><packageSource key="a22-fixtures"><package pattern="NativeWeave.Compatibility.*"/></packageSource></packageSourceMapping></configuration>')
    versions = ("1.0.0", "1.1.0")
    closures, paths = {}, {}
    for version in versions:
        entries = []
        packages = {}
        for name in ("Native", "Facade"):
            identity = f"NativeWeave.Compatibility.{name}"
            dependencies = {"NativeWeave.Compatibility.Native": version} if name == "Facade" else {}
            deps = "".join(f'<dependency id="{key}" version="[{value}]" />' for key, value in dependencies.items())
            nuspec = f'<?xml version="1.0"?><package><metadata><id>{identity}</id><version>{version}</version><authors>Conformance</authors><description>Unpublished graph fixture</description><dependencies><group targetFramework="net11.0">{deps}</group></dependencies></metadata></package>'
            package = feed / f"{identity}.{version}.nupkg"
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr(identity + ".nuspec", nuspec)
                archive.writestr("README.md", "Unsigned restore-graph fixture only. Not a release payload.\n")
            entry = {"id": identity, "version": version, "dependencies": dependencies, "unsigned_entries": compat.package_entries(package)}
            entries.append(entry); packages[identity] = package
        closures[version] = {"schema_version": 1, "packages": entries}
        paths[version] = packages
    project = evidence / "closure-consumer"; project.mkdir()
    (project / "Program.cs").write_text('System.Console.WriteLine("Graph-only fixture");\n')
    cases = []
    def restore(name, version, override=None, expected=0):
        direct = f'<PackageReference Include="NativeWeave.Compatibility.Native" Version="[{override}]" />' if override else ""
        (project / "Consumer.csproj").write_text(f'<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net11.0</TargetFramework><OutputType>Exe</OutputType><RestorePackagesWithLockFile>false</RestorePackagesWithLockFile><NoWarn>NU1608</NoWarn></PropertyGroup><ItemGroup><PackageReference Include="NativeWeave.Compatibility.Facade" Version="[{version}]" />{direct}</ItemGroup></Project>')
        run(f"closure-{name}-restore", ["dotnet", "restore", project / "Consumer.csproj", "--configfile", config,
            "--packages", project / ("cache-" + name), "--force", "-p:NuGetAudit=false", *common], expected=expected)
        assets = compat.read_json(project / "obj/project.assets.json")
        try:
            compat.validate_closure(closures[version], paths[version], assets)
        except compat.Rejected as error:
            assert override and str(error).startswith("NWPKG016:")
            cases.append({"name": name, "hard_rejection": str(error)})
        else:
            assert not override
            cases.append({"name": name, "complete": True})
    restore("old-complete", "1.0.0")
    restore("new-complete", "1.1.0")
    restore("direct-override-suppressed", "1.0.0", "1.1.0")
    restore("rollback-old-complete", "1.0.0")
    # Remove the exact native leaf from this local feed; a newer leaf must not be substituted.
    missing = paths["1.0.0"]["NativeWeave.Compatibility.Native"]
    held = missing.with_suffix(".held")
    missing.rename(held)
    try:
        (project / "Consumer.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net11.0</TargetFramework></PropertyGroup><ItemGroup><PackageReference Include="NativeWeave.Compatibility.Facade" Version="[1.0.0]" /></ItemGroup></Project>')
        run("closure-partial-set-restore", ["dotnet", "restore", project / "Consumer.csproj", "--configfile", config,
            "--packages", project / "empty-cache", "--force", "-p:NuGetAudit=false", *common], expected=None, contains=("NU1102",))
        cases.append({"name": "partial-set", "hard_rejection": "NU1102"})
    finally:
        held.rename(missing)
    # A bare minimum edge is not an exact owned dependency, independent of NuGet warnings.
    facade = paths["1.0.0"]["NativeWeave.Compatibility.Facade"]
    with zipfile.ZipFile(facade) as archive:
        name = "NativeWeave.Compatibility.Facade.nuspec"
        raw = archive.read(name).replace(b"[1.0.0]", b"1.0.0")
    from test_policy import rewrite_package
    bare = rewrite_package(facade, evidence / "bare-range.nupkg", {name: raw})
    try:
        compat.package_payload(bare, closures["1.0.0"]["packages"][1])
        raise AssertionError("Bare owned range passed")
    except compat.Rejected as error:
        assert str(error).startswith("NWPKG012:")
        cases.append({"name": "bare-minimum-edge", "hard_rejection": str(error)})
    write(evidence / "local-closure-cases.json", {"scope": "Unsigned local graph fixtures; cryptographic acceptance is separate", "cases": cases})
    return len(cases)


if __name__ == "__main__":
    main()
