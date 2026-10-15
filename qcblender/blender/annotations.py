"""Native scene annotations attached to source-ordered atom views."""
from ..i18n import error_text, iface, tip, ui_layout
from .node_identity import node_socket

import json
from uuid import uuid4

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, StringProperty
from mathutils import Vector
import numpy as np

from ..measurements import (ATOM_COUNTS, DIHEDRAL_CONVENTION, annotation_prefix, measure, measurement_text, parse_source_atom_numbers,
                            validate_annotation_style)
from ..annotation_geometry import measurement_geometry
from .geometry import current_geometry
from .views import material

ROLES = {'LABEL', 'LEADER', 'DASH', 'ARC', 'PLANE_A', 'PLANE_B'}
CORE_ROLES = ('LABEL', 'LEADER', 'DASH', 'ARC')
PLANE_ROLES = ('PLANE_A', 'PLANE_B')
STYLE_DEFAULTS = {'prefix_mode': 'DEFAULT', 'prefix': '', 'show_measurement': True,
                  'show_planes': True, 'measurement_width': .01, 'arc_radius': .5}


class AnnotationParts(dict):
    """Prepared native parts and material-free display geometry for one label."""
    geometry = None


def _visible(obj, visible):
    """Respect the annotation switch and an already hidden parent display layer."""
    obj.hide_viewport = not visible
    obj.hide_render = not visible
    owner = obj.parent
    if 'qc_layer_restore_render' in obj:
        obj['qc_layer_restore_render'] = not visible
    if owner is not None and getattr(owner, 'hide_render', False):
        obj['qc_layer_restore_render'] = not visible
        obj.hide_render = True
    if owner is not None and hasattr(owner, 'hide_get') and owner.hide_get():
        if 'qc_layer_restore_viewport' not in obj:
            obj['qc_layer_restore_viewport'] = obj.hide_get()
        obj.hide_set(True)


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
    entry = {**STYLE_DEFAULTS, **entry}
    validate_annotation_style(entry, validate_color=False)
    atoms = entry['source_atom_numbers']
    expected = 1 if entry['kind'] == 'ATOM' else ATOM_COUNTS.get(entry['kind'])
    if (expected is None or len(atoms) != expected or len(set(atoms)) != expected
            or any(type(number) is not int or number < 1 or number > len(positions) for number in atoms)):
        raise ValueError('Annotation atom number is outside the current geometry')
    anchor = np.asarray(positions, dtype=float)[np.array(atoms) - 1].mean(axis=0)
    if entry['kind'] == 'ATOM':
        value, reason = None, None
        body = annotation_prefix('ATOM', atoms, entry['prefix_mode'], entry['prefix']) + f"{entry['symbols'][0]}{atoms[0]}"
    else:
        try:
            value, reason = measure(entry['kind'], positions, atoms), None
        except ValueError as error:
            if 'undefined:' not in str(error):
                raise
            value, reason = None, str(error)
        body = measurement_text(entry['kind'], atoms, value, record, entry['decimals'], reason,
                                prefix_mode=entry['prefix_mode'], prefix=entry['prefix'])
    entry.update(geometry=record, value=value, undefined_reason=reason)
    if entry['kind'] == 'DIHEDRAL':
        entry['convention'] = DIHEDRAL_CONVENTION
    return entry, anchor, body


def _apply(label, entry, anchor, body, leader=None):
    """Update native geometry and metadata; never inspect or mutate materials."""
    parts = leader if isinstance(leader, AnnotationParts) else AnnotationParts(
        {'LEADER': leader} if leader is not None else {})
    offset = Vector(entry['offset'])
    label.location = Vector(anchor) + offset
    label.data.body = body
    label.data.size = entry['size']
    _visible(label, entry['visible'])
    label['qc_annotation'] = json.dumps(entry, ensure_ascii=False)
    if 'LEADER' in parts:
        line, line_entry = parts['LEADER']
        line.data.splines[0].points[0].co = (*anchor, 1)
        line.data.splines[0].points[1].co = (*label.location, 1)
        line.data.bevel_depth = entry['line_width'] / 2
        _visible(line, entry['visible'] and entry['show_leader'])
    geometry = parts.geometry or {'dashes': [], 'arc': [], 'planes': []}
    for role in ('DASH', 'ARC'):
        if role not in parts:
            continue
        obj, _ = parts[role]
        paths = geometry['dashes'] if role == 'DASH' else ([geometry['arc']] if len(geometry['arc']) else [])
        _curve_paths(obj.data, paths)
        obj.data.bevel_depth = entry['measurement_width'] / 2
        _visible(obj, entry['visible'] and entry['show_measurement'] and bool(len(paths)))
    for index, role in enumerate(PLANE_ROLES):
        if role not in parts:
            continue
        obj, _ = parts[role]
        points = geometry['planes'][index] if len(geometry['planes']) else []
        obj.data.clear_geometry()
        obj.data.from_pydata(list(points), [], [(0, 1, 2)] if len(points) else [])
        obj.data.update()
        _visible(obj, entry['visible'] and entry['show_planes'] and bool(len(points)))
    for role, (obj, _) in parts.items():
        obj['qc_annotation'] = json.dumps({**entry, 'role': role}, ensure_ascii=False)


def _curve_paths(data, paths):
    data.splines.clear()
    for path in paths:
        if len(path) < 2:
            continue
        spline = data.splines.new('POLY')
        spline.points.add(len(path) - 1)
        for point, coordinate in zip(spline.points, path):
            point.co = (*coordinate, 1)


def _native_data(child, role):
    expected = 'FONT' if role == 'LABEL' else 'MESH' if role in PLANE_ROLES else 'CURVE'
    if child.type != expected or child.data.users != 1:
        raise ValueError(f'{child.name}: annotation {role.lower()} needs independent {expected} data')
    if role == 'LEADER':
        splines = child.data.splines
        if len(splines) != 1 or splines[0].type != 'POLY' or len(splines[0].points) != 2:
            raise ValueError(f'{child.name}: annotation leader needs a two-point poly curve')


def _groups(owner):
    groups = {}
    for child, entry in _entries(owner):
        role, identifier = entry['role'], entry['id']
        if role not in ROLES or not isinstance(identifier, str) or not identifier:
            raise ValueError(f'{child.name}: invalid annotation role or id')
        group = groups.setdefault(identifier, AnnotationParts())
        if role in group:
            raise ValueError(f'{child.name}: duplicate annotation {role.lower()} id')
        _native_data(child, role)
        group[role] = child, entry
    for group in groups.values():
        if not {'LABEL', 'LEADER'}.issubset(group):
            raise ValueError('Annotation labels and leaders must form complete pairs')
        if group['LABEL'][1].get('version', 1) not in (1, 2):
            raise ValueError('Unsupported annotation record version')
    return groups


def prepare_annotations(owner, positions, record):
    """Validate native parts and compute values without touching Blender data or materials."""
    prepared = []
    for group in _groups(owner).values():
        child, entry = group['LABEL']
        for _, part_entry in group.values():
            if (part_entry['source_atom_numbers'] != entry['source_atom_numbers']
                    or any(part_entry[key] != entry[key] for key in
                           ('source_sha256', 'selected_job', 'dataset_sha256'))):
                raise ValueError('Annotation part identity differs from its label')
        allowed = {'LABEL', 'LEADER'} | ({'DASH'} if entry['kind'] == 'DISTANCE' else
                    {'ARC'} if entry['kind'] == 'ANGLE' else
                    {'ARC', *PLANE_ROLES} if entry['kind'] == 'DIHEDRAL' else set())
        if not set(group).issubset(allowed):
            raise ValueError('Annotation part role differs from its measurement kind')
        if entry.get('version', 1) >= 2 and set(group) != allowed:
            raise ValueError('Annotation measurement parts are incomplete')
        entry, anchor, body = _prepare(entry, positions, record)
        parts = AnnotationParts({role: part for role, part in group.items() if role != 'LABEL'})
        parts.geometry = measurement_geometry(entry['kind'], positions, entry['source_atom_numbers'], entry['arc_radius'])
        json.dumps(entry, ensure_ascii=False)
        prepared.append((child, entry, anchor, body, parts))
    return prepared


def apply_annotations(prepared):
    """Apply values already checked by prepare_annotations."""
    for child, entry, anchor, body, leader in prepared:
        _apply(child, entry, anchor, body, leader)


def update_annotations(owner, positions, record):
    """Recompute saved values from real geometry, including undefined steps."""
    apply_annotations(prepare_annotations(owner, positions, record))


def copy_annotations(source, target, collection):
    """Copy complete annotation groups: independent data and one material per role group."""
    groups = _groups(source)
    if not groups:
        return
    source_positions, source_record = current_geometry(source)
    prepare_annotations(source, source_positions, source_record)
    positions, record = current_geometry(target)
    if (source_record['source_sha256'] != record['source_sha256']
            or source_record['selected_job'] != record['selected_job']):
        raise ValueError('Annotation calculation differs from the target atom view')
    prepare_annotations(target, positions, record)
    if groups.keys() & _groups(target).keys():
        raise ValueError('Annotation IDs already exist in the target atom view')
    for group in groups.values():
        _prepare({**group['LABEL'][1], 'dataset_sha256': record['dataset_sha256']}, positions, record)
    created, copied_materials = [], []
    try:
        for group in groups.values():
            identifier = group['LABEL'][1]['id']
            core = _first_material(group['LABEL'][0])
            plane = _first_material(group['PLANE_A'][0]) if 'PLANE_A' in group else None
            materials = {}
            for role, source_material in (('CORE', core), ('PLANE', plane)):
                materials[role] = source_material.copy() if source_material is not None else None
                if materials[role] is not None:
                    copied_materials.append(materials[role])
                    materials[role].use_fake_user = False
            for role, (original, entry) in group.items():
                copied = original.copy()
                created.append(copied)
                copied.data = original.data.copy()
                _assign_material(copied, materials['PLANE' if role in PLANE_ROLES else 'CORE'])
                collection.objects.link(copied)
                copied.parent = target
                copied['qc_annotation'] = json.dumps({**entry, 'id': identifier,
                    'dataset_sha256': record['dataset_sha256']}, ensure_ascii=False)
        update_annotations(target, positions, record)
    except Exception:
        for child in reversed(created):
            _delete(child)
        for mat in copied_materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        raise


def _delete(child):
    data = child.data
    collection = bpy.data.meshes if child.type == 'MESH' else bpy.data.curves
    bpy.data.objects.remove(child, do_unlink=True)
    if data.users == 0:
        collection.remove(data)
    # Materials are editable user data, including nodes and possible external use.
    # Explicit unification preserves old materials with fake users; deletion never purges them.


def remove_annotations(owner):
    """Delete only explicitly marked annotation children of this atom view."""
    for child, _ in list(_entries(owner)):
        _delete(child)


def _first_material(obj):
    return obj.data.materials[0] if len(obj.data.materials) else None


def _assign_material(obj, mat):
    obj.data.materials.clear()
    if mat is not None:
        obj.data.materials.append(mat)


def _new_material(color, plane=False):
    """Initial material defaults only; no update/edit path calls this on existing materials."""
    rgb = np.asarray(color, dtype=float)
    if rgb.shape != (3,) or not np.isfinite(rgb).all() or (rgb < 0).any() or (rgb > 1).any():
        raise ValueError('Annotation initial color must be finite and between zero and one')
    alpha = .2 if plane else 1.
    mat = material('QC annotation plane material' if plane else 'QC annotation material', (*rgb, alpha))
    shader = next(node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
    node_socket(shader.inputs, 'Metallic').default_value = 0. if plane else 1.
    if plane:
        mat.surface_render_method = 'DITHERED'
    return mat


def _part(owner, collection, entry, role, mat):
    name = 'QC annotation ' + role.lower()
    if role in PLANE_ROLES:
        data = bpy.data.meshes.new(name)
    else:
        data = bpy.data.curves.new(name, 'FONT' if role == 'LABEL' else 'CURVE')
        if role != 'LABEL':
            data.dimensions = '3D'
            data.bevel_resolution = 2
            data.use_fill_caps = True
        if role == 'LEADER':
            _curve_paths(data, [np.zeros((2, 3))])
    obj = bpy.data.objects.new(name, data)
    try:
        _assign_material(obj, mat)
        obj['qc_annotation'] = json.dumps({**entry, 'role': role}, ensure_ascii=False)
        collection.objects.link(obj)
        obj.parent = owner
    except Exception:
        _delete(obj)
        raise
    return obj


def _roles(kind):
    return ('LABEL', 'LEADER', 'DASH') if kind == 'DISTANCE' else (
        ('LABEL', 'LEADER', 'ARC', *PLANE_ROLES) if kind == 'DIHEDRAL' else
        ('LABEL', 'LEADER', 'ARC') if kind == 'ANGLE' else ('LABEL', 'LEADER'))


def _create(owner, collection, entry, positions, record):
    from .annotation_fonts import annotation_font
    entry, anchor, body = _prepare({**entry, 'version': 2}, positions, record)
    core = _new_material(entry.get('color', [0., 0., 0.]))
    plane = None
    created = []
    try:
        if entry['kind'] == 'DIHEDRAL':
            plane = _new_material(entry.get('color', [0., 0., 0.]), plane=True)
        for role in _roles(entry['kind']):
            created.append(_part(owner, collection, entry, role, plane if role in PLANE_ROLES else core))
        label = created[0]
        label.data.font = annotation_font()
        parts = AnnotationParts({role: (obj, {**entry, 'role': role})
                                 for role, obj in zip(_roles(entry['kind'])[1:], created[1:])})
        parts.geometry = measurement_geometry(entry['kind'], positions, entry['source_atom_numbers'], entry['arc_radius'])
        _apply(label, entry, anchor, body, parts)
        return label
    except Exception:
        for obj in reversed(created):
            _delete(obj)
        for mat in (core, plane):
            if mat is not None and mat.users == 0:
                bpy.data.materials.remove(mat)
        raise


def _upgrade_parts(label, entry, parts, collection):
    """First explicit edit adds geometry without rewriting any existing material."""
    missing = [role for role in _roles(entry['kind']) if role != 'LABEL' and role not in parts]
    if not missing:
        entry['version'] = 2
        return
    owner = label.parent
    mat = _first_material(label)
    plane = _first_material(parts['PLANE_A'][0]) if 'PLANE_A' in parts else None
    created, new_plane = [], None
    try:
        for role in missing:
            if role in PLANE_ROLES and plane is None:
                plane = new_plane = _new_material(entry.get('color', [0., 0., 0.]), plane=True)
            obj = _part(owner, collection, entry, role, plane if role in PLANE_ROLES else mat)
            created.append(obj)
            parts[role] = obj, {**entry, 'role': role}
    except Exception:
        for obj in reversed(created):
            _delete(obj)
        if new_plane is not None and new_plane.users == 0:
            bpy.data.materials.remove(new_plane)
        raise
    entry['version'] = 2


def _needs_unifying(members):
    if not members:
        return False
    mat = _first_material(members[0])
    if mat is None:
        raise ValueError('Annotation has no reference material to unify')
    return (any(len(obj.data.materials) != 1 or _first_material(obj) != mat for obj in members)
            or mat.users != len(members) + int(mat.use_fake_user))


def material_unification_plan(owner):
    plan = []
    for identifier, group in _groups(owner).items():
        changed = []
        for roles in (CORE_ROLES, PLANE_ROLES):
            members = [group[role][0] for role in roles if role in group]
            if _needs_unifying(members):
                changed.append(members)
        if changed:
            plan.append((identifier, changed))
    return plan


def unify_annotation_materials(owner):
    """Explicit, idempotent material migration; preserves replaced datablocks for save/Undo."""
    plan = material_unification_plan(owner)
    snapshots, copies, old_flags = [], [], {}
    try:
        for _, sets in plan:
            for members in sets:
                clone = _first_material(members[0]).copy()
                copies.append(clone)
                clone.use_fake_user = False
                for obj in members:
                    original = tuple(obj.data.materials)
                    snapshots.append((obj, original))
                    for mat in original:
                        if mat is not None:
                            old_flags.setdefault(mat, mat.use_fake_user)
                    _assign_material(obj, clone)
        for mat in old_flags:
            mat.use_fake_user = True
    except Exception:
        for obj, mats in reversed(snapshots):
            obj.data.materials.clear()
            for mat in mats:
                obj.data.materials.append(mat)
        for mat, flag in old_flags.items():
            mat.use_fake_user = flag
        for mat in copies:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        raise
    return len(plan)


def _atom_view(context):
    obj = context.object
    if obj is not None and 'qc_annotation' in obj:
        obj = obj.parent
    return obj if obj is not None and obj.get('qc_view_kind') == 'atoms' else None


def _draw_style(layout, operator, kind, creating=False):
    layout = ui_layout(layout)
    box = layout.box()
    box.label(text='Text and placement')
    box.prop(operator, 'prefix_mode')
    if operator.prefix_mode == 'CUSTOM':
        box.prop(operator, 'prefix')
    box.prop(operator, 'size')
    box.prop(operator, 'offset')
    if kind != 'ATOM':
        box.prop(operator, 'decimals')
    box.prop(operator, 'show_leader')
    if operator.show_leader:
        box.prop(operator, 'line_width')
    box.prop(operator, 'visible')
    if kind != 'ATOM':
        box = layout.box()
        box.label(text='Measurement geometry')
        box.prop(operator, 'show_measurement')
        box.prop(operator, 'measurement_width')
        if kind in ('ANGLE', 'DIHEDRAL'):
            box.prop(operator, 'arc_radius')
        if kind == 'DIHEDRAL':
            box.prop(operator, 'show_planes')
    if creating:
        box = layout.box()
        box.label(text='Initial material')
        box.prop(operator, 'color')
    else:
        layout.label(text='Edit colors and shaders in Material Properties or the Shader Editor')


def _style_values(operator, kind):
    return {name: list(getattr(operator, name)) if name == 'offset' else getattr(operator, name)
            for name in ('size', 'offset', 'decimals', 'show_leader', 'line_width', 'visible',
                         'prefix_mode', 'prefix', 'show_measurement', 'measurement_width',
                         'arc_radius', 'show_planes')}


def _ensure_legacy_font(label, text):
    font = label.data.font
    if (font is not None and font.name == 'Bfont' and getattr(font, 'filepath', '') in ('', '<builtin>')
            and any(0x2e80 <= ord(character) <= 0x9fff or 0xf900 <= ord(character) <= 0xfaff
                    or 0x20000 <= ord(character) <= 0x3134f for character in text)):
        from .annotation_fonts import annotation_font
        label.data.font = annotation_font()


class QCBLENDER_OT_add_annotation(bpy.types.Operator):
    bl_idname = 'qcblender.add_annotation'
    bl_label = 'Add Source Atom Annotation'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return tip({
            'ATOM': 'Select an atom view; create source-symbol and atom-number labels for the entered atoms',
            'DISTANCE': 'Select an atom view; label the distance and symmetric dashed line between two source atoms',
            'ANGLE': 'Select an atom view; label the ordered three-atom angle and its circular arc',
            'DIHEDRAL': 'Select an atom view; label the signed four-atom dihedral, projected arc and two atom triangles',
        }.get(properties.kind, 'Create a source atom or geometry annotation on the active atom view'))

    kind: EnumProperty(name='Annotation', items=[('ATOM', 'Atom numbers', ''),
                       ('DISTANCE', 'Distance', ''), ('ANGLE', 'Angle', ''), ('DIHEDRAL', 'Dihedral', '')])
    atoms: StringProperty(name='Source atom numbers', description='Enter one-based source atom numbers in measurement order; the source atoms are unchanged', default='1,2')
    size: FloatProperty(name='Text size (local scene units)', description='Size of the annotation text in atom-view local scene units', default=.16, min=.001)
    color: FloatVectorProperty(name='Color', description='Initial material color; later edits belong to the material nodes',
                               subtype='COLOR', size=3, default=(0., 0., 0.), min=0, max=1)
    offset: FloatVectorProperty(name='Offset (local scene units)', description='Move text from its atom-centroid anchor without moving source atoms', size=3, default=(.2, .2, .2))
    decimals: IntProperty(name='Decimal places', description='Displayed decimal places; the saved scientific value is unchanged',
                          default=4, min=0, max=10, options={'SKIP_SAVE'})
    show_leader: BoolProperty(name='Show leader', description='Show the line from the annotation anchor to its text', default=True)
    line_width: FloatProperty(name='Leader diameter (local scene units)', description='Diameter of the round leader, independent of measurement strokes', default=.01, min=.0001)
    visible: BoolProperty(name='Visible', description='Show enabled annotation parts; disable to hide the whole annotation', default=True)
    prefix_mode: EnumProperty(name='Prefix mode', description='Choose a fixed or exact custom prefix; the scientific value and unit remain appended', items=[
        ('DEFAULT', 'Default', 'Use the fixed scientific prefix for this annotation kind'),
        ('CUSTOM', 'Custom', 'Use your prefix exactly, including empty text and spaces')], default='DEFAULT')
    prefix: StringProperty(name='Prefix', description='Exact prefix, including Chinese text, empty text and whitespace; the value is appended', default='')
    show_measurement: BoolProperty(name='Show measurement geometry', description='Show distance dashes or the angular arc independently of leader and planes', default=True)
    measurement_width: FloatProperty(name='Measurement diameter (local scene units)', description='Diameter of round measurement strokes, independent of leader diameter', default=.01, min=.0001)
    arc_radius: FloatProperty(name='Arc radius (local scene units)', description='Local radius of the angular arc; the scientific angle is unchanged', default=.5, min=.0001)
    show_planes: BoolProperty(name='Show dihedral planes', description='Show the actual atom triangles 1-2-3 and 2-3-4 independently of arc visibility', default=True)

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def invoke(self, context, event):
        if not self.properties.is_property_set('decimals', ghost=False):
            self.decimals = 4 if self.kind in ('ATOM', 'DISTANCE') else 2
        self.atoms = '1' if self.kind == 'ATOM' else ','.join(str(i) for i in range(1, ATOM_COUNTS[self.kind] + 1))
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.prop(self, 'atoms')
        _draw_style(layout, self, self.kind, creating=True)

    def execute(self, context):
        owner = _atom_view(context)
        try:
            positions, record = current_geometry(owner)
            numbers = parse_source_atom_numbers(self.atoms, len(positions))
            if self.kind != 'ATOM' and len(numbers) != ATOM_COUNTS[self.kind]:
                raise ValueError(f'{self.kind} needs {ATOM_COUNTS[self.kind]} ordered source atom numbers')
            symbols = [_symbol(int(owner.data.attributes['qc_atomic_number'].data[n - 1].value))
                       for n in numbers]
            decimals = self.decimals if self.properties.is_property_set('decimals', ghost=False) else (
                4 if self.kind in ('ATOM', 'DISTANCE') else 2)
            settings = {**_style_values(self, self.kind), 'kind': self.kind,
                        'color': list(self.color), 'decimals': decimals,
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
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_edit_annotation(bpy.types.Operator):
    bl_idname = 'qcblender.edit_annotation'
    bl_label = 'Edit QC Annotation'
    bl_description = 'Edit annotation text, placement and geometry on its atom view; preserve all material nodes'
    bl_options = {'REGISTER', 'UNDO'}

    annotation_id: StringProperty()
    size: FloatProperty(name='Text size (local scene units)', description='Size of the annotation text in atom-view local scene units', default=.16, min=.001)
    offset: FloatVectorProperty(name='Offset (local scene units)', description='Move text from its atom-centroid anchor without moving source atoms', size=3)
    decimals: IntProperty(name='Decimal places', description='Displayed decimal places; the saved scientific value is unchanged', default=4, min=0, max=10)
    show_leader: BoolProperty(name='Show leader', description='Show the line from the annotation anchor to its text', default=True)
    line_width: FloatProperty(name='Leader diameter (local scene units)', description='Diameter of the round leader, independent of measurement strokes', default=.01, min=.0001)
    visible: BoolProperty(name='Visible', description='Show enabled annotation parts; disable to hide the whole annotation', default=True)
    kind: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    prefix_mode: EnumProperty(name='Prefix mode', description='Choose a fixed or exact custom prefix; the scientific value and unit remain appended', items=[
        ('DEFAULT', 'Default', 'Use the fixed scientific prefix for this annotation kind'),
        ('CUSTOM', 'Custom', 'Use your prefix exactly, including empty text and spaces')], default='DEFAULT')
    prefix: StringProperty(name='Prefix', description='Exact prefix, including Chinese text, empty text and whitespace; the value is appended', default='')
    show_measurement: BoolProperty(name='Show measurement geometry', description='Show distance dashes or the angular arc independently of leader and planes', default=True)
    measurement_width: FloatProperty(name='Measurement diameter (local scene units)', description='Diameter of round measurement strokes, independent of leader diameter', default=.01, min=.0001)
    arc_radius: FloatProperty(name='Arc radius (local scene units)', description='Local radius of the angular arc; the scientific angle is unchanged', default=.5, min=.0001)
    show_planes: BoolProperty(name='Show dihedral planes', description='Show the actual atom triangles 1-2-3 and 2-3-4 independently of arc visibility', default=True)

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def invoke(self, context, event):
        owner = _atom_view(context)
        entry = next((entry for _, entry in _entries(owner, 'LABEL')
                      if entry['id'] == self.annotation_id), None)
        if entry is None:
            self.report({'ERROR'}, error_text('Annotation no longer exists'))
            return {'CANCELLED'}
        self.kind = entry['kind']
        for name in ('size', 'offset', 'decimals', 'show_leader', 'line_width', 'visible', *STYLE_DEFAULTS):
            setattr(self, name, entry.get(name, STYLE_DEFAULTS.get(name)))
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        _draw_style(self.layout, self, self.kind)

    def execute(self, context):
        owner = _atom_view(context)
        try:
            positions, record = current_geometry(owner)
            prepared = prepare_annotations(owner, positions, record)
            found = next((item for item in prepared if item[1]['id'] == self.annotation_id), None)
            if found is None:
                raise ValueError('Annotation no longer exists')
            child, entry, _, _, leader = found
            entry.update(_style_values(self, entry['kind']))
            entry, anchor, body = _prepare(entry, positions, record)
            _ensure_legacy_font(child, body)
            _upgrade_parts(child, entry, leader, owner.users_collection[0])
            leader.geometry = measurement_geometry(entry['kind'], positions, entry['source_atom_numbers'], entry['arc_radius'])
            _apply(child, entry, anchor, body, leader)
        except (ValueError, KeyError, OSError, TypeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def _material_snapshot(owner):
    return json.dumps([(identifier, [(role, obj.name,
        [mat.name if mat is not None else None for mat in obj.data.materials])
        for role, (obj, _) in sorted(group.items())]) for identifier, group in sorted(_groups(owner).items())])


class QCBLENDER_OT_unify_annotation_materials(bpy.types.Operator):
    bl_idname = 'qcblender.unify_annotation_materials'
    bl_label = 'Unify Annotation Materials'
    bl_description = 'Preview and unify annotation material groups on the current atom view; keep old material nodes as saved backups'
    bl_options = {'REGISTER', 'UNDO'}

    preview: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    count: IntProperty(options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def invoke(self, context, event):
        try:
            owner = _atom_view(context)
            self.count = len(material_unification_plan(owner))
            self.preview = _material_snapshot(owner)
        except (ValueError, KeyError, TypeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=560)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.label(text=iface('Preview {count} annotations that need independent, shared materials', count=self.count))
        layout.label(text='Existing material nodes are preserved as saved backup datablocks')

    def execute(self, context):
        try:
            owner = _atom_view(context)
            if self.preview and self.preview != _material_snapshot(owner):
                raise ValueError('Annotation materials changed since preview; preview again')
            count = unify_annotation_materials(owner)
        except (ValueError, KeyError, TypeError, RuntimeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        self.report({'INFO'}, iface('Unified materials for {count} annotations', count=count)
                    if count else iface('No annotation materials need unifying'))
        return {'FINISHED'}


class QCBLENDER_OT_face_annotations(bpy.types.Operator):
    bl_idname = 'qcblender.face_annotations'
    bl_label = 'Face QC Annotations to Camera'
    bl_options = {'REGISTER', 'UNDO'}

    annotation_id: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def description(cls, context, properties):
        return tip('Face this annotation label to the active scene camera; leave geometry unchanged'
                   if properties.annotation_id else
                   'Face every annotation label of the current atom view to the active scene camera')

    @classmethod
    def poll(cls, context):
        return _atom_view(context) is not None

    def execute(self, context):
        camera = context.scene.camera
        if camera is None:
            self.report({'ERROR'}, error_text('Set an active scene camera first'))
            return {'CANCELLED'}
        owner = _atom_view(context)
        identifier = self.annotation_id if self.properties.is_property_set('annotation_id', ghost=False) else ''
        rotation = owner.matrix_world.to_quaternion().inverted() @ camera.matrix_world.to_quaternion()
        matched = False
        for child, entry in _entries(owner, 'LABEL'):
            if not identifier or entry['id'] == identifier:
                child.rotation_mode = 'QUATERNION'
                child.rotation_quaternion = rotation
                matched = True
        if identifier and not matched:
            self.report({'ERROR'}, error_text('Annotation no longer exists'))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_remove_annotation(bpy.types.Operator):
    bl_idname = 'qcblender.remove_annotation'
    bl_label = 'Remove QC Annotation'
    bl_description = 'Remove this annotation label and its own geometry parts; preserve source atoms and user materials'
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
    layout = ui_layout(layout)
    owner = _atom_view(context)
    if owner is None:
        return
    box = layout.box()
    box.label(text='Source Atom Annotations')
    row = box.row(align=True)
    for kind, title in [('ATOM', 'Atoms'), ('DISTANCE', 'Distance'), ('ANGLE', 'Angle'), ('DIHEDRAL', 'Dihedral')]:
        row.operator('qcblender.add_annotation', text=title).kind = kind
    box.operator('qcblender.face_annotations', text='Face All to Camera', icon='CAMERA_DATA').annotation_id = ''
    box.operator('qcblender.unify_annotation_materials', text='Unify Annotation Materials', icon='MATERIAL')
    for _, entry in _entries(owner, 'LABEL'):
        row = box.row(align=True)
        status = iface('Undefined' if entry.get('undefined_reason') else entry['kind'].title())
        row.label(text=f"{','.join(map(str, entry['source_atom_numbers']))}: {status}", translate=False)
        row.operator('qcblender.edit_annotation', text='', icon='PREFERENCES').annotation_id = entry['id']
        row.operator('qcblender.face_annotations', text='', icon='CAMERA_DATA').annotation_id = entry['id']
        row.operator('qcblender.remove_annotation', text='', icon='X').annotation_id = entry['id']
