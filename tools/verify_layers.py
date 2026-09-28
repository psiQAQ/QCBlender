"""Installed layer operations, independent styles, and persistent ordering."""
import importlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
OUT = ROOT / 'outputs/layer-acceptance'
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
layers = importlib.import_module(MODULE + '.blender.layers')
project = importlib.import_module(MODULE + '.blender.project')


def action(obj, operation):
    assert bpy.ops.qcblender.layer_action(target=obj.name, action=operation) == {'FINISHED'}


def material(obj):
    modifier = obj.modifiers[0]
    item = next(s for s in modifier.node_group.interface.items_tree if s.name == 'Material')
    return modifier[item.identifier]


if '--vibration-layers' in sys.argv:
    import numpy as np
    import time
    report = json.loads((OUT / 'report.json').read_text(encoding='utf-8'))
    jobs = importlib.import_module(MODULE + '.blender.jobs')
    views = importlib.import_module(MODULE + '.blender.views')
    job = jobs.Job('import', source=str(input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)), job_index=1)
    deadline = time.monotonic() + 120
    while (result := job.poll()) is None:
        if time.monotonic() > deadline:
            job.cancel()
            raise TimeoutError(str(job.directory))
        time.sleep(.1)
    assert result['status'] == 'succeeded', result
    source = views.atom_view(job.directory / 'dataset')
    spectrum = source.qc_settings.spectrum
    before = [tuple(v.color) for v in spectrum.data.color_attributes['qc_ir_color'].data]
    old_mode = source.qc_settings.active_mode
    action(source, 'DUPLICATE')
    copied = bpy.context.object
    assert copied.qc_settings.spectrum != spectrum
    copied.qc_settings.active_mode = (old_mode + 1) % len(source.qc_settings.modes)
    assert source.qc_settings.active_mode == old_mode
    assert [tuple(v.color) for v in spectrum.data.color_attributes['qc_ir_color'].data] == before
    assert [tuple(v.color) for v in copied.qc_settings.spectrum.data.color_attributes['qc_ir_color'].data] != before
    np.testing.assert_array_equal([v.co[:] for v in copied.data.vertices], [v.co[:] for v in source.data.vertices])
    report['vibration_copy_independence'] = 'Passed'
elif '--reopen-layers' in sys.argv:
    report = json.loads((OUT / 'report.json').read_text(encoding='utf-8'))
    assert [obj.name for obj in layers.display_layers(bpy.context.scene)] == report['order']
    first, second = [bpy.data.objects[name] for name in report['fog_objects']]
    assert first.qc_settings.volume == second.qc_settings.volume
    assert material(first) != material(second)
    assert material(first).node_tree.nodes['Optical Scale'].outputs[0].default_value == 20
    assert material(second).node_tree.nodes['Optical Scale'].outputs[0].default_value == 3
    assert all(layer.qc_settings.volume for layer in layers.display_layers(bpy.context.scene)
               if layer.get('qc_view_kind') in ('field', 'slice', 'fog'))
    report['cold_open'] = 'Passed'
else:
    source = next(o for o in bpy.context.scene.objects if o.get('qc_view_kind') == 'field')
    action(source, 'SELECT')
    assert bpy.ops.qcblender.create_fog() == {'FINISHED'}
    first = bpy.context.object
    action(first, 'DUPLICATE')
    second = bpy.context.object
    assert first != second and first.data != second.data
    assert first.modifiers[0].node_group != second.modifiers[0].node_group
    assert first.qc_settings.volume == second.qc_settings.volume
    first_mat, second_mat = material(first), material(second)
    assert first_mat != second_mat
    second_mat.node_tree.nodes['Optical Scale'].outputs[0].default_value = 3
    assert first_mat.node_tree.nodes['Optical Scale'].outputs[0].default_value == 20
    index = layers.display_layers(bpy.context.scene).index(second)
    action(second, 'UP')
    assert layers.display_layers(bpy.context.scene).index(second) == index - 1
    action(second, 'DOWN')
    assert layers.display_layers(bpy.context.scene).index(second) == index
    action(second, 'VISIBILITY')
    assert second.hide_get() and not first.hide_get()
    action(second, 'VISIBILITY')
    assert not second.hide_get()
    action(second, 'SELECT')
    assert bpy.ops.qcblender.add_surface_layer() == {'FINISHED'}
    added = bpy.context.object
    assert added.get('qc_view_kind') == 'field'
    assert Path(bpy.path.abspath(added['qc_dataset'])).resolve() == Path(bpy.path.abspath(first['qc_dataset'])).resolve()
    assert added['qc_dataset_sha256'] == first['qc_dataset_sha256']
    action(added, 'REMOVE')
    action(first, 'SELECT')
    assert bpy.ops.qcblender.create_slice(resolution=17) == {'FINISHED'}
    sliced = bpy.context.object
    assert sliced.qc_settings.volume == first.qc_settings.volume
    action(sliced, 'DUPLICATE')
    copy = bpy.context.object
    assert copy.modifiers[0].node_group != sliced.modifiers[0].node_group
    assert len(copy.modifiers[0].node_group.links) == len(sliced.modifiers[0].node_group.links)
    action(copy, 'REMOVE')
    # Removing the atoms display must preserve the transforms and sources of child layers.
    parent = source.parent
    bpy.context.view_layer.update()
    positions = {child.name: child.matrix_world.copy() for child in parent.children}
    action(parent, 'REMOVE')
    bpy.context.view_layer.update()
    for name, expected in positions.items():
        assert bpy.data.objects[name].matrix_world == expected
    assert first.qc_settings.volume is not None
    project.save_project(OUT / 'layers.blend')
    report = {'status': 'Passed', 'add_remove': 'Passed', 'duplicate_independence': 'Passed',
              'order_visibility': 'Passed', 'preserve_child_transforms': 'Passed',
              'cold_open': 'Not Run', 'undo': 'Not Run',
              'fog_objects': [first.name, second.name],
              'order': [obj.name for obj in layers.display_layers(bpy.context.scene)]}
(OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
