"""Run in Blender background mode to verify the proposed volume display path."""

import json
from pathlib import Path
import tempfile

import bpy
import numpy as np
import openvdb


root = Path(__file__).resolve().parents[1]
output = root / "outputs" / "volume-probe"
output.mkdir(parents=True, exist_ok=True)

# An asymmetric signed field distinguishes axis order and the two lobes.
indices = np.indices((21, 19, 17), dtype=np.float32)
x, y, z = indices
values = np.exp(-((x - 6) ** 2 + (y - 8) ** 2 + (z - 7) ** 2) / 6)
values -= 0.7 * np.exp(-((x - 15) ** 2 + (y - 10) ** 2 + (z - 9) ** 2) / 6)
matrix = [[0.2, 0, 0, 0], [0.04, 0.3, 0, 0], [0, 0, 0.4, 0], [1, -2, 3, 1]]
grid = openvdb.FloatGrid()
grid.name = "qc_value"
grid.copyFromArray(np.ascontiguousarray(values))
grid.transform = openvdb.createLinearTransform(matrix)
assert np.allclose(grid.transform.indexToWorld((2, 3, 4)), (1.52, -1.1, 4.6))
assert np.isclose(grid.getConstAccessor().getValue((6, 8, 7)), values[6, 8, 7])
assert grid.getConstAccessor().getValue((15, 10, 9)) < 0
negative = openvdb.FloatGrid()
negative.name = "qc_negative"
negative.copyFromArray(np.ascontiguousarray(-values))
negative.transform = openvdb.createLinearTransform(matrix)
color_grid = openvdb.FloatGrid()
color_grid.name = "qc_sample"
world_x, world_y, world_z = 0.2 * x + 0.04 * y + 1, 0.3 * y - 2, 0.4 * z + 3
color_grid.copyFromArray(np.ascontiguousarray(2 * world_x - 3 * world_y + 0.5 * world_z + 1))
color_grid.transform = openvdb.createLinearTransform(matrix)

with tempfile.TemporaryDirectory(prefix="signed-", dir=output) as directory:
    path = Path(directory) / "field.vdb"
    openvdb.write(str(path), grids=[grid, negative, color_grid])
    volume = bpy.data.volumes.new("Probe volume")
    volume.filepath = str(path)
    source = bpy.data.objects.new("Probe source", volume)
    bpy.context.scene.collection.objects.link(source)
    mesh = bpy.data.meshes.new("Probe mesh")
    obj = bpy.data.objects.new("Probe surface", mesh)
    bpy.context.scene.collection.objects.link(obj)
    tree = bpy.data.node_groups.new("QC volume probe", "GeometryNodeTree")
    tree.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    modifier = obj.modifiers.new("QC volume probe", "NODES")
    modifier.node_group = tree
    info = tree.nodes.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = source
    named = tree.nodes.new("GeometryNodeGetNamedGrid")
    named.inputs["Name"].default_value = "qc_value"
    surface = tree.nodes.new("GeometryNodeGridToMesh")
    sample_source = tree.nodes.new("GeometryNodeGetNamedGrid")
    sample_source.inputs["Name"].default_value = "qc_sample"
    sample = tree.nodes.new("GeometryNodeSampleGrid")
    sample.inputs["Interpolation"].default_value = "Trilinear"
    position = tree.nodes.new("GeometryNodeInputPosition")
    store = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT"
    store.domain = "POINT"
    store.inputs["Name"].default_value = "qc_sample_value"
    result = tree.nodes.new("NodeGroupOutput")
    tree.links.new(info.outputs["Geometry"], named.inputs["Volume"])
    tree.links.new(named.outputs["Grid"], surface.inputs["Grid"])
    tree.links.new(info.outputs["Geometry"], sample_source.inputs["Volume"])
    tree.links.new(sample_source.outputs["Grid"], sample.inputs["Grid"])
    tree.links.new(position.outputs["Position"], sample.inputs["Position"])
    tree.links.new(surface.outputs["Mesh"], store.inputs["Geometry"])
    tree.links.new(sample.outputs["Value"], store.inputs["Value"])
    tree.links.new(store.outputs["Geometry"], result.inputs["Geometry"])

    def evaluate(name, threshold):
        named.inputs["Name"].default_value = name
        surface.inputs["Threshold"].default_value = threshold
        obj.update_tag()
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        evaluated_mesh = evaluated.to_mesh()
        try:
            coords = np.array([v.co[:] for v in evaluated_mesh.vertices])
            assert len(coords) > 0, (name, threshold, "empty surface")
            sampled = np.array([v.value for v in evaluated_mesh.attributes["qc_sample_value"].data])
            expected = 2 * coords[:, 0] - 3 * coords[:, 1] + 0.5 * coords[:, 2] + 1
            error = float(np.max(np.abs(sampled - expected)))
            assert error < 1e-5, (name, threshold, "coordinate sampling", error)
            return {"vertices": len(coords), "faces": len(evaluated_mesh.polygons),
                    "sample_max_absolute_error": error,
                    "min": coords.min(axis=0).tolist(), "max": coords.max(axis=0).tolist()}
        finally:
            evaluated.to_mesh_clear()

    low = evaluate("qc_value", 0.1)
    high = evaluate("qc_value", 0.4)
    minus = evaluate("qc_negative", 0.1)
    assert low["min"][0] < high["min"][0] < high["max"][0] < low["max"][0]
    assert minus["min"][0] > low["min"][0]
    report = {"status": "Passed", "blender": bpy.app.version_string,
              "checks": ["signed values", "axis order", "sheared grid transform",
                         "native grid to mesh", "threshold changes geometry", "negative lobe",
                         "trilinear sampling of a second sheared grid"],
              "positive_0.1": low, "positive_0.4": high, "negative_0.1": minus}
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.objects.remove(source, do_unlink=True)
    bpy.data.volumes.remove(volume)
    bpy.data.node_groups.remove(tree)
    bpy.data.meshes.remove(mesh)

(output / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
del grid, negative, color_grid
