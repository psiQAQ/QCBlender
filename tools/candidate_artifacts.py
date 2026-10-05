"""Assemble an immutable candidate from current technical reports and public data."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.package_identity import dependency_identity, extension_filename, extension_manifest, file_record, source_identity
from tools.public_reproduction import reproduction_members
from tools.test_profiles import PUBLIC_SCIENCE, STDLIB

REQUIRED_REPORTS = ('stdlib', 'public-science', 'node-helpers', 'extension-install',
                    'node-assets', 'cold-original', 'cold-moved', 'qualification',
                    'sample-package', 'reproduction')
SAMPLE_NAME = 'qcblender-public-tutorial-samples-v2.zip'


def verify_samples(package, root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'docs/v1-acceptance/tutorial-samples.json').read_text(encoding='utf-8'))
    delivery = json.loads((root / 'docs/acceptance/tutorial-sample-delivery.json').read_text(encoding='utf-8'))
    actual = file_record(package)
    if any(actual[key] != delivery['package'][key] for key in ('bytes', 'sha256')):
        raise ValueError('Frozen v2 sample ZIP identity differs from delivery record')
    import hashlib
    with zipfile.ZipFile(package) as archive:
        expected = {f['archive_path'] for f in manifest['files'].values() if f['distribution'] == 'included'}
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != expected | {'LICENSE', 'NOTICE.md', 'tutorial-samples.json'}:
            raise ValueError('Public sample membership differs from the included-file allowlist')
        if any(name.startswith('P02/') for name in names):
            raise ValueError('Unverified P02 data cannot be included')
        if json.loads(archive.read('tutorial-samples.json')) != manifest:
            raise ValueError('Public sample manifest differs from source')
        for record in manifest['files'].values():
            if record['distribution'] != 'included':
                continue
            raw = archive.read(record['archive_path'])
            if record['license'] != 'CC-BY-4.0' or len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
                raise ValueError('Public sample license or checksum differs: ' + record['id'])
        if archive.testzip() is not None:
            raise ValueError('Public sample ZIP CRC failed')
    return dict(status='Passed', package=actual, included_files=len(expected), excluded_groups=['P02'],
                license_scope='Recorded CC BY 4.0 included files; no independent license determination')


def validate_reports(directory, commit, candidate_sha256):
    directory = Path(directory)
    reports = {}
    for name in REQUIRED_REPORTS:
        path = directory / (name + '.json')
        report = json.loads(path.read_text(encoding='utf-8'))
        if report.get('status') != 'Passed' or report.get('source_commit') != commit:
            raise ValueError(name + ': missing Passed status or current source identity')
        if name in ('stdlib', 'public-science') and (report.get('skipped') != 0 or report.get('errors') != 0 or report.get('failures') != 0):
            raise ValueError(name + ': tests were skipped or failed')
        if name == 'stdlib' and (report.get('suite') != 'stdlib' or report.get('modules') != list(STDLIB) or report.get('tests', 0) < 60):
            raise ValueError('Standard-library suite was not executed completely')
        if name == 'public-science' and (report.get('suite') != 'public-core' or report.get('modules') != list(PUBLIC_SCIENCE) or report.get('tests', 0) < 49):
            raise ValueError('Public numerical suite was not executed completely')
        if name.startswith('cold-') and report.get('cold_open') != 'Passed':
            raise ValueError(name + ': cold reopen was not verified')
        if name == 'reproduction' and (report.get('cold_open') != 'Passed' or report.get('portable_saved') is not True):
            raise ValueError('Public reproduction was not saved and cold reopened')
        if name == 'qualification' and report.get('sha256') != candidate_sha256:
            raise ValueError('Qualification belongs to a different candidate ZIP')
        if name in ('extension-install', 'node-assets', 'cold-original', 'cold-moved', 'reproduction') and report.get('candidate_sha256') != candidate_sha256:
            raise ValueError(name + ': different candidate ZIP')
        reports[name] = dict(file_record(path, directory.parent), status='Passed')
    return reports


def reproduction_zip(directory, destination, root=ROOT):
    directory, destination, root = Path(directory), Path(destination), Path(root)
    inputs = json.loads((root / 'docs/v1-acceptance/tutorial-samples.json').read_text(encoding='utf-8'))['files']
    owned = {item['sha256'] for item in inputs.values() if item['distribution'] == 'included'}
    for name in ('example.blend', 'example.png', 'README.md'):
        if not (directory / name).is_file():
            raise FileNotFoundError('Public reproduction material missing: ' + name)
    paths = [directory / name for name in ('example.blend', 'example.png', 'README.md')]
    paths.extend(sorted((directory / 'example.qcdata').rglob('*')))
    for path in paths:
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError('Reproduction material cannot contain linked paths')
        if not path.resolve().is_relative_to(directory.resolve()):
            raise ValueError('Reproduction material escapes the selected directory')
    files = {path.relative_to(directory).as_posix(): path for path in paths if path.is_file()}
    expected = reproduction_members(lambda name: files[name].open('rb'), files, owned)
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(expected):
            archive.write(files[name], name)
    return file_record(destination)


def assemble(candidate, samples, reproduction, reports_dir, output, run_id, channel='alpha', root=ROOT):
    root, output = Path(root), Path(output)
    commit, tree = source_identity(root)
    manifest = extension_manifest(root)
    if channel not in ('alpha', 'preview') or type(run_id) is not int or run_id < 0:
        raise ValueError('Candidate channel or run ID is invalid')
    if Path(candidate).name != extension_filename(root):
        raise ValueError('Candidate ZIP filename does not match the extension manifest')
    sample_report = verify_samples(samples, root)
    candidate_record = file_record(candidate)
    reports = validate_reports(reports_dir, commit, candidate_record['sha256'])
    qualification = json.loads((Path(reports_dir) / 'qualification.json').read_text(encoding='utf-8'))
    dependencies = dependency_identity((root / 'dependencies.lock.json').read_bytes(),
                                       (root / 'science-sources.lock.json').read_bytes(), qualification['backend'])
    reproduction_report = json.loads((Path(reports_dir) / 'reproduction.json').read_text(encoding='utf-8'))
    public_inputs = json.loads((root / 'docs/v1-acceptance/tutorial-samples.json').read_text(encoding='utf-8'))['files']
    if reproduction_report.get('source_sha256') not in {p['sha256'] for p in public_inputs.values() if p['distribution'] == 'included' and p['id'].startswith('P01')}:
        raise ValueError('Reproduction report does not use a verified public P01 input')
    if json.loads((Path(reports_dir) / 'sample-package.json').read_text())['package']['sha256'] != sample_report['package']['sha256']:
        raise ValueError('Sample report belongs to a different package')
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    for role, path in (('extension', Path(candidate)), ('samples', Path(samples))):
        shutil.copyfile(path, output / path.name)
        files[role] = file_record(output / path.name)
    files['reproduction'] = reproduction_zip(reproduction, output / f"qcblender-reproduction-{manifest['version']}.zip", root)
    target_reports = output / 'reports'
    target_reports.mkdir()
    for name, record in reports.items():
        source = Path(reports_dir).parent / record['path']
        shutil.copyfile(source, target_reports / source.name)
        record['path'] = 'reports/' + source.name
    result = dict(schema='qcblender.release-candidate.v1', version=manifest['version'], channel=channel,
                  source_commit=commit, product_tree=tree, candidate_run_id=run_id,
                  workflow='extension-package.yml', artifact_name=f"qcblender-candidate-{manifest['version']}-{commit}",
                  platform=dict(os='windows', architecture='x64', blender='5.1.1', python='3.13', numpy='2.3.4'),
                  dependencies=dependencies, files=files, reports=reports,
                  license_review=dict(status='Not Run', blocker='IOData/GBasis GPL metadata and LGPL source-license text remain unresolved'),
                  independent_alpha_installation=dict(status='Not Run'), public_release_approval=dict(status='Not Run'))
    manifest_path = output / 'release-manifest.json'
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    checksummed = sorted([output / record['path'] for record in files.values()] + [manifest_path] + list(target_reports.glob('*.json')))
    (output / 'SHA256SUMS.txt').write_text(''.join(file_record(path)['sha256'] + '  ' + path.relative_to(output).as_posix() + '\n' for path in checksummed), encoding='ascii')
    return result


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('check-samples')
    check.add_argument('--package', type=Path, default=ROOT / 'tests/data/distribution' / SAMPLE_NAME)
    check.add_argument('--output', type=Path, required=True)
    build = commands.add_parser('assemble')
    for name in ('candidate', 'reproduction', 'reports', 'output'):
        build.add_argument('--' + name, type=Path, required=True)
    build.add_argument('--samples', type=Path, default=ROOT / 'tests/data/distribution' / SAMPLE_NAME)
    build.add_argument('--run-id', type=int, required=True)
    build.add_argument('--channel', choices=('alpha', 'preview'), default='alpha')
    args = parser.parse_args()
    if args.command == 'check-samples':
        report = verify_samples(args.package)
        import subprocess
        report['source_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    else:
        result = assemble(args.candidate, args.samples, args.reproduction, args.reports, args.output, args.run_id, args.channel)
        print(result['artifact_name'])


if __name__ == '__main__':
    main()
