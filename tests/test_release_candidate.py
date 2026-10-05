import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import urllib.request
import zipfile

from tools import release_candidate as release


ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = ROOT / 'outputs' / 'release-verifier-tests'
COMMIT = 'a' * 40
TREE = 'b' * 40


def sha(data):
    return hashlib.sha256(data).hexdigest()


def zipped(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return stream.getvalue()


def fixture():
    backend_bytes = zipped({'gbasis/__init__.py': b'', 'gbasis/QCBLENDER_BUILD.md': b'Build notice'})
    dependency = {'name': 'locked', 'version': '1.0.0', 'filename': 'locked-py3-none-any.whl',
                  'sha256': sha(b'locked dependency')}
    backend = {'name': 'qc-gbasis', 'version': '0.1.0', 'filename': 'qc_gbasis-fixture.whl', 'sha256': sha(backend_bytes),
               'source_lock': 'science-sources.lock.json'}
    source_manifest = b'id="qcblender"\nversion="0.1.0"\nplatforms=["windows-x64"]\nwheels=[]\n'
    source = {'qcblender/__init__.py': b'VALUE = 1\n', 'qcblender/blender_manifest.toml': source_manifest,
              'dependencies.lock.json': json.dumps({'packages': [dependency],
                                                    'host_provided': {'numpy': '2.3.4', 'openvdb': '13.0.0'}}).encode(),
              'science-sources.lock.json': b'[{"commit":"source"}]', 'LICENSE': b'GPL fixture',
              'THIRD_PARTY.md': b'Unresolved upstream statement differences'}
    extension_entries = {name.removeprefix('qcblender/'): value for name, value in source.items()}
    extension_entries['blender_manifest.toml'] = source_manifest.replace(
        b'wheels=[]', b'wheels=["./wheels/locked-py3-none-any.whl", "./wheels/qc_gbasis-fixture.whl"]')
    extension_entries.update({'backend-wheel.json': json.dumps(backend).encode(),
                              'wheels/locked-py3-none-any.whl': b'locked dependency',
                              'wheels/qc_gbasis-fixture.whl': backend_bytes,
                              'assets/nodes.blend': b'Synthetic generated node asset',
                              'assets/blender_assets.cats.txt': b'Synthetic generated catalog'})
    public_input = b'public scientific fixture'
    samples = {'files': {'P01-o2-uhf': {'archive_path': 'P01/fixture.fchk', 'distribution': 'included',
                                      'license': 'CC-BY-4.0', 'bytes': len(public_input),
                                      'sha256': sha(public_input)}}}
    samples_bytes = zipped({'P01/fixture.fchk': public_input, 'LICENSE': b'CC BY fixture',
                            'NOTICE.md': b'Attribution fixture',
                            'tutorial-samples.json': json.dumps(samples).encode()})
    array = b'Synthetic array bytes; array decoding belongs to science qualification'
    dataset = json.dumps({'format': 'qcblender.project', 'schema': '0.1',
                          'metadata': {'source': {'sha256': sha(public_input)}},
                          'arrays': {'positions': {'path': 'arrays/' + sha(array) + '.npy',
                                                  'sha256': sha(array)}}}).encode()
    dataset_dir = 'datasets/' + sha(dataset)
    reproduction_bytes = zipped({'README.md': b'public fixture instructions', 'example.blend': b'blend fixture',
                                 'example.png': b'png fixture', 'example.qcdata/manifest.json': json.dumps({
                                     'format': 'qcblender.scene', 'schema': '0.1', 'datasets': [dataset_dir]}).encode(),
                                 'example.qcdata/' + dataset_dir + '/manifest.json': dataset,
                                 'example.qcdata/' + dataset_dir + '/arrays/' + sha(array) + '.npy': array})
    data = {'qcblender-0.1.0.zip': zipped(extension_entries),
            'samples-v2.zip': samples_bytes, 'reproduction.zip': reproduction_bytes}
    source['docs/v1-acceptance/tutorial-samples.json'] = json.dumps(samples).encode()
    source['docs/acceptance/tutorial-sample-delivery.json'] = json.dumps({
        'package': {'bytes': len(samples_bytes), 'sha256': sha(samples_bytes)}}).encode()
    manifest = {'schema': 'qcblender.release-candidate.v1', 'version': '0.1.0', 'channel': 'alpha',
                'source_commit': COMMIT, 'product_tree': TREE, 'candidate_run_id': 42,
                'workflow': 'extension-package.yml',
                'platform': {'os': 'windows', 'architecture': 'x64', 'blender': '5.1.1',
                             'python': '3.13', 'numpy': '2.3.4'},
                'artifact_name': f'qcblender-candidate-0.1.0-{COMMIT}', 'files': {}, 'reports': {}}
    manifest['dependencies'] = release.dependency_identity(source['dependencies.lock.json'],
                                                          source['science-sources.lock.json'], backend)
    for role, name in {'extension': 'qcblender-0.1.0.zip', 'samples': 'samples-v2.zip',
                       'reproduction': 'reproduction.zip'}.items():
        manifest['files'][role] = {'path': name, 'bytes': len(data[name]), 'sha256': sha(data[name])}
    for name in release.REQUIRED_REPORTS:
        report = {'status': 'Passed', 'source_commit': COMMIT}
        if name in ('stdlib', 'public-science'):
            report.update(suite='public-core' if name == 'public-science' else 'stdlib',
                          tests=60, skipped=0, errors=0, failures=0)
        if name in ('cold-original', 'cold-moved'):
            report['cold_open'] = 'Passed'
        if name == 'qualification':
            report['sha256'] = sha(data['qcblender-0.1.0.zip'])
            report['backend'] = backend
        if name in ('extension-install', 'node-assets', 'cold-original', 'cold-moved', 'reproduction'):
            report['candidate_sha256'] = sha(data['qcblender-0.1.0.zip'])
        if name == 'reproduction':
            report.update(cold_open='Passed', portable_saved=True, source_sha256=sha(public_input))
        path = f'reports/{name}.json'
        data[path] = json.dumps(report).encode()
        manifest['reports'][name] = {'path': path, 'bytes': len(data[path]), 'sha256': sha(data[path]),
                                     'status': 'Passed'}
    for gate in release.GATES:
        manifest[gate] = {'status': 'Not Run', 'blocker': 'Actual review is pending'}
    return manifest, data, source


def bundle_bytes(manifest, data):
    entries = dict(data)
    entries['release-manifest.json'] = json.dumps(manifest).encode()
    entries['SHA256SUMS.txt'] = ''.join(f'{sha(value)}  {name}\n' for name, value in entries.items()).encode()
    return zipped(entries)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.manifest, self.data, self.source = fixture()

    def unpack(self, *, raw=None):
        bundle = self.root / 'bundle.zip'
        bundle.write_bytes(raw if raw is not None else bundle_bytes(self.manifest, self.data))
        return release.unpack_candidate(bundle, self.root / 'candidate', version='0.1.0',
                                        commit=COMMIT, product_tree=TREE, run_id=42)

    def run_record(self):
        return {'id': 42, 'status': 'completed', 'conclusion': 'success', 'head_sha': COMMIT,
                'workflow_id': 17, 'event': 'push', 'repository': {'full_name': 'owner/repo'},
                'head_repository': {'full_name': 'owner/repo'}}

    def test_exact_bundle_and_tag_source_pass_without_changing_asset_bytes(self):
        result = self.unpack()
        target = self.root / 'candidate' / result['files']['extension']['path']
        self.assertEqual(target.read_bytes(), self.data['qcblender-0.1.0.zip'])
        release.verify_extension(target, self.source, result['dependencies'])
        release.verify_public_materials(result, self.root / 'candidate', self.source)

    def test_wrong_candidate_identity_and_incomplete_reports_are_rejected(self):
        for key, value in [('version', '0.1.1'), ('source_commit', 'c' * 40), ('product_tree', 'c' * 40),
                           ('candidate_run_id', 43), ('workflow', 'other.yml'), ('channel', 'stable')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                changed = copy.deepcopy(self.manifest)
                changed[key] = value
                release.verify_manifest(changed, version='0.1.0', commit=COMMIT, product_tree=TREE, run_id=42)
        del self.manifest['reports']['cold-moved']
        with self.assertRaisesRegex(ValueError, 'reports are incomplete'):
            self.unpack()

    def test_malformed_file_sizes_and_paths_are_rejected(self):
        for value in (True, -1, '1'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.manifest['files']['samples']['bytes'] = value
                self.unpack()
        for path in ('../escape.zip', 'C:/escape.zip', 'reports//x.json', '/absolute.zip'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                release.safe_name(path)

    def test_changed_candidate_content_is_rejected_even_with_unchanged_metadata(self):
        raw = bundle_bytes(self.manifest, self.data)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        entries['samples-v2.zip'] = bytes(reversed(entries['samples-v2.zip']))
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            self.unpack(raw=zipped(entries))

    def test_extra_and_duplicate_bundle_members_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unexpected members'):
            self.unpack(raw=bundle_bytes(self.manifest, {**self.data, 'extra.bin': b'extra'}))
        stream = io.BytesIO(bundle_bytes(self.manifest, self.data))
        with zipfile.ZipFile(stream, 'a') as archive:
            with self.assertWarns(UserWarning):
                archive.writestr('release-manifest.json', b'{}')
        with self.assertRaisesRegex(ValueError, 'Duplicate ZIP member'):
            self.unpack(raw=stream.getvalue())

    def test_missing_and_duplicate_checksum_entries_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            release.parse_checksums('a' * 64 + '  x.zip\n' + 'a' * 64 + '  x.zip\n')
        raw = bundle_bytes(self.manifest, self.data)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        entries['SHA256SUMS.txt'] = b''
        with self.assertRaisesRegex(ValueError, 'coverage is incomplete'):
            self.unpack(raw=zipped(entries))

    def test_unverified_public_sample_or_reproduction_input_is_rejected(self):
        self.unpack()
        manifest = copy.deepcopy(self.manifest)
        root = self.root / 'candidate'
        path = root / manifest['files']['reproduction']['path']
        with zipfile.ZipFile(path) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        dataset_path = next(name for name in entries if '/datasets/' in name and name.endswith('/manifest.json'))
        dataset = json.loads(entries[dataset_path])
        dataset['metadata']['source']['sha256'] = 'c' * 64
        changed = json.dumps(dataset).encode()
        previous_prefix = dataset_path.removesuffix('manifest.json')
        new_directory = 'datasets/' + sha(changed)
        new_prefix = 'example.qcdata/' + new_directory + '/'
        entries = {name.replace(previous_prefix, new_prefix): raw for name, raw in entries.items()}
        entries[new_prefix + 'manifest.json'] = changed
        scene = json.loads(entries['example.qcdata/manifest.json'])
        scene['datasets'] = [new_directory]
        entries['example.qcdata/manifest.json'] = json.dumps(scene).encode()
        path.write_bytes(zipped(entries))
        with self.assertRaisesRegex(ValueError, 'unverified.*input'):
            release.verify_public_materials(manifest, root, self.source)
        path = root / manifest['files']['samples']['path']
        with zipfile.ZipFile(path) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        entries['P02/unverified.out'] = b'unverified input'
        path.write_bytes(zipped(entries))
        with self.assertRaisesRegex(ValueError, 'unlisted inputs'):
            release.verify_public_materials(manifest, root, self.source)

    def test_extra_unknown_license_files_in_sidecar_and_extension_are_rejected(self):
        self.unpack()
        root = self.root / 'candidate'
        for extra in ('example.qcdata/P02-unknown-license.fchk',
                      'example.qcdata/datasets/unreferenced/manifest.json'):
            with self.subTest(extra=extra):
                with zipfile.ZipFile(io.BytesIO(self.data['reproduction.zip'])) as archive:
                    entries = {name: archive.read(name) for name in archive.namelist()}
                entries[extra] = b'Unknown license fixture'
                (root / 'reproduction.zip').write_bytes(zipped(entries))
                with self.assertRaisesRegex(ValueError, 'unlisted material'):
                    release.verify_public_materials(self.manifest, root, self.source)
        with zipfile.ZipFile(io.BytesIO(self.data['qcblender-0.1.0.zip'])) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        entries['P02/unknown-license.fchk'] = b'Unknown license fixture'
        target = root / 'extra-extension.zip'
        target.write_bytes(zipped(entries))
        with self.assertRaisesRegex(ValueError, 'unexpected members'):
            release.verify_extension(target, self.source, self.manifest['dependencies'])

    def test_required_science_skip_and_cold_open_failure_are_rejected(self):
        for key, changes in [('public-science', {'skipped': 1}),
                             ('cold-moved', {'cold_open': 'Not Run'}),
                             ('qualification', {'sha256': 'c' * 64})]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                path = self.manifest['reports'][key]['path']
                previous = self.data[path]
                report = json.loads(previous)
                report.update(changes)
                self.data[path] = json.dumps(report).encode()
                entry = self.manifest['reports'][key]
                entry.update(bytes=len(self.data[path]), sha256=sha(self.data[path]))
                try:
                    self.unpack()
                finally:
                    self.data[path] = previous
                    entry.update(bytes=len(previous), sha256=sha(previous))

    def test_failed_fork_pr_or_wrong_workflow_run_is_rejected(self):
        for key, value in [('id', 43), ('head_sha', 'c' * 40), ('conclusion', 'failure'),
                           ('event', 'pull_request'), ('workflow_id', 18),
                           ('head_repository', {'full_name': 'fork/repo'})]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                record = self.run_record()
                record[key] = value
                release.verify_run(record, run_id=42, repository='owner/repo', commit=COMMIT, workflow_id=17)

    def test_expired_duplicate_and_wrong_run_artifacts_are_rejected(self):
        artifact = {'id': 100, 'name': self.manifest['artifact_name'], 'expired': False,
                    'workflow_run': {'id': 42}}
        self.assertEqual(release.select_artifact({'artifacts': [artifact]}, artifact['name'], 42)['id'], 100)
        for items in ([], [artifact, artifact], [{**artifact, 'expired': True}],
                      [{**artifact, 'workflow_run': {'id': 43}}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                release.select_artifact({'artifacts': items}, artifact['name'], 42)

    def test_changed_python_or_wheel_is_rejected_by_independent_source_check(self):
        for name in ('__init__.py', 'wheels/locked-py3-none-any.whl'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                with zipfile.ZipFile(io.BytesIO(self.data['qcblender-0.1.0.zip'])) as archive:
                    entries = {path: archive.read(path) for path in archive.namelist()}
                entries[name] = b'changed'
                path = self.root / 'changed.zip'
                path.write_bytes(zipped(entries))
                release.verify_extension(path, self.source, self.manifest['dependencies'])

    def test_changed_dependency_identity_or_qualification_backend_is_rejected(self):
        self.unpack()
        path = self.root / 'candidate' / 'qcblender-0.1.0.zip'
        for key, value in [('lock_sha256', 'c' * 64), ('source_lock_sha256', 'c' * 64),
                           ('host_provided', {'numpy': 'different'}), ('bundled_wheels', [])]:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'dependency identity'):
                changed = copy.deepcopy(self.manifest['dependencies'])
                changed[key] = value
                release.verify_extension(path, self.source, changed)
        manifest = copy.deepcopy(self.manifest)
        manifest['dependencies']['backend']['version'] = 'different'
        with self.assertRaisesRegex(ValueError, 'backend identity'):
            release.verify_reports(manifest, self.root / 'candidate')

    def gate_record(self):
        return {'schema': 'qcblender.release-gates.v1', 'candidate_run_id': 42, 'artifact_id': 100,
                'source_commit': COMMIT, 'extension_sha256': self.manifest['files']['extension']['sha256'],
                **{gate: {'status': 'Not Run'} for gate in release.GATES}}

    def test_gate_records_require_exact_candidate_and_real_evidence_fields(self):
        record = self.gate_record()
        result = release.verify_release_gates(record, self.manifest, 100, self.root)
        self.assertEqual(result['license_review']['status'], 'Not Run')
        record['artifact_id'] = 101
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            release.verify_release_gates(record, self.manifest, 100, self.root)
        record['artifact_id'] = 100
        record['license_review'] = {'status': 'Passed'}
        with self.assertRaisesRegex(ValueError, 'reviewer'):
            release.verify_release_gates(record, self.manifest, 100, self.root)

    def test_license_review_can_pass_without_filling_human_installation_or_approval(self):
        proof = self.root / 'review.txt'
        proof.write_text('Synthetic unit-test evidence for the record boundary', encoding='utf-8')
        record = self.gate_record()
        record['license_review'] = {'status': 'Passed', 'reviewer': 'Fixture reviewer',
                                    'reviewed_at': '2026-10-05', 'notes': 'Fixture review',
                                    'evidence': [{'path': 'review.txt', 'sha256': release.digest_file(proof)}]}
        result = release.verify_release_gates(record, self.manifest, 100, self.root)
        self.assertEqual(result['license_review']['status'], 'Passed')
        self.assertEqual(result['independent_alpha_installation']['status'], 'Not Run')
        self.assertEqual(result['public_release_approval']['status'], 'Not Run')
        proof.write_text('Changed evidence', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            release.verify_release_gates(record, self.manifest, 100, self.root)

    def test_cross_host_artifact_redirect_does_not_forward_token(self):
        request = urllib.request.Request('https://api.github.com/fixture', headers={'Authorization': 'Bearer secret'})
        redirected = release.SafeRedirect().redirect_request(
            request, None, 302, '', {}, 'https://storage.example.invalid/signed-artifact')
        self.assertNotIn('Authorization', redirected.headers)
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            release.SafeRedirect().redirect_request(request, None, 302, '', {}, 'http://storage.example.invalid/file')

    def test_draft_retry_only_uploads_missing_assets_and_preserves_bytes(self):
        path = self.root / 'candidate.zip'
        path.write_bytes(b'original candidate')
        client = mock.Mock()
        client.existing_release.return_value = {'id': 10, 'tag_name': 'v0.1.0', 'draft': True,
                                                'prerelease': True, 'assets': []}
        client.upload.return_value = {'name': path.name, 'digest': 'sha256:' + release.digest_file(path),
                                      'state': 'uploaded'}
        result = release.promote_draft(client, 'v0.1.0', '0.1.0', [path], 'notes')
        self.assertEqual(result['status'], 'Draft')
        client.upload.assert_called_once()
        self.assertEqual(path.read_bytes(), b'original candidate')
        client.reset_mock()
        client.existing_release.return_value['assets'] = [client.upload.return_value]
        release.promote_draft(client, 'v0.1.0', '0.1.0', [path], 'notes')
        client.upload.assert_not_called()
        client.create_draft.assert_not_called()

    def test_conflicting_or_published_incomplete_release_is_never_overwritten(self):
        path = self.root / 'candidate.zip'
        path.write_bytes(b'original candidate')
        client = mock.Mock()
        for release_info in (
            {'id': 10, 'tag_name': 'v0.1.0', 'draft': True, 'prerelease': True,
             'assets': [{'name': path.name, 'digest': 'sha256:' + 'c' * 64, 'state': 'uploaded'}]},
            {'id': 10, 'tag_name': 'v0.1.0', 'draft': False, 'prerelease': True, 'assets': []},
        ):
            with self.subTest(release_info=release_info), self.assertRaises(ValueError):
                client.existing_release.return_value = release_info
                release.promote_draft(client, 'v0.1.0', '0.1.0', [path], 'notes')
        client.upload.assert_not_called()
        client.create_draft.assert_not_called()

    def test_complete_published_release_returns_without_writes(self):
        path = self.root / 'candidate.zip'
        path.write_bytes(b'original candidate')
        client = mock.Mock()
        client.existing_release.return_value = {'id': 10, 'tag_name': 'v0.1.0', 'draft': False,
                                                'prerelease': True, 'assets': [
            {'name': path.name, 'digest': 'sha256:' + release.digest_file(path), 'state': 'uploaded'}]}
        self.assertEqual(release.promote_draft(client, 'v0.1.0', '0.1.0', [path], 'notes')['status'],
                         'Already Published')
        client.upload.assert_not_called()
        client.create_draft.assert_not_called()

    def test_default_cli_performs_technical_dry_run_and_reports_pending_license(self):
        fake_git = mock.Mock()
        fake_git.snapshot.return_value = ('0.1.0', COMMIT, TREE, self.source)
        fake_client = mock.Mock()
        fake_client.get_json.side_effect = [{'id': 17, 'path': '.github/workflows/extension-package.yml'},
                                            self.run_record()]
        fake_client.all_artifacts.return_value = {'artifacts': [
            {'id': 100, 'name': self.manifest['artifact_name'], 'expired': False}]}
        fake_client.download.side_effect = lambda artifact_id, target: target.write_bytes(
            bundle_bytes(self.manifest, self.data))
        output = self.root / 'cli'
        argv = ['release_candidate', '--repository', 'owner/repo', '--tag', 'v0.1.0',
                '--candidate-run-id', '42', '--workflow-ref', 'refs/heads/main', '--output-dir', str(output)]
        with mock.patch('sys.argv', argv), mock.patch.object(release, 'GitSource', return_value=fake_git), \
                mock.patch.object(release, 'GitHub', return_value=fake_client), mock.patch('builtins.print'):
            release.main()
        result = json.loads((output / 'verification.json').read_text(encoding='utf-8'))
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['status'], 'Passed')
        self.assertEqual(result['draft_readiness'], 'Failed')
        self.assertEqual(result['gates']['license_review']['status'], 'Not Run')
        fake_client.get_json.side_effect = [{'id': 17, 'path': '.github/workflows/extension-package.yml'},
                                            self.run_record()]
        with mock.patch('sys.argv', argv + ['--create-draft']), \
                mock.patch.object(release, 'GitSource', return_value=fake_git), \
                mock.patch.object(release, 'GitHub', return_value=fake_client), mock.patch('builtins.print'), \
                self.assertRaisesRegex(ValueError, 'license review record'):
            release.main()
        fake_client.create_draft.assert_not_called()
        fake_client.upload.assert_not_called()

    def test_failed_promotion_keeps_technical_pass_and_records_actual_release_failure(self):
        proof = self.root / 'review.txt'
        proof.write_text('Synthetic record-boundary evidence', encoding='utf-8')
        record = self.gate_record()
        record['license_review'] = {'status': 'Passed', 'reviewer': 'Fixture reviewer',
                                    'reviewed_at': '2026-10-05', 'notes': 'Fixture review',
                                    'evidence': [{'path': proof.name, 'sha256': release.digest_file(proof)}]}
        gate_path = self.root / 'gates.json'
        gate_path.write_text(json.dumps(record), encoding='utf-8')
        fake_git = mock.Mock()
        fake_git.snapshot.return_value = ('0.1.0', COMMIT, TREE, self.source)
        fake_git.git.return_value = COMMIT.encode()
        fake_client = mock.Mock()
        fake_client.get_json.side_effect = [{'id': 17, 'path': '.github/workflows/extension-package.yml'},
                                            self.run_record()]
        fake_client.all_artifacts.return_value = {'artifacts': [
            {'id': 100, 'name': self.manifest['artifact_name'], 'expired': False}]}
        fake_client.download.side_effect = lambda artifact_id, target: target.write_bytes(
            bundle_bytes(self.manifest, self.data))
        fake_client.existing_release.return_value = {'id': 10, 'tag_name': 'v0.1.0', 'draft': True,
                                                    'prerelease': True, 'assets': []}
        fake_client.upload.side_effect = OSError('Fixture interrupted upload')
        output = self.root / 'cli-failed-upload'
        argv = ['release_candidate', '--repository', 'owner/repo', '--tag', 'v0.1.0',
                '--candidate-run-id', '42', '--workflow-ref', 'refs/heads/main', '--output-dir', str(output),
                '--gates-record', str(gate_path), '--create-draft']
        with mock.patch('sys.argv', argv), mock.patch.object(release, 'GitSource', return_value=fake_git), \
                mock.patch.object(release, 'GitHub', return_value=fake_client), mock.patch('builtins.print'), \
                self.assertRaisesRegex(OSError, 'interrupted upload'):
            release.main()
        result = json.loads((output / 'verification.json').read_text(encoding='utf-8'))
        self.assertEqual(result['status'], 'Passed')
        self.assertEqual(result['scope'], 'Exact candidate technical verification')
        self.assertEqual(result['release']['status'], 'Failed')
        self.assertIn('interrupted upload', result['release']['error'])
        self.assertEqual(result['gates']['independent_alpha_installation']['status'], 'Not Run')


class GitTagTests(unittest.TestCase):
    def test_real_git_annotated_tag_and_main_ancestry(self):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.STDOUT)
            git('init', '-b', 'main')
            _, _, source = fixture()
            for name, data in source.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            git('add', '.')
            git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                'commit', '--no-gpg-sign', '-m', 'Fixture source')
            git('update-ref', 'refs/remotes/origin/main', 'HEAD')
            git('tag', 'v0.1.0')
            with self.assertRaisesRegex(ValueError, 'annotated'):
                release.GitSource(root).snapshot('v0.1.0', 'main')
            git('tag', '-d', 'v0.1.0')
            git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                'tag', '-a', 'v0.1.0', '-m', 'Fixture annotated tag')
            version, commit, tree, actual_source = release.GitSource(root).snapshot('v0.1.0', 'main')
            self.assertEqual(version, '0.1.0')
            self.assertEqual(commit, git('rev-parse', 'HEAD').decode().strip())
            self.assertEqual(tree, git('rev-parse', 'HEAD:qcblender').decode().strip())
            self.assertEqual(actual_source['qcblender/__init__.py'], source['qcblender/__init__.py'])
            git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                'tag', '-a', 'v0.1.1', '-m', 'Fixture incorrect version')
            with self.assertRaisesRegex(ValueError, 'manifest version'):
                release.GitSource(root).snapshot('v0.1.1', 'main')
            git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                'tag', '-a', 'v0.2.0', 'v0.1.0', '-m', 'Fixture nested annotation')
            with self.assertRaisesRegex(ValueError, 'directly to a commit'):
                release.GitSource(root).snapshot('v0.2.0', 'main')
            git('checkout', '-b', 'other')
            (root / 'unreleased.txt').write_text('Not on main', encoding='utf-8')
            git('add', 'unreleased.txt')
            git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                'commit', '--no-gpg-sign', '-m', 'Fixture divergent commit')
            git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                'tag', '-a', 'v0.1.2', '-m', 'Fixture unreachable from main')
            with self.assertRaisesRegex(ValueError, 'not reachable'):
                release.GitSource(root).snapshot('v0.1.2', 'main')


if __name__ == '__main__':
    unittest.main()
