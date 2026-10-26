"""Preview publication boundaries; fixtures never count as Blender acceptance."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools import release_candidate as release
from tools.package_identity import file_record
from tools.repository_index import asset_url, verify_index
from tools.tutorial_bundle import supplemental_files, verify_archive
from tools.workspace_paths import temporary_tests_root
from test_release_candidate import fixture, versioned_fixture, sha, zipped, COMMIT, TREE

ROOT = Path(__file__).resolve().parents[1]


def preview_fixture():
    manifest, data, source = versioned_fixture()
    manifest['schema'] = 'qcblender.release-candidate.v2'
    source['qcblender/blender_manifest.toml'] += b'type="add-on"\nblender_version_min="5.1.1"\nblender_version_max="5.2.0"\n'
    with zipfile.ZipFile(io.BytesIO(data[manifest['files']['samples']['path']])) as archive:
        for name in archive.namelist():
            if name != 'tutorial-samples.json':
                source['validation/shared/data/public/' + name] = archive.read(name)
    source['validation/shared/data/public/README.md'] = b'Public fixture inputs'
    source['validation/human/SOP.md'] = b'All topic links belong to document validation'
    for number in range(1, 13):
        source[f'validation/human/topics/{number:02}.md'] = f'Topic {number}'.encode()
    groups = {}
    for group in ('surface-projection', 'aicd'):
        name = f'validation/shared/data/public/scientific-displays/{group}/NOTICE.md'
        source[name] = b'Owned synthetic fixture, CC-BY-4.0'
        entry = dict(path=name, bytes=len(source[name]), sha256=sha(source[name]), license='CC-BY-4.0')
        groups[group] = dict(status='Passed', license_evidence=[entry], files=[entry])
    source['validation/agent/acceptance/tutorial-public-extras.json'] = json.dumps(dict(
        schema='qcblender.tutorial-extras.v1', groups=groups)).encode()
    tutorial = zipped({name.removeprefix('validation/'): raw for name, raw in source.items()
                       if name.startswith(('validation/human/', 'validation/shared/data/public/'))})
    extension = manifest['files']['extension']
    index = json.dumps(dict(version='v1', blocklist=[], data=[dict(id='qcblender', version='0.1.0',
        type='add-on', platforms=['windows-x64'], blender_version_min='5.1.1', blender_version_max='5.2.0',
        archive_url=asset_url('0.1.0', extension['path']), archive_size=extension['bytes'],
        archive_hash='sha256:' + extension['sha256'])])).encode()
    for role, name, raw in [('tutorial', 'qcblender-tutorial-0.1.0.zip', tutorial), ('repository_index', 'index.json', index)]:
        data[name] = raw
        manifest['files'][role] = dict(path=name, bytes=len(raw), sha256=sha(raw))
    public = {key: manifest[key] for key in ('version', 'channel', 'source_commit', 'product_tree',
              'candidate_run_id', 'workflow', 'artifact_name', 'platform', 'dependencies')}
    public.update(schema='qcblender.release.v1', files={key: manifest['files'][key]
        for key in ('extension', 'tutorial', 'repository_index')})
    data['release-manifest.json'] = json.dumps(public).encode()
    data['SHA256SUMS.txt'] = ''.join(f'{sha(data[name])}  {name}\n' for name in
        [entry['path'] for entry in public['files'].values()] + ['release-manifest.json']).encode()
    for role, name in [('public_manifest', 'release-manifest.json'), ('public_checksums', 'SHA256SUMS.txt')]:
        manifest['files'][role] = dict(path=name, bytes=len(data[name]), sha256=sha(data[name]))
    raw = json.dumps(dict(status='Passed', source_commit=COMMIT, package=manifest['files']['tutorial'])).encode()
    data['reports/tutorial.json'] = raw
    manifest['reports']['tutorial'] = dict(path='reports/tutorial.json', bytes=len(raw), sha256=sha(raw), status='Passed')
    return manifest, data, source


class PreviewBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_index_binds_platform_versions_url_and_archive_bytes(self):
        manifest = dict(id='qcblender', version='0.1.0', type='add-on', platforms=['windows-x64'],
                        blender_version_min='5.1.1', blender_version_max='5.2.0')
        candidate = dict(path='qcblender-0.1.0.zip', bytes=123, sha256='a' * 64)
        item = dict(manifest, archive_size=123, archive_hash='sha256:' + 'a' * 64,
                    archive_url=asset_url('0.1.0', candidate['path']))
        document = dict(version='v1', blocklist=[], data=[item])
        verify_index(document, manifest, candidate)
        for key, value in [('platforms', ['linux-x64']), ('blender_version_max', '5.3.0'),
                           ('archive_size', 124), ('archive_hash', 'sha256:' + 'b' * 64),
                           ('archive_url', 'https://example.com/latest.zip')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(document)
                changed['data'][0][key] = value
                with self.assertRaises(ValueError):
                    verify_index(changed, manifest, candidate)

    def test_tutorial_archive_rejects_missing_extra_and_changed_bytes(self):
        members = {'human/SOP.md': dict(bytes=3, sha256=sha(b'SOP'))}
        for entries, valid in [({'human/SOP.md': b'SOP'}, True), ({}, False),
                               ({'human/SOP.md': b'BAD'}, False),
                               ({'human/SOP.md': b'SOP', 'private.txt': b'private'}, False)]:
            path = self.root / 'tutorial.zip'
            path.write_bytes(zipped(entries))
            if valid:
                verify_archive(path, members)
            else:
                with self.assertRaises(ValueError):
                    verify_archive(path, members)

    def test_unresolved_license_cannot_be_skipped(self):
        path = self.root / 'validation/agent/acceptance/tutorial-public-extras.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(dict(schema='qcblender.tutorial-extras.v1', groups={
            key: dict(status='Not Run', blocker='Missing permission', license_evidence=[], files=[])
            for key in ('surface-projection', 'aicd')})), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Tutorial public material blocked'):
            supplemental_files(self.root)

    def test_v2_internal_reports_are_separate_from_public_checksums(self):
        manifest, data, _ = fixture()
        manifest['schema'] = 'qcblender.release-candidate.v2'
        for role, name, content in [('tutorial', 'qcblender-tutorial-0.1.0.zip', zipped({'human/SOP.md': b'SOP'})),
                                    ('repository_index', 'index.json', b'{}'),
                                    ('public_manifest', 'release-manifest.json', b'{}'),
                                    ('public_checksums', 'SHA256SUMS.txt', b'public checksums fixture')]:
            data[name] = content
            manifest['files'][role] = dict(path=name, bytes=len(content), sha256=sha(content))
        report = json.dumps(dict(status='Passed', source_commit=COMMIT, package=manifest['files']['tutorial'])).encode()
        data['reports/tutorial.json'] = report
        manifest['reports']['tutorial'] = dict(path='reports/tutorial.json', bytes=len(report), sha256=sha(report), status='Passed')
        data['candidate-manifest.json'] = json.dumps(manifest).encode()
        data['CANDIDATE-SHA256SUMS.txt'] = ''.join(f'{sha(value)}  {name}\n' for name, value in data.items()).encode()
        bundle = self.root / 'bundle.zip'
        bundle.write_bytes(zipped(data))
        verified = release.unpack_candidate(bundle, self.root / 'candidate', version='0.1.0',
                                            commit=COMMIT, product_tree=TREE, run_id=42)
        self.assertEqual(verified['schema'], 'qcblender.release-candidate.v2')
        self.assertEqual((self.root / 'candidate/release-manifest.json').read_bytes(), b'{}')

    def test_agent_gate_requires_all_actual_checks_and_keeps_human_not_run(self):
        manifest, _, _ = fixture()
        manifest['schema'] = 'qcblender.release-candidate.v2'
        evidence = self.root / 'actual-evidence.json'
        evidence.write_text('Synthetic test evidence, not real acceptance.', encoding='utf-8')
        gate = dict(status='Passed', reviewer='fixture', reviewed_at='2026-10-26T00:00:00+00:00',
                    notes='Fixture only', evidence=[file_record(evidence)],
                    checks={key: 'Passed' for key in release.PREVIEW_CHECKS})
        record = dict(schema='qcblender.release-gates.v1', candidate_run_id=42, artifact_id=7,
                      source_commit=COMMIT, extension_sha256=manifest['files']['extension']['sha256'],
                      license_review=gate, public_release_approval=gate,
                      independent_alpha_installation=dict(status='Not Run'), agent_preview_installation=gate)
        result = release.verify_release_gates(record, manifest, 7, self.root)
        self.assertEqual(result['independent_alpha_installation']['status'], 'Not Run')
        record['agent_preview_installation'] = dict(gate, checks={**gate['checks'], 'computer_use': 'Not Run'})
        with self.assertRaisesRegex(ValueError, 'required actual checks'):
            release.verify_release_gates(record, manifest, 7, self.root)

    def test_complete_preview_round_trip_and_tag_owned_tutorial_bytes(self):
        manifest, data, source = preview_fixture()
        data['candidate-manifest.json'] = json.dumps(manifest).encode()
        data['CANDIDATE-SHA256SUMS.txt'] = ''.join(f'{sha(raw)}  {name}\n' for name, raw in data.items()).encode()
        bundle = self.root / 'candidate.zip'
        bundle.write_bytes(zipped(data))
        target = self.root / 'candidate'
        checked = release.unpack_candidate(bundle, target, version='0.1.0', commit=COMMIT, product_tree=TREE, run_id=42)
        release.verify_public_materials(checked, target, source)
        release.verify_preview_materials(checked, target, source)
        source['validation/human/topics/10.md'] += b'Changed after candidate'
        with self.assertRaisesRegex(ValueError, 'Tutorial ZIP content differs'):
            release.verify_preview_materials(checked, target, source)

    def test_publication_downloads_remote_bytes_before_patching_release(self):
        path = self.root / 'original.zip'
        path.write_bytes(b'Original exact candidate')
        client = release.GitHub('psiQAQ/QCBlender', 'synthetic-test-token')
        remote = dict(id=9, draft=True, prerelease=True, html_url='https://github.com/psiQAQ/QCBlender/releases/tag/v0.1.0',
                      assets=[dict(id=3, name=path.name)])
        requests = []
        def request(endpoint, **kwargs):
            requests.append((endpoint, kwargs))
            if kwargs.get('method') == 'PATCH':
                return io.BytesIO(json.dumps(dict(remote, draft=False)).encode())
            return io.BytesIO(path.read_bytes())
        with patch.object(client, 'get_json', return_value=remote), patch.object(client, 'request', side_effect=request):
            self.assertEqual(client.publish_preview(9, [path])['status'], 'Published')
        self.assertEqual(requests[0][0], 'releases/assets/3')
        self.assertEqual(json.loads(requests[1][1]['body']), dict(draft=False, prerelease=True, make_latest='false'))
        with patch.object(client, 'get_json', return_value=remote), patch.object(client, 'request', return_value=io.BytesIO(b'Changed')) as mocked:
            with self.assertRaisesRegex(ValueError, 'Downloaded Release bytes differ'):
                client.publish_preview(9, [path])
            self.assertEqual(mocked.call_count, 1)


if __name__ == '__main__':
    unittest.main()
