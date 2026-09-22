"""Native offline installation, worker, geometry and cold-open acceptance probe."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import zipfile

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/acceptance'
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
REPORT = OUT / 'extension.json'


def mesh_count(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return len(mesh.vertices), len(mesh.polygons)
    finally:
        evaluated.to_mesh_clear()


def run_job(job):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return result
        time.sleep(0.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


if '--reopen' in sys.argv:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    bpy.ops.preferences.addon_enable(module=MODULE)
    storage = importlib.import_module(MODULE + '.data')
    obj = bpy.data.objects[report['surface_name']]
    actual = mesh_count(obj)
    assert list(actual) == report['surface_counts'], (actual, report['surface_counts'])
    assert bpy.data.volumes[report['volume_name']].grids.load()
    root = Path(bpy.data.filepath).parent.resolve()
    for obj in bpy.data.objects:
        if 'qc_dataset' in obj:
            path = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
            assert path.is_relative_to(root), path
            storage.load_dataset(path)
            assert hashlib.sha256((path / 'manifest.json').read_bytes()).hexdigest() == obj['qc_dataset_sha256']
    for volume in bpy.data.volumes:
        assert Path(bpy.path.abspath(volume.filepath)).resolve().is_relative_to(root)
    report['cold_open'] = 'Passed'
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
else:
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(ROOT / 'outputs')
    assert bpy.ops.extensions.package_install_files(
        filepath=str(ROOT / 'outputs/dist/qcblender-0.0.1.zip'), repo='user_default',
        enable_on_install=True, overwrite=True) == {'FINISHED'}
    jobs = importlib.import_module(MODULE + '.blender.jobs')
    views = importlib.import_module(MODULE + '.blender.views')
    diagnose = run_job(jobs.Job('diagnose'))
    assert diagnose['ok']
    for name in ('gbasis', 'iodata', 'scipy'):
        assert name not in sys.modules, f'{name} leaked into the UI process'
    importer = jobs.Job('import', source=str(ROOT / 'tests/data/chemtools/ch4_uhf_ccpvdz.fchk'))
    run_job(importer)
    for obj in bpy.data.objects:
        obj.hide_render = True
    atoms = views.atom_view(importer.directory / 'dataset')
    assert len(atoms.data.vertices) == 5 and len(atoms.data.edges) == 4
    assert mesh_count(atoms)[0] > 100
    generator = jobs.Job('evaluate', dataset=str(importer.directory / 'dataset'),
                         grid={'origin': [-3, -3, -3], 'steps': [[.2, 0, 0], [0, .2, 0], [0, 0, .2]],
                               'shape': [31, 31, 31]},
                         parameters={'quantity': 'orbital_amplitude', 'orbital': 8, 'spin': 'alpha', 'memory_mb': 512})
    run_job(generator)
    repeated = json.loads((generator.directory / 'request.json').read_text(encoding='utf-8'))
    repeated.pop('schema')
    repeated.pop('job_id')
    second_job = jobs.Job(**repeated)
    repeated_report = run_job(second_job)
    assert repeated_report['cache_hit'], repeated_report
    assert (second_job.directory / 'dataset/manifest.json').read_bytes() == (generator.directory / 'dataset/manifest.json').read_bytes()
    directory = generator.directory / 'dataset'
    digest = hashlib.sha256((directory / 'field.vdb').read_bytes()).hexdigest()
    surface = views.field_view(directory, atoms)
    modifier = surface.modifiers[0]
    inputs = {s.name: s.identifier for s in modifier.node_group.interface.items_tree
              if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
    first = mesh_count(surface)
    assert first[0] > 100
    modifier[inputs['Isovalue']] = .10
    second = mesh_count(surface)
    assert first != second and second[0] > 0
    modifier[inputs['Negative Phase']] = False
    positive = mesh_count(surface)
    modifier[inputs['Negative Phase']] = True
    modifier[inputs['Positive Phase']] = False
    negative = mesh_count(surface)
    assert positive[0] > 0 and negative[0] > 0
    assert positive[0] + negative[0] == second[0]
    modifier[inputs['Positive Phase']] = True
    modifier[inputs['Isovalue']] = .05
    final_counts = mesh_count(surface)
    assert hashlib.sha256((directory / 'field.vdb').read_bytes()).hexdigest() == digest
    cancelled = jobs.Job('diagnose')
    cancelled.cancel()
    assert cancelled.process.poll() is not None
    assert not (cancelled.directory / 'result.json').exists()
    bpy.ops.preferences.addon_disable(module=MODULE)
    assert not hasattr(bpy.types, 'QCBLENDER_PT_main')
    bpy.ops.preferences.addon_enable(module=MODULE)
    assert hasattr(bpy.types, 'QCBLENDER_PT_main')
    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new('QC acceptance camera')
    camera = bpy.data.objects.new('QC acceptance camera', camera_data)
    scene.collection.objects.link(camera)
    camera.location = (7, -10, 6)
    camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 8
    scene.camera = camera
    for location, energy, size in [((4, -6, 8), 1500, 5), ((-5, -2, 3), 900, 4), ((1, 5, 6), 1200, 3)]:
        light_data = bpy.data.lights.new('QC acceptance light', 'AREA')
        light_data.energy, light_data.shape, light_data.size = energy, 'DISK', size
        light = bpy.data.objects.new('QC acceptance light', light_data)
        scene.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world.color = (.18, .18, .18)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.render.resolution_x, scene.render.resolution_y = 800, 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(OUT / 'mo8.png')
    project = importlib.import_module(MODULE + '.blender.project')
    project.save_project(OUT / 'mo8.blend')
    bpy.ops.render.render(write_still=True)
    volume = surface.qc_settings.volume.data
    package = importlib.import_module(MODULE + '.project')
    archive_path = package.archive_project(OUT / 'mo8.blend', OUT / 'portable.zip')
    moved = OUT / 'moved 中文 path'
    moved.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(moved)
    report = {'status': 'Passed', 'blender': bpy.app.version_string, 'offline_install': 'Passed',
              'worker_import_evaluate': 'Passed', 'cancel': 'Passed', 'lifecycle': 'Passed',
              'repeated_field_cache': 'Passed',
              'threshold_updates_geometry': 'Passed', 'phase_switches': 'Passed',
              'field_cache_unchanged': 'Passed', 'cold_open': 'Not Run',
              'portable_archive': 'Passed', 'relocated_blend': str(moved / 'mo8.blend'),
              'surface_name': surface.name, 'volume_name': volume.name, 'surface_counts': list(final_counts),
              'positive_counts': list(positive), 'negative_counts': list(negative)}
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
