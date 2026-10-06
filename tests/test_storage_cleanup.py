"""Critical boundaries of the approved output cleanup categories."""
import unittest
import json
import gzip
import os
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

    def test_exact_retirement_can_retire_historical_evidence_and_environment_files(self):
        paths = ('evidence/history/report.md', 'projects/old/a.blend', 'build-site/obsolete.py')
        cleanup.POLICY['retired_files'] = [self.root / path for path in paths]
        for path in paths:
            self.assertEqual(cleanup.classify(self.root / path, {})[0], 'delete')
        self.assertEqual(cleanup.classify(self.root / 'evidence/current/report.md', {})[0], 'keep')

    def test_protection_and_current_report_precede_exact_retirement(self):
        paths = (self.root / 'old/profile/project/a.npy', cleanup.REPORTS / 'summary.json',
                 self.root / 'old/objects/retained.bin', self.root / 'recovery/user.blend')
        cleanup.POLICY['retired_files'] = list(paths)
        cleanup.POLICY['retained_references'] = [paths[2]]
        for path in paths:
            self.assertEqual(cleanup.classify(path, {})[0], 'keep')

    def test_anonymous_objects_require_exact_retirement_even_in_retired_profiles(self):
        for folder in ('objects', 'anonymousobjects', 'content', 'supplemental-objects'):
            path = self.root / 'old/profile' / folder / 'scene.blend'
            cleanup.POLICY['migrated_files'] = [path]
            cleanup.POLICY['retired_files'] = []
            cleanup.POLICY['retained_references'] = []
            self.assertEqual(cleanup.classify(path, {})[0], 'keep')
            cleanup.POLICY['retired_files'] = [path]
            self.assertEqual(cleanup.classify(path, {})[0], 'delete')
            cleanup.POLICY['retained_references'] = [path]
            self.assertEqual(cleanup.classify(path, {})[0], 'keep')

    def make_row(self, relative, content=b'original', action='delete'):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        info = path.stat()
        return {'path': str(path), 'action': action, 'bytes': info.st_size,
                'mtime_ns': info.st_mtime_ns, 'sha256': cleanup.digest(path)}

    def make_manifest(self, rows):
        cleanup.REPORTS.mkdir(parents=True)
        with gzip.open(cleanup.REPORTS / 'inventory.jsonl.gz', 'wt', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row) + '\n')
        (cleanup.REPORTS / 'summary.json').write_text(
            json.dumps({'policy': cleanup.policy_record()}), encoding='utf-8')

    def test_missing_sha_prevents_deletion(self):
        row = self.make_row('old/profile/a.bin')
        del row['sha256']
        with self.assertRaisesRegex(AssertionError, 'missing SHA-256'):
            cleanup.verify_entry(row)

    def test_git_tracked_file_is_protected_even_with_exact_retirement(self):
        row = self.make_row('old/profile/owned.bin')
        cleanup.POLICY['retired_files'] = [Path(row['path'])]
        tracked = {Path(row['path']).relative_to(cleanup.ROOT).as_posix()}
        with self.assertRaisesRegex(AssertionError, 'Git tracked file'):
            cleanup.verify_entry(row, tracked)

    def test_changed_protection_preflight_prevents_every_deletion(self):
        rows = [self.make_row('old/profile/delete.bin'),
                self.make_row('old/profile/project/protected.bin', action='keep')]
        rows[1]['verification_required'] = True
        self.make_manifest(rows)
        Path(rows[1]['path']).write_bytes(b'changed protected object')
        with patch.object(cleanup, 'tracked_paths', return_value=set()):
            report = cleanup.apply()
        self.assertEqual(report['removed']['files'], 0)
        self.assertEqual(report['status'], 'Failed')
        self.assertTrue(Path(rows[0]['path']).is_file())
        self.assertIn('file changed', report['skipped'][0]['reason'])
        receipt = (cleanup.REPORTS / 'applied.json').read_bytes()
        with self.assertRaises(FileExistsError):
            cleanup.apply()
        self.assertEqual((cleanup.REPORTS / 'applied.json').read_bytes(), receipt)

    def test_missing_protected_sha_aborts_before_delete(self):
        rows = [self.make_row('old/profile/delete.bin'),
                self.make_row('old/profile/project/protected.bin', action='keep')]
        rows[1]['reason'] = 'explicit protected path or shared retained root'
        del rows[1]['sha256']
        self.make_manifest(rows)
        with patch.object(cleanup, 'tracked_paths', return_value=set()):
            report = cleanup.apply()
        self.assertEqual(report['removed']['files'], 0)
        self.assertIn('missing SHA-256', report['skipped'][0]['reason'])

    def test_new_git_protection_aborts_before_any_delete(self):
        rows = [self.make_row('old/profile/delete.bin'), self.make_row('old/profile/newly-tracked.bin')]
        self.make_manifest(rows)
        tracked = {Path(rows[1]['path']).relative_to(cleanup.ROOT).as_posix()}
        with patch.object(cleanup, 'tracked_paths', return_value=tracked):
            report = cleanup.apply()
        self.assertEqual(report['removed']['files'], 0)
        self.assertEqual(report['protection_preflight'], 'Failed')
        self.assertEqual(report['skipped'][0]['reason'], 'Git tracked file')
        self.assertTrue(all(Path(row['path']).is_file() for row in rows))

    def test_denied_protected_directory_scan_aborts_before_delete(self):
        row = self.make_row('old/profile/delete.bin')
        self.make_manifest([row])
        summary = cleanup.REPORTS / 'summary.json'
        data = json.loads(summary.read_text(encoding='utf-8'))
        data['skipped'] = [{'path': str(self.root / 'old/profile/project'), 'reason': '[WinError 5] original directory denied'}]
        summary.write_text(json.dumps(data), encoding='utf-8')
        with patch.object(cleanup, 'tracked_paths', return_value=set()):
            report = cleanup.apply()
        self.assertEqual(report['removed']['files'], 0)
        self.assertEqual(report['skipped'][0]['reason'], data['skipped'][0]['reason'])
        self.assertEqual(report['skipped'][0]['phase'], 'protection preflight')

    def test_scanner_records_denied_directory_instead_of_treating_it_as_empty(self):
        skipped = []
        with patch.object(cleanup.os, 'scandir', side_effect=PermissionError('[WinError 5] denied scan')):
            self.assertEqual(list(cleanup.files(self.root, skipped)), [])
        self.assertEqual(skipped, [{'path': str(self.root), 'reason': '[WinError 5] denied scan'}])

    def test_unknown_denied_recovery_does_not_block_independent_retirement(self):
        row = self.make_row('old/profile/delete.bin')
        self.make_manifest([row])
        summary = cleanup.REPORTS / 'summary.json'
        data = json.loads(summary.read_text(encoding='utf-8'))
        unknown = self.root / 'recovery/unknown-owner'
        data['skipped'] = [{'path': str(unknown), 'reason': '[WinError 5] unknown directory denied'}]
        summary.write_text(json.dumps(data), encoding='utf-8')
        self.assertFalse(cleanup.protection_required(unknown, cleanup.classify(unknown, {})[1]))
        with patch.object(cleanup, 'tracked_paths', return_value=set()):
            report = cleanup.apply()
        self.assertEqual(report['removed']['files'], 1)
        self.assertEqual(report['protection_preflight'], 'Passed')
        self.assertEqual(report['skipped'], [])
        self.assertEqual(json.loads(summary.read_text(encoding='utf-8'))['skipped'], data['skipped'])

    def test_apply_retains_changed_and_missing_hash_files_and_original_permission_error(self):
        rows = [self.make_row('old/profile/changed.bin'), self.make_row('old/profile/missing.bin'),
                self.make_row('old/profile/denied.bin'), self.make_row('old/profile/delete.bin')]
        Path(rows[0]['path']).write_bytes(b'altered!')
        info = Path(rows[0]['path']).stat()
        os.utime(rows[0]['path'], ns=(info.st_atime_ns, rows[0]['mtime_ns']))
        del rows[1]['sha256']
        self.make_manifest(rows)
        original_unlink = Path.unlink

        def unlink(path, *args, **kwargs):
            if path == Path(rows[2]['path']):
                raise PermissionError('[WinError 5] Access is denied: exact file')
            return original_unlink(path, *args, **kwargs)

        with patch.object(cleanup, 'tracked_paths', return_value=set()), patch.object(Path, 'unlink', unlink):
            report = cleanup.apply()
        self.assertEqual(report['removed']['files'], 1)
        self.assertEqual(len(report['skipped']), 3)
        self.assertEqual(report['skipped'][2]['reason'], '[WinError 5] Access is denied: exact file')
        self.assertTrue(all(Path(row['path']).is_file() for row in rows[:3]))
        self.assertFalse(Path(rows[3]['path']).exists())
        self.assertEqual(report['protection_preflight'], 'Passed')
        with gzip.open(cleanup.REPORTS / 'removed.jsonl.gz', 'rt', encoding='utf-8') as stream:
            success = list(map(json.loads, stream))
        self.assertEqual(success, [{key: rows[3][key] for key in ('path', 'bytes', 'sha256')}])

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

    def test_reports_allow_only_approved_descendants_and_reject_linked_ancestors(self):
        self.assertEqual(cleanup.safe_report_path(self.root / 'receipts'), self.root / 'receipts')
        allowed = cleanup.ROOT / 'validation/agent/reports/date/prune'
        self.assertEqual(cleanup.safe_report_path(allowed), allowed)
        for path in (cleanup.ROOT / 'validation/human/receipt', cleanup.ROOT / 'other',
                     cleanup.ROOT / 'validation/agent/reports', self.root):
            with self.assertRaisesRegex(AssertionError, 'subdirectory'):
                cleanup.safe_report_path(path)
        linked = cleanup.ROOT / 'validation/agent'
        with patch.object(Path, 'is_junction', lambda path: path == linked):
            with self.assertRaisesRegex(AssertionError, 'link or junction'):
                cleanup.safe_report_path(allowed)

    def test_inaccessible_canonical_wheel_is_kept(self):
        with patch.object(Path, 'is_file', return_value=True), patch.object(cleanup, 'digest', side_effect=PermissionError('denied')):
            self.assertEqual(cleanup.classify(self.root / 'old/library.whl', {})[0], 'keep')

    def test_generated_canonical_input_is_verified_without_a_migration_origin(self):
        input_file = self.root / 'validation/shared/data/local/generated.cub'
        input_file.parent.mkdir(parents=True)
        input_file.write_bytes(b'owned generated field')
        index = self.root / 'validation/shared/data/local-inputs.json'
        index.write_text(json.dumps({'files': {'generated.cub': {
            'path': 'validation/shared/data/local/generated.cub', 'sha256': cleanup.digest(input_file)}}}), encoding='utf-8')
        output = self.root / 'outputs'
        output.mkdir()
        with patch.object(cleanup, 'ROOT', self.root), patch.object(cleanup, 'OUTPUTS', output), \
             patch.object(cleanup, 'REPORTS', output / 'receipts'), \
             patch.object(cleanup.subprocess, 'check_output', return_value=''):
            cleanup.plan()
            self.assertTrue((output / 'receipts/summary.json').is_file())
            input_file.write_bytes(b'changed scientific input')
            with patch.object(cleanup, 'REPORTS', output / 'receipts-second'), self.assertRaisesRegex(AssertionError, 'generated.cub'):
                cleanup.plan()

    def test_plan_hashes_protected_objects_and_candidates_but_not_unknown_outputs(self):
        repo = self.root / 'repo'
        output = repo / 'outputs'
        output.mkdir(parents=True)
        index = repo / 'validation/shared/data/local-inputs.json'
        index.parent.mkdir(parents=True)
        index.write_text('{"files": {}}', encoding='utf-8')
        unknown = output / 'unknown/large.bin'
        retired = output / 'evidence/old/report.md'
        protected = output / 'science/active.bin'
        for path in (unknown, retired, protected):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'content')
        policy = {key: set() for key in ('protected_paths', 'retired_task_roots', 'retired_profiles',
                                         'migrated_files', 'retired_files', 'retained_references')}
        policy['retired_files'].add(retired)
        policy['protected_paths'].add(protected)
        with patch.object(cleanup, 'ROOT', repo), patch.object(cleanup, 'OUTPUTS', output), \
             patch.object(cleanup, 'REPORTS', repo / 'validation/agent/reports/prune'), \
             patch.object(cleanup, 'POLICY', policy), patch.object(cleanup, 'tracked_paths', return_value=set()), \
             patch.object(cleanup, 'digest', wraps=cleanup.digest) as digests:
            cleanup.plan()
            hashed = {call.args[0] for call in digests.call_args_list}
            self.assertNotIn(unknown, hashed)
            self.assertIn(protected, hashed)
            self.assertIn(retired, hashed)
            with gzip.open(cleanup.REPORTS / 'inventory.jsonl.gz', 'rt', encoding='utf-8') as stream:
                rows = {Path(row['path']): row for row in map(json.loads, stream)}
            self.assertNotIn('sha256', rows[unknown])
            self.assertTrue(rows[protected]['verification_required'])
            before = (cleanup.REPORTS / 'inventory.jsonl.gz').read_bytes()
            with self.assertRaisesRegex(AssertionError, 'Report already exists'):
                cleanup.plan()
            self.assertEqual((cleanup.REPORTS / 'inventory.jsonl.gz').read_bytes(), before)
            index.write_text('{"files": {}, "changed": true}', encoding='utf-8')
            report = cleanup.apply()
            self.assertEqual(report['removed']['files'], 0)
            self.assertEqual(report['protection_preflight'], 'Failed')
            self.assertIn('protected input changed', report['skipped'][0]['reason'])
            self.assertTrue(retired.is_file())

    def test_invalid_policy_cannot_retire_shared_roots(self):
        path = self.root / 'policy.json'
        (self.root / 'existing-directory').mkdir()
        for data in ({'retired_profiles': ['../outside']}, {'retired_profiles': ['science']},
                     {'retired_task_roots': ['.']}, {'other': []}, {'retired_files': ['.']},
                     {'retired_files': ['existing-directory']}, {'retained_references': ['../outside']},
                     {'retained_references': ['existing-directory']}):
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises((ValueError, AssertionError)):
                cleanup.load_policy(path)

if __name__ == '__main__':
    unittest.main()
