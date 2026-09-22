"""Check the product sampling nodes with an analytic field and invalid-domain mask."""
from copy import deepcopy
import importlib
import json
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
views = importlib.import_module(MODULE + '.blender.views')
data_module = importlib.import_module(MODULE + '.data')
worker = importlib.import_module(MODULE + '.worker')
scalars = importlib.import_module(MODULE + '.blender.scalars')
existing = next(o for o in bpy.data.objects if 'qc_field' in o
                and json.loads(o['qc_field'])['quantity'] == 'orbital_amplitude')
data = data_module.load_dataset(bpy.path.abspath(existing['qc_dataset']))
field = data.metadata['fields'][0]
target = views.field_view(bpy.path.abspath(existing['qc_dataset']))
out = ROOT / 'outputs/scalar-probe'
out.mkdir(exist_ok=True)
analytic = deepcopy(data)
steps = np.array([[.2, 0, 0], [.04, .25, 0], [0, 0, .3]])
origin = np.array([-5, -5, -5])
shape = (51, 41, 35)
indices = np.indices(shape).reshape(3, -1).T
points = origin + indices @ steps
values = (2 * points[:, 0] - 3 * points[:, 1] + .5 * points[:, 2] + 1).reshape(shape)
analytic.arrays['analytic'] = values
analytic.arrays['analytic_valid'] = np.ones(shape, dtype=bool)
analytic.metadata['fields'] = [{'quantity': 'unknown_scalar', 'unit': 'analytic-test',
                               'array': 'analytic', 'valid_mask': 'analytic_valid',
                               'origin': origin.tolist(), 'steps': steps.tolist(), 'shape': list(shape),
                               'coordinate_unit': 'angstrom', 'vdb': 'field.vdb'}]
data_module.save_dataset(analytic, out)
worker.write_volume(analytic, out / 'field.vdb')
source = views.field_view(out)
source.hide_render = True
source.hide_set(True)
scalars.add_mapping(target, source, -5, 5)
bpy.context.view_layer.update()
evaluated = target.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
try:
    coords = np.array([v.co[:] for v in mesh.vertices])
    actual = np.array([v.value for v in mesh.attributes['qc_scalar_value'].data])
    valid = np.array([v.value for v in mesh.attributes['qc_sample_valid'].data])
    expected = 2*coords[:, 0] - 3*coords[:, 1] + .5*coords[:, 2] + 1
    error = float(np.max(np.abs(actual - expected)))
    assert valid.all()
    assert error < 1e-5, error
finally:
    evaluated.to_mesh_clear()
source.qc_settings.volume.location = (.4, -.5, .6)
source.qc_settings.volume.rotation_euler = (0, 0, .2)
source.qc_settings.volume.scale = (1.2, .8, 1.1)
target.location = (.2, .3, .4)
target.update_tag()
bpy.context.view_layer.update()
evaluated = target.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
try:
    coords = np.array([(*v.co, 1) for v in mesh.vertices])
    transform = np.array(source.qc_settings.volume.matrix_world.inverted() @ target.matrix_world)
    mapped = (coords @ transform.T)[:, :3]
    expected = 2*mapped[:, 0] - 3*mapped[:, 1] + .5*mapped[:, 2] + 1
    actual = np.array([v.value for v in mesh.attributes['qc_scalar_value'].data])
    transformed_error = float(np.max(np.abs(actual-expected)))
    assert transformed_error < 1e-5, transformed_error
finally:
    evaluated.to_mesh_clear()
bpy.context.view_layer.objects.active = source
assert bpy.ops.qcblender.create_slice(resolution=17, minimum=-5, maximum=5) == {'FINISHED'}
slice_obj = bpy.context.object
mod = slice_obj.modifiers[0]
center = next(s.identifier for s in mod.node_group.interface.items_tree
              if s.item_type == 'SOCKET' and s.name == 'Center' and s.in_out == 'INPUT')
mod[center] = (100, 100, 100)
slice_obj.update_tag()
bpy.context.view_layer.update()
evaluated = slice_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
try:
    assert len(mesh.vertices) == 17*17
    assert not any(v.value for v in mesh.attributes['qc_sample_valid'].data)
finally:
    evaluated.to_mesh_clear()
result = {'status': 'Passed', 'sheared_grid_sampling_max_error': error,
          'object_transforms_sampling_max_error': transformed_error,
          'outside_slice_mask': 'Passed', 'slice_vertices': 17*17}
(out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
