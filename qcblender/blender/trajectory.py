"""Discrete XYZ frame navigation with stable atoms and inferred connections."""
import json

import bpy
import bmesh
from bpy.props import EnumProperty, IntProperty


def initialize_trajectory(obj, data):
    """Called after atom_view creation, including copies of trajectory views."""
    info = data.metadata.get('trajectory')
    if info:
        frame = obj.get('qc_trajectory_frame', 1)
        obj['qc_trajectory_frame'] = frame
        obj['qc_trajectory_count'] = len(info['frames'])
        obj['qc_trajectory_record'] = json.dumps(info['frames'][frame - 1], ensure_ascii=False)


def set_frame(obj, data, frame):
    from ..data import Dataset
    from ..geometry import scientific_geometry
    from ..readers import infer_bonds
    from .geometry import current_geometry
    from .annotations import prepare_annotations, apply_annotations
    current_geometry(obj, data)
    positions, record = scientific_geometry(data, 'trajectory', frame)
    record['dataset_sha256'] = obj['qc_dataset_sha256']
    attr = obj.data.attributes.get('qc_equilibrium_position')
    if attr is None or attr.domain != 'POINT' or attr.data_type != 'FLOAT_VECTOR' or len(attr.data) != len(positions):
        raise ValueError('XYZ equilibrium positions are missing or invalid')
    if obj.data.users > 1:
        raise ValueError('XYZ frame changes require an independent atom mesh')
    if obj.data.polygons:
        raise ValueError('XYZ atom mesh must contain only points and connections')
    bond_source = obj.data.attributes.get('qc_bond_source')
    if bond_source is not None and (bond_source.domain != 'EDGE' or bond_source.data_type != 'INT'):
        raise ValueError('XYZ inferred connection attribute is invalid')
    prepared = prepare_annotations(obj, positions, record)
    geometry = Dataset({}, {'positions': positions, 'atomic_numbers': data.arrays['atomic_numbers']})
    infer_bonds(geometry)
    # Edit only edges and vertex coordinates. BMesh retains POINT attributes,
    # vertex selection, material slots and the object's modifiers/properties.
    mesh = bmesh.new()
    try:
        mesh.from_mesh(obj.data)
        mesh.verts.ensure_lookup_table()
        for edge in list(mesh.edges):
            mesh.edges.remove(edge)
        for vertex, coordinate in zip(mesh.verts, positions):
            vertex.co = coordinate
        for a, b in geometry.arrays['bonds']:
            mesh.edges.new((mesh.verts[int(a)], mesh.verts[int(b)]))
        mesh.to_mesh(obj.data)
    finally:
        mesh.free()
    obj.data.attributes['qc_equilibrium_position'].data.foreach_set('vector', positions.ravel())
    bond_source = obj.data.attributes.get('qc_bond_source')
    if bond_source is None:
        bond_source = obj.data.attributes.new('qc_bond_source', 'INT', 'EDGE')
    bond_source.data.foreach_set('value', [1] * len(obj.data.edges))
    obj.data.update()
    obj['qc_trajectory_frame'] = frame
    obj['qc_trajectory_record'] = json.dumps(record['step_record'], ensure_ascii=False)
    apply_annotations(prepared)
    obj.update_tag()


class QCBLENDER_OT_trajectory_frame(bpy.types.Operator):
    bl_idname = 'qcblender.trajectory_frame'
    bl_label = 'Choose XYZ Frame'
    bl_options = {'REGISTER', 'UNDO'}
    direction: EnumProperty(items=[('GOTO', 'Choose', ''), ('PREV', 'Previous', ''), ('NEXT', 'Next', '')])
    frame: IntProperty(name='Frame', default=1, min=1)

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'MESH' and obj.mode == 'OBJECT' and bool(obj.get('qc_trajectory_frame'))

    def invoke(self, context, event):
        if self.direction != 'GOTO':
            return self.execute(context)
        self.frame = context.object['qc_trajectory_frame']
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        from ..data import load_dataset
        obj = context.object
        try:
            data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
            frame = self.frame if self.direction == 'GOTO' else obj['qc_trajectory_frame'] + (1 if self.direction == 'NEXT' else -1)
            set_frame(obj, data, frame)
        except (ValueError, OSError, KeyError, TypeError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_trajectory(bpy.types.Panel):
    bl_label = 'XYZ Frames'
    bl_idname = 'QCBLENDER_PT_trajectory'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_trajectory_frame'))

    def draw(self, context):
        obj, layout = context.object, self.layout
        frame, count = obj['qc_trajectory_frame'], obj['qc_trajectory_count']
        record = json.loads(obj['qc_trajectory_record'])
        layout.label(text=f'Frame {frame} / {count} | angstrom')
        layout.label(text=record['comment'])
        layout.label(text=f'Source lines {record["line_start"]}-{record["line_end"]}')
        layout.label(text='Connections inferred by distance per frame')
        row = layout.row(align=True)
        previous, following = row.row(), row.row()
        previous.enabled, following.enabled = frame > 1, frame < count
        previous.operator('qcblender.trajectory_frame', text='Previous').direction = 'PREV'
        following.operator('qcblender.trajectory_frame', text='Next').direction = 'NEXT'
        layout.operator('qcblender.trajectory_frame').direction = 'GOTO'


CLASSES = (QCBLENDER_OT_trajectory_frame, QCBLENDER_PT_trajectory)
