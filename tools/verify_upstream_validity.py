"""Native GN, shader pixels and CSV checks on one explicitly synthetic field.

Run in an isolated Blender with QCBlender enabled, using --output DIRECTORY and
--module PACKAGE. check(..., configure=callable) also checks a caller's material
operation: the callable receives the slice and its actual shared color material.
No Blender process is launched by this script.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_vmd_parameters as base
from verify_vmd_scalar_edges import analytic_view, evaluated_samples


POINTS = {'physical_zero': (0, 2, 2), 'masked': (1, 0, 0),
          'outside': (-2, 0, 0), 'valid_positive': (2, 2, 2)}


def sample_points(view):
    modifier, names = base.controls(view)
    previous = tuple(modifier[names['Center']])
    rows = {}
    try:
        for label, point in POINTS.items():
            modifier[names['Center']] = point
            sampled = min(evaluated_samples(view),
                          key=lambda row: np.linalg.norm(np.array(row[0]) - point))
            assert np.linalg.norm(np.array(sampled[0]) - point) < 1e-5, (label, sampled)
            rows[label] = dict(position=sampled[0], value=sampled[1], valid=sampled[2], fraction=sampled[3])
    finally:
        modifier[names['Center']] = previous
    assert rows['physical_zero']['valid'] and abs(rows['physical_zero']['value']) < 1e-5, rows
    assert rows['valid_positive']['valid'] and abs(rows['valid_positive']['value'] - 2) < 1e-5, rows
    assert not rows['masked']['valid'] and abs(rows['masked']['value'] - 1) < 1e-5, rows
    assert not rows['outside']['valid'], rows
    return rows


def legend_samples(view, material):
    modifier, names = base.controls(view)
    modifier[names['Show Legend']] = True
    view.update_tag()
    bpy.context.view_layer.update()
    evaluated = view.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        attrs = mesh.attributes
        marked = [bool(item.value) for item in attrs['qc_legend'].data]
        indices = [index for index, value in enumerate(marked) if value]
        assert len(indices) == 130, len(indices)
        assert all(attrs['qc_sample_valid'].data[index].value for index in indices)
        polygons = [polygon for polygon in mesh.polygons if all(marked[index] for index in polygon.vertices)]
        # Depsgraph meshes may reference evaluated Material IDs. Compare their
        # original datablocks so copies with identical names remain distinct.
        used_slots = sorted({polygon.material_index for polygon in polygons})
        identity = {'legend_polygons': len(polygons), 'expected_material': material.name,
                    'expected_original': material.original.as_pointer(),
                    'slots': [{'index': index, 'name': mesh.materials[index].name,
                               'is_evaluated': mesh.materials[index].is_evaluated,
                               'original': mesh.materials[index].original.as_pointer()}
                              for index in used_slots]}
        assert polygons and all(mesh.materials[index].original == material.original
                                for index in used_slots), identity
        print('LEGEND_MATERIAL_IDENTITY: ' + json.dumps(identity))
        fractions = [attrs['qc_color_fraction'].data[index].value for index in indices]
        np.testing.assert_allclose([min(fractions), max(fractions)], [0, 1], atol=1e-6)
        assert any(abs(value - .5) < 1e-6 for value in fractions)
        return {label: dict(fraction=min(fractions, key=lambda value: abs(value - wanted)), valid=True)
                for label, wanted in [('legend_min', 0), ('legend_center', .5), ('legend_max', 1)]}
    finally:
        evaluated.to_mesh_clear()
        modifier[names['Show Legend']] = False


def shader_pixels(material, samples, destination):
    """Render the unmodified scalar shader's emission path with evaluated attributes.

    qc_legend selects the product's unlit branch for quantitative RGB readback;
    the surface Base Color must consume that identical missing-value color socket.
    This verifies material colors, not lighting on a molecular surface.
    """
    nodes = material.node_tree.nodes
    principled = next(node for node in nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
    emission = next(node for node in nodes if node.bl_idname == 'ShaderNodeEmission')
    assert principled.inputs['Base Color'].links[0].from_socket == emission.inputs['Color'].links[0].from_socket
    scene = bpy.data.scenes.new('QC validity pixel check')
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = 128 * len(samples), 128
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    scene.render.image_settings.file_format = 'OPEN_EXR'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '32'
    camera_data = bpy.data.cameras.new('QC validity camera')
    camera = bpy.data.objects.new('QC validity camera', camera_data)
    scene.collection.objects.link(camera)
    camera.location = ((len(samples) - 1) / 2, 0, 5)
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = len(samples)
    scene.camera = camera
    vertices, faces = [], []
    for index in range(len(samples)):
        start = len(vertices)
        vertices.extend([(index + x, y, 0) for x, y in [(-.4, -.4), (.4, -.4), (.4, .4), (-.4, .4)]])
        faces.append(tuple(range(start, start + 4)))
    mesh = bpy.data.meshes.new('QC evaluated sample swatches')
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    swatches = bpy.data.objects.new('QC evaluated sample swatches', mesh)
    scene.collection.objects.link(swatches)
    for name, kind, values in [
            ('qc_color_fraction', 'FLOAT', [row['fraction'] for row in samples.values()]),
            ('qc_sample_valid', 'BOOLEAN', [row['valid'] for row in samples.values()]),
            ('qc_opacity', 'FLOAT', [1.] * len(samples)),
            ('qc_legend', 'BOOLEAN', [True] * len(samples))]:
        mesh.attributes.new(name, kind, 'POINT').data.foreach_set('value', [value for value in values for _ in range(4)])
    scene.render.filepath = str(destination)
    try:
        bpy.ops.render.render(write_still=True, scene=scene.name)
        image = bpy.data.images.load(str(destination), check_existing=False)
        try:
            pixels = np.array(image.pixels[:]).reshape(image.size[1], image.size[0], 4)
            assert tuple(image.size) == (scene.render.resolution_x, scene.render.resolution_y)
            return {label: pixels[64, index * 128 + 64].tolist() for index, label in enumerate(samples)}
        finally:
            bpy.data.images.remove(image)
    finally:
        bpy.data.objects.remove(swatches, do_unlink=True)
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.meshes.remove(mesh)
        bpy.data.cameras.remove(camera_data)
        bpy.data.scenes.remove(scene)


def profile_csv(view, out):
    storage = base.module('data')
    directory = Path(bpy.path.abspath(view['qc_dataset']))
    source = storage.load_dataset(directory)
    field = source.metadata['fields'][0]
    profile = base.module('profile')
    # The line contains grid-exterior points, the mask hole, and adjacent valid points.
    start, end = (1, -1, 0), (1, 2, 0)
    data = profile.sample_profile(source, field, start, end, start, end,
                                  hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest(), count=7)
    target = out / 'profile-dataset'
    storage.save_dataset(data, target)
    result = base.module('data_export').export_dataset(target, out / 'csv', 'profile')
    exported = Path(result['directory'])
    with (exported / 'profile.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 7
    assert not data.arrays['profile_valid'][0] and not data.arrays['profile_valid'][2]
    assert data.arrays['profile_valid'][-2:].all()
    for row, value, valid in zip(rows, data.arrays['profile_values'], data.arrays['profile_valid'], strict=True):
        assert row['valid'] == str(int(valid))
        if valid:
            assert float(row['value']) == float(value)
        else:
            assert row['value'] == '', row
    metadata = json.loads((exported / 'metadata.json').read_text(encoding='utf-8'))
    assert metadata['scientific_metadata'] == data.metadata
    return dict(directory=str(exported), rows=rows,
                files={path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in (exported / 'profile.csv', exported / 'metadata.json')})


def check(output, module='bl_ext.user_default.qcblender', configure=None):
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    base.MODULE = module
    bpy.ops.preferences.addon_enable(module=module)
    view = analytic_view(out, 0)
    base.activate(view)
    assert bpy.ops.qcblender.create_slice(resolution=3, minimum=0, maximum=2) == {'FINISHED'}
    sliced = bpy.context.object
    sliced.name = 'QC upstream validity slice'
    modifier, names = base.controls(sliced)
    for name, value in [('Width', .2), ('Height', .2), ('Center', (0, 2, 2))]:
        modifier[names[name]] = value
    group = next(node for node in modifier.node_group.nodes if node.bl_idname == 'GeometryNodeGroup'
                 and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2')
    material = group.inputs['Material'].default_value
    before = base.hashes()
    initial_samples = sample_points(sliced)
    if configure is not None:
        configure(sliced, material)
    assert sample_points(sliced) == initial_samples, 'Material operation changed scalar values/mask/fraction'
    ramp = next(node.color_ramp for node in material.node_tree.nodes if node.get('qc_role') == 'color_ramp')
    invert = next(node for node in material.node_tree.nodes if node.get('qc_role') == 'color_invert')
    original_invert = invert.outputs[0].default_value
    report = dict(status='Running', module=module,
                  module_file=str(Path(base.module('blender.scalars').__file__).resolve()),
                  blender=bpy.app.version_string,
                  fixture='Synthetic scalar x on 3x3x3 grid with mask[1,0,0]=False; engineering evidence only',
                  GN_samples=initial_samples, renders={}, independent_scientific_acceptance='Not Run')
    try:
        for reverse in (0, 1):
            invert.outputs[0].default_value = reverse
            samples = sample_points(sliced)
            assert samples == initial_samples, 'Reverse changed scalar values/mask/fraction'
            samples.update(legend_samples(sliced, material))
            destination = out / f'colors-reverse-{reverse}.exr'
            pixels = shader_pixels(material, samples, destination)
            for label, row in samples.items():
                expected = list(ramp.evaluate(abs(reverse - row['fraction']))) if row['valid'] else [1, 0, 1, 1]
                np.testing.assert_allclose(pixels[label], expected, atol=2e-3,
                                           err_msg=f'{label} reverse={reverse} shader RGB mismatch')
            np.testing.assert_allclose(pixels['physical_zero'], pixels['legend_min'], atol=2e-3)
            np.testing.assert_allclose(pixels['valid_positive'], pixels['legend_max'], atol=2e-3)
            assert not np.allclose(pixels['physical_zero'], pixels['masked'], atol=2e-3)
            report['renders'][str(reverse)] = dict(path=str(destination), rgba=pixels)
        report['profile_csv'] = profile_csv(view, out)
        assert base.hashes() == before, 'Material checks mutated source Dataset files'
        report['source_files_sha256'] = before
        report['status'] = 'Passed'
        return report
    finally:
        invert.outputs[0].default_value = original_invert


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--module', default='bl_ext.user_default.qcblender')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        result = check(args.output, args.module)
    except Exception as error:
        (args.output / 'validity.json').write_text(json.dumps(
            dict(status='Failed', error_type=type(error).__name__, error=str(error)), indent=2), encoding='utf-8')
        raise
    (args.output / 'validity.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('UPSTREAM_VALIDITY_PASSED: GN mask, shader colors, shared legend, CSV and source hashes')
