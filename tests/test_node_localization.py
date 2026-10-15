"""Identity and edit-preservation contracts independent of the Blender runtime."""
import json
import types
import unittest

from qcblender.asset_catalog import CATEGORIES, catalog_id, catalog_text
from qcblender.blender.node_identity import (canonical_display, interface_socket,
    localize_tree, node_socket, remember_sockets, socket_name, socket_identity_signature,
    adopt_generated_copy, socket_display_override)


class Tree(dict):
    def __init__(self, name='QC Select Atoms'):
        super().__init__(qc_asset_id='qc.atom_selection.v1')
        self.name = name
        self.library = None
        self.nodes = []
        self.asset_data = None
        self.interface = types.SimpleNamespace(items_tree=[])

    def add_socket(self, name, identifier, direction='INPUT'):
        item = types.SimpleNamespace(name=name, identifier=identifier, in_out=direction,
            item_type='SOCKET', socket_type='NodeSocketFloat', default_value=.25, id_data=self)
        self.interface.items_tree.append(item)
        return item


class Sockets(list):
    def __getitem__(self, key):
        if isinstance(key, str):
            return next(item for item in self if item.name == key or item.identifier == key)
        return super().__getitem__(key)


class NodeLocalization(unittest.TestCase):
    def test_custom_socket_display_is_preserved_even_when_it_matches_a_ui_message(self):
        from qcblender.blender.parameters import socket_label, socket_item_label
        tree = Tree()
        custom = tree.add_socket('Workflow', 'custom')
        standard = tree.add_socket('Width', 'width')
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(socket_display_override(custom), 'Workflow')
        self.assertEqual(socket_label('Workflow'), 'Workflow')
        standard.name = 'Workflow'
        self.assertEqual(socket_item_label(standard), 'Workflow')
        self.assertEqual(socket_name(standard), 'Width')

    def test_noneditable_embedded_tree_is_not_mutated(self):
        tree = Tree()
        tree.is_editable = False
        tree.add_socket('Width', 'width')
        before = dict(tree)
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(dict(tree), before)
        self.assertEqual(tree.interface.items_tree[0].name, 'Width')

    def test_locale_roundtrip_keeps_roles_identifiers_values_and_user_rename(self):
        tree = Tree('QC Select Atoms.001')
        atom = tree.add_socket('First Atom (1-based)', 'Socket_1')
        geom = tree.add_socket('Geometry', 'Socket_2', 'OUTPUT')
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(tree.name, 'QC 选择原子.001')
        self.assertEqual(atom.name, '起始原子编号（从 1 开始）')
        self.assertEqual(socket_name(atom), 'First Atom (1-based)')
        self.assertIs(interface_socket(tree, 'Geometry', 'OUTPUT'), geom)
        original = json.loads(tree['qc_sockets'])
        atom.name = 'My preferred label'
        localize_tree(tree, 'en_US')
        self.assertEqual(atom.name, 'My preferred label')
        self.assertEqual(tree.name, 'QC Select Atoms.001')
        self.assertEqual(geom.name, 'Geometry')
        self.assertEqual(atom.default_value, .25)
        self.assertEqual(json.loads(tree['qc_sockets']), original)
        self.assertIs(interface_socket(tree, 'First Atom (1-based)'), atom)

    def test_group_node_and_group_io_use_the_right_interface_direction(self):
        tree = Tree()
        left = tree.add_socket('Geometry', 'in')
        right = tree.add_socket('Geometry', 'out', 'OUTPUT')
        localize_tree(tree, 'zh_HANS')
        for kind, is_output, identifier in [('GROUP', False, 'in'), ('GROUP', True, 'out'),
                                           ('GROUP_INPUT', True, 'in'), ('GROUP_OUTPUT', False, 'out')]:
            node = types.SimpleNamespace(type=kind, node_tree=tree if kind == 'GROUP' else None)
            item = types.SimpleNamespace(name='用户名称', identifier=identifier,
                                         is_output=is_output, node=node, id_data=tree)
            self.assertEqual(socket_name(item), 'Geometry')
            self.assertIs(node_socket(Sockets([item]), 'Geometry'), item)
        self.assertEqual(left.identifier, 'in')
        self.assertEqual(right.identifier, 'out')

    def test_old_graph_fallback_and_new_socket_preserve_existing_map(self):
        tree = Tree()
        item = tree.add_socket('Width', 'width')
        self.assertEqual(socket_name(item), 'Width')
        remember_sockets(tree)
        localize_tree(tree, 'zh_HANS')
        tree.add_socket('Height', 'height')
        remember_sockets(tree)
        self.assertEqual(json.loads(tree['qc_sockets']), {'Width': 'width', 'Height': 'height'})
        self.assertIs(node_socket(Sockets([item]), 'width'), item)
        self.assertIs(node_socket(Sockets([item]), 0), item)

    def test_signature_normalization_rejects_user_and_forged_changes(self):
        tree = Tree()
        item = tree.add_socket('Width', 'width')
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(canonical_display(tree, 'socket:width', item.name), 'Width')
        item.name = 'Scientific meaning changed'
        self.assertEqual(canonical_display(tree, 'socket:width', item.name), item.name)
        record = json.loads(tree['qc_node_locale'])
        record['display']['socket:width']['last'] = item.name
        tree['qc_node_locale'] = json.dumps(record)
        self.assertEqual(canonical_display(tree, 'socket:width', item.name), item.name)

    def test_node_labels_and_tree_names_preserve_user_edits(self):
        tree = Tree()
        node = Tree()
        node.name, node.label, node.type = 'Frame', 'Modes: displacement and animation', 'FRAME'
        tree.nodes.append(node)
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(node.label, '振动模式：位移与动画')
        self.assertEqual(node['qc_frame_role'], 'Modes: displacement and animation')
        tree.name, node.label = 'My graph', 'My explanation'
        localize_tree(tree, 'en_US')
        self.assertEqual((tree.name, node.label), ('My graph', 'My explanation'))

    def test_shared_and_cyclic_groups_do_not_recurse_forever(self):
        tree = Tree()
        node = types.SimpleNamespace(type='GROUP', name='Group', label='', node_tree=tree)
        tree.nodes.append(node)
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(tree.name, 'QC 选择原子')

    def test_unknown_future_metadata_fails_without_editing(self):
        tree = Tree()
        tree['qc_node_locale'] = '{"version": 999}'
        with self.assertRaisesRegex(ValueError, 'version'):
            localize_tree(tree, 'zh_HANS')
        self.assertEqual(tree.name, 'QC Select Atoms')

    def test_corrupt_or_stale_identity_map_is_not_hidden_by_localization(self):
        tree = Tree()
        tree.add_socket('Width', 'width')
        localize_tree(tree, 'zh_HANS')
        before = socket_identity_signature(tree)
        tree['qc_sockets'] = '{"Height": "width"}'
        self.assertNotEqual(socket_identity_signature(tree), before)
        tree['qc_sockets'] = '{"Width": "width"}'
        tree.interface.items_tree.clear()
        self.assertIsNotNone(socket_identity_signature(tree)[1])

    def test_known_plugin_copy_adopts_suffix_but_refresh_preserves_external_rename(self):
        tree = Tree()
        localize_tree(tree, 'en_US')
        tree.name += '.001'
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(tree.name, 'QC Select Atoms.001')
        adopt_generated_copy(tree)
        localize_tree(tree, 'zh_HANS')
        self.assertEqual(tree.name, 'QC 选择原子.001')
        tree.name = 'My copied graph'
        adopt_generated_copy(tree)
        localize_tree(tree, 'en_US')
        self.assertEqual(tree.name, 'My copied graph')

    def test_catalog_locale_changes_paths_but_never_uuid(self):
        lines = lambda language: [line.split(':') for line in catalog_text(language).splitlines()
                                  if line and not line.startswith(('#', 'VERSION'))]
        chinese, english = lines('zh_HANS'), lines('en_US')
        self.assertEqual([row[0] for row in chinese], [row[0] for row in english])
        self.assertEqual([row[0] for row in chinese], [catalog_id(path) for path in CATEGORIES])
        self.assertNotEqual([row[1] for row in chinese], [row[1] for row in english])


if __name__ == '__main__':
    unittest.main()
