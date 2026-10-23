"""Website extraction uses the same explicit public identities as tutorial tools."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from test_tutorial_dataset import identity, write_fixture
from tools.tutorial_dataset import DELIVERY
from tools.workspace_paths import temporary_tests_root

SPEC = importlib.util.spec_from_file_location('extract_public_samples', Path(__file__).with_name('extract-public-samples.py'))
extractor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extractor)


class PublicSamples(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='website-samples-', dir=temporary_tests_root(ROOT))
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        write_fixture(self.root)
        self.delivery = json.loads((self.root / DELIVERY).read_text(encoding='utf-8'))
        self.destination = self.root / 'website-assets'

    def save_delivery(self):
        (self.root / DELIVERY).write_text(json.dumps(self.delivery), encoding='utf-8')

    def update_package(self, members):
        package = self.root / self.delivery['package']['path']
        with zipfile.ZipFile(package, 'w') as archive:
            for name, raw in members.items():
                archive.writestr(name, raw)
        self.delivery['package'].update(identity(package.read_bytes()))
        self.save_delivery()

    def members(self):
        with zipfile.ZipFile(self.root / self.delivery['package']['path']) as archive:
            return {entry.filename: archive.read(entry) for entry in archive.infolist()}

    def test_owned_current_p02_is_extracted_without_historical_data(self):
        report = extractor.public_samples(self.root, self.destination)
        self.assertEqual(report['archive']['dataset_id'], 'gaussian-v1')
        self.assertEqual(report['archive']['download'], 'qcblender-public-tutorial-samples-v3.zip')
        self.assertEqual((self.destination / 'gaussian-v1/P02/water.out').read_bytes(),
                         b'Owned Gaussian optimization/frequency/NBO fixture')
        self.assertFalse((self.destination / 'P01/old.fchk').exists())
        self.assertFalse((self.destination / 'P02').exists())

    def test_inspection_does_not_extract_files(self):
        report = extractor.public_samples(self.root)
        self.assertTrue(any(row['path'] == 'gaussian-v1/P02/water.out' for row in report['samples']))
        self.assertFalse(self.destination.exists())

    def test_manifest_identity_drift_is_rejected_before_writing(self):
        (self.root / self.delivery['manifest']['path']).write_bytes(b'changed manifest')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            extractor.public_samples(self.root, self.destination)
        self.assertFalse(self.destination.exists())

    def test_archive_identity_drift_is_rejected_before_writing(self):
        with (self.root / self.delivery['package']['path']).open('ab') as stream:
            stream.write(b'unreviewed bytes')
        with self.assertRaisesRegex(ValueError, 'identity differs'):
            extractor.public_samples(self.root, self.destination)
        self.assertFalse(self.destination.exists())

    def test_unlisted_legacy_p02_and_traversal_are_rejected_before_writing(self):
        original = self.members()
        for name in ('P02/private.out', '../P02/private.out'):
            with self.subTest(member=name):
                self.update_package(dict(original, **{name: b'not in allowlist'}))
                with self.assertRaisesRegex(ValueError, 'membership differs'):
                    extractor.public_samples(self.root, self.destination)
                self.assertFalse(self.destination.exists())

    def test_relabelled_restricted_p02_hash_is_rejected(self):
        raw = b'Historical water output without redistribution permission'
        manifest_path = self.root / self.delivery['manifest']['path']
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        name = 'gaussian-v1/P02/stolen.out'
        manifest['files'][name] = dict(manifest['files']['gaussian-v1/P02/water.out'],
            id=name, archive_path=name, path='validation/shared/data/public/' + name, **identity(raw))
        encoded = json.dumps(manifest).encode()
        manifest_path.write_bytes(encoded)
        self.delivery['manifest'].update(identity(encoded))
        members = self.members();members[name] = raw;members['tutorial-samples.json'] = encoded
        self.update_package(members)
        with self.assertRaisesRegex(ValueError, 'Unlicensed tutorial input'):
            extractor.public_samples(self.root, self.destination)
        self.assertFalse(self.destination.exists())

    def test_linked_zip_member_is_rejected_before_any_write(self):
        members = self.members()
        package = self.root / self.delivery['package']['path']
        with zipfile.ZipFile(package, 'w') as archive:
            for name, raw in members.items():
                entry = zipfile.ZipInfo(name)
                if name == 'gaussian-v1/P02/water.out':
                    entry.create_system = 3
                    entry.external_attr = 0o120777 << 16
                archive.writestr(entry, raw)
        self.delivery['package'].update(identity(package.read_bytes()));self.save_delivery()
        with self.assertRaisesRegex(ValueError, 'Forbidden public ZIP member'):
            extractor.public_samples(self.root, self.destination)
        self.assertFalse(self.destination.exists())

    def test_schema1_receipt_keeps_historical_dataset_without_p02(self):
        legacy = self.delivery['legacy_dataset']
        self.delivery = dict(schema=1, manifest=legacy['manifest'], package=legacy['package'])
        self.save_delivery()
        report = extractor.public_samples(self.root, self.destination)
        self.assertEqual(report['archive']['dataset_id'], 'legacy-v2')
        self.assertEqual(report['manifest_member'], 'tutorial-samples.json')
        self.assertTrue((self.destination / 'P01/old.fchk').is_file())
        self.assertFalse(any('P02' in row['path'] for row in report['samples']))


if __name__ == '__main__':
    unittest.main()
