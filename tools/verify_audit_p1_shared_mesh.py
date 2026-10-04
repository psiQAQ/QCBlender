"""Verify shared atom mesh guards with installed operators and portable projects."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)).resolve()
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path

MODULE = 'bl_ext.user_default.qcblender'


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def activate(obj):
    module('blender.layers').activate(bpy.context, obj)


def plain(value):
    if isinstance(value, bpy.types.ID):
        return {'id_type': value.bl_rna.identifier, 'name': value.name}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, 'items'):
        return {key: plain(item) for key, item in value.items()}
    return [plain(item) for item in value]


def custom(owner):
    return {key: plain(value) for key, value in owner.items()}


def snapshot(roots):
    """Record scientific state and native data names, usable across processes."""
    bpy.context.view_layer.update()
    objects = set(roots)
    for root in roots:
        objects.update(root.children_recursive)
    result = {}
    for obj in sorted(objects, key=lambda item: item.name):
        data = obj.data
        record = {'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
                  'properties': custom(obj), 'matrix': plain(obj.matrix_world),
                  'visibility': [obj.hide_get(), obj.hide_viewport, obj.hide_render],
                  'data_name': data.name if data else None,
                  'data_users': data.users if data else None,
                  'modifiers': [{'name': mod.name, 'type': mod.type, 'properties': custom(mod),
                                 'node_group': mod.node_group.name if mod.type == 'NODES' and mod.node_group else None}
                                for mod in obj.modifiers]}
        if data is not None:
            record['data_properties'] = custom(data)
            record['materials'] = [{'name': mat.name, 'color': list(mat.diffuse_color)} if mat else None
                                   for mat in data.materials]
        if obj.type == 'MESH':
            record['vertices'] = [list(vertex.co) for vertex in data.vertices]
            record['edges'] = [list(edge.vertices) for edge in data.edges]
            record['polygons'] = [list(face.vertices) for face in data.polygons]
            record['attributes'] = {}
            for attr in data.attributes:
                values = []
                for item in attr.data:
                    field = next(name for name in ('value', 'vector', 'color') if hasattr(item, name))
                    values.append(plain(getattr(item, field)))
                record['attributes'][attr.name] = {'type': attr.data_type, 'domain': attr.domain, 'values': values}
        elif obj.type in ('FONT', 'CURVE'):
            record['splines'] = [[list(point.co) for point in spline.points] for spline in data.splines]
            record['bevel_depth'] = data.bevel_depth
            if obj.type == 'FONT':
                record.update(body=data.body, size=data.size)
        if obj.get('qc_dataset'):
            directory = Path(bpy.path.abspath(obj['qc_dataset']))
            dataset = module('data').load_dataset(directory)
            record['manifest_sha256'] = hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest()
            record['arrays'] = {key: hashlib.sha256(value.tobytes()).hexdigest()
                                for key, value in dataset.arrays.items()}
            reference = getattr(obj.qc_settings, 'association_reference', None)
            record['association_reference'] = reference.name if reference else None
        result[obj.name] = record
    return result


def require_geometry(owner):
    positions, record = module('blender.geometry').current_geometry(owner)
    np.testing.assert_allclose([vertex.co[:] for vertex in owner.data.vertices], positions, atol=2e-6, rtol=0)
    np.testing.assert_allclose([item.vector[:] for item in owner.data.attributes['qc_equilibrium_position'].data],
                               positions, atol=2e-6, rtol=0)
    for child in owner.children:
        if 'qc_annotation' not in child:
            continue
        entry = json.loads(child['qc_annotation'])
        require(entry['geometry'] == record, child.name + ': annotation geometry differs')
        points = positions[np.array(entry['source_atom_numbers']) - 1]
        anchor = points.mean(axis=0)
        value = float(np.linalg.norm(points[1] - points[0]))
        require(abs(entry['value'] - value) < 1e-10, child.name + ': distance differs')
        if entry['role'] == 'LABEL':
            np.testing.assert_allclose(child.location, anchor + entry['offset'], atol=2e-6, rtol=0)
            text = module('measurements').measurement_text('DISTANCE', entry['source_atom_numbers'], value,
                                                          record, entry['decimals'])
            require(child.data.body == text, child.name + ': visible distance differs')
        else:
            np.testing.assert_allclose(child.data.splines[0].points[0].co[:3], anchor, atol=2e-6, rtol=0)


def add_distance(owner):
    activate(owner)
    require(bpy.ops.qcblender.add_annotation(kind='DISTANCE', atoms='1,2') == {'FINISHED'}, 'Add distance failed')
    return next(child for child in owner.children if child.type == 'FONT' and child.get('qc_annotation'))


def linked(owner, name):
    activate(owner)
    require(bpy.ops.object.duplicate(linked=True) == {'FINISHED'}, 'Native linked duplicate failed')
    copied = bpy.context.object
    copied.name = name
    require(copied.data == owner.data and owner.data.users > 1, 'Duplicate must share atom mesh')
    add_distance(copied)
    return copied


def reject(roots, operation, fragment='independent atom mesh'):
    before = snapshot(roots)
    try:
        outcome = operation()
    except RuntimeError as error:
        require(fragment in str(error), 'Unexpected rejection: ' + str(error))
        message = str(error)
    else:
        require(outcome == {'CANCELLED'}, 'Operation unexpectedly succeeded: ' + str(outcome))
        message = 'CANCELLED'
    require(snapshot(roots) == before, 'Rejected operation changed scientific or native scene state')
    return message


def import_atoms(path, name):
    pending = module('blender.jobs').Job('import', source=str(path), job_index=0)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        receipt = pending.poll()
        if receipt is not None:
            require(receipt['status'] == 'succeeded', str(receipt))
            obj = module('blender.views').atom_view(pending.directory / 'dataset')
            obj.name = name
            return obj
        time.sleep(.05)
    pending.cancel()
    raise TimeoutError(str(pending.directory))


def navigation(kind, direction, step=3):
    if kind == 'irc':
        return bpy.ops.qcblender.irc_step(direction=direction)
    return bpy.ops.qcblender.optimization_step(direction=direction, step=step)


def verify_path(owner, kind):
    """Keep a rejected linked pair and an independently navigable copy."""
    activate(owner)
    require(navigation(kind, 'NEXT') == {'FINISHED'}, 'Initial navigation failed')
    original_label = add_distance(owner)
    copied = linked(owner, kind + ' independent copy')
    roots = [owner, copied]
    errors = {}
    for direction in (('NEXT', 'PREV') if kind == 'irc' else ('NEXT', 'PREV', 'GOTO')):
        activate(copied)
        errors[direction] = reject(roots, lambda: navigation(kind, direction))
    if kind == 'irc':
        activate(next(child for child in copied.children if child.get('qc_annotation')))
        errors['child_entry'] = reject(roots, lambda: navigation(kind, 'NEXT'))

    retained = linked(owner, kind + ' retained linked copy')
    roots.append(retained)
    activate(copied)
    require(bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True,
                                           material=False, animation=False) == {'FINISHED'}, 'Make single-user failed')
    require(copied.data != owner.data and copied.data.users == 1, 'Copied atom mesh is not independent')
    require(owner.data == retained.data and owner.data.users == 2, 'Retained pair lost its shared mesh')
    unchanged = snapshot([owner, retained])
    arrays = snapshot([copied])[copied.name]['arrays']
    for direction in (('NEXT', 'PREV') if kind == 'irc' else ('NEXT', 'PREV', 'GOTO')):
        require(navigation(kind, direction) == {'FINISHED'}, 'Independent navigation failed')
        require_geometry(copied)
        require(snapshot([owner, retained]) == unchanged, 'Independent navigation changed original pair')
        require(snapshot([copied])[copied.name]['arrays'] == arrays, 'Navigation changed Dataset arrays')

    label = next(child for child in copied.children if child.type == 'FONT' and child.get('qc_annotation'))
    if kind == 'irc':
        activate(label)
        for direction in ('NEXT', 'PREV'):
            require(navigation(kind, direction) == {'FINISHED'}, 'Independent child-entry navigation failed')
            require_geometry(copied)
            require(snapshot([owner, retained]) == unchanged, 'Child-entry navigation changed original pair')
        activate(copied)
    own_curve = label.data
    label.data = original_label.data
    errors['shared_annotation_data'] = reject(roots, lambda: navigation(kind, 'NEXT' if kind == 'irc' else 'PREV'),
                                              'independent FONT data')
    label.data = own_curve
    own_material = label.data.materials[0]
    label.data.materials[0] = original_label.data.materials[0]
    errors['shared_annotation_material'] = reject(roots, lambda: navigation(kind, 'NEXT' if kind == 'irc' else 'PREV'),
                                                  'material must be independent')
    label.data.materials[0] = own_material
    for obj in roots:
        require_geometry(obj)
    activate(retained)
    errors['retained_pair'] = reject(roots, lambda: navigation(kind, 'NEXT'))
    return roots, {'status': 'Passed', 'rejections': errors, 'independent_navigation': 'Passed',
                   'annotations': 'Passed', 'original_pair_unchanged': 'Passed'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--reopen', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=bool(args.reopen))
    report_path = out / ('cold-reopen.json' if args.reopen else 'checks.json')
    if report_path.exists():
        raise FileExistsError(report_path)
    report = {'status': 'Running', 'blender': bpy.app.version_string, 'pid': os.getpid(),
              'gui': 'Not Run', 'undo_redo': 'Not Run', 'independent_human_review': 'Not Run', 'checks': {}}
    bpy.ops.preferences.addon_enable(module=MODULE)
    try:
        if args.reopen:
            bpy.ops.wm.open_mainfile(filepath=str(args.reopen.resolve()))
            previous = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
            require(os.getpid() != previous['pid'], 'Cold reopen requires a new Blender process')
            roots = [bpy.data.objects[name] for name in previous['roots']]
            require(snapshot(roots) == previous['saved_snapshot'], 'Saved scientific/native state changed')
            for root in roots:
                require_geometry(root)
                if root.get('qc_dataset'):
                    directory = Path(bpy.path.abspath(root['qc_dataset'])).resolve()
                    require(directory.is_relative_to(args.reopen.resolve().with_suffix('.qcdata')),
                            'Dataset is outside the portable project')
            report['checks']['cold_reopen'] = 'Passed'
            report['project'] = str(args.reopen.resolve())
        else:
            installed = Path(importlib.import_module(MODULE).__file__).parent
            report['installed'] = {'path': str(installed), 'guards': {name: hashlib.sha256(
                (installed / 'blender' / (name + '.py')).read_bytes()).hexdigest() for name in ('irc', 'optimization')}}
            require(bpy.ops.qcblender.import_irc_path(manifest_path=str(
                REFERENCE / 'tests/data/tutorial/P04/steps.csv')) == {'FINISHED'}, 'Import real P04 failed')
            irc = bpy.context.object
            irc.name = 'IRC original'
            roots, report['checks']['irc'] = verify_path(irc, 'irc')
            source = import_atoms(input_path('log-examples/water_neutral_nbo_opt_freq.out', REFERENCE), 'P02 source')
            activate(source)
            require(bpy.ops.qcblender.optimization_view() == {'FINISHED'}, 'Create real P02 optimization failed')
            optimization = bpy.context.object
            optimization.name = 'Optimization original'
            opt_roots, report['checks']['optimization'] = verify_path(optimization, 'optimization')
            roots.extend([source, *opt_roots])
            activate(optimization)
            require(bpy.ops.qcblender.layer_action(target=optimization.name, action='DUPLICATE') == {'FINISHED'},
                    'Independent display-layer copy failed')
            copied = bpy.context.object
            unchanged = snapshot(opt_roots)
            require(navigation('optimization', 'GOTO', 4) == {'FINISHED'}, 'Copied optimization navigation failed')
            require_geometry(copied)
            require(snapshot(opt_roots) == unchanged, 'Display-layer copy changed original pair')
            roots.append(copied)
            report['checks']['optimization_layer_copy'] = 'Passed'
            xyz = import_atoms(REFERENCE / 'tests/data/xyz/p04-three-frames.xyz', 'XYZ original')
            module('blender.trajectory').initialize_trajectory(xyz, module('data').load_dataset(bpy.path.abspath(xyz['qc_dataset'])))
            add_distance(xyz)
            xyz_copy = linked(xyz, 'XYZ linked copy')
            message = reject([xyz, xyz_copy], lambda: bpy.ops.qcblender.trajectory_frame(direction='GOTO', frame=2))
            roots.extend([xyz, xyz_copy])
            report['checks']['xyz_control'] = {'status': 'Passed', 'rejection': message}
            for root in roots:
                require_geometry(root)
            target = out / 'shared-mesh.blend'
            require(bpy.ops.qcblender.save_project(filepath=str(target)) == {'FINISHED'}, 'Portable save failed')
            report['roots'] = [root.name for root in roots]
            report['saved_snapshot'] = snapshot(roots)
            report['project'] = str(target)
            report['checks']['portable_save'] = 'Passed'
        report['status'] = 'Passed'
    except Exception as error:
        report.update(status='Failed', error=repr(error))
        raise
    finally:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({key: value for key, value in report.items() if key != 'saved_snapshot'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
