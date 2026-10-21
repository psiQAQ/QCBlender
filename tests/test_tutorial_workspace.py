"""Check tutorial package boundaries without Blender or scientific runtimes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from tools.workspace_paths import temporary_tests_root
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'verify_tutorial_workspace', ROOT / 'validation/agent/tools/verify_workspace.py')
workspace = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workspace)


class TutorialWorkspace(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='tutorial-workspace-', dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temporary.cleanup)
        self.materials = Path(self.temporary.name) / 'validation'
        for part in workspace.PUBLIC_PARTS:
            (self.materials / part).mkdir(parents=True)
        self.write('human/SOP.md', '# Tutorial\n\n![View](screenshots/view.png)\n'
                   '![Render](renders/P01-mo.png)\n[Topic](topics/01-example.md)\n')
        self.write('human/topics/01-example.md', '# Example\n\n![Same view](../screenshots/view.png)\n')

    def write(self, relative, text):
        path = self.materials / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
        return path

    def supply_images(self):
        # The checker verifies package paths and file presence, not image pixels.
        self.write('human/screenshots/view.png', 'image fixture')
        self.write('human/renders/P01-mo.png', 'image fixture')

    def test_screenshots_and_renders_are_counted_once_with_compatible_fields(self):
        self.supply_images()
        report = workspace.check_documents(self.materials, require_images=True)
        self.assertEqual(report['images_supplied'], 2)
        self.assertEqual(len(report['image_slots']), 2)
        self.assertEqual(report['images_missing'], [])
        self.assertEqual(report['screenshots_supplied'], 1)
        self.assertEqual(report['screenshot_slots'], [{'path': 'human/screenshots/view.png', 'present': True}])
        self.assertTrue(report['require_images'])
        self.assertEqual(report['human_execution'], 'Not Run')
        self.assertNotIn('work', workspace.PUBLIC_PARTS)

    def test_step_headings_and_legacy_steps_are_counted_with_toc_links(self):
        self.write('human/SOP.md', '# Tutorial\n\n[Install](#step-01)\n'
                   '[Import](#step-02)\n\n<a id="step-01"></a>\n'
                   '### 1. 安装插件\n\nOpen preferences.\n\n'
                   '<a id="step-02"></a>\n### 2. 导入分子\n\nChoose a file.\n')
        self.write('human/topics/01-example.md', '# Example\n\n1. Legacy operation.\n')
        report = workspace.check_documents(self.materials)
        self.assertEqual(report['numbered_operations'], 3)
        self.assertEqual(report['links'], 2)

    def test_missing_images_are_preparation_placeholders_but_fail_strict_gate(self):
        report = workspace.check_documents(self.materials)
        self.assertEqual(report['images_supplied'], 0)
        self.assertEqual(report['images_missing'], ['human/renders/P01-mo.png', 'human/screenshots/view.png'])
        self.assertFalse(report['require_images'])
        with self.assertRaisesRegex(FileNotFoundError, 'Missing required tutorial images:.*P01-mo.png'):
            workspace.check_documents(self.materials, require_images=True)
        self.supply_images()
        (self.materials / 'human/screenshots/view.png').unlink()
        with self.assertRaisesRegex(FileNotFoundError, 'human/screenshots/view.png'):
            workspace.check_documents(self.materials, require_images=True)

    def test_work_reference_is_rejected_even_when_image_exists(self):
        self.write('work/human/P01/P01-mo.png', 'user render')
        self.write('human/SOP.md', '![Render](../work/human/P01/P01-mo.png)\n')
        with self.assertRaisesRegex(ValueError, 'Link leaves public package'):
            workspace.check_documents(self.materials)

    def test_image_must_use_a_supported_name_in_human_asset_directories(self):
        for link in ('../shared/data/public/image.png', 'topics/image.png', 'renders/image.svg'):
            with self.subTest(link=link):
                self.write('human/SOP.md', f'![Image]({link})\n')
                with self.assertRaisesRegex(ValueError, 'Unsupported tutorial image path'):
                    workspace.check_documents(self.materials)

    def test_unknown_and_scientific_work_files_are_rejected_without_changes(self):
        for relative in ('human/user.blend', 'human/user.blend1', 'human/metadata.json',
                         'human/results.csv', 'human/source.cube', 'human/notes.txt',
                         'human/extra.md', 'human/screenshots/export.csv',
                         'human/renders/project.blend'):
            with self.subTest(relative=relative):
                path = self.write(relative, 'user-owned bytes')
                try:
                    with self.assertRaisesRegex(ValueError, 'Unexpected human resource'):
                        workspace.check_documents(self.materials)
                    self.assertEqual(path.read_text(encoding='utf-8'), 'user-owned bytes')
                finally:
                    path.unlink()

    def test_extra_directories_are_rejected_including_empty_project_data(self):
        for relative in ('human/project.qcdata', 'human/exports', 'human/P01',
                         'human/screenshots/project.qcdata', 'human/renders/extra'):
            with self.subTest(relative=relative):
                path = self.materials / relative
                path.mkdir(parents=True)
                try:
                    with self.assertRaisesRegex(ValueError, 'Unexpected human directory'):
                        workspace.check_documents(self.materials)
                    self.assertTrue(path.is_dir())
                finally:
                    path.rmdir()

    def test_unreferenced_image_is_rejected_instead_of_silently_dropped(self):
        path = self.write('human/renders/unknown.png', 'user-owned image')
        with self.assertRaisesRegex(ValueError, 'Unreferenced human images: renders/unknown.png'):
            workspace.check_documents(self.materials)
        self.assertEqual(path.read_text(encoding='utf-8'), 'user-owned image')

    def test_asset_directory_gitkeep_files_are_valid_preparation_placeholders(self):
        self.write('human/screenshots/.gitkeep', '')
        self.write('human/renders/.gitkeep', '')
        report = workspace.check_documents(self.materials)
        self.assertEqual(report['images_supplied'], 0)
        self.assertEqual(len(report['image_slots']), 2)

    def test_public_copy_is_not_created_when_document_gate_fails(self):
        self.write('agent/current-install.json', json.dumps({'sha256': 'candidate-fixture'}))
        for name, options in (('work-file', []), ('missing-images', ['--require-images'])):
            with self.subTest(gate=name):
                report_path = self.materials / f'agent/reports/{name}.json'
                detached = self.materials / f'work/{name}'
                extra = self.write('human/user.blend', 'user-owned project') if name == 'work-file' else None
                argv = ['verify_workspace.py', '--root', str(self.materials.parent),
                        '--report', str(report_path), '--portable-dir', str(detached), *options]
                # Isolate installer/input identity and Git from the copy-order unit test.
                with mock.patch.object(workspace, 'check_materials', return_value={}), \
                        mock.patch.object(workspace.subprocess, 'check_output', return_value='fixture-commit\n'), \
                        mock.patch('sys.argv', argv):
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        workspace.main()
                self.assertFalse(detached.exists())
                report = json.loads(report_path.read_text(encoding='utf-8'))
                self.assertEqual(report['status'], 'Failed')
                self.assertIn('Unexpected human resource' if extra else 'Missing required tutorial images',
                              report['error'])
                if extra is not None:
                    self.assertEqual(extra.read_text(encoding='utf-8'), 'user-owned project')
                    extra.unlink()


if __name__ == '__main__':
    unittest.main()
