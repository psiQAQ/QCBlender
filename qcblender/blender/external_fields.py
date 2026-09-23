"""User assigned roles for externally calculated paired Cube fields."""
import json
from pathlib import Path

import bpy
from bpy.props import EnumProperty, FloatProperty, StringProperty

from .ui import AsyncOperation


def scatter_view(directory, data, parent):
    from ..external_fields import scatter_points
    from .views import bind, material

    points = scatter_points(data)
    minimum = points.min(axis=0)
    span = points.max(axis=0) - minimum
    span[span == 0] = 1
    scaled = (points - minimum) / span * 4
    mesh = bpy.data.meshes.new('QC field scatter')
    mesh.from_pydata([(float(x), 0, float(y)) for x, y in scaled], [], [])
    mesh.update()
    obj = bpy.data.objects.new('QC δg–sign(λ₂)ρ distribution', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = (0, -5, 0)
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'scatter'
    obj['qc_scatter'] = json.dumps({'x_quantity': data.metadata['fields'][0]['quantity'],
                                    'x_unit': data.metadata['fields'][0]['unit'],
                                    'y_quantity': data.metadata['fields'][1]['quantity'],
                                    'y_unit': data.metadata['fields'][1]['unit'],
                                    'minimum': minimum.tolist(), 'maximum': points.max(axis=0).tolist(),
                                    'sample_count': len(points), 'axis_scale': 'linear'})
    tree = bpy.data.node_groups.new('QC scatter points', 'GeometryNodeTree')
    tree.is_modifier = True
    tree.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    to_points = nodes.new('GeometryNodeMeshToPoints')
    to_points.mode = 'VERTICES'
    to_points.inputs['Radius'].default_value = .012
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = material('QC scatter', (.16, .23, .68, 1))
    links.new(inputs.outputs['Geometry'], to_points.inputs['Mesh'])
    links.new(to_points.outputs['Points'], assign.inputs['Geometry'])
    links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    obj.modifiers.new('QC Scatter', 'NODES').node_group = tree
    return obj


class QCBLENDER_OT_import_paired_field(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_paired_field'
    bl_label = 'Import IGMH / IRI Cube Pair'
    bl_options = {'REGISTER', 'UNDO'}

    method: EnumProperty(name='Analysis', items=[('IGMH', 'IGMH', ''), ('IRI', 'IRI', '')])
    geometry_source: StringProperty(name='Geometry Cube', subtype='FILE_PATH')
    color_source: StringProperty(name='sign(lambda2)rho Cube', subtype='FILE_PATH')
    geometry_unit: StringProperty(name='Geometry value unit', default='dimensionless')
    color_unit: StringProperty(name='Color value unit', default='electron/bohr^3')
    color_minimum: FloatProperty(name='Color minimum', default=-.05)
    color_maximum: FloatProperty(name='Color maximum', default=.05)

    @classmethod
    def poll(cls, context):
        return context.object is not None and 'qc_dataset' in context.object

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=550)

    def draw(self, context):
        for name in ('method', 'geometry_source', 'color_source', 'geometry_unit',
                     'color_unit', 'color_minimum', 'color_maximum'):
            self.layout.prop(self, name)
        self.layout.label(text='Active QC view supplies the calculation and geometry association')

    def begin(self, context):
        import hashlib
        from .jobs import Job
        if self.color_minimum >= self.color_maximum:
            raise ValueError('Color minimum must be below maximum')
        paths = [Path(bpy.path.abspath(p)).resolve(strict=True)
                 for p in (self.geometry_source, self.color_source)]
        if paths[0] == paths[1]:
            raise ValueError('Choose two distinct Cube files for geometry and color')
        self._reference = context.object
        self._reference_path = Path(bpy.path.abspath(self._reference['qc_dataset'])).resolve(strict=True)
        self._reference_digest = hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest()
        return Job('import_pair', geometry_source=str(paths[0]), color_source=str(paths[1]),
                   method=self.method, geometry_unit=self.geometry_unit, color_unit=self.color_unit,
                   reference_dataset=str(self._reference_path), reference_sha256=self._reference_digest)

    def accept(self, context, report):
        import hashlib
        from ..association import compare_sources
        from ..data import load_dataset
        from .scalars import add_mapping
        from .views import field_view

        directory = self._job.directory / 'dataset'
        data = load_dataset(directory)
        if self._reference.name not in bpy.data.objects or hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest() != self._reference_digest:
            raise ValueError('Reference calculation changed during import')
        association = compare_sources(load_dataset(self._reference_path), data)
        parent = self._reference
        geometry = field_view(directory, parent, 0)
        color = field_view(directory, parent, 1)
        color.hide_set(True)
        color.hide_render = True
        geometry['qc_analysis'] = json.dumps(dict(data.metadata['analysis'], reference=association))
        add_mapping(geometry, color, self.color_minimum, self.color_maximum)
        scatter_view(directory, data, parent)
        self.report({'INFO'}, 'Imported paired external Cube fields and scatter distribution')


class QCBLENDER_PT_paired_scatter(bpy.types.Panel):
    bl_label = 'IGMH / IRI Scatter'
    bl_idname = 'QCBLENDER_PT_paired_scatter'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'scatter'

    def draw(self, context):
        record = json.loads(context.object['qc_scatter'])
        layout = self.layout
        layout.label(text=record['x_quantity'] + ' [' + record['x_unit'] + ']')
        layout.label(text=record['y_quantity'] + ' [' + record['y_unit'] + ']')
        layout.label(text=f"Valid samples shown: {record['sample_count']}")
        layout.label(text='Axes: linear; grid values unchanged')
        for index, axis in enumerate('xy'):
            layout.label(text=f"{axis}: {record['minimum'][index]:.6g} to {record['maximum'][index]:.6g}")
