"""Release gates must reject stale/tampered candidates before obtaining credentials."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'eng'))
import release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.packages = self.root / 'packages'
        self.packages.mkdir()
        self.version = '0.1.0-preview.1'
        self.package = self.packages / f'NativeWeave.HelloWorld.{self.version}.nupkg'
        self.metadata = {
            'packageId': 'NativeWeave.HelloWorld', 'packageVersion': self.version,
            'rid': 'linux-x64', 'sourceDirty': False, 'sourceCommit': 'a' * 40,
            'nativePath': 'runtimes/linux-x64/native/libnativeweave_hello.so',
            'nativeSha256': hashlib.sha256(b'native fixture').hexdigest(),
        }
        self.write_candidate()
        self.artifacts_patch = patch.object(release, 'ARTIFACTS', self.root)
        self.artifacts_patch.start()
        self.addCleanup(self.artifacts_patch.stop)
        self.commit_patch = patch.object(release.subprocess, 'check_output', return_value='a' * 40 + '\n')
        self.commit_patch.start()
        self.addCleanup(self.commit_patch.stop)

    def write_candidate(self):
        with zipfile.ZipFile(self.package, 'w') as archive:
            archive.writestr('nativeweave/manifest.json', json.dumps(self.metadata))
            archive.writestr(self.metadata['nativePath'], b'native fixture')
        (self.packages / 'manifest.json').write_text(json.dumps(self.metadata))
        self.write_checksums()

    def write_checksums(self):
        (self.packages / 'SHA256SUMS').write_text(''.join(
            f'{release.digest(file)}  {file.name}\n'
            for file in [self.package, self.packages / 'manifest.json']))

    def test_clean_candidate_matches_commit_and_payload(self):
        self.assertEqual(self.package, release.validate_candidate(self.version))

    def test_archive_tamper_fails(self):
        self.package.write_bytes(self.package.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            release.validate_candidate(self.version)

    def test_dirty_or_wrong_commit_is_not_releasable(self):
        for field, value in [('sourceDirty', True), ('sourceCommit', 'b' * 40)]:
            with self.subTest(field=field):
                old = self.metadata[field]
                self.metadata[field] = value
                self.write_candidate()
                with self.assertRaisesRegex(ValueError, 'clean candidate'):
                    release.validate_candidate(self.version)
                self.metadata[field] = old

    def test_wrong_rid_or_embedded_native_hash_fails(self):
        self.metadata['rid'] = 'osx-arm64'
        self.write_candidate()
        with self.assertRaisesRegex(ValueError, 'platform'):
            release.validate_candidate(self.version)
        self.metadata['rid'] = 'linux-x64'
        self.metadata['nativeSha256'] = '0' * 64
        self.write_candidate()
        with self.assertRaisesRegex(ValueError, 'Native payload'):
            release.validate_candidate(self.version)

    def test_checksum_paths_are_not_arbitrary_files(self):
        with (self.packages / 'SHA256SUMS').open('a') as stream:
            stream.write('0' * 64 + '  ../outside\n')
        with self.assertRaisesRegex(ValueError, 'checksum entry'):
            release.validate_candidate(self.version)

    def test_versions_are_canonical(self):
        for version in ['0.1.0-preview.1', '1.2.3']:
            self.assertEqual(version, release.validate_version(version))
        for version in ['v1.2.3', '1.2', '1.2.3+metadata', '1.2.3\nversion=evil', '1.2.3-01', '../outside']:
            with self.subTest(version=version), self.assertRaises(ValueError):
                release.validate_version(version)

    def test_registry_payload_comparison_ignores_only_signature(self):
        downloaded = self.root / 'registry.nupkg'
        with zipfile.ZipFile(downloaded, 'w') as archive, zipfile.ZipFile(self.package) as original:
            for name in original.namelist():
                archive.writestr(name, original.read(name))
            archive.writestr('.signature.p7s', b'signature fixture, verified separately in publication')
        self.assertEqual(release.entries(self.package), release.entries(downloaded))
        with zipfile.ZipFile(downloaded, 'a') as archive:
            archive.writestr('unexpected.txt', b'not allowed')
        self.assertNotEqual(release.entries(self.package), release.entries(downloaded))
