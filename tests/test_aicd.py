import tempfile
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np

from qcblender.aicd import (anisotropy, current, field_direction, nearest_nodes,
                           parse_dump, remap, _source_bundle, _log_identity, FORMAT, UNIT)


def dump_text(points, tensors, weights):
    lines = [' Gitterpunkte:', ' 1 2 3']
    def rows(values):
        return [str(i+1)+' '+' '.join(f'{x:.12E}'.replace('E', 'D') for x in np.atleast_1d(row))
                for i, row in enumerate(values)]
    lines += rows(points)+[' Gewichtungsfaktoren:', ' 1']+rows(weights)
    for column in range(3):
        lines += [f' Stromdichtetensor, II= {column+1}', ' 1 2 3']+rows(tensors[:, :, column])
    return '\n'.join(lines)+'\n'


class AICDTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.path = Path(self.work.name)/'AICD.txt'
        self.tensors = np.arange(18, dtype=float).reshape(2, 3, 3)-5
        self.points = np.array([[0., 0., 0.], [1., 2., 3.]])
        self.text = dump_text(self.points, self.tensors, [0., .3])
        self.path.write_text(self.text)

    def test_columns_blocks_and_zero_weights(self):
        self.path.write_text(self.text+self.text)
        p, w, t, ids, blocks = parse_dump(self.path)
        np.testing.assert_array_equal(t, np.concatenate((self.tensors, self.tensors)))
        np.testing.assert_array_equal(ids, [[1, 1], [1, 2], [2, 1], [2, 2]])
        np.testing.assert_array_equal(w, [0., .3, 0., .3])
        self.assertEqual(blocks, 2)
        np.testing.assert_array_equal(current(t, [0, 0, 7]), t[:, :, 2])

    def test_incomplete_duplicate_and_nonfinite_rejected(self):
        for text in (self.text.rsplit('\n', 2)[0], self.text.replace('II= 2', 'II= 1'),
                     self.text.replace('1 0.000000000000D+00', '2 0.000000000000D+00', 1),
                     self.text.replace('0.000000000000D+00', 'NaN', 1)):
            with self.subTest(text=text[-50:]):
                self.path.write_text(text)
                with self.assertRaises(ValueError):
                    parse_dump(self.path)

    def test_field_and_proper_rotation(self):
        for b in ([0, 0, 0], [float('inf'), 0, 1], [1, 2]):
            with self.assertRaises(ValueError):
                field_direction(b)
        b = np.array([1., -2., 3.])
        np.testing.assert_allclose(current(self.tensors, -b), -current(self.tensors, b))
        np.testing.assert_allclose(current(self.tensors, b*1e300), current(self.tensors, b))
        q, _ = np.linalg.qr(np.array([[1., 2., 3.], [-4., 5., 1.], [2., 1., -3.]]))
        if np.linalg.det(q)<0:
            q[:, 0] *= -1
        rotated = q @ self.tensors @ q.T
        np.testing.assert_allclose(anisotropy(rotated), anisotropy(self.tensors), atol=1e-13)
        np.testing.assert_allclose(current(rotated, q@b), current(self.tensors, b)@q.T, atol=1e-13)
        np.testing.assert_allclose(current(self.tensors+self.tensors[::-1], b),
                                   current(self.tensors, b)+current(self.tensors[::-1], b))

    def test_nearest_nodes_against_exhaustive_non_cubic_grid(self):
        shape, origin, spacing = (3, 5, 7), np.array([-1., -.5, 2.]), .25
        nodes = np.indices(shape).reshape(3, -1).T*spacing+origin
        points = np.vstack((nodes[[0, 17, -1]], (nodes[0]+nodes[1])/2,
                            [[-10, -.12, 3], [30, 10, 5], [-100, 100, 2.75]],
                            np.random.default_rng(40).uniform([-2, -1, 1], [2, 2, 5], (80, 3))))
        indexes, distances = nearest_nodes(points, origin, spacing, shape)
        for i, point in enumerate(points):
            d = np.sum((nodes-point)**2, axis=1)
            chosen = np.lexsort((np.arange(len(nodes)), d))[:4]
            np.testing.assert_array_equal(indexes[i], chosen)
            np.testing.assert_allclose(distances[i], np.sqrt(d[chosen]))

    def test_map_values_before_tensors_and_preserve_invalid_nodes(self):
        points = np.array([[.1, .2, .3], [.2, .3, .4]])
        tensors = np.array([np.diag([1., 0., -1.]), np.diag([-1., 0., 1.])])
        a = anisotropy(tensors)
        shape, origin = (4, 3, 5), np.zeros(3)
        values, grid_t, mask = remap(points, tensors, a, origin, .5, shape)
        nodes = np.indices(shape).reshape(3, -1).T*.5
        accum, sums = np.zeros((len(nodes), 10)), np.zeros(len(nodes))
        for point, tensor, scalar in zip(points, tensors, a):
            dist = np.linalg.norm(nodes-point, axis=1)
            for node in np.lexsort((np.arange(len(nodes)), dist))[:4]:
                weight = 1/max(dist[node], 1e-8)
                accum[node] += np.r_[scalar, tensor.ravel()]*weight
                sums[node] += weight
        good = sums>0
        accum[good] /= sums[good, None]
        np.testing.assert_array_equal(mask.ravel(), good)
        np.testing.assert_allclose(values.ravel(), accum[:, 0])
        np.testing.assert_allclose(grid_t.reshape(-1, 9), accum[:, 1:])
        self.assertTrue(np.any(np.abs(values-anisotropy(grid_t.reshape(shape+(3, 3))))>1e-3))
        self.assertTrue(np.any(~mask))
        with self.assertRaises(MemoryError):
            remap(points, tensors, a, origin, .5, (1000, 1000, 1000), 32)

    def test_cancellation(self):
        with self.assertRaises(InterruptedError):
            remap(self.points, self.tensors, anisotropy(self.tensors), np.zeros(3), 1., (3, 3, 3), cancelled=lambda: True)

    def test_bound_source_identity_and_mismatch_rejection(self):
        # Minimal format fixture; this is not a scientific benchmark.
        route = '#p rb3lyp/6-31g(d) nmr=csgt iop(10/93=1)'
        inp = self.path.parent/'all.gjf'
        log = self.path.parent/'all.log'
        inp.write_text(route+'\n\nFixture\n\n0 1\nH 0 0 0\nH 0 0 1\n\n')
        text = ('Gaussian 16: ES64L-G16RevC.01\n'+route+'\n ------------------\n'
                ' Charge = 0 Multiplicity = 1\n Standard orientation:\n -----\n'
                ' Center Atomic Atomic Coordinates (Angstroms)\n Number Number Type X Y Z\n -----\n'
                ' 1 1 0 0.000000 0.000000 0.000000\n 2 1 0 0.000000 0.000000 1.000000\n -----\n'
                ' Writing AICD data to file "AICD.txt"\n Normal termination of Gaussian\n')
        text = text.replace(' Standard orientation:', text[text.index(' Standard orientation:'):text.index(' Writing AICD')].replace('Standard orientation:', 'Input orientation:')+' Standard orientation:')
        log.write_text(text)
        record = {'format':FORMAT, 'coordinate_unit':'bohr', 'response_unit':UNIT,
                  'job_index':0, 'component':'all', 'orbitals':[], 'files':{}}
        for role, path in [('tensor', self.path), ('log', log), ('input', inp)]:
            record['files'][role] = {'path':path.name, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        declaration = self.path.parent/'source.json'
        declaration.write_text(json.dumps(record))
        actual, paths = _source_bundle(declaration)
        numbers, positions, identity = _log_identity(log, inp, self.path, actual)
        np.testing.assert_array_equal(numbers, [1,1])
        np.testing.assert_array_equal(positions, [[0,0,0],[0,0,1]])
        self.assertEqual(identity['component'], 'all')
        inp.write_text(inp.read_text().replace('H 0 0 1', 'H 0 0 2'))
        with self.assertRaisesRegex(ValueError, 'coordinates differ'):
            _log_identity(log, inp, self.path, actual)
        inp.write_text(inp.read_text().replace('H 0 0 2', 'H 0 0 1'))
        for change in [dict(job_index=1), dict(component='pi'), dict(orbitals=[1])]:
            with self.assertRaises(ValueError):
                _log_identity(log, inp, self.path, {**actual, **change})
        for bad_text in [text.replace('Normal termination', 'Error termination'),
                         text.replace('AICD.txt', 'other.txt'), text.replace('nmr=csgt', 'nmr=giao')]:
            log.write_text(bad_text)
            with self.assertRaises(ValueError):
                _log_identity(log, inp, self.path, actual)
        with self.assertRaises(ValueError):
            _source_bundle(declaration)
        record['files']['tensor']['path'] = '../AICD.txt'
        declaration.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            _source_bundle(declaration)


if __name__ == '__main__':
    unittest.main()
