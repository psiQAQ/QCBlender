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
    site = root / 'modules/build-site'
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


def verify_canonical_wheels(root):
    root = Path(root).resolve()
    lock = json.loads((root / 'dependencies.lock.json').read_text(encoding='utf-8'))
    backend = json.loads((root / 'modules/backend-wheel.json').read_text(encoding='utf-8'))
    records = []
    for package in lock['packages'] + [backend]:
        filename = package['filename']
        if Path(filename).name != filename or ':' in filename or '\\' in filename:
            raise ValueError('Expected a wheel filename: ' + filename)
        path = root / 'modules/wheels' / filename
        if any(component.is_symlink() or component.is_junction() for component in (path, *path.parents) if component != root and component.is_relative_to(root)):
            raise ValueError('Linked canonical wheel path: ' + str(path))
        if not path.is_file():
            raise FileNotFoundError('Required canonical wheel missing: ' + str(path))
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != package['sha256']:
            raise ValueError(f'Canonical wheel checksum mismatch: {path}; expected {package["sha256"]}, actual {actual}. '
                             'Verify and migrate the qualified same-version content before retiring its source copy.')
        records.append({'path': path.relative_to(root).as_posix(), 'name': package['name'],
                        'version': package['version'], 'bytes': path.stat().st_size,
                        'expected_sha256': package['sha256'], 'actual_sha256': actual, 'status': 'Passed'})
    return records


def plan(root):
    root = Path(root).resolve()
    wheels = verify_canonical_wheels(root)
    requirements, keep, retired, errors = build_file_sets(root)
    source_paths = ['modules/sources/gbasis/gbasis-071969c900d6d7a9fbbdfe193c65ba3be177fbdf.zip',
                    'modules/sources/iodata/iodata.zip',
                    'modules/sources/qcint/qcint-48f138c28bb72cf7b4350224152e407fe9e88b39.zip']
    license_root = root / 'modules/licenses'
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
    return {'schema': 'qcblender.outputs-runtime-plan.v1', 'root': str(root),
            'canonical_wheels_status': 'Passed', 'canonical_wheels': wheels,
            'build_requirements': requirements, 'build_keep_files': keep, 'build_retire_files': retired,
            'protected_paths': ['modules/build-site', 'modules/science', 'modules/wheels', 'modules/backend-wheel.json',
                                'modules/licenses', 'modules/sources', '.local/blender/runtime.json'] + [row['path'] for row in wheels] + source_paths,
            'source_originals': sources,
            'retired_task_roots': ['build-python', 'wheels/qualified', 'repaired-wheels', 'unrepaired-wheels',
                                   'gbasis-build', 'build-sources/gbasis-071969c900d6d7a9fbbdfe193c65ba3be177fbdf',
                                   'build-sources/qcint-48f138c28bb72cf7b4350224152e407fe9e88b39'],
            'conditions': ['build_keep_files/build_retire_files are relative to modules/build-site',
                           'Keep science in full; do not change package versions',
                           'Retirement requires a separate identity-checked deletion manifest',
                           'All root wheels must match the dependency lock and backend record before retiring qualified copies',
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
