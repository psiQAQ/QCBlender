"""Select and verify versioned tutorial data without changing historical inputs."""
import csv
import json
from pathlib import Path

from tools.local_inputs import DATA, checked_path, verify_file

DELIVERY = 'validation/agent/acceptance/tutorial-sample-delivery.json'
FROZEN_MANIFEST = 'validation/agent/v1-acceptance/tutorial-samples.json'
LEGACY_PACKAGE = 'validation/agent/packages/qcblender-public-tutorial-samples-v2.zip'


def _manifest(root, record):
    path = checked_path(root, record['path'])
    verify_file(path, record)
    return path, json.loads(path.read_text(encoding='utf-8'))


def load_dataset(root, dataset='current'):
    """Return selected manifest, package identities and paths; verify the manifest now."""
    root = Path(root).resolve()
    delivery = json.loads(checked_path(root, DELIVERY).read_text(encoding='utf-8'))
    if delivery['schema'] == 1:
        if dataset not in ('current', 'legacy-v2'):
            raise ValueError('Unknown tutorial dataset: ' + dataset)
        selected = dict(dataset_id='legacy-v2',
                        manifest=dict(delivery['manifest'], path=FROZEN_MANIFEST),
                        package=dict(delivery['package'], path=LEGACY_PACKAGE))
    elif delivery['schema'] == 2:
        versions = dict(delivery.get('historical_datasets', {}))
        versions['legacy-v2'] = delivery['legacy_dataset']
        versions[delivery['dataset_id']] = delivery
        if dataset != 'current' and dataset not in versions:
            raise ValueError('Unknown tutorial dataset: ' + dataset)
        selected = delivery if dataset == 'current' else versions[dataset]
    else:
        raise ValueError('Unknown tutorial delivery schema')
    legacy = selected['dataset_id'] == 'legacy-v2'
    manifest_record = selected['manifest']
    if legacy:
        if manifest_record['path'] != FROZEN_MANIFEST:
            raise ValueError('Legacy tutorial manifest must retain its frozen path')
    elif not manifest_record['path'].startswith(DATA + '/public/' + selected['dataset_id'] + '/'):
        raise ValueError('Current tutorial manifest is outside its versioned public directory')
    manifest_path, manifest = _manifest(root, manifest_record)
    package_record = selected['package']
    package_path = checked_path(root, package_record['path'])
    if not package_path.is_relative_to(root / 'validation/agent/packages'):
        raise ValueError('Tutorial package is outside the package directory')
    restricted = {row['sha256'] for row in manifest['files'].values()
                  if row['distribution'] != 'included'}
    if delivery['schema'] == 2:
        if (delivery['legacy_dataset']['dataset_id'] != 'legacy-v2'
                or delivery['legacy_dataset']['manifest']['path'] != FROZEN_MANIFEST):
            raise ValueError('Legacy tutorial dataset must retain its frozen identity')
        _, historical = _manifest(root, delivery['legacy_dataset']['manifest'])
        restricted.update(row['sha256'] for row in historical['files'].values()
                          if row['distribution'] != 'included')
    result = dict(dataset_id=selected['dataset_id'], manifest=manifest,
                  manifest_path=manifest_path, manifest_record=manifest_record,
                  package_path=package_path, package_record=package_record,
                  legacy=legacy, restricted_sha256=restricted)
    included_files(result, root)
    return result


def included_files(dataset, root):
    """Validate the public allowlist and return records keyed by archive path."""
    public = Path(root).resolve() / DATA / 'public'
    records = {}
    for row in dataset['manifest']['files'].values():
        if row['distribution'] != 'included':
            continue
        name = row['archive_path']
        checked_path(public, name)
        if row['license'] != 'CC-BY-4.0' or row['sha256'] in dataset['restricted_sha256']:
            raise ValueError('Unlicensed tutorial input cannot be included: ' + row['id'])
        if dataset['legacy']:
            if name.startswith('P02/') or row.get('calculation_group') == 'P02':
                raise ValueError('Unverified legacy P02 data cannot be included')
        else:
            if not name.startswith(dataset['dataset_id'] + '/'):
                raise ValueError('Current tutorial input is outside its versioned directory: ' + name)
            if row.get('path') != DATA + '/public/' + name:
                raise ValueError('Current tutorial source path differs from archive path: ' + name)
        if name in records:
            raise ValueError('Duplicate tutorial archive path: ' + name)
        records[name] = row
    return records


def verify_csv_inputs(public, dataset):
    """Verify declared IRC/Mayer CSV references and matching step identities."""
    public = Path(public).resolve()
    records = included_files(dataset, public.parents[3])
    steps = {}
    for name, record in records.items():
        if not name.endswith('.csv') or 'P04' not in Path(name).parts:
            continue
        path = checked_path(public, name)
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            columns = [column for column in ('fchk', 'mayer_output') if column in (reader.fieldnames or [])]
            if not columns and record.get('role') == 'energy_and_segment_mapping':
                if not {'step', 'energy_hartree', 'source_segment'}.issubset(reader.fieldnames or []):
                    raise ValueError('Unknown native energy mapping header: ' + name)
                continue
            if 'step' not in (reader.fieldnames or []) or len(columns) != 1:
                raise ValueError('Unknown IRC/Mayer CSV header: ' + name)
            column = columns[0]
            numbers = []
            for row in reader:
                number = row['step']
                if not number or number in numbers:
                    raise ValueError('Missing or duplicate IRC/Mayer step: ' + name)
                numbers.append(number)
                target = checked_path(path.parent, row[column])
                relative = target.relative_to(public).as_posix()
                if relative not in records or not target.is_file():
                    raise ValueError('Broken or undeclared IRC/Mayer relative input: ' + relative)
            if not numbers:
                raise ValueError('Empty IRC/Mayer CSV: ' + name)
            steps.setdefault(column, []).append(tuple(numbers))
    sequences = [sequence for values in steps.values() for sequence in values]
    if sequences and any(sequence != sequences[0] for sequence in sequences):
        raise ValueError('IRC and Mayer CSV step identities differ')
