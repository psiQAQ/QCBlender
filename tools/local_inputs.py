"""Resolve and verify the local-only SOP and regression input catalog."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def input_path(key, root=None):
    root = Path(root or os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)).resolve()
    files = json.loads((root / 'tests/data/local-inputs.json').read_text(encoding='utf-8'))['files']
    matches = [entry for name, entry in files.items() if name == key or name.startswith(key.rstrip('/') + '/')]
    if not matches:
        raise KeyError(f'Unknown local input: {key}; see docs/v1-acceptance/SOURCES.md')
    for entry in matches:
        path = root / entry['path']
        if not path.resolve().is_relative_to(root / 'tests/data/local'):
            raise ValueError(f'Input escapes local data directory: {key}')
        if not path.is_file():
            raise FileNotFoundError(f'Required local input missing: {path}; see docs/v1-acceptance/SOURCES.md')
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != entry['sha256']:
            raise ValueError(f'Local input checksum mismatch: {path}')
    return root / 'tests/data/local' / key

if __name__ == '__main__':
    files = json.loads((ROOT / 'tests/data/local-inputs.json').read_text(encoding='utf-8'))['files']
    for name in files:
        input_path(name)
    print(f'LOCAL_INPUTS_PASSED: {len(files)} files')
