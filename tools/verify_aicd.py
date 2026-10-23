"""Real AICD source, native geometry, CSV and portable-project verification."""
import argparse
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--module', default='qcblender')
parser.add_argument('--science-site', type=Path)
parser.add_argument('--source-dir', required=True, type=Path)
parser.add_argument('--output-dir', required=True, type=Path)
parser.add_argument('--reopen', action='store_true')
parser.add_argument('--render', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
if args.module == 'qcblender':
    sys.path.insert(0, str(ROOT))
    if args.science_site:
        sys.path.insert(1, str(args.science_site))
    importlib.import_module(args.module).register()
else:
    bpy.ops.preferences.addon_enable(module=args.module)


def api(name):
    return importlib.import_module(args.module+'.'+name)


def activate(obj):
    for item in bpy.context.selected_objects:
        item.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def inspect(obj):
    data = api('data').load_dataset(bpy.path.abspath(obj['qc_dataset']))
    parts = {c.get('qc_aicd_part'):c for c in obj.children}
    bpy.context.view_layer.update()
    evaluated = parts['surface'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    count = len(mesh.vertices)
    assert count > 0
    # The native field mask must reject surface vertices whose trilinear cell is invalid.
    from scipy.ndimage import map_coordinates
    points = np.array([v.co[:] for v in mesh.vertices])
    field = data.metadata['fields'][0]
    coordinates = ((points-field['origin'])/field['steps'][0][0]).T
    validity = map_coordinates(data.arrays['aicd_grid_valid'].astype(float), coordinates, order=1, mode='constant', cval=0)
    assert np.min(validity) > .99998, float(np.min(validity))
    evaluated.to_mesh_clear()
    config = api('blender.aicd').settings(obj)
    positions, vectors, indexes = api('aicd').arrow_samples(data, config['isovalue'], config['field'], config['arrow_limit'])
    assert list(parts['arrows']['qc_aicd_grid_ids']) == indexes.tolist()
    assert len(parts['arrows'].data.vertices) == len(indexes)*31
    for i in range(min(len(indexes), 30)):
        tip = np.array(parts['arrows'].data.vertices[i*31+30].co)
        np.testing.assert_allclose(tip-positions[i], vectors[i]*config['length_scale'], atol=1e-6, rtol=1e-5)
    return {'science':{key:hashlib.sha256(v.tobytes()).hexdigest() for key,v in data.arrays.items()},
            'settings':config,'surface_vertices':count,'arrows':len(indexes),
            'point':json.loads(obj['qc_aicd_point']), 'minimum_surface_validity':float(validity.min())}


def main():
    if args.reopen:
        old = json.loads((OUT/'native.json').read_text())
        current = {o.name:inspect(o) for o in bpy.context.scene.objects if o.get('qc_view_kind')=='aicd'}
        assert current == old['objects']
        for obj in bpy.context.scene.objects:
            if obj.get('qc_dataset'):
                assert str(obj['qc_dataset']).startswith('//')
        return {'status':'Passed','objects':current,'relative_data_bindings':True}
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    reference = api('readers').read_source(args.source_dir/'all/all.fchk')
    reference_dir = OUT/'reference'
    api('data').save_dataset(reference, reference_dir)
    parent = api('blender.views').atom_view(reference_dir)
    objects = []
    for role in ['all','pi']:
        data = api('aicd').import_aicd(reference, args.source_dir/role/'source.json')
        directory = OUT/role
        directory.mkdir(exist_ok=True)
        field = data.metadata['fields'][0]
        field['vdb'] = 'field.vdb'
        api('worker').write_volume(data, directory/'field.vdb')
        field['vdb_sha256'] = api('data')._file_sha256(directory/'field.vdb')
        field['display_precision'] = 'float32'
        api('data').save_dataset(data, directory)
        obj = api('blender.aicd').create_view(directory, data, parent, .05)
        obj.location.x = -3.6 if role=='all' else 3.6
        objects.append(obj)
        original = inspect(obj)
        config = api('blender.aicd').settings(obj)
        activate(obj)
        assert bpy.ops.qcblender.aicd_settings(**{**config,'field':(0,0,-3),'arrow_limit':250}) == {'FINISHED'}
        assert inspect(obj)['science'] == original['science']
        assert bpy.ops.qcblender.aicd_point(index=12345) == {'FINISHED'}
        expected = api('aicd').sample_record(data,12345,(0,0,-1))
        assert json.loads(obj['qc_aicd_point']) == expected
        config = api('blender.aicd').settings(obj)
        before = obj['qc_aicd_settings']
        try:
            bpy.ops.qcblender.aicd_settings(**{**config,'field':(0,0,0)})
        except RuntimeError:
            pass
        else:
            raise AssertionError('Zero field should fail')
        assert obj['qc_aicd_settings'] == before
        exported = api('data_export').export_dataset(directory,OUT/'export','AICD',filters={'field':[0,0,-1]})
        with (Path(exported['directory'])/'aicd_samples.csv').open(newline='') as stream:
            rows = csv.DictReader(stream)
            for count,row in enumerate(rows,1):
                if count-1==12345:
                    np.testing.assert_allclose([float(row[k]) for k in ['Jx','Jy','Jz']],expected['current'])
            assert count==240570
        assert bpy.ops.qcblender.aicd_settings(**{**config,'field':(0,0,1),'arrow_limit':600}) == {'FINISHED'}
    parent.hide_render = True
    parent.hide_set(True)
    if args.render:
        from mathutils import Vector
        scene=bpy.context.scene
        camera=bpy.data.objects.new('AICD camera',bpy.data.cameras.new('AICD camera'))
        scene.collection.objects.link(camera)
        camera.location=(0,-11,16)
        camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.type='ORTHO'
        camera.data.ortho_scale=16
        scene.camera=camera
        for location,power,size in [((0,-3,10),1800,8),((5,5,7),1200,6)]:
            light=bpy.data.objects.new('AICD light',bpy.data.lights.new('AICD light','AREA'))
            scene.collection.objects.link(light)
            light.location=location
            light.data.energy,light.data.size=power,size
        scene.world.use_nodes=True
        scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(1,1,1,1)
        scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.8
        scene.render.engine='CYCLES'
        scene.cycles.samples=24
        scene.view_settings.view_transform='Standard'
        scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=1400,800,100
        scene.render.filepath=str(OUT/'aicd.png')
        bpy.ops.render.render(write_still=True)
    activate(objects[0])
    project=api('blender.project').save_project(OUT/'aicd.blend')
    return {'status':'Passed','project':str(project),'objects':{obj.name:inspect(obj) for obj in objects},
            'csv_rows_per_contribution':240570,'independent_human_scientific_acceptance':'Not Run'}


try:
    report=main()
except Exception:
    (OUT/'failure.txt').write_text(traceback.format_exc())
    raise
(OUT/('reopen.json' if args.reopen else 'native.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'objects':len(report['objects']),'output':str(OUT)}))
