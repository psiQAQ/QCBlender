"""Inventory output archives and mapped installer copies without deleting files."""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[3]
INSTALLER_NAME = re.compile(r'qcblender-\d[^/\\]*\.zip$')
MAP_PATH = 'outputs/evidence/2026-10-05/alpha-readiness/preservation-map.jsonl.gz'
LATEST = 'outputs/candidates/current/alpha-ci-0.1.0-190e11e'
PROTECTED_ROOTS = (
    'outputs/projects', 'outputs/recovery', 'outputs/build-python',
    'outputs/build-site', 'outputs/science', 'outputs/science-profile',
    'outputs/wheels', 'outputs/repaired-wheels', 'outputs/unrepaired-wheels',
    'outputs/native-backend-licenses',
)
SKIP_NAMES = {'.git', '.venv', 'venv', 'env', 'site-packages', '__pycache__',
              '.local', 'extensions', 'node_modules', 'objects', 'content'}
GROUPS = {
    'retired-installer': '旧插件安装包',
    'retired-installer-object': '映射中的旧安装包对象',
    'old-samples': '旧版或重复公开样本包',
    'old-reproduction': '旧版自动生成复现包',
    'old-ci-container': '旧 CI 外层压缩包',
    'incomplete-download': '不完整第三方下载',
    'latest-candidate': '最新候选材料',
    'latest-ci-container': '最新 CI 原始容器',
    'other-extension': '其他插件安装包',
    'project': '工程或恢复压缩包',
    'source-or-reference': '源码、依赖或原始资料',
    'unknown': '用途未确认',
    'unreadable': '不可读取',
}
REVIEW_GROUPS = {name for name in GROUPS if name.startswith(('retired-', 'old-'))}
REVIEW_GROUPS.add('incomplete-download')


def linked(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def source_path(root, value):
    """Reject traversal and linked ancestors before opening a source path."""
    path = Path(value)
    path = Path(os.path.abspath(path if path.is_absolute() else root / path))
    if not path.is_relative_to(root):
        raise ValueError(f'Path escapes repository: {path}')
    for ancestor in (path, *path.parents):
        if ancestor.exists() or ancestor.is_symlink():
            if linked(ancestor):
                raise ValueError(f'Linked path is excluded: {ancestor}')
        if ancestor == root:
            break
    return path


def file_identity(path):
    before = path.stat()
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f'File changed during inventory: {path}')
    return {'bytes': after.st_size, 'mtime_ns': after.st_mtime_ns, 'sha256': digest}


def archive_details(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        details = {'members': len(names)}
        if 'blender_manifest.toml' in names:
            member = archive.getinfo('blender_manifest.toml')
            if member.file_size > 1024 * 1024:
                raise ValueError('Extension manifest exceeds the inspection limit')
            manifest = tomllib.loads(archive.read(member).decode('utf-8'))
            details.update(extension_id=manifest.get('id'), version=manifest.get('version'))
        if 'release-manifest.json' in names:
            member = archive.getinfo('release-manifest.json')
            if member.file_size > 1024 * 1024:
                raise ValueError('Candidate manifest exceeds the inspection limit')
            manifest = json.loads(archive.read(member))
            details['candidate_run_id'] = manifest.get('candidate_run_id')
        details['has_blend'] = any(name.lower().endswith('.blend') for name in names)
        return details


def check_latest(root, directory):
    directory = source_path(root, directory)
    manifest_path = source_path(root, directory / 'release-manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    checked = {}
    for role in ('extension', 'samples', 'reproduction'):
        expected = manifest['files'][role]
        path = source_path(root, directory / expected['path'])
        if not path.is_relative_to(directory):
            raise ValueError(f'Candidate member escapes its directory: {path}')
        actual = file_identity(path)
        if any(actual[key] != expected[key] for key in ('bytes', 'sha256')):
            raise ValueError(f'Latest candidate identity differs: {path}')
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise ValueError(f'Latest candidate CRC failed: {path}: {bad}')
        checked[role] = {'path': path.relative_to(root).as_posix(), **actual}
    report_names = ('stdlib', 'public-science', 'node-helpers', 'extension-install',
                    'node-assets', 'cold-original', 'cold-moved', 'qualification',
                    'sample-package', 'reproduction')
    for name in report_names:
        expected = manifest['reports'][name]
        path = source_path(root, directory / expected['path'])
        if not path.is_relative_to(directory):
            raise ValueError(f'Candidate report escapes its directory: {path}')
        actual = file_identity(path)
        report = json.loads(path.read_text(encoding='utf-8'))
        if any(actual[key] != expected[key] for key in ('bytes', 'sha256')):
            raise ValueError(f'Latest candidate report identity differs: {path}')
        if expected.get('status') != 'Passed' or report.get('status') != 'Passed':
            raise ValueError(f'Latest candidate report is not Passed: {path}')
    return directory, {
        'status': 'Passed', 'directory': directory.relative_to(root).as_posix(),
        'source_commit': manifest['source_commit'],
        'product_tree': manifest['product_tree'],
        'candidate_run_id': manifest['candidate_run_id'], 'files': checked,
        'checked_reports': list(report_names),
        'scope': 'Existing file identity, ZIP CRC and recorded reports; no product tests rerun',
        'blender_rerun': 'Not Run', 'independent_human_review': 'Not Run',
    }


def scan_archives(root, exclusions, errors):
    pending = [source_path(root, 'outputs')]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(directory.iterdir(), key=lambda path: path.name)
        except OSError as error:
            errors.append({'path': directory.relative_to(root).as_posix(), 'error': str(error)})
            continue
        for path in entries:
            relative = path.relative_to(root).as_posix()
            try:
                if linked(path):
                    exclusions.append({'path': relative, 'reason': 'Link or reparse point'})
                elif path.is_dir():
                    if (relative in PROTECTED_ROOTS or path.name in SKIP_NAMES
                            or path.name.endswith('.qcdata')):
                        exclusions.append({'path': relative, 'reason': 'Protected or out-of-scope directory'})
                    else:
                        pending.append(path)
                elif path.name.lower().endswith('.zip'):
                    yield path
            except OSError as error:
                errors.append({'path': relative, 'error': str(error)})


def mapped_installers(root, errors):
    mapping = source_path(root, MAP_PATH)
    if not mapping.is_file():
        errors.append({'path': MAP_PATH, 'error': 'Preservation map unavailable; anonymous copies not inventoried'})
        return {}
    records = {}
    with gzip.open(mapping, 'rt', encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            record = json.loads(line)
            if not INSTALLER_NAME.search(record.get('old_path', '')):
                continue
            # Maps retain absolute original destinations; resolve by the evidence suffix.
            destination = record['new_path'].replace('\\', '/')
            suffix = 'outputs/evidence/2026-10-05/alpha-readiness/objects/'
            if suffix not in destination:
                raise ValueError(f'Unexpected installer object destination on line {line_number}')
            relative = suffix + destination.split(suffix, 1)[1]
            try:
                path = source_path(root, relative)
                if not path.is_relative_to(root / suffix):
                    raise ValueError('Mapped installer escapes its object directory')
                if not path.is_file():
                    errors.append({'path': relative, 'error': 'Mapped object does not exist'})
                    continue
            except (OSError, ValueError) as error:
                errors.append({'path': relative, 'error': str(error)})
                continue
            item = records.setdefault(path, {'mapping': MAP_PATH, 'old_paths': [],
                                             'expected_sha256': record['sha256'],
                                             'expected_bytes': record['bytes']})
            if (item['expected_sha256'], item['expected_bytes']) != (record['sha256'], record['bytes']):
                raise ValueError(f'Conflicting preservation identities: {relative}')
            item['old_paths'].append(record['old_path'])
    return records


def classify(path, root, latest_dir, latest, details, mapped=False):
    relative = path.relative_to(root).as_posix()
    if path.is_relative_to(latest_dir):
        return 'latest-candidate', 'Keep current complete candidate and its recorded identity'
    if details.get('extension_id') == 'qcblender':
        if mapped or INSTALLER_NAME.fullmatch(path.name):
            return ('retired-installer-object' if mapped else 'retired-installer',
                    'Superseded installer; preserve reports and record retired binary availability')
    if mapped:
        return 'unknown', 'Mapped installer does not contain the expected extension identity'
    if path.name.startswith('qcblender-public-tutorial-samples-'):
        return 'old-samples', 'Keep canonical frozen v2 and preserve historical NOTICE/manifests before removing copies'
    if path.name.startswith('qcblender-reproduction-') and details['has_blend']:
        return 'old-reproduction', 'Generated candidate reproduction; retain latest example and historical reports'
    if path.name == 'candidate-artifact.zip' and 'candidate_run_id' in details:
        if details['candidate_run_id'] == latest['candidate_run_id']:
            return 'latest-ci-container', 'Keep original downloaded container for the latest CI candidate'
        return 'old-ci-container', 'Superseded CI container; preserve extracted reports and manifests first'
    if 'extension_id' in details:
        return 'other-extension', 'Separate plugin or runtime dependency; outside QCBlender installer cleanup'
    if details['has_blend'] or path.name in {'portable.zip', 'tutorial-project.zip'}:
        return 'project', 'Project or recovery data requires a separate preservation decision'
    prefixes = ('outputs/build-sources/', 'outputs/m0-research/',
                'outputs/committed-build-d1abfe8/source/outputs/build-sources/',
                'outputs/v1-acceptance/sources/')
    if relative.startswith(prefixes):
        return 'source-or-reference', 'Keep source archives, calculation/reference material and license provenance'
    return 'unknown', 'Purpose or active references not established; keep until reviewed'


def inventory(root, latest_directory):
    root = Path(root).absolute()
    latest_dir, latest = check_latest(root, latest_directory)
    exclusions, errors = [], []
    mapped = mapped_installers(root, errors)
    paths = {path: None for path in scan_archives(root, exclusions, errors)}
    paths.update(mapped)
    rows = []
    for path in sorted(paths, key=lambda value: value.as_posix()):
        relative = path.relative_to(root).as_posix()
        row = {'path': relative, 'absolute_path': str(path), 'decision': 'keep',
               'approval': 'Not Requested', 'inspection': 'Not Run'}
        try:
            source_path(root, path)
            info = path.stat()
            row.update(bytes=info.st_size, mtime_ns=info.st_mtime_ns)
            try:
                details = archive_details(path)
            except zipfile.BadZipFile as error:
                if relative == 'outputs/reference-tools/VESTA-3.5.8-win64.zip':
                    row.update(group='incomplete-download', reason='ZIP central directory cannot be read',
                               archive_error=str(error), inspection='Failed')
                else:
                    raise
            else:
                group, reason = classify(path, root, latest_dir, latest, details, path in mapped)
                row.update(group=group, reason=reason, inspection='Passed', archive=details)
            if row['group'] in REVIEW_GROUPS:
                row.update(file_identity(path))
                row.update(decision='review-for-deletion', approval='Required')
            if path in mapped:
                record = mapped[path]
                row['preservation'] = record
                if (row.get('sha256'), row['bytes']) != (record['expected_sha256'], record['expected_bytes']):
                    raise ValueError('Anonymous object differs from preservation map')
        except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
            row.update(group='unreadable', decision='keep', approval='Not Requested',
                       inspection='Failed', reason=str(error))
            errors.append({'path': relative, 'error': str(error)})
        rows.append(row)
    groups = {}
    for name in sorted(GROUPS):
        matches = [row for row in rows if row['group'] == name]
        if matches:
            groups[name] = {'label': GROUPS[name], 'files': len(matches),
                            'bytes': sum(row.get('bytes', 0) for row in matches)}
    proposed = [row for row in rows if row['decision'] == 'review-for-deletion']
    return {
        'schema': 'qcblender.cleanup-inventory.v1',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'root': str(root),
        'status': 'Needs Review', 'deletion': 'Not Run', 'read_only_sources': True,
        'latest': latest, 'groups': groups,
        'review_candidates': {'files': len(proposed), 'bytes': sum(row['bytes'] for row in proposed)},
        'files': rows, 'scan_errors': errors, 'excluded_paths': exclusions,
        'limitations': [
            'Only .zip archives outside protected directories and installer objects in the specified map are inspected.',
            'Other anonymous content stores, environments, projects, recovery data and .qcdata directories are not traversed.',
            'Archive contents are not extracted; full CRC is checked only for the retained latest candidate.',
            'No live process, open project, installed environment or independent human acceptance is inferred.',
            'References and preservation prerequisites require review before any separately authorized deletion.',
        ],
    }


def markdown(report):
    lines = ['# 历史压缩包清理盘点', '',
             f"扫描根目录：`{report['root']}`。生成时间（UTC）：`{report['created_utc']}`。", '',
             '**待确认；没有执行删除。** 安装候选、目录排除和读取失败均在本清单中分别列出。', '',
             f"保留最新候选：`{report['latest']['directory']}`。文件身份及原报告核对 Passed；Blender 复跑 Not Run。", '',
             '| 分组 | 文件数 | 字节 |', '| --- | ---: | ---: |']
    for group in report['groups'].values():
        lines.append(f"| {group['label']} | {group['files']} | {group['bytes']:,} |")
    lines.extend(['', '## 待确认删除候选', '',
                  '本表按精确文件列出，不授权删除其父目录。SHA-256 和修改时间在相邻 JSON 中。', '',
                  '| 路径 | 字节 | 分类 | 前置条件／理由 |', '| --- | ---: | --- | --- |'])
    for row in report['files']:
        if row['decision'] == 'review-for-deletion':
            lines.append(f"| `{row['path']}` | {row['bytes']:,} | {GROUPS[row['group']]} | {row['reason']} |")
    lines.extend(['', '## 保留的可见压缩包', '', '| 路径 | 字节 | 理由 |', '| --- | ---: | --- |'])
    for row in report['files']:
        if row['decision'] == 'keep':
            reason = row['reason'].replace('|', '\\|').replace('\n', ' ')
            lines.append(f"| `{row['path']}` | {row.get('bytes', '未知')} | {reason} |")
    lines.extend(['', '## 未检查范围', ''])
    lines.extend('- ' + item for item in report['limitations'])
    lines.extend(['', f"排除目录/链接：{len(report['excluded_paths'])} 项；读取或枚举失败：{len(report['scan_errors'])} 项。完整路径在 JSON。", '',
                  '## 读取失败', '', '| 路径 | 原因 |', '| --- | --- |'])
    for error in report['scan_errors']:
        message = error['error'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| `{error['path']}` | {message} |")
    return '\n'.join(lines) + '\n'


def write_reports(root, destination, report):
    destination = source_path(root, destination)
    allowed = root / 'validation/agent/reports'
    if not destination.is_relative_to(allowed) or destination == allowed:
        raise ValueError('Report destination must be a new directory below validation/agent/reports')
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'inventory.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (destination / 'inventory.md').write_text(markdown(report), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository containing the actual outputs to inspect')
    parser.add_argument('--latest-candidate', default=LATEST, help='Explicit complete candidate directory, relative to root')
    parser.add_argument('--report-dir', type=Path, required=True, help='New directory under validation/agent/reports')
    args = parser.parse_args()
    root = args.root.absolute()
    destination = source_path(root, args.report_dir)
    if destination.exists():
        parser.error(f'Report directory already exists; choose a fresh batch: {destination}')
    report = inventory(root, args.latest_candidate)
    write_reports(root, destination, report)
    print(json.dumps({'status': report['status'], 'deletion': report['deletion'],
                      'report': str(destination / 'inventory.json'),
                      'review_candidates': report['review_candidates'],
                      'scan_errors': len(report['scan_errors'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
