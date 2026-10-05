"""UI qualification handoff and binding boundaries with controlled Blender calls."""
import types
import hashlib
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import Mock, patch

from test_cancel_finalization import ui, ROOT


class QualificationHandoff(unittest.TestCase):
    def setUp(self):
        self.source = types.SimpleNamespace(name='source')
        self.context = types.SimpleNamespace(object=self.source)
        self.binding = (self.source, 'dataset', 'manifest-sha', 'science-sha')
        self.preview = {'lightweight': True}
        self.report = {'eligible': True, 'reason': None, 'preview': self.preview,
                       'dataset_sha256': 'manifest-sha', 'science_sha256': 'science-sha'}
        ui.clear_qualifications()
        self.addCleanup(ui.clear_qualifications)
        self.ops = types.SimpleNamespace(generate_field=Mock(return_value={'RUNNING_MODAL'}),
                                         qualify_science=Mock(return_value={'RUNNING_MODAL'}))
        self.bpy = types.SimpleNamespace(data=types.SimpleNamespace(objects={'source': self.source}),
                                         ops=types.SimpleNamespace(qcblender=self.ops))
        self.binding_patch = patch.object(ui, 'science_binding', return_value=self.binding)
        self.binding_patch.start()
        self.addCleanup(self.binding_patch.stop)
        self.bpy_patch = patch.object(ui, 'bpy', self.bpy)
        self.bpy_patch.start()
        self.addCleanup(self.bpy_patch.stop)

    def operator(self):
        operator = ui.QCBLENDER_OT_qualify_science()
        operator._source, operator._dataset, operator._digest, operator._fingerprint = self.binding
        return operator

    def test_uncached_click_starts_only_qualification(self):
        generate = ui.QCBLENDER_OT_generate()
        generate.memory_mb = 512
        generate.report = Mock()
        self.assertEqual(generate.invoke(self.context, None), {'RUNNING_MODAL'})
        self.ops.qualify_science.assert_called_once_with('EXEC_DEFAULT', memory_mb=512)
        self.ops.generate_field.assert_not_called()

    def test_success_opens_separate_dialog_and_reuses_bound_preview(self):
        self.operator().accept(self.context, self.report)
        self.ops.generate_field.assert_called_once_with('INVOKE_DEFAULT', memory_mb=512)
        generate = ui.QCBLENDER_OT_generate()
        self.context.window_manager = types.SimpleNamespace(invoke_props_dialog=Mock(return_value={'RUNNING_MODAL'}))
        generate.invoke(self.context, None)
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
        self.ops.qualify_science.assert_called_once_with('INVOKE_DEFAULT', reason='Needs 64 MiB', memory_mb=64)
        self.ops.generate_field.assert_not_called()
        self.assertFalse(ui._qualifications)
        with self.assertRaisesRegex(ValueError, 'Needs'):
            self.operator().accept(self.context, dict(report, minimum_working_bytes=17000 * 1024**2))


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
