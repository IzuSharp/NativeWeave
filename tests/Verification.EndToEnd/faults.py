"""Real database and filesystem failures with independent durable-data oracles."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time

from harness import Database, Evidence, OneShot, Request, admin, configuration, eventually, require
from protocol_proxy import FaultProxy

PAYLOAD = b'Database immutable attachment\n' * 4096


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def events(path):
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class Faults:
    def __init__(self, command, provider, evidence: Evidence, *, cluster=None, shim=None):
        self.command, self.provider, self.evidence = command, provider, evidence
        self.cluster, self.shim = cluster, shim

    def setup(self, path):
        path.mkdir(parents=True, exist_ok=False)
        database = self.cluster.database() if self.provider == 'postgresql' else str(path / 'application.sqlite')
        config = configuration(self.provider, database, path)
        sql = Database(self.provider, database, str(self.cluster.binary / 'psql') if self.cluster else 'psql')
        admin(self.command, config, '--migrate-only', path / 'migration')
        config['skipMigrations'] = True
        return config, sql

    def create(self, config, path, key, title='Database fault fixture'):
        return admin(self.command, dict(config, caseKey=key, caseTitle=title), '--create-case', path)['replies'][0]

    def atomic(self, sql, key, count, *, response=None):
        rows = sql.sql('SELECT operation_id FROM operations WHERE request_key=' + quote(key))
        self.evidence.check('operation-cardinality', len(rows) == count, observed=len(rows), expected=count)
        for row in rows:
            operation = row[0]
            item = int(sql.scalar('SELECT count(*) FROM items WHERE operation_id=' + quote(operation)))
            outbox = int(sql.scalar('SELECT count(*) FROM outbox WHERE operation_id=' + quote(operation)))
            self.evidence.check('atomic-item-result-outbox', item == 1 and outbox == 1, items=item, outbox=outbox)
            if response is not None:
                version, status, stored = sql.replay(operation)
                self.evidence.check('stored-response-bytes', version == 1 and status == 201 and stored == response,
                                    bytes=len(stored), sha256=hashlib.sha256(stored).hexdigest())

    def no_attachment(self, sql, item):
        count = int(sql.scalar('SELECT count(*) FROM attachments WHERE item_id=' + quote(item)))
        version = int(sql.scalar('SELECT version FROM items WHERE item_id=' + quote(item)))
        self.evidence.check('no-incomplete-reference', count == 0 and version == 1, references=count, itemVersion=version)

    def preload(self, path, mode, target):
        require(self.shim is not None, 'The isolated filesystem fault shim is required')
        audit, arm, release = path / 'filesystem.jsonl', path / 'filesystem.arm', path / 'filesystem.release'
        prefix = ['env', 'LD_PRELOAD=' + str(self.shim), 'NW_B22_IO_TARGET=' + str(target),
                  'NW_B22_IO_ARM=' + str(arm), 'NW_B22_IO_AUDIT=' + str(audit),
                  'NW_B22_IO_RELEASE=' + str(release), 'NW_B22_IO_MODE=' + mode]
        return [*prefix, *self.command], arm, audit, release

    def pg_disconnect(self, path, category):
        config, sql = self.setup(path)
        key = 'fault-' + category
        with FaultProxy(config['database'], path / 'proxy') as proxy:
            proxy.arm_fault(category, 'disconnect')
            selected = dict(config, database=proxy.database_uri, caseKey=key)
            receipt = admin(self.command, selected, '--failure-case', path / 'failed')
            proxy.wait()
            self.evidence.check('real-boundary-error', receipt['replies'][0]['status'] == 0, error=receipt['replies'][0]['errorKind'])
            self.atomic(sql, key, 0)
            reply = self.create(selected, path / 'retry', key)
            self.evidence.check('retry-after-transport-loss', reply['status'] == 201)
            self.atomic(sql, key, 1, response=bytes.fromhex(reply['bytesHex']))
            self.evidence.check('proxy-has-no-controller-failure', not proxy.failures, count=len(proxy.failures))

    def pg_commit(self, path, *, acknowledgement_loss):
        config, sql = self.setup(path); key = 'commit-fault'
        with FaultProxy(config['database'], path / 'proxy') as proxy:
            proxy.arm_fault('commit', 'discard' if acknowledgement_loss else 'hold')
            selected = dict(config, database=proxy.database_uri, caseKey=key)
            request = Request(lambda: admin(self.command, selected, '--unknown-case', path / 'fixture'))
            proxy.wait()
            if not acknowledgement_loss:
                self.atomic(sql, key, 0)
                proxy.disconnect_selected()
            receipt = request.result()
            replies = receipt['replies']
            self.evidence.check('uncertain-commit-distinct', replies[0]['status'] == 503 and
                json.loads(bytes.fromhex(replies[0]['bytesHex']))['code'] == 'outcome_unknown')
            self.evidence.check('independent-recovery-outcome', replies[1]['status'] == (200 if acknowledgement_loss else 404))
            self.evidence.check('unknown-remains-protected', receipt['checks']['unknown-recovery-protected'] == 'passed')
            if acknowledgement_loss:
                self.evidence.check('actual-commit-ack-discarded', proxy.discarded.is_set())
            self.atomic(sql, key, 1, response=bytes.fromhex(replies[2]['bytesHex']))
            self.evidence.check('proxy-has-no-controller-failure', not proxy.failures, count=len(proxy.failures))

    def pg_drain(self, path):
        config, sql = self.setup(path); key = 'drain'
        with FaultProxy(config['database'], path / 'proxy') as proxy:
            proxy.arm_fault('drain_after_commit', 'disconnect', match_number=2)
            receipt = admin(self.command, dict(config, database=proxy.database_uri, caseKey=key), '--retry-case', path / 'fixture')
            pid = proxy.wait(); first, second = receipt['replies']
            self.evidence.check('committed-effect-survives-cleanup-failure', first['status'] == 201 and second['status'] == 201 and first['bytesHex'] == second['bytesHex'])
            self.atomic(sql, key, 1, response=bytes.fromhex(first['bytesHex']))
            claims = [row for row in proxy.snapshot() if row['event'] == 'command' and row.get('category') == 'operations_insert']
            self.evidence.check('discarded-connection-is-not-reused', len(claims) == 2 and claims[0]['backend_pid'] == pid and claims[1]['backend_pid'] not in (None, pid), failedBackendPid=pid, claimBackends=[row['backend_pid'] for row in claims])
            eventually(lambda: int(sql.scalar(f'SELECT count(*) FROM pg_stat_activity WHERE pid={pid}')) == 0, 'failed backend retirement')
            self.evidence.check('proxy-has-no-controller-failure', not proxy.failures, count=len(proxy.failures))

    def pg_restart(self, path):
        config, sql = self.setup(path); key = 'restart'
        with FaultProxy(config['database'], path / 'proxy', timeout=60) as proxy:
            proxy.arm_fault('commit', 'hold')
            process = OneShot(self.command, dict(config, database=proxy.database_uri, caseKey=key), '--create-case', path / 'fixture')
            try:
                proxy.wait(); self.cluster.stop(immediate=True); proxy.disconnect_selected()
                receipt = process.result()
                self.evidence.check('restart-does-not-invent-confirmation', receipt['replies'][0]['status'] == 503)
            finally:
                self.cluster.start(); process.close()
            self.atomic(sql, key, 0)
            reply = self.create(config, path / 'retry', key)
            self.evidence.check('actual-postgres-restart-recovery', reply['status'] == 201)
            self.atomic(sql, key, 1, response=bytes.fromhex(reply['bytesHex']))

    def sqlite_busy(self, path):
        config, sql = self.setup(path); key = 'busy'
        with sqlite3.connect(config['database'], isolation_level=None) as writer:
            writer.execute('BEGIN IMMEDIATE')
            receipt = admin(self.command, dict(config, caseKey=key), '--failure-case', path / 'failed')
            self.evidence.check('real-busy-rejected', writer.in_transaction and receipt['replies'][0]['status'] == 0,
                                error=receipt['replies'][0]['errorKind'])
            self.atomic(sql, key, 0); writer.execute('ROLLBACK')
        reply = self.create(config, path / 'retry', key)
        self.evidence.check('busy-release-restores-admission', reply['status'] == 201)
        self.atomic(sql, key, 1, response=bytes.fromhex(reply['bytesHex']))

    def sqlite_enospc(self, path):
        config, sql = self.setup(path); key = 'disk-full'
        command, arm, audit, _ = self.preload(path, 'enospc', config['database'] + '-wal')
        arm.write_text('one exact WAL write\n')
        receipt = admin(command, dict(config, caseKey=key), '--unknown-case', path / 'fixture')
        observed = events(audit)
        self.evidence.check('actual-native-wal-write-was-faulted', len(observed) == 1 and observed[0]['event'] == 'injected-libc-enospc', injection=observed)
        self.evidence.check('commit-io-failure-preserves-unknown', receipt['replies'][0]['status'] == 503)
        self.evidence.check('storage-fault-not-durable', receipt['replies'][1]['status'] == 404)
        self.evidence.check('actual-sqlite-full-provider-code', receipt['replies'][0].get('providerCode') == '13')
        self.atomic(sql, key, 1, response=bytes.fromhex(receipt['replies'][2]['bytesHex']))
        self.evidence.check('sqlite-integrity-after-enospc', sql.scalar('PRAGMA integrity_check') == 'ok')

    def outbox_crash(self, path):
        config, sql = self.setup(path)
        reply = self.create(config, path / 'initial', 'outbox')
        self.evidence.check('outbox-fixture-committed', reply['status'] == 201)
        event = sql.scalar('SELECT event_id FROM outbox')
        consumer = Database('sqlite', config['consumerDatabase'])
        if self.provider == 'postgresql':
            with FaultProxy(config['database'], path / 'proxy', timeout=60) as proxy:
                proxy.arm_fault('outbox_update', 'hold', match_number=2)
                process = OneShot(self.command, dict(config, database=proxy.database_uri), '--outbox-once', path / 'crash-worker')
                try:
                    proxy.wait()
                    self.evidence.check('consumer-durable-before-source-ack', consumer.sql('SELECT delivery_attempts,effects FROM receipts') == [(1, 1)])
                    process.crash(); proxy.disconnect_selected()
                finally: process.close()
        else:
            command, arm, audit, release = self.preload(path, 'after-sync', config['consumerDatabase'] + '-wal')
            arm.write_text('pause consumer WAL before source acknowledgment\n')
            process = OneShot(command, config, '--outbox-once', path / 'crash-worker')
            writer = None
            try:
                eventually(lambda: any(x['event'] == 'completed-filesystem-call-held' for x in events(audit)), 'consumer WAL sync barrier')
                writer = sqlite3.connect(config['database'], isolation_level=None); writer.execute('BEGIN IMMEDIATE')
                release.write_text('source acknowledgement blocked by independent writer\n')
                eventually(lambda: consumer.sql('SELECT delivery_attempts,effects FROM receipts') == [(1, 1)], 'committed consumer receipt', timeout=4)
                self.evidence.check('consumer-durable-before-source-ack', consumer.sql('SELECT delivery_attempts,effects FROM receipts') == [(1, 1)])
                process.crash()
            finally:
                if writer is not None: writer.execute('ROLLBACK'); writer.close()
                process.close()
        state, attempts, lease = sql.sql('SELECT delivery_state,attempt_count,lease_until FROM outbox')[0]
        self.evidence.check('source-ack-not-recorded', int(state) == 1 and int(attempts) == 1)
        deadline = int(lease) / 1000
        self.evidence.event('waiting-real-outbox-lease', leaseUntilUnixMs=int(lease))
        while time.time() < deadline + 0.05: time.sleep(min(0.5, max(0.01, deadline + 0.05 - time.time())))
        admin(self.command, config, '--outbox-once', path / 'restarted-worker')
        receipts = consumer.sql('SELECT event_id,delivery_attempts,effects FROM receipts')
        self.evidence.check('at-least-once-one-effect', receipts == [(event, 2, 1)], receipts=receipts)
        self.evidence.check('retry-ack-committed', int(sql.scalar('SELECT delivery_state FROM outbox')) == 2)

    def upload_crash(self, path, *, after_rename):
        config, sql = self.setup(path)
        reply = self.create(config, path / 'parent', 'upload-parent')
        require(reply['status'] == 201, 'Attachment parent must commit')
        item = json.loads(bytes.fromhex(reply['bytesHex']))['itemId']
        digest = hashlib.sha256(PAYLOAD).hexdigest()
        proxy_context = FaultProxy(config['database'], path / 'proxy', timeout=60) if after_rename and self.provider == 'postgresql' else contextlib.nullcontext(None)
        with proxy_context as proxy:
            runtime_config = dict(config, caseKey='upload-crash', database=proxy.database_uri if proxy else config['database'])
            writer = None
            if after_rename:
                command = self.command
                if proxy: proxy.arm_fault('begin', 'hold')
                else:
                    writer = sqlite3.connect(config['database'], isolation_level=None); writer.execute('BEGIN IMMEDIATE')
            else:
                command, arm, audit, _ = self.preload(path, 'after-staging-write', str(Path(config['blobDirectory']) / 'staging') + '/')
                arm.write_text('hold first staged content write\n')
            process = OneShot(command, runtime_config, '--attachment-case', path / 'crashed-fixture')
            try:
                if after_rename:
                    if proxy: proxy.wait()
                    blob = Path(config['blobDirectory']) / 'blobs' / digest
                    eventually(lambda: blob.exists(), 'immutable content rename before database binding')
                    self.evidence.check('renamed-content-complete', blob.read_bytes() == PAYLOAD)
                else:
                    eventually(lambda: any(x['event'] == 'completed-filesystem-call-held' for x in events(audit)), 'actual first staged content write')
                    sizes = [part.stat().st_size for part in (Path(config['blobDirectory']) / 'staging').glob('*.part')]
                    self.evidence.check('staged-content-incomplete', len(sizes) == 1 and 0 < sizes[0] < len(PAYLOAD), sizes=sizes, expectedLength=len(PAYLOAD))
                self.no_attachment(sql, item); process.crash()
            finally:
                if proxy: proxy.disconnect_selected()
                if writer is not None: writer.execute('ROLLBACK'); writer.close()
                process.close()
        self.no_attachment(sql, item)
        receipt = admin(self.command, dict(config, caseKey='upload-crash'), '--attachment-case', path / 'recovery')
        self.evidence.check('same-key-attachment-recovery', receipt['replies'][0]['status'] == 200 and receipt['checks']['reachable-attachment-content'] == 'passed')
        admin(self.command, config, '--maintenance-once', path / 'reconcile')
        self.evidence.check('reconciled-reference-keeps-content', (Path(config['blobDirectory']) / 'blobs' / digest).read_bytes() == PAYLOAD)

    def gc_crash(self, path):
        config, sql = self.setup(path)
        require(self.create(config, path / 'parent', 'gc-parent')['status'] == 201, 'GC parent must commit')
        admin(self.command, dict(config, caseKey='gc-attachment'), '--attachment-case', path / 'attachment')
        retained_hash = hashlib.sha256(PAYLOAD).hexdigest()
        blobs = Path(config['blobDirectory']) / 'blobs'; orphans = []
        for index in range(8):
            payload = ('independent-old-orphan-' + str(index)).encode(); blob = blobs / hashlib.sha256(payload).hexdigest()
            with blob.open('wb') as stream: stream.write(payload); stream.flush(); os.fsync(stream.fileno())
            os.utime(blob, (time.time() - 120, time.time() - 120)); orphans.append(blob)
        os.utime(blobs / retained_hash, (time.time() - 120, time.time() - 120))
        command, arm, audit, _ = self.preload(path, 'after-unlink', str(blobs) + '/')
        arm.write_text('hold after eligible orphan unlink\n')
        process = OneShot(command, config, '--maintenance-once', path / 'crashed-collector')
        try:
            eventually(lambda: any(x['event'] == 'completed-filesystem-call-held' for x in events(audit)), 'actual successful orphan unlink')
            remaining = sum(p.exists() for p in orphans)
            self.evidence.check('crash-inside-actual-collection', 0 < remaining < len(orphans), remaining=remaining)
            process.crash()
        finally: process.close()
        self.evidence.check('reference-safe-across-collector-crash', (blobs / retained_hash).read_bytes() == PAYLOAD)
        admin(self.command, config, '--maintenance-once', path / 'restarted-collector')
        self.evidence.check('orphan-collection-resumes', not any(p.exists() for p in orphans))
        receipt = admin(self.command, config, '--read-attachment-case', path / 'reference-read')
        self.evidence.check('reachable-reference-after-gc', receipt['checks']['reachable-attachment-content'] == 'passed')
