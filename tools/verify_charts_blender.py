"""Run in an isolated installed Blender profile with -- --dataset DIR --out FILE.blend."""

import argparse
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import bpy
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument('--dataset', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--module', default='bl_ext.user_default.qcblender')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
bpy.ops.preferences.addon_enable(module=args.module)
views = importlib.import_module(args.module + '.blender.views')
charts = importlib.import_module(args.module + '.blender.charts')
profiles = importlib.import_module(args.module + '.blender.profile')
contours = importlib.import_module(args.module + '.contours')
layout = importlib.import_module(args.module + '.plot_layout')
storage = importlib.import_module(args.module + '.data')

source = views.field_view(args.dataset)
assert bpy.ops.qcblender.create_slice() == {'FINISHED'}
slice_obj = bpy.context.object
assert slice_obj.get('qc_view_kind') == 'slice'
mat, ramp = charts._mapped_material(slice_obj)
before = [tuple(element.color) for element in sorted(ramp.color_ramp.elements,
                                                       key=lambda item: item.position)]
assert bpy.ops.qcblender.color_palette(palette='BCY') == {'FINISHED'}
assert mat['qc_palette'] == 'BCY'
assert [tuple(element.color) for element in sorted(ramp.color_ramp.elements,
                                                   key=lambda item: item.position)] != before
assert bpy.ops.qcblender.color_palette(palette='RWB') == {'FINISHED'}

charts._contour_defaults(slice_obj)
slice_obj['qc_contour_enabled'] = True
slice_obj['qc_contour_labels'] = True
field_source, plane, identity = charts._state(slice_obj)
modifier, socket_ids = charts.view_modifier(slice_obj), {
    item.name: item.identifier for item in charts.view_modifier(slice_obj).node_group.interface.items_tree
    if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
minimum_id = socket_ids['Color Minimum']
saved_minimum = modifier[minimum_id]
modifier[minimum_id] = saved_minimum - .01
assert charts._state(slice_obj)[2] != identity
modifier[minimum_id] = saved_minimum
binding = slice_obj['qc_color_source']
changed = json.loads(binding)
changed['field']['array'] = 'another_scalar_array'
slice_obj['qc_color_source'] = json.dumps(changed)
try:
    try:
        charts._state(slice_obj)
    except ValueError:
        pass
    else:
        raise AssertionError('Contour accepted a different color array with the same quantity and unit')
finally:
    slice_obj['qc_color_source'] = binding
request = {'dataset': bpy.path.abspath(field_source['qc_dataset']),
           'dataset_sha256': field_source['qc_dataset_sha256'],
           'field': json.loads(field_source['qc_field']), 'plane': plane,
           'levels': '', 'mapping_range': plane['mapping_range'], 'identity': identity}
report = contours.contour_report(request, storage.load_dataset)
assert report['identity'] == identity and len(report['levels']) == 9
minimum, maximum = (plane['mapping_range'][key] for key in ('minimum', 'maximum'))
np.testing.assert_allclose(report['levels'], np.linspace(minimum, maximum, 11)[1:-1])
sample_line = [plane['origin'],
               list(np.asarray(plane['origin']) + .2 * np.asarray(plane['axis_u']))]
draw_report = dict(report, paths=[{'level': report['levels'][0], 'lines': [sample_line]}])
carrier = charts._draw_contours(slice_obj, field_source, plane, draw_report)
slice_obj['qc_contour_child'] = carrier.name
slice_obj['qc_contour_identity'] = identity
assert carrier.parent == slice_obj and carrier.data.bevel_depth == .02
label = next(child for child in carrier.children if child.get('qc_contour_label'))
offset = np.asarray(label.location) - np.asarray(sample_line[1])
normal = np.cross(plane['axis_u'], plane['axis_v'])
normal /= np.linalg.norm(normal)
assert .001 < np.linalg.norm(offset) < .031
np.testing.assert_allclose(offset / np.linalg.norm(offset), normal)
unrelated = bpy.data.objects.new('Unrelated contour child', None)
bpy.context.collection.objects.link(unrelated)
unrelated.parent = carrier
charts._hide_contours(slice_obj)
assert carrier.hide_get() and not carrier['qc_contour_restore_viewport']
assert label.hide_get() and label.hide_render
assert not unrelated.hide_get() and not unrelated.hide_render
charts._restore_contours(slice_obj, identity)
assert not carrier.hide_get() and 'qc_contour_restore_viewport' not in carrier
assert not label.hide_get() and not label.hide_render

label.hide_set(True)
label.hide_render = True
charts._hide_contours(slice_obj)
charts._restore_contours(slice_obj, identity)
assert label.hide_get() and label.hide_render, 'User-hidden label was restored by the watcher'
label.hide_set(False)
label.hide_render = False

carrier.hide_set(True)
carrier.hide_render = True
charts._hide_contours(slice_obj)
charts._restore_contours(slice_obj, identity)
assert carrier.hide_get() and carrier.hide_render, 'User-hidden contour was restored by the watcher'
assert label.hide_get() and label.hide_render, 'Visible label escaped its hidden carrier'
carrier.hide_set(False)
carrier.hide_render = False
charts._restore_contours(slice_obj, identity)
assert not label.hide_get() and not label.hide_render

curve = bpy.data.curves.new('QC profile layout test', 'CURVE')
curve.dimensions = '3D'
curve.materials.append(views.material('QC profile test', (.1, .3, .7, 1)))
profile_obj = bpy.data.objects.new('QC profile layout test', curve)
bpy.context.collection.objects.link(profile_obj)
profile_obj['qc_chart'] = json.dumps({'x_min': 0., 'x_max': 3., 'y_min': 0.,
                                     'y_max': 3., 'sample_count': 4, 'valid_count': 3})
for key, value in layout.DEFAULT_LAYOUT.items():
    profile_obj['qc_profile_' + key] = value
data = SimpleNamespace(arrays={'profile_distance': np.array([0., 1., 2., 3.]),
                               'profile_values': np.array([0., 1., 0., 3.]),
                               'profile_valid': np.array([True, True, False, True])},
                       metadata={'profile': {'field': {'unit': 'test-unit'}}})
original = data.arrays['profile_values'].copy()
result = profiles.apply_profile_layout(profile_obj, data)
assert result['width'] == 4. and result['height'] == 3.
profile_obj['qc_profile_width'] = 6.
profile_obj['qc_profile_y_auto'] = False
profile_obj['qc_profile_y_min'] = -.5
profile_obj['qc_profile_y_max'] = 2.
assert profiles.apply_profile_layout(profile_obj, data)['width'] == 6.
np.testing.assert_array_equal(original, data.arrays['profile_values'])
profile_copy = profile_obj.copy()
profile_copy.data = profile_obj.data.copy()
bpy.context.collection.objects.link(profile_copy)
profiles.copy_profile_ticks(profile_obj, profile_copy, bpy.context.collection)
assert sum(bool(child.get('qc_profile_tick')) for child in profile_copy.children) == sum(
    bool(child.get('qc_profile_tick')) for child in profile_obj.children)
profiles.cleanup_profile_ticks(profile_copy)
assert not any(child.get('qc_profile_tick') for child in profile_copy.children)

args.out.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(args.out))
names = (slice_obj.name, carrier.name, profile_obj.name)
bpy.ops.wm.open_mainfile(filepath=str(args.out))
assert all(name in bpy.data.objects for name in names)
assert bpy.data.objects[names[1]].parent == bpy.data.objects[names[0]]
assert bpy.data.objects[names[2]]['qc_profile_width'] == 6.
print('CHARTS_BLENDER_PASSED')
