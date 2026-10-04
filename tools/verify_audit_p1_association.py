"""Verify current geometry association through an installed Blender candidate."""
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
REFERENCE_ROOT = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
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


def run_job(action, **arguments):
    job = module('blender.jobs').Job(action, **arguments)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        receipt = job.poll()
        if receipt is not None:
            require(receipt['status'] == 'succeeded', str(receipt))
            return job.directory / 'dataset'
        time.sleep(.05)
    job.cancel()
    raise TimeoutError(str(job.directory))


def atoms(directory, name):
    obj = module('blender.views').atom_view(directory)
    obj.name = name
    return obj


def associate(reference, moving, rigid=False):
    activate(reference)
    moving.select_set(True)
    return bpy.ops.qcblender.associate_sources(allow_rigid=rigid)


def reject(call, text=None):
    try:
        outcome = call()
    except (ValueError, RuntimeError) as error:
        if text:
            require(text.lower() in str(error).lower(), str(error))
        return str(error)
    require(outcome == {'CANCELLED'}, 'Expected rejection, got ' + str(outcome))
    return 'CANCELLED'


def state(obj):
    bpy.context.view_layer.update()
    reference = obj.qc_settings.association_reference
    return {'matrix': np.asarray(obj.matrix_world).tolist(),
            'positions': [list(vertex.co) for vertex in obj.data.vertices] if obj.type == 'MESH' else None,
            'equilibrium': [list(value.vector) for value in obj.data.attributes['qc_equilibrium_position'].data]
                if obj.type == 'MESH' and obj.data.attributes.get('qc_equilibrium_position') else None,
            'steps': {key: obj.get(key) for key in ('qc_irc_step', 'qc_optimization_step', 'qc_trajectory_frame',
                                                   'qc_irc_record', 'qc_optimization_record')},
            'association': obj.get('qc_association'), 'reference': reference.name if reference else None,
            'annotations': {child.name: child.get('qc_annotation') for child in obj.children
                            if 'qc_annotation' in child}}


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if not obj.get('qc_dataset'):
            continue
        data = module('data').load_dataset(bpy.path.abspath(obj['qc_dataset']))
        entry = {'manifest': obj['qc_dataset_sha256'], 'state': state(obj),
                 'arrays': {key: hashlib.sha256(value.tobytes()).hexdigest()
                            for key, value in sorted(data.arrays.items())}}
        if obj.get('qc_view_kind') == 'atoms':
            positions, record = module('blender.geometry').current_geometry(obj, data)
            require(not positions.flags.writeable, 'Current scientific geometry is writable')
            entry['geometry'] = record
            entry['geometry_sha256'] = hashlib.sha256(positions.tobytes()).hexdigest()
        result[obj.name] = entry
    return result


def new_irc(name):
    require(bpy.ops.qcblender.import_irc_path(
        manifest_path=str(REFERENCE_ROOT / 'tests/data/tutorial/P04/steps.csv')) == {'FINISHED'}, 'IRC import')
    obj = bpy.context.object
    obj.name = name
    return obj


def set_step(obj, number):
    activate(obj)
    if obj.get('qc_irc'):
        while obj['qc_irc_step'] != number:
            direction = 'NEXT' if obj['qc_irc_step'] < number else 'PREV'
            outcome = bpy.ops.qcblender.irc_step(direction=direction)
            if outcome != {'FINISHED'}:
                return outcome
        return {'FINISHED'}
    return bpy.ops.qcblender.optimization_step(direction='GOTO', step=number)


def dynamic_checks(dynamic, static, last, report):
    association = module('blender.association')
    key = 'irc' if dynamic.get('qc_irc') else 'optimization'
    require(associate(static, dynamic) == {'FINISHED'}, key + ' initial association')
    association.require_current_association(dynamic, static)
    require(set_step(dynamic, last) == {'FINISHED'}, key + ' last step')
    require(json.loads(dynamic['qc_association'])['status'] == 'stale', key + ' moving step invalidation')
    before = state(static), state(dynamic)
    error = reject(lambda: associate(static, dynamic), 'Different geometries')
    require(before == (state(static), state(dynamic)), key + ' failed association changed scene')
    require(set_step(dynamic, 1) == {'FINISHED'}, key + ' first step')
    reject(lambda: association.require_current_association(dynamic, static), 'again')
    require(associate(dynamic, static) == {'FINISHED'}, key + ' reference initial association')
    same = dynamic.copy()
    same.data = dynamic.data.copy()
    bpy.context.collection.objects.link(same)
    same.name = key + ' same source other view'
    same.qc_settings.association_reference = None
    if 'qc_association' in same:
        del same['qc_association']
    reject(lambda: association.require_current_association(static, same), 'again')
    require(set_step(same, last) == {'FINISHED'}, key + ' other view step')
    association.require_current_association(static, dynamic)
    require(set_step(dynamic, last) == {'FINISHED'}, key + ' reference step')
    require(json.loads(static['qc_association'])['status'] == 'stale', key + ' reference step invalidation')
    reject(lambda: associate(dynamic, static), 'Different geometries')
    require(associate(dynamic, same) == {'FINISHED'}, key + ' matching current steps')
    record = association.require_current_association(same, dynamic)
    require(record['reference_geometry']['step'] == last == record['moving_geometry']['step'], key + ' step provenance')
    dynamic.name = key + ' renamed reference'
    association.require_current_association(same, dynamic)
    if key == 'optimization':
        require(set_step(dynamic, last) == {'FINISHED'}, 'Same-step optimization request')
        association.require_current_association(same, dynamic)
    copied = module('blender.layers').copy_layer(same, bpy.context.collection)
    require('qc_association' not in copied and copied.qc_settings.association_reference is None,
            key + ' plugin copy inherited association')
    require(np.allclose(copied.matrix_world, same.matrix_world), key + ' plugin copy moved')
    report[key] = {'different_step_rejection': error, 'both_roles': 'Passed', 'current_steps': last,
                   'same_source_other_view': 'Passed', 'rename': 'Passed', 'copy_layer_helper': 'Passed'}
    return same


def lifecycle_checks(dynamic, static, report):
    association = module('blender.association')
    require(set_step(dynamic, 1) == {'FINISHED'}, 'Prepare lifecycle reference')
    require(associate(dynamic, static) == {'FINISHED'}, 'Prepare incoming association')
    saved = static['qc_association']
    positions, next_geometry = module('geometry').scientific_geometry(
        module('data').load_dataset(bpy.path.abspath(dynamic['qc_dataset'])), 'irc', 2)
    next_geometry['dataset_sha256'] = dynamic['qc_dataset_sha256']
    before = state(dynamic), state(static)
    prepared = association.prepare_association_invalidation(dynamic, next_geometry)
    require(before == (state(dynamic), state(static)) and prepared, 'Preparation mutated the scene')
    static['qc_association'] = '{'
    before = state(dynamic), state(static)
    reject(lambda: set_step(dynamic, 2), 'damaged')
    require(before == (state(dynamic), state(static)), 'Malformed incoming association changed step')
    static['qc_association'] = saved
    unrelated = bpy.data.objects.new('Unrelated damaged record', None)
    bpy.context.collection.objects.link(unrelated)
    unrelated['qc_association'] = '{'
    require(set_step(dynamic, 2) == {'FINISHED'}, 'Unrelated damaged record blocked step')
    bpy.data.objects.remove(unrelated, do_unlink=True)
    require(set_step(dynamic, 1) == {'FINISHED'}, 'Return lifecycle reference')
    require(associate(dynamic, static) == {'FINISHED'}, 'Rebuild association')
    legacy = json.loads(static['qc_association'])
    for key in ('version', 'reference_geometry', 'moving_geometry'):
        legacy.pop(key)
    static['qc_association'] = json.dumps(legacy)
    reject(lambda: association.require_current_association(static, dynamic), 'again')
    require(association.association_summary(static)['status'] == 'unverified', 'Legacy record appears verified')
    require(associate(dynamic, static) == {'FINISHED'}, 'Rebuild legacy association')
    disposable = dynamic.copy()
    disposable.data = dynamic.data.copy()
    bpy.context.collection.objects.link(disposable)
    require(associate(disposable, static) == {'FINISHED'}, 'Prepare deleted reference')
    bpy.data.objects.remove(disposable, do_unlink=True)
    require(static.qc_settings.association_reference is None, 'Deleted reference pointer survived')
    reject(lambda: association.require_current_association(static, dynamic), 'again')
    require(associate(dynamic, static) == {'FINISHED'}, 'Restore reference after deletion')
    report['lifecycle'] = {'two_phase_preparation': 'Passed', 'damaged_incoming_no_mutation': 'Passed',
                           'unrelated_damaged_record': 'Passed', 'legacy': 'Passed', 'reference_delete': 'Passed'}


def binding_checks(static, directory, report):
    invalid = atoms(directory, 'Binding rejection fixture')
    atom_id = invalid.data.attributes['qc_atom_id'].data[0]
    atom_id.value = 99
    before = state(static), state(invalid)
    reject(lambda: associate(static, invalid), 'identities')
    require(before == (state(static), state(invalid)), 'Invalid atom identity changed the scene')
    atom_id.value = 0
    digest = invalid['qc_dataset_sha256']
    invalid['qc_dataset_sha256'] = '0' * 64
    before = state(static), state(invalid)
    reject(lambda: associate(static, invalid), 'manifest')
    require(before == (state(static), state(invalid)), 'Invalid binding changed the scene')
    invalid['qc_dataset_sha256'] = digest
    job = invalid['qc_source_job']
    invalid['qc_source_job'] = 99
    before = state(static), state(invalid)
    reject(lambda: associate(static, invalid), 'identity')
    require(before == (state(static), state(invalid)), 'Invalid selected job changed the scene')
    invalid['qc_source_job'] = job
    report['binding_rejections'] = {'atom_identity': 'Passed', 'manifest': 'Passed', 'selected_job': 'Passed'}


def consumer_checks(static, dynamic, static_directory, out, report):
    data = module('data').load_dataset(static_directory)
    xyz = out / 'p04-current-geometry.xyz'
    symbols = {1: 'H', 8: 'O'}
    xyz.write_text(str(len(data.arrays['atomic_numbers'])) + '\nP04 source geometry in angstrom\n' +
                   '\n'.join(symbols[int(z)] + ' ' + ' '.join(format(float(x), '.16g') for x in position)
                             for z, position in zip(data.arrays['atomic_numbers'], data.arrays['positions'])) + '\n',
                   encoding='utf-8')
    xyz_atoms = atoms(run_job('import', source=str(xyz)), 'P04 independent XYZ source')
    field_directory = run_job('evaluate', dataset=str(static_directory),
        grid={'origin': [-3., -3., -3.], 'steps': [[.6, 0, 0], [0, .6, 0], [0, 0, .6]], 'shape': [11] * 3},
        parameters={'quantity': 'electron_number_density', 'memory_mb': 512})
    field = module('blender.views').field_view(field_directory, static)
    field.name = 'P04 density consumer field'
    require(field['qc_dataset_sha256'] != static['qc_dataset_sha256'], 'Field did not create a derived dataset')
    association, scalars = module('blender.association'), module('blender.scalars')
    empty = bpy.data.objects.new('Non-scientific field parent', None)
    bpy.context.collection.objects.link(empty)
    for parent in (None, empty):
        field.parent = parent
        scalars.compare_color_sources(xyz_atoms, field)
        scalars.compare_color_sources(field, field)
    field.parent = static
    bpy.data.objects.remove(empty, do_unlink=True)
    require(set_step(dynamic, 2) == {'FINISHED'}, 'Field parent configuration boundary')
    field.parent = dynamic
    reject(lambda: scalars.compare_color_sources(xyz_atoms, field), 'configuration')
    field.parent = static
    require(associate(xyz_atoms, static) == {'FINISHED'}, 'Color association')
    scalars.compare_color_sources(xyz_atoms, field)
    scalars.compare_color_sources(static, field)
    activate(xyz_atoms)
    require(bpy.ops.qcblender.select_color_field(source_name=field.name) == {'FINISHED'}, 'Color field operator')
    other = atoms(bpy.path.abspath(xyz_atoms['qc_dataset']), 'Same XYZ different reference')
    scalars.compare_color_sources(other, field)
    shifted_xyz = out / 'p04-translated-geometry.xyz'
    shifted_xyz.write_text(str(len(data.arrays['atomic_numbers'])) + '\nP04 geometry translated in angstrom\n' +
        '\n'.join(symbols[int(z)] + ' ' + ' '.join(format(float(x), '.16g') for x in position + [2., -1., .5])
                  for z, position in zip(data.arrays['atomic_numbers'], data.arrays['positions'])) + '\n', encoding='utf-8')
    shifted = atoms(run_job('import', source=str(shifted_xyz)), 'P04 translated reference')
    before = state(shifted), state(static)
    reject(lambda: associate(shifted, static), 'Different geometries')
    require(before == (state(shifted), state(static)), 'Failed rigid-disabled association changed scene')
    require(associate(shifted, static, rigid=True) == {'FINISHED'}, 'Explicit rigid association')
    scalars.compare_color_sources(shifted, field)
    shifted_other = atoms(bpy.path.abspath(shifted['qc_dataset']), 'Same translated source different reference')
    reject(lambda: scalars.compare_color_sources(shifted_other, field), 'Different geometries')
    require(associate(xyz_atoms, static) == {'FINISHED'}, 'Restore color reference')
    saved = static['qc_association']
    for alteration in ('legacy', 'stale', 'malformed'):
        record = json.loads(saved)
        if alteration == 'legacy':
            record.pop('version')
        elif alteration == 'stale':
            record['status'] = 'stale'
        static['qc_association'] = '{' if alteration == 'malformed' else json.dumps(record)
        before = state(xyz_atoms), state(static)
        activate(xyz_atoms)
        reject(lambda: bpy.ops.qcblender.select_color_field(source_name=field.name))
        require(before == (state(xyz_atoms), state(static)), 'Rejected color mapping changed geometry')
    static['qc_association'] = saved
    require(set_step(dynamic, 1) == {'FINISHED'}, 'Current color target preparation')
    require(associate(dynamic, static) == {'FINISHED'}, 'Dynamic color reference')
    scalars.compare_color_sources(dynamic, field)
    require(set_step(dynamic, 2) == {'FINISHED'}, 'Dynamic color target change')
    reject(lambda: scalars.compare_color_sources(dynamic, field))
    del static['qc_association']
    static.qc_settings.association_reference = None
    reject(lambda: scalars.compare_color_sources(dynamic, field), 'Different geometries')
    require(set_step(dynamic, 1) == {'FINISHED'}, 'Prepare slice configuration')
    require(associate(static, dynamic) == {'FINISHED'}, 'Slice association')
    activate(field)
    require(bpy.ops.qcblender.create_slice(resolution=11) == {'FINISHED'}, 'Create slice')
    sliced = bpy.context.object
    sliced.name = 'P04 associated atom slice'
    require(bpy.ops.qcblender.define_slice_plane(mode='atoms', configuration=dynamic.name,
                                               atom_1=1, atom_2=2, atom_3=3) == {'FINISHED'}, 'Atom slice')
    require(set_step(dynamic, 2) == {'FINISHED'}, 'Invalidate slice association')
    require(set_step(dynamic, 1) == {'FINISHED'}, 'Return does not restore slice association')
    activate(sliced)
    before = state(sliced), sliced.get('qc_plane_definition')
    reject(lambda: bpy.ops.qcblender.define_slice_plane(mode='atoms', configuration=dynamic.name,
                                                      atom_1=1, atom_2=2, atom_3=3), 'again')
    require(before == (state(sliced), sliced.get('qc_plane_definition')), 'Rejected slice changed definition')
    require(associate(static, dynamic) == {'FINISHED'}, 'Restore slice for record boundaries')
    saved_dynamic = dynamic['qc_association']
    for alteration in ('legacy', 'malformed'):
        record = json.loads(saved_dynamic)
        if alteration == 'legacy':
            record.pop('version')
        dynamic['qc_association'] = '{' if alteration == 'malformed' else json.dumps(record)
        activate(sliced)
        reject(lambda: bpy.ops.qcblender.define_slice_plane(mode='atoms', configuration=dynamic.name,
                                                          atom_1=1, atom_2=2, atom_3=3), 'again')
        require(before == (state(sliced), sliced.get('qc_plane_definition')), 'Invalid record changed slice')
    dynamic['qc_association'] = saved_dynamic
    require(set_step(dynamic, 2) == {'FINISHED'}, 'Keep a stale association for cold reopen')
    require(set_step(dynamic, 1) == {'FINISHED'}, 'Restore geometry without restoring association')
    require(associate(static, xyz_atoms) == {'FINISHED'}, 'Create valid saved association')
    activate(xyz_atoms)
    require(bpy.ops.qcblender.new_current_view() == {'FINISHED'}, 'Create current version view')
    current = bpy.context.object
    require('qc_association' not in current and current.qc_settings.association_reference is None,
            'Current version view inherited association')
    report['consumers'] = {'derived_field_parent': 'Passed', 'unparented_and_empty_parent_exact_comparison': 'Passed',
                           'color_operator': 'Passed', 'same_hash_wrong_view_cannot_authorize_rigid': 'Passed',
                           'own_field_and_unrelated_association_exact_comparison': 'Passed', 'rigid_operator': 'Passed',
                           'legacy_stale_malformed_color': 'Passed', 'dynamic_color_target': 'Passed',
                           'field_parent_configuration': 'Passed', 'slice_operator': 'Passed',
                           'stale_legacy_malformed_slice_no_mutation': 'Passed', 'new_current_view': 'Passed'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--reopen', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'status': 'Running', 'blender': bpy.app.version_string, 'pid': os.getpid(),
              'independent_human_review': 'Not Run', 'checks': {}}
    bpy.ops.preferences.addon_enable(module=MODULE)
    try:
        if args.reopen:
            bpy.ops.wm.open_mainfile(filepath=str(args.reopen.resolve()))
            original = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
            require(snapshot() == original['saved_snapshot'], 'Cold reopen changed scientific or association state')
            verified, stale = 0, 0
            for obj in bpy.context.scene.objects:
                if obj.get('qc_dataset'):
                    require(Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(
                        args.reopen.resolve().with_suffix('.qcdata')), 'Dataset outside portable project')
                if obj.get('qc_association'):
                    if json.loads(obj['qc_association'])['status'] == 'geometry_matched':
                        module('blender.association').require_current_association(obj, obj.qc_settings.association_reference)
                        verified += 1
                    else:
                        reject(lambda: module('blender.association').require_current_association(
                            obj, obj.qc_settings.association_reference))
                        stale += 1
            require(verified > 0 and stale > 0, 'Saved scene must cover valid and stale associations')
            report['checks']['cold_reopen'] = {'status': 'Passed', 'verified': verified, 'stale': stale}
        else:
            for obj in list(bpy.data.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            static_directory = run_job('import', source=str(REFERENCE_ROOT / 'tests/data/tutorial/P04/step-001.fchk'))
            static = atoms(static_directory, 'P04 static source')
            binding_checks(static, static_directory, report['checks'])
            dynamic = new_irc('P04 dynamic path')
            dynamic_checks(dynamic, static, 3, report['checks'])
            optimization_source = atoms(run_job('import', source=str(input_path(
                'log-examples/water_neutral_nbo_opt_freq.out', REFERENCE_ROOT)), job_index=0), 'P02 optimized source')
            activate(optimization_source)
            require(bpy.ops.qcblender.optimization_view() == {'FINISHED'}, 'Optimization view')
            optimization = bpy.context.object
            optimization.name = 'P02 dynamic optimization'
            initial = atoms(bpy.path.abspath(optimization['qc_dataset']), 'P02 static first step')
            dynamic_checks(optimization, initial, 4, report['checks'])
            lifecycle_checks(dynamic, static, report['checks'])
            consumer_checks(static, dynamic, static_directory, out, report['checks'])
            activate(static)
            module('blender.project').save_project(out / 'p1-association.blend')
            report['saved_snapshot'] = snapshot()
            report['source_inputs'] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in
                (REFERENCE_ROOT / 'tests/data/tutorial/P04/step-001.fchk',
                 input_path('log-examples/water_neutral_nbo_opt_freq.out', REFERENCE_ROOT))}
        report['status'] = 'Passed'
    except Exception as error:
        report.update(status='Failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        (out / ('cold-reopen.json' if args.reopen else 'checks.json')).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
