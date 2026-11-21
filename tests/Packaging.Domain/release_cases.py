#!/usr/bin/env python3
"""Exercise real database publication, destination consumers and rollback locally.

Run in the existing pristine SDK container, or select explicitly labeled local
mechanism verification. There is one candidate full consumer
and two previous-version smoke processes; no historical component matrix runs.
Only evidence/ is suitable for CI upload. Other directories contain local feeds,
consumer caches and databases.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/Packaging.Domain"))
from model import TASK, json_bytes, load_manifest, module, relative_file, save, sha

release = module("domain_release", "src/Packaging.Release/release.py")
EXPECTED_CASES = frozenset((
    "partial-domain-publication-unadvertised",
    "resume-and-actual-previous-consumption",
    "matching-existing-closure-readback",
    "candidate-upgrade-and-actual-full-consumption",
    "complete-previous-closure-fresh-process-rollback",
    "live-process-rollback-rejected",
    "partial-rollback-rejected",
    "wrong-source-rollback-rejected",
    "wrong-rid-rollback-rejected",
    "unknown-builder-rejected",
    "wrong-provenance-subject-rejected",
    "same-native-version-conflict-rejected",
    "unsigned-domain-repository-signature-rejected",
    "signature-scope",
))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--consumer-environment", choices=("local", "pristine"), default="pristine")
    args = parser.parse_args()
    manifest_path, output = args.manifest.resolve(), args.output.resolve()
    manifest = load_manifest(manifest_path)
    output.mkdir(parents=True, exist_ok=False)
    evidence = output / "evidence"
    evidence.mkdir()
    cases, commands, receipts = [], [], {}
    destination = output / "destination"
    value = {"schemaVersion": 1, "task": TASK, "passed": False, "status": "running",
             "sourceCommit": manifest["sourceCommit"], "manifestSha256": sha(manifest_path), "rid": "linux-x64",
             "publicDomainReleaseAccepted": False, "newDomainSignerAuthenticated": False,
             "consumer_environment": args.consumer_environment,
             "pristine_machine": args.consumer_environment == "pristine",
             "scope": "Local immutable destination and actual new-process consumption; no public registry write or native hot replacement.",
             "cases": cases}

    def progress():
        # A stopped or failed orchestration must never advertise partial success.
        release.atomic_json(output / "result.json", value)
        release.atomic_json(evidence / "result.json", value)

    progress()

    def record(name, **facts):
        cases.append({"name": name, "passed": True, **facts})
        progress()
        print(name, "passed", flush=True)

    def reject(name, action, code):
        try:
            action()
        except release.compat.Rejected as error:
            if code not in str(error):
                raise
            record(name, rejectionCode=code, error=str(error))
        else:
            raise AssertionError("Required rejection did not occur: " + name)

    def actual_consume(name, closure, mode):
        result_dir = output / name
        arguments = [sys.executable, ROOT / "src/Packaging.Domain/consume.py", "--manifest", manifest_path,
                     "--closure", closure, "--feed", destination, "--output", result_dir, "--mode", mode,
                     "--consumer-environment", args.consumer_environment]
        result = subprocess.run(list(map(str, arguments)), cwd=ROOT, capture_output=True, timeout=1800)
        command = {"label": name, "argv": list(map(str, arguments)), "exitCode": result.returncode, "processExited": True}
        for suffix, data in (("stdout", result.stdout), ("stderr", result.stderr)):
            file = output / (name + "." + suffix)
            file.write_bytes(data)
            command[suffix + "Sha256"] = sha(file)
        commands.append(command)
        save(output / "commands.json", commands)
        save(evidence / "commands.json", commands)
        if result.returncode:
            raise RuntimeError(name + ": " + (result.stdout + result.stderr).decode(errors="replace")[-6000:])
        receipt_file = result_dir / "receipt.json"
        receipt = json.loads(receipt_file.read_text())
        if receipt.get("passed") is not True:
            raise ValueError("Actual domain consumer did not pass")
        if (receipt.get("consumer_environment") != args.consumer_environment
                or receipt.get("pristine_machine") is not (args.consumer_environment == "pristine")):
            raise ValueError("Actual consumer evidence names a different environment")
        save(evidence / (name + ".receipt.json"), receipt)
        # The consumer owns its safe evidence subset. Never recursively upload
        # its working directory, native packages, database or private test keys.
        if (result_dir / "evidence").is_dir():
            shutil.copytree(result_dir / "evidence", evidence / name)
        receipts[closure] = receipt
        return receipt

    records = {name: json.loads(relative_file(manifest_path.parent, manifest[name]["releaseRecord"]).read_text())
               for name in ("previous", "candidate")}
    feeds = {name: relative_file(manifest_path.parent, manifest[name]["feed"]) for name in records}
    previous, candidate = records["previous"], records["candidate"]
    journal, catalog = output / "previous-journal.json", output / "previous-catalog.json"
    attempted = []
    def interrupt(phase, item):
        attempted.append(item["id"])
        if item.get("native"):
            raise InterruptedError("controlled native-leaf upload interruption")
    try:
        release.publish(previous, feeds["previous"], destination, journal, catalog,
                        release.verify_local, lambda *_: {}, interrupt)
    except InterruptedError:
        partial = json.loads(journal.read_text())
        if catalog.exists() or partial["status"] != "partial-unadvertised":
            raise AssertionError("Interrupted domain publication exposed a complete catalog")
        save(evidence / "interrupted-journal.json", partial)
        record("partial-domain-publication-unadvertised", uploaded=attempted)
    else:
        raise AssertionError("Controlled native-leaf interruption did not execute")
    resumed = release.publish(previous, feeds["previous"], destination, journal, catalog, release.verify_local,
        lambda *_: actual_consume("previous-destination", "previous", "smoke"))
    record("resume-and-actual-previous-consumption", packageCount=len(resumed["packages"]), receiptSha256=sha(evidence / "previous-destination.receipt.json"))
    replayed = release.publish(previous, feeds["previous"], destination, output / "existing-journal.json", output / "existing-catalog.json",
        release.verify_local, lambda *_: receipts["previous"])
    record("matching-existing-closure-readback", packageCount=len(replayed["packages"]),
           consumptionReuse="Exact same destination and package bytes already consumed by the completed previous process.")
    upgraded = release.publish(candidate, feeds["candidate"], destination, output / "candidate-journal.json", output / "candidate-catalog.json",
        release.verify_local, lambda *_: actual_consume("candidate-destination", "candidate", "full"))
    record("candidate-upgrade-and-actual-full-consumption", packageCount=len(upgraded["packages"]), receiptSha256=sha(evidence / "candidate-destination.receipt.json"))
    previous_map = {item["id"]: destination / f"{item['id']}.{item['version']}.nupkg" for item in previous["packages"]}
    rollback = release.rollback(previous, previous_map, receipts["previous"], active_processes=0)
    fresh = actual_consume("rollback-destination", "previous", "smoke")
    if fresh.get("packages") != rollback["packages"] or fresh.get("source_commit") != previous["source_commit"] or fresh.get("rid") != previous["rid"]:
        raise AssertionError("Fresh rollback process did not consume the complete previous closure")
    record("complete-previous-closure-fresh-process-rollback", deployment=rollback["deployment"], receiptSha256=sha(evidence / "rollback-destination.receipt.json"))
    reject("live-process-rollback-rejected", lambda: release.rollback(previous, previous_map, fresh, 1), "NWPKG017")
    incomplete = dict(previous_map)
    incomplete.pop(next(item["id"] for item in previous["packages"] if item.get("native")))
    reject("partial-rollback-rejected", lambda: release.rollback(previous, incomplete, fresh, 0), "NWPKG011")
    wrong_receipt = copy.deepcopy(fresh)
    wrong_receipt["source_commit"] = "0" * 40
    reject("wrong-source-rollback-rejected", lambda: release.rollback(previous, previous_map, wrong_receipt, 0), "NWPKG001")
    wrong_receipt = copy.deepcopy(fresh)
    wrong_receipt["rid"] = "win-x64"
    reject("wrong-rid-rollback-rejected", lambda: release.rollback(previous, previous_map, wrong_receipt, 0), "NWPKG001")
    unknown = copy.deepcopy(previous)
    unknown["builder_identity"] = "unknown-builder"
    reject("unknown-builder-rejected", lambda: release.publish(unknown, feeds["previous"], output / "unknown-builder",
        output / "unknown-builder-journal.json", output / "unknown-builder-catalog.json", release.verify_local, lambda *_: {}), "NWPKG015")
    wrong_subject = copy.deepcopy(previous)
    wrong_subject["packages"][0]["upload_archive_sha256"] = "0" * 64
    reject("wrong-provenance-subject-rejected", lambda: release.publish(wrong_subject, feeds["previous"], output / "wrong-subject",
        output / "wrong-subject-journal.json", output / "wrong-subject-catalog.json", release.verify_local, lambda *_: {}), "NWPKG004")
    if any((output / name).exists() for name in ("unknown-builder-catalog.json", "wrong-subject-catalog.json")):
        raise AssertionError("Rejected builder or provenance was advertised")
    selected = next(item for item in candidate["packages"] if item.get("native"))
    native_package = feeds["candidate"] / f"{selected['id']}.{selected['version']}.nupkg"
    conflicts = output / "conflicting-destination"
    conflicts.mkdir()
    (conflicts / native_package.name).write_bytes(native_package.read_bytes() + b"immutable-version-conflict")
    reject("same-native-version-conflict-rejected", lambda: release.publish(candidate, feeds["candidate"], conflicts,
        output / "conflict-journal.json", output / "conflict-catalog.json", release.verify_local, lambda *_: {}), "NWPKG004")
    if (output / "conflict-catalog.json").exists():
        raise AssertionError("Conflicting native version was advertised")
    policy = json.loads((ROOT / "tests/Verification.Compatibility/signature-policy.json").read_text())
    reject("unsigned-domain-repository-signature-rejected", lambda: release.verify_registry(native_package, native_package,
        selected, policy, output / "unsigned-signature"), "NWPKG015")
    record("signature-scope", signatureMechanism="Existing A22 real dotnet nuget verify path rejected this unsigned domain leaf.",
           positiveHistoricalMechanism="Retained A16/A22 evidence only; not a new domain signer or public release claim.")
    if (len(cases) != len(EXPECTED_CASES) or {item["name"] for item in cases} != EXPECTED_CASES
            or not all(item["passed"] is True for item in cases)):
        raise AssertionError("The required database release cases did not all complete")
    for name in ("previous-journal.json", "previous-catalog.json", "existing-journal.json", "existing-catalog.json",
                 "candidate-journal.json", "candidate-catalog.json", "conflict-journal.json"):
        shutil.copyfile(output / name, evidence / name)
    completed = {**value, "status": "completed", "passed": True}
    # json_bytes and the existing atomic_json writer use the same canonical JSON
    # encoding. Index the terminal bytes before exposing either success marker.
    final_hash = hashlib.sha256(json_bytes(completed)).hexdigest()
    files = {path.relative_to(evidence).as_posix(): sha(path) for path in sorted(evidence.rglob("*"))
             if path.is_file() and path not in (evidence / "result.json", evidence / "evidence-index.json")}
    files["result.json"] = final_hash
    release.atomic_json(evidence / "evidence-index.json", {"schemaVersion": 1,
        "scope": "Safe database JSON evidence subset; no private test keys, database files or package payloads.", "files": files})
    release.atomic_json(evidence / "result.json", completed)
    # Keep the top-level result as the final orchestration commit marker.
    release.atomic_json(output / "result.json", completed)
    print("PASS local domain publication, full candidate consumption, and fresh-process whole-closure rollback.", flush=True)


if __name__ == "__main__":
    main()
