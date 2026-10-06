"""Resolve current validation inputs while retaining their recorded identities."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
DATA = 'validation/shared/data'
CATALOG = DATA + '/local-inputs.json'
GUIDE = DATA + '/README.md'


def checked_path(root, relative):
    """Reject traversal and linked paths before reading or copying data."""
    root = Path(root).resolve()
    if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative
            or PureWindowsPath(relative).drive or PurePosixPath(relative).is_absolute()
            or any(part in ('', '.', '..') for part in relative.split('/'))):
        raise ValueError(f'Expected a relative data path: {relative}')
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError(f'Data path escapes its root: {relative}')
    for component in (path, *path.parents):
        if component == root:
            break
        if component.is_symlink() or component.is_junction():
            raise ValueError(f'Linked data path is not allowed: {relative}')
    return path


def verify_file(path, record):
    if not path.is_file():
        raise FileNotFoundError(f'Required validation input missing: {path}; see {GUIDE}')
    if 'bytes' in record and path.stat().st_size != record['bytes']:
        raise ValueError(f'Validation input size mismatch: {path}')
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != record['sha256']:
        raise ValueError(f'Validation input checksum mismatch: {path}')
    return path


def public_input_path(record, root=ROOT):
    """The frozen archive path is the public input's current relative location."""
    if record['distribution'] != 'included' or record['license'] != 'CC-BY-4.0':
        raise ValueError('Input is not in the public tutorial allowlist')
    base = Path(root).resolve() / DATA / 'public'
    path = checked_path(base, record['archive_path'])
    checked_path(root, path.relative_to(Path(root).resolve()).as_posix())
    return verify_file(path, record)


def input_path(key, root=None):
    root = Path(root or os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)).resolve()
    # Keys are stable identities, not paths to concatenate onto a directory.
    checked_path(root, key)
    files = json.loads(checked_path(root, CATALOG).read_text(encoding='utf-8'))['files']
    matches = [(name, entry) for name, entry in files.items()
               if name == key or name.startswith(key + '/')]
    if not matches:
        raise KeyError(f'Unknown local input: {key}; see {GUIDE}')
    resolved = {}
    for name, entry in matches:
        path = checked_path(root, entry['path'])
        if not any(path.is_relative_to(root / DATA / kind) for kind in ('local', 'public')):
            raise ValueError(f'Input escapes validation data directories: {key}')
        resolved[name] = verify_file(path, entry)
    if key in resolved:
        return resolved[key]
    directories = set()
    for name, path in resolved.items():
        suffix = PurePosixPath(name).relative_to(key).parts
        if path.parts[-len(suffix):] != suffix:
            raise ValueError(f'Input directory key has inconsistent relative paths: {key}')
        for _ in suffix:
            path = path.parent
        directories.add(path)
    if len(directories) != 1:
        raise ValueError(f'Input directory key maps to multiple locations: {key}')
    directory = directories.pop()
    if not any(directory.is_relative_to(root / DATA / kind) for kind in ('local', 'public')):
        raise ValueError(f'Input directory key escapes validation data directories: {key}')
    return directory

if __name__ == '__main__':
    reference = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)).resolve()
    files = json.loads((reference / CATALOG).read_text(encoding='utf-8'))['files']
    for name in files:
        input_path(name, reference)
    print(f'LOCAL_INPUTS_PASSED: {len(files)} files')
