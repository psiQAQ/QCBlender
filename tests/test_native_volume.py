"""Boundary checks for temporary native VDB probes, without a Blender runtime."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class NativeVolumeTests(unittest.TestCase):
    def setUp(self):
        self.probes = []
        self.removed = []
        self.grids = SimpleNamespace(load=lambda: True, error_message='',
                                     __iter__=lambda: iter(()))
        self.native = SimpleNamespace(data=SimpleNamespace(volumes=SimpleNamespace(
            new=self.new_volume, remove=self.removed.append)))
        spec = importlib.util.spec_from_file_location(
            'qcblender.blender.native_volume',
            Path(__file__).resolve().parents[1] / 'qcblender/blender/native_volume.py')
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'bpy': self.native,
                                     'qcblender.data': SimpleNamespace(resolve_asset=None, volume_cache=None)}):
            spec.loader.exec_module(self.module)

    def new_volume(self, name):
        volume = SimpleNamespace(filepath='', grids=self.grids)
        self.probes.append(volume)
        return volume

    def grid_result(self, loaded=True, reason='', names=('qc_value', 'qc_negative', 'qc_valid')):
        class Grids:
            error_message = reason

            def load(self):
                return loaded

            def __iter__(self):
                return iter(SimpleNamespace(name=name) for name in names)
        self.grids = Grids()

    def test_native_success_returns_names_and_releases_unlinked_probe(self):
        self.grid_result()
        self.assertEqual(self.module.check_volume('ordinary/field.vdb'),
                         {'qc_value', 'qc_negative', 'qc_valid'})
        self.assertEqual(self.probes, self.removed)
        self.assertEqual(self.probes[0].filepath, 'ordinary/field.vdb')

    def test_native_failure_keeps_path_reason_and_releases_probe(self):
        self.grid_result(False, 'field.vdb not found', ())
        with self.assertRaisesRegex(ValueError, 'field.vdb not found') as caught:
            self.module.check_volume('中文/field.vdb')
        self.assertIn('中文/field.vdb', str(caught.exception))
        self.assertEqual(self.probes, self.removed)

    def test_required_grid_absence_rejected_even_when_load_succeeds(self):
        self.grid_result(names=('qc_value', 'qc_negative'))
        with self.assertRaisesRegex(ValueError, 'qc_valid'):
            self.module.check_volume('mask-missing.vdb')
        self.assertEqual(self.probes, self.removed)

    def test_native_exception_retained_and_probe_released(self):
        self.grid_result()
        def failed_load():
            raise RuntimeError('native read failed')
        self.grids.load = failed_load
        with self.assertRaisesRegex(ValueError, 'native read failed'):
            self.module.check_volume('failed.vdb')
        self.assertEqual(self.probes, self.removed)

    def test_field_cache_native_rejection_precedes_checksum(self):
        self.grid_result(False, 'invalid VDB header', ())
        self.module.resolve_asset = lambda directory, relative: Path(directory) / relative
        self.module.volume_cache = lambda *args: self.fail('checksum read preceded native rejection')
        with self.assertRaisesRegex(ValueError, 'invalid VDB header'):
            self.module.check_field_cache('corrupt', {'vdb': 'field.vdb'})
        self.assertEqual(self.probes, self.removed)

    def test_native_success_retains_checksum_validation_and_path(self):
        self.grid_result()
        self.module.resolve_asset = lambda directory, relative: Path(directory) / relative
        def checksum_failure(*args):
            raise ValueError('Volume cache checksum mismatch')
        self.module.volume_cache = checksum_failure
        with self.assertRaisesRegex(ValueError, 'checksum mismatch') as caught:
            self.module.check_field_cache('changed', {'vdb': 'field.vdb'})
        self.assertIn(str(Path('changed') / 'field.vdb'), str(caught.exception))
        self.assertEqual(self.probes, self.removed)

    def test_missing_field_cache_in_dataset_receives_native_reason(self):
        self.grid_result(False, 'missing.vdb not found', ())
        def missing_asset(*args):
            raise FileNotFoundError('missing cache')
        self.module.resolve_asset = missing_asset
        with self.assertRaisesRegex(ValueError, 'missing.vdb not found'):
            self.module.check_field_cache(Path(__file__).parent, {'vdb': 'missing.vdb'})
        self.assertEqual(self.probes, self.removed)


if __name__ == '__main__':
    unittest.main()
