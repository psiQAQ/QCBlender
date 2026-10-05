"""Installed-extension cancellation probe; ESC is dispatched by script, not a human click."""
import argparse
from functools import partial
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
import uuid

import bpy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--reference-root', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve() / uuid.uuid4().hex
OUT.mkdir(parents=True)
REF = args.reference_root.resolve()
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
module = lambda name: importlib.import_module(MODULE + '.' + name)
jobs, ui, storage, external, exports = map(module,
    ('blender.jobs', 'blender.ui', 'data', 'external_fields', 'data_export'))
if jobs._active or ui._operations:
    raise RuntimeError('Run the probe only when this extension has no existing jobs or modal operations')
report = {'status': 'Failed', 'blender': bpy.app.version_string,
          'module': MODULE, 'checks': {}, 'gui': 'Not Run',
          'boundary': 'Real workers and native timers; scripted ESC and controlled process fault injection'}
owned = []


def new_job(action, **parameters):
    job = jobs.Job(action, **parameters)
    owned.append(job)
    return job


def operator(job):
    operation = ui.AsyncOperation()
    operation._job = job
    operation.messages = []
    operation.report = lambda levels, text: operation.messages.append(text)
    operation._timer = bpy.context.window_manager.event_timer_add(.25, window=bpy.context.window)
    ui._operations[id(operation)] = (operation, bpy.context.window_manager)
    return operation


def await_exit(job, timeout=60):
    deadline = time.monotonic() + timeout
    while job.process.poll() is None:
        if time.monotonic() >= deadline:
            raise TimeoutError(f'Worker did not exit: PID {job.process.pid}, {job.directory}')
        time.sleep(.05)


def cancelled(operation, event='ESC'):
    assert operation.modal(bpy.context, SimpleNamespace(type=event)) == {'CANCELLED'}
    result = operation._job.cancellation
    assert id(operation) not in ui._operations
    return dict(result, messages=list(operation.messages))


class ProcessFault:
    """Inject only child-process control responses; preserve the real Popen for recovery."""
    def __init__(self, process, fault):
        self.actual = process
        self.pid = process.pid
        self.fault = fault

    def poll(self):
        return None

    def terminate(self):
        if self.fault == 'terminate':
            raise OSError('controlled terminate failure')

    def wait(self, timeout):
        raise subprocess.TimeoutExpired('controlled child exit wait', timeout)


try:
    ordinary = new_job('diagnose')
    ordinary_result = cancelled(operator(ordinary))
    assert ordinary_result['status'] == 'exited', ordinary_result
    assert not ordinary_result['errors'], ordinary_result
    assert ordinary not in jobs._active
    report['checks']['real_worker_scripted_escape'] = ordinary_result

    # P03 is a real, redistributed Multiwfn pair; no fabricated exporter fixture.
    pair = input_path('public-tutorial/P03/igmh', REF)
    data = external.pair_cubes(pair / 'dg_inter.cub', pair / 'sl2r.cub',
                               'IGMH', 'electron/bohr^4', 'electron/bohr^3')
    seed = OUT / 'paired-dataset'
    storage.save_dataset(data, seed)
    output = OUT / 'csv'
    token = uuid.uuid4().hex
    manifest_sha = hashlib.sha256((seed / 'manifest.json').read_bytes()).hexdigest()
    exporting = new_job('export_data', dataset=str(seed), dataset_sha256=manifest_sha,
                        output_directory=str(output), kind='paired', scope='ALL',
                        filters={}, export_token=token)
    exporting.cleanup_after_exit = partial(exports.cleanup_staging, output, token)
    staging = output / ('.qc-export-' + token)
    deadline = time.monotonic() + 120
    while not staging.exists():
        if exporting.process.poll() is not None:
            raise RuntimeError('Export finished before cancellation could observe its real staging directory')
        if time.monotonic() >= deadline:
            raise TimeoutError('Real CSV exporter did not reach staging')
        time.sleep(.005)
    export_result = cancelled(operator(exporting))
    assert export_result['status'] == 'exited', export_result
    assert not export_result['errors'], export_result
    assert not staging.exists()
    assert not list(output.glob('*-paired-' + token))
    report['checks']['real_export_staging_escape'] = export_result

    for fault in ('terminate', 'wait'):
        bad = new_job('diagnose')
        actual = bad.process
        bad.process = ProcessFault(actual, fault)
        good = new_job('diagnose')
        first, second = operator(bad), operator(good)
        results = ui.cancel_operations()
        assert bad.cancellation['status'] == 'exit_unconfirmed'
        assert bad in jobs._active
        assert good.cancellation['status'] == 'exited'
        assert not ui._operations
        assert any(fault in text for text in first.messages), first.messages
        report['checks']['controlled_' + fault] = {
            'boundary': 'Injected process control responses, real worker ownership',
            'reports': results, 'messages': first.messages}
        bad.process = actual
        await_exit(bad)
        retry = bad.cancel()
        assert retry['status'] == 'exited' and bad not in jobs._active, retry

    failed = new_job('import', source=str(OUT / 'missing.fchk'), job_index=0)
    await_exit(failed)
    original = json.loads((failed.directory / 'result.json').read_text(encoding='utf-8'))
    assert original['status'] == 'failed', original
    def cleanup_fault():
        raise OSError('controlled staging cleanup failure')
    failed.cleanup_after_exit = cleanup_fault
    failed_result = cancelled(operator(failed), 'TIMER')
    assert any(original['error'] in text for text in failed_result['messages']), failed_result
    assert any('controlled staging cleanup failure' in text for text in failed_result['messages'])
    failed.cleanup_after_exit = None
    failed.cancel()
    report['checks']['real_task_error_with_controlled_cleanup_error'] = failed_result
    assert not jobs._active and not ui._operations
    report['status'] = 'Passed'
finally:
    # Restore actual child handles before finalizing only jobs created by this probe.
    for job in owned:
        if isinstance(job.process, ProcessFault):
            job.process = job.process.actual
        if job in jobs._active:
            job.cancel()
    report['remaining_jobs'] = [{'pid': job.process.pid, 'directory': str(job.directory)}
                                for job in owned if job in jobs._active]
    (OUT / 'cancel-finalization.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'report': str(OUT / 'cancel-finalization.json'), 'status': report['status']}))
