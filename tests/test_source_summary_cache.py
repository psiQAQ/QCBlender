"""Real cache/manifest logic with only bpy and scientific storage imports isolated."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_browser():
    bpy = ModuleType('bpy')
    bpy.path = SimpleNamespace(abspath=lambda path: path)
    bpy.types = SimpleNamespace(Operator=object)
    bpy.app = SimpleNamespace(handlers=SimpleNamespace(persistent=lambda function: function))
    props = ModuleType('bpy.props')
    props.EnumProperty = props.StringProperty = lambda **kwargs: None
    storage = ModuleType('qcblender.data')
    storage.SCHEMA = '0.1'
    storage.dataset_path_key = lambda path: path
    storage.filesystem_path = Path
    with patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': props, 'qcblender.data': storage}):
        spec = importlib.util.spec_from_file_location('qcblender.blender.source_browser',
                                                     ROOT / 'qcblender/blender/source_browser.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class Object(dict):
    def __init__(self, name, parent=None, **properties):
        super().__init__(properties)
        self.name, self.parent = name, parent

    @property
    def data(self):
        raise AssertionError('A summary must not inspect the mesh')


class DescriptorOnlyArray:
    def __init__(self, shape, dtype='<f8'):
        self.shape, self.dtype = shape, SimpleNamespace(str=dtype)

    def __len__(self):
        return self.shape[0]

    def __iter__(self):
        raise AssertionError('A summary must not inspect array values')


class SourceSummaryCache(unittest.TestCase):
    def setUp(self):
        self.browser = load_browser()
        self.owner = Object('Owner', qc_view_kind='atoms', qc_dataset='fixture.qcdata', qc_dataset_sha256='binding')
        self.meta = {'source': {'filename': 'water.xyz', 'parser': 'fixture'}, 'coordinate_unit': 'angstrom',
                     'trajectory': {'frames': [{}] * 3}}
        self.data = SimpleNamespace(metadata=self.meta, arrays={
            'atomic_numbers': DescriptorOnlyArray((12,), '<i4'),
            'positions': DescriptorOnlyArray((12, 3)),
            'trajectory_positions': DescriptorOnlyArray((3, 12, 3))})

    def rows(self, result):
        return {row['key']: row for row in result['short']}

    def test_bind_caches_descriptors_without_io_or_array_values(self):
        with patch.object(Path, 'open', side_effect=AssertionError('No disk IO')):
            self.browser.cache_dataset(self.owner, self.data)
            result = self.browser.cached_object_summary(self.owner)
        self.assertEqual(self.rows(result)['atom_count']['value'], 12)
        self.assertEqual(result['categories'][3]['items'][0]['shape'], [3, 12, 3])
        self.assertNotIn('_atom_count', self.meta)
        self.assertNotIn('_array_descriptors', self.meta)

    def test_active_child_owner_and_live_steps_never_follow_other_objects(self):
        self.browser.cache_dataset(self.owner, self.data)
        self.owner['qc_trajectory_frame'] = 2
        annotation = Object('Label', parent=self.owner, qc_annotation='{}')
        with patch.object(self.browser, 'read_metadata', side_effect=AssertionError('No refresh during draw')):
            result = self.browser.cached_object_summary(annotation)
            self.assertEqual(self.rows(result)['owner']['value'], 'Owner')
            self.assertEqual(self.rows(result)['xyz']['value'], '2 / 3')
            self.owner['qc_trajectory_frame'] = 3
            self.assertEqual(self.rows(self.browser.cached_object_summary(annotation))['xyz']['value'], '3 / 3')
            for obj in (None, Object('Cube', parent=self.owner)):
                self.assertFalse(self.browser.cached_object_summary(obj)['available'])
            raw_volume = Object('Volume', qc_dataset='fixture.qcdata')
            raw_summary = self.browser.cached_object_summary(raw_volume)
            self.assertTrue(raw_summary['available'])
            self.assertEqual(raw_summary['state'], 'uncached')

    def test_cache_binding_identity_prevents_reusing_another_manifest(self):
        self.browser.cache_dataset(self.owner, self.data)
        self.owner['qc_dataset_sha256'] = 'other'
        result = self.browser.cached_object_summary(self.owner)
        self.assertEqual(result['state'], 'uncached')
        self.assertIsNone(self.rows(result)['atom_count']['value'])

    def test_manifest_only_refresh_does_not_require_array_files(self):
        output = ROOT / '.tmp/tests/source-summary-cache'
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as directory:
            manifest = Path(directory) / 'manifest.json'
            record = {'format': 'qcblender.project', 'schema': '0.1', 'metadata': self.meta,
                      'arrays': {'atomic_numbers': {'shape': [12], 'dtype': '<i4', 'path': 'absent.npy'},
                                 'trajectory_positions': {'shape': [3, 12, 3], 'dtype': '<f8', 'path': 'absent.npy'}}}
            raw = json.dumps(record).encode('utf-8')
            manifest.write_bytes(raw)
            self.owner.update(qc_dataset=directory, qc_dataset_sha256=hashlib.sha256(raw).hexdigest())
            meta = self.browser.read_metadata(self.owner)
            self.assertEqual(meta, dict(self.meta, _atom_count=12))
            self.browser._metadata[self.browser.binding_key(self.owner)] = meta
            self.assertEqual(self.browser.cached_object_summary(self.owner)['categories'][3]['items'][0]['shape'], [3, 12, 3])
            manifest.unlink()
            # The cache still works even when its explicitly refreshed manifest
            # becomes unavailable; a subsequent refresh must show that failure.
            self.assertEqual(self.browser.cached_object_summary(self.owner)['state'], 'ready')
            self.browser.refresh_source(self.owner)
            self.assertEqual(self.browser.cached_object_summary(self.owner)['state'], 'error')
            self.assertNotIn(self.browser.binding_key(self.owner), self.browser._array_descriptors)

    def test_color_field_uses_its_own_source_and_cache_clears_together(self):
        self.data.metadata = dict(self.meta, analysis={'color_source': {'filename': 'color.cube', 'parser': 'cube'}})
        field = Object('Color field', qc_view_kind='field', qc_dataset='fixture.qcdata', qc_dataset_sha256='binding',
                       qc_field=json.dumps({'role': 'color'}))
        self.browser.cache_dataset(field, self.data)
        self.assertEqual(self.rows(self.browser.cached_object_summary(field))['source']['value'], 'color.cube')
        self.browser.clear_source_cache()
        self.assertEqual(self.browser._metadata, {})
        self.assertEqual(self.browser._array_descriptors, {})
        self.assertEqual(self.browser.cached_object_summary(field)['state'], 'uncached')


if __name__ == '__main__':
    unittest.main()
