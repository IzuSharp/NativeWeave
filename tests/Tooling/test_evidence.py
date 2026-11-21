"""Export only useful fixture assertions; private input canaries must stay local."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eng"))
import build


class FixtureEvidenceTests(unittest.TestCase):
    def test_private_canaries_do_not_enter_export_but_assertions_and_origin_hash_do(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "private"
            source.mkdir()
            target = root / "export"
            (source / "config.private.json").write_text('{"cursorKey":"CONFIG_CANARY"}')
            (source / "raw.log").write_text("LOG_CANARY")
            result = source / "receipt.json"
            result.write_text(json.dumps({"status": "passed", "cases": [{"id": "nullable-key", "status": "passed"}],
                "command": ["psql", "postgresql://user:ARG_CANARY@localhost/db"],
                "error_context": "postgresql://user:URI_CANARY@localhost/db",
                "configuration": {"password": "NESTED_CANARY"}}))
            component = source / "provider"
            component.mkdir()
            for name in ("summary.json", "status.json"):
                (component / name).write_text(json.dumps({"result": "failed", "completed_commands": 7,
                    "details": {"argv": ["ARG_CANARY"], "connectionString": "PRIVATE_CANARY"},
                    "error": "postgresql://user:URI_CANARY@localhost/db"}))
            before = result.read_bytes()
            build.export_fixture_results(source, target)
            files = list(target.rglob("*"))
            self.assertEqual(["provider/status.json", "provider/summary.json", "receipt.json"],
                             sorted(str(p.relative_to(target)) for p in files if p.is_file()))
            text = (target / "receipt.json").read_text()
            self.assertNotIn("CANARY", text)
            exported = json.loads(text)
            self.assertEqual(build.digest(result), exported["source_artifact_sha256"])
            self.assertTrue(exported["sanitized"])
            self.assertEqual("passed", exported["data"]["cases"][0]["status"])
            self.assertEqual(before, result.read_bytes())
            for name in ("summary.json", "status.json"):
                text = (target / "provider" / name).read_text()
                self.assertNotIn("CANARY", text)
                component_result = json.loads(text)
                self.assertEqual("failed", component_result["data"]["result"])
                self.assertEqual(7, component_result["data"]["completed_commands"])
                self.assertEqual(build.digest(component / name), component_result["source_artifact_sha256"])


if __name__ == "__main__":
    unittest.main()
