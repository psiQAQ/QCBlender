"""Native Blender views for imported ESP, AIM, and ETS-NOCV records."""
import json
from pathlib import Path
import uuid

import bpy
from bpy.props import EnumProperty, StringProperty


def store_analysis(data):
    from ..data import save_dataset
    location = bpy.utils.user_resource('DATAFILES', path='qcblender/analyses', create=True)
    if not location:
        raise OSError('Blender user data directory is unavailable')
    root = Path(location)
    directory = root / uuid.uuid4().hex
    save_dataset(data, directory)
    return directory


def point_view(directory, data, parent, points, name, color, role):
    from .views import bind, material
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([point['position_angstrom'] for point in points], [], [])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'analysis'
    obj['qc_analysis_role'] = role
    obj['qc_analysis_index'] = 1
    tree = bpy.data.node_groups.new(name + ' points', 'GeometryNodeTree')
    tree.is_modifier = True
    tree.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    dots = nodes.new('GeometryNodeMeshToPoints')
    dots.mode = 'VERTICES'
    dots.inputs['Radius'].default_value = .065
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = material(name, color)
    links.new(inputs.outputs['Geometry'], dots.inputs['Mesh'])
    links.new(dots.outputs['Points'], assign.inputs['Geometry'])
    links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    obj.modifiers.new('QC Point Markers', 'NODES').node_group = tree
    return obj


def area_view(directory, data, parent):
    return table_view(directory, data, parent, 'QC ESP area data', 'esp_area')


def path_view(directory, data, parent):
    from .views import bind, material
    curve = bpy.data.curves.new('QC AIM bond paths', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = .012
    curve.bevel_resolution = 2
    for path in data.metadata['analysis']['paths']:
        spline = curve.splines.new('POLY')
        spline.points.add(len(path['points_angstrom']) - 1)
        for point, coordinates in zip(spline.points, path['points_angstrom']):
            point.co = (*coordinates, 1)
    curve.materials.append(material('QC AIM paths', (.13, .71, .42, 1)))
    obj = bpy.data.objects.new('QC AIM bond paths', curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'analysis'
    obj['qc_analysis_role'] = 'aim_paths'
    obj['qc_analysis_index'] = 1
    return obj


def table_view(directory, data, parent, name, role):
    from .views import bind
    mesh = bpy.data.meshes.new(name + ' records')
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'analysis'
    obj['qc_data_record'] = True
    obj['qc_analysis_role'] = role
    obj['qc_analysis_index'] = 1
    return obj


class QCBLENDER_OT_import_esp(bpy.types.Operator):
    bl_idname = 'qcblender.import_esp_analysis'
    bl_label = 'Import ESP Surface Results'
    bl_options = {'REGISTER', 'UNDO'}

    extrema_path: StringProperty(name='Extrema PDB', subtype='FILE_PATH')
    area_path: StringProperty(name='Area distribution text', subtype='FILE_PATH')
    surface_definition: StringProperty(name='Surface definition', default='electron density 0.001 e/bohr^3')
    extrema_unit: StringProperty(name='Extrema value unit (optional with PDB REMARK)', default='')
    center_unit: StringProperty(name='Distribution center unit', default='')
    area_unit: StringProperty(name='Area unit (optional with table note)', default='')

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'esp')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)

    def draw(self, context):
        for name in ('extrema_path', 'area_path', 'surface_definition', 'extrema_unit', 'center_unit', 'area_unit'):
            self.layout.prop(self, name)
        self.layout.label(text='ESP values: a.u., eV or kcal/mol; area: angstrom^2 or bohr^2')
        self.layout.label(text='Center unit is always user assigned; source declarations are checked on import')

    def execute(self, context):
        from ..analysis_data import import_esp
        from ..data import load_dataset
        try:
            parent = context.object
            reference = load_dataset(bpy.path.abspath(parent['qc_dataset']))
            data = import_esp(reference, bpy.path.abspath(self.extrema_path), bpy.path.abspath(self.area_path),
                              self.surface_definition, self.extrema_unit, self.center_unit, self.area_unit)
            data.metadata['analysis']['surface_field'] = json.loads(parent['qc_field'])
            directory = store_analysis(data)
            points = data.metadata['analysis']['extrema']
            for kind, color in [('maximum', (.95, .6, .12, 1)), ('minimum', (.12, .65, .94, 1))]:
                selected = [point for point in points if point['kind'] == kind]
                if selected:
                    point_view(directory, data, parent, selected, 'QC ESP ' + kind, color, 'esp_' + kind)
            area_view(directory, data, parent)
        except (ValueError, OSError, KeyError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_import_aim(bpy.types.Operator):
    bl_idname = 'qcblender.import_aim_analysis'
    bl_label = 'Import AIM Topology'
    bl_options = {'REGISTER', 'UNDO'}

    cps_path: StringProperty(name='CPs PDB', subtype='FILE_PATH')
    paths_path: StringProperty(name='Paths PDB', subtype='FILE_PATH')
    properties_path: StringProperty(name='CP properties text (optional)', subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'aim')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)

    def draw(self, context):
        for name in ('cps_path', 'paths_path', 'properties_path'):
            self.layout.prop(self, name)

    def execute(self, context):
        from ..analysis_data import import_aim
        from ..data import load_dataset
        try:
            parent = context.object
            reference = load_dataset(bpy.path.abspath(parent['qc_dataset']))
            props = bpy.path.abspath(self.properties_path) if self.properties_path.strip() else None
            data = import_aim(reference, bpy.path.abspath(self.cps_path), bpy.path.abspath(self.paths_path), props)
            directory = store_analysis(data)
            colors = {'C': (.9, .15, .9, 1), 'N': (.12, .8, .22, 1),
                      'O': (.9, .8, .1, 1), 'F': (.12, .8, .85, 1)}
            for kind, color in colors.items():
                selected = [point for point in data.metadata['analysis']['critical_points'] if point['type'] == kind]
                if selected:
                    point_view(directory, data, parent, selected, 'QC AIM CP ' + kind, color, 'aim_' + kind)
            path_view(directory, data, parent)
        except (ValueError, OSError, KeyError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_import_ets(bpy.types.Operator):
    bl_idname = 'qcblender.import_ets_nocv'
    bl_label = 'Import ETS-NOCV Pair Table'
    bl_options = {'REGISTER', 'UNDO'}

    output_path: StringProperty(name='ETS-NOCV output text', subtype='FILE_PATH')
    energy_unit: EnumProperty(name='Pair energy unit', items=[('kcal/mol', 'kcal/mol', ''), ('hartree', 'hartree', '')])

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'nocv_table')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'output_path')
        self.layout.prop(self, 'energy_unit')

    def execute(self, context):
        from ..analysis_data import import_ets
        from ..data import load_dataset
        try:
            parent = context.object
            reference = load_dataset(bpy.path.abspath(parent['qc_dataset']))
            data = import_ets(reference, bpy.path.abspath(self.output_path), self.energy_unit)
            directory = store_analysis(data)
            table_view(directory, data, parent, 'QC ETS-NOCV pairs', 'ets_nocv')
        except (ValueError, OSError, KeyError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_external_results(bpy.types.Panel):
    bl_label = 'External Analysis Records'
    bl_idname = 'QCBLENDER_PT_external_results'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.get('qc_analysis_role') in
                ('esp_maximum', 'esp_minimum', 'esp_area', 'aim_C', 'aim_N', 'aim_O', 'aim_F',
                 'aim_paths', 'ets_nocv'))

    def draw(self, context):
        from .source_browser import cached_metadata
        obj = context.object
        analysis = cached_metadata(obj).get('analysis')
        if not analysis:
            self.layout.label(text='来源未读取或关联断裂，请刷新来源', icon='INFO')
            self.layout.operator('qcblender.refresh_sources')
            return
        role = obj['qc_analysis_role']
        layout = self.layout
        layout.label(text=analysis['kind'] + ': ' + role)
        layout.prop(obj, '["qc_analysis_index"]', text='Record (1-based)')
        index = int(obj['qc_analysis_index']) - 1
        if role.startswith('esp_') and role != 'esp_area':
            records = [row for row in analysis['extrema'] if row['kind'] == role[4:]]
            unit = analysis['extrema_unit']
        elif role == 'esp_area':
            records, unit = analysis['area_bins'], analysis['area_unit']
            layout.label(text='Surface: ' + analysis['surface_definition'])
            layout.label(text=f"Total area: {analysis['area_sum']:.6g} {unit}")
        elif role.startswith('aim_') and role != 'aim_paths':
            records = [row for row in analysis['critical_points'] if row['type'] == role[4:]]
            unit = 'angstrom'
        elif role == 'aim_paths':
            records, unit = analysis['paths'], 'angstrom'
        else:
            records, unit = analysis['pairs'], analysis['energy_unit']
        layout.label(text=f'{len(records)} records | {unit}')
        if 0 <= index < len(records):
            for key, value in records[index].items():
                layout.label(text=f'{key}: {value}'[:110])
            if role.startswith('aim_') and role != 'aim_paths':
                serial = records[index]['serial']
                properties = analysis['properties'].get(str(serial), analysis['properties'].get(serial, {}))
                for key, value in properties.items():
                    layout.label(text=f'{key}: {value}'[:110])
