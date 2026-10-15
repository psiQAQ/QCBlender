"""Source summaries use metadata dimensions, never evaluated scientific values."""
import copy
import unittest

from qcblender.object_summary import array_descriptors, summarize_object


class ObjectSummary(unittest.TestCase):
    def setUp(self):
        self.context = {'is_qc': True, 'bound': True, 'object': 'Water', 'view_type': 'atoms'}
        self.meta = {'source': {'filename': 'water.log', 'parser': 'fixture', 'sha256': 'a' * 64},
                     'selected_job': 1, 'jobs': [{}, {}], '_atom_count': 3,
                     'method': 'B3LYP', 'basis_name': '6-31G*', 'coordinate_unit': 'angstrom',
                     'calculation_status': 'complete'}

    def rows(self, result, group='short'):
        return {row['key']: row for row in result[group]}

    def categories(self, result):
        return {category['key']: category for category in result['categories']}

    def test_empty_selection_and_ordinary_object_never_inherit_metadata(self):
        for context in ({}, {'object': 'Cube', 'bound': True}):
            self.assertEqual(summarize_object(context, self.meta),
                             {'available': False, 'state': 'empty', 'short': [], 'details': [], 'categories': []})

    def test_source_atom_total_and_calculation_are_not_display_mesh_counts(self):
        result = summarize_object(self.context, self.meta,
                                  {'atomic_numbers': {'shape': [15], 'dtype': '<i4'}})
        self.assertEqual(self.rows(result)['atom_count']['value'], 15)
        self.assertEqual(self.rows(result)['calculation']['value'], '2 / 2')
        self.assertEqual(self.rows(result, 'details')['method']['value'], 'B3LYP')
        self.assertEqual(result['state'], 'ready')

    def test_missing_cache_error_and_unbound_are_distinct(self):
        for meta, bound, state in (({}, True, 'uncached'), ({'error': 'missing manifest'}, True, 'error'),
                                    ({}, False, 'unbound')):
            result = summarize_object(dict(self.context, bound=bound), meta)
            self.assertEqual(result['state'], state)
            self.assertIsNone(self.rows(result)['atom_count']['value'])
            self.assertIsNone(self.rows(result)['source']['value'])
            self.assertTrue(all(category['count'] is None for category in result['categories']))

    def test_xyz_optimization_irc_use_explicit_current_indices(self):
        cases = [({'xyz_frame': 2}, {'trajectory': {'frames': [{}, {}, {}]}}, 'xyz', '2 / 3'),
                 ({'optimization_step': 7}, {'optimization': {'steps': [{}] * 10}}, 'optimization', '7 / 10'),
                 ({'irc_step': 3}, {'analysis': {'kind': 'IRC', 'steps': [{}] * 4}}, 'irc', '3 / 4')]
        for context, meta, key, expected in cases:
            with self.subTest(key=key):
                result = summarize_object(dict(self.context, **context), dict(self.meta, **meta))
                self.assertEqual(self.rows(result)[key]['value'], expected)
        result = summarize_object(self.context, dict(self.meta, xyz_frames=[{'frame': 1}]))
        self.assertEqual(self.rows(result)['xyz']['value'], '1 / 1')

    def test_fields_preserve_units_dimensions_and_report_omitted_count(self):
        fields = [{'quantity': 'density', 'unit': 'e/bohr^3', 'array': f'field_{i}', 'shape': [8, 9, 10]}
                  for i in range(1000)]
        meta = dict(self.meta, fields=fields)
        descriptors = {'field_0': {'shape': [8, 9, 10], 'dtype': '<f8', 'path': 'do-not-open.npy'}}
        original = copy.deepcopy((meta, descriptors))
        category = self.categories(summarize_object(self.context, meta, descriptors, limit=3))['fields']
        self.assertEqual((category['count'], len(category['items']), category['omitted']), (1000, 3, 997))
        self.assertEqual(category['items'][0]['shape'], [8, 9, 10])
        self.assertEqual(category['items'][0]['unit'], 'e/bohr^3')
        self.assertIsNone(category['items'][1]['dtype'])
        self.assertEqual((meta, descriptors), original)
        self.assertNotIn('valid_sample_count', str(category))

    def test_orbitals_modes_and_trajectory_counts_from_descriptors(self):
        meta = dict(self.meta, orbitals={'kind': 'unrestricted', 'norba': 5, 'norbb': 4, 'energy_unit': 'hartree'},
                    modes={'frequency_unit': 'cm^-1', 'ir_unit': 'km/mol'},
                    trajectory={'kind': 'xyz', 'frames': [{}] * 12, 'coordinate_unit': 'angstrom'})
        descriptors = {key: {'shape': shape, 'dtype': '<f8'} for key, shape in
                       [('mo_coeffs', [5, 9]), ('mo_energies', [9]), ('mode_frequencies', [3]),
                        ('mode_displacements', [3, 3, 3]), ('mode_ir_intensities', [3]),
                        ('trajectory_positions', [12, 3, 3])]}
        categories = self.categories(summarize_object(self.context, meta, descriptors))
        self.assertEqual(categories['orbitals']['count'], 9)
        self.assertEqual(categories['vibrations']['count'], 3)
        self.assertEqual(categories['vibrations']['items'][0]['unit'], 'cm^-1')
        self.assertEqual(categories['trajectories']['items'][0]['shape'], [12, 3, 3])
        self.assertEqual(categories['trajectories']['items'][0]['value'], 12)

    def test_external_tables_report_counts_without_returning_numerical_records(self):
        meta = dict(self.meta, analysis={'kind': 'ESP', 'extrema_unit': 'kcal/mol', 'area_unit': 'angstrom^2',
                                        'extrema': [{'value': 12345}] * 100, 'area_bins': [{}] * 25})
        category = self.categories(summarize_object(self.context, meta))['external_analysis']
        self.assertEqual(category['count'], 1)
        rows = {row['key']: row for row in category['items']}
        self.assertEqual(rows['extrema']['value'], 100)
        self.assertEqual(rows['area_bins']['unit'], 'angstrom^2')
        self.assertNotIn('12345', str(category))

    def test_nbo_tables_are_separate_from_canonical_orbitals(self):
        meta = dict(self.meta, analysis={'kind': 'NBO', 'orbitals': [{}] * 6, 'interactions': [{}] * 30,
                                        'orbital_energy_unit': 'hartree', 'interaction_energy_unit': 'kcal/mol'})
        categories = self.categories(summarize_object(self.context, meta))
        self.assertEqual(categories['orbitals']['count'], 0)
        rows = {row['key']: row for row in categories['external_analysis']['items']}
        self.assertEqual(rows['orbitals']['value'], 6)
        self.assertEqual(rows['interactions']['unit'], 'kcal/mol')

    def test_irc_is_a_trajectory_not_an_external_analysis_table(self):
        meta = dict(self.meta, analysis={'kind': 'IRC', 'steps': [{}] * 3, 'coordinate_unit': 'angstrom'})
        categories = self.categories(summarize_object(self.context, meta))
        self.assertEqual(categories['trajectories']['items'][0]['value'], 3)
        self.assertEqual(categories['external_analysis']['count'], 0)
        self.assertEqual(categories['external_analysis']['items'], [])

    def test_profile_reports_sample_dimensions_and_original_field_unit(self):
        meta = dict(self.meta, profile={'sample_count': 50, 'field': {'unit': 'bohr^-3/2'}})
        descriptors = {'profile_values': {'shape': [50], 'dtype': '<f8'}}
        category = self.categories(summarize_object(self.context, meta, descriptors))['fields']
        self.assertEqual(category['items'][0]['value'], 50)
        self.assertEqual(category['items'][0]['unit'], 'bohr^-3/2')
        self.assertEqual(category['items'][0]['shape'], [50])

    def test_failed_binding_never_reuses_scientific_descriptors(self):
        descriptors = {'atomic_numbers': {'shape': [999], 'dtype': '<i4'}}
        result = summarize_object(self.context, {'error': 'broken'}, descriptors)
        self.assertIsNone(self.rows(result)['atom_count']['value'])
        self.assertEqual(self.rows(result, 'details')['error']['value'], 'broken')

    def test_invalid_descriptors_are_not_trusted_and_paths_are_discarded(self):
        records = {'ok': {'shape': [1, 2], 'dtype': '<f8', 'path': 'absent.npy'},
                   'bool': {'shape': [True], 'dtype': '<f8'},
                   'negative': {'shape': [-1], 'dtype': '<f8'},
                   'deep': {'shape': [1] * 5, 'dtype': '<f8'},
                   'dtype': {'shape': [2], 'dtype': None}, 'not_record': [3]}
        self.assertEqual(array_descriptors(records), {'ok': {'shape': (1, 2), 'dtype': '<f8'}})

    def test_limit_and_strings_are_bounded(self):
        meta = dict(self.meta, fields=[{'quantity': 'x' * 10000}] * 1000)
        for limit, expected in ((999, 16), (0, 1), ('bad', 6)):
            fields = self.categories(summarize_object(self.context, meta, limit=limit))['fields']
            self.assertEqual(len(fields['items']), expected)
            self.assertEqual(len(fields['items'][0]['value']), 256)


if __name__ == '__main__':
    unittest.main()
