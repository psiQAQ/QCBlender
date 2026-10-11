"""Exercise real Blender RNA selector assignments against small metadata fixtures."""
import argparse
import importlib
import json
from pathlib import Path
import sys
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--module', default='qcblender')
parser.add_argument('--quit', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
sys.path.insert(0, str(ROOT))
package = importlib.import_module(args.module)
report = {'status': 'Failed', 'blender': bpy.app.version_string, 'checks': [],
          'scope': 'Real RNA with synthetic metadata; no scientific computation claimed'}


def module(name):
    return importlib.import_module(args.module + '.blender.' + name)


def check(name, function):
    try:
        function()
    except Exception:
        report['checks'].append({'name': name, 'status': 'Failed', 'error': traceback.format_exc()})
    else:
        report['checks'].append({'name': name, 'status': 'Passed'})


def probe(source_class, values, expected, after=None):
    def execute(self, context):
        for name, value in expected.items():
            assert getattr(self, name) == value, (name, getattr(self, name), value)
        if after:
            after(self, context)
        return {'FINISHED'}
    cls = type('QCBOUNDS_OT_probe', (bpy.types.Operator,), {
        'bl_idname': 'qcbounds.probe', 'bl_label': 'RNA bounds probe',
        '__annotations__': dict(source_class.__annotations__), 'execute': execute})
    bpy.utils.register_class(cls)
    try:
        assert bpy.ops.qcbounds.probe(**values) == {'FINISHED'}
    finally:
        bpy.utils.unregister_class(cls)


def run_checks():
    browser = module('source_browser')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_cube_add()
    source = bpy.context.object
    source['qc_view_kind'] = 'atoms'
    source['qc_optimization_count'] = 3
    source['qc_trajectory_count'] = 2
    browser._metadata[browser.binding_key(source)] = {
        '_atom_count': 8, 'orbitals': {'kind': 'unrestricted', 'norba': 4, 'norbb': 2}}
    ui = module('ui')

    def beta(self, context):
        self.spin = 'beta'
        assert self.orbital == 2, self.orbital
        self.orbital = -10
        assert self.orbital == 1, self.orbital
    check('orbital upper/lower and spin switch', lambda: probe(ui.QCBLENDER_OT_generate,
        {'spin': 'alpha', 'orbital': 999}, {'orbital': 4}, beta))
    check('optimization step upper', lambda: probe(module('optimization').QCBLENDER_OT_optimization_step,
        {'step': 999}, {'step': 3}))
    check('XYZ frame upper', lambda: probe(module('trajectory').QCBLENDER_OT_trajectory_frame,
        {'frame': 999}, {'frame': 2}))
    check('distance atom upper', lambda: probe(module('atomic_properties').QCBLENDER_OT_distance,
        {'first': 999, 'second': 0}, {'first': 8, 'second': 1}))

    small = bpy.data.objects.new('Three source atoms', bpy.data.meshes.new('Three source atoms'))
    bpy.context.collection.objects.link(small)
    small['qc_view_kind'] = 'atoms'
    browser._metadata[browser.binding_key(small)] = {'_atom_count': 3}
    # Distinct bindings prevent fixture metadata from leaking between objects.
    source['qc_dataset_sha256'] = 'eight-atoms'
    small['qc_dataset_sha256'] = 'three-atoms'
    browser._metadata[browser.binding_key(source)] = {
        '_atom_count': 8, 'orbitals': {'kind': 'unrestricted', 'norba': 4, 'norbb': 2}}
    browser._metadata[browser.binding_key(small)] = {'_atom_count': 3}

    def smaller(self, context):
        self.configuration = small.name
        assert (self.atom_1, self.atom_2, self.atom_3) == (3, 3, 3)
    check('plane atom range follows configuration', lambda: probe(module('interaction').QCBLENDER_OT_define_plane,
        {'configuration': source.name, 'atom_1': 999, 'atom_2': 999, 'atom_3': 999},
        {'atom_1': 8, 'atom_2': 8, 'atom_3': 8}, smaller))

    def collections():
        settings = source.qc_settings
        for _ in range(3):
            settings.modes.add()
        for _ in range(2):
            settings.energies.add()
        settings.active_mode = 999
        settings.active_energy = 999
        assert settings.active_mode == 2 and settings.active_energy == 1
        settings.modes.clear()
        settings.energies.clear()
        assert settings.active_mode == 0 and settings.active_energy == 0
    check('mode and energy indexes follow collection size', collections)

    def sparse_pairs():
        browser._metadata[browser.binding_key(source)]['analysis'] = {'pairs': [
            {'pair': 1, 'spin': 'Alpha'}, {'pair': 4, 'spin': 'Alpha'}, {'pair': 2, 'spin': 'Beta'}]}
        nocv = module('nocv')
        def switch(self, context):
            assert self.pair_choice == '4'
            self.spin = 'Beta'
            assert self.pair_number == 2 and self.pair_choice == '2'
            self.spin = 'Alpha'
            self.pair_choice = '4'
            assert self.pair_number == 4
            self.pair_number = 3
            assert self.pair_number == 4
        probe(nocv.QCBLENDER_OT_import_nocv, {'spin': 'Alpha', 'pair_number': 999}, {'pair_number': 4}, switch)
    check('sparse NOCV pairs retain original identity across spin changes', sparse_pairs)

    def nbo_jobs():
        summary = json.dumps({'jobs': [{'nbo_blocks': 3}, {'nbo_blocks': 1}, {'nbo_blocks': 0}]})
        def other_job(self, context):
            self.job_number = 2
            self.block_number = 999
            assert self.block_number == 1
            self.job_number = 999
            assert self.job_number == 3
            assert module('nbo').block_bounds(self, context)[1] == 0
        probe(module('nbo').QCBLENDER_OT_import_nbo,
              {'filepath': 'fixture.log', 'summary': summary, 'job_number': 1, 'block_number': 999},
              {'job_number': 1, 'block_number': 3}, other_job)
    check('NBO job/block range follows inspected source', nbo_jobs)

    def result_rows():
        source['qc_view_kind'] = 'nbo'
        browser._metadata[browser.binding_key(source)]['analysis'] = {'kind': 'NBO',
            'orbitals': [{'number': 2, 'type': 'LP', 'occupancy': 2.},
                         {'number': 7, 'type': 'BD', 'occupancy': 1.8},
                         {'number': 9, 'type': 'BD', 'occupancy': 1.7}],
            'interactions': [{'donor': 2, 'acceptor': 7, 'e2_kcal_mol': 3.}]}
        state = source.qc_result_browser
        state.row_index = 999
        assert state.row_index == 3, state.row_index
        state.orbital_type = 'LP'
        assert state.row_index == 1, state.row_index
        state.orbital_type = 'RY'
        state.donor = 99
        assert module('result_browser').match_count(state) == 0
        assert state.row_index == 1
    check('result row range follows filtered matches without renumbering sources', result_rows)

    def custom_rows():
        source['qc_view_kind'] = 'nbo'
        source['qc_nbo_index'], source['qc_e2_index'] = 999, -5
        module('record_ranges').refresh_record_ranges(source, browser.cached_metadata(source))
        assert (source['qc_nbo_index'], source['qc_e2_index']) == (3, 1)
        limits = source.id_properties_ui('qc_nbo_index').as_dict()
        assert limits['min'] == 1 and limits['max'] == 3
    check('custom row ID property limits and stale value normalization', custom_rows)

    def view_sockets():
        from mathutils import Vector
        source['qc_view_kind'] = 'atoms'
        metadata = browser.cached_metadata(source)
        source['qc_dataset'] = 'fixture-dataset'
        browser._metadata[browser.binding_key(source)] = metadata
        source.data.clear_geometry()
        source.data.from_pydata([Vector((0, 0, 0))] * 8, [], [])
        views = module('views')
        tree = bpy.data.node_groups.new('Bound ranges', 'GeometryNodeTree')
        tree['qc_view_kind'] = 'atoms'
        for name, value in [('First Atom (1-based)', 1), ('Last Atom (0 = all)', 0),
                            ('Style (0 ball-stick, 1 space-fill, 2 bonds)', 0)]:
            views.socket(tree, name, 'NodeSocketInt', default=value)
        modifier = source.modifiers.new('QC', 'NODES')
        modifier.node_group = tree
        module('graph').tag_view(tree)
        module('record_ranges').refresh_record_ranges(source, browser.cached_metadata(source))
        limits = {item.name: (item.min_value, item.max_value) for item in tree.interface.items_tree
                  if item.item_type == 'SOCKET'}
        assert limits['First Atom (1-based)'] == (1, 8), limits
        assert limits['Last Atom (0 = all)'] == (0, 8), limits
        assert limits['Style (0 ball-stick, 1 space-fill, 2 bonds)'] == (0, 2), limits
    check('per-view geometry socket ranges retain Last Atom zero sentinel', view_sockets)


def run():
    try:
        if args.module == 'qcblender':
            package.register()
        else:
            bpy.ops.preferences.addon_enable(module=args.module)
        report['module_path'] = package.__file__
        run_checks()
        report['status'] = 'Failed' if any(c['status'] == 'Failed' for c in report['checks']) else 'Passed'
    except Exception:
        report['error'] = traceback.format_exc()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'checks': len(report['checks']), 'report': str(args.report)}))
    if args.quit:
        bpy.ops.wm.quit_blender()
    if report['status'] != 'Passed' and bpy.app.background:
        raise AssertionError('UI index regression failed; inspect ' + str(args.report))


if bpy.app.background:
    run()
else:
    bpy.app.timers.register(run, first_interval=1)
