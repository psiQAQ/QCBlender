import copy
from io import StringIO
import logging
from pathlib import Path
import tempfile
import unittest

from cclib.parser import Gaussian
import numpy as np

from qcblender.data import save_dataset, load_dataset
from qcblender.gaussian_log import read_log, summarize_jobs
from qcblender.optimization import optimization_records

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
SOURCE = input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)


class Optimization(unittest.TestCase):
    def test_real_steps_match_raw_geometry_energy_and_convergence(self):
        data = read_log(SOURCE)
        trajectory = data.metadata['optimization']
        steps = trajectory['steps']
        self.assertEqual(trajectory['status'], 'available')
        self.assertEqual([s['geometry_line_start'] for s in steps], [153, 477, 599, 721])
        self.assertEqual([s['energy']['line_start'] for s in steps], [200, 526, 648, 761])
        self.assertEqual([s['energy']['value_hartree'] for s in steps],
                         [-74.9643287914, -74.9649723283, -74.9659003010, -74.9659011806])
        lines = SOURCE.read_text().splitlines()
        for index, step in enumerate(steps):
            begin = step['geometry_line_start'] + 4
            raw_coords = [[float(x) for x in line.split()[-3:]] for line in lines[begin:begin + 3]]
            np.testing.assert_array_equal(data.arrays['optimization_positions'][index], raw_coords)
            self.assertEqual(len(step['convergence']), 4)
            self.assertIn('Hartrees-Bohrs-Radians', step['convergence_unit_system']['text'])
        self.assertEqual([s['status'] for s in steps], ['not_completed'] * 3 + ['converged'])
        self.assertEqual(steps[0]['convergence'][0]['value'], .029587)
        np.testing.assert_array_equal(data.arrays['positions'], data.arrays['optimization_positions'][-1])
        self.assertNotIn('optimization', read_log(SOURCE, 1).metadata)
        self.assertNotIn('optimization', read_log(ROOT / 'tests/data/cclib/water_mp2.log').metadata)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            save_dataset(data, directory)
            reopened = load_dataset(directory)
            self.assertEqual(reopened.metadata, data.metadata)
            np.testing.assert_array_equal(reopened.arrays['optimization_positions'], data.arrays['optimization_positions'])

    def test_partial_job_keeps_observed_steps_without_convergence_claim(self):
        lines = SOURCE.read_text().splitlines(keepends=True)
        for tail, status in [('', 'incomplete'), (' Error termination\n', 'failed')]:
            with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
                path = Path(directory) / 'partial.log'
                path.write_text(''.join(lines[:698]) + tail)
                data = read_log(path)
                steps = data.metadata['optimization']['steps']
                self.assertEqual(len(steps), 3)
                self.assertEqual(steps[-1]['calculation_status'], status)
                self.assertEqual(steps[-1]['status'], 'not_completed')
                self.assertEqual(steps[-1]['energy']['value_hartree'], -74.9659003010)
                self.assertNotIn('normally terminated', steps[-1]['energy_reason'])

    def test_association_rejects_ambiguous_steps_and_identity_changes(self):
        lines = SOURCE.read_text().splitlines(keepends=True)[:1090]
        parsed = Gaussian(StringIO(''.join(lines)), loglevel=logging.ERROR).parse()
        job = summarize_jobs(lines)[0]
        missing = copy.deepcopy(job)
        missing['energies'] = [e for e in missing['energies'] if e['line_start'] != 526]
        steps = optimization_records(lines, 1, missing, parsed)['steps']
        self.assertIsNone(steps[1]['energy'])
        ambiguous = copy.deepcopy(job)
        ambiguous['energies'].append(dict(ambiguous['energies'][1], id='extra'))
        self.assertEqual(optimization_records(lines, 1, ambiguous, parsed)['steps'][1]['energy_status'], 'ambiguous')
        duplicate = list(lines)
        duplicate[545] = duplicate[545].replace('number   2', 'number   1')
        self.assertEqual(optimization_records(duplicate, 1, job, parsed)['status'], 'unavailable')
        changed = list(lines)
        changed[157] = changed[157].replace('          8 ', '          7 ')
        self.assertNotEqual(changed[157], lines[157])
        with self.assertRaisesRegex(ValueError, 'identities'):
            optimization_records(changed, 1, job, parsed)
        for option in ('scan', 'restart', 'qst2', 'oniom'):
            unsupported = dict(job, route=job['route'] + ' ' + option)
            self.assertEqual(optimization_records(lines, 1, unsupported, parsed)['status'], 'unavailable')
        missing_geometry = list(lines)
        missing_geometry[476] = ' geometry omitted\n'
        self.assertEqual(optimization_records(missing_geometry, 1, job, parsed)['status'], 'unavailable')

    def test_no_symmetry_uses_input_orientation_and_invalid_storage_rejects(self):
        lines = SOURCE.read_text().splitlines(keepends=True)[:1090]
        # A format-boundary derivative of the real log: omit all standard tables.
        starts = [i for i, line in enumerate(lines) if line.strip() == 'Standard orientation:']
        for begin in reversed(starts):
            del lines[begin:begin + 9]
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = Path(directory) / 'input-only.log'
            path.write_text(''.join(lines))
            data = read_log(path)
            self.assertEqual(data.metadata['optimization']['status'], 'available')
            self.assertEqual(data.metadata['optimization']['steps'][0]['orientation'], 'Input orientation:')
            data.arrays['optimization_positions'] = data.arrays['optimization_positions'][:-1]
            with self.assertRaisesRegex(ValueError, 'coordinate arrays'):
                data.validate()


if __name__ == '__main__':
    unittest.main()
