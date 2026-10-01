"""Pure Python checks for the boundaries of saved fog material slot repair."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    graph_spec = importlib.util.spec_from_file_location(
        'qcblender.blender.graph', ROOT / 'qcblender/blender/graph.py')
    graph = importlib.util.module_from_spec(graph_spec)
    graph_spec.loader.exec_module(graph)
    timers = {}
    bpy = types.ModuleType('bpy')
    bpy.types = types.SimpleNamespace(Operator=type('Operator', (), {}))
    bpy.data = types.SimpleNamespace(objects=[])
    bpy.app = types.SimpleNamespace(
        handlers=types.SimpleNamespace(persistent=lambda callback: callback, load_post=[], save_post=[]),
        timers=types.SimpleNamespace(is_registered=lambda callback: callback in timers,
                                    register=lambda callback, **kwargs: timers.update({callback: kwargs}),
                                    unregister=lambda callback: timers.pop(callback)))
    views = types.ModuleType('qcblender.blender.views')
    views.group_sockets = views.socket = lambda *args, **kwargs: None
    spec = importlib.util.spec_from_file_location(
        'qcblender.blender._fog_test', ROOT / 'qcblender/blender/fog.py')
    fog = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'bpy': bpy, 'qcblender.blender.graph': graph,
                                  'qcblender.blender.views': views}):
        spec.loader.exec_module(fog)
    return fog, graph, timers


fog, graph, timers = load_module()


class FogObject(dict):
    def __init__(self):
        super().__init__(qc_view_kind='fog', qc_dataset='unchanged')
        self.type, self.library, self.is_editable = 'MESH', None, True
        self.data = types.SimpleNamespace(materials=[], library=None, is_editable=True)
        record = {'qc_fog': True}
        self.mat = types.SimpleNamespace(use_nodes=True, get=record.get)
        source = types.SimpleNamespace(identifier='material',
                                       node=types.SimpleNamespace(bl_idname='NodeGroupInput'))
        group = types.SimpleNamespace(bl_idname='GeometryNodeGroup',
                                      node_tree={'qc_asset_id': 'qc.volume_fog.v1'},
                                      inputs={'Material': types.SimpleNamespace(
                                          links=[types.SimpleNamespace(from_socket=source)])})
        item = types.SimpleNamespace(item_type='SOCKET', in_out='INPUT', name='Material',
                                     socket_type='NodeSocketMaterial', identifier='material',
                                     default_value=self.mat)
        tree = types.SimpleNamespace(get={'qc_view_graph': 2}.get, name='QC Fog View v1',
                                     nodes=[group], interface=types.SimpleNamespace(items_tree=[item]))

        class Modifier(dict):
            type = 'NODES'
            node_group = tree
            name = 'QC Volume Fog'

        self.modifiers = [Modifier(material=self.mat)]

    @property
    def material_slots(self):
        return [types.SimpleNamespace(material=mat) for mat in self.data.materials]


class FogMaterialRepair(unittest.TestCase):
    def ensure(self, obj):
        with patch.dict(sys.modules, {'qcblender.blender.graph': graph}):
            return fog._ensure_fog_material_slot(obj)

    def test_missing_slot_is_added_once_without_overwriting_existing_slots(self):
        obj = FogObject()
        unrelated = object()
        obj.data.materials.extend([unrelated, None])
        before = dict(obj)
        self.assertTrue(self.ensure(obj))
        self.assertEqual(obj.data.materials, [unrelated, None, obj.mat])
        self.assertFalse(self.ensure(obj))
        self.assertEqual(len(obj.data.materials), 3)
        self.assertEqual(dict(obj), before)
        self.assertIs(obj.modifiers[0]['material'], obj.mat)

    def test_existing_matching_slot_and_socket_default_are_supported(self):
        obj = FogObject()
        obj.data.materials.append(obj.mat)
        self.assertFalse(self.ensure(obj))
        del obj.modifiers[0]['material']
        self.assertFalse(self.ensure(obj))
        obj.data.materials.clear()
        self.assertTrue(self.ensure(obj))
        self.assertIs(obj.data.materials[0], obj.mat)

    def test_linked_and_readonly_object_or_mesh_is_unchanged(self):
        for owner_name, attribute, value in (
                ('object', 'library', object()), ('object', 'is_editable', False),
                ('mesh', 'library', object()), ('mesh', 'is_editable', False)):
            with self.subTest(owner=owner_name, attribute=attribute):
                obj = FogObject()
                owner = obj if owner_name == 'object' else obj.data
                setattr(owner, attribute, value)
                self.assertFalse(self.ensure(obj))
                self.assertEqual(obj.data.materials, [])

    def test_other_views_and_ambiguous_or_unrecognized_graph_are_unchanged(self):
        for case in ('kind', 'type', 'ambiguous', 'asset', 'socket', 'material', 'disconnected', 'rerouted'):
            with self.subTest(case=case):
                obj = FogObject()
                if case == 'kind':
                    obj['qc_view_kind'] = 'field'
                elif case == 'type':
                    obj.type = 'VOLUME'
                elif case == 'ambiguous':
                    obj.modifiers.append(obj.modifiers[0])
                elif case == 'asset':
                    obj.modifiers[0].node_group.nodes[0].node_tree['qc_asset_id'] = 'custom'
                elif case == 'socket':
                    obj.modifiers[0].node_group.interface.items_tree = []
                elif case == 'material':
                    obj.modifiers[0]['material'] = None
                elif case == 'disconnected':
                    obj.modifiers[0].node_group.nodes[0].inputs['Material'].links = []
                else:
                    obj.modifiers[0].node_group.nodes[0].inputs['Material'].links[0].from_socket.identifier = 'other'
                self.assertFalse(self.ensure(obj))
                self.assertEqual(obj.data.materials, [])

    def test_registration_uses_only_load_hook_and_one_initial_timer(self):
        try:
            fog.register()
            fog.register()
            self.assertEqual(fog.bpy.app.handlers.load_post, [fog._restore_fog_material_slots])
            self.assertEqual(fog.bpy.app.handlers.save_post, [])
            self.assertEqual(timers, {fog._restore_fog_material_slots: {'first_interval': 0}})
            obj = FogObject()
            fog.bpy.data.objects = [obj]
            with patch.dict(sys.modules, {'qcblender.blender.graph': graph}):
                self.assertIsNone(fog._restore_fog_material_slots())
                self.assertIsNone(fog._restore_fog_material_slots())
            self.assertEqual(obj.data.materials, [obj.mat])
        finally:
            fog.unregister()
            fog.unregister()
            fog.bpy.data.objects = []
        self.assertEqual(fog.bpy.app.handlers.load_post, [])
        self.assertEqual(timers, {})


if __name__ == '__main__':
    unittest.main()
