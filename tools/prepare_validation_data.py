"""Prepare the frozen public samples and explicitly selected local input copies."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.candidate_artifacts import SAMPLE_NAME, verify_samples
from tools.local_inputs import DATA, checked_path, input_path, verify_file

PACKAGE = 'validation/agent/packages/' + SAMPLE_NAME
MIGRATION = DATA + '/migration-map.json'
FROZEN_MANIFEST = 'docs/v1-acceptance/tutorial-samples.json'


def write_public(path, raw):
    expected = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    if path.exists():
        verify_file(path, expected)
        return 'verified'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)
    verify_file(path, expected)
    return 'created'


def copy_record(source, destination, record):
    if destination.exists():
        verify_file(destination, record)
        return 'verified'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open('rb') as source_stream, destination.open('xb') as target_stream:
        shutil.copyfileobj(source_stream, target_stream)
    verify_file(destination, record)
    return 'copied'


def verify_csv_inputs(root):
    base = checked_path(root, DATA + '/public/P04')
    for name, column in (('steps.csv', 'fchk'), ('mayer-pyscf.csv', 'mayer_output')):
        with (base / name).open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        if [row['step'] for row in rows] != ['1', '2', '3']:
            raise ValueError('P04 input steps differ: ' + name)
        for row in rows:
            path = checked_path(base, row[column])
            if not path.is_file():
                raise FileNotFoundError('P04 relative input missing: ' + str(path))


def prepare(root=ROOT, reference_root=None, reference_layout='current',
            include_local=False, include_calculations=False):
    root = Path(root).resolve()
    if reference_layout not in ('legacy', 'current'):
        raise ValueError('Reference layout must be legacy or current')
    if (include_local or include_calculations) and reference_root is None:
        raise ValueError('Local inputs require an explicit --reference-root')
    reference = Path(reference_root).resolve() if reference_root is not None else None
    package = checked_path(root, PACKAGE)
    sample_report = verify_samples(package, root)
    manifest = json.loads(checked_path(root, FROZEN_MANIFEST).read_text(encoding='utf-8'))
    migration = json.loads(checked_path(root, MIGRATION).read_text(encoding='utf-8'))
    if migration['schema'] != 'qcblender.validation-data-migration.v1':
        raise ValueError('Unknown validation migration schema')
    verify_file(checked_path(root, FROZEN_MANIFEST), migration['frozen_manifest'])
    public_names = {item['archive_path'] for item in manifest['files'].values()
                    if item['distribution'] == 'included'}
    public_names.update(('LICENSE', 'NOTICE.md', 'tutorial-samples.json'))
    public = checked_path(root, DATA + '/public')
    # Preflight every selected source and existing target before creating copies.
    planned = []
    with zipfile.ZipFile(package) as archive:
        for name in sorted(public_names):
            path = checked_path(public, name)
            raw = archive.read(name)
            if path.exists():
                verify_file(path, dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
            planned.append((name, path, raw))
    selected = {'local'} if include_local else set()
    if include_calculations:
        selected.add('calculations')
    copies, verified = [], []
    identities = {}
    for row in migration['files']:
        group = row['group']
        if group not in selected | {'regression', 'package', 'catalog'}:
            continue
        target = checked_path(root, row['path'])
        allowed = (root / DATA, root / 'validation/agent/packages')
        if not any(target.is_relative_to(base) for base in allowed):
            raise ValueError('Migration target is outside validation data: ' + row['path'])
        identity = (row['bytes'], row['sha256'])
        if row['path'] in identities and identities[row['path']] != identity:
            raise ValueError('Conflicting migration identities: ' + row['path'])
        identities[row['path']] = identity
        if group not in selected:
            verify_file(target, row)
            verified.append(row['path'])
            continue
        relative_source = row['source'] if reference_layout == 'legacy' else row['path']
        source = checked_path(reference, relative_source)
        verify_file(source, row)
        if target.exists():
            verify_file(target, row)
        copies.append((source, target, row))
    public_files = []
    for name, path, raw in planned:
        public_files.append(dict(path=path.relative_to(root).as_posix(),
                                 action=write_public(path, raw)))
    local_files = []
    for source, target, row in copies:
        action = copy_record(source, target, row)
        local_files.append(dict(source=str(source), path=row['path'], group=row['group'],
                                action=action, bytes=row['bytes'], sha256=row['sha256']))
    verify_csv_inputs(root)
    local_count = 0
    if include_local:
        catalog = json.loads((root / DATA / 'local-inputs.json').read_text(encoding='utf-8'))
        for key in catalog['files']:
            input_path(key, root)
            local_count += 1
    return dict(schema='qcblender.validation-data-preparation.v1', status='Passed',
                reference_root=str(reference) if reference is not None else None,
                reference_layout=reference_layout, public_package=sample_report,
                public_files=public_files, verified_paths=sorted(set(verified)),
                copies=local_files, local_input_count=local_count,
                calculations='Passed' if include_calculations else 'Not Run',
                scientific_regression='Not Run', gui='Not Run', independent_human_review='Not Run',
                deletion='Not Run; this command only creates or verifies files')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--reference-root', type=Path)
    parser.add_argument('--reference-layout', choices=('legacy', 'current'), default='current',
                        help='Use legacy source paths only for the reviewed first migration')
    parser.add_argument('--include-local', action='store_true')
    parser.add_argument('--include-calculations', action='store_true')
    parser.add_argument('--report', type=Path, required=True,
                        help='New report path inside this checkout; existing reports are preserved')
    args = parser.parse_args()
    report = args.report.resolve()
    if not report.is_relative_to(ROOT):
        parser.error('--report must be inside this checkout')
    checked_path(ROOT, report.relative_to(ROOT).as_posix())
    if report.exists():
        raise FileExistsError('Choose a new report path: ' + str(report))
    result = prepare(ROOT, args.reference_root, args.reference_layout,
                     args.include_local, args.include_calculations)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], public_inputs=result['public_package']['included_files'],
                          local_inputs=result['local_input_count'],
                          mapped_copies=len(result['copies']), report=str(report))))


if __name__ == '__main__':
    main()
