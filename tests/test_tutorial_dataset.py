"""Version selection and public restore checks using explicit small sample fixtures."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.candidate_artifacts import verify_samples
from tools.prepare_validation_data import prepare
from tools.tutorial_dataset import DELIVERY, FROZEN_MANIFEST, LEGACY_PACKAGE, load_dataset
from tools.workspace_paths import temporary_tests_root

ROOT = Path(__file__).resolve().parents[1]


def identity(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def write_fixture(root):
    """A legacy dataset plus an owned P02 and a two-step Gaussian IRC dataset."""
    root = Path(root)

    def write(name, raw):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def entry(sid, name, raw, group):
        return dict(id=sid, archive_path=name, path='validation/shared/data/public/' + name,
                    distribution='included', license='CC-BY-4.0', calculation_group=group,
                    **identity(raw))

    old_raw = b'Historical owned O2 wavefunction fixture'
    restricted_raw = b'Historical water output without redistribution permission'
    old = dict(files={'old': entry('old', 'P01/old.fchk', old_raw, 'P01'),
                      'restricted': dict(id='restricted', distribution='external-acquisition',
                                         license='unverified', calculation_group='P02',
                                         **identity(restricted_raw))})
    old_json = json.dumps(old).encode()
    write(FROZEN_MANIFEST, old_json)
    write('validation/shared/data/public/P01/old.fchk', old_raw)
    write('validation/shared/data/public/tutorial-samples.json', old_json)
    for name in ('LICENSE', 'NOTICE.md', 'README.md'):
        write('validation/shared/data/public/' + name, b'Root public explanation\n')
    old_package = write(LEGACY_PACKAGE, b'')
    with zipfile.ZipFile(old_package, 'w') as archive:
        for name, raw in {'P01/old.fchk': old_raw, 'tutorial-samples.json': old_json,
                          'LICENSE': b'CC-BY-4.0', 'NOTICE.md': b'Legacy data'}.items():
            archive.writestr(name, raw)
    blobs = {'gaussian-v1/P02/water.out': b'Owned Gaussian optimization/frequency/NBO fixture',
             'gaussian-v1/P04/a.fchk': b'Gaussian wavefunction step 10',
             'gaussian-v1/P04/b.fchk': b'Gaussian wavefunction step 20',
             'gaussian-v1/P04/a-mayer.txt': b'Actual step 10 Mayer fixture',
             'gaussian-v1/P04/b-mayer.txt': b'Actual step 20 Mayer fixture',
             'gaussian-v1/P04/steps.csv': b'step,fchk\n10,a.fchk\n20,b.fchk\n',
             'gaussian-v1/P04/mayer.csv': b'step,mayer_output\n10,a-mayer.txt\n20,b-mayer.txt\n'}
    manifest = dict(files={name: entry(name, name, raw, 'P02' if '/P02/' in name else 'P04')
                           for name, raw in blobs.items()})
    raw = json.dumps(manifest).encode()
    manifest_name = 'validation/shared/data/public/gaussian-v1/tutorial-samples.json'
    write(manifest_name, raw)
    package_name = 'validation/agent/packages/qcblender-public-tutorial-samples-v3.zip'
    package = write(package_name, b'')
    with zipfile.ZipFile(package, 'w') as archive:
        for name, content in dict(blobs, **{'tutorial-samples.json': raw,
                                          'LICENSE': b'CC-BY-4.0', 'NOTICE.md': b'Owned data'}).items():
            archive.writestr(name, content)
    delivery = dict(schema=2, dataset_id='gaussian-v1',
                    manifest=dict(path=manifest_name, **identity(raw)),
                    package=dict(path=package_name, **identity(package.read_bytes())),
                    legacy_dataset=dict(dataset_id='legacy-v2',
                                        manifest=dict(path=FROZEN_MANIFEST, **identity(old_json)),
                                        package=dict(path=LEGACY_PACKAGE, **identity(old_package.read_bytes()))))
    write(DELIVERY, json.dumps(delivery).encode())
    return delivery, manifest, blobs


class TutorialDatasets(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.delivery, self.manifest, self.blobs = write_fixture(self.root)

    def update_manifest(self):
        raw = json.dumps(self.manifest).encode()
        (self.root / self.delivery['manifest']['path']).write_bytes(raw)
        self.delivery['manifest'].update(identity(raw))
        (self.root / DELIVERY).write_text(json.dumps(self.delivery), encoding='utf-8')

    def test_owned_p02_package_is_allowed_and_legacy_is_explicit(self):
        report = verify_samples(root=self.root)
        self.assertEqual(report['dataset_id'], 'gaussian-v1')
        self.assertEqual(report['excluded_groups'], [])
        self.assertEqual(report['included_files'], len(self.blobs))
        self.assertEqual(load_dataset(self.root, 'legacy-v2')['manifest']['files']['old']['archive_path'],
                         'P01/old.fchk')
        self.assertEqual(verify_samples(root=self.root, dataset='legacy-v2')['excluded_groups'], ['P02'])

    def test_manifest_identity_mismatch_fails_before_restoring(self):
        (self.root / self.delivery['manifest']['path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            prepare(self.root)
        self.assertFalse((self.root / 'validation/shared/data/public/gaussian-v1/P02').exists())

    def test_unlicensed_current_record_is_rejected(self):
        self.manifest['files']['gaussian-v1/P02/water.out']['license'] = 'unverified'
        self.update_manifest()
        with self.assertRaisesRegex(ValueError, 'Unlicensed'):
            load_dataset(self.root)

    def test_archive_cannot_smuggle_restricted_legacy_input(self):
        package = self.root / self.delivery['package']['path']
        with zipfile.ZipFile(package, 'a') as archive:
            archive.writestr('P02/restricted.out', b'Unlicensed historical input')
        self.delivery['package'].update(identity(package.read_bytes()))
        (self.root / DELIVERY).write_text(json.dumps(self.delivery), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'membership differs'):
            verify_samples(root=self.root)

    def test_archive_manifest_must_match_recorded_bytes_not_only_json_values(self):
        package = self.root / self.delivery['package']['path']
        with zipfile.ZipFile(package, 'w') as archive:
            for name, raw in self.blobs.items():
                archive.writestr(name, raw)
            archive.writestr('tutorial-samples.json', json.dumps(self.manifest, indent=2))
            archive.writestr('LICENSE', 'CC-BY-4.0')
            archive.writestr('NOTICE.md', 'Owned data')
        self.delivery['package'].update(identity(package.read_bytes()))
        (self.root / DELIVERY).write_text(json.dumps(self.delivery), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'manifest differs'):
            verify_samples(root=self.root)

    def test_relabelled_restricted_legacy_bytes_cannot_enter_current_allowlist(self):
        old = load_dataset(self.root, 'legacy-v2')['manifest']['files']['restricted']
        self.manifest['files']['gaussian-v1/P02/water.out'].update(
            {key: old[key] for key in ('bytes', 'sha256')})
        self.update_manifest()
        with self.assertRaisesRegex(ValueError, 'Unlicensed'):
            load_dataset(self.root)

    def test_restore_keeps_legacy_and_checks_two_arbitrary_irc_steps(self):
        legacy = self.root / 'validation/shared/data/public/P01/old.fchk'
        frozen = (self.root / FROZEN_MANIFEST).read_bytes()
        root_manifest = (self.root / 'validation/shared/data/public/tutorial-samples.json').read_bytes()
        previous = legacy.read_bytes()
        report = prepare(self.root)
        self.assertEqual(report['dataset_id'], 'gaussian-v1')
        self.assertEqual(legacy.read_bytes(), previous)
        self.assertEqual((self.root / FROZEN_MANIFEST).read_bytes(), frozen)
        self.assertEqual((self.root / 'validation/shared/data/public/tutorial-samples.json').read_bytes(), root_manifest)
        self.assertEqual({row['action'] for row in prepare(self.root)['public_files']}, {'verified'})
        changed = self.root / 'validation/shared/data/public/gaussian-v1/P02/water.out'
        changed.write_bytes(b'User edit')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            prepare(self.root)
        self.assertEqual(changed.read_bytes(), b'User edit')

    def test_schema_one_paths_are_mapped_without_rewriting_legacy_receipt(self):
        delivery = dict(schema=1, manifest=dict(self.delivery['legacy_dataset']['manifest'], path='docs/old.json'),
                        package=dict(self.delivery['legacy_dataset']['package'], path='outputs/old.zip'))
        raw = json.dumps(delivery).encode()
        (self.root / DELIVERY).write_bytes(raw)
        selected = load_dataset(self.root)
        self.assertEqual(selected['dataset_id'], 'legacy-v2')
        self.assertEqual(selected['package_path'], self.root / LEGACY_PACKAGE)
        self.assertEqual((self.root / DELIVERY).read_bytes(), raw)

    def test_csv_cannot_reference_unlisted_or_parent_files(self):
        from tools.tutorial_dataset import verify_csv_inputs
        prepare(self.root)
        path = self.root / 'validation/shared/data/public/gaussian-v1/P04/steps.csv'
        path.write_text('step,fchk\n10,../P02/water.out\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'relative data path'):
            verify_csv_inputs(self.root / 'validation/shared/data/public', load_dataset(self.root))


if __name__ == '__main__':
    unittest.main()
