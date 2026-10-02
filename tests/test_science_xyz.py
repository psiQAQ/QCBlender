import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.data import load_dataset, save_dataset
from qcblender.geometry import scientific_geometry
from qcblender.measurements import measure, measurement_text
from qcblender.readers import read_source, infer_bonds

ROOT = Path(__file__).resolve().parents[1]


class XYZTests(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = Path(directory) / '中文.xyz'
            path.write_bytes(text.encode('utf-8'))
            return read_source(path)

    def test_multiframe_scientific_association_is_explicitly_rejected(self):
        from qcblender.association import compare_sources
        from qcblender.analysis_data import analysis_dataset, spatial_check
        multi = self.parse('2\nfirst\nH 0 0 0\nH 0.7 0 0\n2\nsecond\nH 0 0 0\nH 5 0 0\n')
        single = self.parse('2\nsingle\nH 0 0 0\nH 0.7 0 0\n')
        for reference, moving in ((multi, single), (single, multi), (multi, multi)):
            with self.assertRaisesRegex(ValueError, 'single-frame'):
                compare_sources(reference, moving)
        with self.assertRaisesRegex(ValueError, 'single-frame'):
            spatial_check([[0, 0, 0]], multi)
        with self.assertRaisesRegex(ValueError, 'single-frame'):
            analysis_dataset(multi, 'ETS-NOCV', [], {})
        self.assertEqual(compare_sources(single, single)['status'], 'geometry_matched')

    def test_single_native_angstrom_and_source(self):
        text = '2\n  中文注释  \nH 0 0 0\n1 0.123456789012345 0 0\n'
        data = self.parse(text)
        self.assertNotIn('trajectory', data.metadata)
        self.assertNotIn('orbitals', data.metadata)
        self.assertEqual(data.arrays['positions'][1, 0], 0.123456789012345)
        self.assertEqual(data.metadata['xyz_frames'][0]['comment'], '  中文注释  ')
        self.assertEqual(data.metadata['source']['sha256'], hashlib.sha256(text.encode()).hexdigest())

    def test_frames_blank_separators_geometry_bonds_and_roundtrip(self):
        first = '2\nfirst\nH 0 0 0\nH 0.7 0 0\n'
        second = '2\n第二帧\n1 0 0 0\n1 5 0 0\n'
        data = self.parse(first + '\n\n' + second)
        self.assertNotIn('optimization', data.metadata)
        self.assertNotIn('analysis', data.metadata)
        positions, record = scientific_geometry(data, 'trajectory', 2)
        self.assertEqual(record['step_record']['line_start'], 7)
        self.assertEqual(record['step_record']['line_end'], 10)
        self.assertEqual(record['step_record']['sha256'], hashlib.sha256(second.encode()).hexdigest())
        self.assertEqual(record['step_record']['comment'], '第二帧')
        self.assertFalse(positions.flags.writeable)
        distance = measure('DISTANCE', positions, [1, 2])
        self.assertEqual(distance, 5.)
        self.assertIn('XYZ Frame 2', measurement_text('DISTANCE', [1, 2], distance, record, 3))
        self.assertEqual(len(data.arrays['bonds']), 1)
        geometry = copy.deepcopy(data)
        geometry.arrays['positions'] = positions
        infer_bonds(geometry)
        self.assertEqual(len(geometry.arrays['bonds']), 0)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            save_dataset(data, directory)
            restored = load_dataset(directory)
            self.assertEqual(restored.metadata, data.metadata)
            np.testing.assert_array_equal(restored.arrays['trajectory_positions'], data.arrays['trajectory_positions'])
        for frame in (0, 3, True, None):
            with self.assertRaises(ValueError):
                scientific_geometry(data, 'trajectory', frame)

    def test_strict_invalid_sources(self):
        invalid = ['', '0\nempty\n', '1\n', '2\nx\nH 0 0 0\n',
                   '1\nx\nH 0 0 0 1\n', '1\nx\nX 0 0 0\n', '1\nx\n0 0 0 0\n',
                   '1\nx\n119 0 0 0\n', '1\nx\nH NaN 0 0\n', '1\nx\nH inf 0 0\n',
                   '1\nx\nH 1D0 0 0\n', '1\nx\n\n',
                   '1\nx\nH 0 0 0\n\n2\ntruncated\nH 0 0 0\n',
                   '1\nx\nH 0 0 0\n1\nx\nO 0 0 0\n',
                   '1\nx\nH 0 0 0\n2\nx\nH 0 0 0\nH 1 0 0\n']
        invalid += [f'1\n{keyword}=x\nH 0 0 0\n' for keyword in ('Properties', 'Lattice', 'pbc')]
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_bom_crlf_and_element_order(self):
        text = '\ufeff1\r\n 中文 \r\nH 0.123456789012345 0 0\r\n'
        data = self.parse(text)
        self.assertEqual(data.metadata['source']['sha256'], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(data.metadata['xyz_frames'][0]['sha256'], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(data.metadata['xyz_frames'][0]['comment'], ' 中文 ')
        with self.assertRaisesRegex(ValueError, 'element order'):
            self.parse('2\nx\nH 0 0 0\nO 1 0 0\n2\ny\nO 0 0 0\nH 1 0 0\n')

    def test_corrupt_trajectory_is_rejected(self):
        data = self.parse('1\nx\nH 0 0 0\n1\ny\nH 1 0 0\n')
        for change in ('positions', 'identity', 'lines'):
            damaged = copy.deepcopy(data)
            if change == 'positions':
                damaged.arrays['trajectory_positions'][0, 0, 0] = 2
            elif change == 'identity':
                damaged.metadata['trajectory']['frames'][1]['frame'] = 1
            else:
                damaged.metadata['trajectory']['frames'][1]['line_start'] = 1
            with self.assertRaises(ValueError):
                damaged.validate()

    def test_public_fixtures(self):
        folder = ROOT / 'tests/data/xyz'
        for filename, count in [('water-dimer.xyz', 1), ('p04-three-frames.xyz', 3)]:
            data = read_source(folder / filename)
            self.assertEqual(len(data.metadata['xyz_frames']), count)


if __name__ == '__main__':
    unittest.main()
