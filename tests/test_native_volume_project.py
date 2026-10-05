"""Transaction boundary tests; Blender-save injection is not native integration evidence."""
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


class Object(dict):
    __hash__ = object.__hash__


class Volume(SimpleNamespace):
    __hash__ = object.__hash__


class NativeVolumeProjectTests(unittest.TestCase):
    def setUp(self):
        outputs = ROOT / 'outputs'
        outputs.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='native-volume-unit-', dir=outputs)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.source = self.directory / 'source'
        self.replacement = self.directory / 'replacement'
        self.source.mkdir()
        self.replacement.mkdir()
        (self.replacement / 'manifest.json').write_bytes(b'{}')
        self.object = Object(qc_dataset=str(self.source), qc_dataset_sha256='original')
        self.volume = Volume(filepath=str(self.source / 'field.vdb'),
                             grids=SimpleNamespace(unload=lambda: None), update_tag=lambda: None)
        self.save = lambda **kwargs: {'FINISHED'}
        bpy = SimpleNamespace(data=SimpleNamespace(objects=[self.object], volumes=[self.volume], filepath=''),
                              path=SimpleNamespace(abspath=lambda value: value, relpath=lambda value, start: value),
                              ops=SimpleNamespace(wm=SimpleNamespace(save_as_mainfile=lambda **kwargs: self.save(**kwargs))),
                              types=SimpleNamespace(Operator=type('Operator', (), {})))
        spec = importlib.util.spec_from_file_location('qcblender.blender.project', ROOT / 'qcblender/blender/project.py')
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            'bpy': bpy,
            'bpy.props': SimpleNamespace(StringProperty=lambda **kwargs: None),
            'bpy_extras.io_utils': SimpleNamespace(ExportHelper=type('ExportHelper', (), {}),
                                                  ImportHelper=type('ImportHelper', (), {})),
            'qcblender.blender.ui': SimpleNamespace(AsyncOperation=type('AsyncOperation', (), {})),
            'qcblender.blender.native_volume': SimpleNamespace(check_volume=lambda path: None, check_field_cache=None),
            'qcblender.data': SimpleNamespace(load_dataset=None, filesystem_path=Path, unprefixed_path=Path),
            'qcblender.project': SimpleNamespace(archive_project=None, copy_dataset=None),
        }):
            spec.loader.exec_module(self.module)
        self.module.load_dataset = lambda path: SimpleNamespace(metadata={'fields': [{'vdb': 'field.vdb'}]})
        self.module.volume_cache = lambda directory, field: Path(directory) / field['vdb']
        def checked_cache(directory, field):
            cache = Path(directory) / field['vdb']
            self.module.check_volume(cache)
            return cache
        self.module.check_field_cache = checked_cache

    def state(self):
        return dict(self.object), self.volume.filepath

    def test_rebind_native_rejection_precedes_all_binding_changes(self):
        before = self.state()
        checked = []
        def reject(path):
            checked.append(path)
            raise ValueError('native target unreadable')
        self.module.check_volume = reject
        with self.assertRaisesRegex(ValueError, 'native target unreadable'):
            self.module.rebind_dataset(self.source, self.replacement)
        self.assertEqual(self.state(), before)
        self.assertEqual(checked, [self.replacement / 'field.vdb'])

    def test_rebind_checks_actual_volume_target_before_changes(self):
        self.volume.filepath = str(self.source / 'extra.vdb')
        before = self.state()
        def reject_extra(path):
            if path.name == 'extra.vdb':
                raise ValueError('extra target unreadable')
        self.module.check_volume = reject_extra
        with self.assertRaisesRegex(ValueError, 'extra target unreadable'):
            self.module.rebind_dataset(self.source, self.replacement)
        self.assertEqual(self.state(), before)

    def test_save_checks_final_copy_before_index_scene_or_save_changes(self):
        target = self.directory / 'original.blend'
        target.write_bytes(b'original project')
        sidecar = target.with_suffix('.qcdata')
        sidecar.mkdir()
        index = sidecar / 'manifest.json'
        index.write_bytes(b'original index')
        destination = sidecar / 'datasets/identity'
        self.module.copy_dataset = lambda source, root: destination
        checked = []
        def reject(path):
            checked.append(path)
            raise ValueError('final copy unreadable')
        self.module.check_volume = reject
        self.save = lambda **kwargs: self.fail('save called before validation')
        before = self.state()
        with self.assertRaisesRegex(ValueError, 'final copy unreadable'):
            self.module.save_project(target)
        self.assertEqual(checked, [destination / 'field.vdb'])
        self.assertEqual(self.state(), before)
        self.assertEqual(target.read_bytes(), b'original project')
        self.assertEqual(index.read_bytes(), b'original index')

    def test_injected_blender_save_failure_restores_bindings_and_index(self):
        target = self.directory / 'original.blend'
        target.write_bytes(b'original project')
        sidecar = target.with_suffix('.qcdata')
        sidecar.mkdir()
        index = sidecar / 'manifest.json'
        index.write_bytes(b'original index')
        self.module.copy_dataset = lambda source, root: sidecar / 'datasets/identity'
        def failed_save(**kwargs):
            raise RuntimeError('injected Blender-save boundary failure')
        self.save = failed_save
        before = self.state()
        with self.assertRaisesRegex(RuntimeError, 'Blender-save boundary failure'):
            self.module.save_project(target)
        self.assertEqual(self.state(), before)
        self.assertEqual(target.read_bytes(), b'original project')
        self.assertEqual(index.read_bytes(), b'original index')
        self.assertFalse(list(sidecar.glob('*.pending.json')))


if __name__ == '__main__':
    unittest.main()
