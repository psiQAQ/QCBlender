"""View summaries use live configuration inputs at the Blender-state seam."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_snapshot_module():
    copy = ModuleType('qcblender.blender.copy_display')
    copy._state = lambda obj: obj.state
    copy._material_role = lambda mat, role: mat.controls
    browser = ModuleType('qcblender.blender.source_browser')
    browser.source_object = lambda obj: obj
    browser.read_metadata = lambda obj: obj.metadata
    browser.binding_key = lambda obj: ('dataset', obj['qc_dataset_sha256'])
    browser.bound_field = lambda obj: (obj, obj.field, obj.metadata, obj.metadata['source'])
    browser.field_source = lambda meta, field: meta['source']
    browser.mapped_field = lambda obj: (obj, obj.field, obj.metadata)
    browser.object_record = lambda obj, key: obj.field
    spec = importlib.util.spec_from_file_location('qcblender.blender._summary_test',
                                                 ROOT / 'qcblender/blender/view_summary.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {copy.__name__: copy, browser.__name__: browser}):
        spec.loader.exec_module(module)
    return module


capture = load_snapshot_module()


class View(dict):
    name = '实时视图'
    matrix_world = ((1., 0., 0., 0.), (0., 1., 0., 0.), (0., 0., 1., 0.), (0., 0., 0., 1.))


class Modifier(dict):
    name = 'QC test display'


class ViewSummary(unittest.TestCase):
    def view(self):
        obj = View(qc_dataset_sha256='a' * 64, qc_source_sha256='b' * 64,
                   qc_view_kind='field', qc_field='stored', qc_old_isovalue=.99)
        obj.field = {'array': 'values', 'quantity': 'orbital_amplitude', 'unit': 'bohr^-3/2'}
        obj.metadata = {'source': {'sha256': 'b' * 64}, 'fields': [obj.field]}
        obj.state = {'modifier': Modifier(threshold=.03),
                     'sockets': {'Isovalue': SimpleNamespace(identifier='threshold', socket_type='NodeSocketFloat')},
                     'materials': {}}
        return obj

    def test_live_modifier_value_replaces_stale_object_record(self):
        obj = self.view()
        first = capture.capture_view_summary(obj, 7)
        obj.state['modifier']['threshold'] = .06
        second = capture.capture_view_summary(obj, 8)
        self.assertEqual(first['display']['parameters'][0]['value'], .03)
        self.assertEqual(second['display']['parameters'][0]['value'], .06)
        self.assertEqual(second['view']['scene_frame'], 8)
        self.assertIn('bohr^-3/2', second['display']['parameters'][0]['label'])
        self.assertEqual(obj['qc_old_isovalue'], .99)

    def test_missing_modifier_input_is_partial_without_default(self):
        obj = self.view()
        obj.state['modifier'].clear()
        obj.state['sockets']['Isovalue'].default_value = .99
        result = capture.capture_view_summary(obj, 1)['display']
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['parameters'], [])
        self.assertIn('no default', result['reasons'][0])

    def test_custom_graph_has_no_stale_input_values(self):
        obj = self.view()
        with patch.object(capture, '_state', side_effect=ValueError('Disconnected threshold')):
            result = capture.capture_view_summary(obj, 1)
        self.assertEqual(result['display']['status'], 'unverified')
        self.assertEqual(result['display']['parameters'], [])
        self.assertIn('Disconnected', result['display']['reasons'][0])
        self.assertEqual(result['fields']['geometry']['field'], obj.field)

    def test_missing_material_input_does_not_export_socket_default(self):
        obj = self.view()
        mat = SimpleNamespace(name='Default material', controls={}, node_tree=SimpleNamespace(nodes=[]))
        modifier = obj.state['modifier']
        obj.state['sockets']['Material'] = SimpleNamespace(
            identifier='material', socket_type='NodeSocketMaterial', default_value=mat)
        obj.state['materials']['Material'] = (mat, [('socket', modifier, 'material')])
        result = capture.capture_view_summary(obj, 1)['display']
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['materials'], [])
        self.assertNotIn('Material', [item['name'] for item in result['parameters']])
        self.assertTrue(any('Material' in reason and 'no default' in reason for reason in result['reasons']))

    def test_live_material_ramp_and_opacity(self):
        obj = self.view()
        element = SimpleNamespace(position=.5, color=[.1, .2, .3, 1.])
        ramp = SimpleNamespace(color_mode='RGB', interpolation='LINEAR', hue_interpolation='NEAR', elements=[element])
        color = SimpleNamespace(name='Live color', color_ramp=ramp)
        scale = SimpleNamespace(name='Live scale', bl_idname='ShaderNodeValue', outputs=[SimpleNamespace(default_value=20.)])
        mat = View(qc_fog=True)
        mat.name = 'Live material'
        mat.controls = {'color_ramp': color, 'Opacity Scale': scale}
        mat.node_tree = SimpleNamespace(nodes=[])
        obj.state['materials'] = {'Material': (mat, [])}
        before = capture.capture_view_summary(obj, 1)
        element.color[0] = .7
        scale.outputs[0].default_value = 40.
        after = capture.capture_view_summary(obj, 1)
        controls = {item['name']: item['value'] for item in after['display']['materials'][0]['controls']}
        self.assertEqual(controls['Opacity Scale'], 40.)
        self.assertEqual(controls['color_ramp']['elements'][0]['color'][0], .7)
        self.assertEqual(before['display']['materials'][0]['controls'][0]['value']['elements'][0]['color'][0], .1)

    def test_custom_emission_material_is_partial_with_explicit_reason(self):
        obj = self.view()
        mat = View()
        mat.name = 'Custom emission'
        mat.controls = {}
        mat.node_tree = SimpleNamespace(nodes=[SimpleNamespace(bl_idname='ShaderNodeEmission')])
        obj.state['materials'] = {'Material': (mat, [])}
        result = capture.capture_view_summary(obj, 1)['display']
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['materials'][0]['controls'], [])
        self.assertTrue(any('Surface shader' in reason and 'unverified' in reason for reason in result['reasons']))

    def test_source_identity_mismatch_fails(self):
        obj = self.view()
        obj['qc_source_sha256'] = 'c' * 64
        self.assertRaisesRegex(ValueError, 'source differs', capture.capture_view_summary, obj, 1)


if __name__ == '__main__':
    unittest.main()
