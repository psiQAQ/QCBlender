"""Check saved mode/energy selections and animation or color-map node state after cold open."""
import importlib
import json
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
storage = importlib.import_module(MODULE + '.data')
report = {'status': 'Passed', 'file': bpy.data.filepath}

def inputs(obj):
    return {s.name: s.identifier for s in obj.modifiers[0].node_group.interface.items_tree
            if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}

if Path(bpy.data.filepath).stem == 'water-mode':
    obj = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'atoms')
    assert len(obj.qc_settings.modes) == 3
    assert len(obj.qc_settings.energies) == 10
    assert obj.qc_settings.active_mode == 1
    assert obj.qc_settings.spectrum is not None
    data = storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
    np.testing.assert_allclose([v.vector[:] for v in obj.data.attributes['qc_mode_displacement'].data],
                               data.arrays['mode_display_displacements'][1], atol=1e-7)
    modifier, sockets = obj.modifiers[0], inputs(obj)
    assert modifier[sockets['Animate']] and modifier[sockets['Show Displacement Vectors']]
    assert abs(modifier[sockets['Amplitude (angstrom)']] - .35) < 1e-7
    output = next(n for n in modifier.node_group.nodes if n.type == 'GROUP_OUTPUT')
    position = next(n for n in modifier.node_group.nodes if n.bl_idname == 'GeometryNodeSetPosition')
    original = output.inputs['Geometry'].links[0].from_socket
    modifier.node_group.links.new(position.outputs['Geometry'], output.inputs['Geometry'])
    try:
        bpy.context.scene.frame_set(6)
        obj.update_tag()
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            np.testing.assert_allclose([v.co[:] for v in mesh.vertices],
                data.arrays['positions'] + .35 * data.arrays['mode_display_displacements'][1], atol=1e-6)
        finally:
            evaluated.to_mesh_clear()
    finally:
        modifier.node_group.links.new(original, output.inputs['Geometry'])
    obj.qc_settings.active_mode = 2
    np.testing.assert_allclose([v.vector[:] for v in obj.data.attributes['qc_mode_displacement'].data],
                               data.arrays['mode_display_displacements'][2], atol=1e-7)
    bpy.ops.preferences.addon_disable(module=MODULE)
    bpy.ops.preferences.addon_enable(module=MODULE)
    assert len(obj.qc_settings.modes) == 3 and obj.qc_settings.active_mode == 2
    obj.qc_settings.active_mode = 1
    report.update(mode_selection='Passed', frequency_and_energy_records='Passed',
                  native_animation_equation='Passed', addon_toggle_preserves_selection='Passed')
else:
    obj = next(o for o in bpy.data.objects if o.get('qc_color_source'))
    modifier, sockets = obj.modifiers[0], inputs(obj)
    assert modifier[sockets['Show Legend']]
    np.testing.assert_allclose([modifier[sockets[k]] for k in ('Color Minimum', 'Color Center', 'Color Maximum')],
                              [-.05, 0, .05], atol=1e-7)
    assert obj.qc_settings.volume is not None
    assert json.loads(obj['qc_color_source'])['quantity'] == 'electrostatic_potential'
    source = [n.inputs['Object'].default_value for n in modifier.node_group.nodes
              if n.bl_idname == 'GeometryNodeObjectInfo' and n.inputs['Object'].default_value]
    assert len(source) >= 2
    for volume in source:
        assert volume.data.grids.load()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        assert len(mesh.vertices) > 100
        assert 'qc_scalar_value' in mesh.attributes and 'qc_sample_valid' in mesh.attributes
        with_legend = len(mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
    modifier[sockets['Show Legend']] = False
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        assert with_legend > len(mesh.vertices) + 130, 'Numeric legend text must survive cold open'
    finally:
        evaluated.to_mesh_clear()
    modifier[sockets['Show Legend']] = True
    obj.update_tag()
    bpy.context.scene.render.filepath = str(ROOT / 'outputs/visual-acceptance/cold-density-esp.png')
    bpy.ops.render.render(write_still=True)
    report.update(legend_range='Passed', field_and_color_source_bindings='Passed', sampled_attributes='Passed')
path = ROOT / 'outputs/acceptance' / (Path(bpy.data.filepath).stem + '-cold-view.json')
path.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
