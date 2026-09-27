"""Verify material creation and atom display in Blender's Chinese UI locale."""
import hashlib
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qcblender.blender.scalars import add_legend, scalar_material
from qcblender.blender.views import atom_view, node_by_type, socket
from qcblender.data import Dataset, save_dataset
import qcblender

bpy.context.preferences.view.language = 'zh_HANS'
qcblender.register()
directory = ROOT / 'outputs' / 'localized-materials' / 'atoms.qcdata'
data = Dataset(
    {'source': {'filename': 'localized-material-probe', 'sha256': hashlib.sha256(b'localized-material-probe').hexdigest()},
     'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': []},
    {'atomic_numbers': np.array([1, 8, 1], dtype=np.int32),
     'positions': np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float),
     'bonds': np.array([[0, 1], [1, 2]], dtype=np.int32)},
)
save_dataset(data, directory)
obj = atom_view(directory)
assert len(obj.data.vertices) == 3
assert len(obj.modifiers) == 1

for mat in (bpy.data.materials['QC Elements'], scalar_material(opacity_attribute=True)):
    nodes = mat.node_tree.nodes
    shader = node_by_type(nodes, 'ShaderNodeBsdfPrincipled')
    output = node_by_type(nodes, 'ShaderNodeOutputMaterial')
    assert shader is not None and output is not None
    assert output.inputs['Surface'].is_linked
assert bpy.data.materials['QC Elements'].node_tree.nodes.get('Principled BSDF') is None
tree = obj.modifiers[0].node_group
for name, value in [('Color Minimum', -1.), ('Color Center', 0.), ('Color Maximum', 1.)]:
    item = socket(tree, name, 'NodeSocketFloat', default=value)
    obj.modifiers[0][item.identifier] = value
add_legend(obj, scalar_material(), 'Color Minimum', 'Color Center', 'Color Maximum', 'Scalar [unit]')
output = next(n for n in tree.nodes if n.type == 'GROUP_OUTPUT')
assert output.inputs['Geometry'].links[0].from_node.bl_idname == 'GeometryNodeJoinGeometry'
print('LOCALIZED_MATERIALS_PASSED')
