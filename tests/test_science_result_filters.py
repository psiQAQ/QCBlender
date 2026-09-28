"""Result browsing keeps source records intact and filters before sampling."""
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

from qcblender.external_fields import pair_cubes
from qcblender.external_results import (aim_points, aim_properties, esp_area, esp_extrema,
                                        ets_nocv_pairs)
from qcblender.result_filters import (area_selection, nbo_selection, nocv_selection,
                                      point_label, point_selection, scatter_report,
                                      scatter_selection)


ROOT = Path(__file__).resolve().parents[1]
SOURCES = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)) / 'outputs/v1-acceptance/sources'
C07 = SOURCES / 'c07-c09-research/phenol-2026-09-27/igmh'
C08 = SOURCES / 'multiwfn-local/C08'
C09 = SOURCES / 'multiwfn-local/C09'
NOCV = SOURCES / 'c10-c13/multiwfn-cobh3-20260927/COBH3-ETS-NOCV.txt'


class ResultFilters(unittest.TestCase):
    def test_full_valid_filter_precedes_deterministic_sampling(self):
        data = SimpleNamespace(metadata={'fields': [
            {'array': 'geometry', 'valid_mask': 'good'}, {'array': 'color', 'valid_mask': 'good'}]},
            arrays={'geometry': np.arange(12, dtype=float),
                    'color': np.arange(12, dtype=float) * -1,
                    'good': np.array([True] * 11 + [False])})
        first = scatter_selection(data, 1, 0, -8, -3, 3, 8, maximum=3)
        second = scatter_selection(data, 1, 0, -8, -3, 3, 8, maximum=3)
        self.assertEqual((first['matching_count'], first['displayed_count']), (6, 3))
        np.testing.assert_array_equal(first['points'], second['points'])
        np.testing.assert_array_equal(first['flat_indices'], [3, 5, 8])
        large = SimpleNamespace(metadata=data.metadata, arrays={
            'geometry': np.arange(100001, dtype=float),
            'color': -np.arange(100001, dtype=float),
            'good': np.ones(100001, dtype=bool)})
        capped = scatter_selection(large, 1, 0, -100000, 0, 0, 100000)
        self.assertEqual((capped['matching_count'], capped['displayed_count']), (100001, 50000))
        with self.assertRaisesRegex(ValueError, 'minimum exceeds maximum'):
            scatter_selection(data, x_min=1, x_max=0)

    def test_real_pair_worker_contract_and_source_preservation(self):
        if not all(path.is_file() for path in (C07 / 'dg_inter.cub', C07 / 'sl2r.cub')):
            self.skipTest('Real C07 Cube pair is required; set QCBLENDER_REFERENCE_ROOT')
        from qcblender.data import save_dataset

        data = pair_cubes(C07 / 'dg_inter.cub', C07 / 'sl2r.cub', 'IGMH',
                          'electron/bohr^4', 'electron/bohr^3')
        original = data.arrays[data.metadata['fields'][0]['array']].copy()
        output = ROOT / 'outputs/science-result-filters'
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as temporary:
            directory = Path(temporary)
            source = directory / 'source'
            save_dataset(data, source)
            import hashlib
            digest = hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest()
            request = {'dataset': str(source), 'dataset_sha256': digest,
                       'x_field': 1, 'y_field': 0, 'x_min': -.05, 'x_max': .05,
                       'y_min': 0, 'y_max': .05}
            report = scatter_report(request, directory)
            points = np.load(directory / 'scatter.npy', allow_pickle=False)
            self.assertEqual(len(points), report['displayed_count'])
            self.assertLessEqual(len(points), 50000)
            self.assertGreaterEqual(report['matching_count'], len(points))
            self.assertTrue(np.all((-0.05 <= points[:, 0]) & (points[:, 0] <= 0.05)))
            with self.assertRaisesRegex(ValueError, 'changed'):
                scatter_report(dict(request, dataset_sha256='0' * 64), directory)
        np.testing.assert_array_equal(data.arrays[data.metadata['fields'][0]['array']], original)

    def test_real_esp_and_nocv_record_selection(self):
        if not all(path.is_file() for path in (C08 / 'surfanalysis.pdb', C08 / 'stdout.log',
                                                C09 / 'CPs.pdb', C09 / 'CPprop.txt', NOCV)):
            self.skipTest('Real C08/C09/NOCV records are required; set QCBLENDER_REFERENCE_ROOT')
        esp = {'kind': 'ESP', 'extrema': esp_extrema(C08 / 'surfanalysis.pdb'),
               'area_bins': esp_area(C08 / 'stdout.log')}
        before = [dict(row) for row in esp['area_bins']]
        self.assertEqual(len(point_selection(esp, kind='maximum')), 11)
        self.assertEqual(len(point_selection(esp, kind='minimum')), 8)
        self.assertEqual(len(point_selection(esp, serial=1)), 2)
        area = area_selection(esp, -10, 10)
        self.assertEqual(len(area['indexes']), 4)
        self.assertLess(area['displayed_area'], area['total_area'])
        intervals = area_selection(esp, -10, 10, mode='source_interval')
        self.assertTrue(intervals['indexes'])
        self.assertTrue(all(esp['area_bins'][index]['end'] >= -10 and
                            esp['area_bins'][index]['begin'] <= 10
                            for index in intervals['indexes']))
        self.assertEqual(intervals['total_area'], area['total_area'])
        self.assertEqual(before, esp['area_bins'])
        cps = aim_points(C09 / 'CPs.pdb')
        props = aim_properties(C09 / 'CPprop.txt', {row['serial'] for row in cps})
        aim = {'kind': 'AIM', 'critical_points': cps,
               'properties': {str(number): value for number, value in props.items()}}
        low_density = point_selection(aim, kind='N', value_max=.4,
                                      value_key='Density of all electrons')
        self.assertTrue(low_density)
        self.assertTrue(all(props[cps[index]['serial']]['Density of all electrons'] <= .4
                            for index in low_density))
        with self.assertRaisesRegex(ValueError, 'absent or nonnumeric'):
            point_selection(aim, value_min=0, value_key='CP_type')
        rows = ets_nocv_pairs(NOCV, 'kcal/mol')
        analysis = {'kind': 'ETS-NOCV', 'pairs': rows}
        self.assertEqual(len(nocv_selection(analysis, pair=1, spin='Total')), 1)
        selected = nocv_selection(analysis, eigen_min=.4, eigen_side='positive',
                                  energy_max=-10, sort_by='pair_energy')
        self.assertTrue(all(rows[index]['positive_eigenvalue'] >= .4 and
                            rows[index]['pair_energy'] <= -10 for index in selected))

    def test_nbo_number_type_occupancy_and_donor_e2(self):
        analysis = {'kind': 'NBO', 'orbitals': [
            {'number': 1, 'type': 'LP', 'occupancy': 1.9},
            {'number': 2, 'type': 'BD*', 'occupancy': .1},
            {'number': 3, 'type': 'LP', 'occupancy': 1.8}],
            'interactions': [{'donor': 1, 'acceptor': 2, 'e2_kcal_mol': 10},
                             {'donor': 3, 'acceptor': 2, 'e2_kcal_mol': 4}]}
        result = nbo_selection(analysis, number=1, orbital_type='LP',
                               occupancy_min=1.85, donor=1, acceptor=2, e2_min=5)
        self.assertEqual(result, {'orbitals': [0], 'interactions': [0]})
        self.assertEqual(nbo_selection(analysis, orbital_type='BD*')['interactions'], [0, 1])
        before = [dict(row) for row in analysis['orbitals']]
        self.assertEqual(nbo_selection(analysis, orbital_sort='type')['orbitals'], [1, 0, 2])
        self.assertEqual(nbo_selection(analysis, orbital_sort='occupancy_desc')['orbitals'], [0, 2, 1])
        self.assertEqual(nbo_selection(analysis, interaction_sort='e2_desc')['interactions'], [0, 1])
        self.assertEqual(nbo_selection(analysis, interaction_sort='acceptor')['interactions'], [0, 1])
        reordered = dict(analysis, interactions=[dict(row) for row in analysis['interactions']])
        reordered['interactions'][0]['e2_kcal_mol'] = 1
        self.assertEqual(nbo_selection(reordered, interaction_sort='e2_desc')['interactions'], [1, 0])
        self.assertEqual(analysis['orbitals'], before)
        with self.assertRaisesRegex(ValueError, 'sort field'):
            nbo_selection(analysis, orbital_sort='energy')

    def test_recorded_esp_intervals_and_point_labels(self):
        esp = {'kind': 'ESP', 'extrema_unit': 'kcal/mol', 'area_bins': [
            {'begin': -2., 'end': -1., 'center': -1.5, 'area': 2., 'percentage': 20.},
            {'begin': -1., 'end': 0., 'center': -.5, 'area': 3., 'percentage': 30.},
            {'begin': 0., 'end': 1., 'center': .5, 'area': 5., 'percentage': 50.}]}
        original = [dict(row) for row in esp['area_bins']]
        self.assertEqual(area_selection(esp, -.25, .25)['indexes'], [])
        interval = area_selection(esp, -.25, .25, mode='source_interval')
        self.assertEqual(interval['indexes'], [1, 2])
        self.assertEqual((interval['total_area'], interval['displayed_area'],
                          interval['displayed_source_percentage']), (10., 8., 80.))
        self.assertEqual(esp['area_bins'], original)
        with self.assertRaisesRegex(ValueError, 'not recorded'):
            area_selection({'kind': 'ESP', 'area_bins': [
                {'begin': None, 'end': None, 'center': 0., 'area': 1., 'percentage': 100.}]},
                0, 1, mode='source_interval')
        self.assertEqual(point_label(esp, {'kind': 'minimum', 'serial': 4, 'value': -3.125}),
                         'minimum 4 | -3.125 kcal/mol')
        aim = {'kind': 'AIM', 'properties': {'7': {'Density of all electrons': .25}}}
        self.assertEqual(point_label(aim, {'type': 'N', 'serial': 7}, 'Density of all electrons'),
                         'N 7 | Density of all electrons: 0.25')
        self.assertEqual(point_label(aim, {'type': 'N', 'serial': 7}),
                         'N 7 | Density of all electrons: 0.25')


if __name__ == '__main__':
    unittest.main()
