"""Exercise installed UI operators and render a real FCHK density/ESP example."""
import importlib
import json
from pathlib import Path
import time
from copy import deepcopy

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
jobs = importlib.import_module(MODULE + '.blender.jobs')
views = importlib.import_module(MODULE + '.blender.views')
project = importlib.import_module(MODULE + '.blender.project')
storage = importlib.import_module(MODULE + '.data')
OUT = ROOT / 'outputs/visual-acceptance'
OUT.mkdir(parents=True, exist_ok=True)


def finish(job):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return job.directory / 'dataset'
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


def sockets(obj):
    return {s.name: s.identifier for s in obj.modifiers[0].node_group.interface.items_tree
            if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}


def mesh(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    result = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    geometry = result.to_mesh()
    try:
        return np.array([v.co[:] for v in geometry.vertices])
    finally:
        result.to_mesh_clear()


for old in bpy.data.objects:
    old.hide_render = True
directory = finish(jobs.Job('import', source=str(ROOT / 'tests/data/chemtools/ch4_uhf_ccpvdz.fchk')))
atoms = views.atom_view(directory)
modifier, tree = atoms.modifiers[0], atoms.modifiers[0].node_group
inputs = sockets(atoms)
output = next(n for n in tree.nodes if n.type == 'GROUP_OUTPUT')
original = output.inputs['Geometry'].links[0].from_socket
selected = next(n for n in tree.nodes if n.bl_idname == 'GeometryNodeDeleteGeometry')
tree.links.new(selected.outputs['Geometry'], output.inputs['Geometry'])
try:
    assert len(mesh(atoms)) == 5
    modifier[inputs['Element (0 = all)']] = 6
    assert len(mesh(atoms)) == 1
    modifier[inputs['Element (0 = all)']] = 0
    modifier[inputs['First Atom (1-based)']] = 2
    modifier[inputs['Last Atom (0 = all)']] = 3
    assert len(mesh(atoms)) == 2
finally:
    modifier[inputs['First Atom (1-based)']], modifier[inputs['Last Atom (0 = all)']] = 1, 0
    tree.links.new(original, output.inputs['Geometry'])

surfaces = []
for quantity in ('electron_number_density', 'electrostatic_potential'):
    field = finish(jobs.Job('evaluate', dataset=str(directory),
        grid={'origin': [-3., -3., -3.], 'steps': [[.15, 0, 0], [0, .15, 0], [0, 0, .15]], 'shape': [41]*3},
        parameters={'quantity': quantity, 'memory_mb': 512}))
    surfaces.append(views.field_view(field, atoms))
density, esp = surfaces
for obj in bpy.context.selected_objects:
    obj.select_set(False)
density.select_set(True)
esp.select_set(True)
bpy.context.view_layer.objects.active = density
assert bpy.ops.qcblender.map_scalar(minimum=-.05, maximum=.05) == {'FINISHED'}
inputs = sockets(density)
before = len(mesh(density))
density.modifiers[0][inputs['Show Legend']] = True
density.modifiers[0][inputs['Legend Position']] = (3., -1.5, 0.)
with_legend = len(mesh(density))
assert with_legend > before + 130
density.modifiers[0][inputs['Color Minimum']] = -.12345
assert len(mesh(density)) != with_legend, 'Legend numeric glyphs must follow the actual range input'
density.modifiers[0][inputs['Color Minimum']] = -.05
esp.hide_render = True
esp.hide_set(True)

# Two imported sources remain independent while their atom coordinate frames can be matched.
second = views.atom_view(directory)
for obj in bpy.context.selected_objects:
    obj.select_set(False)
second.select_set(True)
atoms.select_set(True)
bpy.context.view_layer.objects.active = atoms
assert bpy.ops.qcblender.associate_sources(allow_rigid=False) == {'FINISHED'}
assert json.loads(second['qc_association'])['status'] == 'geometry_matched'
second.hide_render = True

# Rigid source coordinates are transformed for display without changing their arrays.
rotated = deepcopy(storage.load_dataset(directory))
rotation = np.array([[0., -1, 0], [1, 0, 0], [0, 0, 1]])
rotated.arrays['positions'] = rotated.arrays['positions'] @ rotation + [3, 2, 1]
rotated.metadata['source']['sha256'] = '1' * 64
storage.save_dataset(rotated, OUT / 'rotated-test')
moving = views.atom_view(OUT / 'rotated-test')
for item in bpy.context.selected_objects:
    item.select_set(False)
moving.select_set(True)
atoms.select_set(True)
bpy.context.view_layer.objects.active = atoms
assert bpy.ops.qcblender.associate_sources(allow_rigid=True) == {'FINISHED'}
bpy.context.view_layer.update()
world = np.array(moving.matrix_world)
actual = np.column_stack((rotated.arrays['positions'], np.ones(5))) @ world.T
np.testing.assert_allclose(actual[:, :3], storage.load_dataset(directory).arrays['positions'], atol=1e-6)
moving.hide_render = True
assert bpy.ops.qcblender.measure_distance(first=1, second=2) == {'FINISHED'}
for obj in bpy.data.objects:
    if 'qc_measurement' in obj:
        record = json.loads(obj['qc_measurement'])
        coords = np.array([v.co[:] for v in atoms.data.vertices])
        np.testing.assert_allclose(record['value'], np.linalg.norm(coords[0] - coords[1]), atol=1e-6)
        obj.hide_render = True

# Generic Cube values require an explicit interpretation; assigning it never rescales them.
cube = OUT / 'unknown.cube'
cube.write_text('Scalar quantity unspecified\nSynthetic declaration test\n1 0 0 0\n'
                '-2 1 0 0\n-2 0 1 0\n-2 0 0 1\n1 1 0 0 0\n1 2 3 4 5 6 7 8\n', encoding='ascii')
unknown = finish(jobs.Job('import', source=str(cube)))
unknown_data = storage.load_dataset(unknown)
assert unknown_data.metadata['fields'][0]['quantity'] == 'unknown_scalar'
declared = finish(jobs.Job('declare_field', dataset=str(unknown), field_array='cube_0',
                           quantity='electrostatic_potential'))
declared_data = storage.load_dataset(declared)
np.testing.assert_array_equal(unknown_data.arrays['cube_0'], declared_data.arrays['cube_0'])
assert declared_data.metadata['fields'][0]['unit'] == 'hartree/e'
assert declared_data.metadata['fields'][0]['interpretation'] == 'user_assigned'

scene = bpy.context.scene
camera = bpy.data.objects.new('QC ESP camera', bpy.data.cameras.new('QC ESP camera'))
scene.collection.objects.link(camera)
camera.location = (1., 0., 12.)
camera.rotation_euler = (0, 0, 0)
camera.data.type, camera.data.ortho_scale = 'ORTHO', 10
scene.camera = camera
for location, energy, size in [((1, -4, 8), 1000, 5), ((-4, 3, 6), 900, 5)]:
    light = bpy.data.objects.new('QC ESP light', bpy.data.lights.new('QC ESP light', 'AREA'))
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    light.data.energy, light.data.size = energy, size
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.7, .7, .7, 1)
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1000, 700, 100
scene.render.filepath = str(OUT / 'density-esp.png')
project.save_project(OUT / 'density-esp.blend')
bpy.ops.render.render(write_still=True)
report = {'status': 'Passed', 'atom_selection': 'Passed', 'range_linked_legend_geometry': 'Passed',
          'real_density_esp_mapping': 'Passed', 'association_operator': 'Passed',
          'equilibrium_distance': 'Passed', 'render': str(OUT / 'density-esp.png')}
report.update(rigid_coordinate_alignment='Passed', explicit_cube_quantity='Passed')
(OUT / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
