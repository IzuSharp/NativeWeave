#!/usr/bin/env python3
"""Finite package-consumer database scenarios with independent durable SQL oracles."""
import argparse
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid

from golden import verify_fixture, scope_hash, create_hash
from postgres_oracles import run_postgres_oracles

HERE = Path(__file__).resolve().parent


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


class Database:
    """Independent CPython SQLite / PostgreSQL command-line SQL, outside NativeWeave."""
    def __init__(self, provider, database, psql='psql'):
        self.provider, self.database, self.psql = provider, database, psql

    def sql(self, statement):
        return self.query(statement)

    def scalar(self, statement):
        rows = self.query(statement)
        if len(rows) != 1 or len(rows[0]) != 1: raise AssertionError('Expected one scalar SQL result.')
        return rows[0][0]

    def replay(self, operation):
        encoded = "encode(response_bytes,'hex')" if self.provider == 'postgresql' else 'lower(hex(response_bytes))'
        rows = self.query('SELECT response_version,response_status,' + encoded + " FROM operations WHERE operation_id='" + operation + "'")
        if len(rows) != 1: raise AssertionError('Expected one durable replay.')
        return int(rows[0][0]), int(rows[0][1]), bytes.fromhex(rows[0][2])

    def query(self, statement):
        if self.provider == 'sqlite':
            with sqlite3.connect(self.database) as connection:
                return connection.execute(statement).fetchall()
        result = subprocess.run([str(self.psql), self.database, '-X', '--csv', '-t', '-v',
            'ON_ERROR_STOP=1', '-c', statement], text=True, capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError('Independent psql failed: ' + result.stderr[-1000:])
        return [tuple(None if value == '\\N' else value for value in row)
                for row in csv.reader(io.StringIO(result.stdout)) if row]


def configuration(provider, database, output):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    return {'provider': provider, 'database': str(database), 'blobDirectory': str(output / 'blobs'),
        'consumerDatabase': str(output / 'consumer.sqlite'), 'cursorKey': base64.b64encode(bytes(range(32))).decode(),
        'principals': [{'tenant': 'tenant-a', 'principal': 'alice', 'canWrite': True}],
        'allowLocalDatabaseTlsDisable': provider == 'postgresql', 'operationTimeoutSeconds': 90,
        'caseKey': 'db-scope-' + uuid.uuid4().hex, 'caseTitle': 'Strongly typed database fixture 世界'}


def run_case(command, config, mode, output, environment=None, timeout=120):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    path = output / 'config.private.json'; save(path, config); path.chmod(0o600)
    result = subprocess.run([*map(str, command), '--config', str(path), mode],
        env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    (output / 'process.log').write_text(result.stdout)
    if result.returncode:
        raise AssertionError('Database fixture failed (' + mode + '); inspect ' + str(output / 'process.log'))
    if mode == '--migrate-only':
        if 'MIGRATED' not in result.stdout.splitlines(): raise AssertionError('Missing migration completion.')
        return {'case': mode}
    lines = [line[len('DATABASE_REFERENCE_RESULT '):] for line in result.stdout.splitlines()
        if line.startswith('DATABASE_REFERENCE_RESULT ')]
    if len(lines) != 1: raise AssertionError('Expected one completed database fixture receipt.')
    receipt = json.loads(lines[0])
    if not receipt['databaseResourcesReleased'] or not receipt['consumerResourcesReleased']:
        raise AssertionError('The fixture did not release database resources.')
    save(output / 'receipt.json', receipt)
    return receipt


def reconcile(config, receipt, psql):
    database = Database(config['provider'], config['database'], psql)
    statements = {'items': ('SELECT count(*) FROM items', 3),
        'operations': ('SELECT count(*) FROM operations', 4),
        'outbox': ('SELECT count(*) FROM outbox', 4),
        'attachments': ('SELECT count(*) FROM attachments', 1),
        'stale_rollback': ("SELECT count(*) FROM operations WHERE request_key LIKE '%-stale'", 0),
        'delivered_outbox': ('SELECT count(*) FROM outbox WHERE delivery_state=2 AND completed_at>0', 4),
        'item_versions': ('SELECT sum(version) FROM items', 4)}
    observations = {}
    for name, (statement, expected) in statements.items():
        rows = database.query(statement)
        if len(rows) != 1 or int(rows[0][0]) != expected: raise AssertionError('Independent SQL failed: ' + name)
        observations[name] = {'expected': expected, 'observed': int(rows[0][0])}
    if config['provider'] == 'sqlite':
        if database.query('PRAGMA integrity_check') != [('ok',)] or database.query('PRAGMA foreign_key_check'):
            raise AssertionError('SQLite integrity or foreign-key check failed.')
    with sqlite3.connect(config['consumerDatabase']) as consumer:
        rows = consumer.execute('SELECT count(*),sum(effects),sum(delivery_attempts) FROM receipts').fetchone()
        if rows != (4, 4, 4): raise AssertionError('Outbox consumer effect/receipt oracle failed: ' + str(rows))
        observations['outbox_consumer'] = list(rows)
    first = receipt['replies'][0]
    encode = "encode(response_bytes,'hex')" if config['provider'] == 'postgresql' else 'lower(hex(response_bytes))'
    rows = database.query('SELECT ' + encode + " FROM operations WHERE operation_id='" + first['operationId'] + "'")
    if len(rows) != 1 or rows[0][0] != first['bytesHex']: raise AssertionError('Durable replay differs from returned bytes.')
    observations['replay_sha256'] = hashlib.sha256(bytes.fromhex(first['bytesHex'])).hexdigest()
    return observations


def keyset_checks(command, config, output, psql):
    """Force real composite-order ties and compare every public result with independent SQL."""
    config = dict(config, skipMigrations=True)
    database = Database(config['provider'], config['database'], psql)
    for index in range(6):
        seed = dict(config, caseKey='keyset-page-' + str(index), caseTitle='keyset page ' + str(index))
        receipt = run_case(command, seed, '--create-case', output / ('seed-' + str(index)))
        if receipt['replies'][0]['status'] != 201: raise AssertionError('Keyset seed operation failed.')
    tenant = config['principals'][0]['tenant'].replace("'", "''")
    database.query(f"UPDATE items SET created_at=1790000000000 WHERE tenant_id='{tenant}'")
    expected_rows = database.query(f"SELECT item_id,created_at FROM items WHERE tenant_id='{tenant}' ORDER BY created_at,item_id")
    if len(expected_rows) < 8 or any(int(row[1]) != 1790000000000 for row in expected_rows):
        raise AssertionError('Independent SQL did not establish a nontrivial real keyset tie group.')
    expected = [row[0] for row in expected_rows]
    receipt = run_case(command, config, '--keyset-case', output / 'traverse')
    observed = receipt['checks']['keyset-observed-item-order'].split(',')
    if observed != expected or len(set(observed)) != len(expected):
        raise AssertionError('Composite keyset traversal lost, duplicated or reordered tied rows.')
    for name in ('tampered-valid-cursor-rejected', 'cross-tenant-valid-cursor-rejected', 'cross-principal-valid-cursor-rejected'):
        if receipt['checks'].get(name) != 'passed': raise AssertionError('Missing cursor authority oracle: ' + name)
    result = {'passed': True, 'tie_created_at': 1790000000000, 'expected_item_order': expected,
        'observed_item_order': observed, 'checks': receipt['checks']}
    save(output / 'independent-keyset.json', result)
    return result


def maintenance_checks(command, config, receipt, output, psql):
    """Retain independent redelivery, retention, protected recovery and orphan checks."""
    config = dict(config, skipMigrations=True)
    db = Database(config['provider'], config['database'], psql)
    consumer = Database('sqlite', config['consumerDatabase'])
    checks = {}
    def check(name, passed):
        if not passed: raise AssertionError('Maintenance oracle failed: ' + name)
        checks[name] = 'passed'
    def run(mode, label, selected=None):
        return run_case(command, selected or config, mode, output / label)
    first = receipt['replies'][0]
    event = db.scalar("SELECT event_id FROM outbox WHERE operation_id='" + first['operationId'] + "'")
    before = int(consumer.scalar("SELECT delivery_attempts FROM receipts WHERE event_id='" + event + "'"))
    db.sql("UPDATE outbox SET delivery_state=0,available_at=0,lease_until=0,completed_at=0 WHERE event_id='" + event + "'")
    run('--outbox-once', 'explicit-redelivery')
    check('persistent-consumer-counts-duplicate', int(consumer.scalar("SELECT delivery_attempts FROM receipts WHERE event_id='" + event + "'")) == before + 1)
    check('persistent-consumer-one-effect', int(consumer.scalar('SELECT count(*) FROM receipts WHERE effects<>1')) == 0)
    retention = run('--create-case', 'expired-key-fixture', dict(config, caseKey='retention-expiry', caseTitle='retention example'))['replies'][0]
    within = run('--create-case', 'within-window-fixture', dict(config, caseKey='retention-within-window', caseTitle='retention guarantee'))['replies'][0]
    delivered = run('--outbox-once', 'publish-retention-fixtures')
    check('bounded-outbox-claim', int(delivered['checks']['delivered']) == 2)
    check('outbox-acknowledged', int(db.scalar('SELECT count(*) FROM outbox WHERE delivery_state<>2')) == 0)
    now = int(time.time() * 1000); old = now - 8 * 24 * 60 * 60 * 1000
    within_id = within['operationId']; operation = retention['operationId']
    within_event = db.scalar("SELECT event_id FROM outbox WHERE operation_id='" + within_id + "' AND delivery_state=2")
    check('within-window-effect-confirmed', int(consumer.scalar("SELECT effects FROM receipts WHERE event_id='" + within_event + "'")) == 1)
    db.sql("DELETE FROM outbox WHERE operation_id='" + within_id + "' AND delivery_state=2")
    db.sql(f"UPDATE operations SET completed_at={now - 7 * 24 * 60 * 60 * 1000 + 3600000} WHERE operation_id='{within_id}'")
    db.sql(f"UPDATE operations SET completed_at={old} WHERE operation_id='{operation}'")
    db.sql(f"UPDATE outbox SET delivery_state=0,completed_at=0 WHERE operation_id='{operation}'")
    run('--maintenance-once', 'pending-outbox')
    check('pending-outbox-protects-old-operation', int(db.scalar(f"SELECT count(*) FROM operations WHERE operation_id='{operation}'")) == 1)
    db.sql(f"UPDATE outbox SET delivery_state=2,completed_at={old} WHERE operation_id='{operation}'")
    root = Path(config['blobDirectory']); principal = config['principals'][0]
    recovery = root / 'recovery' / (operation + '.json')
    save(recovery, {'version': 1, 'operationId': operation,
        'scope': scope_hash(principal['tenant'], principal['principal'], 'POST /v1/items'), 'requestKey': 'retention-expiry',
        'requestHash': create_hash(principal['tenant'], principal['principal'], 'retention example'), 'createdAt': old})
    run('--maintenance-once', 'confirmed-recovery')
    check('durable-result-reconciles-recovery', not recovery.exists())
    check('expired-unreferenced-operation-removed', int(db.scalar(f"SELECT count(*) FROM operations WHERE operation_id='{operation}'")) == 0)
    unresolved_id = str(uuid.uuid4()); unresolved = recovery.parent / (unresolved_id + '.json')
    save(unresolved, {'version': 1, 'operationId': unresolved_id,
        'scope': scope_hash(principal['tenant'], principal['principal'], 'POST /v1/items'), 'requestKey': 'unconfirmed-recovery',
        'requestHash': create_hash(principal['tenant'], principal['principal'], 'unconfirmed'), 'createdAt': old})
    run('--maintenance-once', 'unconfirmed-recovery')
    check('missing-row-keeps-recovery-protection', unresolved.exists())
    fixtures = {}
    for name in ['old-orphan', 'recent-orphan', 'protected-recovery']:
        payload = ('independent-' + name).encode(); digest = hashlib.sha256(payload).hexdigest()
        path = root / 'blobs' / digest; path.write_bytes(payload); fixtures[name] = (path, payload, digest)
        if name != 'recent-orphan': os.utime(path, (old / 1000, old / 1000))
    protected_id = str(uuid.uuid4()); protected = fixtures['protected-recovery']
    original = json.loads(bytes.fromhex(first['bytesHex']))
    save(root / 'staging' / (protected_id + '.json'), {'version': 1, 'operationId': protected_id,
        'tenant': principal['tenant'], 'principal': principal['principal'], 'itemId': original['itemId'],
        'requestKey': 'protected-fixture', 'expectedVersion': 2, 'contentHash': protected[2],
        'contentLength': len(protected[1]), 'state': 'prepared', 'createdAt': old})
    run('--maintenance-once', 'orphan-grace-and-protection')
    check('old-orphan-collected', not fixtures['old-orphan'][0].exists())
    check('recent-blob-grace-preserved', fixtures['recent-orphan'][0].exists())
    check('prepared-recovery-blob-preserved', protected[0].exists())
    check('inside-seven-day-window-survives', db.replay(within_id) == (1, 201, bytes.fromhex(within['bytesHex'])))
    replay = run('--create-case', 'within-window-replay', dict(config, caseKey='retention-within-window', caseTitle='retention guarantee'))['replies'][0]
    check('within-window-exact-replay-after-restart', replay['status'] == 201 and replay['bytesHex'] == within['bytesHex'])
    expired = run('--create-case', 'expired-key-reuse', dict(config, caseKey='retention-expiry', caseTitle='retention example'))['replies'][0]
    check('expired-key-has-no-permanent-replay-promise', expired['status'] == 201 and expired['operationId'] != operation)
    save(output / 'result.json', checks)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['sqlite', 'postgresql'], required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--psql', default='psql')
    parser.add_argument('--mode', choices=['jit', 'aot'], required=True)
    parser.add_argument('--postgres-oracles', action='store_true')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command: parser.error('An already-built consumer command is required after --.')
    args.output.mkdir(parents=True, exist_ok=False)
    result = {'task': 'DB-Scope-01', 'provider': args.provider, 'mode': args.mode, 'passed': False}
    try:
        golden = subprocess.run([*command, '--golden-vectors'], capture_output=True, text=True, timeout=30, check=True)
        if json.loads(golden.stdout) != verify_fixture(HERE / 'golden-v1.json'):
            raise AssertionError('Actual canonical bytes differ from independent immutable golden vectors.')
        save(args.output / 'golden-actual.json', json.loads(golden.stdout))
        config = configuration(args.provider, args.database, args.output)
        receipt = run_case(command, config, '--verify', args.output / 'verify')
        if receipt['dynamicCodeSupported'] != (args.mode == 'jit'): raise AssertionError('Actual runtime mode mismatch.')
        result['checks'] = receipt['checks']
        result['independent_sql'] = reconcile(config, receipt, args.psql)
        result['maintenance_checks'] = maintenance_checks(command, config, receipt, args.output / 'maintenance', args.psql)
        result['keyset_checks'] = keyset_checks(command, config, args.output / 'keyset', args.psql)
        if args.postgres_oracles:
            if args.provider != 'postgresql': raise ValueError('PostgreSQL oracles need PostgreSQL.')
            config['skipMigrations'] = True
            sql = Database(args.provider, args.database, args.psql).query
            result['postgres_oracles'] = run_postgres_oracles(command, config, args.output / 'postgres-oracles',
                lambda selected, mode, directory: run_case(command, selected, mode, directory), sql)
        result['passed'] = True
        return 0
    except BaseException as error:
        result['failure'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        save(args.output / 'result.json', result)


if __name__ == '__main__':
    sys.exit(main())
