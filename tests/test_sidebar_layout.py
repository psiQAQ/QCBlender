"""Exercise panel draws and navigation at Blender's layout/context boundary."""
import ast
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from qcblender import i18n

ROOT = Path(__file__).resolve().parents[1]


class Layout:
    def __init__(self, calls=None):
        self.calls = calls if calls is not None else []
        self.enabled = True

    def operator(self, name, **kwargs):
        item = SimpleNamespace(name=name, **kwargs)
        self.calls.append(item)
        return item

    def label(self, **kwargs):
        self.calls.append(SimpleNamespace(name='label', **kwargs))

    def separator(self):
        pass

    def row(self, **kwargs):
        return Layout(self.calls)

    box = row
    grid_flow = row


class Object(dict):
    def __init__(self, name='Molecule', **props):
        super().__init__(props)
        self.name, self.parent, self.mode = name, None, 'OBJECT'
        self.hidden, self.hide_viewport, self.hide_render, self.selected = False, False, False, False
        self.qc_settings = SimpleNamespace(volume=None)

    def hide_get(self):
        return self.hidden

    def select_set(self, value):
        self.selected = value


def load_editor(browser):
    bpy = ModuleType('bpy')
    bpy.types = SimpleNamespace(**{name: type(name, (), {}) for name in ('Operator', 'Panel', 'Menu')})
    props = ModuleType('bpy.props')
    props.EnumProperty = lambda **kwargs: None
    spec = importlib.util.spec_from_file_location('qcblender.blender._sidebar_test', ROOT / 'qcblender/blender/editor_ui.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': props, 'qcblender.blender.source_browser': browser}):
        spec.loader.exec_module(module)
    return module


def load_layers(browser):
    tree = ast.parse((ROOT / 'qcblender/blender/layers.py').read_text(encoding='utf-8'))
    names = {'display_layers', 'QCBLENDER_PT_layers', 'QCBLENDER_PT_layer_management', 'QCBLENDER_OT_layer_action'}
    body = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names]
    namespace = {'__package__': 'qcblender.blender', 'ui_layout': i18n.ui_layout, 'iface': i18n.iface,
                 'error_text': i18n.error_text, 'EnumProperty': lambda **kwargs: None, 'StringProperty': lambda **kwargs: None,
                 'bpy': SimpleNamespace(types=SimpleNamespace(Panel=type('Panel', (), {}), Operator=type('Operator', (), {})))}
    exec(compile(ast.Module(body=body, type_ignores=[]), '<real-layer-panels>', 'exec'), namespace)
    return SimpleNamespace(**namespace)


class SidebarLayout(unittest.TestCase):
    def setUp(self):
        self.browser = ModuleType('qcblender.blender.source_browser')
        self.browser.cached_metadata = lambda obj: {}
        self.browser.source_object = lambda obj: obj.parent if 'qc_annotation' in obj and obj.parent else obj
        self.browser.source_group = lambda obj: ('source', 'source.xyz')
        self.browser.cached_object_summary = lambda obj: dict(available=True, state='ready', short=[], details=[], categories=[])
        self.editor = load_editor(self.browser)
        self.layers = load_layers(self.browser)
        self.obj = Object(qc_view_kind='atoms', qc_dataset='dataset')
        self.objects = {self.obj.name: self.obj}
        self.context = SimpleNamespace(object=self.obj, region=SimpleNamespace(width=240),
            scene=SimpleNamespace(objects=[self.obj]), selected_objects=[self.obj],
            view_layer=SimpleNamespace(objects=SimpleNamespace(get=self.objects.get, active=self.obj)))
        export = ModuleType('qcblender.blender.data_export')
        export.export_choices = lambda *args: [('DATA', 'Data', '')]
        patcher = patch.dict(sys.modules, {'qcblender.blender.source_browser': self.browser,
                                         'qcblender.blender.data_export': export})
        patcher.start()
        self.addCleanup(patcher.stop)

    def draw(self, cls):
        layout = Layout()
        cls.draw(SimpleNamespace(layout=layout), self.context)
        return [item for item in layout.calls if item.name != 'label']

    def test_sidebar_has_workflow_and_inspection_but_no_object_editors(self):
        classes = [self.editor.QCBLENDER_PT_main, self.editor.QCBLENDER_PT_dataset,
                   self.editor.QCBLENDER_PT_dataset_details, self.editor.QCBLENDER_PT_external_import,
                   self.editor.QCBLENDER_PT_project, self.layers.QCBLENDER_PT_layers]
        with patch.object(self.editor, '_action_group', lambda layout, context, title, actions:
                          [layout.operator(op) for _, op, _ in actions]):
            calls = [item for cls in classes for item in self.draw(cls)]
        allowed = {'import_calculation', 'import_irc_path', 'import_paired_field', 'import_esp_analysis',
                   'import_nbo', 'import_aim_analysis', 'import_ets_nocv', 'import_nocv_field',
                   'export_data', 'open_properties', 'save_project', 'archive_project', 'rebuild_cache',
                   'relocate_dataset', 'cleanup_legacy_node_assets', 'check_runtime', 'layer_action',
                   'import_surface_projection', 'import_aicd'}
        self.assertEqual({item.name.removeprefix('qcblender.') for item in calls}, allowed)
        self.assertEqual(sum(item.name == 'qcblender.open_properties' for item in calls), 1)
        self.assertEqual([item.action for item in calls if item.name == 'qcblender.layer_action'], ['SELECT'])
        self.assertFalse(hasattr(self.editor.QCBLENDER_PT_dataset, 'bl_options'))
        self.assertIn('DEFAULT_CLOSED', self.layers.QCBLENDER_PT_layers.bl_options)

    def test_object_tools_and_layer_controls_have_properties_destinations(self):
        self.assertEqual(self.editor.QCBLENDER_PT_create.bl_space_type, 'PROPERTIES')
        with patch.object(self.editor, '_action_group', lambda layout, context, title, actions:
                          [layout.operator(op) for _, op, _ in actions]), patch.object(
                          self.editor, 'action_button', lambda layout, context, action, op, *args: layout.operator(op)), patch.object(
                          self.editor, 'capability', return_value=(True, True, '')), patch.object(
                          self.editor, 'draw_probe_actions', lambda layout, context: layout.operator('qcblender.click_probe')):
            calls = self.draw(self.editor.QCBLENDER_PT_create)
        names = {item.name for item in calls}
        self.assertTrue({'qcblender.generate_field', 'qcblender.local_selection_layer', 'qcblender.create_slice',
                         'qcblender.probe_field', 'qcblender.click_probe', 'qcblender.create_framed_camera'} <= names)
        self.assertNotIn('qcblender.add_annotation', names)
        self.assertNotIn('qcblender.optimization_view', names)
        calls = self.draw(self.layers.QCBLENDER_PT_layer_management)
        self.assertEqual({item.action for item in calls}, {'VISIBILITY', 'RENDER', 'DUPLICATE', 'REMOVE', 'UP', 'DOWN'})
        self.assertTrue(all(item.target == self.obj.name for item in calls))

    def test_navigation_does_not_unhide_or_change_render_state(self):
        self.obj.hidden = self.obj.hide_render = True
        self.context.scene.objects = self.objects
        operator = SimpleNamespace(action='SELECT', target=self.obj.name, report=lambda *args: None)
        # display_layers iterates Blender's object collection, not mapping keys.
        self.layers.QCBLENDER_OT_layer_action.execute.__globals__['display_layers'] = lambda scene: [self.obj]
        self.assertEqual(self.layers.QCBLENDER_OT_layer_action.execute(operator, self.context), {'FINISHED'})
        self.assertTrue(self.obj.hidden)
        self.assertTrue(self.obj.hide_render)
        self.assertIs(self.context.view_layer.objects.active, self.obj)

    def test_sidebar_subject_does_not_reuse_old_object_or_properties_pin(self):
        self.assertIsNone(self.editor.sidebar_subject(None))
        self.assertIsNone(self.editor.sidebar_subject(Object('Cube')))
        child = Object('Label', qc_annotation='{}')
        child.parent = self.obj
        self.assertIs(self.editor.sidebar_subject(child), self.obj)
        other = Object('Other', qc_view_kind='atoms', qc_dataset='other')
        space = SimpleNamespace(pin_id=other, use_pin_id=True, context='MATERIAL')
        self.context.screen = SimpleNamespace(areas=[SimpleNamespace(type='PROPERTIES', spaces=SimpleNamespace(active=space), tag_redraw=lambda: None)])
        self.context.object = child
        result = self.editor.QCBLENDER_OT_open_properties.execute(SimpleNamespace(editor='OBJECT'), self.context)
        self.assertEqual(result, {'FINISHED'})
        self.assertIs(space.pin_id, self.obj)
        self.assertIs(self.context.object, child)

    def test_cjk_and_long_source_text_are_bounded(self):
        lines = self.editor.compact_lines('来源文件很长' * 100, 18)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[-1].endswith('…'))
        self.assertTrue(all(len(line) <= 10 for line in lines))


if __name__ == '__main__':
    unittest.main()
