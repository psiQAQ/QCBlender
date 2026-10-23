"""Independent calculated pairs, sampled against the IRC atom selection field."""
import json
import math

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty
import numpy as np

from ..data import load_dataset
from ..i18n import error_text, iface, ui_layout
from ..mayer import color_range, display_samples
from .graph import geometry_output, view_modifier
from .node_identity import node_socket
from .views import socket


STYLE = 'Style (0 ball-stick, 1 space-fill, 2 bonds)'
PART = 'qc_mayer_part'


def irc_root(obj):
    return obj if obj and obj.get('qc_irc') else obj.parent if obj and obj.parent and obj.parent.get('qc_irc') else None


def mayer_table(root):
    tables = [child for child in root.children if child.get('qc_analysis_role') == 'irc_mayer'] if root else []
    if len(tables) > 1:
        raise ValueError('IRC path has more than one Mayer result')
    return tables[0] if tables else None


def settings(table, data):
    low, high = color_range(data)
    return json.loads(table['qc_mayer_settings']) if 'qc_mayer_settings' in table else {
        'range_mode': 'FULL', 'minimum': low, 'maximum': high,
        'use_threshold': False, 'threshold': 0., 'show_legend': True,
        'legend_position': [3., 0., 0.], 'legend_rotation': [0., 0., 0.]}


def _source(target):
    if len(target.links) != 1:
        raise ValueError('Mayer display requires an intact QC atom graph')
    return target.links[0].from_socket


def _parts(root):
    tree = view_modifier(root).node_group
    parts = {node[PART]: node for node in tree.nodes if PART in node}
    if len(parts) != sum(PART in node for node in tree.nodes):
        raise ValueError('Mayer display graph is ambiguous')
    return tree, parts


def checked_parts(root, style):
    """Recognize only the owned Mayer branch before standard graph validation."""
    _, parts = _parts(root)
    if not parts and not root.get('qc_mayer_enabled'):
        return parts
    kinds = {'bonds': 'GeometryNodeGroup', 'edges': 'GeometryNodeDeleteGeometry',
             'style': 'GeometryNodeSwitch', 'show': 'GeometryNodeSwitch', 'join': 'GeometryNodeJoinGeometry'}
    table = mayer_table(root)
    carrier = table.get('qc_mayer_carrier_object') if table else None
    if (not root.get('qc_irc') or set(parts) != set(kinds)
            or any(parts[role].bl_idname != kind for role, kind in kinds.items())
            or carrier is None or carrier.parent != root or carrier.type != 'MESH'
            or not carrier.get('qc_mayer_carrier') or carrier.data.users != 1):
        raise ValueError('Mayer display graph or pair carrier is missing or shared')
    bonds, edges, small, show, join = (parts[role] for role in ('bonds', 'edges', 'style', 'show', 'join'))
    group = bonds.node_tree
    if group is None or group.get('qc_mayer_version') != 1 or group.users != 1:
        raise ValueError('Mayer display graph or pair carrier is missing or shared')
    sources = [node for node in group.nodes if node.bl_idname == 'GeometryNodeObjectInfo']
    if (len(sources) != 1 or sources[0].transform_space != 'RELATIVE'
            or node_socket(sources[0].inputs, 'Object').default_value != carrier
            or node_socket(sources[0].inputs, 'Object').is_linked
            or edges.domain != 'EDGE' or edges.mode != 'EDGE_FACE'
            or small.input_type != 'INT' or show.input_type != 'GEOMETRY'
            or _source(node_socket(style.inputs, 'Geometry')) != node_socket(edges.outputs, 'Geometry')
            or _source(node_socket(style.inputs, STYLE)) != node_socket(small.outputs, 'Output')
            or _source(node_socket(bonds.inputs, 'Atoms')) != _source(node_socket(edges.inputs, 'Geometry'))
            or _source(node_socket(bonds.inputs, 'Visible')) != _source(node_socket(style.inputs, 'Selection'))
            or _source(node_socket(bonds.inputs, 'Bond Radius')) != _source(node_socket(style.inputs, 'Bond Radius'))
            or _source(node_socket(show.inputs, 'True')) != node_socket(bonds.outputs, 'Geometry')
            or node_socket(show.inputs, 'False').is_linked
            or node_socket(small.inputs, 'True').is_linked or node_socket(small.inputs, 'True').default_value != 0):
        raise ValueError('Mayer display requires an intact QC atom graph')
    for node, name in ((edges, 'Selection'), (small, 'Switch'), (show, 'Switch')):
        control = node_socket(node.inputs, name)
        if control.is_linked or bool(control.default_value) != bool(root.get('qc_mayer_enabled')):
            raise ValueError('Mayer display requires an intact QC atom graph')
    branches = [link.from_socket for link in node_socket(join.inputs, 'Geometry').links]
    if len(branches) != 2 or branches.count(node_socket(show.outputs, 'Output')) != 1:
        raise ValueError('Mayer display requires an intact QC atom graph')
    return parts


def original_output(parts, displayed):
    if parts and displayed == node_socket(parts['join'].outputs, 'Geometry'):
        return next(link.from_socket for link in node_socket(parts['join'].inputs, 'Geometry').links
                    if link.from_socket != node_socket(parts['show'].outputs, 'Output'))
    return displayed


def _style(root):
    from .atom_selection import _preflight
    tree = _preflight(root)[0]
    return tree, next(node for node in tree.nodes if node.type == 'GROUP' and node.node_tree
                     and node.node_tree.get('qc_asset_id') == 'qc.atom_style.v1')


def _data(root):
    from .geometry import current_geometry
    from .source_browser import read_metadata
    table = mayer_table(root)
    if table is None:
        raise ValueError('Import Mayer results for this IRC path first')
    read_metadata(table)
    path = load_dataset(bpy.path.abspath(root['qc_dataset']))
    current_geometry(root, path)
    data = load_dataset(bpy.path.abspath(table['qc_dataset']))
    return table, path, data


def _mesh_samples(mesh, samples):
    positions, atom_ids, values, pair_ids = samples
    mesh.vertices.foreach_set('co', positions.ravel())
    for name, members in (('qc_mayer_atom', atom_ids), ('qc_mayer_value', values), ('qc_mayer_pair', pair_ids)):
        mesh.attributes[name].data.foreach_set('value', members)
    mesh.update()


def _new_carrier(root, samples):
    positions = samples[0]
    mesh = bpy.data.meshes.new('QC Mayer source pairs')
    mesh.from_pydata(positions.tolist(), [(i, i + 1) for i in range(0, len(positions), 2)], [])
    for name, kind in (('qc_mayer_atom', 'INT'), ('qc_mayer_value', 'FLOAT'), ('qc_mayer_pair', 'INT')):
        mesh.attributes.new(name, kind, 'POINT')
    _mesh_samples(mesh, samples)
    obj = bpy.data.objects.new('QC Mayer pair carrier', mesh)
    root.users_collection[0].objects.link(obj)
    obj.parent = root
    obj['qc_mayer_carrier'] = True
    obj.hide_render = True
    obj.hide_set(True)
    return obj


def _display_group(root, carrier):
    from ..color_presets import get_preset
    from .assets import math as node_math
    from .color_presets import _write_ramp
    from .scalars import add_legend, color_fraction, scalar_material
    tree = bpy.data.node_groups.new('QC Mayer display', 'GeometryNodeTree')
    tree['qc_mayer_version'] = 1
    tree['qc_asset_id'] = 'qc.mayer_display.v1'
    for name, kind, value in [('Atoms', 'NodeSocketGeometry', None), ('Visible', 'NodeSocketBool', True),
                             ('Bond Radius', 'NodeSocketFloat', .07),
                             ('Color Minimum', 'NodeSocketFloat', 0.), ('Color Center', 'NodeSocketFloat', .5),
                             ('Color Maximum', 'NodeSocketFloat', 1.), ('Use Lower Limit', 'NodeSocketBool', False),
                             ('Lower Limit', 'NodeSocketFloat', 0.)]:
        socket(tree, name, kind, default=value)
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    info = nodes.new('GeometryNodeObjectInfo')
    info.transform_space = 'RELATIVE'
    node_socket(info.inputs, 'Object').default_value = carrier
    attributes = {}
    for name, kind in [('qc_mayer_atom', 'INT'), ('qc_mayer_value', 'FLOAT')]:
        attr = nodes.new('GeometryNodeInputNamedAttribute')
        attr.data_type = kind
        node_socket(attr.inputs, 'Name').default_value = name
        attributes[name] = node_socket(attr.outputs, 'Attribute')
    selected = nodes.new('GeometryNodeSampleIndex')
    selected.data_type, selected.domain, selected.clamp = 'BOOLEAN', 'POINT', False
    links.new(node_socket(inputs.outputs, 'Atoms'), node_socket(selected.inputs, 'Geometry'))
    links.new(node_socket(inputs.outputs, 'Visible'), node_socket(selected.inputs, 'Value'))
    links.new(attributes['qc_mayer_atom'], node_socket(selected.inputs, 'Index'))
    below = node_math(tree, 'LESS_THAN', attributes['qc_mayer_value'], node_socket(inputs.outputs, 'Lower Limit'))
    rejected = node_math(tree, 'MULTIPLY', below, node_socket(inputs.outputs, 'Use Lower Limit'))
    visible = node_math(tree, 'MULTIPLY', node_socket(selected.outputs, 'Value'), node_math(tree, 'SUBTRACT', 1., rejected))
    delete = nodes.new('GeometryNodeDeleteGeometry')
    delete.domain = 'POINT'
    links.new(node_socket(info.outputs, 'Geometry'), node_socket(delete.inputs, 'Geometry'))
    links.new(node_math(tree, 'SUBTRACT', 1., visible), node_socket(delete.inputs, 'Selection'))
    fraction = color_fraction(tree, inputs, attributes['qc_mayer_value'], 'Color Minimum', 'Color Center', 'Color Maximum')
    constant = nodes.new('GeometryNodeSwitch')
    constant.input_type = 'FLOAT'
    links.new(node_math(tree, 'COMPARE', node_socket(inputs.outputs, 'Color Minimum'), node_socket(inputs.outputs, 'Color Maximum'), 0.),
              node_socket(constant.inputs, 'Switch'))
    links.new(fraction, node_socket(constant.inputs, 'False'))
    node_socket(constant.inputs, 'True').default_value = .5
    geometry = node_socket(delete.outputs, 'Geometry')
    for name, kind, value in [('qc_color_fraction', 'FLOAT', node_socket(constant.outputs, 'Output')),
                              ('qc_sample_valid', 'BOOLEAN', True)]:
        store = nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        node_socket(store.inputs, 'Name').default_value = name
        links.new(geometry, node_socket(store.inputs, 'Geometry'))
        if value is True:
            node_socket(store.inputs, 'Value').default_value = True
        else:
            links.new(value, node_socket(store.inputs, 'Value'))
        geometry = node_socket(store.outputs, 'Geometry')
    curves = nodes.new('GeometryNodeMeshToCurve')
    links.new(geometry, node_socket(curves.inputs, 'Mesh'))
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    node_socket(circle.inputs, 'Resolution').default_value = 12
    links.new(node_socket(inputs.outputs, 'Bond Radius'), node_socket(circle.inputs, 'Radius'))
    tubes = nodes.new('GeometryNodeCurveToMesh')
    links.new(node_socket(curves.outputs, 'Curve'), node_socket(tubes.inputs, 'Curve'))
    links.new(node_socket(circle.outputs, 'Curve'), node_socket(tubes.inputs, 'Profile Curve'))
    node_socket(tubes.inputs, 'Fill Caps').default_value = True
    mat = scalar_material()
    mat.name = 'QC Mayer Viridis'
    ramp = next(node.color_ramp for node in mat.node_tree.nodes if node.get('qc_role') == 'color_ramp')
    preset = get_preset('VIRIDIS')
    _write_ramp(ramp, {name: getattr(preset, name) for name in ('elements', 'interpolation', 'color_mode', 'hue_interpolation')})
    assign = nodes.new('GeometryNodeSetMaterial')
    node_socket(assign.inputs, 'Material').default_value = mat
    links.new(node_socket(tubes.outputs, 'Mesh'), node_socket(assign.inputs, 'Geometry'))
    links.new(node_socket(assign.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
    add_legend(root, mat, 'Color Minimum', 'Color Center', 'Color Maximum',
               iface('Mayer bond order (dimensionless)'), tree=tree)
    from .graph import arrange
    arrange(tree)
    return tree


def _create(root, table, samples):
    tree, style = _style(root)
    if _parts(root)[1]:
        raise ValueError('Mayer display graph is incomplete')
    if tree.get('qc_color_mapping'):
        raise ValueError('Use an IRC atom view without a scalar color field for Mayer display')
    geometry_input = node_socket(style.inputs, 'Geometry')
    style_input = node_socket(style.inputs, STYLE)
    original_geometry, original_style = _source(geometry_input), _source(style_input)
    output = geometry_output(tree)
    original_output = _source(output)
    before_objects, before_groups, before_materials = set(bpy.data.objects), set(bpy.data.node_groups), set(bpy.data.materials)
    created = []
    try:
        carrier = _new_carrier(root, samples)
        group = _display_group(root, carrier)
        def node(kind, role):
            result = tree.nodes.new(kind)
            result[PART] = role
            created.append(result)
            return result
        bonds = node('GeometryNodeGroup', 'bonds')
        bonds.node_tree = group
        tree.links.new(original_geometry, node_socket(bonds.inputs, 'Atoms'))
        tree.links.new(_source(node_socket(style.inputs, 'Selection')), node_socket(bonds.inputs, 'Visible'))
        tree.links.new(_source(node_socket(style.inputs, 'Bond Radius')), node_socket(bonds.inputs, 'Bond Radius'))
        edges = node('GeometryNodeDeleteGeometry', 'edges')
        edges.domain, edges.mode = 'EDGE', 'EDGE_FACE'
        node_socket(edges.inputs, 'Selection').default_value = False
        tree.links.new(original_geometry, node_socket(edges.inputs, 'Geometry'))
        tree.links.new(node_socket(edges.outputs, 'Geometry'), geometry_input)
        small = node('GeometryNodeSwitch', 'style')
        small.input_type = 'INT'
        tree.links.new(original_style, node_socket(small.inputs, 'False'))
        node_socket(small.inputs, 'True').default_value = 0
        tree.links.new(node_socket(small.outputs, 'Output'), style_input)
        show = node('GeometryNodeSwitch', 'show')
        show.input_type = 'GEOMETRY'
        tree.links.new(node_socket(bonds.outputs, 'Geometry'), node_socket(show.inputs, 'True'))
        join = node('GeometryNodeJoinGeometry', 'join')
        tree.links.new(original_output, node_socket(join.inputs, 'Geometry'))
        tree.links.new(node_socket(show.outputs, 'Output'), node_socket(join.inputs, 'Geometry'))
        tree.links.new(node_socket(join.outputs, 'Geometry'), output)
        table['qc_mayer_carrier_object'] = carrier
        root['qc_mayer_enabled'] = False
    except Exception:
        for item in created:
            tree.nodes.remove(item)
        tree.links.new(original_geometry, geometry_input)
        tree.links.new(original_style, style_input)
        tree.links.new(original_output, output)
        for obj in set(bpy.data.objects) - before_objects:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        for group in set(bpy.data.node_groups) - before_groups:
            bpy.data.node_groups.remove(group)
        for mat in set(bpy.data.materials) - before_materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        raise


def prepare_update(root, path, step, data=None):
    tree, parts = _parts(root)
    if not parts and not root.get('qc_mayer_enabled'):
        return None
    _style(root)
    table = mayer_table(root)
    carrier = table['qc_mayer_carrier_object']
    if data is None:
        from .source_browser import read_metadata
        read_metadata(table)
        data = load_dataset(bpy.path.abspath(table['qc_dataset']))
    samples = display_samples(path, data, step)
    mesh = carrier.data
    if len(mesh.vertices) != len(samples[0]) or len(mesh.edges) != len(samples[0]) // 2:
        raise ValueError('Mayer pair carrier topology differs from imported pairs')
    edges = np.empty(len(mesh.edges) * 2, dtype=np.int32)
    mesh.edges.foreach_get('vertices', edges)
    if not np.array_equal(edges, np.arange(len(samples[0]))):
        raise ValueError('Mayer pair carrier topology differs from imported pairs')
    for name, kind, expected in [('qc_mayer_atom', 'INT', samples[1]), ('qc_mayer_pair', 'INT', samples[3]),
                                  ('qc_mayer_value', 'FLOAT', None)]:
        attr = mesh.attributes.get(name)
        if attr is None or attr.domain != 'POINT' or attr.data_type != kind or len(attr.data) != len(samples[0]):
            raise ValueError('Mayer pair carrier attributes are missing or invalid')
        if expected is not None and [item.value for item in attr.data] != expected.tolist():
            raise ValueError('Mayer pair carrier atom identities differ from imported pairs')
    return carrier, samples


def apply_update(prepared):
    if prepared:
        _mesh_samples(prepared[0].data, prepared[1])


def configure(root, enabled, config=None):
    table, path, data = _data(root)
    samples = display_samples(path, data, int(root['qc_irc_step']))
    config = settings(table, data) if config is None else config
    if config['range_mode'] not in {'FULL', 'MANUAL'} or not math.isfinite(config['threshold']):
        raise ValueError('Mayer display settings are invalid')
    if any(np.asarray(config[name]).shape != (3,) or not np.isfinite(config[name]).all()
           for name in ('legend_position', 'legend_rotation')):
        raise ValueError('Mayer display settings are invalid')
    low, high = color_range(data, (config['minimum'], config['maximum']) if config['range_mode'] == 'MANUAL' else None)
    if not _parts(root)[1]:
        _create(root, table, samples)
    prepared = prepare_update(root, path, int(root['qc_irc_step']), data)
    tree, parts = _parts(root)
    apply_update(prepared)
    for role, control in [('edges', 'Selection'), ('style', 'Switch'), ('show', 'Switch')]:
        node_socket(parts[role].inputs, control).default_value = enabled
    bonds = parts['bonds']
    for name, value in [('Color Minimum', low), ('Color Center', (low + high) / 2), ('Color Maximum', high),
                        ('Use Lower Limit', config['use_threshold']), ('Lower Limit', config['threshold']),
                        ('Show Legend', config['show_legend']), ('Legend Position', config['legend_position']),
                        ('Legend Rotation', config['legend_rotation'])]:
        node_socket(bonds.inputs, name).default_value = value
    table['qc_mayer_settings'] = json.dumps({**config, 'minimum': low, 'maximum': high}, sort_keys=True)
    root['qc_mayer_enabled'] = enabled
    root.update_tag()


class QCBLENDER_OT_mayer_display(bpy.types.Operator):
    bl_idname = 'qcblender.mayer_display'
    bl_label = 'Mayer Display'
    bl_description = 'Show calculated Mayer pairs with atom balls; disabling restores the existing atom representation'
    bl_options = {'REGISTER', 'UNDO'}
    enabled: BoolProperty(name='Show Mayer Bonds', default=True)

    @classmethod
    def poll(cls, context):
        root = irc_root(context.object)
        return root is not None and any(child.get('qc_analysis_role') == 'irc_mayer' for child in root.children)

    def execute(self, context):
        try:
            configure(irc_root(context.object), self.enabled)
        except (ValueError, OSError, KeyError, TypeError, MemoryError, RuntimeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_mayer_settings(bpy.types.Operator):
    bl_idname = 'qcblender.mayer_settings'
    bl_label = 'Mayer Display Settings'
    bl_description = 'Set the Mayer color range, lower bond-order limit and legend without changing imported values'
    bl_options = {'REGISTER', 'UNDO'}
    range_mode: EnumProperty(name='Mayer Color Range', items=[('FULL', 'Entire IRC Path', ''), ('MANUAL', 'Manual Range', '')], default='FULL')
    minimum: FloatProperty(name='Minimum', default=0.)
    maximum: FloatProperty(name='Maximum', default=1.)
    use_threshold: BoolProperty(name='Filter by Lower Bond Order', default=False)
    threshold: FloatProperty(name='Minimum Mayer Order', default=0.)
    show_legend: BoolProperty(name='Show Legend', default=True)
    legend_position: FloatVectorProperty(name='Legend Position', default=(3., 0., 0.))
    legend_rotation: FloatVectorProperty(name='Legend Rotation', subtype='EULER', default=(0., 0., 0.))

    @classmethod
    def poll(cls, context):
        return QCBLENDER_OT_mayer_display.poll(context)

    def invoke(self, context, event):
        try:
            table, _, data = _data(irc_root(context.object))
            for name, value in settings(table, data).items():
                setattr(self, name, value)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=440)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.label(text='Viridis; values are dimensionless')
        layout.prop(self, 'range_mode')
        bounds = layout.row()
        bounds.enabled = self.range_mode == 'MANUAL'
        bounds.prop(self, 'minimum')
        bounds.prop(self, 'maximum')
        layout.prop(self, 'use_threshold')
        row = layout.row()
        row.enabled = self.use_threshold
        row.prop(self, 'threshold')
        layout.prop(self, 'show_legend')
        if self.show_legend:
            layout.prop(self, 'legend_position')
            layout.prop(self, 'legend_rotation')

    def execute(self, context):
        try:
            root = irc_root(context.object)
            config = {name: getattr(self, name) for name in
                      ('range_mode', 'minimum', 'maximum', 'use_threshold', 'threshold', 'show_legend')}
            config.update({name: list(getattr(self, name)) for name in ('legend_position', 'legend_rotation')})
            configure(root, bool(root.get('qc_mayer_enabled')), config)
        except (ValueError, OSError, KeyError, TypeError, MemoryError, RuntimeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def draw_controls(layout, root):
    table = mayer_table(root)
    if table is None:
        return
    box = layout.box()
    active = bool(root.get('qc_mayer_enabled'))
    box.operator('qcblender.mayer_display', text='Show Mayer Bonds', depress=active).enabled = not active
    box.operator('qcblender.mayer_settings')
    if active:
        box.label(text='Atom balls and calculated pairs; source data retained')
    if 'qc_mayer_settings' in table:
        config = json.loads(table['qc_mayer_settings'])
        box.label(text=iface('Mayer range: {value0:.6g} to {value1:.6g}', value0=config['minimum'], value1=config['maximum']))
