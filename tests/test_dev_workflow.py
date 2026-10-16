"""Necessary workflow boundaries: real failed checks and exact-input reuse."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.dev_workflow.records import Run, read


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        (root/'outputs').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='workflow-tests-',dir=root/'outputs')
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)
        self.run=Run(root,self.path)

    def test_failed_command_records_failure_and_does_not_retry(self):
        command=[sys.executable,'-c','raise SystemExit(7)']
        result=self.run.command('failure',command,{'version':1})
        self.assertEqual(result['status'],'Failed')
        self.assertEqual(read(result['report'])['exit_code'],7)
        before=(self.path/'failure.log').stat().st_mtime_ns
        with self.assertRaisesRegex(ValueError,'--retry'):
            self.run.command('failure',command,{'version':1})
        self.assertEqual((self.path/'failure.log').stat().st_mtime_ns,before)

    def test_same_inputs_reuse_success_changed_inputs_require_decision(self):
        command=[sys.executable,'-c','print("actual execution")']
        first=self.run.command('check',command,{'version':1})
        second=self.run.command('check',[sys.executable,'-c','raise SystemExit(9)'],{'version':1})
        self.assertEqual(first['status'],second['status'])
        self.assertIn('reused_from',second)
        with self.assertRaisesRegex(ValueError,'--retry'):
            self.run.command('check',command,{'version':2})

    def test_failed_report_cannot_be_success_even_with_zero_exit(self):
        report=self.path/'native.json'
        command=[sys.executable,'-c',f'import json;from pathlib import Path;Path({str(report)!r}).write_text(json.dumps({{"status":"Failed"}}))']
        result=self.run.command('native',command,{},expected_report=report)
        self.assertEqual(result['status'],'Failed')


if __name__=='__main__':
    unittest.main()
