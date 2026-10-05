"""Packaging boundaries use synthetic reports; numerical acceptance runs separately."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools import candidate_artifacts as artifacts
from tools.build_science_backend import verify_source_lock
from tools.fetch_ci_blender import published_digest
from tools.package_identity import extension_filename, file_record, source_identity
from tools.qualify_package import validate_archive, validate_evidence
from tools.test_profiles import PUBLIC_SCIENCE, STDLIB

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '1' * 40
TREE = '2' * 40


class CandidateBoundaries(unittest.TestCase):
    def setUp(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='candidate-tests-', dir=ROOT / 'outputs')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'qcblender').mkdir()
        shutil.copyfile(ROOT / 'qcblender/blender_manifest.toml', self.root / 'qcblender/blender_manifest.toml')
        for relative in ('docs/v1-acceptance/tutorial-samples.json', 'docs/acceptance/tutorial-sample-delivery.json',
                         'science-sources.lock.json'):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, path)
        self.samples = ROOT / 'tests/data/distribution' / artifacts.SAMPLE_NAME
        self.candidate = self.root / extension_filename(self.root)
        self.candidate.write_bytes(b'exact original candidate bytes')
        self.digest = file_record(self.candidate)['sha256']
        self.reports = self.root / 'reports'
        self.reports.mkdir()
        self.public_sha = json.loads((self.root / 'docs/v1-acceptance/tutorial-samples.json').read_text(encoding='utf-8'))['files']['P01-o2-uhf']['sha256']
        self.reproduction = self.root / 'example'
        self.reproduction.mkdir()
        for name in ('example.blend', 'example.png', 'README.md'):
            (self.reproduction / name).write_bytes(name.encode('ascii'))
        dataset = self.reproduction / 'example.qcdata/datasets/wavefunction'
        dataset.mkdir(parents=True)
        (dataset / 'manifest.json').write_text(json.dumps({'metadata': {'source': {'sha256': self.public_sha}}}), encoding='utf-8')
        for name in artifacts.REQUIRED_REPORTS:
            report = dict(status='Passed', source_commit=COMMIT, candidate_sha256=self.digest)
            if name in ('stdlib', 'public-science'):
                report.update(suite='stdlib' if name == 'stdlib' else 'public-core', tests=100,
                              failures=0, errors=0, skipped=0,
                              modules=list(STDLIB if name == 'stdlib' else PUBLIC_SCIENCE))
            if name.startswith('cold-') or name == 'reproduction':
                report['cold_open'] = 'Passed'
            if name == 'reproduction':
                report.update(portable_saved=True, source_sha256=self.public_sha)
            if name == 'qualification':
                report['sha256'] = self.digest
            if name == 'sample-package':
                report['package'] = file_record(self.samples)
            self.write_report(name, report)

    def write_report(self, name, report):
        (self.reports / (name + '.json')).write_text(json.dumps(report), encoding='utf-8')

    def change_report(self, name, **changes):
        report = json.loads((self.reports / (name + '.json')).read_text(encoding='utf-8'))
        report.update(changes)
        self.write_report(name, report)

    def test_real_frozen_sample_zip_matches_delivery_and_excludes_p02(self):
        report = artifacts.verify_samples(self.samples)
        self.assertEqual(report['included_files'], 30)
        self.assertEqual(report['excluded_groups'], ['P02'])
        self.assertEqual(report['package']['sha256'], 'b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd')

    def test_changed_sample_byte_fails(self):
        changed = self.root / 'changed.zip'
        changed.write_bytes(self.samples.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'identity differs'):
            artifacts.verify_samples(changed)

    def test_version_and_filename_follow_manifest(self):
        manifest = self.root / 'qcblender/blender_manifest.toml'
        text = manifest.read_text(encoding='utf-8').replace('version = "0.1.0"', 'version = "2.3.4"')
        manifest.write_text(text, encoding='utf-8')
        self.assertEqual(extension_filename(self.root), 'qcblender-2.3.4.zip')

    def test_source_lock_is_verified_without_rewriting(self):
        lock = self.root / 'science-sources.lock.json'
        before = lock.read_bytes()
        self.assertEqual(verify_source_lock(self.root)['name'], 'gbasis')
        self.assertEqual(lock.read_bytes(), before)
        lock.write_text('[]', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'lock does not match'):
            verify_source_lock(self.root)
        self.assertEqual(lock.read_text(encoding='utf-8'), '[]')

    def test_source_identity_rejects_untracked_changes(self):
        with patch('tools.package_identity.subprocess.check_output', side_effect=[COMMIT, '?? untracked.py\n']):
            with self.assertRaisesRegex(ValueError, 'untracked'):
                source_identity(self.root)

    def test_reports_require_every_named_current_check(self):
        self.assertEqual(set(artifacts.validate_reports(self.reports, COMMIT, self.digest)), set(artifacts.REQUIRED_REPORTS))
        (self.reports / 'node-assets.json').unlink()
        with self.assertRaises(FileNotFoundError):
            artifacts.validate_reports(self.reports, COMMIT, self.digest)

    def test_numerical_skip_and_incomplete_modules_fail(self):
        self.change_report('public-science', skipped=1)
        with self.assertRaisesRegex(ValueError, 'skipped'):
            artifacts.validate_reports(self.reports, COMMIT, self.digest)
        self.change_report('public-science', skipped=0, modules=['test_science_adapter'])
        with self.assertRaisesRegex(ValueError, 'numerical suite'):
            artifacts.validate_reports(self.reports, COMMIT, self.digest)

    def test_stale_source_and_candidate_fail(self):
        self.change_report('cold-original', source_commit='3' * 40)
        with self.assertRaisesRegex(ValueError, 'source identity'):
            artifacts.validate_reports(self.reports, COMMIT, self.digest)
        self.change_report('cold-original', source_commit=COMMIT, candidate_sha256='4' * 64)
        with self.assertRaisesRegex(ValueError, 'different candidate'):
            artifacts.validate_reports(self.reports, COMMIT, self.digest)

    def test_reproduction_requires_saved_and_cold_open(self):
        self.change_report('reproduction', cold_open='Not Run')
        with self.assertRaisesRegex(ValueError, 'cold reopened'):
            artifacts.validate_reports(self.reports, COMMIT, self.digest)

    def test_reproduction_rejects_unknown_input(self):
        path = self.reproduction / 'example.qcdata/datasets/wavefunction/manifest.json'
        path.write_text('{"metadata":{"source":{"sha256":"unknown"}}}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unverified scientific input'):
            artifacts.reproduction_zip(self.reproduction, self.root / 'reproduction.zip', self.root)

    def test_reproduction_only_includes_selected_public_material(self):
        (self.reproduction / 'exports').mkdir()
        (self.reproduction / 'exports/metadata.json').write_text('{}', encoding='utf-8')
        target = self.root / 'reproduction.zip'
        artifacts.reproduction_zip(self.reproduction, target, self.root)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(set(archive.namelist()), {'example.blend', 'example.png', 'README.md',
                                                     'example.qcdata/datasets/wavefunction/manifest.json'})

    def test_assembly_preserves_original_zips_and_has_no_artifact_id_cycle(self):
        output = self.root / 'artifact'
        with patch('tools.candidate_artifacts.source_identity', return_value=(COMMIT, TREE)):
            manifest = artifacts.assemble(self.candidate, self.samples, self.reproduction, self.reports, output, 123, root=self.root)
        self.assertEqual((output / self.candidate.name).read_bytes(), self.candidate.read_bytes())
        self.assertEqual(file_record(output / self.samples.name)['sha256'], file_record(self.samples)['sha256'])
        self.assertEqual(manifest['product_tree'], TREE)
        self.assertEqual(manifest['candidate_run_id'], 123)
        self.assertEqual(manifest['license_review']['status'], 'Not Run')
        self.assertEqual(manifest['independent_alpha_installation']['status'], 'Not Run')
        self.assertNotIn('artifact_id', manifest)
        checksums = (output / 'SHA256SUMS.txt').read_text(encoding='ascii')
        self.assertNotIn('SHA256SUMS.txt', checksums)
        self.assertIn('release-manifest.json', checksums)
        for line in checksums.splitlines():
            digest, relative = line.split('  ')
            self.assertEqual(file_record(output / relative)['sha256'], digest)

    def test_non_public_reproduction_report_fails_before_assembly(self):
        self.change_report('reproduction', source_sha256='unknown')
        with patch('tools.candidate_artifacts.source_identity', return_value=(COMMIT, TREE)):
            with self.assertRaisesRegex(ValueError, 'P01 input'):
                artifacts.assemble(self.candidate, self.samples, self.reproduction, self.reports,
                                   self.root / 'artifact', 123, root=self.root)

    def test_explicit_qualification_rejects_stale_and_changed_evidence(self):
        report = self.root / 'passed.json'
        report.write_text(json.dumps({'status': 'Passed', 'source_commit': COMMIT}), encoding='utf-8')
        index = self.root / 'index.json'
        data = dict(candidate_sha256=self.digest, source_commit=COMMIT,
                    checks={'check': dict(path='passed.json', sha256=file_record(report)['sha256'], candidate_sha256=self.digest)})
        index.write_text(json.dumps(data), encoding='utf-8')
        self.assertIn('check', validate_evidence(index, self.digest, COMMIT))
        with self.assertRaisesRegex(ValueError, 'different candidate'):
            validate_evidence(index, 'wrong', COMMIT)
        report.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'changed evidence'):
            validate_evidence(index, self.digest, COMMIT)

    def test_qualification_evidence_cannot_escape_batch(self):
        index = self.reports / 'index.json'
        data = dict(candidate_sha256=self.digest, source_commit=COMMIT,
                    checks={'check': dict(path='../science-sources.lock.json', sha256='unused', candidate_sha256=self.digest)})
        index.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'inside this batch'):
            validate_evidence(index, self.digest, COMMIT)

    def test_blender_checksum_requires_unique_exact_fixed_filename(self):
        digest = 'a' * 64
        text = digest + '  blender-5.1.1-windows-x64.zip\n' + 'b' * 64 + '  other.zip\n'
        self.assertEqual(published_digest(text), digest)
        with self.assertRaisesRegex(ValueError, 'unique valid'):
            published_digest(text + text)
        with self.assertRaisesRegex(ValueError, 'unique valid'):
            published_digest('invalid  blender-5.1.1-windows-x64.zip')

    def qualified_zip_fixture(self):
        (self.root / 'qcblender/__init__.py').write_text('VALUE = 1\n', encoding='utf-8')
        (self.root / 'outputs').mkdir()
        wheel = io.BytesIO()
        with zipfile.ZipFile(wheel, 'w') as archive:
            archive.writestr('gbasis/__init__.py', '')
            archive.writestr('gbasis/QCBLENDER_BUILD.md', 'Synthetic packaging boundary')
        backend = dict(name='qc-gbasis', filename='qc_gbasis-0.1.0-py3-none-any.whl', sha256=hashlib.sha256(wheel.getvalue()).hexdigest())
        (self.root / 'outputs/backend-wheel.json').write_text(json.dumps(backend), encoding='utf-8')
        (self.root / 'dependencies.lock.json').write_text('{"packages":[]}', encoding='utf-8')
        for name in ('LICENSE', 'THIRD_PARTY.md'):
            (self.root / name).write_text('Synthetic packaging boundary', encoding='utf-8')
        manifest = (self.root / 'qcblender/blender_manifest.toml').read_text(encoding='utf-8')
        manifest = manifest.replace('wheels = []', 'wheels = ["./wheels/' + backend['filename'] + '"]')
        contents = {'__init__.py': (self.root / 'qcblender/__init__.py').read_bytes(),
                    'blender_manifest.toml': manifest.encode('utf-8'), 'assets/nodes.blend': b'synthetic node bytes',
                    'backend-wheel.json': json.dumps(backend).encode('utf-8'),
                    'wheels/' + backend['filename']: wheel.getvalue()}
        for name in ('LICENSE', 'THIRD_PARTY.md', 'science-sources.lock.json', 'dependencies.lock.json'):
            contents[name] = (self.root / name).read_bytes()
        installed = self.root / 'installed'
        with zipfile.ZipFile(self.candidate, 'w') as archive:
            for name, raw in contents.items():
                archive.writestr(name, raw)
                target = installed / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        return installed

    def test_archive_qualification_checks_installed_assets_and_all_source_bytes(self):
        installed = self.qualified_zip_fixture()
        self.assertEqual(validate_archive(self.candidate, installed, self.root)['name'], 'qc-gbasis')
        (installed / 'assets/nodes.blend').write_bytes(b'changed node asset')
        with self.assertRaisesRegex(ValueError, 'Installed file differs'):
            validate_archive(self.candidate, installed, self.root)

    def test_archive_qualification_rejects_changed_source(self):
        installed = self.qualified_zip_fixture()
        (self.root / 'qcblender/__init__.py').write_text('VALUE = 2\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Source differs'):
            validate_archive(self.candidate, installed, self.root)


if __name__ == '__main__':
    unittest.main()
