import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import numpy as np

from qcblender.data import Dataset, load_dataset, save_dataset
from qcblender.project import archive_project, copy_dataset

ROOT = Path(__file__).resolve().parents[1]


class PortableProject(unittest.TestCase):
    def test_exact_copy_archive_and_corruption_rejection(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as temporary:
            root = Path(temporary)
            # No display field: native VDB integration is checked by Blender acceptance.
            data = Dataset({'coordinate_unit': 'angstrom'}, {
                'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3))})
            source = root / 'source'
            manifest = save_dataset(data, source)
            raw = manifest.read_bytes()
            target = root / '迁移 project.qcdata'
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as pool:
                copies = list(pool.map(lambda _: copy_dataset(source, target), range(4)))
            copied = copies[0]
            self.assertTrue(all(path == copied for path in copies))
            self.assertEqual(copied.name, hashlib.sha256(raw).hexdigest())
            self.assertEqual((copied / 'manifest.json').read_bytes(), raw)
            np.testing.assert_array_equal(load_dataset(copied).arrays['positions'], data.arrays['positions'])
            self.assertEqual(copy_dataset(source, target), copied)
            (target / 'manifest.json').write_text(json.dumps({'format': 'qcblender.scene', 'schema': '0.1',
                'datasets': [copied.relative_to(target).as_posix()]}), encoding='utf-8')
            blend = target.with_suffix('.blend')
            blend.write_bytes(b'package membership test only')
            archive = archive_project(blend, root / 'project.zip')
            with zipfile.ZipFile(archive) as package:
                self.assertIn(blend.name, package.namelist())
                self.assertEqual(package.read(target.name + '/datasets/' + copied.name + '/manifest.json'), raw)
            (copied / 'manifest.json').write_bytes(raw + b' ')
            with self.assertRaisesRegex(ValueError, 'identity'):
                copy_dataset(source, target)
