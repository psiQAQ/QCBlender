"""Run in an isolated installed Blender profile with -- --module EXTENSION_MODULE."""
import argparse
import importlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--module', default='bl_ext.user_default.qcblender')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
bpy.ops.preferences.addon_enable(module=args.module)
properties = importlib.import_module(args.module + '.blender.properties')

parent = bpy.data.objects.new('Spectrum visibility source', None)
bpy.context.collection.objects.link(parent)
frequencies = np.array([1600., 3600., 3700.])
intensities = np.array([20., 10., 30.])
spectrum = properties.ir_spectrum(parent, frequencies, intensities)
label = next(child for child in spectrum.children if child.get('qc_spectrum_label'))
mesh_before = [vertex.co[:] for vertex in spectrum.data.vertices]
colors_before = [color.color[:] for color in spectrum.data.color_attributes['qc_ir_color'].data]
text_before = label.data.body
unrelated = bpy.data.objects.new('Unrelated spectrum text', bpy.data.curves.new('User text', 'FONT'))
bpy.context.collection.objects.link(unrelated)
unrelated.parent = spectrum
other = properties.ir_spectrum(parent, frequencies, intensities)
other_label = next(child for child in other.children if child.get('qc_spectrum_label'))


def action(operation):
    assert bpy.ops.qcblender.layer_action(target=spectrum.name, action=operation) == {'FINISHED'}
    assert not unrelated.hide_get() and not unrelated.hide_render
    assert not other.hide_get() and not other.hide_render
    assert not other_label.hide_get() and not other_label.hide_render


# Tagged labels remain owned when their datablock is renamed.
original_name = label.data.name
label.data.name = 'Renamed spectrum label'
action('VISIBILITY')
assert spectrum.hide_get() and label.hide_get()
assert not spectrum.hide_render and not label.hide_render
action('RENDER')
assert spectrum.hide_render and label.hide_render
action('VISIBILITY')
assert not spectrum.hide_get() and not label.hide_get()
assert spectrum.hide_render and label.hide_render
action('RENDER')
assert not spectrum.hide_render and not label.hide_render

# Restore individual user choices after toggling the entire layer.
label.hide_set(True)
label.hide_render = True
for operation in ('VISIBILITY', 'VISIBILITY', 'RENDER', 'RENDER'):
    action(operation)
assert label.hide_get() and label.hide_render
label.hide_set(False)
label.hide_render = False

# Existing saved spectra predate the ownership marker.
label.data.name = original_name
del label['qc_spectrum_label']
for operation in ('VISIBILITY', 'RENDER'):
    action(operation)
assert label.hide_get() and label.hide_render
for operation in ('VISIBILITY', 'RENDER'):
    action(operation)
assert not label.hide_get() and not label.hide_render
assert [vertex.co[:] for vertex in spectrum.data.vertices] == mesh_before
assert [color.color[:] for color in spectrum.data.color_attributes['qc_ir_color'].data] == colors_before
assert label.data.body == text_before
np.testing.assert_array_equal(frequencies, [1600., 3600., 3700.])
np.testing.assert_array_equal(intensities, [20., 10., 30.])
report = {'status': 'Passed', 'viewport_render': 'Passed', 'individual_visibility': 'Passed',
          'legacy_labels': 'Passed', 'unrelated_objects': 'Passed', 'scientific_data': 'Passed'}
out = Path(__file__).resolve().parents[1] / 'outputs/spectrum-visibility/report.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
