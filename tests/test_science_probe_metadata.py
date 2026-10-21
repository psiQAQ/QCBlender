"""Probe identity uses actual manifest/binding/Dataset IO; only bpy is isolated."""
import ast
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

import test_property_viewport_context as boundary_module

ROOT = Path(__file__).resolve().parents[1]


class ProbeScientificMetadata(unittest.TestCase):
    def setUp(self):
        boundary = boundary_module.PropertyViewportContext('test_probe_invocation_captures_pin_and_selected_viewport')
        boundary.setUp()
        for name in ('bpy', 'namespace', 'pinned', 'context', 'helper'):
            setattr(self, name, getattr(boundary, name))
        self.probe, self.event = boundary.probe, boundary.event

    def real_dataset_probe(self):
        """Use actual manifest reader, binding checks, Dataset IO and profile resolver."""
        import numpy as np
        from qcblender.data import Dataset, load_dataset, save_dataset
        output = ROOT / '.tmp/tests/property-viewport-context'
        output.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name) / 'field'
        field = {'array': 'values', 'valid_mask': 'valid', 'unit': 'e', 'quantity': 'test',
                 'shape': [2, 2, 2], 'origin': [0., 0., 0.], 'steps': np.eye(3).tolist()}
        metadata = {'source': {'sha256': 'a' * 64, 'filename': 'synthetic.cube', 'parser': 'fixture'},
                    'coordinate_unit': 'angstrom', 'selected_job': 0, 'fields': [field]}
        save_dataset(Dataset(metadata, {'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3)),
            'values': np.ones((2, 2, 2)), 'valid': np.ones((2, 2, 2), dtype=bool)}), directory)
        props = ModuleType('bpy.props')
        props.EnumProperty = props.StringProperty = lambda **kwargs: None
        self.bpy.app = SimpleNamespace(handlers=SimpleNamespace(persistent=lambda fn: fn))
        self.bpy.path = SimpleNamespace(abspath=lambda value: value)
        with patch.dict(sys.modules, {'bpy': self.bpy, 'bpy.props': props}):
            spec = importlib.util.spec_from_file_location('qcblender.blender.source_browser',
                ROOT / 'qcblender/blender/source_browser.py')
            browser = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(browser)
        source = boundary_module.Object('volume', qc_view_kind='volume', qc_field=json.dumps(field))
        for obj in (source, self.pinned):
            obj.update(qc_dataset=str(directory), qc_dataset_sha256=hashlib.sha256(
                (directory / 'manifest.json').read_bytes()).hexdigest(), qc_source_sha256='a' * 64,
                qc_source_job=0, qc_field=json.dumps(field))
        self.pinned.qc_settings = SimpleNamespace(volume=source)
        tree = ast.parse((ROOT / 'qcblender/blender/profile.py').read_text(encoding='utf-8'))
        resolver = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'profile_source')
        resolver_namespace = {'json': json, 'read_metadata': browser.read_metadata}
        exec(compile(ast.Module(body=[resolver], type_ignores=[]), 'profile.py', 'exec'), resolver_namespace)
        cls, operator = self.probe()
        self.namespace.update(bound_field=browser.bound_field, field_source=browser.field_source,
            binding_key=browser.binding_key, profile_source=resolver_namespace['profile_source'],
            load_dataset=load_dataset)
        return operator, browser, directory


    def test_probe_real_manifest_derived_count_does_not_change_scientific_identity(self):
        operator, browser, directory = self.real_dataset_probe()
        before = copy.deepcopy(browser.read_metadata(self.pinned))
        self.assertEqual(before['_atom_count'], 1)
        self.assertEqual(operator.invoke(self.context, self.event()), {'RUNNING_MODAL'})
        self.assertEqual(operator._sample_meta, before)
        self.assertEqual(browser.read_metadata(self.pinned), before)
        self.assertNotIn('_atom_count', operator._data.metadata)
        operator._check_binding(self.context)
        self.assertEqual(operator.modal(self.context, self.event('ESC')), {'CANCELLED'})


    def test_probe_real_metadata_changes_other_than_ui_count_are_rejected(self):
        from qcblender.data import load_dataset
        operator, browser, directory = self.real_dataset_probe()
        before = copy.deepcopy(browser.read_metadata(self.pinned))
        for key, value in [('title', 'changed'), ('selected_job', 1), ('_other', 'unknown'),
                           ('source', {'sha256': 'b' * 64, 'filename': 'other.cube', 'parser': 'fixture'})]:
            loaded = load_dataset(directory)
            loaded.metadata[key] = value
            self.namespace['load_dataset'] = lambda path, loaded=loaded: loaded
            with self.subTest(key=key):
                self.assertEqual(operator.invoke(self.context, self.event()), {'CANCELLED'})
                self.assertIn('Dataset changed', operator.messages[-1])
                self.assertEqual(browser.read_metadata(self.pinned), before)


if __name__ == '__main__':
    unittest.main()
