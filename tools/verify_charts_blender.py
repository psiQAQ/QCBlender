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
field_source, plane, identity = charts._state(slice_obj)
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
           'levels': '', 'identity': identity}
report = contours.contour_report(request, storage.load_dataset)
assert report['identity'] == identity and len(report['levels']) in (0, 9)
carrier = charts._draw_contours(slice_obj, field_source, plane, report)
slice_obj['qc_contour_child'] = carrier.name
slice_obj['qc_contour_identity'] = identity
assert carrier.parent == slice_obj and carrier.data.bevel_depth == .02

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
