"""Offline boundaries for exact SOP project comparison and portable references."""
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest

from qcblender.data import filesystem_path, unprefixed_path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('verify_sop_project',
    ROOT / 'validation/agent/tools/verify_sop_project.py')
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class SOPProjectTests(unittest.TestCase):
    def fixture(self):
        raw = {'identity': {'pid': 12, 'filepath': 'old/project.blend'}, 'state': {
            'active': 'atoms', 'screens': {'Layout': [100, 200]}, 'frame': 2,
            'objects': {'atoms': {'selected': True, 'hidden': False, 'hide_render': False,
                'parent': None, 'properties': {'qc_association': 'same source identity'}}},
            'datasets': {'atoms': {'metadata_sha256': 'meta', 'arrays': {
                'positions': {'dtype': '<f8', 'shape': [6, 3], 'sha256': 'original'}}}},
            'groups': {'atoms': {'nodes': [{'inputs': [['radius', .25]]}], 'links': [['a', 'b']]}}}}
        return checker.canonical_snapshot(raw, {'atoms': 'project.qcdata/datasets/meta'},
            {'project.qcdata/manifest.json': {'sha256': 'index', 'bytes': 20}}, {})

    def test_arrays_dtype_shape_values_and_metadata_are_not_ignored(self):
        baseline = self.fixture()
        for field, value in [('dtype', '<f4'), ('shape', [3, 6]), ('sha256', 'changed')]:
            actual = deepcopy(baseline)
            actual['state']['datasets']['atoms']['arrays']['positions'][field] = value
            result = checker.compare_snapshots(baseline, actual)
            self.assertEqual(result['status'], 'Failed')
            self.assertTrue(any(field in path for path in result['differences']))
        actual = deepcopy(baseline)
        actual['state']['datasets']['atoms']['metadata_sha256'] = 'changed'
        self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')

    def test_nodes_visibility_association_and_annotation_changes_fail(self):
        for section, key, value in [('objects', 'hidden', True), ('objects', 'hide_render', True),
                                    ('objects', 'parent', 'another-source')]:
            baseline, actual = self.fixture(), self.fixture()
            actual['state'][section]['atoms'][key] = value
            self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')
        for change in ('socket', 'link', 'annotation', 'material'):
            baseline, actual = self.fixture(), self.fixture()
            if change == 'socket':
                actual['state']['groups']['atoms']['nodes'][0]['inputs'][0][1] = .5
            elif change == 'link':
                actual['state']['groups']['atoms']['links'] = []
            elif change == 'annotation':
                actual['state']['objects']['atoms']['properties']['qc_annotation'] = 'new text or geometry'
            else:
                actual['state']['persistent']['materials'] = {'shared': {'roughness': .9}}
            self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')

    def test_only_transient_selection_and_window_state_are_removed(self):
        baseline = self.fixture()
        self.assertNotIn('screens', baseline['state'])
        self.assertNotIn('active', baseline['state'])
        self.assertNotIn('selected', baseline['state']['objects']['atoms'])
        actual = deepcopy(baseline)
        actual['project'], actual['execution'] = 'moved/project.blend', {'pid': 99}
        self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Passed')
        actual['state']['frame'] = 3
        self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')

    def test_moved_roots_normalize_but_external_runtime_paths_are_rejected(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs', prefix='sop-project-') as folder:
            base = Path(folder)
            normalized = []
            for name in ('original', '中文 moved'):
                root = base / name
                resource = root / 'project.qcdata/datasets/id/field.vdb'
                resource.parent.mkdir(parents=True)
                resource.write_bytes(b'cache')
                normalized.append(checker.project_reference(resource, root))
            self.assertEqual(normalized[0], normalized[1])
            with self.assertRaisesRegex(ValueError, 'outside saved project'):
                checker.project_reference(base / 'original/project.qcdata/datasets/id/field.vdb', base / '中文 moved')

    def test_provenance_is_not_rewritten_and_resource_hash_changes_fail(self):
        baseline, actual = self.fixture(), self.fixture()
        baseline['state']['objects']['atoms']['properties']['source_filename'] = 'C:/original/input.fchk'
        actual['state']['objects']['atoms']['properties']['source_filename'] = 'D:/other/input.fchk'
        self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')
        actual = deepcopy(baseline)
        actual['state']['resources']['project.qcdata/manifest.json']['sha256'] = 'changed'
        self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')

    def test_long_runtime_file_reference_and_digest_use_real_windows_io(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        folder = Path(tempfile.mkdtemp(dir=ROOT / 'outputs', prefix='sop-long-path-'))
        self.addCleanup(shutil.rmtree, filesystem_path(folder))
        root = folder / ('project-location-' + 'x' * 60) / ('nested-' + 'y' * 60)
        relative = Path('project.qcdata') / 'datasets' / ('a' * 64) / 'arrays' / ('b' * 64 + '.npy')
        resource = root / relative
        self.assertGreater(len(str(resource)), 260)
        filesystem_path(resource.parent).mkdir(parents=True)
        content = b'actual long-path byte fixture'
        filesystem_path(resource).write_bytes(content)
        self.assertTrue(filesystem_path(resource).is_file())
        for label, value in [('ordinary', resource), ('extended', filesystem_path(resource))]:
            with self.subTest(operation='reference', syntax=label):
                self.assertEqual(checker.project_reference(value, root), relative.as_posix())
            with self.subTest(operation='digest', syntax=label):
                self.assertEqual(checker.digest(value), hashlib.sha256(content).hexdigest())
        other_root = folder / 'different-root'
        other_root.mkdir()
        with self.assertRaisesRegex(ValueError, 'outside saved project'):
            checker.project_reference(filesystem_path(resource), other_root)
        self.assertEqual(unprefixed_path(filesystem_path(root)), root)

    def test_schema_and_removed_objects_cannot_silently_pass(self):
        baseline, actual = self.fixture(), self.fixture()
        actual['state']['objects'].clear()
        self.assertEqual(checker.compare_snapshots(baseline, actual)['status'], 'Failed')
        actual['schema'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'schema'):
            checker.compare_snapshots(baseline, actual)

    def test_existing_collector_receives_only_used_real_datablocks(self):
        used, orphan = object(), object()
        bpy = SimpleNamespace(data=SimpleNamespace(objects=[used, orphan],
            node_groups=[], materials=[], fonts={}), context=object())
        original = lambda: bpy
        ops = SimpleNamespace(_bpy=original)
        def collect():
            self.assertIs(ops._bpy().context, bpy.context)
            return list(ops._bpy().data.objects)
        ops._snapshot = collect
        self.assertEqual(checker._used_snapshot(ops, bpy, {'used': used}, {}, {}, {}), [used])
        self.assertIs(ops._bpy, original)
        self.assertEqual(bpy.data.objects, [used, orphan])

    def test_collector_failure_restores_the_existing_collector_binding(self):
        bpy = SimpleNamespace(data=SimpleNamespace(fonts={}))
        original = lambda: bpy
        def fail():
            raise ValueError('unreadable real dataset')
        ops = SimpleNamespace(_bpy=original, _snapshot=fail)
        with self.assertRaisesRegex(ValueError, 'unreadable real dataset'):
            checker._used_snapshot(ops, bpy, {}, {}, {}, {})
        self.assertIs(ops._bpy, original)


if __name__ == '__main__':
    unittest.main()
