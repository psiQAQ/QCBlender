"""Real Blender checks of composable assets using isolated synthetic scientific data."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import qcblender
from qcblender.blender import views, assets
from qcblender.blender.graph import view_modifier, append_branch
from qcblender.data import Dataset, save_dataset

qcblender.register()
OUT = ROOT / 'outputs/composable'
OUT.mkdir(parents=True, exist_ok=True)


def mesh_points(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return np.array([v.co[:] for v in mesh.vertices])
    finally:
        evaluated.to_mesh_clear()


def set_input(obj, name, value):
    modifier = view_modifier(obj)
    item = next(s for s in modifier.node_group.interface.items_tree if s.name == name and s.in_out == 'INPUT')
    modifier[item.identifier] = value
    obj.update_tag()


data = Dataset(metadata={'source': {'filename': 'analytic', 'sha256': hashlib.sha256(b'analytic').hexdigest()},
                         'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': []},
               arrays={'positions': np.array([[0., 0, 0], [1.4, 0, 0]]),
                       'atomic_numbers': np.array([6, 1], dtype=np.int32),
                       'bonds': np.array([[0, 1]], dtype=np.int32)})
save_dataset(data, OUT / 'atoms')
obj = views.atom_view(OUT / 'atoms')
initial = mesh_points(obj)
assert len(initial) == 100  # Two subdivision-2 icospheres (42 each), one 8-sided tube.
modifier = view_modifier(obj)
extra = obj.modifiers.new('Unrelated', 'BEVEL')
obj.modifiers.move(1, 0)
assert view_modifier(obj) == modifier
obj.modifiers.remove(extra)
set_input(obj, 'Style (0 ball-stick, 1 space-fill, 2 bonds)', 1)
filled = mesh_points(obj)
assert filled[:, 0].min() < -1.5
set_input(obj, 'Style (0 ball-stick, 1 space-fill, 2 bonds)', 2)
assert 0 < len(mesh_points(obj)) < len(initial)
set_input(obj, 'Style (0 ball-stick, 1 space-fill, 2 bonds)', 0)
np.testing.assert_array_equal(mesh_points(obj), initial)
tree = modifier.node_group
cube = tree.nodes.new('GeometryNodeMeshCube')
append_branch(tree, cube.outputs['Mesh'])
assert len(mesh_points(obj)) == len(initial) + 8
for group in (assets.sample_group(), assets.selection_group(), assets.atom_style_group(),
              assets.surface_style_group(), assets.slice_group(), views.isosurface_group()):
    assert group.asset_data and group.get('qc_asset_id')
    assert not any(n.bl_idname == 'GeometryNodeObjectInfo' for n in group.nodes)
from qcblender.blender.scalars import scalar_material
assert assets.color_group().asset_data
assert scalar_material().use_nodes
from qcblender.worker import write_volume
from qcblender.blender.scalars import add_mapping
axis = np.linspace(-2, 2, 21)
x, y, z = np.meshgrid(axis, axis, axis, indexing='ij')
values = x * np.exp(-x*x-y*y-z*z)
field = {'array': 'field', 'valid_mask': 'valid', 'shape': [21, 21, 21],
         'origin': [-2, -2, -2], 'steps': (np.eye(3)*.2).tolist(),
         'quantity': 'orbital_amplitude', 'unit': 'bohr^-3/2', 'vdb': 'field.vdb'}
data.metadata['fields'] = [field]
data.arrays.update(field=values, valid=np.ones(values.shape, dtype=bool))
save_dataset(data, OUT / 'field')
write_volume(data, OUT / 'field/field.vdb')
surface = views.field_view(OUT / 'field')
solid = mesh_points(surface)
assert solid[:, 0].min() < -.1 and solid[:, 0].max() > .1
for style in (1, 2):
    set_input(surface, 'Style (0 solid, 1 wire, 2 points)', style)
    assert len(mesh_points(surface)) > len(solid)
set_input(surface, 'Style (0 solid, 1 wire, 2 points)', 0)
set_input(surface, 'Negative Phase', False)
assert mesh_points(surface)[:, 0].min() > 0
set_input(surface, 'Negative Phase', True)
set_input(surface, 'Link Thresholds', False)
set_input(surface, 'Negative Isovalue', .2)
assert len(mesh_points(surface)) < len(solid)
add_mapping(surface, surface, -.3, .3)
assert len(mesh_points(surface)) > 0
set_input(surface, 'Negative Opacity', .25)
surface.update_tag()
bpy.context.view_layer.update()
evaluated = surface.evaluated_get(bpy.context.evaluated_depsgraph_get())
geometry = evaluated.to_mesh()
try:
    coords = np.array([v.co[:] for v in geometry.vertices])
    opacity = np.array([v.value for v in geometry.attributes['qc_opacity'].data])
    np.testing.assert_allclose(opacity[coords[:, 0] < 0], .25)
    np.testing.assert_allclose(opacity[coords[:, 0] > 0], 1.)
finally:
    evaluated.to_mesh_clear()
from qcblender.blender.inspection import add_clip, sample_point
add_clip(surface)
set_input(surface, 'Plane Enabled', True)
assert mesh_points(surface)[:, 0].min() >= 0
set_input(surface, 'Plane Enabled', False)
set_input(surface, 'Box Enabled', True)
set_input(surface, 'Box Minimum', (-.5, -.5, -.5))
set_input(surface, 'Box Maximum', (.5, .5, .5))
clipped = mesh_points(surface)
assert len(clipped) > 0 and np.abs(clipped).max() < .501
assert abs(sample_point(2*x-3*y+.5*z+1, np.ones(values.shape, bool), field, [.1, -.2, .3]) - 1.95) < 1e-12
shear = np.array([[.2, .03, 0], [0, .2, .02], [.01, 0, .2]])
indices = np.moveaxis(np.indices(values.shape), 0, -1)
positions = indices @ shear + [-2, -2, -2]
analytic = positions @ [2., -3., .5] + 1
sheared_field = dict(field, steps=shear.tolist())
point = np.array([7.2, 9.1, 12.4]) @ shear + [-2, -2, -2]
assert abs(sample_point(analytic, np.ones(values.shape, bool), sheared_field, point) - (point @ [2, -3, .5] + 1)) < 1e-12
invalid = np.ones(values.shape, bool)
invalid[7, 9, 12] = False
try:
    sample_point(analytic, invalid, sheared_field, point)
except ValueError:
    pass
else:
    raise AssertionError('Invalid contributing voxel accepted')
for point in ([8, 0, 0], [float('nan'), 0, 0]):
    try:
        sample_point(values, np.ones(values.shape, bool), field, point)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid sample accepted')
from qcblender.blender.fog import fog_view
fog = fog_view(surface)
mat = next(s.default_value for s in view_modifier(fog).node_group.interface.items_tree
           if s.item_type == 'SOCKET' and s.socket_type == 'NodeSocketMaterial')
assert any(n.get('qc_role') == 'opacity_ramp' for n in mat.node_tree.nodes)
from mathutils import Vector
volume = surface.qc_settings.volume
volume.location = (1, -2, .5)
volume.rotation_euler = (.2, .3, -.1)
volume.scale = (1.2, .8, 1.5)
bpy.context.view_layer.update()
bpy.context.scene.cursor.location = volume.matrix_world @ Vector((.1, -.2, .3))
bpy.context.view_layer.objects.active = surface
assert bpy.ops.qcblender.probe_field() == {'FINISHED'}
np.testing.assert_allclose(json.loads(surface['qc_probe'])['source_position_angstrom'], [.1, -.2, .3], atol=1e-6)
old_tree = view_modifier(surface).node_group
old_links = [(l.from_socket, l.to_socket) for l in old_tree.links]
assert bpy.ops.qcblender.new_current_view() == {'FINISHED'}
new = bpy.context.object
assert new != surface and view_modifier(new).node_group != old_tree
assert old_links == [(l.from_socket, l.to_socket) for l in old_tree.links]
report = {'status': 'Passed', 'blender': bpy.app.version_string, 'atom_styles': 'Passed',
          'modifier_reorder': 'Passed', 'preserved_branch': 'Passed', 'unbound_assets': 'Passed',
          'signed_surface_styles': 'Passed', 'independent_thresholds': 'Passed', 'mapping': 'Passed',
          'plane_box_clip': 'Passed', 'point_sampling': 'Passed', 'volume_transfer_graph': 'Passed',
          'affine_sampling_invalid_regions': 'Passed', 'cursor_world_transform': 'Passed', 'keep_original_upgrade': 'Passed',
          'phase_opacity_after_mapping': 'Passed'}
(OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
