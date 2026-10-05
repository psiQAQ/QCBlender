"""Qualify an exact ZIP using an explicit current-batch evidence index."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.package_identity import extension_filename, extension_manifest, file_record, source_identity


def validate_archive(candidate, installed_dir, root=ROOT):
    root, installed_dir = Path(root), Path(installed_dir)
    lock = json.loads((root / 'dependencies.lock.json').read_text(encoding='utf-8'))
    backend = json.loads((root / 'outputs/backend-wheel.json').read_text(encoding='utf-8'))
    packages = lock['packages'] + [backend]
    with zipfile.ZipFile(candidate) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Candidate ZIP contains duplicate members')
        source_members = {path.relative_to(root / 'qcblender').as_posix()
                          for path in (root / 'qcblender').rglob('*')
                          if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'}
        expected_members = source_members | {'LICENSE', 'THIRD_PARTY.md', 'science-sources.lock.json',
            'dependencies.lock.json', 'backend-wheel.json', 'assets/nodes.blend', 'assets/blender_assets.cats.txt'}
        expected_members |= {'wheels/' + package['filename'] for package in packages}
        if {name for name in names if not name.endswith('/')} != expected_members:
            raise ValueError('Candidate ZIP contains missing or unexpected members')
        for name in names:
            target = (installed_dir / name).resolve()
            if not target.is_relative_to(installed_dir.resolve()) or name.startswith(('/', '\\')) or '\\' in name:
                raise ValueError('Unsafe candidate ZIP member')
            if not name.endswith('/') and target.read_bytes() != archive.read(name):
                raise ValueError('Installed file differs from candidate ZIP: ' + name)
        if archive.testzip() is not None:
            raise ValueError('Candidate ZIP CRC failed')
        expected_sources = set()
        for source in (root / 'qcblender').rglob('*.py'):
            ast.parse(source.read_bytes(), filename=str(source))
            relative = source.relative_to(root / 'qcblender')
            expected_sources.add(relative.as_posix())
            if archive.read(relative.as_posix()) != source.read_bytes():
                raise ValueError(f'Source differs from ZIP: {relative}')
            if (installed_dir / relative).read_bytes() != source.read_bytes():
                raise ValueError(f'Installed source differs from ZIP: {relative}')
        if {name for name in names if name.endswith('.py')} != expected_sources:
            raise ValueError('Candidate Python membership differs from source')
        expected_manifest = extension_manifest(root)
        expected_manifest['wheels'] = ['./wheels/' + p['filename'] for p in packages]
        for actual in (tomllib.loads(archive.read('blender_manifest.toml').decode('utf-8')),
                       tomllib.loads((installed_dir / 'blender_manifest.toml').read_text(encoding='utf-8'))):
            if actual != expected_manifest:
                raise ValueError('Candidate or installed manifest differs from source and locked wheels')
        if {name for name in names if name.endswith('.whl')} != {'wheels/' + p['filename'] for p in packages}:
            raise ValueError('Candidate wheel membership differs from locks')
        for package in packages:
            raw = archive.read('wheels/' + package['filename'])
            if hashlib.sha256(raw).hexdigest() != package['sha256']:
                raise ValueError('Candidate wheel checksum mismatch: ' + package['filename'])
        with zipfile.ZipFile(io.BytesIO(archive.read('wheels/' + backend['filename']))) as wheel:
            if any(name.endswith(('.pyd', '.dll', '.so', '/libcint.py')) for name in wheel.namelist()):
                raise ValueError('GBasis contains excluded native code')
            if 'gbasis/QCBLENDER_BUILD.md' not in wheel.namelist():
                raise ValueError('GBasis build notice missing')
        for relative in ('LICENSE', 'THIRD_PARTY.md', 'science-sources.lock.json', 'dependencies.lock.json'):
            if archive.read(relative) != (root / relative).read_bytes():
                raise ValueError('Candidate license or lock differs from source: ' + relative)
        if json.loads(archive.read('backend-wheel.json')) != backend:
            raise ValueError('Candidate backend record differs from this build')
    return backend


def validate_evidence(index_path, candidate_sha256, source_commit):
    index_path = Path(index_path)
    index = json.loads(index_path.read_text(encoding='utf-8'))
    if index.get('candidate_sha256') != candidate_sha256 or index.get('source_commit') != source_commit:
        raise ValueError('Evidence belongs to a different candidate or source commit')
    if not index.get('checks'):
        raise ValueError('No current-batch checks recorded')
    evidence = {}
    for name, entry in index['checks'].items():
        if entry.get('candidate_sha256') != candidate_sha256:
            raise ValueError(name + ': stale candidate')
        path = (index_path.parent / entry['path']).resolve(strict=True)
        if not path.is_relative_to(index_path.parent.resolve()):
            raise ValueError('Evidence must remain inside this batch')
        if file_record(path)['sha256'] != entry['sha256']:
            raise ValueError(name + ': changed evidence')
        report = json.loads(path.read_text(encoding='utf-8'))
        if report.get('status') != 'Passed':
            raise ValueError(name + ': check did not pass')
        if report.get('source_commit') not in (None, source_commit):
            raise ValueError(name + ': stale source commit')
        evidence[name] = dict(sha256=entry['sha256'], report=report)
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, default=ROOT / 'outputs/dist' / extension_filename())
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/qualification.json')
    parser.add_argument('--evidence-index', type=Path, required=True)
    parser.add_argument('--installed-dir', type=Path, required=True)
    args = parser.parse_args()
    commit, tree = source_identity()
    record = file_record(args.candidate.resolve())
    backend = validate_archive(args.candidate, args.installed_dir)
    evidence = validate_evidence(args.evidence_index, record['sha256'], commit)
    report = dict(status='Passed', scope='Current-batch automated technical qualification',
                  source_commit=commit, product_tree=tree, version=extension_manifest()['version'],
                  evidence_index=str(args.evidence_index), installed_matches_archive='Passed',
                  archive=str(args.candidate.resolve()), bytes=record['bytes'], sha256=record['sha256'],
                  backend=backend, source_matches_archive='Passed', wheel_checksums='Passed',
                  excluded_native_gbasis='Passed', evidence=evidence,
                  independent_user_acceptance='Not Run')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (args.candidate.parent / (args.candidate.name + '.sha256')).write_text(
        record['sha256'] + '  ' + args.candidate.name + '\n', encoding='ascii')
    print(json.dumps({key: value for key, value in report.items() if key != 'evidence'}, indent=2))


if __name__ == '__main__':
    main()
