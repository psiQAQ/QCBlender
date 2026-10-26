"""Build the complete portable tutorial, without an installer or private inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import checked_path, verify_file
from tools.package_identity import extension_manifest, file_record, source_identity
from tools.tutorial_dataset import included_files, load_dataset, verify_csv_inputs
from validation.agent.tools.verify_workspace import check_documents, human_resources

EXTRAS = 'validation/agent/acceptance/tutorial-public-extras.json'


def supplemental_files(root, *, require_complete=True):
    record = json.loads((root / EXTRAS).read_text(encoding='utf-8'))
    if record.get('schema') != 'qcblender.tutorial-extras.v1' or set(record.get('groups', {})) != {'surface-projection', 'aicd'}:
        raise ValueError('Complete tutorial requires both scientific display groups')
    files = {}
    for name, group in record['groups'].items():
        if not require_complete and group.get('status') == 'Not Run':
            continue
        if group.get('status') != 'Passed' or not group.get('license_evidence') or not group.get('files'):
            raise ValueError(f"Tutorial public material blocked: {name}: {group.get('blocker', 'missing license evidence or files')}")
        for entry in group['license_evidence']:
            verify_file(checked_path(root, entry['path']), entry)
        for entry in group['files']:
            path = entry['path']
            if not path.startswith('validation/shared/data/public/scientific-displays/') or not entry.get('license'):
                raise ValueError('Supplemental input must have a public path and a recorded license: ' + path)
            verify_file(checked_path(root, path), entry)
            if path in files:
                raise ValueError('Duplicate supplemental input: ' + path)
            files[path] = entry
    return files


def inventory(root=ROOT):
    root = Path(root).resolve()
    extra = supplemental_files(root)
    dataset = load_dataset(root)
    public = root / 'validation/shared/data/public'
    human_resources(root / 'validation/human')
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', 'validation/human'], cwd=root).decode('utf-8').split('\0')
    files = {path.removeprefix('validation/'): root / path for path in tracked if path and not path.endswith('/.gitkeep')}
    topics = {path for path in files if path.startswith('human/topics/')}
    if len(topics) != 12 or 'human/SOP.md' not in files:
        raise ValueError('Tutorial must include the SOP and all twelve topics')
    for name, entry in included_files(dataset, root).items():
        path = checked_path(public, name)
        verify_file(path, entry)
        files['shared/data/public/' + name] = path
    for name in ('LICENSE', 'NOTICE.md', 'README.md', dataset['dataset_id'] + '/tutorial-samples.json'):
        files['shared/data/public/' + name] = checked_path(public, name)
    for name in extra:
        files[name.removeprefix('validation/')] = checked_path(root, name)
    verify_csv_inputs(public, dataset)
    for name, path in files.items():
        checked_path(root, path.relative_to(root).as_posix())
        if not path.is_file():
            raise FileNotFoundError(path)
        if name.startswith('human/') and path.suffix == '.md':
            text = path.read_text(encoding='utf-8')
            if 'shared/data/local/' in text or 'shared/install/' in text:
                raise ValueError('Public tutorial still requires private data or a bundled installer: ' + name)
    return files, dataset


def verify_source_references(materials):
    """Check the exact input/log/tensor references carried by AICD declarations."""
    for path in (materials / 'shared/data/public').rglob('source.json'):
        record = json.loads(path.read_text(encoding='utf-8'))
        if record.get('format') != 'qcblender.aicd.source.v1':
            continue
        for entry in record['files'].values():
            target = checked_path(path.parent, entry['path'])
            if file_record(target)['sha256'] != entry['sha256']:
                raise ValueError('AICD companion identity differs: ' + str(target))


def build(output, stage, root=ROOT):
    root, output, stage = Path(root).resolve(), Path(output), Path(stage)
    files, dataset = inventory(root)
    version = extension_manifest(root)['version']
    if output.name != f'qcblender-tutorial-{version}.zip':
        raise ValueError('Tutorial filename must match extension version')
    stage.mkdir(parents=True, exist_ok=False)
    for name, path in files.items():
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    # Existing document validation also accepts legacy detached tutorials with installers.
    (stage / 'shared/install').mkdir()
    documents = check_documents(stage, require_images=True)
    verify_source_references(stage)
    members = {name: file_record(stage / name, stage) for name in sorted(files)}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.write(stage / name, name)
    verify_archive(output, members)
    return dict(status='Passed', source_commit=source_identity(root)[0], package=file_record(output),
                members=members, documents=documents, human_execution='Not Run')


def verify_archive(path, members):
    with zipfile.ZipFile(path) as archive:
        if any((info.external_attr >> 16) & 0o170000 == 0o120000 for info in archive.infolist()):
            raise ValueError('Tutorial ZIP cannot contain symbolic links')
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(members):
            raise ValueError('Tutorial ZIP membership differs from exact inventory')
        for name, record in members.items():
            raw = archive.read(name)
            if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
                raise ValueError('Tutorial ZIP content differs: ' + name)
        if archive.testzip() is not None:
            raise ValueError('Tutorial ZIP CRC failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'stage', 'report'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output, args.stage)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('status', 'package')}))


if __name__ == '__main__':
    main()
