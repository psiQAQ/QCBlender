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
report = {'status': 'Passed', 'blender': bpy.app.version_string, 'atom_styles': 'Passed',
          'modifier_reorder': 'Passed', 'preserved_branch': 'Passed', 'unbound_assets': 'Passed',
          'signed_surface_styles': 'Passed', 'independent_thresholds': 'Passed', 'mapping': 'Passed'}
(OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
