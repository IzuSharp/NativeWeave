#!/usr/bin/env python3
"""Finite real database fault cells against an already-built reference package consumer."""
from __future__ import annotations
import argparse
import contextlib
import json
from pathlib import Path
import shutil
import subprocess

from faults import Faults
from harness import Evidence, HERE, PostgresCluster, REFERENCE, require, sha

COMMON = ('outbox-after-publication-before-ack', 'upload-before-durable-content',
          'upload-after-rename-before-commit', 'orphan-collection-interrupted')
POSTGRES = ('begin-transport-loss', 'write-transport-loss', 'commit-held-before-upstream-send',
            'commit-acknowledgement-discarded', 'provider-drain-failure', 'postgres-restart')
SQLITE = ('sqlite-busy', 'sqlite-write-enospc')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-directory', type=Path, required=True)
    parser.add_argument('--mode', choices=['jit', 'aot'], required=True)
    parser.add_argument('--provider', choices=['sqlite', 'postgresql'], required=True)
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--postgres-bin', type=Path, default=Path(shutil.which('postgres') or '/usr/lib/postgresql/18/bin/postgres').parent)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', nargs='+')
    parser.add_argument('--filesystem-shim', type=Path)
    args = parser.parse_args()
    artifact = args.artifact_directory.resolve()
    executable = artifact / ('NativeWeave.Reference.TaskService.dll' if args.mode == 'jit' else 'NativeWeave.Reference.TaskService')
    require(executable.is_file(), 'The selected actual reference consumer does not exist')
    required = (*POSTGRES, *COMMON) if args.provider == 'postgresql' else (*SQLITE, *COMMON)
    selected = args.cases or list(required)
    require(len(set(selected)) == len(selected) and all(case in required for case in selected), 'Unknown or duplicate fault selection')
    command = [args.dotnet, str(executable)] if args.mode == 'jit' else [str(executable)]
    identity = {'mode': args.mode, 'provider': args.provider, 'program': command,
        'executableSha256': sha(executable), 'artifactDirectory': str(artifact),
        'artifacts': {str(path.relative_to(artifact)): sha(path) for path in sorted(artifact.rglob('*')) if path.is_file()},
        'controller': {path.name: sha(path) for path in sorted(HERE.glob('*.py'))},
        'referenceController': {path.name: sha(path) for path in (REFERENCE / 'run.py', REFERENCE / 'golden.py', REFERENCE / 'postgres_oracles.py')},
        'requiredFaultCasesForProvider': list(required), 'selectedFaultCases': selected, 'performanceMeasurement': False}
    evidence = Evidence(args.output.resolve(), identity)
    completed = False; outer_failure = None
    try:
        shim = args.filesystem_shim.resolve() if args.filesystem_shim else evidence.output / 'libdatabase_filesystem_fault.so'
        if args.filesystem_shim is None:
            source = HERE.parents[1] / 'src/Verification.EndToEnd/FilesystemFaults/fs_fault.c'
            compiler = shutil.which('cc'); require(compiler is not None, 'The isolated filesystem fault shim needs a C compiler')
            argv = [compiler, '-std=c11', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', str(source), '-ldl', '-o', str(shim)]
            with (evidence.output / 'shim-build.log').open('wb') as log:
                build = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, timeout=60)
            require(build.returncode == 0, 'Filesystem fault shim compilation failed')
            evidence.record['filesystemShim'] = {'sourceSha256': sha(source), 'sha256': sha(shim), 'command': argv,
                'scope': 'disposable verification child only; packaged database libraries unchanged'}
        cluster_scope = PostgresCluster(args.postgres_bin, evidence.output / 'postgres') if args.provider == 'postgresql' else contextlib.nullcontext(None)
        with cluster_scope as cluster:
            faults = Faults(command, args.provider, evidence, cluster=cluster, shim=shim)
            actions = {'begin-transport-loss': lambda path: faults.pg_disconnect(path, 'begin'),
                'write-transport-loss': lambda path: faults.pg_disconnect(path, 'items_insert'),
                'commit-held-before-upstream-send': lambda path: faults.pg_commit(path, acknowledgement_loss=False),
                'commit-acknowledgement-discarded': lambda path: faults.pg_commit(path, acknowledgement_loss=True),
                'provider-drain-failure': faults.pg_drain, 'postgres-restart': faults.pg_restart,
                'sqlite-busy': faults.sqlite_busy, 'sqlite-write-enospc': faults.sqlite_enospc,
                'outbox-after-publication-before-ack': faults.outbox_crash,
                'upload-before-durable-content': lambda path: faults.upload_crash(path, after_rename=False),
                'upload-after-rename-before-commit': lambda path: faults.upload_crash(path, after_rename=True),
                'orphan-collection-interrupted': faults.gc_crash}
            for name in selected:
                print('DATABASE_FAULT_BEGIN ' + name, flush=True)
                try:
                    with evidence.case(name) as path: actions[name](path)
                except Exception as error:
                    print('DATABASE_FAULT_FAILED ' + name + ' ' + type(error).__name__, flush=True)
                else: print('DATABASE_FAULT_END ' + name, flush=True)
        completed = True
    except BaseException as error:
        outer_failure = type(error).__name__ + ': ' + str(error)
    finally:
        cases = evidence.record['cases']; executed = [case['id'] for case in cases]
        complete = completed and outer_failure is None and executed == selected and all(case['status'] == 'passed' for case in cases)
        evidence.record.update(status='passed' if complete else 'incomplete', completedOuterLifecycle=completed,
            outerFailure=outer_failure, selectedCasesComplete=executed == selected,
            notSelected=[case for case in required if case not in selected],
            selectedNotExecuted=[case for case in selected if case not in executed])
        evidence.save(); evidence.timeline.close()
    print(json.dumps({'status': evidence.record['status'], 'receipt': str(evidence.output / 'receipt.json')}, sort_keys=True))
    return 0 if evidence.record['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
