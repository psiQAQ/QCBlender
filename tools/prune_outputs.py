"""Inventory approved output categories, then delete only unchanged manifest entries.

Run --plan first, inspect outputs/storage-cleanup/inventory.jsonl.gz and summary.json,
then --apply. Symlinks, junctions and inaccessible paths are never followed.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
from itertools import batched
import json
import os
from pathlib import Path
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / 'outputs'
REPORTS = OUTPUTS / 'storage-cleanup'
ENVIRONMENTS = {'build-python', 'build-site', 'build-sources', 'reference-tools',
                'science', 'wheels', 'repaired-wheels', 'unrepaired-wheels',
                'gbasis-build', 'native-backend-licenses', 'm0-research'}
TEXT = {'.log', '.txt', '.md', '.json', '.jsonl', '.csv', '.py', '.ps1', '.bat', '.html', '.xml'}
GENERATED = {'acceptance', 'analysis-gui', 'animation-acceptance', 'animation-acceptance-v2',
             'atom-visibility', 'committed-build-d1abfe8', 'complex-examples', 'composable',
             'diagnostics', 'dist', 'external-results', 'external-worker', 'fog-acceptance',
             'irc-acceptance', 'layer-acceptance', 'localized-materials', 'log-fixtures',
             'molecularnodes-parameters', 'multiwfn-parameters', 'nbo-acceptance', 'nocv-acceptance',
             'node-assets', 'optimization-trajectory', 'paired-fields', 'result-browser', 'scalar-probe',
             'source-adoption', 'storage-cleanup', 'v1-acceptance', 'vesta-comparison',
             'visual-acceptance', 'visual-acceptance-v2', 'vmd-parameters', 'volume-probe'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def files(directory, skipped):
    try:
        with os.scandir(directory) as scan:
            entries = sorted(scan, key=lambda entry: entry.name)
    except OSError as error:
        skipped.append({'path': str(directory), 'reason': str(error)})
        return
    for entry in entries:
        try:
            info = entry.stat(follow_symlinks=False)
            if entry.is_symlink() or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                skipped.append({'path': entry.path, 'reason': 'link or junction'})
            elif entry.is_dir(follow_symlinks=False):
                yield from files(Path(entry.path), skipped)
            elif entry.is_file(follow_symlinks=False):
                yield Path(entry.path), info
        except OSError as error:
            skipped.append({'path': entry.path, 'reason': str(error)})


def classify(path, migrated):
    rel = path.relative_to(OUTPUTS)
    parts = rel.parts
    if parts[0] in ('recovery', 'branch-archive'):
        return 'keep', 'preserved project or cleanup evidence'
    if path.name == 'stale-pending' or any(part.startswith('.~stale~') for part in parts):
        return 'keep', 'deferred installation cache managed by Blender startup'
    if '__pycache__' in parts:
        return 'delete', 'regenerable Python bytecode'
    if path.suffix.startswith('.blend') and (any(p in ('temp', 'process-temp') for p in parts)
                                            or 'autosave' in path.name or path.name == 'quit.blend'):
        return 'keep', 'recovery file ownership not independently established'
    if 'uv-cache' in parts or parts[0] == 'process-temp':
        return 'delete', 'download or ended-session temporary cache'
    if path.relative_to(ROOT).as_posix() in migrated:
        return 'delete', 'hash-verified migrated input'
    if parts[:2] == ('v1-acceptance', 'sources') or parts[0] == 'visualization-adoption':
        return 'keep', 'reference material or generation provenance'
    runtime = 'jobs' in parts and ('extensions' in parts or '.user' in parts)
    if runtime:
        if path.suffix in TEXT and not any(p in ('dataset', 'datasets', 'cache') for p in parts):
            return 'keep', 'worker request or diagnostic log'
        return 'delete', 'unreferenced worker data or field cache'
    if any(parts[i:i+2] == ('datafiles', 'qcblender') for i in range(len(parts) - 1)):
        return 'delete', 'unreferenced analysis runtime dataset'
    if any(p in ENVIRONMENTS or p in ('extensions', 'config', 'scripts', 'datafiles') for p in parts):
        return 'keep', 'software environment or configuration'
    if parts[0] not in GENERATED:
        return 'keep', 'unclassified output purpose; retained for review'
    if any(p.endswith('.qcdata') for p in parts):
        return 'delete', 'historical portable dataset'
    if path.suffix in ('.blend', '.blend1', '.blend2', '.png', '.jpg', '.jpeg', '.exr', '.mp4', '.avi'):
        return 'delete', 'historical generated scene or visual evidence'
    if path.suffix == '.zip':
        return 'delete', 'historical candidate or generated archive'
    if path.suffix in ('.npy', '.npz', '.vdb'):
        return 'delete', 'generated scientific dataset or display cache'
    if path.suffix == '.whl':
        canonical = OUTPUTS / 'wheels' / path.name
        if canonical.is_file() and digest(canonical) == digest(path):
            return 'delete', 'duplicate of retained shared wheel'
    if path.suffix in TEXT or path.name.lower().startswith(('license', 'copying')):
        return 'keep', 'log, report, generation script or provenance'
    return 'keep', 'unclassified; retained for review'


def plan():
    REPORTS.mkdir(exist_ok=True)
    index = json.loads((ROOT / 'tests/data/local-inputs.json').read_text(encoding='utf-8'))['files']
    migrated = {record['original_path']: record for record in index.values()}
    for old, record in migrated.items():
        target = ROOT / record['path']
        assert digest(target) == record['sha256'], target
        if (ROOT / old).is_file():
            assert digest(ROOT / old) == record['sha256'], old
    tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines())
    summary = defaultdict(lambda: {'files': 0, 'bytes': 0})
    skipped = []

    def record(item):
        path, info = item
        action, reason = classify(path, migrated)
        if path.relative_to(ROOT).as_posix() in tracked:
            action, reason = 'keep', 'Git tracked file'
        row = dict(path=str(path), action=action, reason=reason, bytes=info.st_size,
                   mtime_ns=info.st_mtime_ns)
        if reason in ('software environment or configuration', 'preserved project or cleanup evidence'):
            try:
                row['sha256'] = digest(path)
            except OSError as error:
                skipped.append(dict(path=str(path), reason=str(error)))
        return row

    with gzip.open(REPORTS / 'inventory.jsonl.gz', 'wt', encoding='utf-8') as stream, ThreadPoolExecutor(max_workers=8) as pool:
        entries = (item for item in files(OUTPUTS, skipped) if item[0] != REPORTS / 'inventory.jsonl.gz')
        for batch in batched(entries, 512):
            for row in pool.map(record, batch):
                key = row['action'] + ': ' + row['reason']
                summary[key]['files'] += 1
                summary[key]['bytes'] += row['bytes']
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    result = {'categories': dict(summary), 'skipped': skipped, 'status': 'Planned'}
    (REPORTS / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result['categories'], ensure_ascii=False, indent=2))


def apply():
    # Every target is a manifest file, under this repository, with unchanged stat data.
    failures, removed, protected = [], {'files': 0, 'bytes': 0}, 0
    def verify(row):
        if row['action'] == 'keep' and 'sha256' in row:
            try:
                if digest(Path(row['path'])) != row['sha256']:
                    return 'protected file changed'
            except OSError as error:
                return str(error)
        return None

    with gzip.open(REPORTS / 'inventory.jsonl.gz', 'rt', encoding='utf-8') as stream, ThreadPoolExecutor(max_workers=8) as pool:
        rows = (json.loads(line) for line in stream)
        for batch in batched(rows, 512):
            for row, error in zip(batch, pool.map(verify, batch)):
                path = Path(row['path'])
                try:
                    if error:
                        raise OSError(error)
                    if row['action'] == 'keep':
                        if 'sha256' in row:
                            protected += 1
                        continue
                    resolved = path.resolve()
                    assert path.is_absolute() and resolved.is_relative_to(OUTPUTS.resolve()), 'outside outputs'
                    assert resolved == path, 'aliased path through a link or junction'
                    assert not path.is_relative_to(OUTPUTS / 'recovery')
                    info = path.stat(follow_symlinks=False)
                    assert not getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT, 'link or junction'
                    assert info.st_size == row['bytes'] and info.st_mtime_ns == row['mtime_ns'], 'file changed after inventory'
                    path.unlink()
                    removed['files'] += 1
                    removed['bytes'] += row['bytes']
                except (OSError, AssertionError) as error:
                    failures.append({'path': str(path), 'reason': str(error)})
    report = {'removed': removed, 'protected_hashes_verified': protected, 'skipped': failures}
    (REPORTS / 'applied.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--report-dir', type=Path, default=REPORTS,
                        help='Task record directory inside outputs; retain each completed inventory')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--plan', action='store_true')
    modes.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    REPORTS = args.report_dir.resolve()
    if not REPORTS.is_relative_to(OUTPUTS.resolve()) or REPORTS.is_symlink() or REPORTS.is_junction():
        parser.error('--report-dir must be an ordinary directory within outputs')
    if args.plan and (REPORTS / 'applied.json').exists():
        parser.error('This inventory has already been applied; choose a new --report-dir')
    if args.apply and (REPORTS / 'applied.json').exists():
        parser.error('This inventory has already been applied; preserve it and create a new plan')
    plan() if args.plan else apply()
