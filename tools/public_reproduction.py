"""Verify the exact scene, Dataset, array and cache members of public reproduction data."""

import hashlib
import json
from pathlib import PurePosixPath
import re


def contained_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value or
            PurePosixPath(value).is_absolute() or any(part in ('', '.', '..') for part in value.split('/'))):
        raise ValueError('Public reproduction asset must use a contained relative path')
    return value


def reproduction_members(open_file, names, allowed_sources):
    def read_bytes(name):
        with open_file(name) as stream:
            return stream.read()

    expected = {'example.blend', 'example.png', 'README.md', 'example.qcdata/manifest.json'}
    if not expected <= set(names):
        raise ValueError('Public reproduction is incomplete')
    scene = json.loads(read_bytes('example.qcdata/manifest.json'))
    if scene.get('format') != 'qcblender.scene' or scene.get('schema') != '0.1':
        raise ValueError('Unsupported public scene manifest')
    datasets = scene.get('datasets')
    if not isinstance(datasets, list) or not datasets or len(set(datasets)) != len(datasets):
        raise ValueError('Public reproduction has no unique scientific Datasets')
    for relative in datasets:
        if re.fullmatch(r'datasets/[0-9a-f]{64}', contained_path(relative)) is None:
            raise ValueError('Invalid public Dataset path')
        prefix = 'example.qcdata/' + relative + '/'
        name = prefix + 'manifest.json'
        raw = read_bytes(name)
        if hashlib.sha256(raw).hexdigest() != relative.split('/')[-1]:
            raise ValueError('Public Dataset identity mismatch')
        dataset = json.loads(raw)
        if dataset.get('format') != 'qcblender.project' or dataset.get('schema') != '0.1':
            raise ValueError('Unsupported public Dataset manifest')
        if dataset.get('metadata', {}).get('source', {}).get('sha256') not in allowed_sources:
            raise ValueError('Public reproduction contains an unverified scientific input')
        expected.add(name)
        if not isinstance(dataset.get('arrays'), dict) or not dataset['arrays']:
            raise ValueError('Public Dataset has no arrays')
        for entry in dataset['arrays'].values():
            path = contained_path(entry['path'])
            digest = entry['sha256']
            if not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None or path != 'arrays/' + digest + '.npy':
                raise ValueError('Public array identity path mismatch')
            with open_file(prefix + path) as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                    raise ValueError('Public array content digest mismatch')
            expected.add(prefix + path)
        for field in dataset['metadata'].get('fields', []):
            path = contained_path(field.get('vdb', 'field.vdb'))
            if not path.endswith('.vdb'):
                raise ValueError('Unexpected public field cache path')
            if field.get('vdb_sha256'):
                with open_file(prefix + path) as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() != field['vdb_sha256']:
                        raise ValueError('Public field cache content digest mismatch')
            expected.add(prefix + path)
    if set(names) != expected:
        raise ValueError('Public reproduction contains missing or unlisted material')
    return expected
