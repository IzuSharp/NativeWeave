#!/usr/bin/env python3
"""Package identity helpers and the finite database reference JIT/Native AOT matrix."""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE_NAMES = ('libnw_database_sqlite.so', 'libnw_database_postgresql.so')
DIRECT_PACKAGES = {'NativeWeave.Database.Sqlite', 'NativeWeave.Database.PostgreSql'}
RETAINED_PACKAGES = {
    'NativeWeave.Interop.Abi', 'NativeWeave.Core', 'NativeWeave.Data',
    'NativeWeave.Database.Transactions', 'NativeWeave.Data.Streaming',
    'NativeWeave.Query.Binding', 'NativeWeave.Query.Generator', 'NativeWeave.Database',
    'NativeWeave.Database.Sqlite', 'NativeWeave.Database.PostgreSql',
    'NativeWeave.Database.Sqlite.Native', 'NativeWeave.Database.PostgreSql.Native'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def inventory(directory):
    directory = Path(directory)
    return {str(path.relative_to(directory)): sha(path) for path in sorted(directory.rglob('*'))
            if path.is_file() and not {'bin', 'obj', '__pycache__'}.intersection(path.relative_to(directory).parts)}


def git_identity(directory):
    def read(*arguments):
        result = subprocess.run(['git', '-C', str(directory), *arguments], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {'root': read('rev-parse', '--show-toplevel'), 'commit': read('rev-parse', 'HEAD'),
            'scope_status': read('status', '--porcelain', '--', str(directory))}


def package_inputs(feed, version):
    """Freeze every package in this candidate feed, including independently versioned shared packages."""
    result, native = {}, {}
    for path in sorted(Path(feed).glob('*.nupkg')):
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith('.nuspec')]
            if len(names) != 1: raise ValueError('Expected exactly one nuspec in ' + path.name)
            spec = ET.fromstring(archive.read(names[0]))
            identity = spec.findtext('.//{*}metadata/{*}id')
            selected_version = spec.findtext('.//{*}metadata/{*}version')
            if not identity or not identity.startswith('NativeWeave.'): continue
            if identity not in RETAINED_PACKAGES: raise ValueError('Removed package entered candidate feed: ' + identity)
            if identity in result: raise ValueError('Duplicate candidate package identity: ' + identity)
            dependencies = [{'id': node.attrib['id'], 'version': node.attrib['version']}
                            for node in spec.findall('.//{*}dependency')]
            if any(row['id'].startswith('NativeWeave.') and row['id'] not in RETAINED_PACKAGES for row in dependencies):
                raise ValueError('Removed package dependency: ' + identity)
            repository = spec.find('.//{*}repository')
            result[identity] = {'filename': path.name, 'version': selected_version, 'sha256': sha(path),
                'bytes': path.stat().st_size, 'dependencies': dependencies,
                'repository': dict(repository.attrib) if repository is not None else {}}
            for name in archive.namelist():
                basename = Path(name).name
                if '/native/' in name and basename.endswith('.so'):
                    if basename not in NATIVE_NAMES: raise ValueError('Unexpected native library in database feed: ' + name)
                    digest = hashlib.sha256(archive.read(name)).hexdigest()
                    if basename in native and native[basename] != digest: raise ValueError('Conflicting native bytes: ' + basename)
                    native[basename] = digest
    if set(result) != RETAINED_PACKAGES or set(native) != set(NATIVE_NAMES):
        raise ValueError('The complete database package/native closure is required.')
    if any(result[name]['version'] != version for name in DIRECT_PACKAGES):
        raise ValueError('Provider facade versions differ from --version.')
    return result, native


if __name__ == '__main__':
    import importlib.util
    spec = importlib.util.spec_from_file_location('database_package_matrix', ROOT / 'tests/Verification.EndToEnd/api_probe.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    raise SystemExit(module.main(fixture='reference'))
