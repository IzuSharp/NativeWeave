"""Bounded external process/evidence helpers for database-only composition.

No NativeWeave implementation is imported. The reference fixture supplies its independent SQL adapter, never product outcomes.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "Reference.TaskService"
sys.path.insert(0, str(REFERENCE))
_spec = importlib.util.spec_from_file_location("database_reference_fixture", REFERENCE / "run.py")
assert _spec and _spec.loader
reference = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reference)
Database = reference.Database
run_case = reference.run_case
from postgres_oracles import PostgreSqlProxy, OracleFailure, _cstring  # noqa: E402


class Unavailable(RuntimeError):
    """An explicit real execution precondition is absent; never a passed case."""


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".new")
    with temporary.open("wb") as stream:
        stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OracleFailure(message)


def eventually(predicate: Callable[[], Any], description: str, timeout: float = 30) -> Any:
    deadline = time.monotonic() + timeout
    while True:
        value = predicate()
        if value:
            return value
        if time.monotonic() >= deadline:
            raise OracleFailure("Missing actual barrier: " + description)
        time.sleep(0.01)


class Request:
    """One independent external request with finite owned completion state."""
    def __init__(self, action: Callable[[], Any]):
        self.done = threading.Event()
        self.value = None
        self.error: BaseException | None = None
        def run():
            try:
                self.value = action()
            except BaseException as error:
                self.error = error
            finally:
                self.done.set()
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def result(self, timeout: float = 60, *, allow_transport_error: bool = False):
        require(self.done.wait(timeout), "External request exceeded its finite controller deadline")
        if self.error is not None:
            if allow_transport_error:
                return {"transportError": type(self.error).__name__}
            raise self.error
        return self.value


class Evidence:
    def __init__(self, output: Path, identity: dict[str, Any]):
        self.output = output
        output.mkdir(parents=True, exist_ok=False)
        self.started = time.monotonic_ns()
        self.record: dict[str, Any] = {"schemaVersion": 1, "task": "DB-Scope-01", "platform": "linux-x64",
            "identity": identity, "startedUnixNs": time.time_ns(), "status": "running", "cases": []}
        self.timeline = (output / "timeline.jsonl").open("w", encoding="utf-8")
        self.current: dict[str, Any] | None = None
        self.save()

    def event(self, name: str, **fields):
        self.timeline.write(json.dumps({"monotonicNs": time.monotonic_ns(), "event": name, **fields}, sort_keys=True) + "\n")
        self.timeline.flush()

    def save(self):
        self.record["elapsedSeconds"] = (time.monotonic_ns() - self.started) / 1e9
        write_json(self.output / "receipt.json", self.record)

    def check(self, name: str, condition: bool, **observations):
        require(self.current is not None, "Assertion outside a case")
        item = {"id": name, "status": "passed" if condition else "failed", "observations": observations}
        self.current["assertions"].append(item)
        self.event("assertion", case=self.current["id"], **item)
        self.save()
        require(condition, name)

    @contextlib.contextmanager
    def case(self, name: str):
        require(self.current is None, "Cases must not overlap mutable evidence ownership")
        value = {"id": name, "status": "running", "assertions": [], "startedMonotonicNs": time.monotonic_ns()}
        self.record["cases"].append(value); self.current = value
        self.event("case-start", case=name); self.save()
        try:
            yield self.output / name
            require(bool(value["assertions"]), "A case without a nonvacuous observation cannot pass")
            value["status"] = "passed"
        except Unavailable as error:
            value["status"] = "unavailable"
            value["reason"] = str(error)
        except BaseException as error:
            value["status"] = "interrupted" if isinstance(error, (KeyboardInterrupt, SystemExit)) else "failed"
            value["failureType"] = type(error).__name__
            # SQL/provider exceptions may contain bound values. Only oracle-owned
            # assertions are copied into the public receipt.
            if isinstance(error, OracleFailure):
                value["failure"] = str(error)
            raise
        finally:
            value["elapsedSeconds"] = (time.monotonic_ns() - value["startedMonotonicNs"]) / 1e9
            self.event("case-end", case=name, status=value["status"])
            self.current = None; self.save()

    def close(self):
        cases = self.record["cases"]
        self.record["status"] = "passed" if cases and all(x["status"] == "passed" for x in cases) else "incomplete"
        self.save(); self.timeline.close()


class PostgresCluster:
    """Disposable PostgreSQL18 children owned by this controller invocation."""
    def __init__(self, binary: Path, output: Path):
        self.binary, self.output = binary.resolve(), output
        self.running = False

    def run(self, name, argv, timeout=90):
        with (self.output / (name + ".log")).open("ab") as log:
            completed = subprocess.run(list(map(str, argv)), stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
        require(completed.returncode == 0, "PostgreSQL lifecycle command failed: " + name)

    def __enter__(self):
        self.output.mkdir(parents=True, exist_ok=False)
        version = subprocess.check_output([self.binary / "postgres", "--version"], text=True).strip()
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0)); self.port = listener.getsockname()[1]
        self.data = self.output / "data"
        self.run("init", [self.binary / "initdb", "-D", self.data, "-U", "nativeweave", "--auth=trust", "--no-locale", "--encoding=UTF8"])
        self.uri = f"postgresql://nativeweave@127.0.0.1:{self.port}/postgres"
        self.start()
        write_json(self.output / "identity.json", {"version": version, "postgresSha256": sha(self.binary / "postgres"), "psqlSha256": sha(self.binary / "psql")})
        return self

    def start(self):
        self.run("start", [self.binary / "pg_ctl", "-D", self.data, "-l", self.output / "server.log", "-o", f"-h 127.0.0.1 -p {self.port} -k ''", "-w", "start"])
        self.running = True

    def stop(self, *, immediate=False):
        if self.running:
            self.run("immediate-stop" if immediate else "stop", [self.binary / "pg_ctl", "-D", self.data, "-m", "immediate" if immediate else "fast", "-w", "stop"])
            self.running = False

    def database(self):
        name = "b22_" + secrets.token_hex(8)
        Database("postgresql", self.uri, str(self.binary / "psql")).sql('CREATE DATABASE "' + name + '"')
        return self.uri.rsplit("/", 1)[0] + "/" + name

    def __exit__(self, *args):
        self.stop()


def configuration(provider: str, database: str, output: Path):
    config = reference.configuration(provider, database, output)
    config['orphanGraceSeconds'] = 60
    return config


def admin(command, config, option, output, timeout=120):
    return run_case(command, config, option, output, timeout=timeout)


class OneShot:
    """One finite, externally controlled migration/business/maintenance process."""
    def __init__(self, command, config, option, output):
        self.output = output
        output.mkdir(parents=True, exist_ok=False)
        private = output / 'config.private.json'
        write_json(private, config); private.chmod(0o600)
        self.log = (output / 'process.log').open('wb')
        self.process = subprocess.Popen([*command, '--config', str(private), option],
            stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        self.crashed = False

    def crash(self):
        require(self.process.poll() is None, 'Fault requires a live database fixture process')
        os.killpg(self.process.pid, signal.SIGKILL); self.process.wait(timeout=15)
        require(self.process.returncode == -signal.SIGKILL, 'Fixture process crash was not observed')
        self.crashed = True

    def result(self, timeout=120):
        self.process.wait(timeout=timeout); self.log.flush()
        require(self.process.returncode == 0, 'Finite database fixture failed: ' + str(self.output / 'process.log'))
        lines = [line[len('DATABASE_REFERENCE_RESULT '):] for line in (self.output / 'process.log').read_text().splitlines()
            if line.startswith('DATABASE_REFERENCE_RESULT ')]
        require(len(lines) == 1, 'Missing actual fixture completion receipt')
        receipt = json.loads(lines[0])
        require(receipt['databaseResourcesReleased'] and receipt['consumerResourcesReleased'], 'Database resources were not released')
        write_json(self.output / 'receipt.json', receipt)
        return receipt

    def close(self):
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGKILL); self.process.wait(timeout=15)
        self.log.close()
