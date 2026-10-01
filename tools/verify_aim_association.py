"""Exercise real C09 association through the installed Blender operators."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import sys
import time

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--reopen', choices=('saved', 'moved'))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
storage = importlib.import_module(MODULE + '.data')
project = importlib.import_module(MODULE + '.blender.project')
browser = importlib.import_module(MODULE + '.blender.source_browser')
activate = importlib.import_module(MODULE + '.blender.layers').activate
REPORT = OUT / 'aim.json'


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.get('qc_dataset'):
            data = storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
            result[obj.name] = {
                'manifest': obj['qc_dataset_sha256'],
                'arrays': {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in data.arrays.items()},
                'source_group': list(browser.source_group(obj)[0]),
                'analysis': data.metadata.get('analysis'),
                'diagnostics': data.metadata['diagnostics']}
    return result


def panel_labels(obj):
    # Isolate the layout sink; use the real installed panel and bound source cache.
    from types import SimpleNamespace

    class Labels:
        def __init__(self):
            self.text = []

        def label(self, *, text):
            self.text.append(text)

        def prop(self, *args, **kwargs):
            pass

    layout = Labels()
    panel = importlib.import_module(MODULE + '.blender.external_results').QCBLENDER_PT_external_results
    panel.draw(SimpleNamespace(layout=layout), SimpleNamespace(object=obj))
    expected = storage.load_dataset(bpy.path.abspath(obj['qc_dataset'])).metadata['analysis']['properties']['1']
    assert 'CP_type: ' + expected['CP_type'] in layout.text
    for key in ('Corresponding nucleus', 'Density of all electrons', 'Position (Angstrom)'):
        assert f'{key}: {expected[key]}'[:110] in layout.text, (key, layout.text)
    return len(layout.text)


if args.reopen:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert snapshot() == report['snapshot']
    for obj in bpy.context.scene.objects:
        if obj.get('qc_dataset'):
            assert Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(
                Path(bpy.data.filepath).with_suffix('.qcdata'))
    bpy.context.scene.render.filepath = str(OUT / (args.reopen + '.png'))
    bpy.ops.render.render(write_still=True)
    report[args.reopen + '_cold_reopen'] = 'Passed'
else:
    Job = importlib.import_module(MODULE + '.blender.jobs').Job
    job = Job('import', source=str(input_path('complex-examples/Trp_polar.fchk', ROOT)))
    deadline = time.monotonic() + 180
    while True:
        receipt = job.poll()
        if receipt is not None:
            assert receipt['status'] == 'succeeded', receipt
            break
        if time.monotonic() > deadline:
            job.cancel()
            raise TimeoutError(str(job.directory))
        time.sleep(.1)
    for obj in bpy.context.scene.objects:
        obj.hide_render = True
        obj.hide_set(True)
    atoms = importlib.import_module(MODULE + '.blender.views').atom_view(job.directory / 'dataset')
    activate(bpy.context, atoms)
    sources = input_path('sop/multiwfn-local/C09', ROOT)
    arguments = dict(cps_path=str(sources / 'CPs.pdb'), paths_path=str(sources / 'paths.pdb'))
    assert bpy.ops.qcblender.import_aim_analysis(**arguments,
        properties_path=str(sources / 'CPprop.txt')) == {'FINISHED'}
    objects = [obj for obj in bpy.context.scene.objects if obj.get('qc_analysis_role', '').startswith('aim_')]
    assert {obj['qc_analysis_role']: len(obj.data.vertices) for obj in objects if obj.type == 'MESH'} == {
        'aim_C': 27, 'aim_N': 29, 'aim_O': 3}
    paths = next(obj for obj in objects if obj.type == 'CURVE')
    assert len(paths.data.splines) == 58
    cp = next(obj for obj in objects if obj.get('qc_analysis_role') == 'aim_C')
    valid = storage.load_dataset(bpy.path.abspath(cp['qc_dataset']))
    assert len(valid.metadata['analysis']['properties']) == 59
    assert valid.metadata['diagnostics'] == []
    immediate_panel_labels = panel_labels(cp)
    browser.refresh_source(cp)
    assert panel_labels(cp) == immediate_panel_labels
    text = (sources / 'CPprop.txt').read_text(encoding='utf-8')
    errors = {}
    for name, altered, message in (
        ('type', text.replace('Type (3,-3)', 'Type (3,-1)', 1), 'type conflicts'),
        ('position', re.sub(r'^ Position \(Angstrom\):.*$', ' Position (Angstrom): 10 0 0',
                           text, count=1, flags=re.M), 'position conflicts'),
        ('malformed', re.sub(r'^ Position \(Angstrom\):.*$', ' Position (Angstrom): nan 0 0',
                            text, count=1, flags=re.M), 'malformed or nonfinite')):
        path = OUT / (name + '-CPprop.txt')
        path.write_text(altered, encoding='utf-8')
        before = (set(bpy.data.objects.keys()), set(bpy.data.meshes.keys()),
                  set(bpy.data.curves.keys()), set(bpy.data.node_groups.keys()))
        try:
            bpy.ops.qcblender.import_aim_analysis(**arguments, properties_path=str(path))
        except RuntimeError as error:
            assert message in str(error), str(error)
            errors[name] = str(error).strip()
        else:
            raise AssertionError('Invalid AIM import did not report an error')
        assert before == (set(bpy.data.objects.keys()), set(bpy.data.meshes.keys()),
                          set(bpy.data.curves.keys()), set(bpy.data.node_groups.keys()))
    missing = re.sub(r'^.*CP\s+1,\s+Type \(3,-3\).*$\n', ' Critical point 1:\n', text, count=1, flags=re.M)
    missing = re.sub(r'^ Position \(Angstrom\):.*$\n', '', missing, count=1, flags=re.M)
    path = OUT / 'missing-CPprop.txt'
    path.write_text(missing, encoding='utf-8')
    before = set(bpy.data.objects.keys())
    assert bpy.ops.qcblender.import_aim_analysis(**arguments, properties_path=str(path)) == {'FINISHED'}
    for name in set(bpy.data.objects.keys()) - before:
        obj = bpy.data.objects[name]
        assert 'unverified for 1 CP(s)' in obj['qc_diagnostics']
        obj.hide_render = True
        obj.hide_set(True)
    scene = bpy.context.scene
    center = sum((atoms.matrix_world @ v.co for v in atoms.data.vertices), Vector()) / len(atoms.data.vertices)
    camera_data = bpy.data.cameras.new('AIM acceptance camera')
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((8, -20, 12))
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type, camera_data.ortho_scale = 'ORTHO', 15
    scene.camera = camera
    light_data = bpy.data.lights.new('AIM acceptance light', 'AREA')
    light_data.energy, light_data.size = 1800, 8
    light = bpy.data.objects.new(light_data.name, light_data)
    scene.collection.objects.link(light)
    light.location = center + Vector((4, -5, 12))
    light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world.color = (.2, .2, .2)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x, scene.render.resolution_y = 800, 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(OUT / 'C09.png')
    bpy.ops.render.render(write_still=True)
    paths.hide_render = True
    scene.render.filepath = str(OUT / 'C09-points.png')
    bpy.ops.render.render(write_still=True)
    paths.hide_render = False
    for obj in objects:
        if obj.type == 'MESH':
            obj.hide_render = True
    scene.render.filepath = str(OUT / 'C09-paths.png')
    bpy.ops.render.render(write_still=True)
    for obj in objects:
        obj.hide_render = False
    activate(bpy.context, cp)
    project.save_project(OUT / 'C09.blend')
    moved = OUT / 'moved'
    moved.mkdir(exist_ok=True)
    shutil.copy2(OUT / 'C09.blend', moved / 'C09.blend')
    shutil.copytree(OUT / 'C09.qcdata', moved / 'C09.qcdata', dirs_exist_ok=True)
    report = {'status': 'Passed', 'blender': bpy.app.version_string,
              'actual_cp_count': 59, 'actual_path_count': 58, 'valid_association': 'Passed',
              'errors_preserve_scene': 'Passed', 'error_messages': errors,
              'missing_diagnostics': 'Passed', 'point_path_visibility_render': 'Passed',
              'panel_labels_before_and_after_refresh': 'Passed',
              'immediate_panel_label_count': immediate_panel_labels,
              'saved_cold_reopen': 'Not Run', 'moved_cold_reopen': 'Not Run', 'snapshot': snapshot()}
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'snapshot'}))
