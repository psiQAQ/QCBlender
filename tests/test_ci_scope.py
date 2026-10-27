"""Exercise candidate routing against real Git changes, including renames and PR bases."""
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import ci_scope
from tools.ci_scope import changed_paths, requires_candidate
from tools.workspace_paths import temporary_tests_root

ROOT = Path(__file__).resolve().parents[1]


class CandidateScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-b', 'main')
        self.git('config', 'user.email', 'ci-test@example.invalid')
        self.git('config', 'user.name', 'CI fixture')
        self.git('config', 'commit.gpgsign', 'false')
        self.write('qcblender/source.py', 'original\n')
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-m', 'fixture')
        return self.git('rev-parse', 'HEAD')

    def test_known_unrelated_and_unknown_inputs(self):
        self.assertFalse(requires_candidate(['website/src/index.astro', 'AGENTS.md', 'docs/agents/rules.md', 'README.md']))
        for path in ('validation/human/SOP.md', 'validation/shared/data/public/example.xyz',
                     'tools/run_candidate_ci.py', 'dependencies.lock.json', 'LICENSE',
                     '.github/workflows/extension-package.yml', 'new-input.json'):
            with self.subTest(path=path):
                self.assertTrue(requires_candidate(['website/src/index.astro', path]))

    def test_push_compares_all_commits_and_renames_both_paths(self):
        self.write('README.md', 'docs\n')
        self.commit()
        (self.root / 'website').mkdir()
        self.git('mv', 'qcblender/source.py', 'website/source.py')
        head = self.commit()
        paths, commits = changed_paths('push', {'before': self.base, 'after': head}, self.root)
        self.assertEqual(set(paths), {'README.md', 'qcblender/source.py', 'website/source.py'})
        self.assertEqual(commits, (self.base, head))
        self.assertTrue(requires_candidate(paths))

    def test_pr_ignores_base_only_changes(self):
        self.git('checkout', '-b', 'topic')
        self.write('website/guide.md', 'website only\n')
        head = self.commit()
        self.git('checkout', 'main')
        self.write('qcblender/source.py', 'base branch changed\n')
        base_tip = self.commit()
        event = {'pull_request': {'base': {'sha': base_tip}, 'head': {'sha': head}}}
        paths, commits = changed_paths('pull_request', event, self.root)
        self.assertEqual(paths, ['website/guide.md'])
        self.assertEqual(commits, (self.base, head))
        self.assertFalse(requires_candidate(paths))

    def test_dispatch_empty_and_missing_base_require_full(self):
        for event_name, event in (
                ('workflow_dispatch', {}),
                ('push', {'before': '0' * 40, 'after': self.base}),
                ('push', {'before': '1' * 40, 'after': self.base}),
                ('push', {'before': self.base, 'after': self.base})):
            with self.subTest(event_name=event_name, event=event):
                paths, _ = changed_paths(event_name, event, self.root)
                self.assertTrue(requires_candidate(paths))

    def test_lightweight_cli_checks_diff_before_emitting_output(self):
        for whitespace_error in (False, True):
            with self.subTest(whitespace_error=whitespace_error):
                self.write('README.md', 'docs  \n' if whitespace_error else 'docs\n')
                head = self.commit()
                event = self.root / '.git/event.json'
                event.write_text(json.dumps({'before': self.base, 'after': head}), encoding='utf-8')
                output = self.root / '.git' / f'output-{whitespace_error}'
                env = {'GITHUB_EVENT_NAME': 'push', 'GITHUB_EVENT_PATH': str(event),
                       'GITHUB_OUTPUT': str(output), 'GITHUB_STEP_SUMMARY': str(self.root / '.git/summary')}
                with patch.object(ci_scope, '__file__', str(self.root / 'tools/ci_scope.py')), patch.dict('os.environ', env):
                    if whitespace_error:
                        with self.assertRaises(subprocess.CalledProcessError):
                            ci_scope.main()
                        self.assertFalse(output.exists())
                    else:
                        ci_scope.main()
                        self.assertEqual(output.read_text(encoding='utf-8'), 'full=false\n')


if __name__ == '__main__':
    unittest.main()
