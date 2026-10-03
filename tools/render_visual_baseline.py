"""Render one installed-extension scene and compare it with a reviewed PNG."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visual_regression import THRESHOLDS, check_identity, compare_pixels

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
CASES = ('atoms', 'signed-mo', 'density-esp', 'slice-contours', 'fog', 'legend-annotations')
REGIONS = {'molecule': [80, 35, 560, 350]}
SCENE = {'resolution': [640, 448], 'samples': 32, 'seed': 17,
         'camera': [0., 0., 12.], 'ortho_scale': 8., 'field_spacing': .2,
         'mo': {'orbital': 8, 'spin': 'alpha', 'isovalue': .05},
         'color_range': [-.05, .05], 'legend_position': [0., -2., 2.],
         'slice_resolution': 81, 'contour_levels': '-0.03, 0.0, 0.03'}


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def controls(obj):
    modifier = module('blender.graph').view_modifier(obj)
    return modifier, {item.name: item.identifier for item in modifier.node_group.interface.items_tree
                      if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}


def set_control(obj, name, value):
    modifier, names = controls(obj)
    modifier[names[name]] = value
    obj.update_tag()
    bpy.context.view_layer.update()


def activate(obj):
    module('blender.layers').activate(bpy.context, obj)


def finish(job):
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            if result['status'] != 'succeeded':
                raise RuntimeError(result)
            return job.directory / 'dataset', result
        time.sleep(.05)
    job.cancel()
    raise TimeoutError('Visual fixture worker: ' + str(job.directory))


def array_identity(directory):
    data = module('data').load_dataset(directory)
    return {key: {'shape': list(value.shape), 'dtype': str(value.dtype),
                  'sha256': hashlib.sha256(value.tobytes(order='C')).hexdigest()}
            for key, value in sorted(data.arrays.items())}


def configure_scene():
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    camera = bpy.data.objects.new('Baseline camera', bpy.data.cameras.new('Baseline camera'))
    scene.collection.objects.link(camera)
    camera.location = SCENE['camera']
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = SCENE['ortho_scale']
    scene.camera = camera
    for location, energy, size in [((4, -6, 8), 1500, 5), ((-5, -2, 3), 900, 4), ((1, 5, 6), 1200, 3)]:
        light = bpy.data.objects.new('Baseline area', bpy.data.lights.new('Baseline area', 'AREA'))
        scene.collection.objects.link(light)
        light.data.energy, light.data.size = energy, size
        light.location = location
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world = bpy.data.worlds.new('Baseline world')
    scene.world.use_nodes = True
    background = next(node for node in scene.world.node_tree.nodes if node.type == 'BACKGROUND')
    background.inputs['Color'].default_value = (.18, .18, .18, 1.)
    background.inputs['Strength'].default_value = .8
    scene.render.engine = 'CYCLES'
    scene.cycles.device, scene.cycles.samples, scene.cycles.seed = 'CPU', SCENE['samples'], SCENE['seed']
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.render.resolution_x, scene.render.resolution_y = SCENE['resolution']
    scene.render.resolution_percentage = 100
    scene.render.threads_mode, scene.render.threads = 'FIXED', 4
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.display_settings.display_device = 'sRGB'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure, scene.view_settings.gamma = 0., 1.


def environment():
    scene = bpy.context.scene
    return {'blender': bpy.app.version_string, 'build_hash': bpy.app.build_hash.decode(),
            'engine': scene.render.engine, 'device': scene.cycles.device,
            'samples': scene.cycles.samples, 'seed': scene.cycles.seed,
            'denoising': scene.cycles.use_denoising, 'adaptive_sampling': scene.cycles.use_adaptive_sampling,
            'threads': scene.render.threads, 'resolution': [scene.render.resolution_x, scene.render.resolution_y],
            'display': scene.display_settings.display_device, 'view': scene.view_settings.view_transform,
            'look': scene.view_settings.look, 'exposure': scene.view_settings.exposure,
            'gamma': scene.view_settings.gamma, 'font_files': sorted({font.filepath for font in bpy.data.fonts}),
            'pixel_space': 'decoded PNG RGB, Non-Color, [0,1]'}


def prepare_case(case):
    configure_scene()
    jobs, views = module('blender.jobs'), module('blender.views')
    source = ROOT / 'tests/data/chemtools/ch4_uhf_ccpvdz.fchk'
    directory, _ = finish(jobs.Job('import', source=str(source)))
    atoms = views.atom_view(directory)
    assert len(atoms.data.vertices) == 5 and len(atoms.data.edges) == 4
    datasets = {'atoms': directory}
    objects = {'atoms': atoms}
    quantities = [] if case == 'atoms' else ['orbital_amplitude'] if case in ('signed-mo', 'fog') else [
        'electron_number_density', 'electrostatic_potential']
    for quantity in quantities:
        shape = [31, 31, 31]
        if case == 'density-esp' and quantity == 'electrostatic_potential':
            shape[0] = 19  # Real ESP sampled only to x=0.6 A; the density surface extends beyond it.
        parameters = {'quantity': quantity, 'memory_mb': 512}
        if quantity == 'orbital_amplitude':
            parameters.update(orbital=8, spin='alpha')
        field_dir, _ = finish(jobs.Job('evaluate', dataset=str(directory),
            grid={'origin': [-3., -3., -3.], 'steps': [[.2, 0, 0], [0, .2, 0], [0, 0, .2]], 'shape': shape},
            parameters=parameters))
        datasets[quantity] = field_dir
        objects[quantity] = views.field_view(field_dir, atoms)
    if case in ('density-esp', 'legend-annotations'):
        target, color = objects['electron_number_density'], objects['electrostatic_potential']
        module('blender.scalars').add_mapping(target, color, -.05, .05)
        color.hide_render = True
        color.hide_set(True)
        objects['target'] = target
    elif case == 'slice-contours':
        color = objects['electrostatic_potential']
        activate(color)
        assert bpy.ops.qcblender.create_slice(resolution=81, minimum=-.05, maximum=.05) == {'FINISHED'}
        target = bpy.context.object
        set_control(target, 'Center', (0., 0., .4))
        set_control(target, 'Width', 5.)
        set_control(target, 'Height', 5.)
        charts = module('blender.charts')
        charts._contour_defaults(target)
        target['qc_contour_enabled'] = True
        target['qc_contour_source'] = 'GEOMETRY'
        target['qc_contour_levels'] = SCENE['contour_levels']
        source_view, plane, identity = charts._state(target)
        _, report = finish(jobs.Job('contours', dataset=bpy.path.abspath(source_view['qc_dataset']),
            dataset_sha256=source_view['qc_dataset_sha256'], field=json.loads(source_view['qc_field']),
            plane=plane, levels=target['qc_contour_levels'], mapping_range=plane.get('mapping_range'), identity=identity))
        carrier = charts._draw_contours(target, source_view, plane, report)
        assert len(carrier.data.splines) > 0, 'Expected real ESP contour paths'
        target['qc_contour_child'], target['qc_contour_identity'] = carrier.name, identity
        color.hide_render = objects['electron_number_density'].hide_render = True
        atoms.hide_render = True
        objects['target'] = target
    elif case == 'fog':
        surface = objects['orbital_amplitude']
        activate(surface)
        assert bpy.ops.qcblender.create_fog() == {'FINISHED'}
        target = bpy.context.object
        modifier, names = controls(target)
        modifier[names['Material']].node_tree.nodes['Optical Scale'].outputs[0].default_value = 20
        surface.hide_render = True
        objects['target'] = target
    if case == 'legend-annotations':
        target = objects['target']
        set_control(target, 'Show Legend', True)
        set_control(target, 'Legend Position', SCENE['legend_position'])
        set_control(target, 'Legend Length', 3.)
        set_control(target, 'Legend Text Size', .18)
        activate(atoms)
        assert bpy.ops.qcblender.add_annotation(kind='DISTANCE', atoms='1,2', size=.18,
            color=(1., .8, .2), offset=(0., 1.7, 2.), decimals=4) == {'FINISHED'}
        assert any(child.type == 'FONT' for child in atoms.children)
    for role, obj in objects.items():
        obj['qc_baseline_role'] = role
    bpy.context.view_layer.update()
    scientific = {key: array_identity(value) for key, value in datasets.items()}
    return objects, datasets, scientific, digest(source)


def mutate(case, objects, mutation):
    if mutation == 'hide-negative' and case == 'signed-mo':
        set_control(objects['orbital_amplitude'], 'Negative Phase', False)
    elif mutation in ('legend-unit', 'legend-position') and case == 'legend-annotations':
        target = objects['target']
        if mutation == 'legend-position':
            set_control(target, 'Legend Position', (1.5, -1., 2.))
        else:
            tree = controls(target)[0].node_group
            title = next(node for node in tree.nodes if node.label == 'QC Legend Title')
            original = title.inputs['String'].default_value
            assert 'hartree/e' in original, original
            title.inputs['String'].default_value = original.replace('hartree/e', 'eV/e')
            target.update_tag()
    elif mutation == 'disable-valid-mask' and case == 'density-esp':
        tree = controls(objects['target'])[0].node_group
        assign = next(node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
                      and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2')
        assert len(assign.inputs['Valid'].links) == 1
        tree.links.remove(assign.inputs['Valid'].links[0])
        assign.inputs['Valid'].default_value = True
        objects['target'].update_tag()
    else:
        raise ValueError('Mutation is not applicable to case ' + case)
    bpy.context.view_layer.update()


def read_pixels(path):
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        image.colorspace_settings.name = 'Non-Color'
        return np.asarray(image.pixels[:], dtype=np.float64).reshape(image.size[1], image.size[0], 4)[::-1, :, :3].copy()
    finally:
        bpy.data.images.remove(image)


def save_difference(actual, expected, path):
    height, width, _ = actual.shape
    image = bpy.data.images.new('Visual difference x8', width=width, height=height, alpha=True)
    try:
        pixels = np.ones((height, width, 4), dtype=np.float32)
        pixels[:, :, :3] = np.clip(np.abs(actual - expected) * 8, 0, 1)
        image.colorspace_settings.name = 'Non-Color'
        image.pixels.foreach_set(pixels[::-1].ravel())
        image.filepath_raw, image.file_format = str(path), 'PNG'
        image.save()
    finally:
        bpy.data.images.remove(image)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=CASES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'tests/data/visual-baseline')
    parser.add_argument('--mode', choices=('compare', 'record'), default='compare')
    parser.add_argument('--mutation', choices=('hide-negative', 'legend-unit', 'legend-position', 'disable-valid-mask'))
    parser.add_argument('--reopen', type=Path, help='Cold-open a self-contained scene produced by this tool')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    output, baseline = args.output.resolve(), args.baseline.resolve()
    if output == baseline or output.is_relative_to(baseline):
        raise ValueError('Output must not replace or enter the reference directory')
    output.mkdir(parents=True, exist_ok=False)
    report = {'status': 'Running', 'case': args.case, 'mode': args.mode, 'mutation': args.mutation,
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'independent_human_review': 'Not Run'}
    try:
        assert bpy.app.version[:3] == (5, 1, 1), 'Reference profile requires Blender 5.1.1'
        bpy.ops.preferences.addon_enable(module=MODULE)
        installed = Path(importlib.import_module(MODULE).__file__).resolve().parent
        report['installed_source_sha256'] = {path.relative_to(installed).as_posix(): digest(path)
                                            for path in sorted(installed.rglob('*.py'))}
        expected_source = {path.relative_to(ROOT / 'qcblender').as_posix(): digest(path)
                           for path in sorted((ROOT / 'qcblender').rglob('*.py'))}
        assert report['installed_source_sha256'] == expected_source, 'Installed Python files differ from checkout'
        if args.reopen:
            bpy.ops.wm.open_mainfile(filepath=str(args.reopen.resolve()))
            saved = json.loads(bpy.context.scene['qc_visual_baseline'])
            assert saved['case'] == args.case
            objects = {obj['qc_baseline_role']: obj for obj in bpy.context.scene.objects if 'qc_baseline_role' in obj}
            datasets = {key: Path(bpy.path.abspath(value)) for key, value in saved['datasets'].items()}
            scientific = {key: array_identity(value) for key, value in datasets.items()}
            assert scientific == saved['scientific_arrays']
            source_sha = saved['input_sha256']
        else:
            objects, datasets, scientific, source_sha = prepare_case(args.case)
        if args.mutation:
            mutate(args.case, objects, args.mutation)
        regions = dict(REGIONS)
        if args.case == 'legend-annotations':
            regions.update(legend=[155, 345, 590, 435], annotation=[330, 35, 600, 145])
        identity = {'environment': environment(), 'scene': dict(SCENE, case=args.case, regions=regions),
                    'input_sha256': source_sha, 'scientific_arrays': scientific}
        image_path = output / (args.case + '.png')
        bpy.context.scene.render.filepath = str(image_path)
        started = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        report['render_seconds'] = time.perf_counter() - started
        actual = read_pixels(image_path)
        assert np.ptp(actual) > .1, 'Blank visual render'
        assert {key: array_identity(value) for key, value in datasets.items()} == scientific
        report.update(identity=identity, image_sha256=digest(image_path), scientific_arrays_unchanged='Passed')
        if args.mode == 'compare':
            expected = json.loads((baseline / (args.case + '.json')).read_text(encoding='utf-8'))
            check_identity(identity, expected['identity'])
            reference_path = baseline / (args.case + '.png')
            assert digest(reference_path) == expected['image_sha256'], 'Reference PNG checksum changed'
            reference = read_pixels(reference_path)
            comparison = compare_pixels(actual, reference, regions)
            report.update(status=comparison['status'], comparison=comparison)
            save_difference(actual, reference, output / 'difference-x8.png')
        else:
            report.update(status='Recorded', thresholds=THRESHOLDS, baseline_review='Pending Agent visual inspection')
        if not args.reopen:
            project_path = output / (args.case + '.blend')
            module('blender.project').save_project(project_path)
            relocated = {key: bpy.path.relpath(bpy.path.abspath(obj['qc_dataset']))
                         for key, obj in objects.items() if key in datasets}
            assert set(relocated) == set(datasets)
            bpy.context.scene['qc_visual_baseline'] = json.dumps(dict(case=args.case, datasets=relocated,
                scientific_arrays=scientific, input_sha256=source_sha))
            bpy.ops.wm.save_as_mainfile(filepath=str(project_path))
            report['project'] = project_path.name
    except Exception as error:
        report.update(status='Failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        (output / (args.case + '.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps({key: report[key] for key in ('status', 'case', 'mode', 'mutation')}), flush=True)
    if report['status'] == 'Failed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
