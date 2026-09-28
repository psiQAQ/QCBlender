"""Installed C07 chart checks. Run prepare, then reopen saved and moved blends separately.

blender --background --factory-startup --python tools/verify_multiwfn_charts.py -- \
  --mode prepare --fixture outputs/multiwfn-parameters/01-foundation-r5/final-sop/cases/C07/C07.blend \
  --out outputs/multiwfn-parameters/03-charts
blender --background --factory-startup --python tools/verify_multiwfn_charts.py -- \
  --mode reopen --fixture outputs/multiwfn-parameters/03-charts/evidence.blend \
  --out outputs/multiwfn-parameters/03-charts
Repeat reopen with --fixture "<out>/moved 中文 path/evidence.blend".
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qc_evidence', ROOT / 'tools/verify_vmd_parameters.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
module = evidence.module


def record(report, name, action):
    try:
        detail = action()
    except Exception as error:
        report['checks'][name] = 'Failed'
        report.setdefault('errors', {})[name] = repr(error)
        raise
    report['checks'][name] = 'Passed'
    report.setdefault('details', {})[name] = detail
    return detail


def field_view():
    matches = [obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'field'
               and json.loads(obj['qc_field']).get('quantity') == 'delta_g']
    assert matches, 'C07 has no real delta_g field view'
    field = matches[0]
    module('blender.source_browser').refresh_source(field)
    module('blender.source_browser').bound_field(field)
    return field


def run_contours(charts, obj, *, levels='', cancel=False, expected='succeeded'):
    source, plane, identity = charts._state(obj)
    job = module('blender.jobs').Job(
        'contours', dataset=bpy.path.abspath(source['qc_dataset']),
        dataset_sha256=source['qc_dataset_sha256'], field=json.loads(source['qc_field']),
        plane=plane, levels=levels, mapping_range=plane.get('mapping_range'), identity=identity)
    request = json.loads((job.directory / 'request.json').read_text(encoding='utf-8'))
    assert request['action'] == 'contours' and request['identity'] == identity
    if cancel:
        assert job.process.poll() is None, 'Contour worker finished before cancellation'
        job.cancel()
        assert job.process.poll() is not None and (job.directory / 'cancel').exists()
        return {'cancelled_job': job.directory.name}
    deadline = time.monotonic() + 300
    try:
        while time.monotonic() < deadline:
            result = job.poll()
            if result is not None:
                break
            time.sleep(.1)
        else:
            raise TimeoutError('Contour worker did not finish in five minutes')
    finally:
        if job.process.poll() is None:
            job.cancel()
    assert result['status'] == expected, result
    if expected == 'succeeded':
        assert result.get('identity') == identity
    else:
        assert 'error' in result
    return {'job': job.directory.name, 'source': source, 'plane': plane,
            'identity': identity, 'request': request, 'report': result}


def attach_contours(charts, obj, result):
    source, plane, identity = charts._state(obj)
    assert source == result['source'] and identity == result['identity']
    assert result['report']['identity'] == identity
    digest = hashlib.sha256((Path(bpy.path.abspath(source['qc_dataset'])) / 'manifest.json').read_bytes()).hexdigest()
    assert digest == source['qc_dataset_sha256']
    carrier = charts._draw_contours(obj, source, plane, result['report'])
    obj['qc_contour_child'] = carrier.name
    obj['qc_contour_identity'] = identity
    assert carrier.parent == obj and carrier['qc_contour_identity'] == identity
    return carrier


def check_contours(source_field, out):
    charts = module('blender.charts')
    module('blender.layers').activate(bpy.context, source_field)
    assert bpy.ops.qcblender.create_slice() == {'FINISHED'}
    sliced = bpy.context.object
    sliced.name = 'QC charts C07 slice'
    assert not sliced.get('qc_contour_enabled', False)
    assert bpy.ops.qcblender.toggle_contours() == {'FINISHED'}
    assert sliced['qc_contour_source'] == 'COLOR'
    sliced['qc_contour_labels'] = True
    child_count = len(bpy.data.objects)

    source, plane, identity = charts._state(sliced)
    assert plane['mapping_range'] is not None
    bad = module('blender.jobs').Job(
        'contours', dataset=bpy.path.abspath(source['qc_dataset']),
        dataset_sha256='0' * 64, field=json.loads(source['qc_field']), plane=plane,
        levels='', mapping_range=plane['mapping_range'], identity=identity)
    deadline = time.monotonic() + 300
    try:
        while time.monotonic() < deadline:
            failure = bad.poll()
            if failure is not None:
                break
            time.sleep(.1)
        else:
            raise TimeoutError('Invalid contour worker did not finish')
    finally:
        if bad.process.poll() is None:
            bad.cancel()
    assert failure['status'] == 'failed' and 'changed' in failure.get('error', '').lower(), failure
    assert len(bpy.data.objects) == child_count and charts._carrier(sliced) is None
    cancelled = run_contours(charts, sliced, cancel=True)
    assert len(bpy.data.objects) == child_count and charts._carrier(sliced) is None

    original_binding = sliced['qc_color_source']
    altered = json.loads(original_binding)
    altered['field']['array'] = 'wrong_source_array'
    sliced['qc_color_source'] = json.dumps(altered)
    try:
        try:
            charts._state(sliced)
        except ValueError:
            pass
        else:
            raise AssertionError('Contour accepted a changed bound color field')
    finally:
        sliced['qc_color_source'] = original_binding
    assert charts._state(sliced)[2] == identity

    valid = run_contours(charts, sliced)
    bounds = valid['request']['mapping_range']
    expected = np.linspace(bounds['minimum'], bounds['maximum'], 11)[1:-1]
    np.testing.assert_allclose(valid['report']['levels'], expected, rtol=0, atol=1e-9)
    assert valid['report']['sample_count'] == 101**2
    assert valid['report']['valid_count'] > 0
    assert any(path['lines'] for path in valid['report']['paths']), 'Real C07 plane has no contour lines'
    carrier = attach_contours(charts, sliced, valid)
    labels = [obj for obj in carrier.children if obj.get('qc_contour_label')]
    assert labels and all(label.parent == carrier for label in labels)

    duplicate = module('blender.layers').copy_layer(sliced, bpy.context.collection)
    duplicate.name = 'QC charts C07 slice copy'
    assert charts._carrier(duplicate) is None and 'qc_contour_identity' not in duplicate
    original_material, original_ramp = charts._mapped_material(sliced)
    copied_material, copied_ramp = charts._mapped_material(duplicate)
    assert copied_material != original_material
    original_colors = [tuple(item.color) for item in original_ramp.color_ramp.elements]
    module('blender.layers').activate(bpy.context, duplicate)
    assert bpy.ops.qcblender.color_palette(palette='BCY') == {'FINISHED'}
    assert [tuple(item.color) for item in original_ramp.color_ramp.elements] == original_colors
    assert copied_material.get('qc_palette') == 'BCY'
    assert [tuple(item.color) for item in copied_ramp.color_ramp.elements] != original_colors
    copied_result = run_contours(charts, duplicate)
    copied_carrier = attach_contours(charts, duplicate, copied_result)
    copied_labels = [obj for obj in copied_carrier.children if obj.get('qc_contour_label')]
    assert copied_labels and copied_carrier.data != carrier.data
    assert all(label.data not in [source_label.data for source_label in labels] for label in copied_labels)
    doomed = {obj.name for obj in (copied_carrier, *copied_labels)}
    doomed_curves = {obj.data.name for obj in (copied_carrier, *copied_labels)}
    contour_material = copied_carrier.data.materials[0].name
    assert bpy.ops.qcblender.layer_action(target=duplicate.name, action='REMOVE') == {'FINISHED'}
    assert all(name not in bpy.data.objects for name in doomed)
    assert all(name not in bpy.data.curves for name in doomed_curves)
    assert contour_material not in bpy.data.materials
    assert carrier.name in bpy.data.objects and all(label.name in bpy.data.objects for label in labels)
    return {'slice': sliced.name, 'carrier': carrier.name, 'labels': len(labels),
            'levels': valid['report']['levels'], 'mapping_range': bounds,
            'valid_samples': valid['report']['valid_count'], 'cancel': cancelled}


def valid_profile_points(volume, field, data):
    valid = data.arrays[field['valid_mask']]
    cells = valid[:-1, :-1, :-1].copy()
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                cells &= valid[i:i+cells.shape[0], j:j+cells.shape[1], k:k+cells.shape[2]]
    candidates = np.argwhere(cells)
    assert len(candidates), 'C07 has no fully valid interpolation cell'
    middle = np.asarray(cells.shape) / 2
    base = candidates[np.argmin(np.sum((candidates - middle)**2, axis=1))]
    origin, steps = np.asarray(field['origin']), np.asarray(field['steps'])
    points = [origin + (base + offset) @ steps for offset in ((.2, .3, .4), (.8, .7, .6))]
    return [volume.matrix_world @ Vector(point) for point in points]


def check_profile(source_field, out):
    browser = module('blender.source_browser')
    volume, field, _, _ = browser.bound_field(source_field)
    data = module('data').load_dataset(bpy.path.abspath(volume['qc_dataset']))
    start, end = valid_profile_points(volume, field, data)
    module('blender.layers').activate(bpy.context, source_field)
    bpy.context.scene.cursor.location = start
    assert bpy.ops.qcblender.mark_profile_start() == {'FINISHED'}
    bpy.context.scene.cursor.location = end
    assert bpy.ops.qcblender.create_line_profile(field_role='GEOMETRY', samples=101) == {'FINISHED'}
    profile = bpy.context.object
    profile.name = 'QC charts C07 profile'
    dataset = module('data').load_dataset(bpy.path.abspath(profile['qc_dataset']))
    assert dataset.arrays['profile_values'].shape == (101,)
    assert int(dataset.arrays['profile_valid'].sum()) == 101
    assert json.loads(profile['qc_chart'])['sample_count'] == 101
    first = out / 'profile-before.csv'
    second = out / 'profile-after.csv'
    assert bpy.ops.qcblender.export_line_profile('EXEC_DEFAULT', filepath=str(first)) == {'FINISHED'}
    values = dataset.arrays['profile_values'].copy()
    profile['qc_profile_width'] = 6.
    profile['qc_profile_height'] = 4.
    profile['qc_profile_y_auto'] = False
    profile['qc_profile_y_min'] = float(values.min()) - 1.
    profile['qc_profile_y_max'] = float(values.max()) + 1.
    profile['qc_profile_precision'] = 3
    assert bpy.ops.qcblender.apply_profile_axes() == {'FINISHED'}
    assert bpy.ops.qcblender.export_line_profile('EXEC_DEFAULT', filepath=str(second)) == {'FINISHED'}
    assert first.read_bytes() == second.read_bytes(), 'Profile layout changed exported scientific CSV'
    refreshed = module('data').load_dataset(bpy.path.abspath(profile['qc_dataset']))
    np.testing.assert_array_equal(refreshed.arrays['profile_values'], values)
    ticks = [child for child in profile.children if child.get('qc_profile_tick')]
    assert ticks and profile.data.materials[0] is not None

    copied = module('blender.layers').copy_layer(profile, bpy.context.collection)
    copied.name = 'QC charts C07 profile copy'
    copied_ticks = [child for child in copied.children if child.get('qc_profile_tick')]
    assert len(copied_ticks) == len(ticks) and copied.data.materials[0] != profile.data.materials[0]
    original_texts = {child.data.as_pointer() for child in ticks}
    assert all(child.data.as_pointer() not in original_texts
               and child.data.materials[0] == copied.data.materials[0] for child in copied_ticks)
    doomed = {child.name for child in copied_ticks}
    doomed_curves = {child.data.name for child in copied_ticks}
    assert bpy.ops.qcblender.layer_action(target=copied.name, action='REMOVE') == {'FINISHED'}
    assert all(name not in bpy.data.objects for name in doomed)
    assert all(name not in bpy.data.curves for name in doomed_curves)
    assert all(child.name in bpy.data.objects for child in ticks)
    return {'profile': profile.name, 'sample_count': 101, 'ticks': len(ticks),
            'csv_sha256': hashlib.sha256(first.read_bytes()).hexdigest()}


def unchanged_source_arrays(original, current):
    assert all(current.get(key) == value for key, value in original.items()), 'C07 source arrays changed'
    return len(original)


def save_and_verify(out, report):
    evidence.save_evidence(out, report)
    assert evidence.hashes() == report['arrays']
    return {'blend': str(out / 'evidence.blend'), 'arrays': len(report['arrays'])}


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    report = {'checks': {name: 'Not Run' for name in (
        'real_c07_binding', 'contour_worker_error_cancel_identity_copy_remove_palette',
        'profile_101_csv_layout_copy_remove', 'scientific_arrays_unchanged',
        'portable_save', 'cold_open', 'moved_cold_open', 'gui_modal_and_watcher')},
        'status': 'Not Run'}
    try:
        field_name = record(report, 'real_c07_binding', lambda: field_view().name)
        field = bpy.data.objects[field_name]
        original = evidence.hashes()
        contour = record(report, 'contour_worker_error_cancel_identity_copy_remove_palette',
                         lambda: check_contours(field, out))
        profile = record(report, 'profile_101_csv_layout_copy_remove', lambda: check_profile(field, out))
        after = evidence.hashes()
        record(report, 'scientific_arrays_unchanged', lambda: unchanged_source_arrays(original, after))
        report['charts'] = {'contour': contour, 'profile': profile}
        record(report, 'portable_save', lambda: save_and_verify(out, report))
    except Exception as error:
        report['status'] = 'Failed'
        report['error'] = repr(error)
        raise
    finally:
        (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report['checks']


def reopen(out):
    report = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
    moved = 'moved 中文 path' in Path(bpy.data.filepath).parts
    key = 'moved_cold_open' if moved else 'cold_open'
    try:
        assert evidence.hashes() == report['arrays'], 'Scientific arrays changed after cold reopen'
        contour = report['charts']['contour']
        sliced = bpy.data.objects[contour['slice']]
        carrier = bpy.data.objects[contour['carrier']]
        assert carrier.parent == sliced and carrier['qc_contour_identity'] == sliced['qc_contour_identity']
        assert sum(bool(child.get('qc_contour_label')) for child in carrier.children) == contour['labels']
        profile_record = report['charts']['profile']
        profile = bpy.data.objects[profile_record['profile']]
        assert sum(bool(child.get('qc_profile_tick')) for child in profile.children) == profile_record['ticks']
        data = module('data').load_dataset(bpy.path.abspath(profile['qc_dataset']))
        assert len(data.arrays['profile_values']) == 101
        csv = out / ('profile-moved.csv' if moved else 'profile-reopen.csv')
        module('profile').export_profile_csv(data, csv)
        assert hashlib.sha256(csv.read_bytes()).hexdigest() == profile_record['csv_sha256']
        for obj in (sliced, profile):
            assert Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(Path(bpy.data.filepath).parent)
        report['checks'][key] = 'Passed'
        report['status'] = ('Passed' if report['checks']['cold_open'] == report['checks']['moved_cold_open'] == 'Passed'
                            else 'Not Run')
    except Exception as error:
        report['checks'][key] = 'Failed'
        report['status'] = 'Failed'
        report.setdefault('errors', {})[key] = repr(error)
        raise
    finally:
        (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return {key: report['checks'][key], 'status': report['status']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('prepare', 'reopen'), required=True)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    out = args.out.resolve()
    assert out.is_relative_to((ROOT / 'outputs').resolve()), 'Use an output directory inside the repository'
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to((ROOT / 'outputs').resolve())
    assert bpy.ops.preferences.addon_enable(module=evidence.MODULE) == {'FINISHED'}
    installed = Path(module('blender.charts').__file__).resolve()
    assert 'extensions' in installed.parts and installed != ROOT / 'qcblender/blender/charts.py'
    assert bpy.ops.wm.open_mainfile(filepath=str(args.fixture.resolve(strict=True))) == {'FINISHED'}
    result = prepare(out) if args.mode == 'prepare' else reopen(out)
    print(json.dumps(result, ensure_ascii=False))
