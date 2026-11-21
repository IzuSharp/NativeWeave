"""Controlled records exercise gates; actual binaries/signatures are supplied by verify.py."""
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("compatibility", ROOT / "src/Verification.Compatibility/compatibility.py")
compat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compat)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
    return path


def record(path, root):
    return {"path": str(path.relative_to(root)), "sha256": compat.file_hash(path)}


def run(root, evidence, old_dll, new_dll, native_old, native_new, old_api, new_api, behavior):
    cases = []
    def check(name, action, code=None):
        try:
            value = action()
        except compat.Rejected as error:
            if code is None or not str(error).startswith(code + ":"):
                raise
            cases.append({"case": name, "passed": True, "expected_rejection": str(error)})
            return None
        if code is not None:
            raise AssertionError(f"{name}: expected {code}")
        cases.append({"case": name, "passed": True})
        return value

    policy_dir = evidence / "policy"
    policy_dir.mkdir(parents=True, exist_ok=True)
    source = ROOT / "tests/Verification.Compatibility/native/fixture.rs"
    source_files = [source, ROOT / "native/interop/abi/src/lib.rs", ROOT / "native/interop/abi/src/generated.rs",
                    ROOT / "samples/api/verification-compatibility/Program.cs",
                    ROOT / "samples/api/verification-compatibility/CompatibilitySample.csproj",
                    *sorted((ROOT / "src/Interop.Negotiation").glob("*.cs"))]
    inventory = write(policy_dir / "source.json", {"commit": behavior["source_commit"], "files": [record(p, root) for p in source_files]})
    old_receipt = write(policy_dir / "old-behavior.json", {"passed": True, "native_sha256": compat.file_hash(native_old),
        "managed_sha256": compat.file_hash(old_dll), "matrix_receipt": record(evidence / "matrix.json", root)})
    new_receipt = write(policy_dir / "new-behavior.json", {"passed": True, "native_sha256": compat.file_hash(native_new),
        "managed_sha256": compat.file_hash(new_dll), "matrix_receipt": record(evidence / "matrix.json", root)})
    old = {
        "schema_version": 1, "component": "unpublished-a02-a22-conformance", "version": "0.1.0", "rid": "linux-x64",
        "source_commit": behavior["source_commit"], "available_utc": "2026-01-01T00:00:00Z",
        "artifacts": {"managed": record(old_dll, root), "native": record(native_old, root), "api": record(old_api, root),
            "api_assembly": record(old_dll.parent / "NativeWeave.Core.dll", root),
            "cargo_lock": record(ROOT / "Cargo.lock", root), "source_inventory": record(inventory, root),
            "behavior_receipt": record(old_receipt, root)},
        "abi": {"major": 1, "minor": 0, "layout_sha256": compat.file_hash(ROOT / "native/interop/abi/src/generated.rs"),
                "capabilities": {"compat.base.v1": 0}, "required": ["compat.base.v1"]},
        "domain": {"schema": 1, "semantics": "wrapping-add-seven-v1", "errors": "a05-v1", "cancellation": "not-async"},
        "upstream": {"commit": behavior["source_commit"], "public_seams": {"write_abi_v1": record(ROOT / "native/interop/abi/src/lib.rs", root)},
            "private_seams": {}, "features": [], "msrv": "1.100", "dependencies": [], "patches": []}
    }
    new = deepcopy(old)
    new.update(version="0.2.0")
    new["abi"].update(minor=1, capabilities={"compat.base.v1": 0, "compat.optional.v1": 1})
    new["artifacts"].update(managed=record(new_dll, root), native=record(native_new, root), api=record(new_api, root),
                             behavior_receipt=record(new_receipt, root), api_assembly=record(new_dll.parent / "NativeWeave.Core.dll", root))
    previous_path, candidate_path = policy_dir / "previous.json", policy_dir / "candidate.json"
    review_path = policy_dir / "controlled-review.json"
    write(previous_path, old)
    write(candidate_path, new)
    base_review = {"previous_sha256": compat.file_hash(previous_path), "candidate_sha256": compat.file_hash(candidate_path),
        "reviewer": "controlled-test-fixture-not-independent-approval", "decision": "compatible",
        "regression_receipt": record(evidence / "matrix.json", root), "reviewed_upstream_changes": []}
    write(review_path, base_review)
    def compare(candidate=None, review=None):
        write(candidate_path, new if candidate is None else candidate)
        r = deepcopy(base_review if review is None else review)
        r["candidate_sha256"] = compat.file_hash(candidate_path)
        write(review_path, r)
        return compat.compare_components(previous_path, candidate_path, root, review_path,
                                         datetime(2026, 11, 17, tzinfo=timezone.utc))
    check("optional-minor-addition", compare)
    failed_matrix = deepcopy(compat.read_json(evidence / "matrix.json")); failed_matrix["passed"] = False
    failed_path = write(policy_dir / "failed-regression.json", failed_matrix)
    bad_review = deepcopy(base_review); bad_review["regression_receipt"] = record(failed_path, root)
    check("failed-complete-regression", lambda: compare(review=bad_review), "NWCMP007")
    unrelated_matrix = deepcopy(compat.read_json(evidence / "matrix.json")); unrelated_matrix["rows"] = []
    unrelated_path = write(policy_dir / "unrelated-regression.json", unrelated_matrix)
    bad_review = deepcopy(base_review); bad_review["regression_receipt"] = record(unrelated_path, root)
    check("empty-complete-regression", lambda: compare(review=bad_review), "NWCMP007")
    unrelated_matrix = deepcopy(compat.read_json(evidence / "matrix.json"))
    unrelated_matrix["rows"][0]["managed_profile"]["sha256"] = "0" * 64
    unrelated_path = write(policy_dir / "stale-pair-regression.json", unrelated_matrix)
    bad_review = deepcopy(base_review); bad_review["regression_receipt"] = record(unrelated_path, root)
    check("stale-cross-pair-regression", lambda: compare(review=bad_review), "NWCMP007")
    failed_negative = deepcopy(compat.read_json(evidence / "matrix.json"))
    next(row for row in failed_negative["rows"] if row["scenario"] != "pass")["passed"] = False
    failed_negative_path = write(policy_dir / "failed-negative-regression.json", failed_negative)
    bad_review = deepcopy(base_review); bad_review["regression_receipt"] = record(failed_negative_path, root)
    check("failed-negative-matrix-row", lambda: compare(review=bad_review), "NWCMP007")
    for name, path, value, code in [
        ("upstream-branch-not-commit", ("upstream", "commit"), "main", "NWCMP005"),
        ("major", ("abi", "major"), 2, "NWCMP004"),
        ("layout", ("abi", "layout_sha256"), "0" * 64, "NWCMP004"),
        ("semantic", ("domain", "semantics"), "wrapping-add-eight-v1", "NWCMP003"),
        ("schema", ("domain", "schema"), 2, "NWCMP003"),
        ("capability-bit", ("abi", "capabilities"), {"compat.base.v1": 2}, "NWCMP004"),
        ("required-feature", ("abi", "required"), ["compat.optional.v1"], "NWCMP004"),
        ("features", ("upstream", "features"), ["changed-default"], "NWCMP007"),
        ("msrv", ("upstream", "msrv"), "1.101", "NWCMP007"),
        ("dependencies-license", ("upstream", "dependencies"), [{"name": "controlled", "version": "2", "license": "different", "checksum": "0" * 64}], "NWCMP007"),
        ("private-seam", ("upstream", "private_seams"), {"private_layout": {**record(source, root), "visibility": "private",
             "symbol": "controlled_source_fixture", "start_line": 1, "end_line": 3, "assumptions": "Controlled record change, not an actual private dependency"}}, "NWCMP007")
    ]:
        bad = deepcopy(new)
        bad[path[0]][path[1]] = value
        check(name, lambda bad=bad: compare(bad), code)
    bad = deepcopy(new); bad["artifacts"]["native"]["sha256"] = "0" * 64
    check("stale-artifact", lambda: compare(bad), "NWCMP002")
    bad = deepcopy(new); bad["upstream"]["private_seams"] = {"outside": {**record(source, root), "visibility": "private",
        "symbol": "controlled", "start_line": 100000, "end_line": 100001, "assumptions": "Invalid location negative"}}
    check("private-seam-outside-file", lambda: compare(bad), "NWCMP005")
    bad = deepcopy(new); bad["source_commit"] = "0" * 40
    check("source-provenance-substitution", lambda: compare(bad), "NWCMP002")
    compare()
    review = deepcopy(base_review); review["previous_sha256"] = "0" * 64
    check("review-manifest-substitution", lambda: compare(review=review), "NWCMP007")
    bad = deepcopy(new); bad["available_utc"] = None
    check("unknown-availability", lambda: compare(bad), "NWCMP008")
    bad["available_utc"] = "2026-11-16T00:00:00Z"
    check("seven-day-cooldown", lambda: compare(bad), "NWCMP008")
    lock_diff = policy_dir / "controlled-lock-diff.txt"
    lock_diff.write_text("Controlled security-exception fixture; the actual Cargo.lock is unchanged.\n")
    review = deepcopy(base_review)
    review["security_exception"] = {"advisory": "controlled-test-no-real-advisory", "rationale": "Exercise explicit review binding",
        "risk_decision": "Fixture only; does not authorize a production update", "lock_diff": record(lock_diff, root),
        "regression_receipt": record(evidence / "matrix.json", root)}
    check("bound-security-exception", lambda: compare(bad, review))
    failed_security = deepcopy(review); failed_security["security_exception"]["regression_receipt"] = record(failed_path, root)
    check("failed-security-regression", lambda: compare(bad, failed_security), "NWCMP007")
    patch = policy_dir / "controlled.patch"; patch.write_text("Controlled patch queue identity fixture; not applied to any upstream.\n")
    differential = write(policy_dir / "controlled-differential.json", {"passed": True,
        "scope": "Controlled binding fixture, not an applied upstream patch or executed upstream differential proof",
        "upstream_commit": behavior["source_commit"], "patch_sha256": compat.file_hash(patch),
        "native_sha256": compat.file_hash(native_new), "matrix_receipt": record(evidence / "matrix.json", root)})
    fork = deepcopy(new)
    fork["upstream"]["patches"] = [{"upstream_commit": behavior["source_commit"], "owner": "A22-test-role",
        "upstream_issue": "controlled-test", "exit_condition": "Remove when public seam exists", "public_replacement_available": False,
        "patch": record(patch, root), "differential_receipt": record(differential, root)}]
    review = deepcopy(base_review); review["reviewed_upstream_changes"] = ["patches"]
    check("exact-fork-patch-queue", lambda: compare(fork, review))
    fork["upstream"]["patches"][0]["upstream_commit"] = "0" * 40
    check("fork-upstream-drift", lambda: compare(fork, review), "NWCMP005")
    fork["upstream"]["patches"][0]["upstream_commit"] = behavior["source_commit"]
    fork["upstream"]["patches"][0]["public_replacement_available"] = True
    check("fork-public-replacement", lambda: compare(fork, review), "NWCMP005")
    compare()
    write(policy_dir / "cases.json", cases)
    return cases
