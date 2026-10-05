"""UI qualification handoff and binding boundaries with controlled Blender calls."""
import types
from contextlib import nullcontext
import hashlib
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import Mock, patch

from test_cancel_finalization import ui, ROOT


class Timers:
    def __init__(self):
        self.callbacks = []

    def register(self, callback, **kwargs):
        self.callbacks.append(callback)

    def unregister(self, callback):
        self.callbacks.remove(callback)

    def is_registered(self, callback):
        return callback in self.callbacks

    def tick(self):
        for callback in list(self.callbacks):
            if callback() is None:
                self.callbacks.remove(callback)


class QualificationHandoff(unittest.TestCase):
    def setUp(self):
        self.source = types.SimpleNamespace(name='source')
        region = object()
        area = types.SimpleNamespace(regions=[region])
        window = types.SimpleNamespace(screen=types.SimpleNamespace(areas=[area]))
        self.context = types.SimpleNamespace(object=self.source, window=window, area=area, region=region,
            window_manager=types.SimpleNamespace(windows=[window], popup_menu=Mock()))
        self.context.temp_override = Mock(side_effect=lambda **kwargs: nullcontext())
        self.binding = (self.source, 'dataset', 'manifest-sha', 'science-sha')
        self.preview = {'lightweight': True}
        self.report = {'eligible': True, 'reason': None, 'preview': self.preview,
                       'dataset_sha256': 'manifest-sha', 'science_sha256': 'science-sha'}
        ui.clear_qualifications()
        self.addCleanup(ui.clear_qualifications)
        self.ops = types.SimpleNamespace(generate_field=Mock(return_value={'RUNNING_MODAL'}),
                                         qualify_science=Mock(return_value={'RUNNING_MODAL'}))
        self.timers = Timers()
        self.bpy = types.SimpleNamespace(data=types.SimpleNamespace(objects={'source': self.source}),
                                         ops=types.SimpleNamespace(qcblender=self.ops), context=self.context,
                                         app=types.SimpleNamespace(timers=self.timers))
        self.binding_patch = patch.object(ui, 'science_binding', return_value=self.binding)
        self.binding_mock = self.binding_patch.start()
        self.addCleanup(self.binding_patch.stop)
        self.bpy_patch = patch.object(ui, 'bpy', self.bpy)
        self.bpy_patch.start()
        self.addCleanup(self.bpy_patch.stop)
        self.addCleanup(ui.clear_qualifications)

    def operator(self):
        operator = ui.QCBLENDER_OT_qualify_science()
        operator._source, operator._dataset, operator._digest, operator._fingerprint = self.binding
        operator._handoff_context = {name: getattr(self.context, name) for name in ('window', 'area', 'region')}
        return operator

    def test_uncached_click_starts_only_qualification(self):
        generate = ui.QCBLENDER_OT_generate()
        generate.memory_mb = 512
        generate.report = Mock()
        self.assertEqual(generate.invoke(self.context, None), {'CANCELLED'})
        self.ops.qualify_science.assert_called_once_with('EXEC_DEFAULT', memory_mb=512)
        self.ops.generate_field.assert_not_called()

    def test_synchronous_qualification_cancel_does_not_finish_dispatcher(self):
        self.ops.qualify_science.return_value = {'CANCELLED'}
        self.context.window_manager = types.SimpleNamespace(invoke_props_dialog=Mock())
        generate = ui.QCBLENDER_OT_generate()
        generate.memory_mb = 512
        generate.report = Mock()
        self.assertEqual(generate.invoke(self.context, None), {'CANCELLED'})
        self.ops.qualify_science.assert_called_once_with('EXEC_DEFAULT', memory_mb=512)
        self.ops.generate_field.assert_not_called()
        self.context.window_manager.invoke_props_dialog.assert_not_called()
        self.assertFalse(ui._qualifications)

    def test_qualification_dispatch_error_is_preserved_and_cancelled(self):
        self.ops.qualify_science.side_effect = RuntimeError('Worker start failed: denied executable')
        self.context.window_manager = types.SimpleNamespace(invoke_props_dialog=Mock())
        generate = ui.QCBLENDER_OT_generate()
        generate.memory_mb = 512
        generate.report = Mock()
        self.assertEqual(generate.invoke(self.context, None), {'CANCELLED'})
        generate.report.assert_called_once_with({'ERROR'}, 'Worker start failed: denied executable')
        self.ops.generate_field.assert_not_called()
        self.context.window_manager.invoke_props_dialog.assert_not_called()
        self.assertFalse(ui._qualifications)

    def test_success_opens_separate_dialog_and_reuses_bound_preview(self):
        self.operator().accept(self.context, self.report)
        self.ops.generate_field.assert_not_called()
        self.timers.tick()
        self.ops.generate_field.assert_called_once_with('INVOKE_DEFAULT', True, memory_mb=512)
        self.context.temp_override.assert_called_once_with(
            window=self.context.window, area=self.context.area, region=self.context.region)
        generate = ui.QCBLENDER_OT_generate()
        self.context.window_manager = types.SimpleNamespace(invoke_props_dialog=Mock(return_value={'RUNNING_MODAL'}))
        generate.invoke(self.context, None)
        self.context.window_manager.invoke_props_dialog.assert_called_once_with(generate, width=600)
        self.assertIs(generate._preview, self.preview)
        self.ops.qualify_science.assert_not_called()

    def test_rejection_does_not_open_generation_or_cache_qualification(self):
        rejected = dict(self.report, eligible=False, reason='ECP not qualified')
        with self.assertRaisesRegex(ValueError, 'ECP'):
            self.operator().accept(self.context, rejected)
        self.ops.generate_field.assert_not_called()
        self.assertFalse(ui._qualifications)

    def test_selected_object_change_or_binding_change_discards_handoff(self):
        self.context.object = types.SimpleNamespace(name='other')
        with self.assertRaisesRegex(ValueError, 'Selected source'):
            self.operator().accept(self.context, self.report)
        self.context.object = self.source
        with patch.object(ui, 'science_binding', return_value=(self.source, 'other-path', 'manifest-sha', 'science-sha')):
            with self.assertRaisesRegex(ValueError, 'binding'):
                self.operator().accept(self.context, self.report)
        self.ops.generate_field.assert_not_called()

    def test_report_identity_mismatch_and_clear_invalidate_qualification(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.operator().accept(self.context, dict(self.report, science_sha256='other-science'))
        self.operator().accept(self.context, self.report)
        self.assertTrue(ui._qualifications)
        ui.clear_qualifications(None)
        self.assertFalse(ui._qualifications)

    def test_resource_refusal_opens_only_budget_retry_and_is_not_cached(self):
        report = dict(self.report, eligible=False, refusal_kind='resource',
                      reason='Needs 64 MiB', minimum_working_bytes=64 * 1024**2)
        self.operator().accept(self.context, report)
        self.ops.qualify_science.assert_not_called()
        self.timers.tick()
        self.ops.qualify_science.assert_called_once_with('INVOKE_DEFAULT', reason='Needs 64 MiB', memory_mb=64)
        self.ops.generate_field.assert_not_called()
        self.assertFalse(ui._qualifications)
        with self.assertRaisesRegex(ValueError, 'Needs'):
            self.operator().accept(self.context, dict(report, minimum_working_bytes=17000 * 1024**2))

    def test_handoff_waits_for_parent_modal_without_retaining_operator(self):
        operator = self.operator()
        parent_id = id(operator)
        ui._operations[parent_id] = (operator, self.context.window_manager)
        self.addCleanup(ui._operations.pop, parent_id, None)
        operator.accept(self.context, self.report)
        callback = self.timers.callbacks[0]
        self.assertNotIn('self', callback.__code__.co_freevars)
        self.timers.tick()
        self.ops.generate_field.assert_not_called()
        ui._operations.pop(parent_id)
        self.timers.tick()
        self.ops.generate_field.assert_called_once_with('INVOKE_DEFAULT', True, memory_mb=512)
        self.assertFalse(self.timers.callbacks)
        self.assertFalse(ui._qualification_handoffs)

    def test_deferred_handoff_rechecks_object_binding_and_cache(self):
        changes = ('object', 'path', 'digest', 'fingerprint', 'cache')
        for changed in changes:
            with self.subTest(changed=changed):
                self.context.object = self.source
                self.binding_mock.return_value = self.binding
                self.operator().accept(self.context, self.report)
                if changed == 'object':
                    self.context.object = types.SimpleNamespace(name='other')
                elif changed == 'cache':
                    ui._qualifications.clear()
                else:
                    index = {'path': 1, 'digest': 2, 'fingerprint': 3}[changed]
                    binding = list(self.binding)
                    binding[index] = 'changed'
                    self.binding_mock.return_value = tuple(binding)
                self.timers.tick()
                self.ops.generate_field.assert_not_called()
                self.assertFalse(self.timers.callbacks)
                self.context.window_manager.popup_menu.assert_called()
                ui.clear_qualifications()

    def test_deferred_handoff_rejects_closed_editor_and_reports_dispatch_error(self):
        self.operator().accept(self.context, self.report)
        self.context.window.screen.areas.clear()
        self.timers.tick()
        self.ops.generate_field.assert_not_called()
        self.context.window_manager.popup_menu.assert_called_once()
        self.context.window.screen.areas.append(self.context.area)
        self.ops.generate_field.side_effect = RuntimeError('Controlled dialog failure')
        self.operator().accept(self.context, self.report)
        with patch('builtins.print') as diagnostic:
            self.timers.tick()
        self.assertTrue(any('Controlled dialog failure' in str(call) for call in diagnostic.call_args_list))
        self.assertEqual(self.context.window_manager.popup_menu.call_count, 2)
        self.assertFalse(ui._qualification_handoffs)

    def test_save_or_clear_removes_pending_handoff(self):
        self.operator().accept(self.context, self.report)
        callback = self.timers.callbacks[0]
        ui.clear_qualification_handoffs(None)
        self.assertFalse(self.timers.callbacks)
        self.assertIsNone(callback())
        self.ops.generate_field.assert_not_called()
        self.assertTrue(ui._qualifications)
        self.operator().accept(self.context, self.report)
        ui.clear_qualifications()
        self.assertFalse(self.timers.callbacks)
        self.assertFalse(ui._qualifications)

    def test_generate_draw_wraps_resource_refusal_without_changing_grid_labels(self):
        preflight = types.ModuleType('qcblender.science_preflight')
        preflight.preview_grid = Mock(return_value={'shape': (2, 3, 4)})
        refusal = 'The evaluation requires more memory for the current grid and all resident input arrays. ' * 3
        preflight.preview_resources = Mock(return_value={'dataset_bytes': 2 * 1024**2,
            'minimum_working_bytes': 64 * 1024**2, 'refusal_reason': refusal.strip()})
        generate = ui.QCBLENDER_OT_generate()
        generate.quantity = 'electron_number_density'
        generate.memory_mb = 512
        generate.spacing = .2
        generate.padding = 3.
        generate._preview = self.preview
        generate.layout = Mock()
        with patch.dict(sys.modules, {preflight.__name__: preflight}):
            generate.draw(self.context)
        labels = [call.kwargs for call in generate.layout.label.call_args_list]
        errors = [call['text'] for call in labels if call.get('icon') == 'ERROR']
        self.assertGreater(len(errors), 1)
        self.assertTrue(all(len(line) <= 75 for line in errors))
        self.assertEqual(' '.join(errors), refusal.strip())
        self.assertIn({'text': 'Grid: 2 × 3 × 4 | 24 voxels'}, labels)
        self.assertIn({'text': 'Dataset: 2.00 MiB / 1024 MiB'}, labels)
        self.assertIn({'text': 'Evaluation estimate: 64.00 MiB / 512 MiB'}, labels)


class ScienceBinding(unittest.TestCase):
    def test_missing_or_stale_saved_digest_stops_before_qualification(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        identity = types.ModuleType('qcblender.science_identity')
        identity.scientific_identity = Mock(return_value={'sha256': 'science-sha'})
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_bytes(b'{"identity":"original"}')
            digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            source = {'qc_dataset': directory, 'qc_dataset_sha256': digest}
            context = types.SimpleNamespace(object=source)
            qualify = Mock()
            bpy = types.SimpleNamespace(path=types.SimpleNamespace(abspath=lambda path: path),
                                        ops=types.SimpleNamespace(qcblender=types.SimpleNamespace(qualify_science=qualify)))
            with patch.object(ui, 'bpy', bpy), patch.dict(sys.modules, {identity.__name__: identity}):
                self.assertEqual(ui.science_binding(context)[2:], (digest, 'science-sha'))
                manifest.write_bytes(b'{"identity":"replacement"}')
                generate = ui.QCBLENDER_OT_generate()
                generate.report = Mock()
                self.assertEqual(generate.invoke(context, None), {'CANCELLED'})
                qualify.assert_not_called()
                self.assertIn('saved source binding', generate.report.call_args.args[1])
                del source['qc_dataset_sha256']
                self.assertRaisesRegex(ValueError, 'saved source binding', ui.science_binding, context)


if __name__ == '__main__':
    unittest.main()
