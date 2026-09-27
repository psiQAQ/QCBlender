"""Extra installed-extension checks using real C07 pairs and an analytic GN grid."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_vmd_parameters as base


C07 = {
    'IGMH': ('d118e51e9fbe71ba3fcd41c90ad7fbdff38defcede73a6fabf23f138acba4345',
             'dg_inter.cub', '3d8c044dbbac7a08f18f7bb6a4fa1a71628157c24d3b781bcb0da993bcc99695',
             'sl2r.cub', 'ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514',
             'delta_g', 'electron/bohr^4'),
    'IRI': ('7fad22457236fe2c56fe3343588bc4679a81ff9dfbb4161f2fc1367703c54fa4',
            'func2.cub', 'a08baaa600115d4321c826be6c1783ecc17649a3b52728f363cbe5faf7e41a1f',
            'func1.cub', 'ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514',
            'iri_function', 'a.u. (electron^-0.1 bohr^-0.7)'),
}


def evaluated_samples(obj):
    """Read actual evaluated Geometry Nodes attributes, including the validity bit."""
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        attrs = [mesh.attributes[name].data for name in
                 ('qc_scalar_value', 'qc_sample_valid', 'qc_color_fraction')]
        return [(tuple(vertex.co), attrs[0][i].value, bool(attrs[1][i].value), attrs[2][i].value)
                for i, vertex in enumerate(mesh.vertices)]
    finally:
        evaluated.to_mesh_clear()


def analytic_view(out, number, job=None):
    """Two real but explicitly synthetic Dataset sources with the same filename."""
    data_module = base.module('data')
    values = np.broadcast_to(np.arange(3, dtype=np.float64)[:, None, None], (3, 3, 3)).copy()
    values += number * .1
    job = number if job is None else job
    valid = np.ones((3, 3, 3), dtype=bool)
    valid[1, 0, 0] = False
    directory = out / 'datasets' / f'analytic-source-{number + 1}-job-{job + 1}'
    directory.mkdir(parents=True, exist_ok=True)
    source_bytes = f'analytic VMD edge fixture {number}\n'.encode('ascii')
    (directory / 'synthetic-grid.txt').write_bytes(source_bytes)
    field = {'quantity': 'analytic_scalar', 'unit': 'test-unit', 'array': 'scalar',
             'valid_mask': 'valid', 'origin': [0, 0, 0],
             'steps': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'shape': [3, 3, 3],
             'coordinate_unit': 'angstrom', 'vdb': 'field.vdb'}
    data = data_module.Dataset({
        'source': {'filename': 'synthetic-grid.txt', 'sha256': hashlib.sha256(source_bytes).hexdigest(),
                   'parser': 'analytic fixture'},
        'coordinate_unit': 'angstrom', 'selected_job': job,
        'jobs': [{'id': f'analytic-{i + 1}', 'route': 'analytic fixture', 'status': 'complete'}
                 for i in range(2)], 'fields': [field], 'diagnostics': []},
        {'atomic_numbers': np.array([1], dtype=np.int32),
         'positions': np.zeros((1, 3)), 'scalar': values, 'valid': valid})
    base.module('worker').write_volume(data, directory / 'field.vdb')
    field['vdb_sha256'] = hashlib.sha256((directory / 'field.vdb').read_bytes()).hexdigest()
    data_module.save_dataset(data, directory)
    obj = base.module('blender.views').field_view(directory)
    obj.name = f'VMD analytic source {number + 1} Job {job + 1}'
    obj.hide_render = True
    return obj


def check_edges(out):
    bpy.ops.preferences.addon_enable(module=base.MODULE)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    browser = base.module('blender.source_browser')
    views = base.module('blender.views')
    scalars = base.module('blender.scalars')
    report = {'checks': {}, 'c07': {}}
    evidence = base.ROOT / 'outputs/source-adoption/04-profile/final-sop/cases/C07/C07.qcdata/datasets'
    for kind, (digest, geo_name, geo_sha, color_name, color_sha, quantity, unit) in C07.items():
        original = evidence / digest
        directory = out / 'datasets' / f'C07-{kind}'
        shutil.copytree(original, directory, dirs_exist_ok=True)
        assert hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest() == digest
        geometry, color = (views.field_view(directory, index=i) for i in (0, 1))
        geometry.name, color.name = f'C07 {kind} geometry', f'C07 {kind} color'
        geometry.hide_render = color.hide_render = True
        _, geometry_field, meta, geometry_source = browser.bound_field(geometry)
        _, color_field, _, color_source = browser.bound_field(color)
        assert meta['analysis']['kind'] == kind
        assert (geometry_field['role'], geometry_field['quantity'], geometry_field['unit']) == (
            'geometry', quantity, unit)
        assert (color_field['role'], color_field['quantity'], color_field['unit']) == (
            'color', 'sign_lambda2_rho', 'electron/bohr^3')
        assert (geometry_source['filename'], geometry_source['sha256']) == (geo_name, geo_sha)
        assert (color_source['filename'], color_source['sha256']) == (color_name, color_sha)
        base.activate(geometry)
        assert bpy.ops.qcblender.select_color_field(source_name=color.name, minimum=-.02, maximum=.02) == {'FINISHED'}
        linked, linked_field, _ = browser.mapped_field(geometry)
        recorded = json.loads(geometry['qc_color_source'])
        assert linked == color.qc_settings.volume and linked_field == color_field
        assert recorded['field_source']['sha256'] == color_sha
        assert recorded['field_source']['filename'] == color_name
        report['c07'][kind] = {'geometry_source_sha256': geo_sha, 'color_source_sha256': color_sha,
                                'geometry_quantity': quantity, 'color_quantity': color_field['quantity'],
                                'status': 'Passed'}
    report['checks']['C07_real_geometry_color_roles'] = 'Passed'

    first, second = analytic_view(out, 0), analytic_view(out, 1)
    candidates = {row['name']: row for row in scalars.color_field_candidates(bpy.context)}
    a, b = candidates[first.name], candidates[second.name]
    assert a['source']['filename'] == b['source']['filename'] == 'synthetic-grid.txt'
    assert a['source']['sha256'] != b['source']['sha256']
    assert a['job'] == 0 and b['job'] == 1
    for row, number in ((a, 1), (b, 2)):
        assert ('synthetic-grid.txt' in row['label'] and row['source']['sha256'][:12] in row['label']
                and f'Job {number}' in row['label'])
    assert browser.source_group(first)[0] != browser.source_group(second)[0]
    same_source = analytic_view(out, 0, job=1)
    c = next(row for row in scalars.color_field_candidates(bpy.context) if row['name'] == same_source.name)
    assert c['source'] == a['source'] and c['job'] != a['job']
    assert browser.source_group(first)[0] != browser.source_group(same_source)[0]
    report['checks']['same_filename_distinct_source_and_job_labels'] = 'Passed'
    report['candidate_labels'] = [a['label'], b['label'], c['label']]
    report['identity_fixture'] = 'Synthetic metadata tests file and calculation identity independently; not a Gaussian calculation.'
    before_arrays = base.hashes()

    # Both views sample the same analytic x field through installed QC GN assets.
    base.activate(first)
    modifier, names = base.controls(first)
    modifier[names['Isovalue']] = .8
    modifier[names['Negative Phase']] = False
    assert bpy.ops.qcblender.select_color_field(source_name=first.name, minimum=0, maximum=2) == {'FINISHED'}
    assert bpy.ops.qcblender.create_slice(resolution=5, minimum=0, maximum=2) == {'FINISHED'}
    sliced = bpy.context.object
    sliced.name = 'VMD analytic slice'
    sliced.hide_render = True
    slice_modifier, slice_names = base.controls(sliced)
    for name, value in {'Center': (.8, 1, 1), 'Rotation': (0, math.pi / 2, 0),
                        'Width': 1., 'Height': 1., 'Resolution': 5}.items():
        slice_modifier[slice_names[name]] = value
    ranges = base.module('blender.color_ranges')
    for interval, expected in (((0, 1, 2), .4), ((1.2, 1.5, 1.8), 0.),
                               ((-.8, -.5, -.2), 1.)):
        for obj in (first, sliced):
            ranges.apply_range(obj, interval)
            samples = [row for row in evaluated_samples(obj) if row[2]]
            assert samples, (obj.name, interval)
            assert all(abs(row[1] - .8) < .04 and abs(row[3] - expected) < .03
                       for row in samples), (obj.name, interval, samples[:5])
    report['checks']['surface_slice_equal_three_point_mapping_and_clamp'] = 'Passed'

    ranges.apply_range(sliced, (0, 1, 2))
    slice_modifier[slice_names['Rotation']] = (0, 0, 0)
    slice_modifier[slice_names['Width']] = .2
    slice_modifier[slice_names['Height']] = .2
    slice_modifier[slice_names['Resolution']] = 3
    observations = {}
    for label, point in (('valid_physical_zero', (0, 2, 2)),
                         ('masked_grid_point', (1, 0, 0)), ('outside_grid', (-2, 0, 0))):
        slice_modifier[slice_names['Center']] = point
        sample = min(evaluated_samples(sliced), key=lambda row: sum((a - b) ** 2 for a, b in zip(row[0], point)))
        assert sum((a - b) ** 2 for a, b in zip(sample[0], point)) < 1e-8
        observations[label] = {'value': sample[1], 'valid': sample[2], 'fraction': sample[3]}
    assert observations['valid_physical_zero']['valid']
    assert abs(observations['valid_physical_zero']['value']) < 1e-5
    assert not observations['masked_grid_point']['valid']
    assert abs(observations['masked_grid_point']['value'] - 1) < 1e-5
    assert not observations['outside_grid']['valid']
    report['checks']['evaluated_GN_mask_and_outside_distinct_from_zero'] = 'Passed'
    report['GN_samples'] = observations
    assert base.hashes() == before_arrays
    report['checks']['copied_dataset_arrays_unchanged'] = 'Passed'
    report['status'] = 'Passed'
    (out / 'edges.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    check_edges(args.out)
