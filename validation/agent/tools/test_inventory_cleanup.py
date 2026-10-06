"""Exercise inventory decisions against small real archives in the workspace."""

import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


SOURCE = Path(__file__).with_name('inventory_cleanup.py')
SPEC = importlib.util.spec_from_file_location('inventory_cleanup', SOURCE)
INVENTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INVENTORY)
WORK = SOURCE.parents[2] / 'work' / 'inventory-tests'


def make_zip(path, members):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in members.items():
            archive.writestr(name, data)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        WORK.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='case-', dir=WORK)
        self.root = Path(self.temporary.name).absolute()
        self.assertTrue(self.root.is_relative_to(WORK.absolute()))
        self.addCleanup(self.temporary.cleanup)
        self.latest = self.root / INVENTORY.LATEST
        files = {}
        for role, name, contents in (
            ('extension', 'qcblender-0.1.0.zip', {'blender_manifest.toml': 'id = "qcblender"\nversion = "0.1.0"\n'}),
            ('samples', 'qcblender-public-tutorial-samples-v2.zip', {'LICENSE': 'sample'}),
            ('reproduction', 'qcblender-reproduction-0.1.0.zip', {'example.blend': b'fixture'}),
        ):
            path = self.latest / name
            make_zip(path, contents)
            files[role] = {'path': name, **INVENTORY.file_identity(path)}
        reports = {}
        for name in ('stdlib', 'public-science', 'node-helpers', 'extension-install',
                     'node-assets', 'cold-original', 'cold-moved', 'qualification',
                     'sample-package', 'reproduction'):
            path = self.latest / 'reports' / (name + '.json')
            path.parent.mkdir(exist_ok=True)
            path.write_text('{"status":"Passed"}', encoding='utf-8')
            reports[name] = {'path': 'reports/' + path.name, 'status': 'Passed',
                             **INVENTORY.file_identity(path)}
        manifest = {'files': files, 'reports': reports, 'source_commit': 'fixture',
                    'product_tree': 'fixture', 'candidate_run_id': 2}
        (self.latest / 'release-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        mapping = self.root / INVENTORY.MAP_PATH
        mapping.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(mapping, 'wt', encoding='utf-8'):
            pass

    def test_current_materials_and_other_plugins_are_not_cleanup_candidates(self):
        old = self.root / 'outputs/candidates/old/qcblender-0.0.1.zip'
        other = self.root / 'outputs/qcblender-99.zip'
        project = self.root / 'outputs/qa/portable.zip'
        protected = self.root / 'outputs/projects/user/qcblender-0.0.1.zip'
        make_zip(old, {'blender_manifest.toml': 'id="qcblender"'})
        make_zip(other, {'blender_manifest.toml': 'id="another_plugin"'})
        make_zip(project, {'example.blend': b'owned'})
        make_zip(protected, {'blender_manifest.toml': 'id="qcblender"'})
        report = INVENTORY.inventory(self.root, INVENTORY.LATEST)
        proposed = [row['path'] for row in report['files'] if row['decision'] == 'review-for-deletion']
        self.assertEqual(proposed, [old.relative_to(self.root).as_posix()])
        self.assertEqual(report['groups']['latest-candidate']['files'], 3)
        self.assertEqual(report['groups']['project']['files'], 1)
        self.assertTrue(any(row['path'] == 'outputs/projects' for row in report['excluded_paths']))
        self.assertEqual(report['deletion'], 'Not Run')
        self.assertTrue(all(path.is_file() for path in (old, other, project, protected)))

    def test_changed_latest_candidate_stops_the_inventory(self):
        package = self.latest / 'qcblender-0.1.0.zip'
        package.write_bytes(package.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'identity differs'):
            INVENTORY.inventory(self.root, INVENTORY.LATEST)

    def test_mapped_anonymous_copy_requires_matching_identity(self):
        path = self.root / 'outputs/evidence/2026-10-05/alpha-readiness/objects/example'
        make_zip(path, {'blender_manifest.toml': 'id="qcblender"'})
        mapping = self.root / INVENTORY.MAP_PATH
        record = {'old_path': 'D:/old/ac1/qcblender-0.1.0.zip', 'new_path': str(path),
                  **INVENTORY.file_identity(path)}
        with gzip.open(mapping, 'wt', encoding='utf-8') as stream:
            stream.write(json.dumps(record) + '\n')
        report = INVENTORY.inventory(self.root, INVENTORY.LATEST)
        self.assertEqual(report['groups']['retired-installer-object']['files'], 1)
        path.write_bytes(path.read_bytes() + b'changed')
        changed = INVENTORY.inventory(self.root, INVENTORY.LATEST)
        row = next(row for row in changed['files'] if row['path'].endswith('/objects/example'))
        self.assertEqual(row['decision'], 'keep')
        self.assertEqual(row['inspection'], 'Failed')
        self.assertIn('differs from preservation map', row['reason'])

    def test_reports_cannot_overwrite_or_escape_the_designated_directory(self):
        report = INVENTORY.inventory(self.root, INVENTORY.LATEST)
        destination = self.root / 'validation/agent/reports/test'
        INVENTORY.write_reports(self.root, destination, report)
        before = (destination / 'inventory.json').read_bytes()
        with self.assertRaises(FileExistsError):
            INVENTORY.write_reports(self.root, destination, report)
        self.assertEqual((destination / 'inventory.json').read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'below validation/agent/reports'):
            INVENTORY.write_reports(self.root, self.root / 'outputs/replace', report)
        with self.assertRaisesRegex(ValueError, 'escapes repository'):
            INVENTORY.source_path(self.root, self.root.parent / 'outside.zip')


if __name__ == '__main__':
    unittest.main(verbosity=2)
