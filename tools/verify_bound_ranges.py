"""Verify installed per-view limits on real saved datasets and shared bindings."""
import argparse
import importlib
import json
from pathlib import Path
import sys
import time
import traceback

import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--saved', type=Path, required=True)
parser.add_argument('--nbo-source', type=Path)
parser.add_argument('--reopen', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
MODULE = 'bl_ext.user_default.qcblender'
report = json.loads(args.report.read_text(encoding='utf-8')) if args.reopen else {
    'status': 'Failed', 'checks': [], 'blender': bpy.app.version_string, 'cold_open': 'Not Run'}


def module(name):
    return importlib.import_module(MODULE + '.blender.' + name)


def run_job(job, expected='succeeded'):
    deadline = time.monotonic() + 60
    while job.process.poll() is None:
        if time.monotonic() > deadline:
            job.cancel()
            raise TimeoutError(str(job.directory))
        time.sleep(.1)
    # Job owns all worker cleanup even when a deliberately invalid source fails.
    try:
        result = job.poll()
    except RuntimeError:
        if expected != 'failed':
            raise
        result = json.loads((job.directory / 'result.json').read_text(encoding='utf-8'))
    assert result['status'] == expected, result
    return result


def assert_limits(obj, count):
    modifier = module('graph').view_modifier(obj)
    inputs = {item.name: item for item in modifier.node_group.interface.items_tree
              if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    for name, bounds in [('First Atom (1-based)', (1, count)), ('Last Atom (0 = all)', (0, count)),
                         ('Style (0 ball-stick, 1 space-fill, 2 bonds)', (0, 2))]:
        assert (inputs[name].min_value, inputs[name].max_value) == bounds, name
    assert module('source_browser').cached_metadata(obj)['_atom_count'] == count
    return modifier, inputs


try:
    bpy.ops.preferences.addon_enable(module=MODULE)
    module('source_browser').refresh_loaded_sources()
    report['module_path'] = importlib.import_module(MODULE).__file__
    atoms = [obj for obj in bpy.data.objects if obj.get('qc_view_kind') == 'atoms']
    if args.reopen:
        for obj in atoms:
            modifier, inputs = assert_limits(obj, len(obj.data.vertices))
            assert modifier[inputs['First Atom (1-based)'].identifier] == len(obj.data.vertices)
            assert modifier[inputs['Last Atom (0 = all)'].identifier] == 0
        assert len(atoms) == 2
        assert module('graph').view_modifier(atoms[0]).node_group != module('graph').view_modifier(atoms[1]).node_group
        report['cold_open'] = 'Passed'
    else:
        assert len(atoms) == 1
        source = atoms[0]
        count = len(source.data.vertices)
        modifier, inputs = assert_limits(source, count)
        copy = source.copy()
        bpy.context.collection.objects.link(copy)
        copy.name = 'QC shared-binding range check'
        inputs['First Atom (1-based)'].max_value = 2147483647
        modifier[inputs['First Atom (1-based)'].identifier] = 999
        module('graph').view_modifier(copy)[inputs['First Atom (1-based)'].identifier] = 999
        module('source_browser').refresh_loaded_sources()
        for obj in (source, copy):
            current, sockets = assert_limits(obj, count)
            assert current[sockets['First Atom (1-based)'].identifier] == count
            assert current[sockets['Last Atom (0 = all)'].identifier] == 0
        assert module('graph').view_modifier(source).node_group != module('graph').view_modifier(copy).node_group
        report['checks'].append({'name': 'each shared binding gets private limits and stale values normalize', 'status': 'Passed'})
        if args.nbo_source:
            jobs = module('jobs')
            preview = run_job(jobs.Job('inspect_source', source=str(args.nbo_source), include_nbo=True))
            blocks = [job['nbo_blocks'] for job in preview['jobs']]
            assert blocks == [2, 1], blocks
            rejected = jobs.Job('import_nbo', source=str(args.nbo_source), job_index=1, block_index=0,
                                reference_dataset=bpy.path.abspath(source['qc_dataset']),
                                reference_sha256=source['qc_dataset_sha256'], source_sha256='0' * 64)
            failure = run_job(rejected, expected='failed')
            assert 'Gaussian source changed after job/block selection' in str(failure), failure
            report['checks'].append({'name': 'real NBO inspection and changed-source refusal', 'status': 'Passed',
                                     'blocks_per_job': blocks, 'preview_job': str(rejected.directory.parent / preview['job_id']),
                                     'refused_job': str(rejected.directory)})
        module('project').save_project(args.saved)
        report['saved'] = str(args.saved)
        report['status'] = 'Passed'
except Exception:
    report['status'] = 'Failed'
    report['error'] = traceback.format_exc()
args.report.parent.mkdir(parents=True, exist_ok=True)
args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': report['status'], 'cold_open': report['cold_open'], 'report': str(args.report)}))
if report['status'] != 'Passed':
    raise AssertionError('Bound ranges failed; inspect ' + str(args.report))
