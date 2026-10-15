"""Pure boundary tests; native Blender geometry and Undo are validated separately."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np


def load_annotations():
    bpy = types.ModuleType('bpy')
    bpy.types = types.SimpleNamespace(Operator=type('Operator', (), {}))
    props = types.ModuleType('bpy.props')
    for name in ('BoolProperty', 'EnumProperty', 'FloatProperty', 'FloatVectorProperty', 'IntProperty', 'StringProperty'):
        setattr(props, name, lambda **values: None)
    geom = types.ModuleType('qcblender.blender.geometry')
    geom.current_geometry = lambda owner: (owner.positions, owner.record)
    views = types.ModuleType('qcblender.blender.views')
    views.material = lambda *args, **kwargs: None
    modules = {'bpy': bpy, 'bpy.props': props, 'mathutils': types.SimpleNamespace(Vector=np.asarray),
               'qcblender.blender.geometry': geom, 'qcblender.blender.views': views}
    path = Path(__file__).resolve().parents[1] / 'qcblender/blender/annotations.py'
    spec = importlib.util.spec_from_file_location('qcblender.blender._annotations_boundary', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


annotations = load_annotations()
RECORD = {'source_sha256': 'source', 'selected_job': 0, 'dataset_sha256': 'dataset',
          'coordinate_unit': 'angstrom', 'kind': 'source', 'step': None}
POSITIONS = np.array([[0., 1., 0.], [0., 0., 0.], [1., 0., 0.], [1., 0., 1.]])


def entry(identifier='id', kind='DISTANCE', version=1):
    return {'role': 'LABEL', 'id': identifier, 'kind': kind, 'version': version,
            'source_atom_numbers': [1, 2] if kind == 'DISTANCE' else [1, 2, 3] if kind == 'ANGLE' else [1, 2, 3, 4],
            'symbols': ['H', 'H', 'H', 'H'], 'source_sha256': 'source', 'selected_job': 0,
            'dataset_sha256': 'dataset', 'size': .16, 'color': [0., 0., 0.],
            'offset': [.2, .2, .2], 'decimals': 4, 'line_width': .01,
            'show_leader': True, 'visible': True}


class Points(list):
    def add(self, count):
        self.extend(types.SimpleNamespace(co=None) for _ in range(count))


class Splines(list):
    def new(self, kind):
        item = types.SimpleNamespace(type=kind, points=Points([types.SimpleNamespace(co=None)]))
        self.append(item)
        return item


class Material:
    copies = []

    def __init__(self, name):
        self.name = name
        self.use_fake_user = False
        self.slot_users = 0
        self.opaque_nodes = {'arbitrary': ['shader', 'color', .123]}

    @property
    def users(self):
        return self.slot_users + int(self.use_fake_user)

    @property
    def node_tree(self):
        raise AssertionError('Existing material nodes must not be consulted')

    def copy(self):
        result = Material(self.name + '.copy')
        result.opaque_nodes = copy.deepcopy(self.opaque_nodes)
        Material.copies.append(result)
        return result


class Slots(list):
    def append(self, mat):
        super().append(mat)
        if mat is not None:
            mat.slot_users += 1

    def clear(self):
        for mat in self:
            if mat is not None:
                mat.slot_users -= 1
        super().clear()


class Data:
    def __init__(self, role, mat=None, inaccessible_materials=False):
        self.users = 1
        self.body, self.size = '', 0.
        self.splines = Splines()
        if role == 'LEADER':
            self.splines.new('POLY').points.add(1)
        self._materials = Slots()
        if mat is not None:
            self._materials.append(mat)
        self.inaccessible_materials = inaccessible_materials
        self.vertices, self.faces = [], []
        self.font = types.SimpleNamespace(name='Bfont')

    @property
    def materials(self):
        if self.inaccessible_materials:
            raise AssertionError('Update must not consult material slots or users')
        return self._materials

    def clear_geometry(self):
        self.vertices, self.faces = [], []

    def from_pydata(self, vertices, edges, faces):
        self.vertices, self.faces = vertices, faces

    def update(self):
        pass

    def copy(self):
        result = Data('LABEL')
        result.splines = copy.deepcopy(self.splines)
        result.font = self.font
        for mat in self.materials:
            result.materials.append(mat)
        return result


class Object(dict):
    def __init__(self, role, record, mat=None, inaccessible_materials=False):
        super().__init__(qc_annotation=json.dumps({**record, 'role': role}))
        self.name = role + record['id']
        self.type = 'FONT' if role == 'LABEL' else 'MESH' if role.startswith('PLANE_') else 'CURVE'
        self.data = Data(role, mat, inaccessible_materials)
        self.location = np.zeros(3)
        self.hide_viewport = self.hide_render = False
        self.parent = None

    def __setattr__(self, key, value):
        if key == 'parent':
            previous = getattr(self, 'parent', None)
            if previous is not None and self in previous.children:
                previous.children.remove(self)
            if value is not None and self not in value.children:
                value.children.append(self)
        super().__setattr__(key, value)

    def copy(self):
        result = Object(json.loads(self['qc_annotation'])['role'], json.loads(self['qc_annotation']))
        result.data = self.data
        result.location = self.location.copy()
        return result


def owner(parts):
    result = types.SimpleNamespace(children=list(parts), positions=POSITIONS.copy(), record=RECORD.copy())
    for part in parts:
        part.parent = result
    return result


class AnnotationUpdates(unittest.TestCase):
    def test_regular_edit_does_not_read_material_slots_or_nodes(self):
        saved = entry(version=2)
        parts = [Object(role, saved, inaccessible_materials=True) for role in ('LABEL', 'LEADER', 'DASH')]
        target = owner(parts)
        target.users_collection = [object()]
        styles = {**annotations.STYLE_DEFAULTS, **saved, 'size': .3, 'decimals': 2}
        operator = types.SimpleNamespace(**{key: styles[key] for key in
            ('size', 'offset', 'decimals', 'show_leader', 'line_width', 'visible', *annotations.STYLE_DEFAULTS)},
            annotation_id='id', report=lambda *args: None)
        with patch.object(annotations, '_atom_view', return_value=target):
            result = annotations.QCBLENDER_OT_edit_annotation.execute(operator, types.SimpleNamespace())
        self.assertEqual(result, {'FINISHED'})
        self.assertEqual(parts[0].data.size, .3)
        self.assertEqual(parts[0].data.body, 'Distance(1,2) = 1.00 Å')

    def test_update_legacy_pair_never_reads_materials_and_does_not_migrate(self):
        saved = entry()
        saved['color'] = 'unrelated legacy material display state'
        parts = [Object(role, saved, inaccessible_materials=True) for role in ('LABEL', 'LEADER')]
        target = owner(parts)
        annotations.update_annotations(target, POSITIONS, RECORD)
        self.assertEqual(parts[0].data.body, 'Distance(1,2) = 1.0000 Å')
        self.assertEqual(len(target.children), 2)
        np.testing.assert_allclose(parts[1].data.splines[0].points[0].co, [0., .5, 0., 1.])

    def test_v2_geometry_updates_and_undefined_step_clears_stale_parts(self):
        saved = entry(kind='DIHEDRAL', version=2)
        parts = [Object(role, saved, inaccessible_materials=True)
                 for role in ('LABEL', 'LEADER', 'ARC', 'PLANE_A', 'PLANE_B')]
        target = owner(parts)
        annotations.update_annotations(target, POSITIONS, RECORD)
        self.assertTrue(len(parts[2].data.splines))
        self.assertEqual(parts[2].data.bevel_depth, .005)
        self.assertEqual(parts[3].data.faces, [(0, 1, 2)])
        np.testing.assert_array_equal(parts[3].data.vertices, POSITIONS[[0, 1, 2]])
        positions = POSITIONS.copy()
        positions[0] = [-1., 0., 0.]
        annotations.update_annotations(target, positions, RECORD)
        self.assertIn('undefined', parts[0].data.body)
        for part in parts[2:]:
            self.assertTrue(part.hide_render)
        self.assertEqual(len(parts[2].data.splines), 0)
        self.assertEqual(parts[3].data.faces, [])

    def test_independent_native_data_is_still_required(self):
        parts = [Object(role, entry(), inaccessible_materials=True) for role in ('LABEL', 'LEADER')]
        parts[0].data.users = 2
        with self.assertRaisesRegex(ValueError, 'independent FONT data'):
            annotations.prepare_annotations(owner(parts), POSITIONS, RECORD)

    def test_v2_parts_and_scientific_identity_are_validated_before_mutation(self):
        saved = entry(version=2)
        parts = [Object(role, saved, inaccessible_materials=True) for role in ('LABEL', 'LEADER')]
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            annotations.prepare_annotations(owner(parts), POSITIONS, RECORD)
        self.assertEqual(parts[0].data.body, '')

    def test_visible_and_plane_switches_are_independent(self):
        saved = {**entry(kind='DIHEDRAL', version=2), 'show_measurement': False, 'show_planes': True}
        parts = [Object(role, saved, inaccessible_materials=True)
                 for role in ('LABEL', 'LEADER', 'ARC', 'PLANE_A', 'PLANE_B')]
        target = owner(parts)
        annotations.update_annotations(target, POSITIONS, RECORD)
        self.assertTrue(parts[2].hide_render)
        self.assertFalse(parts[3].hide_render)
        for part in parts:
            current = json.loads(part['qc_annotation'])
            current['visible'] = False
            part['qc_annotation'] = json.dumps(current)
        annotations.update_annotations(target, POSITIONS, RECORD)
        self.assertTrue(all(part.hide_render for part in parts))

    def test_hidden_parent_layer_keeps_new_parts_hidden(self):
        saved = entry(version=2)
        parts = [Object(role, saved, inaccessible_materials=True) for role in ('LABEL', 'LEADER', 'DASH')]
        target = owner(parts)
        target.hide_render = True
        annotations.update_annotations(target, POSITIONS, RECORD)
        self.assertTrue(all(part.hide_render for part in parts))
        self.assertTrue(all(part['qc_layer_restore_render'] is False for part in parts))


class MaterialUnification(unittest.TestCase):
    def setUp(self):
        Material.copies.clear()

    def test_arbitrary_nodes_preserved_and_groups_shared_independently_idempotently(self):
        old_label, old_line = Material('custom-label'), Material('custom-leader')
        groups = [Object(role, entry(identifier), old_label if role == 'LABEL' else old_line)
                  for identifier in ('a', 'b') for role in ('LABEL', 'LEADER')]
        target = owner(groups)
        self.assertEqual(annotations.unify_annotation_materials(target), 2)
        first, second = groups[0].data.materials[0], groups[2].data.materials[0]
        self.assertIs(groups[1].data.materials[0], first)
        self.assertIs(groups[3].data.materials[0], second)
        self.assertIsNot(first, second)
        self.assertEqual(first.opaque_nodes, old_label.opaque_nodes)
        self.assertTrue(old_label.use_fake_user and old_line.use_fake_user)
        self.assertEqual(annotations.unify_annotation_materials(target), 0)
        self.assertEqual(len(Material.copies), 2)

    def test_dihedral_planes_keep_their_own_reference_material(self):
        text, plane_a, plane_b = Material('text'), Material('plane_a'), Material('plane_b')
        plane_a.opaque_nodes = {'alpha': .07, 'custom': True}
        saved = entry(kind='DIHEDRAL', version=2)
        parts = [Object(role, saved, plane_a if role == 'PLANE_A' else plane_b if role == 'PLANE_B' else text)
                 for role in ('LABEL', 'LEADER', 'ARC', 'PLANE_A', 'PLANE_B')]
        self.assertEqual(annotations.unify_annotation_materials(owner(parts)), 1)
        self.assertIs(parts[0].data.materials[0], text)
        self.assertIs(parts[3].data.materials[0], parts[4].data.materials[0])
        self.assertEqual(parts[3].data.materials[0].opaque_nodes, plane_a.opaque_nodes)
        self.assertIsNot(parts[3].data.materials[0], text)

    def test_runtime_failure_restores_slots_and_fake_user_state(self):
        first, second = Material('first'), Material('second')
        parts = [Object('LABEL', entry(), first), Object('LEADER', entry(), second)]
        original = annotations._assign_material
        calls = []
        def fail(obj, mat):
            calls.append(obj)
            if len(calls) == 2:
                raise RuntimeError('write failed')
            original(obj, mat)
        removed = []
        data = types.SimpleNamespace(materials=types.SimpleNamespace(remove=removed.append))
        with patch.object(annotations, '_assign_material', side_effect=fail), patch.object(annotations.bpy, 'data', data, create=True):
            with self.assertRaisesRegex(RuntimeError, 'write failed'):
                annotations.unify_annotation_materials(owner(parts))
        self.assertIs(parts[0].data.materials[0], first)
        self.assertIs(parts[1].data.materials[0], second)
        self.assertFalse(first.use_fake_user or second.use_fake_user)
        self.assertEqual(len(removed), 1)


class AnnotationLifecycle(unittest.TestCase):
    def runtime(self):
        removed_data, removed_materials = [], []
        def remove_object(obj, **kwargs):
            obj.parent = None
            obj.data.users -= 1
        def remove_data(data):
            data.materials.clear()
            removed_data.append(data)
        def new_data(name, *args):
            role = name.removeprefix('QC annotation ').upper()
            return Data(role)
        def new_object(name, data):
            role = name.removeprefix('QC annotation ').upper()
            obj = Object(role, entry())
            obj.data, obj.name = data, name
            return obj
        db = types.SimpleNamespace(
            objects=types.SimpleNamespace(remove=remove_object, new=new_object),
            curves=types.SimpleNamespace(remove=remove_data, new=new_data),
            meshes=types.SimpleNamespace(remove=remove_data, new=new_data),
            materials=types.SimpleNamespace(remove=removed_materials.append))
        collection = types.SimpleNamespace(objects=types.SimpleNamespace(link=lambda obj: None))
        return db, collection, removed_data, removed_materials

    def test_copy_preserves_owner_scoped_ids_and_material_group_sharing(self):
        core, plane = Material('core'), Material('planes')
        saved = entry(kind='DIHEDRAL', version=2)
        originals = [Object(role, saved, plane if role.startswith('PLANE_') else core)
                     for role in ('LABEL', 'LEADER', 'ARC', 'PLANE_A', 'PLANE_B')]
        source, target = owner(originals), owner([])
        target.record['dataset_sha256'] = 'target'
        db, collection, _, removed_materials = self.runtime()
        with patch.object(annotations.bpy, 'data', db, create=True):
            annotations.copy_annotations(source, target, collection)
            self.assertEqual(len(target.children), 5)
            copied = {json.loads(obj['qc_annotation'])['role']: obj for obj in target.children}
            self.assertTrue(all(json.loads(obj['qc_annotation'])['id'] == 'id' for obj in target.children))
            self.assertTrue(all(obj.data is not original.data for obj, original in zip(target.children, originals)))
            clone = copied['LABEL'].data.materials[0]
            self.assertIsNot(clone, core)
            self.assertIs(copied['LEADER'].data.materials[0], clone)
            self.assertIs(copied['ARC'].data.materials[0], clone)
            self.assertIs(copied['PLANE_A'].data.materials[0], copied['PLANE_B'].data.materials[0])
            self.assertIsNot(copied['PLANE_A'].data.materials[0], plane)
            annotations.remove_annotations(target)
        self.assertEqual(len(target.children), 0)
        self.assertEqual(len(source.children), 5)
        self.assertEqual(removed_materials, [])

    def test_legacy_first_edit_adds_dash_using_the_existing_label_material(self):
        text, leader = Material('custom text'), Material('custom leader')
        parts = [Object('LABEL', entry(), text), Object('LEADER', entry(), leader)]
        target = owner(parts)
        prepared = annotations.prepare_annotations(target, POSITIONS, RECORD)[0]
        db, collection, _, _ = self.runtime()
        with patch.object(annotations.bpy, 'data', db, create=True):
            annotations._upgrade_parts(prepared[0], prepared[1], prepared[4], collection)
        self.assertEqual(len(target.children), 3)
        dash = target.children[-1]
        self.assertIs(dash.data.materials[0], text)
        self.assertIs(parts[1].data.materials[0], leader)
        self.assertEqual(prepared[1]['version'], 2)

    def test_legacy_font_only_replaced_when_builtin_and_cjk_is_needed(self):
        obj = Object('LABEL', entry())
        font = object()
        helper = types.SimpleNamespace(annotation_font=lambda: font)
        with patch.dict(sys.modules, {'qcblender.blender.annotation_fonts': helper}):
            annotations._ensure_legacy_font(obj, 'Distance(1,2) = 1.0 Å')
            self.assertEqual(obj.data.font.name, 'Bfont')
            annotations._ensure_legacy_font(obj, '距离 1.0 Å')
            self.assertIs(obj.data.font, font)
            custom = types.SimpleNamespace(name='My Custom Font')
            obj.data.font = custom
            annotations._ensure_legacy_font(obj, '距离 1.0 Å')
            self.assertIs(obj.data.font, custom)
            renamed = types.SimpleNamespace(name='Bfont', filepath='//my-font.ttf')
            obj.data.font = renamed
            annotations._ensure_legacy_font(obj, '距离 1.0 Å')
            self.assertIs(obj.data.font, renamed)


class FaceAll(unittest.TestCase):
    def test_remembered_single_id_is_ignored_but_explicit_single_id_is_used(self):
        class Rotation:
            def __matmul__(self, other):
                return 'camera-facing'
            def inverted(self):
                return self
        matrix = types.SimpleNamespace(to_quaternion=Rotation)
        parts = [Object('LABEL', entry(identifier)) for identifier in ('a', 'b', 'c')]
        target = owner(parts)
        target.matrix_world = matrix
        context = types.SimpleNamespace(scene=types.SimpleNamespace(camera=types.SimpleNamespace(matrix_world=matrix)))
        operator = types.SimpleNamespace(annotation_id='a',
            properties=types.SimpleNamespace(is_property_set=lambda *args, **kwargs: False), report=lambda *args: None)
        with patch.object(annotations, '_atom_view', return_value=target):
            self.assertEqual(annotations.QCBLENDER_OT_face_annotations.execute(operator, context), {'FINISHED'})
            self.assertTrue(all(part.rotation_quaternion == 'camera-facing' for part in parts))
            for part in parts:
                part.rotation_quaternion = 'original'
            operator.properties.is_property_set = lambda *args, **kwargs: True
            annotations.QCBLENDER_OT_face_annotations.execute(operator, context)
        self.assertEqual([part.rotation_quaternion for part in parts], ['camera-facing', 'original', 'original'])


if __name__ == '__main__':
    unittest.main()
