"""Exercise data preparation with the real frozen public archive and local boundaries."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from tools.workspace_paths import temporary_tests_root
from tools.tutorial_dataset import DELIVERY, load_dataset

from tools.local_inputs import CATALOG, DATA, ROOT
from tools.prepare_validation_data import FROZEN_MANIFEST, MIGRATION, prepare


class ValidationDataPreparation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'checkout'
        migration = json.loads((ROOT / MIGRATION).read_text(encoding='utf-8'))
        paths = {FROZEN_MANIFEST, MIGRATION, CATALOG,
                 'validation/agent/acceptance/tutorial-sample-delivery.json'}
        paths.update(row['path'] for row in migration['files']
                     if row['group'] in ('package', 'regression', 'catalog'))
        for relative in paths:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        legacy = load_dataset(ROOT, 'legacy-v2')
        (self.root / DELIVERY).write_text(json.dumps(dict(schema=1,
            manifest=legacy['manifest_record'], package=legacy['package_record'])), encoding='utf-8')

    def test_public_archive_prepares_portable_inputs_without_overwriting_changes(self):
        report = prepare(self.root, dataset='legacy-v2')
        self.assertEqual(report['public_package']['included_files'], 30)
        self.assertEqual(len(report['public_files']), 33)
        self.assertEqual(report['local_input_count'], 0)
        self.assertFalse((self.root / DATA / 'public/P02').exists())
        self.assertFalse((self.root / DATA / 'local').exists())
        self.assertEqual((self.root / DATA / 'public/tutorial-samples.json').read_bytes(),
                         (self.root / FROZEN_MANIFEST).read_bytes())
        repeat = prepare(self.root, dataset='legacy-v2')
        self.assertEqual({row['action'] for row in repeat['public_files']}, {'verified'})
        changed = self.root / DATA / 'public/P01/o2-uhf.fchk'
        changed.write_bytes(b'user changed file')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            prepare(self.root, dataset='legacy-v2')
        self.assertEqual(changed.read_bytes(), b'user changed file')

    def test_current_package_guide_is_not_frozen_but_regression_inputs_are(self):
        guide = self.root / 'validation/agent/packages/README.md'
        guide.write_bytes(b'Current package navigation, revised after the migration.\n')
        report = prepare(self.root, dataset='legacy-v2')
        self.assertNotIn(guide.relative_to(self.root).as_posix(), report['verified_paths'])
        self.assertEqual(guide.read_bytes(), b'Current package navigation, revised after the migration.\n')
        migration = json.loads((self.root / MIGRATION).read_text(encoding='utf-8'))
        record = next(row for row in migration['files'] if row['group'] == 'regression')
        (self.root / record['path']).write_bytes(b'changed scientific fixture')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            prepare(self.root, dataset='legacy-v2')

    def test_local_layout_is_explicit_and_missing_source_fails_before_copying(self):
        reference = Path(self.temporary.name) / 'reference'
        reference.mkdir()
        relative = DATA + '/local/example.log'
        raw = b'local boundary input'
        identity = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        (self.root / CATALOG).write_text(json.dumps({'files': {'example.log': {
            'path': relative, **identity}}}), encoding='utf-8')
        migration = json.loads((self.root / MIGRATION).read_text(encoding='utf-8'))
        migration['files'] = [row for row in migration['files'] if row['group'] != 'local']
        migration['files'].append(dict(source='legacy/example.log', path=relative,
                                       group='local', **identity))
        (self.root / MIGRATION).write_text(json.dumps(migration), encoding='utf-8')
        with self.assertRaises(FileNotFoundError):
            prepare(self.root, reference, 'legacy', include_local=True, dataset='legacy-v2')
        self.assertFalse((self.root / DATA / 'public').exists())
        legacy = reference / 'legacy/example.log'
        legacy.parent.mkdir()
        legacy.write_bytes(raw)
        with self.assertRaises(FileNotFoundError):
            prepare(self.root, reference, 'current', include_local=True, dataset='legacy-v2')
        report = prepare(self.root, reference, 'legacy', include_local=True, dataset='legacy-v2')
        self.assertEqual(report['local_input_count'], 1)
        self.assertEqual((self.root / relative).read_bytes(), raw)
        self.assertEqual(legacy.read_bytes(), raw)
        legacy.write_bytes(b'changed source')
        with self.assertRaises(ValueError):
            prepare(self.root, reference, 'legacy', include_local=True, dataset='legacy-v2')
        self.assertEqual((self.root / relative).read_bytes(), raw)
        current = reference / relative
        current.parent.mkdir(parents=True)
        current.write_bytes(raw)
        (self.root / relative).unlink()
        repeated = prepare(self.root, reference, 'current', include_local=True, dataset='legacy-v2')
        self.assertEqual(repeated['local_input_count'], 1)
        self.assertEqual((self.root / relative).read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
