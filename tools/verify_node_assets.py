"""Run after verify_extension.py in the installed Blender extension profile."""
import importlib
import argparse
import json
import subprocess
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, default=ROOT / 'outputs/node-assets/report.json')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = args.report.parent
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.qcblender')
views = importlib.import_module('bl_ext.user_default.qcblender.blender.views')
identity = importlib.import_module('bl_ext.user_default.qcblender.blender.node_identity')
library_tools = importlib.import_module('bl_ext.user_default.qcblender.blender.asset_library')
catalog = importlib.import_module('bl_ext.user_default.qcblender.asset_catalog')


def vertices(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return np.array([v.co[:] for v in mesh.vertices])
    finally:
        evaluated.to_mesh_clear()


original = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'field')
directory = bpy.path.abspath(original['qc_dataset'])
first, second = views.field_view(directory), views.field_view(directory)
first_tree, second_tree = first.modifiers[0].node_group, second.modifiers[0].node_group
group = views.isosurface_group()
assert first_tree != second_tree
assert all(next(n for n in tree.nodes if n.type == 'GROUP').node_tree == group
           for tree in (first_tree, second_tree))
assert group.asset_data is None and first_tree.asset_data is None
assert not any(n.bl_idname == 'GeometryNodeObjectInfo' for n in group.nodes)
assert all(s.socket_type not in ('NodeSocketObject', 'NodeSocketCollection')
           for s in group.interface.items_tree if s.item_type == 'SOCKET')
assert all(s.default_value is None for s in group.interface.items_tree
           if s.item_type == 'SOCKET' and s.socket_type == 'NodeSocketMaterial')

baseline = vertices(first)
assert len(baseline) > 100
np.testing.assert_array_equal(baseline, vertices(second))
inputs = {identity.socket_name(s, second_tree): s.identifier for s in second_tree.interface.items_tree
          if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
second.modifiers[0][inputs['Isovalue']] = .1
assert 0 < len(vertices(second)) < len(baseline)
np.testing.assert_array_equal(baseline, vertices(first))
second.modifiers[0][inputs['Isovalue']] = .05
second.qc_settings.volume.location.x = 1.0
second.qc_settings.volume.update_tag()
shifted = vertices(second)
np.testing.assert_allclose(shifted.min(axis=0), baseline.min(axis=0) + [1, 0, 0], atol=2e-5)
np.testing.assert_allclose(shifted.max(axis=0), baseline.max(axis=0) + [1, 0, 0], atol=2e-5)
np.testing.assert_array_equal(baseline, vertices(first))

# Appending an asset to a second branch preserves the existing output connection.
output = next(n for n in first_tree.nodes if n.type == 'GROUP_OUTPUT')
existing = identity.node_socket(output.inputs, 'Geometry').links[0].from_socket
extra = first_tree.nodes.new('GeometryNodeGroup')
extra.node_tree = group
identity.node_socket(extra.inputs, 'Isovalue').default_value = .1
info = next(n for n in first_tree.nodes if n.bl_idname == 'GeometryNodeObjectInfo')
first_tree.links.new(info.outputs['Geometry'], identity.node_socket(extra.inputs, 'Volume'))
join = first_tree.nodes.new('GeometryNodeJoinGeometry')
first_tree.links.new(existing, join.inputs['Geometry'])
first_tree.links.new(identity.node_socket(extra.outputs, 'Geometry'), join.inputs['Geometry'])
first_tree.links.new(join.outputs['Geometry'], identity.node_socket(output.inputs, 'Geometry'))
assert len(vertices(first)) > len(baseline)
assert any(link.from_socket == existing for link in join.inputs['Geometry'].links)

# Library export contains no bound volume, source object or per-view material.
library = OUT / 'nodes.blend'
bpy.data.libraries.write(str(library), {group}, fake_user=True)
with bpy.data.libraries.load(str(library), link=False) as (source, target):
    assert not source.objects and not source.volumes and not source.materials
    target.node_groups = [group.name]
loaded = target.node_groups[0]
extra.node_tree = loaded
assert len(vertices(first)) > len(baseline)

# Language is display metadata, not topology, numeric defaults or geometry.
signature = library_tools._group_signature(group)
stable_inputs = json.loads(second_tree['qc_sockets'])
locale_geometry = vertices(second)
for language in ('en_US', 'zh_HANS', 'en_US'):
    for tree in (first_tree, second_tree, group, loaded):
        identity.localize_tree(tree, language)
    assert library_tools._group_signature(group) == signature
    assert json.loads(second_tree['qc_sockets']) == stable_inputs
    np.testing.assert_array_equal(vertices(second), locale_geometry)
    assert identity.interface_socket(second_tree, 'Isovalue').identifier == inputs['Isovalue']

# A numeric edit or additional node must still invalidate standard identity.
control = identity.interface_socket(group, 'Isovalue')
old_value = control.default_value
control.default_value = old_value + .013
assert library_tools._group_signature(group) != signature
control.default_value = old_value
added = group.nodes.new('ShaderNodeMath')
assert library_tools._group_signature(group) != signature
group.nodes.remove(added)
assert library_tools._group_signature(group) == signature

# Owner names survive subsequent switches while canonical lookup remains valid.
old_label = control.name
control.name = 'My preserved isovalue'
identity.localize_tree(group, 'zh_HANS')
assert control.name == 'My preserved isovalue'
assert identity.interface_socket(group, 'Isovalue') == control
assert library_tools._group_signature(group) != signature
control.name = old_label
identity.localize_tree(group, 'en_US')

# Both shipped libraries must contain all nine data-only, same-identity assets.
localized_signatures = {}
package_root = Path(views.__file__).resolve().parents[1]
for language in ('en_US', 'zh_HANS'):
    folder = package_root / 'assets' / language
    assert (folder / 'blender_assets.cats.txt').read_text(encoding='utf-8') == catalog.catalog_text(language)
    with bpy.data.libraries.load(str(folder / 'nodes.blend'), link=False) as (source, target):
        assert not source.objects and not source.volumes and not source.materials
        target.node_groups = list(source.node_groups)
    appended = tuple(group for group in target.node_groups if group is not None)
    assert {group.get('qc_asset_id') for group in appended} == set(catalog.ASSETS)
    assert all(str(group.asset_data.catalog_id) == catalog.catalog_id(catalog.ASSETS[group['qc_asset_id']][0])
               for group in appended)
    localized_signatures[language] = {group['qc_asset_id']: library_tools._group_signature(group)
                                      for group in appended}
    for group in reversed(appended):
        bpy.data.node_groups.remove(group, do_unlink=True)
assert localized_signatures['en_US'] == localized_signatures['zh_HANS']
report = {'status': 'Passed', 'blender': bpy.app.version_string,
          'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'shared_unbound_asset': 'Passed', 'independent_parameters': 'Passed',
          'independent_source_transforms': 'Passed', 'preserved_branch': 'Passed',
          'library_roundtrip': 'Passed', 'locale_identity_and_geometry': 'Passed',
          'modified_graph_detection': 'Passed', 'user_rename_preservation': 'Passed',
          'bilingual_library_structure': 'Passed', 'baseline_vertices': len(baseline)}
args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
