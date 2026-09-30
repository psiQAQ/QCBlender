"""Critical boundaries of the approved output cleanup categories."""
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools import prune_outputs as cleanup
from tools.prune_outputs import OUTPUTS, classify


class CleanupBoundaries(unittest.TestCase):
    def test_environment_and_user_project_precede_generated_file_rules(self):
        keep = ('recovery/pid3144-preserved/evidence.blend',
                'batch/profile/config/userpref.blend',
                'batch/profile/extensions/user_default/qcblender/assets/nodes.blend',
                'committed-build/source/outputs/science/package/reference.npy',
                'v1-acceptance/sources/raw-calculation.log', 'branch-archive/manifest.json',
                'unknown-user-folder/user.blend', 'process-temp/quit.blend')
        remove = ('vmd-parameters/evidence.qcdata/datasets/id/manifest.json', 'vmd-parameters/dist/qcblender.zip',
                  'batch/profile/extensions/.user/qcblender/jobs/id/dataset/arrays/a.npy',
                  'batch/profile/datafiles/qcblender/analyses/id/arrays/a.npy')
        for path in keep:
            self.assertEqual(classify(OUTPUTS / path, {})[0], 'keep', path)
        for path in remove:
            self.assertEqual(classify(OUTPUTS / path, {})[0], 'delete', path)
        self.assertEqual(classify(OUTPUTS / 'batch/profile/extensions/.user/qcblender/jobs/id/worker.log', {})[0], 'keep')



class PolicySafety(unittest.TestCase):
    def setUp(self):
        base = cleanup.ROOT / 'outputs' / 'policy-tests'
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.addCleanup(patch.stopall)
        patch.object(cleanup, 'OUTPUTS', self.root).start()
        patch.object(cleanup, 'REPORTS', self.root / 'receipts').start()
        patch.object(cleanup, 'POLICY', {'protected_paths': [self.root / 'old/profile/project'], 'retired_task_roots': [self.root / 'old'], 'retired_profiles': [self.root / 'old/profile']}).start()

    def test_explicit_protection_and_retirement(self):
        for path, expected in [('old/profile/project/a.npy', 'keep'), ('old/profile/extensions/a.dll', 'delete'), ('old/scene.blend', 'delete'), ('unknown/scene.blend', 'keep'), ('science/a.npy', 'keep'), ('backend-wheel.json', 'keep'), ('evidence/a.png', 'keep')]:
            self.assertEqual(cleanup.classify(self.root / path, {})[0], expected, path)

    def test_verified_migration_can_retire_a_report_without_retiring_other_logs(self):
        cleanup.POLICY['migrated_files'] = [self.root / 'old/report.json']
        self.assertEqual(cleanup.classify(self.root / 'old/report.json', {})[0], 'delete')
        self.assertEqual(cleanup.classify(self.root / 'old/other.log', {})[0], 'keep')

    def test_content_change_with_preserved_size_and_time_is_rejected(self):
        import os
        path = self.root / 'old/file.txt'
        path.parent.mkdir(); path.write_bytes(b'abcd')
        info = path.stat()
        row = {'path': str(path), 'action': 'delete', 'bytes': info.st_size, 'mtime_ns': info.st_mtime_ns, 'sha256': cleanup.digest(path)}
        path.write_bytes(b'efgh')
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        with self.assertRaisesRegex(AssertionError, 'content changed'):
            cleanup.verify_entry(row)

    def test_changed_policy_refuses_a_previously_retired_file(self):
        path = self.root / 'old/profile/a.dll'
        path.parent.mkdir(parents=True); path.write_bytes(b'library')
        info = path.stat()
        row = {'path': str(path), 'action': 'delete', 'bytes': info.st_size, 'mtime_ns': info.st_mtime_ns, 'sha256': cleanup.digest(path)}
        cleanup.POLICY['protected_paths'].append(path.parent)
        with self.assertRaisesRegex(AssertionError, 'policy no longer'):
            cleanup.verify_entry(row)

    def test_outside_path_and_junction_ancestor_are_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'outside outputs'):
            cleanup.safe_output_path(self.root.parent / 'outside')
        with patch.object(Path, 'is_junction', return_value=True):
            with self.assertRaisesRegex(AssertionError, 'link or junction'):
                cleanup.safe_output_path(self.root / 'old/a.dll')

    def test_inaccessible_canonical_wheel_is_kept(self):
        with patch.object(Path, 'is_file', return_value=True), patch.object(cleanup, 'digest', side_effect=PermissionError('denied')):
            self.assertEqual(cleanup.classify(self.root / 'old/library.whl', {})[0], 'keep')

    def test_generated_canonical_input_is_verified_without_a_migration_origin(self):
        input_file = self.root / 'tests/data/local/generated.cub'
        input_file.parent.mkdir(parents=True)
        input_file.write_bytes(b'owned generated field')
        index = self.root / 'tests/data/local-inputs.json'
        index.write_text(json.dumps({'files': {'generated.cub': {
            'path': 'tests/data/local/generated.cub', 'sha256': cleanup.digest(input_file)}}}), encoding='utf-8')
        output = self.root / 'outputs'
        output.mkdir()
        with patch.object(cleanup, 'ROOT', self.root), patch.object(cleanup, 'OUTPUTS', output), \
             patch.object(cleanup, 'REPORTS', output / 'receipts'), \
             patch.object(cleanup.subprocess, 'check_output', return_value=''):
            cleanup.plan()
            self.assertTrue((output / 'receipts/summary.json').is_file())
            input_file.write_bytes(b'changed scientific input')
            with self.assertRaises(AssertionError):
                cleanup.plan()

    def test_invalid_policy_cannot_retire_shared_roots(self):
        path = self.root / 'policy.json'
        for data in ({'retired_profiles': ['../outside']}, {'retired_profiles': ['science']}, {'retired_task_roots': ['.']}, {'other': []}):
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises((ValueError, AssertionError)):
                cleanup.load_policy(path)

if __name__ == '__main__':
    unittest.main()
