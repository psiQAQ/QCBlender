"""Real cancellation paths with controlled process and bpy boundaries."""
import gc
import importlib.util
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_modules():
    bpy = types.ModuleType('bpy')
    bpy.types = types.SimpleNamespace(Operator=type('Operator', (), {}),
                                    AddonPreferences=type('AddonPreferences', (), {}),
                                    Panel=type('Panel', (), {}))
    props = types.ModuleType('bpy.props')
    for name in ('EnumProperty', 'FloatProperty', 'IntProperty', 'StringProperty'):
        setattr(props, name, lambda **kwargs: None)
    extras = types.ModuleType('bpy_extras.io_utils')
    extras.ImportHelper = type('ImportHelper', (), {})
    modules = {}
    with patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': props,
                                  'bpy_extras.io_utils': extras}):
        for name in ('jobs', 'ui', 'data_export'):
            fullname = 'qcblender.blender.' + name
            spec = importlib.util.spec_from_file_location(fullname, ROOT / 'qcblender/blender' / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[name] = module
            if name == 'ui':
                with patch.dict(sys.modules, {fullname: module}):
                    export_spec = importlib.util.spec_from_file_location('qcblender.blender.data_export',
                                                                       ROOT / 'qcblender/blender/data_export.py')
                    export = importlib.util.module_from_spec(export_spec)
                    export_spec.loader.exec_module(export)
                    modules['data_export'] = export
                    paired_spec = importlib.util.spec_from_file_location('qcblender.blender.external_fields',
                                                                       ROOT / 'qcblender/blender/external_fields.py')
                    paired = importlib.util.module_from_spec(paired_spec)
                    paired_spec.loader.exec_module(paired)
                    modules['external_fields'] = paired
                break
    return modules


MODULES = load_modules()
jobs, ui, exports = (MODULES[name] for name in ('jobs', 'ui', 'data_export'))


class Process:
    pid = 12345

    def __init__(self, terminate_error=None, wait_error=None, poll_error=None):
        self.code = None
        self.terminate_error = terminate_error
        self.wait_error = wait_error
        self.poll_error = poll_error
        self.terminated = False

    def poll(self):
        if self.poll_error:
            raise self.poll_error
        return self.code

    def terminate(self):
        self.terminated = True
        if self.terminate_error:
            raise self.terminate_error

    def wait(self, timeout):
        if self.wait_error:
            raise self.wait_error
        self.code = -15
        return self.code


class Manager:
    def __init__(self):
        self.removed = []

    def event_timer_remove(self, timer):
        self.removed.append(timer)


class Cancellation(unittest.TestCase):
    def setUp(self):
        self.directory = ROOT / 'outputs/tests/cancel-finalization' / self.id().rsplit('.', 1)[-1]
        self.directory.mkdir(parents=True, exist_ok=True)
        jobs._active.clear()
        ui._operations.clear()

    def tearDown(self):
        jobs._active.clear()
        ui._operations.clear()
        for path in self.directory.iterdir():
            path.unlink()
        self.directory.rmdir()

    def job(self, process=None):
        job = jobs.Job.__new__(jobs.Job)
        job.directory = self.directory
        job.process = process or Process()
        job.cleanup_after_exit = None
        jobs._active.add(job)
        return job

    def operator(self, job, export=False):
        cls = exports.QCBLENDER_OT_export_data if export else ui.AsyncOperation
        operator = cls()
        operator._job = job
        operator._timer = object()
        operator.messages = []
        operator.report = lambda levels, message: operator.messages.append(message)
        manager = Manager()
        context = types.SimpleNamespace(window_manager=manager, area=None)
        ui._operations[id(operator)] = (operator, manager)
        return operator, context

    def test_terminate_failure_is_explicit_and_retains_job(self):
        job = self.job(Process(terminate_error=OSError('denied terminate')))
        report = job.cancel()
        self.assertEqual(report['status'], 'exit_unconfirmed')
        self.assertTrue(report['cancel_requested'])
        self.assertIn('denied terminate', '\n'.join(report['errors']))
        self.assertEqual(report['pid'], 12345)
        self.assertIn(job, jobs._active)

    def test_timeout_retains_job_and_staging_until_retry_confirms_exit(self):
        job = self.job(Process(wait_error=subprocess.TimeoutExpired('worker', 10)))
        staging = self.directory / 'staging'
        staging.write_text('preserve', encoding='utf-8')
        job.cleanup_after_exit = staging.unlink
        report = job.cancel()
        self.assertEqual(report['status'], 'exit_unconfirmed')
        self.assertTrue(staging.exists())
        job.process.wait_error = None
        self.assertEqual(job.cancel()['status'], 'exited')
        self.assertFalse(staging.exists())
        self.assertNotIn(job, jobs._active)

    def test_unconfirmed_job_survives_operator_release(self):
        job = self.job(Process(wait_error=subprocess.TimeoutExpired('worker', 10)))
        identifier = id(job)
        job.cancel()
        del job
        gc.collect()
        self.assertIn(identifier, [id(item) for item in jobs._active])

    def test_exit_after_terminate_error_is_confirmed_but_error_remains(self):
        class Exited(Process):
            def terminate(self):
                self.code = 0
                raise OSError('already stopped')
        job = self.job(Exited())
        report = job.cancel()
        self.assertEqual(report['status'], 'exited')
        self.assertIn('already stopped', '\n'.join(report['errors']))
        self.assertNotIn(job, jobs._active)

    def test_cleanup_failure_stays_traceable_and_can_be_retried(self):
        job = self.job()
        def denied():
            raise OSError('staging is locked')
        job.cleanup_after_exit = denied
        report = job.cancel()
        self.assertEqual(report['status'], 'exited')
        self.assertIn('staging is locked', '\n'.join(report['errors']))
        self.assertIn(job, jobs._active)
        with self.assertRaises(RuntimeError):
            job.poll()
        self.assertIn(job, jobs._active)
        job.cleanup_after_exit = lambda: None
        job.cancel()
        self.assertNotIn(job, jobs._active)

    def test_modal_original_error_and_cancel_error_are_both_reported(self):
        job = self.job()
        job.process.code = 1
        def denied():
            raise OSError('staging is locked')
        job.cleanup_after_exit = denied
        operator, context = self.operator(job)
        self.assertEqual(operator.modal(context, types.SimpleNamespace(type='TIMER')), {'CANCELLED'})
        self.assertIn('Worker exited with 1', '\n'.join(operator.messages))
        self.assertIn('staging is locked', '\n'.join(operator.messages))
        self.assertEqual(context.window_manager.removed, [operator._timer])
        self.assertNotIn(id(operator), ui._operations)

    def test_poll_error_is_preserved_when_termination_also_fails(self):
        class Unavailable(Process):
            def poll(self):
                if self.poll_error:
                    error, self.poll_error = self.poll_error, None
                    raise error
                return self.code
        job = self.job(Unavailable(terminate_error=OSError('denied terminate'),
                                  poll_error=OSError('original process status failure')))
        operator, context = self.operator(job)
        self.assertEqual(operator.modal(context, types.SimpleNamespace(type='TIMER')), {'CANCELLED'})
        self.assertIn('original process status failure', '\n'.join(operator.messages))
        self.assertIn('denied terminate', '\n'.join(operator.messages))

    def test_scientific_failure_report_and_cleanup_error_both_survive(self):
        import json
        job = self.job()
        job.process.code = 0
        (job.directory / 'result.json').write_text(json.dumps({
            'schema': 1, 'job_id': job.directory.name, 'status': 'failed',
            'error': 'original scientific failure'}), encoding='utf-8')
        def denied():
            raise OSError('staging is locked')
        job.cleanup_after_exit = denied
        operator, context = self.operator(job)
        self.assertEqual(operator.modal(context, types.SimpleNamespace(type='TIMER')), {'CANCELLED'})
        self.assertIn('original scientific failure', '\n'.join(operator.messages))
        self.assertIn('staging is locked', '\n'.join(operator.messages))

    def test_poll_failure_preserves_staging_and_job(self):
        job = self.job(Process(poll_error=OSError('cannot query child')))
        calls = []
        job.cleanup_after_exit = lambda: calls.append('cleanup')
        report = job.cancel()
        self.assertEqual(report['status'], 'exit_unconfirmed')
        self.assertIn('cannot query child', '\n'.join(report['errors']))
        self.assertEqual(calls, [])
        self.assertIn(job, jobs._active)

    def test_already_exited_child_does_not_receive_terminate(self):
        job = self.job()
        job.process.code = 0
        self.assertEqual(job.cancel()['status'], 'exited')
        self.assertFalse(job.process.terminated)

    def test_escape_returns_cancelled_with_unconfirmed_exit_report(self):
        job = self.job(Process(wait_error=subprocess.TimeoutExpired('worker', 10)))
        operator, context = self.operator(job)
        self.assertEqual(operator.modal(context, types.SimpleNamespace(type='ESC')), {'CANCELLED'})
        self.assertIn('exit_unconfirmed', '\n'.join(operator.messages))
        self.assertIn(job, jobs._active)
        self.assertEqual(context.window_manager.removed, [operator._timer])

    def test_unstarted_dialog_cancel_keeps_other_job_running(self):
        job = self.job()
        operator = ui.QCBLENDER_OT_generate()
        messages = []
        operator.report = lambda levels, message: messages.append(message)
        self.assertIsNone(operator.cancel(None))
        self.assertEqual(messages, [])
        self.assertFalse(job.process.terminated)
        self.assertIn(job, jobs._active)

    def test_existing_job_cancellation_error_is_not_swallowed(self):
        job = self.job()
        operator, context = self.operator(job)
        with patch.object(job, 'cancel', side_effect=RuntimeError('Controlled job cancellation failure')):
            with self.assertRaisesRegex(RuntimeError, 'Controlled job cancellation failure'):
                operator.cancel(context)
        self.assertEqual(context.window_manager.removed, [operator._timer])
        self.assertNotIn(id(operator), ui._operations)
        self.assertIn(job, jobs._active)

    def test_cancel_all_attempts_every_owned_job(self):
        bad = self.job(Process(terminate_error=OSError('denied terminate')))
        good = self.job()
        reports = jobs.cancel_all()
        self.assertTrue(good.process.terminated)
        self.assertIn(bad, jobs._active)
        self.assertNotIn(good, jobs._active)
        self.assertEqual(len(reports), 2)

    def test_cancel_operations_attempts_every_task_and_removes_timers(self):
        bad = self.job(Process(terminate_error=OSError('denied terminate')))
        good = self.job()
        first, first_context = self.operator(bad)
        second, second_context = self.operator(good)
        ui.cancel_operations()
        self.assertTrue(good.process.terminated)
        self.assertEqual(first_context.window_manager.removed, [first._timer])
        self.assertEqual(second_context.window_manager.removed, [second._timer])
        self.assertFalse(ui._operations)

    def test_unexpected_finalizer_error_does_not_interrupt_other_operations(self):
        bad = self.job(Process())
        good = self.job()
        first, first_context = self.operator(bad)
        second, second_context = self.operator(good)
        def broken(context):
            raise RuntimeError('controlled operator failure')
        first.cancel = broken
        reports = ui.cancel_operations()
        self.assertIn('controlled operator failure', '\n'.join(reports[0]['errors']))
        self.assertTrue(good.process.terminated)
        self.assertEqual(first_context.window_manager.removed, [first._timer])
        self.assertEqual(second_context.window_manager.removed, [second._timer])
        self.assertIn(bad, jobs._active)

    def test_unexpected_job_error_does_not_interrupt_other_jobs(self):
        bad = self.job(Process())
        good = self.job()
        def broken():
            raise RuntimeError('controlled job finalizer failure')
        bad.cancel = broken
        reports = jobs.cancel_all()
        self.assertTrue(good.process.terminated)
        self.assertTrue(any('controlled job finalizer failure' in '\n'.join(r['errors']) for r in reports))
        self.assertIn(bad, jobs._active)

    def test_export_cancel_does_not_cleanup_before_exit_confirmation(self):
        job = self.job(Process(wait_error=subprocess.TimeoutExpired('worker', 10)))
        operator, context = self.operator(job, export=True)
        calls = []
        operator.cleanup_export = lambda: calls.append('cleanup')
        job.cleanup_after_exit = operator.cleanup_export
        operator.cancel(context)
        self.assertEqual(calls, [])
        self.assertEqual(context.window_manager.removed, [operator._timer])
        job.process.wait_error = None
        jobs.cancel_all()
        self.assertEqual(calls, ['cleanup'])

    def test_blender_import_cancel_callback_returns_none(self):
        for cls in (ui.QCBLENDER_OT_import, MODULES['external_fields'].QCBLENDER_OT_import_paired_field):
            with self.subTest(operator=cls.__name__):
                job = self.job()
                operation = cls()
                operation._job = job
                operation._timer = object()
                operation.report = lambda levels, text: None
                manager = Manager()
                ui._operations[id(operation)] = (operation, manager)
                self.assertIsNone(operation.cancel(types.SimpleNamespace(window_manager=manager)))
                self.assertEqual(job.cancellation['status'], 'exited')

    def test_blender_export_cancel_callback_returns_none(self):
        job = self.job()
        operation, context = self.operator(job, export=True)
        self.assertIsNone(operation.cancel(context))
        self.assertEqual(job.cancellation['status'], 'exited')


if __name__ == '__main__':
    unittest.main()
