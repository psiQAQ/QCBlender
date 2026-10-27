"""Storage boundaries exercised without launching Blender or installing packages."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from tools import build_extension
from tools import run_candidate_ci
from tools.dev_workflow import __main__ as workflow
from tools.dev_workflow.artifacts import prepare_build
from tools.workspace_paths import temporary_tests_root

ROOT = Path(__file__).resolve().parents[1]


class WorkspacePaths(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fixture(self):
        package = self.root / 'qcblender'
        package.mkdir()
        (package / '__init__.py').write_text('VALUE = 1\n', encoding='utf-8')
        (package / 'blender_manifest.toml').write_text('wheels = []\n', encoding='utf-8')
        for name in ('THIRD_PARTY.md', 'LICENSE', 'science-sources.lock.json'):
            (self.root / name).write_text('fixture\n', encoding='utf-8')
        (self.root / 'dependencies.lock.json').write_text('{"packages": []}', encoding='utf-8')
        wheel = b'locked wheel fixture'
        backend = dict(name='backend', filename='backend-1.0-py3-none-any.whl',
                       sha256=hashlib.sha256(wheel).hexdigest())
        candidate = self.root / 'existing.zip'
        with zipfile.ZipFile(candidate, 'w') as archive:
            archive.writestr('backend-wheel.json', json.dumps(backend))
            archive.writestr('wheels/' + backend['filename'], wheel)
        return candidate, backend

    def test_build_uses_modules_and_temporary_profiles_preserving_zip_layout(self):
        candidate, backend = self.fixture()
        prepare_build(self.root, candidate)
        self.assertTrue((self.root / 'modules/wheels' / backend['filename']).is_file())
        calls = []

        def blender_command(command, *, env, check):
            calls.append(command)
            self.assertTrue(check)
            self.assertEqual(Path(env['BLENDER_USER_CONFIG']), self.root / '.tmp/build/blender/config')
            self.assertEqual(Path(env['BLENDER_USER_CACHE']), self.root / '.tmp/cache/blender-build')
            self.assertEqual(Path(env['TEMP']), self.root / '.tmp/build/process-temp')
            self.assertEqual(env['TMP'], env['TEMP'])
            if '--source-dir' in command:
                stage = Path(command[command.index('--source-dir') + 1])
                self.assertTrue(stage.is_relative_to(self.root / '.tmp/build'))
                self.assertEqual(json.loads((stage / 'backend-wheel.json').read_text()), backend)
                self.assertEqual((stage / 'wheels' / backend['filename']).read_bytes(), b'locked wheel fixture')

        with patch.object(build_extension, 'ROOT', self.root), \
             patch.object(build_extension.subprocess, 'run', side_effect=blender_command), \
             patch('sys.argv', ['build_extension.py', '--blender', 'blender.exe']):
            build_extension.main()
        self.assertEqual(len(calls), 2)
        self.assertTrue((self.root / 'outputs/dist').is_dir())
        self.assertFalse((self.root / 'outputs/wheels').exists())
        self.assertFalse((self.root / 'outputs/blender-build').exists())

    def test_workflow_build_places_candidate_outside_run_directory_with_override(self):
        for explicit in (False, True):
            run = self.root / '.tmp/runs' / str(explicit)
            out = self.root / 'outputs/custom' if explicit else self.root / 'outputs/candidates' / run.name
            argv = ['dev_workflow', '--repo', str(self.root), '--run-dir', str(run),
                    'build', '--blender', 'blender.exe']
            if explicit:
                argv.extend(['--output-dir', str(out)])
            with patch('sys.argv', argv), \
                 patch('tools.package_identity.source_identity'), \
                 patch('tools.dev_workflow.session.list_blender_processes', return_value=[]), \
                 patch.object(workflow, 'identity', return_value={}), \
                 patch.object(workflow.Run, 'command', return_value={'status': 'Failed'}) as command:
                workflow.main()
            args = command.call_args.args[1]
            self.assertEqual(args[args.index('--output-dir') + 1], out.resolve())

    def test_candidate_ci_keeps_installed_environment_outside_candidate(self):
        lock = {'target': {'python': '.'.join(str(v) for v in sys.version_info[:2])},
                'host_provided': {'numpy': 'fixture-version'}}
        (self.root / 'dependencies.lock.json').write_text(json.dumps(lock), encoding='utf-8')
        out = self.root / 'outputs/candidate-ci'
        work = self.root / '.tmp/runs/candidate-ci/123'
        with patch.object(run_candidate_ci, 'ROOT', self.root), \
             patch.object(run_candidate_ci, 'source_identity', return_value=('a' * 40, None)), \
             patch('tools.tutorial_bundle.inventory', return_value=({}, None)) as inventory, \
             patch.dict(sys.modules, {'numpy': SimpleNamespace(__version__='fixture-version')}), \
             patch.dict('os.environ', {'GITHUB_STEP_SUMMARY': str(self.root / 'summary.md')}), \
             patch.object(run_candidate_ci.subprocess, 'run', return_value=SimpleNamespace(returncode=7)) as process, \
             patch('sys.argv', ['run_candidate_ci', '--blender', 'blender.exe', '--run-id', '123']):
            with self.assertRaisesRegex(RuntimeError, 'stdlib failed with exit code 7'):
                run_candidate_ci.main()
        inventory.assert_called_once_with(self.root)
        env = process.call_args.kwargs['env']
        self.assertEqual(Path(env['BLENDER_USER_EXTENSIONS']), work / 'profile/extensions')
        self.assertEqual(Path(env['TEMP']), work / 'process-temp')
        self.assertTrue((out / 'commands.json').is_file())
        self.assertFalse((out / 'profile').exists())


if __name__ == '__main__':
    unittest.main()
