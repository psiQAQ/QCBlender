"""Measure 1/8/32 real MO views, dependency graph updates, meshes and CPU renders.

This records completed dependency graph work, not viewport FPS. A view contains
an atom layer plus a two-phase MO surface. Scene construction precedes warmups.
"""
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import benchmark_fields as bench


def controls(obj):
    modifier = bench.module('blender.graph').view_modifier(obj)
    return modifier, {s.name: s.identifier for s in modifier.node_group.interface.items_tree
                      if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}


def completed(action, timeout):
    """Includes dependency graph completion; post-check catches overlong blocking calls."""
    import bpy
    started = time.perf_counter()
    action()
    bpy.context.view_layer.update()
    bpy.context.evaluated_depsgraph_get().update()
    seconds = time.perf_counter() - started
    if seconds > timeout:
        raise TimeoutError(f'Dependency graph operation exceeded {timeout}s: {seconds}s')
    return seconds


def extract(objects, timeout):
    import bpy
    started = time.perf_counter()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    counts = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            counts.append([len(mesh.vertices), len(mesh.polygons)])
        finally:
            evaluated.to_mesh_clear()
    seconds = time.perf_counter() - started
    if seconds > timeout:
        raise TimeoutError('Mesh extraction exceeded timeout')
    if any(vertices == 0 or polygons == 0 for vertices, polygons in counts):
        raise ValueError('Expected nonempty rendered meshes: ' + str(counts))
    return seconds, counts


def clear_scene():
    import bpy
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    # Only the dedicated benchmark scene is present. Remove unused display data
    # before building the next group so previous copies do not remain resident.
    for _ in range(4):
        for collection in (bpy.data.meshes, bpy.data.volumes, bpy.data.materials, bpy.data.node_groups,
                           bpy.data.cameras, bpy.data.lights):
            for item in list(collection):
                if item.users == 0:
                    collection.remove(item)


def build_scene(source, field, count):
    import bpy
    from mathutils import Vector
    clear_scene()
    started = time.perf_counter()
    views = bench.module('blender.views')
    atoms, surfaces = [], []
    columns = min(8, count)
    rows = (count + columns - 1) // columns
    for index in range(count):
        atom = views.atom_view(source)
        surface = views.field_view(field, atom)
        atom.location = ((index % columns - (columns - 1) / 2) * 4,
                         (index // columns - (rows - 1) / 2) * 4, 0)
        atoms.append(atom)
        surfaces.append(surface)
    scene = bpy.context.scene
    camera = bpy.data.objects.new('Performance camera', bpy.data.cameras.new('Performance camera'))
    scene.collection.objects.link(camera)
    camera.location = (0, -2, 30)
    camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = max(columns * 4 + 2, (rows * 4 + 2) * 640 / 448)
    scene.camera = camera
    light = bpy.data.objects.new('Performance area', bpy.data.lights.new('Performance area', 'AREA'))
    scene.collection.objects.link(light)
    light.location = (0, 0, 20)
    light.data.energy = 3000
    light.data.shape = 'DISK'
    light.data.size = 20
    scene.world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value = (.15, .15, .15, 1)
    scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value = .5
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.seed = 17
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = 640, 448
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.use_persistent_data = False
    for obj in surfaces:
        modifier, names = controls(obj)
        modifier[names['Isovalue']] = .05
        obj.update_tag()
    bpy.context.view_layer.update()
    return atoms, surfaces, time.perf_counter() - started


def set_controls(objects, key, value):
    for obj in objects:
        modifier, names = controls(obj)
        modifier[names[key]] = value
        obj.update_tag()


def render(path, timeout):
    import bpy
    import numpy as np
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    started = time.perf_counter()
    result = bpy.ops.render.render(write_still=True)
    seconds = time.perf_counter() - started
    if seconds > timeout:
        raise TimeoutError('Render exceeded timeout')
    if result != {'FINISHED'} or not path.is_file():
        raise RuntimeError('Render did not publish expected PNG')
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        pixels = np.asarray(image.pixels[:]).reshape(-1, 4)
        if tuple(image.size) != (640, 448) or not np.isfinite(pixels).all() or (pixels[:, 3] > .01).sum() < 100:
            raise ValueError('Render is empty, invalid or has wrong dimensions')
    finally:
        bpy.data.images.remove(image)
    return seconds


def main():
    args = bench.parser(__doc__, 'views', '1,8,32').parse_args(bench.cli_arguments())
    report = bench.setup(args, 'display')
    try:
        bench.enable(args, report)
        report['parameters'].update(views=args.views, grid=bench.grid(31), isovalue=.05,
            render={'engine': 'CYCLES', 'device': 'CPU', 'samples': 32, 'seed': 17, 'resolution': [640, 448],
                    'adaptive_sampling': False, 'denoising': False, 'view_transform': 'Standard', 'look': 'None'})
        report['timing_definition'].update(display='Threshold/atom selection writes through dependency graph completion',
            mesh='Evaluated mesh extraction after dependency graph completion',
            render='Canonical .05 threshold/all atoms, CPU render through PNG publication; validation outside timer',
            threshold='Reset .06, measure .05; all surfaces updated', selection='Reset carbon-only, measure all; all atom layers updated',
            ui_timeout='Blocking UI operations are checked after return; launcher must enforce process deadline')
        source, report['import'] = bench.run_job('import', args.timeout, source=str(bench.SOURCE), source_sha256=bench.sha256(bench.SOURCE))
        field, report['evaluate'] = bench.run_job('evaluate', args.timeout, **bench.evaluation(source, 31))
        if report['evaluate']['cache_hit'] or report['evaluate']['cache_rejected']:
            raise ValueError('Initial display evaluation must be a cold cache miss')
        original = {'source': bench.dataset_identity(source), 'field': bench.dataset_identity(field)}
        report['scientific_identity'] = original
        report['summary'], report['scene_setup'] = {}, {}
        for count in args.views:
            atoms, surfaces, setup_seconds = build_scene(source, field, count)
            expected_counts = None
            report['scene_setup'][str(count)] = {'seconds': setup_seconds, 'atom_layers': len(atoms), 'surface_layers': len(surfaces)}
            for iteration in range(args.warmups + args.repeats):
                warmup = iteration < args.warmups
                trial = {'views': count, 'iteration': iteration, 'ui_process_id': __import__('os').getpid()}
                (report['warmups'] if warmup else report['trials']).append(trial)
                # Reset to the alternate state before each timed update, ensuring
                # each trial performs actual changed graph work after rendering.
                completed(lambda: set_controls(surfaces, 'Isovalue', .06), args.timeout)
                completed(lambda: set_controls(atoms, 'Element (0 = all)', 6), args.timeout)
                _, restricted = extract(atoms, args.timeout)
                trial['threshold_seconds'] = completed(lambda: set_controls(surfaces, 'Isovalue', .05), args.timeout)
                trial['selection_seconds'] = completed(lambda: set_controls(atoms, 'Element (0 = all)', 0), args.timeout)
                trial['mesh_seconds'], trial['mesh_counts'] = extract(surfaces + atoms, args.timeout)
                if expected_counts is not None and trial['mesh_counts'] != expected_counts:
                    raise ValueError('Canonical mesh counts changed across repeated display trials')
                expected_counts = trial['mesh_counts']
                if any(full == partial for full, partial in zip(trial['mesh_counts'][count:], restricted)):
                    raise ValueError('Atom selection did not change evaluated meshes')
                prefix = 'warmup' if warmup else 'trial'
                png = args.output / f'{count}-{prefix}-{iteration}.png'
                trial['render_seconds'] = render(png, args.timeout)
                trial['render_sha256'] = bench.sha256(png)
                trial['ui_peak_working_set_mib'] = bench.process_peak()
                if {'source': bench.dataset_identity(source), 'field': bench.dataset_identity(field)} != original:
                    raise ValueError('Display updates changed scientific arrays')
                if bench.sha256(bench.SOURCE) != report['source']['sha256']:
                    raise ValueError('Scientific input changed')
                bench.save(args.output, report)
            report['summary'][str(count)] = bench.summary([t for t in report['trials'] if t['views'] == count])
        report['status'] = 'Passed'
        if args.baseline:
            report['comparison'] = bench.compare(report, args.baseline)
        bench.save(args.output, report)
    except BaseException as error:
        report.update(status='Failed', error=f'{type(error).__name__}: {error}')
        if hasattr(error, 'job_directory'):
            report['failed_job_directory'] = error.job_directory
        bench.save(args.output, report)
        raise


if __name__ == '__main__':
    main()
