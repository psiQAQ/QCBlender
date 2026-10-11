"""Record selection ranges at the Blender custom-property boundary."""
import unittest
from types import SimpleNamespace

from qcblender.blender.record_ranges import refresh_record_ranges


class PropertyUI(dict):
    def update(self, **kwargs):
        super().update(kwargs)


class Object(dict):
    def __init__(self, **values):
        super().__init__(values)
        self.ui = {}

    def id_properties_ui(self, name):
        return self.ui.setdefault(name, PropertyUI())


class RecordRanges(unittest.TestCase):
    def test_external_record_rows_use_the_current_display_layer(self):
        obj = Object(qc_analysis_role='esp_minimum', qc_analysis_index=40)
        meta = {'analysis': {'extrema': [
            {'kind': 'maximum', 'serial': 9},
            {'kind': 'minimum', 'serial': 20},
            {'kind': 'minimum', 'serial': 77}]}}
        refresh_record_ranges(obj, meta)
        self.assertEqual(obj['qc_analysis_index'], 2)
        self.assertEqual(obj.ui['qc_analysis_index'],
                         {'min': 1, 'max': 2, 'soft_min': 1, 'soft_max': 2})
        self.assertEqual(meta['analysis']['extrema'][2]['serial'], 77)

    def test_nbo_rows_have_independent_ranges_and_refresh_after_count_changes(self):
        obj = Object(qc_view_kind='nbo', qc_nbo_index=15, qc_e2_index=-5)
        meta = {'analysis': {'orbitals': [{'number': 2}, {'number': 7}, {'number': 20}],
                             'interactions': [{'donor': 2, 'acceptor': 20}]}}
        refresh_record_ranges(obj, meta)
        self.assertEqual((obj['qc_nbo_index'], obj['qc_e2_index']), (3, 1))
        self.assertEqual(obj.ui['qc_nbo_index']['max'], 3)
        self.assertEqual(obj.ui['qc_e2_index']['max'], 1)
        meta['analysis']['orbitals'] = []
        refresh_record_ranges(obj, meta)
        self.assertEqual(obj['qc_nbo_index'], 1)
        self.assertEqual(obj.ui['qc_nbo_index']['max'], 1)

    def test_mayer_atom_numbers_use_source_atom_count_without_changing_identity(self):
        obj = Object(qc_analysis_role='irc_mayer', qc_pair_a=4, qc_pair_b=500)
        refresh_record_ranges(obj, {'_atom_count': 8})
        self.assertEqual((obj['qc_pair_a'], obj['qc_pair_b']), (4, 8))
        self.assertEqual(obj.ui['qc_pair_a']['max'], 8)

    def test_refresh_does_not_create_missing_selectors_or_change_source_filters(self):
        obj = Object(qc_analysis_role='ets_nocv', source_number=77)
        refresh_record_ranges(obj, {'analysis': {'pairs': [{'pair': 77, 'spin': 'Alpha'}]}})
        self.assertEqual(obj, {'qc_analysis_role': 'ets_nocv', 'source_number': 77})
        self.assertEqual(obj.ui, {})

    def test_area_path_pair_and_aim_rows_keep_layer_specific_limits(self):
        cases = [
            ('esp_area', {'area_bins': [{}, {}, {}]}, 3),
            ('aim_paths', {'paths': [{}]}, 1),
            ('ets_nocv', {'pairs': [{'pair': 2}, {'pair': 20}]}, 2),
            ('aim_N', {'critical_points': [{'type': 'C'}, {'type': 'N'}, {'type': 'N'}]}, 2),
            ('aim_F', {'critical_points': [{'type': 'C'}]}, 1),
        ]
        for role, analysis, expected in cases:
            with self.subTest(role=role):
                obj = Object(qc_analysis_role=role, qc_analysis_index=30)
                refresh_record_ranges(obj, {'analysis': analysis})
                self.assertEqual(obj['qc_analysis_index'], expected)
                self.assertEqual(obj.ui['qc_analysis_index']['max'], expected)

    def test_bound_atom_view_ranges_are_private_and_preserve_last_atom_all(self):
        first = SimpleNamespace(item_type='SOCKET', in_out='INPUT', socket_type='NodeSocketInt',
                                name='First Atom (1-based)', identifier='first', min_value=0, max_value=999)
        last = SimpleNamespace(item_type='SOCKET', in_out='INPUT', socket_type='NodeSocketInt',
                               name='Last Atom (0 = all)', identifier='last', min_value=0, max_value=999)
        style = SimpleNamespace(item_type='SOCKET', in_out='INPUT', socket_type='NodeSocketInt',
                                name='Style (0 ball-stick, 1 space-fill, 2 bonds)', identifier='style',
                                min_value=0, max_value=999)

        class Tree(Object):
            users = 2

            def copy(self):
                import copy
                result = copy.deepcopy(self)
                result.users = 1
                return result

        shared = Tree(qc_view_graph=2)
        shared.interface = SimpleNamespace(items_tree=[first, last, style])
        modifier = Object(first=99, last=0, style=40)
        modifier.type, modifier.node_group = 'NODES', shared
        obj = Object(qc_view_kind='atoms', qc_dataset='bound-dataset')
        obj.modifiers = [modifier]
        refresh_record_ranges(obj, {'_atom_count': 3})
        self.assertIsNot(modifier.node_group, shared)
        self.assertEqual(first.max_value, 999)
        private = modifier.node_group.interface.items_tree
        self.assertEqual([(item.min_value, item.max_value) for item in private], [(1, 3), (0, 3), (0, 2)])
        self.assertEqual((modifier['first'], modifier['last'], modifier['style']), (3, 0, 2))


if __name__ == '__main__':
    unittest.main()
