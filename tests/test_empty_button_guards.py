"""Exercise the object menu's real draw path at the bpy/UI boundary."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_editor():
    bpy = types.ModuleType('bpy')
    bpy.types = types.SimpleNamespace(**{
        name: type(name, (), {}) for name in ('Operator', 'Panel', 'Menu')})
    props = types.ModuleType('bpy.props')
    props.EnumProperty = lambda **kwargs: None
    browser = types.ModuleType('qcblender.blender.source_browser')
    browser.cached_metadata = lambda obj: {}
    modules = {'bpy': bpy, 'bpy.props': props,
               'qcblender.blender.source_browser': browser}
    with patch.dict(sys.modules, modules):
        for name in ('capabilities', 'editor_ui'):
            fullname = 'qcblender.blender.' + name
            spec = importlib.util.spec_from_file_location(
                fullname, ROOT / 'qcblender/blender' / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[fullname] = module
            sys.modules[fullname] = module
    return module


EDITOR = load_editor()


class Layout:
    def __init__(self):
        self.buttons = []

    def operator(self, name, **kwargs):
        self.buttons.append(name)
        return types.SimpleNamespace()

    def row(self):
        return self

    def label(self, **kwargs):
        pass


class Object(dict):
    mode = 'OBJECT'
    qc_settings = types.SimpleNamespace(volume=None)


class EmptyObjectMenu(unittest.TestCase):
    def draw(self, obj):
        layout = Layout()
        context = types.SimpleNamespace(object=obj, selected_objects=[])
        EDITOR.QCBLENDER_MT_object.draw(types.SimpleNamespace(layout=layout), context)
        return layout.buttons

    def test_empty_scene_direct_menu_has_no_object_actions(self):
        self.assertEqual(self.draw(None), [])

    def test_default_cube_direct_menu_has_no_qc_actions(self):
        self.assertEqual(self.draw(Object()), [])

    def test_qc_atom_view_keeps_existing_menu_actions(self):
        buttons = self.draw(Object(qc_view_kind='atoms', qc_dataset='molecule/manifest.json'))
        self.assertEqual(buttons, ['qcblender.source_details', 'qcblender.open_properties',
                                  'qcblender.create_framed_camera',
                                  'qcblender.copy_display_parameters'])


if __name__ == '__main__':
    unittest.main()
