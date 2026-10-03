import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.gaussian_log import energy_events, inspect_log, read_log, select_energy, summarize_jobs
from qcblender.data import load_dataset, save_dataset

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
DATA = Path(__file__).parent / 'data/cclib'


class GaussianLog(unittest.TestCase):
    def test_preview_matches_real_multijob_import_without_geometry_inheritance(self):
        path = input_path('log-examples/water_neutral_nbo_opt_freq.out')
        preview = inspect_log(path)
        self.assertGreaterEqual(len(preview['jobs']), 2)
        for index in range(len(preview['jobs'])):
            try:
                data = read_log(path, index)
            except ValueError as error:
                self.assertIn('explicit geometry', str(error))
            else:
                self.assertEqual(preview['jobs'], data.metadata['jobs'])
                self.assertEqual(preview['source']['sha256'], data.metadata['source']['sha256'])
                self.assertEqual(data.metadata['selected_job'], index)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            missing = Path(directory) / 'missing.log'
            missing.write_text(' # HF/STO-3G\n\n Error termination\n', encoding='utf-8')
            job = inspect_log(missing)['jobs'][0]
            self.assertEqual(job['status'], 'failed')
            self.assertFalse(job['explicit_geometry'])
            with self.assertRaisesRegex(ValueError, 'explicit geometry'):
                read_log(missing)
        self.assertEqual(summarize_jobs([' # HF/STO-3G\n'])[0]['status'], 'incomplete')

    @classmethod
    def setUpClass(cls):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        for record in json.loads((DATA / 'sources.json').read_text(encoding='utf-8')):
            assert hashlib.sha256((DATA / record['file']).read_bytes()).hexdigest() == record['sha256']

    def test_pre_scf_failure_and_truncation_preserve_job_identities(self):
        lines = [
            ' Batch preamble\n', ' Entering Gaussian System, Link 0=g16\n',
            ' # HF/STO-3G\n', '\n', ' Error termination via Lnk1e\n',
            ' Entering Gaussian System, Link 0=g16\n',
            ' # MP2/6-31G\n', '\n',
            ' Entering Gaussian System, Link 0=g16\n',
            ' # B3LYP/STO-3G\n', '\n', ' Error termination via Lnk1e\n',
            ' Entering Gaussian System, Link 0=g16\n',
            ' # B3LYP/6-31G\n', '\n',
            ' SCF Done: E(RB3LYP) = -76.0 A.U.\n',
            ' Normal termination of Gaussian\n',
            ' Link1:  Proceeding to internal job step number 2.\n',
            ' # HF/STO-3G\n', '\n',
        ]
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = Path(directory) / 'segments.log'
            path.write_text(''.join(lines), encoding='utf-8')
            jobs = inspect_log(path)['jobs']
        self.assertEqual([job['status'] for job in jobs],
                         ['failed', 'incomplete', 'failed', 'normal', 'incomplete'])
        self.assertEqual([job['route'] for job in jobs],
                         ['# HF/STO-3G', '# MP2/6-31G', '# B3LYP/STO-3G',
                          '# B3LYP/6-31G', '# HF/STO-3G'])
        self.assertEqual([(job['line_start'], job['line_end']) for job in jobs],
                         [(1, 5), (6, 8), (9, 12), (13, 17), (18, 20)])
        self.assertEqual([len(job['energies']) for job in jobs], [0, 0, 0, 1, 0])
        energy = jobs[3]['energies'][0]
        self.assertEqual(energy['job_id'], 'job4')
        self.assertEqual(energy['evaluation_id'], 'job4:eval1')
        self.assertEqual(energy['line_start'], 16)
        self.assertEqual(energy['line_end'], 16)
        self.assertEqual(energy['calculation_status'], 'normal')
        self.assertFalse(any(job['explicit_geometry'] for job in jobs))

    def test_real_selected_job_after_failed_truncated_and_normal_runs(self):
        healthy = (DATA / 'water_mp2.log').read_text(encoding='utf-8')
        standalone = read_log(DATA / 'water_mp2.log')
        failed = (' Entering Gaussian System, Link 0=g16\n'
                  ' # B3LYP/6-31G\n\n Error termination via Lnk1e\n')
        truncated = failed.rsplit(' Error termination', 1)[0]
        for prefix, statuses in [(failed, ['failed', 'normal']),
                                 (truncated, ['incomplete', 'normal']),
                                 (failed + truncated + failed,
                                  ['failed', 'incomplete', 'failed', 'normal']),
                                 (healthy, ['normal', 'normal']),
                                 (healthy.partition('\n')[2], ['normal', 'normal'])]:
            with self.subTest(statuses=statuses):
                with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
                    path = Path(directory) / 'concatenated.log'
                    path.write_text(prefix + healthy, encoding='utf-8')
                    jobs = inspect_log(path)['jobs']
                    self.assertEqual([job['status'] for job in jobs], statuses)
                    selected_index = len(statuses) - 1
                    data = read_log(path, selected_index)
                    self.assertEqual(data.metadata['jobs'], jobs)
                    self.assertEqual(data.metadata['selected_job'], selected_index)
                    self.assertEqual(data.metadata['calculation_status'], 'normal')
                    self.assertEqual(data.metadata['method'], standalone.metadata['method'])
                    self.assertEqual(data.metadata['energy_selection']['status'], 'available')
                    np.testing.assert_array_equal(data.arrays['atomic_numbers'], standalone.arrays['atomic_numbers'])
                    np.testing.assert_array_equal(data.arrays['positions'], standalone.arrays['positions'])
                    offset = len(prefix.splitlines())
                    self.assertEqual(jobs[-1]['line_start'], offset + 1)
                    self.assertEqual(jobs[-1]['line_end'], offset + len(healthy.splitlines()))
                    self.assertEqual(len(data.metadata['energies']), len(standalone.metadata['energies']))
                    for actual, original in zip(data.metadata['energies'], standalone.metadata['energies']):
                        self.assertEqual(actual['job_id'], f'job{selected_index + 1}')
                        self.assertEqual(actual['line_start'], original['line_start'] + offset)
                        self.assertEqual(actual['line_end'], original['line_end'] + offset)
                        self.assertEqual(actual['method_ref'], original['method_ref'])
                        self.assertEqual(actual['value_hartree'], original['value_hartree'])
                        self.assertEqual(actual['raw_line'], original['raw_line'])
                    if statuses[0] != 'normal':
                        self.assertFalse(jobs[0]['explicit_geometry'])
                        self.assertEqual(jobs[0]['energies'], [])
                        with self.assertRaisesRegex(ValueError, 'explicit geometry'):
                            read_log(path, 0)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = Path(directory) / 'healthy-then-failed.log'
            path.write_text(healthy + failed, encoding='utf-8')
            self.assertFalse(inspect_log(path)['jobs'][1]['explicit_geometry'])
            with self.assertRaisesRegex(ValueError, 'explicit geometry'):
                read_log(path, 1)

    def test_initial_run_banner_does_not_create_empty_job(self):
        for preamble in ['', ' Batch preamble\n\n',
                         ' Entering Gaussian System, Link 0=g16\n\n']:
            lines = (preamble + ' Entering Gaussian System, Link 0=g16\n'
                     ' # HF/STO-3G\n\n Error termination via Lnk1e\n').splitlines(keepends=True)
            jobs = summarize_jobs(lines)
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]['line_start'], 1)
            self.assertEqual(jobs[0]['line_end'], len(lines))
            self.assertEqual(jobs[0]['status'], 'failed')

    def test_missing_first_banner_keeps_observed_calculation_separate(self):
        healthy = (' Entering Gaussian System, Link 0=g16\n'
                   ' # HF/STO-3G\n\n SCF Done: E(RHF) = -75.0 A.U.\n'
                   ' Normal termination of Gaussian\n')
        for prefix, status in [('# MP2/6-31G\n\n', 'incomplete'),
                               (' SCF Done: E(RHF) = -74.0 A.U.\n', 'incomplete'),
                               (' Error termination via Lnk1e\n', 'failed'),
                               (' Standard orientation:\n', 'incomplete')]:
            with self.subTest(prefix=prefix):
                jobs = summarize_jobs((prefix + healthy).splitlines(keepends=True))
                self.assertEqual([job['status'] for job in jobs], [status, 'normal'])
                self.assertEqual(jobs[0]['line_end'], len(prefix.splitlines()))
                self.assertEqual(jobs[1]['line_start'], len(prefix.splitlines()) + 1)
                self.assertEqual(jobs[1]['route'], '# HF/STO-3G')
                self.assertEqual(jobs[1]['energies'][0]['value_hartree'], -75.0)

    def test_mp2_and_ccsdt_keep_reference_correction_and_target(self):
        mp2 = read_log(DATA / 'water_mp2.log')
        energies = mp2.metadata['energies']
        target = [e for e in energies if e['role'] == 'target']
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0]['method'], 'MP2')
        self.assertEqual(mp2.metadata['energy_selection']['status'], 'available')
        self.assertEqual(target[0]['archive_consistency'], 'matched')
        self.assertEqual(target[0]['line_start'], 342)
        self.assertAlmostEqual(target[0]['value_hartree'], -75.002282127454, places=11)
        self.assertTrue(any(e['kind'] == 'correlation_correction' for e in energies))
        self.assertTrue(any(e['role'] == 'reference' for e in energies))
        cc = read_log(DATA / 'water_ccsdt.log')
        targets = [e for e in cc.metadata['energies'] if e['role'] == 'target']
        self.assertEqual([e['method'] for e in targets], ['CCSD(T)'])
        self.assertAlmostEqual(targets[0]['value_hartree'], -75.017760422)
        self.assertEqual(targets[0]['archive_consistency'], 'matched')
        self.assertEqual(len([e for e in cc.metadata['energies'] if e['role'] == 'iteration']), 7)
        truncated = energy_events([' SCF Done:  E(RHF) = -75.0 A.U.\n'], 1, 'job1', '# MP2/STO-3G', 'failed')
        self.assertEqual(truncated[0]['role'], 'reference')
        self.assertFalse(any(e['role'] == 'target' for e in truncated))
        self.assertEqual(select_energy(truncated, 'failed')['status'], 'unavailable')

    def test_wrapped_archive_rounding_conflict_and_ambiguous_evaluations(self):
        lines = [' SCF Done: E(RHF) = -75.123456789 A.U.\n',
                 ' 1\\1\\GINC-TEST\\HF=-75.1234\n', ' 568\\\\@\n']
        records = energy_events(lines, 1, 'job1', '# HF/STO-3G', 'normal')
        self.assertEqual(records[-1]['line_end'], 3)
        self.assertEqual(records[-1]['consistency'], 'matched')
        self.assertEqual(select_energy(records, 'normal')['status'], 'available')
        lines[-1] = ' 000\\\\@\n'
        conflict = energy_events(lines, 1, 'job1', '# HF/STO-3G', 'normal')
        self.assertEqual(select_energy(conflict, 'normal')['status'], 'conflicting')
        multiple = energy_events([lines[0], lines[0]], 1, 'job1', '# HF/STO-3G opt', 'normal')
        self.assertEqual(select_energy(multiple, 'normal')['status'], 'ambiguous')

    def test_td_excitation_and_direct_total_have_state_identity(self):
        data = read_log(DATA / 'dvb_td.out')
        records = data.metadata['energies']
        total = next(e for e in records if e['role'] == 'target')
        excitation = next(e for e in records if e['kind'] == 'excitation')
        self.assertEqual(total['state']['source_number'], 1)
        self.assertEqual(total['line_start'], 655)
        self.assertAlmostEqual(total['value_hartree'], -382.112205281)
        self.assertEqual(excitation['raw_unit'], 'eV')
        self.assertEqual(excitation['raw_value_text'], '5.3351')
        self.assertEqual(len([e for e in records if e['kind'] == 'excitation']), 5)
        unresolved = energy_events([' Excited State 2: Singlet-A 3.0 eV\n',
                                   ' Total Energy, E(TD-HF/TD-DFT) = -75.0\n'],
                                  1, 'job1', '# TD B3LYP/STO-3G', 'normal')
        self.assertIsNone(unresolved[-1]['state'])
        self.assertEqual(unresolved[-1]['role'], 'candidate')

    def test_dft_ir_mode_alignment_and_roundtrip(self):
        data = read_log(DATA / 'dvb_ir.out')
        self.assertEqual(data.arrays['mode_frequencies'].shape, (54,))
        self.assertEqual(data.arrays['mode_displacements'].shape, (54, 20, 3))
        self.assertEqual(data.arrays['mode_ir_intensities'].shape, (54,))
        np.testing.assert_allclose(np.linalg.norm(data.arrays['mode_display_displacements'], axis=2).max(axis=1), 1)
        self.assertEqual(data.metadata['dipole']['unit'], 'debye')
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            save_dataset(data, directory)
            restored = load_dataset(directory)
            self.assertEqual(restored.metadata, data.metadata)

    def test_link1_and_real_double_hybrid_local_examples(self):
        local = input_path('log-examples')
        self.assertTrue((local / 'water_neutral_nbo_opt_freq.out').is_file(), 'Run tools/fetch_log_examples.py')
        for record in json.loads((ROOT / 'tests/data/local-log-downloads.json').read_text(encoding='utf-8')):
            assert hashlib.sha256((local / record['file']).read_bytes()).hexdigest() == record['sha256']
        path = local / 'water_neutral_nbo_opt_freq.out'
        opt, freq = read_log(path, 0), read_log(path, 1)
        self.assertEqual(len(opt.metadata['jobs']), 2)
        self.assertNotIn('mode_frequencies', opt.arrays)
        self.assertEqual(freq.metadata['jobs'][1]['line_start'], 1091)
        np.testing.assert_allclose(freq.arrays['mode_frequencies'], [2169.7613, 4141.3837, 4392.5759])
        np.testing.assert_allclose(freq.arrays['dipole'], [0, 0, -1.7093])
        double = read_log(local / 'issue746-dsdpbep86.log')
        target = next(e for e in double.metadata['energies'] if e['role'] == 'target')
        self.assertEqual(target['method'], 'DSDPBEP86')
        self.assertEqual(target['archive_consistency'], 'matched')
        self.assertAlmostEqual(target['value_hartree'], -852.43369150131, places=10)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            partial = Path(directory) / 'truncated.log'
            partial.write_text(''.join(path.read_text(encoding='utf-8').splitlines(keepends=True)[:-5]), encoding='utf-8')
            incomplete = read_log(partial, 1)
            self.assertEqual(incomplete.metadata['jobs'][0]['status'], 'normal')
            self.assertEqual(incomplete.metadata['calculation_status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
