"""CSV export checks against Dataset values and source records."""
import csv
import hashlib
import json
import os
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qcblender.data import Dataset, save_dataset
from qcblender.data_export import (available_exports, default_output_directory,
                                  documents_directory, export_dataset, export_report)
from qcblender.irc import import_irc, import_irc_mayer
from qcblender.readers import read_fchk

ROOT = Path(__file__).resolve().parents[1]


class DataExport(unittest.TestCase):
    def setUp(self):
        output = ROOT / 'outputs/runs/display-xyz-export/export-tests'
        output.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def export(self, data, kind, scope='ALL', filters=None, **kwargs):
        dataset = self.directory / ('dataset-' + kind)
        save_dataset(data, dataset)
        report = export_dataset(dataset, self.directory / 'results', kind, scope, filters, **kwargs)
        result = Path(report['directory'])
        metadata = json.loads((result / 'metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(metadata['scientific_metadata'], data.metadata)
        self.assertEqual(metadata['dataset_manifest_sha256'], hashlib.sha256((dataset / 'manifest.json').read_bytes()).hexdigest())
        tables = {}
        for record in metadata['files']:
            path = result / record['filename']
            self.assertEqual(record['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            with path.open(encoding='utf-8', newline='') as stream:
                tables[path.name] = list(csv.DictReader(stream))
            self.assertEqual(record['row_count'], len(tables[path.name]))
        return tables, metadata, report

    def test_real_ir_and_optimization_raw_values(self):
        from qcblender.gaussian_log import read_log
        from tools.local_inputs import input_path
        source = input_path('log-examples/water_neutral_nbo_opt_freq.out', Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)))
        data = read_log(source)
        self.assertIn('optimization', available_exports(data))
        vibrational = read_log(source, 1)
        self.assertIn('IR', available_exports(vibrational))
        tables, _, _ = self.export(vibrational, 'IR')
        self.assertEqual([float(row['frequency_cm-1']) for row in tables['ir.csv']], vibrational.arrays['mode_frequencies'].tolist())
        self.assertEqual([float(row['ir_intensity_km_mol']) for row in tables['ir.csv']], vibrational.arrays['mode_ir_intensities'].tolist())
        tables, _, _ = self.export(data, 'optimization')
        self.assertEqual([float(row['energy_hartree']) for row in tables['optimization_steps.csv']], [s['energy']['value_hartree'] for s in data.metadata['optimization']['steps']])
        self.assertEqual(len(tables['optimization_convergence.csv']), 16)
        self.assertTrue(all(row['unit'] == '' and 'Hartrees-Bohrs-Radians' in row['source_unit_system'] for row in tables['optimization_convergence.csv']))

    def test_real_irc_mayer_all_steps_and_all_pairs(self):
        path = import_irc(ROOT / 'tests/data/tutorial/P04/steps.csv')
        tables, _, _ = self.export(path, 'IRC')
        self.assertEqual([float(row['energy_hartree']) for row in tables['irc_steps.csv']], path.arrays['irc_energies'].tolist())
        mayer = import_irc_mayer(path, ROOT / 'tests/data/tutorial/P04/mayer-pyscf.csv')
        tables, _, _ = self.export(mayer, 'Mayer')
        rows = tables['mayer.csv']
        self.assertEqual(len(rows), mayer.arrays['mayer_orders'].size)
        for row in rows:
            pair = [int(row['atom_a_1based']), int(row['atom_b_1based'])]
            index = mayer.arrays['mayer_pairs'].tolist().index(pair)
            self.assertEqual(float(row['mayer_order']), mayer.arrays['mayer_orders'][int(row['step']) - 1, index])

    def paired(self):
        shape = (51, 41, 31)
        count = np.prod(shape)
        fields = [dict(array=name, valid_mask=name + '_valid', shape=list(shape),
                       origin=[1, 2, 3], steps=[[.2, .1, 0], [0, .3, .1], [.1, 0, .4]],
                       quantity=name, unit=unit) for name, unit in [('a', 'electron/bohr^4'), ('b', 'electron/bohr^3')]]
        return Dataset({'source': {'filename': '配对.cube', 'sha256': 'a' * 64},
                        'coordinate_unit': 'angstrom', 'fields': fields, 'analysis': {'kind': 'IGMH'}},
                       {'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3)),
                        'a': np.arange(count, dtype=float).reshape(shape), 'b': -np.arange(count, dtype=float).reshape(shape),
                        'a_valid': np.ones(shape, dtype=bool), 'b_valid': np.ones(shape, dtype=bool)})

    def test_paired_full_and_filtered_voxels_no_display_cap(self):
        data = self.paired()
        data.arrays['a_valid'].ravel()[10] = False
        tables, _, _ = self.export(data, 'paired')
        rows = tables['paired_voxels.csv']
        self.assertEqual(len(rows), data.arrays['a'].size - 1)
        self.assertGreater(len(rows), 50000)
        self.assertNotIn(10, [int(row['flat_index_0based']) for row in rows])
        row = rows[-1]
        index = np.array([int(row[k]) for k in ('i_0based', 'j_0based', 'k_0based')])
        np.testing.assert_allclose([float(row[k]) for k in ('x_angstrom', 'y_angstrom', 'z_angstrom')], np.array([1, 2, 3]) + index @ np.array(data.metadata['fields'][0]['steps']))
        tables, metadata, _ = self.export(data, 'paired', 'FILTERED', {'x_field': 0, 'y_field': 1, 'x_min': 8, 'x_max': 13})
        self.assertEqual([int(r['flat_index_0based']) for r in tables['paired_voxels.csv']], [8, 9, 11, 12, 13])
        self.assertEqual(metadata['filters']['x_field'], 0)

    def test_profile_invalid_empty_and_imaginary_raw_frequency(self):
        data = self.paired()
        data.metadata['profile'] = {'field': {'unit': 'hartree'}}
        data.arrays.update(profile_distance=np.array([0., 1., 2.]), profile_positions=np.zeros((3, 3)),
                           profile_values=np.array([2., 0., 4.]), profile_valid=np.array([True, False, True]))
        tables, _, _ = self.export(data, 'profile')
        self.assertEqual(len(tables['profile.csv'][0]), 7)
        self.assertEqual(tables['profile.csv'][1]['value'], '')
        data.arrays.update(mode_frequencies=np.array([-100., 20.]), mode_ir_intensities=np.array([1., 3.]))
        tables, _, _ = self.export(data, 'IR')
        self.assertEqual((tables['ir.csv'][0]['frequency_cm-1'], tables['ir.csv'][0]['imaginary']), ('-100.0', '1'))

    def test_real_esp_original_percentage_and_source_intervals(self):
        from qcblender.analysis_data import import_esp
        reference = read_fchk(ROOT / 'tests/data/tutorial/P03/water-dimer.fchk')
        base = ROOT / 'tests/data/tutorial/P03/esp'
        data = import_esp(reference, base / 'surfanalysis.pdb', base / 'stdout.log', 'electron density 0.001 e/bohr^3', '', 'kcal/mol', '')
        bins = data.metadata['analysis']['area_bins']
        chosen = bins[len(bins) // 2]
        tables, _, _ = self.export(data, 'ESP_AREA', 'FILTERED', {'center_min': chosen['center'], 'center_max': chosen['center']})
        self.assertEqual(float(tables['esp_area.csv'][0]['source_percentage']), chosen['percentage'])
        self.assertEqual(float(tables['esp_area.csv'][0]['area']), chosen['area'])

    def test_cancel_failed_write_no_final_and_no_overwrite(self):
        data = self.paired()
        source = self.directory / 'source'
        save_dataset(data, source)
        results = self.directory / 'results'
        with self.assertRaisesRegex(RuntimeError, 'cancelled'):
            export_dataset(source, results, 'paired', cancelled=lambda: True)
        self.assertEqual(list(results.iterdir()), [])
        calls = 0
        def midway():
            nonlocal calls
            calls += 1
            return calls >= 4
        with self.assertRaisesRegex(RuntimeError, 'cancelled'):
            export_dataset(source, results, 'paired', cancelled=midway)
        self.assertEqual(list(results.iterdir()), [])
        with patch('qcblender.data_export.csv.writer', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError, 'disk full'):
                export_dataset(source, results, 'paired')
        self.assertEqual(list(results.iterdir()), [])
        token = '1' * 32
        first = export_dataset(source, results, 'paired', token=token)
        original = (Path(first['directory']) / 'metadata.json').read_bytes()
        with self.assertRaises(FileExistsError):
            export_dataset(source, results, 'paired', token=token)
        self.assertEqual((Path(first['directory']) / 'metadata.json').read_bytes(), original)
        with self.assertRaisesRegex(ValueError, 'changed'):
            export_report(dict(dataset=str(source), dataset_sha256='0' * 64, output_directory=str(results), kind='paired'), self.directory)

    def test_default_directory_uses_preference_blend_or_known_folder(self):
        absolute = str(self.directory)
        self.assertEqual(default_output_directory(absolute), self.directory)
        self.assertEqual(default_output_directory(blend_filepath=absolute + '/project.blend'), self.directory)
        self.assertEqual(default_output_directory(documents=lambda: self.directory), self.directory)
        with self.assertRaisesRegex(ValueError, 'absolute'):
            default_output_directory('relative')
        self.assertTrue(documents_directory().is_absolute())


if __name__ == '__main__':
    unittest.main()
