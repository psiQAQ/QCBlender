"""Capability regression at the saved-metadata seam, without a Blender process."""
import importlib
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class View(dict):
    mode = 'OBJECT'
    parent = None


class StaticReferenceCapabilities(unittest.TestCase):
    def setUp(self):
        self.original = sys.modules.get('qcblender.blender.source_browser')
        browser = ModuleType('qcblender.blender.source_browser')
        browser.cached_metadata = lambda obj: obj.metadata if obj is not None else {}
        sys.modules[browser.__name__] = browser
        sys.modules.pop('qcblender.blender.capabilities', None)
        self.capability = importlib.import_module('qcblender.blender.capabilities').capability

    def tearDown(self):
        sys.modules.pop('qcblender.blender.capabilities', None)
        if self.original is None:
            sys.modules.pop('qcblender.blender.source_browser', None)
        else:
            sys.modules['qcblender.blender.source_browser'] = self.original

    def view(self, metadata):
        obj = View(qc_dataset='saved', qc_view_kind='field',
                   qc_field='{"quantity":"electrostatic_potential"}',
                   qc_analysis_role='ets_nocv')
        obj.metadata = dict(source={'sha256': 'source'}, analysis={'pairs': [1]}, **metadata)
        return obj

    def test_dynamic_references_and_ancestors_are_disabled(self):
        for metadata in ({'optimization': {'status': 'available', 'steps': [1]}},
                         {'trajectory': {'frames': [1, 2]}},
                         {'analysis': {'kind': 'IRC', 'steps': [1, 2]}}):
            obj = self.view({})
            obj.metadata.update(metadata)
            for ancestor in (False, True):
                target = self.view({}) if ancestor else obj
                if ancestor:
                    target.parent = obj
                for action in ('aim', 'paired', 'nbo', 'nocv_table', 'esp', 'nocv_field'):
                    with self.subTest(metadata=metadata, ancestor=ancestor, action=action):
                        relevant, enabled, reason = self.capability(SimpleNamespace(object=target), action)
                        self.assertTrue(relevant)
                        self.assertFalse(enabled)
                        self.assertIn('独立', reason)

    def test_static_and_unavailable_optimization_remain_enabled(self):
        for metadata in ({}, {'optimization': {'status': 'unavailable', 'steps': []}}):
            obj = self.view(metadata)
            for action in ('aim', 'paired', 'nbo', 'nocv_table', 'esp', 'nocv_field'):
                with self.subTest(metadata=metadata, action=action):
                    self.assertTrue(self.capability(SimpleNamespace(object=obj), action)[1])


if __name__ == '__main__':
    unittest.main()
