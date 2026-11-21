"""Fault-inject the actual release main; no packages, tools or apps are executed.

The publication/consumer boundaries below are explicit control-flow stubs. Their
success is not B24 product acceptance; only the persisted overall state is tested.
"""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location("b24_release_cases", Path(__file__).with_name("release_cases.py"))
CASES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CASES)

from model import validate_database_payload


class DatabasePayloadTests(unittest.TestCase):
    """Nuspec/file-layout fixtures exercise scope gates, not product binaries."""

    def package(self, directory, *, dependency="", extra=None):
        path = directory / "fixture.nupkg"
        metadata = ('<package><metadata><id>NativeWeave.Data</id><version>1.0.0-test</version>'
                    + dependency + '</metadata></package>')
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("NativeWeave.Data.nuspec", metadata)
            archive.writestr("lib/net11.0/NativeWeave.Data.dll", b"unexecuted scope fixture")
            if extra:
                archive.writestr(extra, b"unexecuted unwanted asset")
        return path

    def test_external_protocol_dependency_is_rejected(self):
        expected = {"id": "NativeWeave.Data", "dependencies": {}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            valid = self.package(root)
            self.assertEqual(validate_database_payload(valid, expected)["dependencies"], {})
            invalid = self.package(root, dependency='<dependencies><dependency id="Grpc.Core" version="[1.0.0]" /></dependencies>')
            with self.assertRaisesRegex(ValueError, "Retired non-database package"):
                validate_database_payload(invalid, expected)

    def test_undeclared_native_and_managed_runtime_files_are_rejected(self):
        expected = {"id": "NativeWeave.Data", "dependencies": {}}
        with tempfile.TemporaryDirectory() as temporary:
            for name in ("runtimes/linux-x64/native/libnativeweave_server.so", "lib/net11.0/NativeWeave.Server.dll"):
                with self.subTest(name=name):
                    invalid = self.package(Path(temporary), extra=name)
                    with self.assertRaisesRegex(ValueError, "undeclared"):
                        validate_database_payload(invalid, expected)


class ReleaseResultTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "output"
        self.manifest_path = self.root / "manifest.json"
        self.manifest = {"sourceCommit": "1" * 40}
        self.records = {}
        self.transitions = []
        self.original_atomic = CASES.release.atomic_json
        for closure in ("previous", "candidate"):
            directory = self.root / closure
            directory.mkdir()
            item = {"id": "NativeWeave.Fixture.Native", "version": "1.0.0-" + closure, "native": True}
            # Uninterpreted fixture bytes, not a built or valid NuGet package.
            (directory / f"{item['id']}.{item['version']}.nupkg").write_bytes(closure.encode())
            record = {"source_commit": self.manifest["sourceCommit"], "rid": "linux-x64", "packages": [item],
                      "builder_identity": "nativeweave-local-reviewed-staging"}
            self.records[closure] = record
            CASES.save(directory / "record.json", record)
            self.manifest[closure] = {"releaseRecord": closure + "/record.json", "feed": closure}
        CASES.save(self.manifest_path, self.manifest)

    def publish_stub(self, record, feed, destination, journal, catalog, verify, consume, fault=None):
        if record["builder_identity"] == "unknown-builder":
            raise CASES.release.compat.Rejected("NWPKG015 fixture unknown builder")
        if any(item.get("upload_archive_sha256") == "0" * 64 for item in record["packages"]):
            raise CASES.release.compat.Rejected("NWPKG004 fixture wrong provenance subject")
        destination.mkdir(parents=True, exist_ok=True)
        self.original_atomic(journal, {"status": "partial-unadvertised"})
        packages = {}
        for item in record["packages"]:
            name = f"{item['id']}.{item['version']}.nupkg"
            source, target = feed / name, destination / name
            if target.exists() and target.read_bytes() != source.read_bytes():
                raise CASES.release.compat.Rejected("NWPKG004 fixture conflict")
            target.write_bytes(source.read_bytes())
            packages[item["id"]] = target
            if fault:
                fault("uploaded", item)
        consume(record, packages)
        result = {"packages": {identity: CASES.sha(path) for identity, path in packages.items()}}
        self.original_atomic(journal, {"status": "completed"})
        self.original_atomic(catalog, result)
        return result

    def rollback_stub(self, record, packages, receipt, active_processes):
        if active_processes:
            raise CASES.release.compat.Rejected("NWPKG017 fixture active process")
        if set(packages) != {item["id"] for item in record["packages"]}:
            raise CASES.release.compat.Rejected("NWPKG011 fixture missing package")
        if receipt["source_commit"] != record["source_commit"]:
            raise CASES.release.compat.Rejected("NWPKG001 fixture source mismatch")
        if receipt["rid"] != record["rid"]:
            raise CASES.release.compat.Rejected("NWPKG001 fixture RID mismatch")
        return {"deployment": "fixture-fresh-process", "packages": receipt["packages"]}

    def run_main(self, *, consume_error=None, index_error=False):
        evidence = self.output / "evidence"

        def consume_stub(arguments, **kwargs):
            self.assertEqual(Path(arguments[1]), CASES.ROOT / "src/Packaging.Domain/consume.py")
            if consume_error is not None:
                raise consume_error
            closure = arguments[arguments.index("--closure") + 1]
            destination = Path(arguments[arguments.index("--feed") + 1])
            directory = Path(arguments[arguments.index("--output") + 1])
            directory.mkdir()
            record = self.records[closure]
            receipt = {"passed": True, "rid": record["rid"], "source_commit": record["source_commit"],
                "consumer_environment": arguments[arguments.index("--consumer-environment") + 1],
                "pristine_machine": arguments[arguments.index("--consumer-environment") + 1] == "pristine",
                "packages": {item["id"]: CASES.sha(destination / f"{item['id']}.{item['version']}.nupkg")
                             for item in record["packages"]}}
            CASES.save(directory / "receipt.json", receipt)
            return subprocess.CompletedProcess(arguments, 0, b"", b"")

        def observe_atomic(path, value):
            if path == evidence / "evidence-index.json":
                # Even all completed cases cannot pass before index creation.
                for result in (self.output / "result.json", evidence / "result.json"):
                    running = json.loads(result.read_text())
                    self.assertFalse(running["passed"])
                    self.assertEqual(running["status"], "running")
                    self.assertEqual(len(running["cases"]), len(CASES.EXPECTED_CASES))
                if index_error:
                    raise OSError("injected evidence index failure")
            if path in (self.output / "result.json", evidence / "result.json"):
                snapshot = json.loads(json.dumps(value))
                self.transitions.append((path, snapshot))
                if snapshot["passed"]:
                    self.assertEqual(snapshot["status"], "completed")
                    self.assertEqual({item["name"] for item in snapshot["cases"]}, CASES.EXPECTED_CASES)
                    self.assertEqual(len(snapshot["cases"]), len(CASES.EXPECTED_CASES))
                    index = json.loads((evidence / "evidence-index.json").read_text())
                    for name in ("previous-journal.json", "previous-catalog.json", "existing-journal.json",
                                 "existing-catalog.json", "candidate-journal.json", "candidate-catalog.json", "conflict-journal.json"):
                        self.assertEqual(index["files"][name], CASES.sha(evidence / name))
                    self.assertEqual(index["files"]["result.json"], CASES.hashlib.sha256(CASES.json_bytes(snapshot)).hexdigest())
            self.original_atomic(path, value)

        with (patch.object(CASES, "load_manifest", return_value=self.manifest),
              patch.object(CASES.release, "publish", side_effect=self.publish_stub),
              patch.object(CASES.release, "rollback", side_effect=self.rollback_stub),
              patch.object(CASES.release, "verify_registry", side_effect=CASES.release.compat.Rejected("NWPKG015 fixture unsigned")),
              patch.object(CASES.release, "atomic_json", side_effect=observe_atomic),
              patch.object(CASES.subprocess, "run", side_effect=consume_stub),
              patch.object(CASES.sys, "argv", ["release_cases.py", "--manifest", str(self.manifest_path), "--output", str(self.output)]),
              redirect_stdout(io.StringIO())):
            CASES.main()

    def assert_incomplete(self, case_count):
        for path in (self.output / "result.json", self.output / "evidence/result.json"):
            value = json.loads(path.read_text())
            self.assertFalse(value["passed"])
            self.assertEqual(value["status"], "running")
            self.assertEqual(len(value["cases"]), case_count)
            self.assertEqual(value["cases"][0]["name"], "partial-domain-publication-unadvertised")
        self.assertTrue(self.transitions)
        self.assertTrue(all(value["passed"] is False for _, value in self.transitions))

    def test_later_consumer_exception_preserves_incomplete_result(self):
        with self.assertRaisesRegex(RuntimeError, "injected consume failure"):
            self.run_main(consume_error=RuntimeError("injected consume failure"))
        self.assert_incomplete(1)
        self.assertFalse((self.output / "evidence/evidence-index.json").exists())

    def test_later_consumer_interruption_preserves_incomplete_result(self):
        with self.assertRaisesRegex(KeyboardInterrupt, "injected consume interruption"):
            self.run_main(consume_error=KeyboardInterrupt("injected consume interruption"))
        self.assert_incomplete(1)

    def test_index_failure_after_all_cases_preserves_incomplete_result(self):
        with self.assertRaisesRegex(OSError, "injected evidence index failure"):
            self.run_main(index_error=True)
        self.assert_incomplete(len(CASES.EXPECTED_CASES))

    def test_only_terminal_success_is_indexed_and_committed(self):
        self.run_main()
        result, evidence_result = self.output / "result.json", self.output / "evidence/result.json"
        self.assertEqual(result.read_bytes(), evidence_result.read_bytes())
        terminal = json.loads(result.read_text())
        self.assertTrue(terminal["passed"])
        self.assertEqual(terminal["status"], "completed")
        self.assertTrue(all(value["passed"] is False for _, value in self.transitions[:-2]))
        self.assertEqual([path for path, value in self.transitions[-2:] if value["passed"]], [evidence_result, result])
        index = json.loads((self.output / "evidence/evidence-index.json").read_text())
        for name, expected in index["files"].items():
            self.assertEqual(CASES.sha(self.output / "evidence" / name), expected)


if __name__ == "__main__":
    unittest.main()
