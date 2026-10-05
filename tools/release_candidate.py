"""Verify an exact CI candidate and optionally copy its assets to a draft Release."""

import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.public_reproduction import reproduction_members
from tools.package_identity import dependency_identity


REQUIRED_REPORTS = frozenset({
    'stdlib', 'public-science', 'node-helpers', 'extension-install', 'node-assets',
    'cold-original', 'cold-moved', 'qualification', 'sample-package', 'reproduction',
})
REQUIRED_FILES = frozenset({'extension', 'samples', 'reproduction'})
GATES = ('license_review', 'independent_alpha_installation', 'public_release_approval')
SHA256 = re.compile(r'[0-9a-f]{64}')
GIT_SHA = re.compile(r'[0-9a-f]{40}')
VERSION = re.compile(r'(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(value, *, root_file=False):
    require(isinstance(value, str) and value, 'Missing file path')
    path = PurePosixPath(value)
    require('\\' not in value and ':' not in value and not path.is_absolute(), 'Unsafe file path')
    require(all(part not in ('', '.', '..') for part in value.split('/')), 'Unsafe file path')
    require(not root_file or len(path.parts) == 1, 'Asset must be an artifact root file')
    return value


def digest_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def zip_members(archive):
    files = {}
    seen = set()
    for info in archive.infolist():
        name = info.filename[:-1] if info.is_dir() else info.filename
        safe_name(name)
        require(info.filename not in seen, 'Duplicate ZIP member: ' + info.filename)
        seen.add(info.filename)
        mode = info.external_attr >> 16
        require(mode & 0o170000 != 0o120000, 'ZIP symlink is not allowed: ' + name)
        require(not info.flag_bits & 1, 'Encrypted ZIP member: ' + name)
        if not info.is_dir():
            files[name] = info
    return files


def select_artifact(document, name, run_id):
    items = [item for item in document['artifacts'] if item['name'] == name]
    require(len(items) == 1, 'Expected exactly one candidate artifact')
    item = items[0]
    require(item.get('expired') is False, 'Candidate artifact is expired')
    require(isinstance(item.get('id'), int) and item['id'] > 0, 'Invalid artifact ID')
    if 'workflow_run' in item:
        require(str(item['workflow_run']['id']) == str(run_id), 'Artifact belongs to another run')
    return item


def verify_run(run, *, run_id, repository, commit, workflow_id):
    require(str(run.get('id')) == str(run_id), 'Candidate run ID mismatch')
    require(run.get('status') == 'completed' and run.get('conclusion') == 'success',
            'Candidate workflow did not complete successfully')
    require(run.get('head_sha') == commit, 'Candidate run head does not match tag')
    require(run.get('workflow_id') == workflow_id, 'Unexpected candidate workflow')
    require(run.get('event') in ('push', 'workflow_dispatch'), 'PR runs cannot be release candidates')
    require(run.get('repository', {}).get('full_name') == repository, 'Candidate repository mismatch')
    require(run.get('head_repository', {}).get('full_name') == repository,
            'Fork runs cannot be release candidates')


def verify_manifest(manifest, *, version, commit, product_tree, run_id):
    require(manifest.get('schema') == 'qcblender.release-candidate.v1', 'Unsupported candidate schema')
    require(VERSION.fullmatch(version) is not None and manifest.get('version') == version,
            'Candidate version does not match tag source')
    require(manifest.get('channel') == 'alpha', 'Expected Alpha candidate channel')
    require(manifest.get('source_commit') == commit, 'Candidate source commit mismatch')
    require(manifest.get('product_tree') == product_tree, 'Candidate product tree mismatch')
    require(str(manifest.get('candidate_run_id')) == str(run_id), 'Manifest candidate run mismatch')
    require(manifest.get('workflow') == 'extension-package.yml', 'Unexpected manifest workflow')
    expected_platform = {'os': 'windows', 'architecture': 'x64', 'blender': '5.1.1',
                         'python': '3.13', 'numpy': '2.3.4'}
    require(manifest.get('platform') == expected_platform, 'Unsupported candidate platform')
    expected_name = f'qcblender-candidate-{version}-{commit}'
    require(manifest.get('artifact_name') == expected_name, 'Candidate artifact name mismatch')
    require(isinstance(manifest.get('dependencies'), dict), 'Candidate dependency identity is missing')
    require(set(manifest.get('files', {})) == REQUIRED_FILES, 'Candidate file roles are incomplete')
    require(set(manifest.get('reports', {})) == REQUIRED_REPORTS, 'Candidate reports are incomplete')
    paths = []
    for role, entry in manifest['files'].items():
        paths.append(safe_name(entry['path'], root_file=True))
        require(entry['path'].endswith('.zip'), 'Candidate asset must be a ZIP: ' + role)
    require(manifest['files']['extension']['path'] == f'qcblender-{version}.zip',
            'Extension asset name does not match manifest version')
    for key, entry in manifest['reports'].items():
        path = safe_name(entry['path'])
        require(path.startswith('reports/') and path.endswith('.json'), 'Invalid report path: ' + key)
        require(entry.get('status') == 'Passed', 'Technical report is not Passed: ' + key)
        paths.append(path)
    require(len(paths) == len(set(paths)), 'Candidate paths are not unique')
    for entry in list(manifest['files'].values()) + list(manifest['reports'].values()):
        require(type(entry.get('bytes')) is int and entry['bytes'] > 0, 'Invalid candidate file size')
        require(isinstance(entry.get('sha256'), str) and SHA256.fullmatch(entry['sha256']),
                'Invalid candidate file digest')
    for gate in GATES:
        require(manifest.get(gate, {}).get('status') in ('Passed', 'Failed', 'Not Run'),
                'Missing release gate: ' + gate)


def parse_checksums(text):
    checksums = {}
    for line in text.splitlines():
        if not line:
            continue
        require(len(line) > 66 and SHA256.fullmatch(line[:64]) and line[64:66] == '  ',
                'Invalid SHA256SUMS entry')
        name = safe_name(line[66:])
        require(name not in checksums, 'Duplicate SHA256SUMS entry')
        checksums[name] = line[:64]
    return checksums


def unpack_candidate(bundle, destination, *, version, commit, product_tree, run_id):
    with zipfile.ZipFile(bundle) as archive:
        members = zip_members(archive)
        require('release-manifest.json' in members, 'Candidate manifest is missing')
        manifest = json.loads(archive.read('release-manifest.json'))
        verify_manifest(manifest, version=version, commit=commit, product_tree=product_tree, run_id=run_id)
        entries = list(manifest['files'].values()) + list(manifest['reports'].values())
        expected = {entry['path'] for entry in entries} | {'release-manifest.json', 'SHA256SUMS.txt'}
        require(set(members) == expected, 'Candidate bundle contains missing or unexpected members')
        require(all(any(name.startswith(info.filename) for name in expected)
                    for info in archive.infolist() if info.is_dir()), 'Unexpected bundle directory')
        sums = parse_checksums(archive.read('SHA256SUMS.txt').decode('utf-8'))
        require(set(sums) == expected - {'SHA256SUMS.txt'}, 'SHA256SUMS coverage is incomplete')
        for entry in entries:
            require(members[entry['path']].file_size == entry['bytes'], 'Candidate file size mismatch')
            require(sums[entry['path']] == entry['sha256'], 'Manifest/checksum digest mismatch')
        destination.mkdir(parents=True, exist_ok=True)
        for name, info in members.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            require(target.resolve().is_relative_to(destination.resolve()), 'Extraction path escapes candidate directory')
            with archive.open(info) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output, length=65536)
            if name in sums:
                require(digest_file(target) == sums[name], 'Candidate content digest mismatch: ' + name)
        verify_reports(manifest, destination)
        return manifest


def verify_reports(manifest, root):
    extension_sha = manifest['files']['extension']['sha256']
    for key, entry in manifest['reports'].items():
        report = json.loads((root / entry['path']).read_text(encoding='utf-8'))
        require(report.get('status') == 'Passed', 'Technical report failed: ' + key)
        require(report.get('source_commit') == manifest['source_commit'], 'Report source mismatch: ' + key)
        if 'candidate_sha256' in report:
            require(report['candidate_sha256'] == extension_sha, 'Report candidate mismatch: ' + key)
        if key in ('stdlib', 'public-science'):
            suite = 'stdlib' if key == 'stdlib' else 'public-core'
            require(report.get('suite') == suite and report.get('skipped') == 0 and
                    report.get('errors') == 0 and report.get('failures') == 0 and
                    type(report.get('tests')) is int and report['tests'] > 0,
                    'Required test qualification is incomplete: ' + key)
        if key in ('cold-original', 'cold-moved'):
            require(report.get('cold_open') == 'Passed', 'Cold-open qualification is incomplete')
        if key == 'qualification':
            require(report.get('sha256') == extension_sha, 'Qualification belongs to another ZIP')
            require(report.get('backend') == manifest.get('dependencies', {}).get('backend'),
                    'Qualification backend identity differs from candidate')
        if key in ('extension-install', 'node-assets', 'cold-original', 'cold-moved', 'reproduction'):
            require(report.get('candidate_sha256') == extension_sha, 'Report candidate mismatch: ' + key)


def verify_extension(path, source, dependencies):
    with zipfile.ZipFile(path) as archive:
        members = zip_members(archive)
        expected_python = {name for name in source if name.endswith('.py') and name.startswith('qcblender/')}
        actual_python = {name for name in members if name.endswith('.py')}
        require(actual_python == {name.removeprefix('qcblender/') for name in expected_python},
                'Extension Python inventory differs from tag')
        for name in expected_python:
            require(archive.read(name.removeprefix('qcblender/')) == source[name],
                    'Extension Python source differs from tag: ' + name)
        for name in ('dependencies.lock.json', 'science-sources.lock.json', 'LICENSE', 'THIRD_PARTY.md'):
            require(archive.read(name) == source[name], 'Extension source material differs from tag: ' + name)
        tracked = tomllib.loads(source['qcblender/blender_manifest.toml'].decode('utf-8'))
        packaged = tomllib.loads(archive.read('blender_manifest.toml').decode('utf-8'))
        require({key: value for key, value in packaged.items() if key != 'wheels'} ==
                {key: value for key, value in tracked.items() if key != 'wheels'},
                'Extension manifest differs from tag')
        backend = json.loads(archive.read('backend-wheel.json'))
        require(backend.get('source_lock') == 'science-sources.lock.json', 'Backend source lock is missing')
        expected_dependencies = dependency_identity(source['dependencies.lock.json'],
                                                    source['science-sources.lock.json'], backend)
        require(dependencies == expected_dependencies,
                'Candidate dependency identity differs from tag locks or bundled backend')
        wheels = json.loads(source['dependencies.lock.json'])['packages'] + [backend]
        expected_wheels = {'wheels/' + entry['filename'] for entry in wheels}
        expected_members = {name.removeprefix('qcblender/') for name in source if name.startswith('qcblender/')}
        expected_members |= {'dependencies.lock.json', 'science-sources.lock.json', 'LICENSE', 'THIRD_PARTY.md',
                             'backend-wheel.json', 'assets/nodes.blend', 'assets/blender_assets.cats.txt'} | expected_wheels
        require(set(members) == expected_members, 'Extension contains missing or unexpected members')
        for name in source:
            if name.startswith('qcblender/') and not name.endswith(('.py', '/blender_manifest.toml')):
                require(archive.read(name.removeprefix('qcblender/')) == source[name],
                        'Extension source asset differs from tag: ' + name)
        require({name for name in members if name.endswith('.whl')} == expected_wheels,
                'Extension wheel inventory differs from locks')
        require(set(packaged['wheels']) == {'./' + name for name in expected_wheels},
                'Extension manifest wheel list differs from locks')
        for entry in wheels:
            require(hashlib.sha256(archive.read('wheels/' + entry['filename'])).hexdigest() == entry['sha256'],
                    'Extension wheel checksum mismatch: ' + entry['filename'])
        with zipfile.ZipFile(io.BytesIO(archive.read('wheels/' + backend['filename']))) as wheel:
            names = zip_members(wheel)
            require('gbasis/QCBLENDER_BUILD.md' in names, 'Backend build notice is missing')
            require(not any(name.endswith(('.pyd', '.dll', '.so', '/libcint.py')) for name in names),
                    'Unexpected native GBasis component')


def verify_release_gates(record, manifest, artifact_id, evidence_root):
    identity = {
        'schema': 'qcblender.release-gates.v1',
        'candidate_run_id': manifest['candidate_run_id'],
        'artifact_id': artifact_id,
        'source_commit': manifest['source_commit'],
        'extension_sha256': manifest['files']['extension']['sha256'],
    }
    require(all(record.get(key) == value for key, value in identity.items()), 'Release gate identity mismatch')
    for key in GATES:
        gate = record.get(key, {})
        require(gate.get('status') in ('Passed', 'Failed', 'Not Run'), 'Missing release gate result: ' + key)
        if gate['status'] == 'Passed':
            require(isinstance(gate.get('reviewer'), str) and gate['reviewer'].strip(),
                    'Passed gate has no actual reviewer: ' + key)
            require(isinstance(gate.get('notes'), str) and gate['notes'].strip(),
                    'Passed gate has no review notes: ' + key)
            require(isinstance(gate.get('reviewed_at'), str), 'Passed gate has no review date: ' + key)
            datetime.fromisoformat(gate['reviewed_at'])
            require(isinstance(gate.get('evidence'), list) and gate['evidence'],
                    'Passed gate has no evidence: ' + key)
            for entry in gate['evidence']:
                path = (evidence_root / safe_name(entry['path'])).resolve(strict=True)
                require(path.is_relative_to(evidence_root.resolve()), 'Gate evidence escapes its record directory')
                require(SHA256.fullmatch(entry['sha256']) and digest_file(path) == entry['sha256'],
                        'Gate evidence checksum mismatch: ' + key)
    return {key: record[key] for key in GATES}


def verify_public_materials(manifest, root, source):
    samples = json.loads(source['docs/v1-acceptance/tutorial-samples.json'])
    delivery = json.loads(source['docs/acceptance/tutorial-sample-delivery.json'])['package']
    sample_entry = manifest['files']['samples']
    require(all(sample_entry[key] == delivery[key] for key in ('bytes', 'sha256')),
            'Public sample package differs from tag delivery record')
    included = {entry['archive_path']: entry for entry in samples['files'].values()
                if entry['distribution'] == 'included'}
    with zipfile.ZipFile(root / sample_entry['path']) as archive:
        members = zip_members(archive)
        require(set(members) == set(included) | {'LICENSE', 'NOTICE.md', 'tutorial-samples.json'},
                'Public sample ZIP has unlisted inputs')
        require(json.loads(archive.read('tutorial-samples.json')) == samples,
                'Public sample source manifest differs from tag')
        for name, entry in included.items():
            raw = archive.read(name)
            require(entry['license'] == 'CC-BY-4.0' and len(raw) == entry['bytes'] and
                    hashlib.sha256(raw).hexdigest() == entry['sha256'],
                    'Public input license or digest mismatch: ' + name)
    reproduction = json.loads((root / manifest['reports']['reproduction']['path']).read_text(encoding='utf-8'))
    require(reproduction.get('cold_open') == 'Passed' and reproduction.get('portable_saved') is True and
            reproduction.get('source_sha256') == samples['files']['P01-o2-uhf']['sha256'],
            'Public reproduction lacks its P01 identity or portable cold-open check')
    allowed_sources = {entry['sha256'] for entry in included.values()}
    with zipfile.ZipFile(root / manifest['files']['reproduction']['path']) as archive:
        members = zip_members(archive)
        reproduction_members(archive.open, members, allowed_sources)


class GitSource:
    def __init__(self, root):
        self.root = root

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root).strip()

    def read(self, commit, path):
        return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=self.root)

    def snapshot(self, tag, default_branch):
        require(re.fullmatch(r'v' + VERSION.pattern, tag) is not None, 'Invalid Alpha release tag')
        require(self.git('cat-file', '-t', 'refs/tags/' + tag) == b'tag', 'Release tag must be annotated')
        tag_headers = self.git('cat-file', '-p', 'refs/tags/' + tag).split(b'\n\n', 1)[0].splitlines()
        require(b'type commit' in tag_headers, 'Annotated release tag must point directly to a commit')
        commit = self.git('rev-list', '-n', '1', 'refs/tags/' + tag).decode('ascii')
        require(GIT_SHA.fullmatch(commit), 'Invalid tag commit')
        ancestry = subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'origin/' + default_branch],
                                  cwd=self.root, check=False, capture_output=True)
        require(ancestry.returncode == 0, 'Release tag is not reachable from the default branch')
        product_tree = self.git('rev-parse', commit + ':qcblender').decode('ascii')
        names = self.git('ls-tree', '-r', '--name-only', '-z', commit, '--', 'qcblender').split(b'\0')
        paths = [name.decode('utf-8') for name in names if name]
        paths += ['qcblender/blender_manifest.toml', 'dependencies.lock.json', 'science-sources.lock.json',
                  'LICENSE', 'THIRD_PARTY.md', 'docs/v1-acceptance/tutorial-samples.json',
                  'docs/acceptance/tutorial-sample-delivery.json']
        source = {path: self.read(commit, path) for path in paths}
        version = tomllib.loads(source['qcblender/blender_manifest.toml'].decode('utf-8'))['version']
        require(tag == 'v' + version, 'Release tag does not match manifest version')
        return version, commit, product_tree, source


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        redirected = super().redirect_request(request, response, code, message, headers, new_url)
        require(urllib.parse.urlsplit(new_url).scheme == 'https', 'Artifact redirect must use HTTPS')
        if redirected and urllib.parse.urlsplit(request.full_url).hostname != urllib.parse.urlsplit(new_url).hostname:
            redirected.remove_header('Authorization')
        return redirected


class GitHub:
    def __init__(self, repository, token):
        require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository), 'Invalid repository')
        require(token, 'GH_TOKEN is required')
        self.repository = repository
        self.token = token
        self.opener = urllib.request.build_opener(SafeRedirect())

    def request(self, path, *, method='GET', body=None, headers=None):
        url = 'https://api.github.com/repos/' + self.repository + '/' + path
        values = {'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + self.token,
                  'User-Agent': 'QCBlender-release'}
        values.update(headers or {})
        request = urllib.request.Request(url, data=body, method=method, headers=values)
        return self.opener.open(request, timeout=60)

    def get_json(self, path):
        with self.request(path) as response:
            return json.load(response)

    def all_artifacts(self, run_id):
        items = []
        page = 1
        while True:
            current = self.get_json(f'actions/runs/{run_id}/artifacts?per_page=100&page={page}')['artifacts']
            items.extend(current)
            if len(current) < 100:
                return {'artifacts': items}
            page += 1

    def download(self, artifact_id, target):
        with self.request(f'actions/artifacts/{artifact_id}/zip') as response, target.open('wb') as output:
            shutil.copyfileobj(response, output, length=65536)

    def existing_release(self, tag):
        matches = []
        page = 1
        while True:
            items = self.get_json(f'releases?per_page=100&page={page}')
            matches.extend(item for item in items if item['tag_name'] == tag)
            if len(items) < 100:
                require(len(matches) <= 1, 'Multiple Releases exist for tag')
                return matches[0] if matches else None
            page += 1

    def verify_remote_tag(self, tag, commit):
        reference = self.get_json('git/ref/tags/' + tag)
        require(reference.get('object', {}).get('type') == 'tag', 'Remote tag is no longer annotated')
        annotated = self.get_json('git/tags/' + reference['object']['sha'])
        require(annotated.get('object', {}).get('type') == 'commit' and
                annotated['object']['sha'] == commit, 'Remote release tag moved after verification')

    def create_draft(self, tag, version, notes):
        body = json.dumps({'tag_name': tag, 'name': f'QCBlender {version} Alpha', 'draft': True,
                           'prerelease': True, 'make_latest': 'false', 'body': notes}).encode('utf-8')
        with self.request('releases', method='POST', body=body, headers={'Content-Type': 'application/json'}) as response:
            return json.load(response)

    def upload(self, release, path):
        base = release['upload_url'].split('{', 1)[0]
        parsed = urllib.parse.urlsplit(base)
        require(parsed.scheme == 'https' and parsed.hostname == 'uploads.github.com' and
                parsed.port in (None, 443) and not parsed.username, 'Unexpected asset upload URL')
        url = base + '?' + urllib.parse.urlencode({'name': path.name})
        def chunks():
            with path.open('rb') as stream:
                while block := stream.read(65536):
                    yield block
        request = urllib.request.Request(url, data=chunks(), method='POST', headers={
            'Authorization': 'Bearer ' + self.token, 'User-Agent': 'QCBlender-release',
            'Content-Type': 'application/octet-stream', 'Content-Length': str(path.stat().st_size),
        })
        with self.opener.open(request, timeout=60) as response:
            return json.load(response)


def promote_draft(client, tag, version, assets, notes):
    release = client.existing_release(tag)
    if release is None:
        release = client.create_draft(tag, version, notes)
    require(release.get('tag_name') == tag and release.get('prerelease') is True,
            'Existing Release has a different identity or channel')
    expected = {path.name: 'sha256:' + digest_file(path) for path in assets}
    existing = {entry['name']: entry for entry in release.get('assets', [])}
    require(len(existing) == len(release.get('assets', [])), 'Duplicate Release asset names')
    require(set(existing) <= set(expected), 'Unexpected Release asset')
    for name, asset in existing.items():
        require(asset.get('digest') == expected[name] and asset.get('state') == 'uploaded',
                'Existing Release asset digest or upload state differs: ' + name)
    if release.get('draft') is False:
        require(set(existing) == set(expected), 'Published Release is incomplete; it cannot be changed')
        return {'status': 'Already Published', 'release_id': release['id']}
    require(release.get('draft') is True, 'Unexpected Release draft state')
    for path in assets:
        if path.name not in existing:
            asset = client.upload(release, path)
            require(asset.get('name') == path.name and asset.get('digest') == expected[path.name] and
                    asset.get('state') == 'uploaded', 'Uploaded asset digest mismatch: ' + path.name)
    return {'status': 'Draft', 'release_id': release['id']}


def main():
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--candidate-run-id', required=True, type=int)
    parser.add_argument('--default-branch', default='main')
    parser.add_argument('--workflow-ref', required=True)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/release-verification'))
    parser.add_argument('--gates-record', type=Path)
    parser.add_argument('--notes-file', type=Path)
    parser.add_argument('--require-draft-ready', action='store_true')
    parser.add_argument('--create-draft', action='store_true', help='Explicitly write a draft; never publish it')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / 'verification.json'
    report_path.write_text(json.dumps({'status': 'Failed', 'scope': 'Release verification',
                                      'tag': args.tag, 'candidate_run_id': args.candidate_run_id,
                                      'error': 'Verification has not completed'}) + '\n', encoding='utf-8')
    require(args.workflow_ref == 'refs/heads/' + args.default_branch, 'Release workflow must run from default branch')
    require(args.candidate_run_id > 0, 'Invalid candidate run ID')
    root = Path(__file__).resolve().parents[1]
    git = GitSource(root)
    version, commit, product_tree, source = git.snapshot(args.tag, args.default_branch)
    client = GitHub(args.repository, os.environ.get('GH_TOKEN', ''))
    workflow = client.get_json('actions/workflows/extension-package.yml')
    require(workflow.get('path') == '.github/workflows/extension-package.yml', 'Unexpected workflow path')
    run = client.get_json(f'actions/runs/{args.candidate_run_id}')
    verify_run(run, run_id=args.candidate_run_id, repository=args.repository, commit=commit,
               workflow_id=workflow['id'])
    name = f'qcblender-candidate-{version}-{commit}'
    artifact = select_artifact(client.all_artifacts(args.candidate_run_id), name, args.candidate_run_id)
    bundle = args.output_dir / 'candidate-bundle.zip'
    client.download(artifact['id'], bundle)
    unpacked = args.output_dir / 'candidate'
    manifest = unpack_candidate(bundle, unpacked, version=version, commit=commit,
                                product_tree=product_tree, run_id=args.candidate_run_id)
    verify_extension(unpacked / manifest['files']['extension']['path'], source, manifest.get('dependencies'))
    verify_public_materials(manifest, unpacked, source)
    gates = {key: manifest[key] for key in GATES}
    if args.gates_record:
        require(args.gates_record.resolve(strict=True).is_relative_to(root),
                'Release gate record must be inside the checkout')
        record = json.loads(args.gates_record.read_text(encoding='utf-8'))
        gates = verify_release_gates(record, manifest, artifact['id'], args.gates_record.parent)
    draft_ready = args.gates_record is not None and gates['license_review']['status'] == 'Passed'
    assets = [unpacked / manifest['files'][role]['path'] for role in sorted(REQUIRED_FILES)]
    assets += [unpacked / 'release-manifest.json', unpacked / 'SHA256SUMS.txt']
    report = {'status': 'Passed', 'scope': 'Exact candidate technical verification',
              'schema': 'qcblender.release-verification.v1', 'source_commit': commit,
              'product_tree': product_tree, 'tag': args.tag,
              'candidate_run_id': args.candidate_run_id, 'artifact_id': artifact['id'],
              'extension_sha256': manifest['files']['extension']['sha256'],
              'assets': {path.name: {'bytes': path.stat().st_size, 'sha256': digest_file(path)} for path in assets},
              'dry_run': not args.create_draft, 'draft_readiness': 'Passed' if draft_ready else 'Failed',
              'draft_blocker': None if draft_ready else 'Verified license review record is required',
              'gates': gates, 'release': {'status': 'Not Run'}}
    (args.output_dir / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    if args.require_draft_ready or args.create_draft:
        require(draft_ready, report['draft_blocker'])
    if args.create_draft:
        try:
            require(git.git('rev-list', '-n', '1', 'refs/tags/' + args.tag).decode('ascii') == commit,
                    'Tag changed after verification')
            client.verify_remote_tag(args.tag, commit)
            notes = args.notes_file.read_text(encoding='utf-8') if args.notes_file else (
                f'Alpha preview for Windows x64 / Blender 5.1.1.\n\n'
                f'Candidate commit: `{commit}`. Independent scientific acceptance remains pending.\n'
                f'Install the attached `qcblender-{version}.zip`; compare its SHA-256 to its entry '
                f'in SHA256SUMS.txt before installation.\n')
            report['release'] = promote_draft(client, args.tag, version, assets, notes)
        except (OSError, ValueError) as error:
            report['release'] = {'status': 'Failed', 'error': str(error)}
            report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            raise
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
