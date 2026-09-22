"""Run after verify_extension.py in the installed Blender extension profile."""
import importlib
import json
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/node-assets'
OUT.mkdir(parents=True, exist_ok=True)
views = importlib.import_module('bl_ext.user_default.qcblender.blender.views')


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
assert group.asset_data is not None and first_tree.asset_data is None
assert not any(n.bl_idname == 'GeometryNodeObjectInfo' for n in group.nodes)
assert all(s.socket_type not in ('NodeSocketObject', 'NodeSocketCollection')
           for s in group.interface.items_tree if s.item_type == 'SOCKET')
assert all(s.default_value is None for s in group.interface.items_tree
           if s.item_type == 'SOCKET' and s.socket_type == 'NodeSocketMaterial')

baseline = vertices(first)
assert len(baseline) > 100
np.testing.assert_array_equal(baseline, vertices(second))
inputs = {s.name: s.identifier for s in second_tree.interface.items_tree if s.item_type == 'SOCKET'}
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
existing = output.inputs['Geometry'].links[0].from_socket
extra = first_tree.nodes.new('GeometryNodeGroup')
extra.node_tree = group
extra.inputs['Isovalue'].default_value = .1
info = next(n for n in first_tree.nodes if n.bl_idname == 'GeometryNodeObjectInfo')
first_tree.links.new(info.outputs['Geometry'], extra.inputs['Volume'])
join = first_tree.nodes.new('GeometryNodeJoinGeometry')
first_tree.links.new(existing, join.inputs['Geometry'])
first_tree.links.new(extra.outputs['Geometry'], join.inputs['Geometry'])
first_tree.links.new(join.outputs['Geometry'], output.inputs['Geometry'])
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
report = {'status': 'Passed', 'blender': bpy.app.version_string,
          'shared_unbound_asset': 'Passed', 'independent_parameters': 'Passed',
          'independent_source_transforms': 'Passed', 'preserved_branch': 'Passed',
          'library_roundtrip': 'Passed', 'baseline_vertices': len(baseline)}
(OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
