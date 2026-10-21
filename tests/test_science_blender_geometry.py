"""Real Dataset/read_metadata/current_geometry chain with only the bpy boundary isolated."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from qcblender.data import Dataset, load_dataset, save_dataset


ROOT = Path(__file__).resolve().parents[1]


class AtomObject(dict):
    type = 'MESH'
    mode = 'OBJECT'


def real_blender_modules():
    # RNA registration and abspath are the only native calls needed by this
    # source-geometry path. Dataset IO and both production functions stay real.
    bpy = ModuleType('bpy')
    bpy.path = SimpleNamespace(abspath=lambda value: value)
    bpy.types = SimpleNamespace(Operator=object)
    bpy.app = SimpleNamespace(handlers=SimpleNamespace(persistent=lambda function: function))
    props = ModuleType('bpy.props')
    props.EnumProperty = props.StringProperty = lambda **kwargs: None
    with patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': props}):
        spec = importlib.util.spec_from_file_location('qcblender.blender.source_browser',
                                                     ROOT / 'qcblender/blender/source_browser.py')
        browser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(browser)
        with patch.dict(sys.modules, {'qcblender.blender.source_browser': browser}):
            spec = importlib.util.spec_from_file_location('qcblender.blender.geometry',
                                                         ROOT / 'qcblender/blender/geometry.py')
            geometry = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(geometry)
    return browser, geometry


class CurrentBlenderGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser, cls.geometry = real_blender_modules()

    def setUp(self):
        output = ROOT / '.tmp/tests/science-blender-geometry'
        output.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / 'dataset'
        self.source = Dataset(
            {'source': {'filename': 'geometry-fixture.xyz', 'sha256': 'a' * 64, 'parser': 'fixture'},
             'selected_job': 0, 'jobs': [{'id': 'source', 'status': 'complete'}],
             'coordinate_unit': 'angstrom', 'title': 'Synthetic source geometry'},
            {'atomic_numbers': np.array([8, 1, 1]),
             'positions': np.array([[0., 0., 0.], [1., .5, 0.], [-.5, 1., .25]])})
        save_dataset(self.source, self.directory)
        self.obj = AtomObject(qc_view_kind='atoms', qc_dataset=str(self.directory),
                              qc_dataset_sha256=hashlib.sha256((self.directory / 'manifest.json').read_bytes()).hexdigest(),
                              qc_source_sha256='a' * 64, qc_source_job=0)
        self.obj.data = SimpleNamespace(vertices=[None] * 3, attributes={
            name: SimpleNamespace(domain='POINT', data_type='INT',
                                  data=[SimpleNamespace(value=value) for value in values])
            for name, values in [('qc_atom_id', [0, 1, 2]), ('qc_atomic_number', [8, 1, 1])]})

    def test_real_metadata_reader_and_dataset_loader_accept_derived_atom_count(self):
        metadata = self.browser.read_metadata(self.obj)
        loaded = load_dataset(self.directory)
        self.assertEqual(metadata['_atom_count'], 3)
        self.assertNotIn('_atom_count', loaded.metadata)
        original = copy.deepcopy(loaded.metadata)
        for data in (None, loaded):
            with self.subTest(explicit_dataset=data is not None):
                positions, record = self.geometry.current_geometry(self.obj, data)
                np.testing.assert_array_equal(positions, self.source.arrays['positions'])
                self.assertEqual(record['source_sha256'], 'a' * 64)
                self.assertEqual(record['selected_job'], 0)
                self.assertEqual(record['dataset_sha256'], self.obj['qc_dataset_sha256'])
        self.assertEqual(loaded.metadata, original)
        self.assertEqual(self.browser.read_metadata(self.obj), metadata)

    def test_real_metadata_changes_in_supplied_dataset_are_rejected(self):
        for key, value in [('title', 'changed'), ('coordinate_unit', 'bohr'),
                           ('jobs', [{'id': 'changed'}]), ('_other', 'not a UI-derived field'),
                           ('source', {'filename': 'other.xyz', 'sha256': 'a' * 64, 'parser': 'fixture'}),
                           ('selected_job', 1)]:
            loaded = load_dataset(self.directory)
            loaded.metadata[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'source identity differs'):
                self.geometry.current_geometry(self.obj, loaded)

    def test_source_sha_job_and_manifest_binding_changes_are_rejected(self):
        for key, value, error in [('qc_source_sha256', 'b' * 64, 'source identity differs'),
                                  ('qc_source_job', 1, 'source identity differs'),
                                  ('qc_dataset_sha256', 'c' * 64, 'manifest differs')]:
            original = self.obj[key]
            self.obj[key] = value
            try:
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, error):
                    self.geometry.current_geometry(self.obj)
            finally:
                self.obj[key] = original

    def test_on_disk_metadata_change_requires_matching_binding(self):
        manifest = self.directory / 'manifest.json'
        record = json.loads(manifest.read_text(encoding='utf-8'))
        record['metadata']['title'] = 'changed on disk'
        manifest.write_text(json.dumps(record), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'manifest differs'):
            self.geometry.current_geometry(self.obj)

    def test_source_atom_order_element_type_and_count_are_still_checked(self):
        for name in ('qc_atom_id', 'qc_atomic_number'):
            attr = self.obj.data.attributes[name]
            original = attr.data[0].value
            attr.data[0].value = 100
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'identities or ordering changed'):
                    self.geometry.current_geometry(self.obj)
            finally:
                attr.data[0].value = original
        self.obj.data.attributes['qc_atom_id'].data_type = 'FLOAT'
        with self.assertRaisesRegex(ValueError, 'identities or ordering changed'):
            self.geometry.current_geometry(self.obj)
        self.obj.data.attributes['qc_atom_id'].data_type = 'INT'
        self.obj.data.vertices.pop()
        with self.assertRaisesRegex(ValueError, 'mesh no longer matches'):
            self.geometry.current_geometry(self.obj)


if __name__ == '__main__':
    unittest.main()
