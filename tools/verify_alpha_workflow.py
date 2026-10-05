"""Installed Alpha: public P01 MO9, live summaries and portable cold reopening."""
import argparse
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

import bpy

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--reopen', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
args.report.parent.mkdir(parents=True, exist_ok=True)
report = {'status': 'Failed', 'source_commit': subprocess.check_output(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'candidate_sha256': hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
    'gui': 'Not Run', 'independent_alpha_installation': 'Not Run', 'checks': {}}


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(job, expect='succeeded'):
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == expect, result
            return result
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


def mesh_counts(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return [len(mesh.vertices), len(mesh.polygons)]
    finally:
        evaluated.to_mesh_clear()


def summary(obj):
    snapshot = module('blender.view_summary').capture_view_summary(obj, bpy.context.scene.frame_current)
    owner = module('blender.source_browser').source_object(obj)
    result = run(module('blender.jobs').Job('export_data',
        dataset=bpy.path.abspath(owner['qc_dataset']), dataset_sha256=owner['qc_dataset_sha256'],
        output_directory=str(OUT / 'exports'), kind='SUMMARY', scope='ALL', filters={},
        export_token=uuid.uuid4().hex, view_snapshot=snapshot))
    directory = Path(result['directory'])
    metadata = json.loads((directory / 'metadata.json').read_text(encoding='utf-8'))
    assert (directory / 'view-summary.md').is_file()
    assert metadata['view_summary']['display'] == snapshot['display']
    report.setdefault('summaries', []).append({'view': obj.name, 'directory': str(directory),
        'status': snapshot['display']['status'], 'metadata_sha256': digest(directory / 'metadata.json')})
    return snapshot


try:
    assert bpy.app.version[:3] == (5, 1, 1)
    bpy.ops.preferences.addon_enable(module=MODULE)
    installed = Path(importlib.import_module(MODULE).__file__).resolve().parent
    for source in (ROOT / 'qcblender').rglob('*.py'):
        assert (installed / source.relative_to(ROOT / 'qcblender')).read_bytes() == source.read_bytes()
    storage, jobs, views = map(module, ('data', 'blender.jobs', 'blender.views'))
    if args.reopen:
        report = json.loads(args.report.read_text(encoding='utf-8'))
        assert report['source_commit'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        assert report['candidate_sha256'] == digest(args.candidate)
        surface = bpy.data.objects[report['surface_name']]
        assert mesh_counts(surface) == report['surface_counts']
        for obj in bpy.data.objects:
            if 'qc_dataset' in obj:
                directory = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
                assert directory.is_relative_to(Path(bpy.data.filepath).parent.resolve())
                data = storage.load_dataset(directory)
                assert data.metadata['source']['sha256'] == report['source_sha256']
                assert digest(directory / 'manifest.json') == obj['qc_dataset_sha256']
        snapshot = summary(surface)
        isovalue = next(entry['value'] for entry in snapshot['display']['parameters'] if entry['name'] == 'Isovalue')
        assert abs(isovalue - .045) < 1e-7
        assert not module('blender.ui')._qualifications
        report.update(status='Passed', cold_open='Passed')
    else:
        source = ROOT / 'tests/data/tutorial/P01/o2-uhf.fchk'
        source_record = json.loads((ROOT / 'docs/v1-acceptance/tutorial-samples.json').read_text(encoding='utf-8'))['files']['P01-o2-uhf']
        assert digest(source) == source_record['sha256']
        report['source_sha256'] = digest(source)
        importer = jobs.Job('import', source=str(source))
        run(importer)
        directory = importer.directory / 'dataset'
        manifest_sha = digest(directory / 'manifest.json')
        qualification = jobs.Job('qualify_science', dataset=str(directory), dataset_sha256=manifest_sha)
        qualified = run(qualification)
        assert qualified['eligible'] and not (qualification.directory / 'dataset').exists()
        preview = qualified['preview']
        preflight = module('science_preflight')
        grid = preflight.preview_grid(preview, .2, 3)
        parameters = {'quantity': 'orbital_amplitude', 'spin': 'alpha', 'orbital': 9, 'memory_mb': 512}
        request = {'dataset': str(directory), 'dataset_sha256': manifest_sha,
                   'science_sha256': qualified['science_sha256'], 'grid': grid, 'parameters': parameters}
        generator = jobs.Job('evaluate', **request)
        run(generator)
        repeated = run(jobs.Job('evaluate', **request))
        assert repeated['cache_hit']
        oversized = dict(request, grid=dict(grid, shape=[512, 512, 512]), parameters=dict(parameters, memory_mb=16384))
        rejected = jobs.Job('evaluate', **oversized)
        refusal = run(rejected, 'failed')
        assert 'dataset arrays' in refusal['error'] and not (rejected.directory / 'dataset').exists()
        unsupported = deepcopy(storage.load_dataset(directory))
        unsupported.metadata['method'] = 'unqualified'
        unsupported_dir = OUT / 'unsupported-input'
        unsupported_manifest = storage.save_dataset(unsupported, unsupported_dir)
        refusal_job = jobs.Job('qualify_science', dataset=str(unsupported_dir), dataset_sha256=digest(unsupported_manifest))
        assert not run(refusal_job)['eligible']
        assert not (refusal_job.directory / 'dataset').exists()
        for obj in bpy.context.scene.objects:
            obj.hide_render = True
        atoms = views.atom_view(directory)
        surface = views.field_view(generator.directory / 'dataset', atoms)
        modifier = module('blender.graph').view_modifier(surface)
        sockets = {item.name: item.identifier for item in modifier.node_group.interface.items_tree
                   if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
        modifier[sockets['Isovalue']] = .03
        low = mesh_counts(surface)
        modifier[sockets['Isovalue']] = .045
        high = mesh_counts(surface)
        assert low != high and high[0] > 0
        first = summary(surface)
        second = summary(surface)
        assert first['display'] == second['display']
        assert report['summaries'][-1]['directory'] != report['summaries'][-2]['directory']
        value = next(entry['value'] for entry in second['display']['parameters'] if entry['name'] == 'Isovalue')
        assert abs(value - .045) < 1e-7
        summary(atoms)
        atom_modifier = module('blender.graph').view_modifier(atoms)
        material_socket = next(item for item in atom_modifier.node_group.interface.items_tree
                               if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.name == 'Material')
        saved_material = atom_modifier[material_socket.identifier]
        assert material_socket.default_value is not None
        del atom_modifier[material_socket.identifier]
        missing_material = summary(atoms)['display']
        assert missing_material['status'] == 'partial'
        assert not any(item['role'] == 'Material' for item in missing_material['materials'])
        atom_modifier[material_socket.identifier] = saved_material
        custom_material = bpy.data.materials.new('Alpha summary custom Emission')
        custom_material.use_nodes = True
        custom_material.node_tree.nodes.clear()
        emission = custom_material.node_tree.nodes.new('ShaderNodeEmission')
        output = custom_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        custom_material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        atom_modifier[material_socket.identifier] = custom_material
        custom_material_summary = summary(atoms)['display']
        assert custom_material_summary['status'] == 'partial'
        assert any('unverified' in reason for reason in custom_material_summary['reasons'])
        atom_modifier[material_socket.identifier] = saved_material
        module('blender.layers').activate(bpy.context, atoms)
        saved_digest = atoms['qc_dataset_sha256']
        atoms['qc_dataset_sha256'] = '0' * 64
        try:
            module('blender.ui').science_binding(bpy.context)
        except ValueError as error:
            assert 'saved source binding' in str(error)
        else:
            raise AssertionError('Stale source binding was accepted')
        finally:
            atoms['qc_dataset_sha256'] = saved_digest
        fog = module('blender.fog').fog_view(surface)
        fog.hide_render = True
        before = summary(fog)
        fog_mat = next(mat for mat in bpy.data.materials if mat.get('qc_fog'))
        ramp = next(node for node in fog_mat.node_tree.nodes if node.get('qc_role') == 'color_ramp')
        ramp.color_ramp.elements[0].color = (.1, .7, .2, 1)
        after = summary(fog)
        assert before['display']['materials'] != after['display']['materials']
        module('blender.layers').activate(bpy.context, surface)
        assert bpy.ops.qcblender.create_slice() == {'FINISHED'}
        sliced = bpy.context.object
        sliced.hide_render = True
        summary(sliced)
        saved_quality = modifier[sockets['Quality']]
        del modifier[sockets['Quality']]
        assert summary(surface)['display']['status'] in ('partial', 'unverified')
        modifier[sockets['Quality']] = saved_quality
        tree = modifier.node_group
        graph_version = tree['qc_view_graph']
        tree['qc_view_graph'] = -1
        custom = summary(surface)
        assert custom['display']['status'] == 'unverified' and not custom['display']['parameters']
        tree['qc_view_graph'] = graph_version
        module('blender.layers').activate(bpy.context, surface)
        scene = bpy.context.scene
        camera = bpy.data.objects.new('Alpha camera', bpy.data.cameras.new('Alpha camera'))
        scene.collection.objects.link(camera)
        camera.location = (8, -10, 6)
        camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.type, camera.data.ortho_scale = 'ORTHO', 8
        scene.camera = camera
        for location, energy in [((4, -6, 8), 1500), ((-5, -2, 3), 900)]:
            light = bpy.data.objects.new('Alpha light', bpy.data.lights.new('Alpha light', 'AREA'))
            scene.collection.objects.link(light)
            light.data.energy, light.data.size = energy, 5
            light.location = location
            light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
        scene.world.color = (.18, .18, .18)
        scene.render.engine, scene.cycles.samples = 'CYCLES', 24
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 640, 480, 100
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(OUT / 'example.png')
        bpy.ops.render.render(write_still=True)
        module('blender.project').save_project(OUT / 'example.blend')
        moved = OUT / '中文路径移动'
        moved.mkdir(exist_ok=True)
        shutil.copy2(OUT / 'example.blend', moved / 'example.blend')
        shutil.copytree(OUT / 'example.qcdata', moved / 'example.qcdata', dirs_exist_ok=True)
        (OUT / 'README.md').write_text('# QCBlender Alpha P01 MO9\n\nBlender 5.1.1 / Windows x64.\n'
            'P01 o2-uhf.fchk, Alpha source MO9, spacing 0.2 Å, margin 3 Å, budget 512 MiB, '
            'isovalue 0.045 bohr^-3/2.\nKeep example.blend and example.qcdata together.\n'
            'Input attribution: QCBlender contributors, CC BY 4.0; retain sample ZIP LICENSE and NOTICE.\n'
            'Technical automation only; independent user/scientific acceptance remains Not Run.\n', encoding='utf-8')
        report.update(status='Passed', portable_saved=True, cold_open='Not Run',
            moved_blend=str(moved / 'example.blend'), surface_name=surface.name, surface_counts=high,
            grid=grid, parameters=parameters, isovalue=.045)
        report['checks'] = {name: 'Passed' for name in ('qualification', 'unsupported_science',
            'cache_hit', 'early_dataset_limit', 'live_isovalue', 'live_color_ramp',
            'standard_view_summaries', 'missing_input', 'missing_material', 'custom_material', 'stale_source_binding',
            'custom_graph', 'repeat_export', 'render', 'portable_save')}
    for name in ('gbasis', 'iodata', 'scipy'):
        assert name not in sys.modules, name + ' leaked into the UI process'
except Exception as error:
    report.update(status='Failed', error=f'{type(error).__name__}: {error}')
    raise
finally:
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: report.get(key) for key in ('status', 'error', 'cold_open')}))
