"""Describe the retained runtime and obsolete build files without deleting them."""
import argparse
import csv
import hashlib
from importlib.metadata import distributions
import json
import os
from pathlib import Path


def ordinary_files(directory, errors):
    for folder, names, files in os.walk(directory, followlinks=False,
                                         onerror=lambda error: errors.append(str(error))):
        parent = Path(folder)
        for name in list(names):
            path = parent / name
            if path.is_symlink() or path.is_junction():
                errors.append('Excluded linked directory: ' + str(path))
                names.remove(name)
        for name in files:
            path = parent / name
            if path.is_symlink():
                errors.append('Excluded linked file: ' + str(path))
            else:
                yield path


def build_file_sets(root):
    root = Path(root).resolve()
    site = root / 'outputs/build-site'
    expected = dict(line.split('==') for line in (root / 'tools/build-requirements.txt').read_text(encoding='utf-8').splitlines() if line)
    normalize = lambda name: name.lower().replace('_', '-')
    expected = {normalize(name): value for name, value in expected.items()}
    installed = {normalize(dist.metadata['Name']): dist for dist in distributions(path=[str(site)])}
    retained = set()
    requirements = []
    for name, version in expected.items():
        dist = installed.get(name)
        if dist is None or dist.version != version:
            raise ValueError(f'Locked build tool is missing or changed: {name}=={version}')
        record = dist.read_text('RECORD')
        if record is None:
            raise ValueError('Missing build distribution RECORD: ' + name)
        for relative, _, _ in csv.reader(record.splitlines()):
            path = Path(os.path.abspath(site / relative))
            if not path.is_relative_to(site):
                raise ValueError(f'Build RECORD escapes build-site: {name}: {relative}')
            if any(component.is_symlink() or component.is_junction() for component in (path, *path.parents) if component.is_relative_to(site)):
                raise ValueError('Linked build file: ' + str(path))
            if path.is_file():
                retained.add(path.relative_to(site).as_posix())
        requirements.append({'name': name, 'version': version, 'requires_dist': dist.requires or []})
    if (site / '.lock').is_file():
        retained.add('.lock')
    errors = []
    existing = {path.relative_to(site).as_posix() for path in ordinary_files(site, errors)}
    return requirements, sorted(retained), sorted(existing - retained), errors


def plan(root):
    root = Path(root).resolve()
    requirements, keep, retired, errors = build_file_sets(root)
    source_paths = ['outputs/build-sources/gbasis-071969c900d6d7a9fbbdfe193c65ba3be177fbdf.zip',
                    'outputs/m0-research/iodata.zip',
                    'outputs/build-sources/qcint-48f138c28bb72cf7b4350224152e407fe9e88b39.zip']
    license_root = root / 'outputs/native-backend-licenses'
    source_paths += [path.relative_to(root).as_posix() for path in ordinary_files(license_root, errors)]
    sources = []
    source_urls = {
        source_paths[0]: 'https://codeload.github.com/theochem/gbasis/zip/071969c900d6d7a9fbbdfe193c65ba3be177fbdf',
        source_paths[1]: 'https://codeload.github.com/theochem/iodata/zip/adab5813713ba64641565eb2a8c11803a4e9bba6',
        source_paths[2]: 'https://codeload.github.com/sunqm/qcint/zip/48f138c28bb72cf7b4350224152e407fe9e88b39'}
    for relative in source_paths:
        path = root / relative
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        sources.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': digest,
                        'source_url': source_urls.get(relative),
                        'role': 'upstream source archive' if path.suffix == '.zip' else 'original license text',
                        'keep_reason': 'One complete original for offline reconstruction or historical source/license verification'})
    lock = json.loads((root / 'dependencies.lock.json').read_text(encoding='utf-8'))
    backend = json.loads((root / 'outputs/backend-wheel.json').read_text(encoding='utf-8'))
    wheels = ['outputs/wheels/' + row['filename'] for row in lock['packages'] + [backend]]
    return {'schema': 'qcblender.outputs-runtime-plan.v1', 'root': str(root),
            'build_requirements': requirements, 'build_keep_files': keep, 'build_retire_files': retired,
            'protected_paths': ['outputs/science', 'outputs/backend-wheel.json', 'outputs/blender-runtime.json'] + wheels + source_paths,
            'source_originals': sources,
            'retired_task_roots': ['build-python', 'wheels/qualified', 'repaired-wheels', 'unrepaired-wheels',
                                   'gbasis-build', 'build-sources/gbasis-071969c900d6d7a9fbbdfe193c65ba3be177fbdf',
                                   'build-sources/qcint-48f138c28bb72cf7b4350224152e407fe9e88b39'],
            'conditions': ['build_keep_files/build_retire_files are relative to outputs/build-site',
                           'Keep science in full; do not change package versions',
                           'Retirement requires a separate identity-checked deletion manifest',
                           'Linked and inaccessible paths remain excluded',
                           'Blender Python is supplied by the installed Blender 5.1.1'],
            'scan_errors': errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--report-dir', type=Path, required=True)
    args = parser.parse_args()
    result = plan(args.root)
    args.report_dir.mkdir(parents=True, exist_ok=False)
    (args.report_dir / 'runtime-plan.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'keep_files': len(result['build_keep_files']), 'retire_files': len(result['build_retire_files']),
                      'scan_errors': result['scan_errors']}))


if __name__ == '__main__':
    main()
