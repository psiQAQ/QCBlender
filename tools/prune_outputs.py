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
POLICY = None
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


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def safe_path(path, root):
    path = Path(path)
    require(path.is_absolute() and path.is_relative_to(root), 'outside approved root')
    require(path.resolve() == path, 'aliased path through a link or junction')
    for ancestor in (path, *path.parents):
        require(not ancestor.is_symlink() and not ancestor.is_junction(), 'link or junction')
        if ancestor == root:
            break
    return path


def safe_output_path(path):
    require(Path(path).is_absolute() and Path(path).is_relative_to(OUTPUTS), 'outside outputs')
    return safe_path(path, OUTPUTS)


def safe_report_path(path):
    path = Path(path).absolute()
    allowed = (OUTPUTS, ROOT / 'validation/agent/reports')
    require(any(path != root and path.is_relative_to(root) for root in allowed),
            '--report-dir must be a subdirectory of outputs or validation/agent/reports')
    return safe_path(path, ROOT)


def load_policy(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    groups = {'protected_paths', 'retired_task_roots', 'retired_profiles', 'migrated_files',
              'retired_files', 'retained_references'}
    if not isinstance(data, dict) or set(data) - groups:
        raise ValueError('Unknown cleanup policy fields')
    result = {}
    for group in groups:
        values = data.get(group, [])
        if not isinstance(values, list):
            raise ValueError('Policy paths must be lists')
        result[group] = []
        for value in values:
            if not isinstance(value, str):
                raise ValueError('Policy path must be a string')
            relative = Path(value)
            if relative.is_absolute() or not relative.parts or '..' in relative.parts or ':' in value:
                raise ValueError('Policy paths must be relative descendants of outputs')
            target = OUTPUTS / relative
            safe_output_path(target)
            if target == OUTPUTS:
                raise ValueError('Policy cannot retire all outputs')
            if group in ('retired_files', 'retained_references', 'migrated_files') and target.is_dir():
                raise ValueError('Exact file policy cannot name a directory')
            result[group].append(target)
    shared = [OUTPUTS / name for name in ('build-site', 'science', 'wheels', 'backend-wheel.json', 'blender-runtime.json', 'evidence', 'projects', 'candidates')]
    for target in result['retired_profiles'] + result['retired_task_roots']:
        if any(target == protected or protected.is_relative_to(target) for protected in shared):
            raise ValueError('Cannot retire shared environments or canonical retained roots')
    result = {group: set(paths) for group, paths in result.items()}
    return result


def covered(path, roots):
    return any(parent in roots for parent in (path, *path.parents))


def tracked_paths():
    return set(subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines())


def anonymous_object(path):
    return any(part in ('objects', 'anonymousobjects', 'content') or part.endswith('-objects')
               for part in path.relative_to(OUTPUTS).parts)


def authorize_delete(path, tracked):
    require(not path.is_relative_to(OUTPUTS / 'recovery'), 'protected recovery project')
    require(not path.is_relative_to(REPORTS), 'current cleanup report')
    if POLICY is not None or anonymous_object(path):
        require(classify(path, {})[0] == 'delete', 'policy no longer authorizes deletion')
    require(path.relative_to(ROOT).as_posix() not in tracked, 'Git tracked file')


def verify_entry(row, tracked=None):
    path = safe_output_path(row['path'])
    info = path.stat(follow_symlinks=False)
    require(info.st_size == row['bytes'] and info.st_mtime_ns == row['mtime_ns'], 'file changed after inventory')
    require(bool(row.get('sha256')), 'missing SHA-256 in inventory')
    require(digest(path) == row['sha256'], 'content changed after inventory')
    if row['action'] == 'delete':
        tracked = tracked_paths() if tracked is None else tracked
        authorize_delete(path, tracked)
    return path


def classify(path, migrated):
    rel = path.relative_to(OUTPUTS)
    parts = rel.parts
    if path.is_relative_to(REPORTS):
        return 'keep', 'current cleanup report'
    if parts[0] == 'recovery':
        return 'keep', 'preserved project or cleanup evidence'
    if POLICY is not None:
        if covered(path, POLICY['protected_paths']) or path in POLICY.get('retained_references', []):
            return 'keep', 'explicit protected path or shared retained root'
    anonymous = anonymous_object(path)
    if anonymous and (POLICY is None or path not in POLICY.get('retired_files', [])):
        return 'keep', 'anonymous preservation object requires exact retirement'
    if POLICY is not None:
        if path in POLICY.get('retired_files', []):
            return 'delete', 'reviewed exact file retirement'
        if parts[0] in ('build-site', 'science', 'wheels', 'backend-wheel.json', 'blender-runtime.json', 'evidence', 'projects', 'candidates'):
            return 'keep', 'explicit protected path or shared retained root'
        if path in POLICY.get('migrated_files', []):
            return 'delete', 'hash-verified migrated evidence or input'
        if covered(path, POLICY['retired_profiles']):
            return 'delete', 'verified ended-session isolated environment'
        if not covered(path, POLICY['retired_task_roots']):
            return 'keep', 'outside reviewed retired tasks'
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
    if parts[0] not in GENERATED and POLICY is None:
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
        try:
            if canonical.is_file() and digest(canonical) == digest(path):
                return 'delete', 'duplicate of retained shared wheel'
        except OSError:
            return 'keep', 'wheel identity inaccessible; retained for review'
    if path.suffix in TEXT or path.name.lower().startswith(('license', 'copying')):
        return 'keep', 'log, report, generation script or provenance'
    return 'keep', 'unclassified; retained for review'


def protection_required(path, reason):
    if POLICY is not None:
        return (covered(path, POLICY['protected_paths']) or path in POLICY.get('retained_references', [])
                or reason == 'Git tracked file')
    return reason in ('Git tracked file', 'software environment or configuration')


def policy_record():
    return {key: sorted(str(path) for path in paths) for key, paths in POLICY.items()} if POLICY is not None else None


def plan():
    safe_report_path(REPORTS)
    require(not any((REPORTS / name).exists() for name in ('inventory.jsonl.gz', 'summary.json', 'applied.json', 'removed.jsonl.gz')),
            'Report already exists; choose a new --report-dir')
    input_index = safe_path(ROOT / 'validation/shared/data/local-inputs.json', ROOT)
    index = json.loads(input_index.read_text(encoding='utf-8'))['files']
    migrated = {record['original_path']: record for record in index.values() if record.get('original_path')}
    protected_inputs = []
    for record in index.values():
        target = safe_path(ROOT / record['path'], ROOT)
        info = target.stat(follow_symlinks=False)
        require(digest(target) == record['sha256'], str(target))
        protected_inputs.append({'path': str(target), 'bytes': info.st_size,
                                 'mtime_ns': info.st_mtime_ns, 'sha256': record['sha256']})
        old = record.get('original_path')
        if old and (ROOT / old).is_file():
            require(digest(ROOT / old) == record['sha256'], old)
    info = input_index.stat(follow_symlinks=False)
    protected_inputs.append({'path': str(input_index), 'bytes': info.st_size,
                             'mtime_ns': info.st_mtime_ns, 'sha256': digest(input_index)})
    tracked = tracked_paths()
    REPORTS.mkdir(parents=True, exist_ok=True)
    summary = defaultdict(lambda: {'files': 0, 'bytes': 0})
    skipped = []

    def record(item):
        path, info = item
        action, reason = classify(path, migrated)
        if path.relative_to(ROOT).as_posix() in tracked:
            action, reason = 'keep', 'Git tracked file'
        row = dict(path=str(path), action=action, reason=reason, bytes=info.st_size,
                   mtime_ns=info.st_mtime_ns)
        if action == 'keep' and protection_required(path, reason):
            row['verification_required'] = True
        if action == 'delete' or row.get('verification_required'):
            try:
                row['sha256'] = digest(path)
            except OSError as error:
                skipped.append(dict(path=str(path), reason=str(error)))
                row['action'], row['reason'] = 'keep', 'unreadable content; deletion prohibited'
                row['error'] = str(error)
        return row

    with gzip.open(REPORTS / 'inventory.jsonl.gz', 'xt', encoding='utf-8') as stream, ThreadPoolExecutor(max_workers=8) as pool:
        entries = (item for item in files(OUTPUTS, skipped) if not item[0].is_relative_to(REPORTS))
        for batch in batched(entries, 512):
            for row in pool.map(record, batch):
                key = row['action'] + ': ' + row['reason']
                summary[key]['files'] += 1
                summary[key]['bytes'] += row['bytes']
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    result = {'categories': dict(summary), 'skipped': skipped, 'status': 'Planned',
              'policy': policy_record(), 'protected_inputs': protected_inputs}
    with (REPORTS / 'summary.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(result['categories'], ensure_ascii=False, indent=2))


def apply():
    safe_report_path(REPORTS)
    failures, removed, protected = [], {'files': 0, 'bytes': 0}, 0
    with (REPORTS / 'applied.json').open('x', encoding='utf-8') as receipt:
        status = 'Failed'
        preflight = 'Failed'
        removed_receipt_created = False
        try:
            saved = json.loads((REPORTS / 'summary.json').read_text(encoding='utf-8'))
            require(saved.get('policy') == policy_record(), 'policy changed after inventory')
            tracked = tracked_paths()
            for row in saved.get('protected_inputs', []):
                try:
                    path = safe_path(row['path'], ROOT)
                    info = path.stat(follow_symlinks=False)
                    require(info.st_size == row['bytes'] and info.st_mtime_ns == row['mtime_ns'], 'protected input changed after inventory')
                    require(bool(row.get('sha256')), 'missing SHA-256 for protected input')
                    require(digest(path) == row['sha256'], 'protected input content changed after inventory')
                    protected += 1
                except (OSError, AssertionError) as error:
                    failures.append({'path': row['path'], 'reason': str(error), 'phase': 'protection preflight'})
            for skipped in saved.get('skipped', []):
                path = safe_output_path(skipped['path'])
                reason = classify(path, {})[1] if path != OUTPUTS else ''
                needed = path == OUTPUTS or protection_required(path, reason)
                if POLICY is not None:
                    retained = (*POLICY.get('protected_paths', []), *POLICY.get('retained_references', []))
                    needed = needed or any(target.is_relative_to(path) for target in retained)
                needed = needed or any((ROOT / target).is_relative_to(path) for target in tracked)
                if needed:
                    failures.append({'path': str(path), 'reason': skipped['reason'], 'phase': 'protection preflight'})
            with gzip.open(REPORTS / 'inventory.jsonl.gz', 'rt', encoding='utf-8') as stream:
                rows = [json.loads(line) for line in stream]
            # Preflight every protected entry before the first deletion.
            for row in rows:
                require(row['action'] in ('keep', 'delete'), 'unknown inventory action')
                path = safe_output_path(row['path'])
                require(isinstance(row['bytes'], int) and isinstance(row['mtime_ns'], int), 'invalid inventory stat data')
                if row['action'] == 'delete':
                    try:
                        authorize_delete(path, tracked)
                    except AssertionError as error:
                        failures.append({'path': str(path), 'reason': str(error), 'phase': 'protection preflight'})
                    continue
                needed = row.get('verification_required') or protection_required(path, row.get('reason'))
                if not needed and 'sha256' not in row:
                    continue
                try:
                    verify_entry(row, tracked)
                    protected += 1
                except (OSError, AssertionError) as error:
                    failures.append({'path': str(path), 'reason': str(error), 'phase': 'protection preflight'})
            if not failures:
                preflight = 'Passed'
                with gzip.open(REPORTS / 'removed.jsonl.gz', 'xt', encoding='utf-8') as removed_receipt:
                    removed_receipt_created = True
                    for row in rows:
                        if row['action'] != 'delete':
                            continue
                        try:
                            verify_entry(row, tracked).unlink()
                        except (OSError, AssertionError) as error:
                            failures.append({'path': row['path'], 'reason': str(error), 'phase': 'delete'})
                            continue
                        removed['files'] += 1
                        removed['bytes'] += row['bytes']
                        removed_receipt.write(json.dumps({key: row[key] for key in ('path', 'bytes', 'sha256')}, ensure_ascii=False) + '\n')
                status = 'Applied' if not failures else 'Applied with retained failures'
        except (OSError, AssertionError, ValueError, KeyError) as error:
            failures.append({'path': str(REPORTS), 'reason': str(error),
                             'phase': 'receipt' if preflight == 'Passed' else 'preflight'})
        report = {'status': status, 'protection_preflight': preflight, 'removed': removed,
                  'removed_receipt': 'removed.jsonl.gz' if removed_receipt_created else None,
                  'protected_hashes_verified': protected, 'skipped': failures}
        json.dump(report, receipt, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--policy', type=Path, help='Reviewed task cleanup policy JSON; paths are relative to outputs')
    parser.add_argument('--report-dir', type=Path, default=REPORTS,
                        help='New record subdirectory within outputs or validation/agent/reports')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--plan', action='store_true')
    modes.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        REPORTS = safe_report_path(args.report_dir)
    except (OSError, AssertionError) as error:
        parser.error(str(error))
    if args.plan and any((REPORTS / name).exists() for name in ('inventory.jsonl.gz', 'summary.json', 'applied.json', 'removed.jsonl.gz')):
        parser.error('This inventory already exists; choose a new --report-dir')
    if args.apply and (REPORTS / 'applied.json').exists():
        parser.error('This inventory has already been applied; preserve it and create a new plan')
    POLICY = load_policy(args.policy) if args.policy else None
    if args.plan:
        plan()
    elif apply()['skipped']:
        raise SystemExit(1)
