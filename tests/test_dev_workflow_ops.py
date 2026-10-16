"""Process ownership boundary; actual Blender operations run in Blender acceptance."""
import os
import unittest
from unittest.mock import patch

from tools.dev_workflow import blender_ops


class BlenderDispatchTests(unittest.TestCase):
    def test_wrong_or_missing_pid_rejects_every_write_before_loading_blender(self):
        with patch.object(blender_ops, '_bpy', side_effect=AssertionError('Blender was accessed')):
            for action in blender_ops.ACTIONS - blender_ops.READ_ACTIONS:
                for pid in (None, os.getpid() + 1):
                    with self.subTest(action=action, pid=pid), self.assertRaisesRegex(ValueError, 'PID mismatch'):
                        blender_ops.dispatch({'action': action, 'expected_pid': pid})

    def test_read_only_identity_accepts_no_pid_but_rejects_wrong_pid(self):
        with patch.object(blender_ops, '_identity', return_value={'pid': os.getpid()}) as identity:
            self.assertEqual(blender_ops.dispatch({'action': 'identity'})['status'], 'Passed')
            with self.assertRaisesRegex(ValueError, 'PID mismatch'):
                blender_ops.dispatch({'action': 'identity', 'expected_pid': os.getpid() + 1})
            identity.assert_called_once()

    def test_snapshot_assert_ignores_process_and_project_locations_but_checks_state(self):
        expected = {'identity': {'pid': 1, 'filepath': 'before.blend'}, 'state': {'objects': {'atoms': {}}}}
        actual = {'identity': {'pid': 2, 'filepath': 'moved.blend'}, 'state': {'objects': {'atoms': {}}}}
        with patch.object(blender_ops, '_snapshot', return_value=actual):
            self.assertTrue(blender_ops.dispatch({'action': 'assert', 'args': {'expected': expected}})['result']['snapshot_matches'])
            actual['state']['objects']['atoms']['parent'] = 'changed'
            with self.assertRaisesRegex(AssertionError, 'snapshot differs'):
                blender_ops.dispatch({'action': 'assert', 'args': {'expected': expected}})


if __name__ == '__main__':
    unittest.main()
