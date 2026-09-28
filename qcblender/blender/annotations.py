"""Native scene annotations attached to source-ordered atom views."""

import json
from uuid import uuid4

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, StringProperty
from mathutils import Vector
import numpy as np

from ..measurements import (ATOM_COUNTS, DIHEDRAL_CONVENTION, measure, measurement_text, parse_source_atom_numbers,
                            validate_annotation_style)
from .geometry import current_geometry
from .views import material


def _entries(owner, role=None):
    for child in owner.children:
        if 'qc_annotation' not in child:
            continue
        entry = json.loads(child['qc_annotation'])
        if role is None or entry['role'] == role:
            yield child, entry


def _symbol(number):
    import periodictable

    if not 1 <= number <= 118:
        raise ValueError(f'No element symbol for atomic number {number}')
    return periodictable.elements[number].symbol


def _prepare(entry, positions, record):
    if (entry['source_sha256'] != record['source_sha256']
            or entry['selected_job'] != record['selected_job']
            or entry['dataset_sha256'] != record['dataset_sha256']
            or record['coordinate_unit'] != 'angstrom'):
        raise ValueError('Annotation source identity differs from the atom view')
    validate_annotation_style(entry)
    atoms = entry['source_atom_numbers']
    expected = 1 if entry['kind'] == 'ATOM' else ATOM_COUNTS.get(entry['kind'])
    if (expected is None or len(atoms) != expected or len(set(atoms)) != expected
            or any(type(number) is not int or number < 1 or number > len(positions) for number in atoms)):
        raise ValueError('Annotation atom number is outside the current geometry')
    anchor = np.asarray(positions, dtype=float)[np.array(atoms) - 1].mean(axis=0)
    if entry['kind'] == 'ATOM':
        value, reason = None, None
        body = f"{entry['symbols'][0]}{atoms[0]}"
    else:
        try:
            value, reason = measure(entry['kind'], positions, atoms), None
        except ValueError as error:
            if 'undefined:' not in str(error):
                raise
            value, reason = None, str(error)
        body = measurement_text(entry['kind'], atoms, value, record, entry['decimals'], reason)
    entry.update(geometry=record, value=value, undefined_reason=reason)
    if entry['kind'] == 'DIHEDRAL':
        entry['convention'] = DIHEDRAL_CONVENTION
    return entry, anchor, body


def _apply(label, entry, anchor, body, leader=None):
    offset = Vector(entry['offset'])
    label.location = Vector(anchor) + offset
    label.data.body = body
    label.data.size = entry['size']
    label.data.materials[0].diffuse_color = (*entry['color'], 1)
    shader = next(node for node in label.data.materials[0].node_tree.nodes
                  if node.bl_idname == 'ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value = (*entry['color'], 1)
    label.hide_viewport = label.hide_render = not entry['visible']
    label['qc_annotation'] = json.dumps(entry, ensure_ascii=False)
    if leader is not None:
        line, line_entry = leader
        line.data.splines[0].points[0].co = (*anchor, 1)
        line.data.splines[0].points[1].co = (*label.location, 1)
        line.data.bevel_depth = entry['line_width'] / 2
        line.hide_viewport = line.hide_render = not (entry['visible'] and entry['show_leader'])
        line.data.materials[0].diffuse_color = (*entry['color'], 1)
        line_shader = next(node for node in line.data.materials[0].node_tree.nodes
                           if node.bl_idname == 'ShaderNodeBsdfPrincipled')
        line_shader.inputs['Base Color'].default_value = (*entry['color'], 1)
        line_entry.update(geometry=entry['geometry'], value=entry['value'],
                          undefined_reason=entry['undefined_reason'])
        if entry['kind'] == 'DIHEDRAL':
            line_entry['convention'] = DIHEDRAL_CONVENTION
        line['qc_annotation'] = json.dumps(line_entry, ensure_ascii=False)


def _native_data(child, role):
    expected = 'FONT' if role == 'LABEL' else 'CURVE'
    if child.type != expected or child.data.users != 1 or len(child.data.materials) != 1:
        raise ValueError(f'{child.name}: annotation {role.lower()} needs independent {expected} data and material')
    mat = child.data.materials[0]
    if mat is None or mat.users != 1 or not mat.use_nodes or mat.node_tree is None:
        raise ValueError(f'{child.name}: annotation material must be independent and use nodes')
    shaders = [node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled']
    if len(shaders) != 1 or shaders[0].inputs.get('Base Color') is None:
        raise ValueError(f'{child.name}: annotation material needs one Principled shader')
    if role == 'LEADER':
        splines = child.data.splines
        if len(splines) != 1 or splines[0].type != 'POLY' or len(splines[0].points) != 2:
            raise ValueError(f'{child.name}: annotation leader needs a two-point poly curve')


def prepare_annotations(owner, positions, record):
    """Validate all marked children and compute new values without changing Blender data."""
    labels, leaders = {}, {}
    for child, entry in _entries(owner):
        role, identifier = entry['role'], entry['id']
        if role not in ('LABEL', 'LEADER') or not isinstance(identifier, str) or not identifier:
            raise ValueError(f'{child.name}: invalid annotation role or id')
        group = labels if role == 'LABEL' else leaders
        if identifier in group:
            raise ValueError(f'{child.name}: duplicate annotation {role.lower()} id')
        _native_data(child, role)
        group[identifier] = child, entry
    if labels.keys() != leaders.keys():
        raise ValueError('Annotation labels and leaders must form complete pairs')
    prepared = []
    for identifier, (child, entry) in labels.items():
        line, line_entry = leaders[identifier]
        if (line_entry['source_atom_numbers'] != entry['source_atom_numbers']
                or any(line_entry[key] != entry[key] for key in
                       ('source_sha256', 'selected_job', 'dataset_sha256'))):
            raise ValueError('Annotation leader identity differs from its label')
        entry, anchor, body = _prepare(entry, positions, record)
        line_entry.update(geometry=entry['geometry'], value=entry['value'],
                          undefined_reason=entry['undefined_reason'])
        if entry['kind'] == 'DIHEDRAL':
            line_entry['convention'] = DIHEDRAL_CONVENTION
        json.dumps(entry, ensure_ascii=False)
        json.dumps(line_entry, ensure_ascii=False)
        prepared.append((child, entry, anchor, body, (line, line_entry)))
    return prepared


def apply_annotations(prepared):
    """Apply values already checked by prepare_annotations."""
    for child, entry, anchor, body, leader in prepared:
        _apply(child, entry, anchor, body, leader)


def update_annotations(owner, positions, record):
    """Recompute saved values from real geometry, including undefined steps."""
    apply_annotations(prepare_annotations(owner, positions, record))


def copy_annotations(source, target, collection):
    """Copy only this atom view's annotation children, with independent curve and material data."""
    originals = list(_entries(source))
    if not originals:
        return
    source_positions, source_record = current_geometry(source)
    prepare_annotations(source, source_positions, source_record)
    positions, record = current_geometry(target)
    if (source_record['source_sha256'] != record['source_sha256']
            or source_record['selected_job'] != record['selected_job']):
        raise ValueError('Annotation calculation differs from the target atom view')
    prepare_annotations(target, positions, record)
    for _, entry in originals:
        if entry['role'] == 'LABEL':
            _prepare({**entry, 'dataset_sha256': record['dataset_sha256']}, positions, record)
    created = []
    try:
        for original, entry in originals:
            copied = original.copy()
            created.append(copied)
            copied.data = original.data.copy()
            for index, mat in enumerate(copied.data.materials):
                copied.data.materials[index] = mat.copy()
            collection.objects.link(copied)
            copied.parent = target
            entry['dataset_sha256'] = record['dataset_sha256']
            copied['qc_annotation'] = json.dumps(entry, ensure_ascii=False)
        update_annotations(target, positions, record)
    except Exception:
        for child in reversed(created):
            _delete(child)
        raise


def _delete(child):
    data = child.data
    materials = list(data.materials)
    bpy.data.objects.remove(child, do_unlink=True)
    if data.users == 0:
        bpy.data.curves.remove(data)
    for mat in materials:
        if mat and mat.users == 0:
            bpy.data.materials.remove(mat)


def remove_annotations(owner):
    """Delete only explicitly marked annotation children of this atom view."""
    for child, _ in list(_entries(owner)):
        _delete(child)


def _create(owner, collection, entry, positions, record):
    entry, anchor, body = _prepare(entry, positions, record)
    label_data = bpy.data.curves.new('QC annotation text', 'FONT')
    label_data.materials.append(material('QC annotation material', (*entry['color'], 1)))
    label = bpy.data.objects.new('QC annotation', label_data)
    collection.objects.link(label)
    label.parent = owner
    line_data = bpy.data.curves.new('QC annotation leader', 'CURVE')
    line_data.dimensions = '3D'
    line_data.bevel_resolution = 2
    spline = line_data.splines.new('POLY')
    spline.points.add(1)
    line_data.materials.append(material('QC annotation leader material', (*entry['color'], 1)))
    line = bpy.data.objects.new('QC annotation leader', line_data)
    collection.objects.link(line)
    line.parent = owner
    leader_entry = {'role': 'LEADER', 'id': entry['id'], 'source_atom_numbers': entry['source_atom_numbers'],
                    'source_sha256': entry['source_sha256'], 'selected_job': entry['selected_job'],
                    'dataset_sha256': entry['dataset_sha256']}
    _apply(label, entry, anchor, body, (line, leader_entry))
    return label


def _atom_view(context):
    obj = context.object
    if obj is not None and 'qc_annotation' in obj:
        obj = obj.parent
    return obj if obj is not None and obj.get('qc_view_kind') == 'atoms' else None


class QCBLENDER_OT_add_annotation(bpy.types.Operator):
    bl_idname = 'qcblender.add_annotation'
    bl_label = 'Add Source Atom Annotation'
    bl_options = {'REGISTER', 'UNDO'}

    kind: EnumProperty(name='Annotation', items=[('ATOM', 'Atom numbers', ''),
                       ('DISTANCE', 'Distance', ''), ('ANGLE', 'Angle', ''), ('DIHEDRAL', 'Dihedral', '')])
    atoms: StringProperty(name='Source atom numbers', default='1,2')
    size: FloatProperty(name='Text size (local scene units)', default=.16, min=.001)
    color: FloatVectorProperty(name='Color', subtype='COLOR', size=3, default=(1., .8, .2), min=0, max=1)
    offset: FloatVectorProperty(name='Offset (local scene units)', size=3, default=(.2, .2, .2))
    decimals: IntProperty(name='Decimal places', default=4, min=0, max=10)
    show_leader: BoolProperty(name='Show leader', default=True)
    line_width: FloatProperty(name='Leader width (local scene units)', default=.01, min=.0001)
    visible: BoolProperty(name='Visible', default=True)

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def invoke(self, context, event):
        if not self.properties.is_property_set('decimals', ghost=False):
            self.decimals = 4 if self.kind in ('ATOM', 'DISTANCE') else 2
        self.atoms = '1' if self.kind == 'ATOM' else ','.join(str(i) for i in range(1, ATOM_COUNTS[self.kind] + 1))
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'atoms')
        row = layout.row()
        left, right = row.column(), row.column()
        left.prop(self, 'size')
        left.prop(self, 'offset')
        right.prop(self, 'color')
        if self.kind != 'ATOM':
            right.prop(self, 'decimals')
        right.prop(self, 'show_leader')
        if self.show_leader:
            right.prop(self, 'line_width')
        right.prop(self, 'visible')

    def execute(self, context):
        owner = _atom_view(context)
        try:
            positions, record = current_geometry(owner)
            numbers = parse_source_atom_numbers(self.atoms, len(positions))
            if self.kind != 'ATOM' and len(numbers) != ATOM_COUNTS[self.kind]:
                raise ValueError(f'{self.kind} needs {ATOM_COUNTS[self.kind]} ordered source atom numbers')
            if self.kind != 'ATOM':
                measure(self.kind, positions, numbers)
            symbols = [_symbol(int(owner.data.attributes['qc_atomic_number'].data[n - 1].value))
                       for n in numbers]
            decimals = self.decimals if self.properties.is_property_set('decimals', ghost=False) else (
                4 if self.kind in ('ATOM', 'DISTANCE') else 2)
            settings = {'kind': self.kind, 'size': self.size, 'color': list(self.color),
                        'offset': list(self.offset), 'decimals': decimals,
                        'show_leader': self.show_leader, 'line_width': self.line_width, 'visible': self.visible,
                        'source_sha256': record['source_sha256'], 'selected_job': record['selected_job'],
                        'dataset_sha256': record['dataset_sha256']}
            collection = owner.users_collection[0]
            for atom in numbers if self.kind == 'ATOM' else [None]:
                chosen = [atom] if atom is not None else numbers
                entry = {**settings, 'role': 'LABEL', 'id': uuid4().hex,
                         'source_atom_numbers': chosen,
                         'symbols': [symbols[numbers.index(atom)]] if atom is not None else symbols}
                _create(owner, collection, entry, positions, record)
        except (ValueError, KeyError, OSError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_edit_annotation(bpy.types.Operator):
    bl_idname = 'qcblender.edit_annotation'
    bl_label = 'Edit QC Annotation'
    bl_options = {'REGISTER', 'UNDO'}

    annotation_id: StringProperty()
    size: FloatProperty(name='Text size (local scene units)', default=.16, min=.001)
    color: FloatVectorProperty(name='Color', subtype='COLOR', size=3, default=(1., .8, .2), min=0, max=1)
    offset: FloatVectorProperty(name='Offset (local scene units)', size=3)
    decimals: IntProperty(name='Decimal places', default=4, min=0, max=10)
    show_leader: BoolProperty(name='Show leader', default=True)
    line_width: FloatProperty(name='Leader width (local scene units)', default=.01, min=.0001)
    visible: BoolProperty(name='Visible', default=True)

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def invoke(self, context, event):
        owner = _atom_view(context)
        entry = next((entry for _, entry in _entries(owner, 'LABEL')
                      if entry['id'] == self.annotation_id), None)
        if entry is None:
            self.report({'ERROR'}, 'Annotation no longer exists')
            return {'CANCELLED'}
        for name in ('size', 'color', 'offset', 'decimals', 'show_leader', 'line_width', 'visible'):
            setattr(self, name, entry[name])
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        row = self.layout.row()
        left, right = row.column(), row.column()
        for name in ('size', 'offset'):
            left.prop(self, name)
        for name in ('color', 'decimals', 'show_leader', 'line_width', 'visible'):
            if name != 'line_width' or self.show_leader:
                right.prop(self, name)

    def execute(self, context):
        owner = _atom_view(context)
        try:
            positions, record = current_geometry(owner)
            prepared = prepare_annotations(owner, positions, record)
            found = next((item for item in prepared if item[1]['id'] == self.annotation_id), None)
            if found is None:
                raise ValueError('Annotation no longer exists')
            child, entry, _, _, leader = found
            entry.update(size=self.size, color=list(self.color), offset=list(self.offset),
                         decimals=self.decimals, show_leader=self.show_leader,
                         line_width=self.line_width, visible=self.visible)
            entry, anchor, body = _prepare(entry, positions, record)
            _apply(child, entry, anchor, body, leader)
        except (ValueError, KeyError, OSError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_face_annotations(bpy.types.Operator):
    bl_idname = 'qcblender.face_annotations'
    bl_label = 'Face QC Annotations to Camera'
    bl_options = {'REGISTER', 'UNDO'}

    annotation_id: StringProperty()

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def execute(self, context):
        camera = context.scene.camera
        if camera is None:
            self.report({'ERROR'}, 'Set an active scene camera first')
            return {'CANCELLED'}
        owner = _atom_view(context)
        rotation = owner.matrix_world.to_quaternion().inverted() @ camera.matrix_world.to_quaternion()
        for child, entry in _entries(owner, 'LABEL'):
            if not self.annotation_id or entry['id'] == self.annotation_id:
                child.rotation_mode = 'QUATERNION'
                child.rotation_quaternion = rotation
        return {'FINISHED'}


class QCBLENDER_OT_remove_annotation(bpy.types.Operator):
    bl_idname = 'qcblender.remove_annotation'
    bl_label = 'Remove QC Annotation'
    bl_options = {'REGISTER', 'UNDO'}

    annotation_id: StringProperty()

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def execute(self, context):
        for child, entry in list(_entries(_atom_view(context))):
            if entry['id'] == self.annotation_id:
                _delete(child)
        return {'FINISHED'}


def draw_annotations(layout, context):
    """Draw controls from stored records only; never load source arrays in draw."""
    owner = _atom_view(context)
    if owner is None:
        return
    box = layout.box()
    box.label(text='Source Atom Annotations')
    row = box.row(align=True)
    for kind, title in [('ATOM', 'Atoms'), ('DISTANCE', 'Distance'), ('ANGLE', 'Angle'), ('DIHEDRAL', 'Dihedral')]:
        row.operator('qcblender.add_annotation', text=title).kind = kind
    box.operator('qcblender.face_annotations', text='Face All to Camera', icon='CAMERA_DATA')
    for _, entry in _entries(owner, 'LABEL'):
        row = box.row(align=True)
        status = 'undefined' if entry.get('undefined_reason') else entry['kind'].title()
        row.label(text=f"{','.join(map(str, entry['source_atom_numbers']))}: {status}")
        row.operator('qcblender.edit_annotation', text='', icon='PREFERENCES').annotation_id = entry['id']
        row.operator('qcblender.face_annotations', text='', icon='CAMERA_DATA').annotation_id = entry['id']
        row.operator('qcblender.remove_annotation', text='', icon='X').annotation_id = entry['id']
