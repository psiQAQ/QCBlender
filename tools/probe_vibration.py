"""Run in the development Blender after importing the water frequency job."""
import json
import math
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
objects = [o for o in bpy.data.objects if o.get('qc_view_kind') == 'atoms' and len(o.qc_settings.modes) == 3]
obj = sorted(objects, key=lambda o: o.name)[-1]
tree = obj.modifiers[0].node_group
modifier = obj.modifiers[0]
inputs = {s.name: s.identifier for s in tree.interface.items_tree
          if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
assert abs(modifier[inputs['Amplitude (angstrom)']] - .2) < 1e-6
assert abs(modifier[inputs['Cycles per second']] - 1) < 1e-6
obj.qc_settings.active_mode = 0
first = np.array([d.vector[:] for d in obj.data.attributes['qc_mode_displacement'].data])
obj.qc_settings.active_mode = 1
displacements = np.array([d.vector[:] for d in obj.data.attributes['qc_mode_displacement'].data])
assert not np.array_equal(first, displacements)
colors = np.array([d.color[:] for d in obj.qc_settings.spectrum.data.color_attributes['qc_ir_color'].data])
np.testing.assert_allclose(colors[2:4, :3], [[1, .3, .04], [1, .3, .04]], atol=1e-6)
output = next(n for n in tree.nodes if n.type == 'GROUP_OUTPUT')
position = next(n for n in tree.nodes if n.bl_idname == 'GeometryNodeSetPosition')
original = output.inputs['Geometry'].links[0].from_socket
tree.links.new(position.outputs['Geometry'], output.inputs['Geometry'])
try:
    equilibrium = np.array([d.vector[:] for d in obj.data.attributes['qc_equilibrium_position'].data])
    for phase in (0, math.pi / 2, -math.pi / 2):
        modifier[inputs['Phase']] = phase
        obj.update_tag()
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            actual = np.array([v.co[:] for v in mesh.vertices])
            np.testing.assert_allclose(actual, equilibrium + .2 * displacements * math.sin(phase), atol=1e-6)
        finally:
            evaluated.to_mesh_clear()
finally:
    tree.links.new(original, output.inputs['Geometry'])
    modifier[inputs['Phase']] = 0
    obj.update_tag()

# Isolate the actual arrow branch to check its vector magnitude and zero suppression.
vectors = next(n for n in tree.nodes if n.bl_idname == 'GeometryNodeSwitch'
               and n.input_type == 'GEOMETRY' and n.inputs['Switch'].is_linked
               and n.inputs['Switch'].links[0].from_socket.name == 'Show Displacement Vectors')
tree.links.new(vectors.outputs['Output'], output.inputs['Geometry'])
modifier[inputs['Show Displacement Vectors']] = True
modifier[inputs['First Atom (1-based)']] = 1
modifier[inputs['Last Atom (0 = all)']] = 1
try:
    for amplitude in (.2, .5, 0):
        modifier[inputs['Amplitude (angstrom)']] = amplitude
        obj.update_tag()
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            if amplitude == 0:
                assert len(mesh.vertices) == 0
            else:
                coords = np.array([v.co[:] for v in mesh.vertices]) - equilibrium[0]
                direction = displacements[0] / np.linalg.norm(displacements[0])
                projection = coords @ direction
                np.testing.assert_allclose([projection.min(), projection.max()],
                    [0, amplitude * np.linalg.norm(displacements[0])], atol=1e-6)
        finally:
            evaluated.to_mesh_clear()
finally:
    tree.links.new(original, output.inputs['Geometry'])
    modifier[inputs['First Atom (1-based)']], modifier[inputs['Last Atom (0 = all)']] = 1, 0
    modifier[inputs['Amplitude (angstrom)']] = .2
    modifier[inputs['Show Displacement Vectors']] = False
    obj.update_tag()
result = {'status': 'Passed', 'modes': len(obj.qc_settings.modes),
          'selected_source_number': obj['qc_mode_source_number'],
          'frequency_cm-1': obj['qc_mode_frequency_cm-1'], 'ir_linked_highlight': 'Passed',
          'displacement_equation': 'Passed', 'equilibrium_geometry_unchanged': 'Passed',
          'vector_direction_length_zero': 'Passed'}
(ROOT / 'outputs/vibration-probe.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
