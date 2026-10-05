"""UI qualification handoff and binding boundaries with controlled Blender calls."""
import types
import unittest
from unittest.mock import Mock, patch

from test_cancel_finalization import ui


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
        generate.report = Mock()
        self.assertEqual(generate.invoke(self.context, None), {'RUNNING_MODAL'})
        self.ops.qualify_science.assert_called_once_with('EXEC_DEFAULT')
        self.ops.generate_field.assert_not_called()

    def test_success_opens_separate_dialog_and_reuses_bound_preview(self):
        self.operator().accept(self.context, self.report)
        self.ops.generate_field.assert_called_once_with('INVOKE_DEFAULT')
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


if __name__ == '__main__':
    unittest.main()
