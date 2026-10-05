"""Storage digest parity and corruption checks without Blender or peak-memory claims."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qcblender import data as storage


ROOT = Path(__file__).resolve().parents[1]


class StreamingDigests(unittest.TestCase):
    def setUp(self):
        output = ROOT / 'outputs/streaming-digest-tests'
        output.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.data = storage.Dataset({'coordinate_unit': 'angstrom'}, {
            'atomic_numbers': np.array([1, 8], dtype=np.int32),
            'positions': np.array([[0., 0., 0.], [0., 0., 1.]], dtype=np.float64),
            'large_values': np.linspace(-1., 1., 262145, dtype=np.float64),
            'validity': np.arange(262145) % 3 != 0,
        })

    def test_save_hash_names_manifest_and_roundtrip_match_complete_bytes(self):
        manifest_path = storage.save_dataset(self.data, self.directory / 'dataset')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for name, array in self.data.arrays.items():
            with self.subTest(array=name):
                payload = io.BytesIO()
                np.save(payload, array, allow_pickle=False)
                expected = hashlib.sha256(payload.getvalue()).hexdigest()
                self.assertEqual(manifest['arrays'][name], {
                    'path': f'arrays/{expected}.npy', 'sha256': expected,
                    'dtype': array.dtype.str, 'shape': list(array.shape)})
                self.assertEqual((manifest_path.parent / f'arrays/{expected}.npy').read_bytes(),
                                 payload.getvalue())
        loaded = storage.load_dataset(manifest_path.parent)
        self.assertEqual(loaded.metadata, self.data.metadata)
        for name, array in self.data.arrays.items():
            np.testing.assert_array_equal(loaded.arrays[name], array)
            self.assertEqual(loaded.arrays[name].dtype, array.dtype)

    def test_large_storage_digest_paths_do_not_materialize_file_bytes(self):
        # This probes only the hashing boundary: array loading still uses the
        # established np.load/mmap and materialization behavior.
        dataset = self.directory / 'dataset'
        opaque_cache = self.directory / 'cache.vdb'
        payload = bytes(range(256)) * 8192 + b'tail'
        opaque_cache.write_bytes(payload)
        scalar = {'vdb': opaque_cache.name, 'vdb_sha256': hashlib.sha256(payload).hexdigest()}
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('Whole-file read_bytes used for digest')):
            storage.save_dataset(self.data, dataset)
            loaded = storage.load_dataset(dataset)
            self.assertEqual(storage.volume_cache(self.directory, scalar), opaque_cache)
        np.testing.assert_array_equal(loaded.arrays['large_values'], self.data.arrays['large_values'])

    def test_array_corruption_rejected_before_numpy_loading(self):
        manifest_path = storage.save_dataset(self.data, self.directory / 'dataset')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        # Keep the .npy layout and file size unchanged, but change one value byte.
        name = 'atomic_numbers'
        path = manifest_path.parent / manifest['arrays'][name]['path']
        with path.open('r+b') as stream:
            stream.seek(-1, 2)
            value = stream.read(1)
            stream.seek(-1, 2)
            stream.write(bytes([value[0] ^ 1]))
        with patch.object(np, 'load', side_effect=AssertionError('Corrupted array reached np.load')):
            with self.assertRaisesRegex(ValueError, 'Array checksum mismatch: atomic_numbers'):
                storage.load_dataset(manifest_path.parent)

    def test_vdb_digest_parity_and_corruption_rejection(self):
        path = self.directory / 'display.vdb'
        payload = bytes(range(256)) * 8192 + b'vdb-byte-parity'
        path.write_bytes(payload)
        scalar = {'vdb': path.name, 'vdb_sha256': hashlib.sha256(payload).hexdigest()}
        self.assertEqual(storage.volume_cache(self.directory, scalar), path)
        with path.open('r+b') as stream:
            stream.seek(1048576)
            value = stream.read(1)
            stream.seek(1048576)
            stream.write(bytes([value[0] ^ 1]))
        with self.assertRaisesRegex(ValueError, 'Volume cache checksum mismatch'):
            storage.volume_cache(self.directory, scalar)

    def test_digest_empty_and_multichunk_files_match_legacy_digest(self):
        for name, payload in [('empty', b''), ('multi', bytes(range(256)) * 8192 + b'end')]:
            with self.subTest(file=name):
                path = self.directory / name
                path.write_bytes(payload)
                self.assertEqual(storage._file_sha256(path), hashlib.sha256(payload).hexdigest())

    def test_optional_vdb_digest_contract_is_preserved(self):
        path = self.directory / 'without-digest.vdb'
        path.write_bytes(b'Native readability is validated separately by Blender')
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('Optional checksum unexpectedly read')):
            self.assertEqual(storage.volume_cache(self.directory, {'vdb': path.name}), path)


if __name__ == '__main__':
    unittest.main()
