"""Use real child processes to check timings and failure evidence without Blender."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from tools.run_candidate_ci import run_command
from tools.workspace_paths import temporary_tests_root

ROOT = Path(__file__).resolve().parents[1]


class CandidateTimingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'logs').mkdir()
        self.summary = self.root / 'summary.md'
        self.env = {**os.environ, 'GITHUB_STEP_SUMMARY': str(self.summary)}
        self.commands = []

    def run_child(self, name, code):
        run_command(name, [sys.executable, '-I', '-S', '-B', '-c', code], root=self.root,
                    env=self.env, output=self.root, commands=self.commands)

    def test_success_and_failure_keep_order_log_hashes_and_summary(self):
        self.run_child('ok', 'print("evidence")')
        with self.assertRaisesRegex(RuntimeError, 'failed with exit code 7'):
            self.run_child('failure', 'import sys; print("failure evidence"); sys.exit(7)')
        records = json.loads((self.root / 'commands.json').read_text(encoding='utf-8'))
        self.assertEqual([r['exit_code'] for r in records], [0, 7])
        for record in records:
            self.assertGreater(record['elapsed_seconds'], 0)
            self.assertLessEqual(datetime.fromisoformat(record['started_at']), datetime.fromisoformat(record['completed_at']))
            self.assertEqual(record['log_sha256'], hashlib.sha256((self.root / record['log']).read_bytes()).hexdigest())
        summary = self.summary.read_text(encoding='utf-8')
        self.assertEqual(summary.count('### Candidate command timings'), 1)
        self.assertIn('| failure |', summary)
        self.assertIn('failure evidence', (self.root / records[1]['log']).read_text(encoding='utf-8'))

    def test_launch_failure_is_not_success(self):
        with self.assertRaises(FileNotFoundError):
            run_command('missing', [self.root / 'missing-executable'], root=self.root,
                        env=self.env, output=self.root, commands=self.commands)
        record = json.loads((self.root / 'commands.json').read_text(encoding='utf-8'))[0]
        self.assertIsNone(record['exit_code'])
        self.assertIn('elapsed_seconds', record)


if __name__ == '__main__':
    unittest.main()
