"""Native flat distance maps with explicit validity, projected atoms and contours."""
import json
import math

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
import numpy as np

from ..i18n import error_text, iface, ui_layout
from ..surface_projection import VALID, UNKNOWN, color_range, grid_positions
from .graph import tag_view, view_modifier
from .node_identity import node_socket, socket_name
from .views import bind, material, socket


def settings(obj):
    return json.loads(obj['qc_projection_settings'])


def _input(obj, name, value):
    modifier = view_modifier(obj)
    item = next(item for item in modifier.node_group.interface.items_tree
                if item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                and socket_name(item, modifier.node_group) == name)
    modifier[item.identifier] = value


def _color_material(palette):
    from .scalars import scalar_material
    from .color_presets import _write_ramp
    from ..color_presets import get_preset
    mat = scalar_material()
    mat.name = 'QC Projection ' + palette
    ramp = next(node.color_ramp for node in mat.node_tree.nodes if node.get('qc_role') == 'color_ramp')
    preset = get_preset(palette)
    _write_ramp(ramp, {name: getattr(preset, name) for name in ('elements', 'interpolation', 'color_mode', 'hue_interpolation')})
    mat['qc_projection_palette'] = palette
    emission = next(node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeEmission')
    output = next(node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_socket(emission.outputs, 0), node_socket(output.inputs, 'Surface'))
    return mat


def _flat_material(name, color, attribute=None):
    mat = material(name, color, attribute)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    emission = nodes.new('ShaderNodeEmission')
    node_socket(emission.inputs, 'Color').default_value = color
    if attribute:
        source = next(node for node in nodes if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == attribute)
        links.new(node_socket(source.outputs, 'Color'), node_socket(emission.inputs, 'Color'))
    output = next(node for node in nodes if node.bl_idname == 'ShaderNodeOutputMaterial')
    links.new(node_socket(emission.outputs, 0), node_socket(output.inputs, 'Surface'))
    return mat


def _edges(axis):
    return np.concatenate(([axis[0] - (axis[1] - axis[0]) / 2],
                           (axis[1:] + axis[:-1]) / 2,
                           [axis[-1] + (axis[-1] - axis[-2]) / 2]))


def _mesh(data, config, low, high):
    x, y = _edges(data.arrays['projection_x']), _edges(data.arrays['projection_y'])
    state, depth = data.arrays['projection_state'], data.arrays['projection_depth']
    selected = (state == VALID) | ((state == UNKNOWN) & config['show_unknown'])
    ix, iy = np.nonzero(selected)
    vertices = np.zeros((len(ix), 4, 3))
    vertices[:, :, 0] = np.stack((x[ix], x[ix+1], x[ix+1], x[ix]), axis=1)
    vertices[:, :, 1] = np.stack((y[iy], y[iy], y[iy+1], y[iy+1]), axis=1)
    mesh = bpy.data.meshes.new('QC Projection samples')
    mesh.from_pydata(vertices.reshape(-1, 3).tolist(), [], np.arange(len(ix) * 4).reshape(-1, 4).tolist())
    mesh.update()
    fractions = np.clip((depth[ix, iy] - low) / (high - low), 0., 1.)
    for name, kind, values in (
            ('qc_color_fraction', 'FLOAT', fractions), ('qc_sample_valid', 'BOOLEAN', state[ix, iy] == VALID),
            ('qc_projection_depth', 'FLOAT', depth[ix, iy]), ('qc_projection_state', 'INT', state[ix, iy]),
            ('qc_projection_ix', 'INT', ix), ('qc_projection_iy', 'INT', iy)):
        attr = mesh.attributes.new(name, kind, 'POINT')
        attr.data.foreach_set('value', np.repeat(values, 4))
    for face, sample_state in zip(mesh.polygons, state[ix, iy]):
        face.material_index = int(sample_state == UNKNOWN)
    return mesh


def _part(root, obj, role):
    bpy.context.collection.objects.link(obj)
    obj.parent = root
    obj['qc_projection_part'] = role
    obj.hide_select = True
    return obj


def _curve(root, name, lines, role, width, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions, curve.bevel_depth, curve.bevel_resolution = '3D', width, 1
    curve.resolution_u = 1
    for line in lines:
        spline = curve.splines.new('POLY')
        spline.points.add(len(line) - 1)
        spline.points.foreach_set('co', [coordinate for point in line for coordinate in (*point, 1.)])
    curve.materials.append(mat)
    return _part(root, bpy.data.objects.new(name, curve), role)


def _text(root, body, position, size, mat, role='axes', align='CENTER'):
    from .annotation_fonts import annotation_font
    curve = bpy.data.curves.new('QC Projection label', 'FONT')
    curve.font = annotation_font()
    curve.body, curve.size, curve.align_x = body, size, align
    curve.materials.append(mat)
    obj = _part(root, bpy.data.objects.new('QC Projection label', curve), role)
    obj.location = position
    return obj


def _axes_and_atoms(root, data):
    x, y = data.arrays['projection_x'], data.arrays['projection_y']
    ex, ey = _edges(x), _edges(y)
    dark = _flat_material('QC Projection axes', (.015, .015, .015, 1.))
    lines = [[(ex[0], ey[0], .04), (ex[-1], ey[0], .04)],
             [(ex[0], ey[0], .04), (ex[0], ey[-1], .04)]]
    for value in np.linspace(x[0], x[-1], 5):
        lines.append([(value, ey[0], .04), (value, ey[0] - .12, .04)])
        _text(root, f'{value:g}', (value, ey[0] - .52, .04), .8, dark)
    for value in np.linspace(y[0], y[-1], 5):
        lines.append([(ex[0], value, .04), (ex[0] - .12, value, .04)])
        _text(root, f'{value:g}', (ex[0] - .22, value - .1, .04), .8, dark, align='RIGHT')
    _curve(root, 'QC Projection axes', lines, 'axes', .012, dark)
    _text(root, 'X / Å', (ex[-1] + .25, ey[0] - .5, .04), .9, dark, align='LEFT')
    _text(root, 'Y / Å', (ex[0], ey[-1] + .35, .04), .9, dark)
    _text(root, iface('Gray: unknown | Blank: missed'), ((x[0] + x[-1]) / 2, ey[-1] + .35, .04), 1., dark)
    vertices, faces, colors, ids = [], [], [], []
    palette = {1: (.85, .85, .85, 1), 6: (.12, .16, .2, 1), 7: (.12, .22, .8, 1),
               8: (.85, .08, .06, 1), 9: (.1, .65, .15, 1), 15: (1., .4, .05, 1),
               16: (.9, .7, .05, 1), 17: (.1, .65, .15, 1)}
    for atom_id, (number, position) in enumerate(zip(data.arrays['atomic_numbers'], data.arrays['positions'])):
        start = len(vertices)
        vertices.extend([(position[0] + .075 * math.cos(2 * math.pi * i / 16),
                          position[1] + .075 * math.sin(2 * math.pi * i / 16), .12) for i in range(16)])
        faces.append(tuple(range(start, start + 16)))
        colors.extend([palette.get(int(number), (.45, .35, .6, 1))] * 16)
        ids.extend([atom_id] * 16)
    mesh = bpy.data.meshes.new('QC Projected atom markers')
    mesh.from_pydata(vertices, [], faces)
    mesh.color_attributes.new('qc_element_color', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.array(colors).ravel())
    mesh.attributes.new('qc_atom_id', 'INT', 'POINT').data.foreach_set('value', ids)
    mesh.materials.append(_flat_material('QC Projected elements', (.4, .4, .4, 1), 'qc_element_color'))
    _part(root, bpy.data.objects.new('QC Projected atoms', mesh), 'atoms')


def _contours(data, config, low, high):
    if not config['show_contours']:
        return []
    from ..contours import levels_from_samples, trace_contours
    values, valid = data.arrays['projection_depth'], data.arrays['projection_state'] == VALID
    levels = levels_from_samples(values, valid, config['contour_levels'],
                                 {'minimum': low, 'center': (low + high) / 2, 'maximum': high})
    positions = grid_positions(data, .045)
    return [(level, trace_contours(values, valid, positions, level)) for level in levels]


def _set_point(obj, data, ix, iy):
    from ..surface_projection import STATE_NAMES
    if not 0 <= ix < len(data.arrays['projection_x']) or not 0 <= iy < len(data.arrays['projection_y']):
        raise ValueError('Projection point index is outside the grid')
    obj['qc_projection_point'] = json.dumps({'ix': ix, 'iy': iy,
        'x': float(data.arrays['projection_x'][ix]), 'y': float(data.arrays['projection_y'][iy]),
        'depth': float(data.arrays['projection_depth'][ix, iy]),
        'state': STATE_NAMES[int(data.arrays['projection_state'][ix, iy])]})


def apply_settings(obj, data, config):
    from ..color_presets import get_preset
    get_preset(config['palette'])
    low, high = color_range(data, (config['minimum'], config['maximum']) if config['manual_range'] else None)
    contours = _contours(data, config, low, high)
    if not math.isfinite(config['contour_width']) or config['contour_width'] <= 0:
        raise ValueError('Projection contour width must be positive and finite')
    # Resolve the graph and existing materials before replacing generated geometry.
    modifier = view_modifier(obj)
    old_mesh = obj.data
    old_mat = old_mesh.materials[0]
    ramp = next(node.color_ramp for node in old_mat.node_tree.nodes if node.get('qc_role') == 'color_ramp')
    mesh = _mesh(data, config, low, high)
    from .color_presets import _write_ramp
    preset = get_preset(config['palette'])
    _write_ramp(ramp, {name: getattr(preset, name) for name in ('elements', 'interpolation', 'color_mode', 'hue_interpolation')})
    old_mat['qc_projection_palette'] = config['palette']
    for mat in old_mesh.materials:
        mesh.materials.append(mat)
    obj.data = mesh
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    for name, value in (('Color Minimum', low), ('Color Center', (low + high) / 2),
                        ('Color Maximum', high), ('Show Legend', config['show_legend'])):
        _input(obj, name, value)
    for child in list(obj.children):
        role = child.get('qc_projection_part')
        if role == 'contours':
            curve = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if curve.users == 0:
                bpy.data.curves.remove(curve)
        elif role == 'atoms':
            child.hide_viewport = child.hide_render = not config['show_atoms']
    if contours:
        mat = next(child.data.materials[0] for child in obj.children if child.get('qc_projection_part') == 'axes')
        for level, lines in contours:
            if lines:
                child = _curve(obj, 'QC Projection contour', lines, 'contours', config['contour_width'], mat)
                child['qc_projection_level'] = level
    obj['qc_projection_settings'] = json.dumps({**config, 'minimum': low, 'maximum': high}, sort_keys=True)
    obj.update_tag()
    modifier.node_group.interface_update(bpy.context)


def create_view(directory, data, reference):
    from .scalars import add_legend
    config = {'palette': 'VIRIDIS', 'manual_range': False, 'minimum': -6., 'maximum': 0.,
              'show_atoms': True, 'show_unknown': True, 'show_legend': True,
              'show_contours': False, 'contour_levels': '', 'contour_width': .015}
    low, high = color_range(data)
    mesh = _mesh(data, config, low, high)
    mesh.materials.append(_color_material(config['palette']))
    mesh.materials.append(_flat_material('QC Projection unknown validity', (.45, .45, .45, 1)))
    obj = bpy.data.objects.new('QC Surface distance projection', mesh)
    bpy.context.collection.objects.link(obj)
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'projection'
    obj['qc_analysis_role'] = 'surface_projection'
    obj['qc_projection_reference'] = reference.name
    # A separate chart beside the molecule; all child geometry uses the generating frame.
    obj.location.x = float(data.arrays['positions'][:, 0].max() - data.arrays['projection_x'][0] + 2.5)
    tree = bpy.data.node_groups.new('QC Surface projection display', 'GeometryNodeTree')
    tree.is_modifier = True
    tree['qc_asset_id'] = 'qc.surface_projection.v1'
    socket(tree, 'Geometry', 'NodeSocketGeometry')
    for name, value in (('Color Minimum', low), ('Color Center', (low + high) / 2), ('Color Maximum', high)):
        socket(tree, name, 'NodeSocketFloat', default=value)
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    inputs, output = tree.nodes.new('NodeGroupInput'), tree.nodes.new('NodeGroupOutput')
    tree.links.new(node_socket(inputs.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
    obj.modifiers.new('QC Surface projection', 'NODES').node_group = tree
    add_legend(obj, mesh.materials[0], 'Color Minimum', 'Color Center', 'Color Maximum',
               iface('Surface depth (Å): z_hit-z_start'))
    from .annotation_fonts import annotation_font
    for node in tree.nodes:
        if node.bl_idname == 'GeometryNodeStringToCurves':
            node_socket(node.inputs, 'Font').default_value = annotation_font()
    tag_view(tree)
    x, y = data.arrays['projection_x'], data.arrays['projection_y']
    for name, value in (('Legend Position', ((x[0] + x[-1]) / 2, y[0] - 1.6, .05)),
                        ('Legend Length', max(2., float(x[-1] - x[0]) * .6)), ('Legend Width', .22),
                        ('Legend Text Size', .8), ('Legend Decimals', 3)):
        _input(obj, name, value)
    _axes_and_atoms(obj, data)
    apply_settings(obj, data, config)
    _set_point(obj, data, len(x) // 2, len(y) // 2)
    from .graph import arrange
    arrange(tree)
    return obj


class QCBLENDER_OT_import_projection(bpy.types.Operator):
    bl_idname = 'qcblender.import_surface_projection'
    bl_label = 'Import Surface Distance Projection'
    bl_description = 'Import an unscaled Multiwfn XY depth map with its scan declaration and log against the selected static atoms in the generating orientation'
    bl_options = {'REGISTER', 'UNDO'}

    data_path: StringProperty(name='Distance map text', subtype='FILE_PATH')
    settings_path: StringProperty(name='Projection scan JSON', subtype='FILE_PATH')
    log_path: StringProperty(name='Multiwfn generation log', subtype='FILE_PATH')
    mask_path: StringProperty(name='Validity CSV (optional)', subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'projection')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=620)

    def draw(self, context):
        layout = ui_layout(self.layout)
        for name in ('data_path', 'settings_path', 'log_path', 'mask_path'):
            layout.prop(self, name)
        layout.label(text='Use the static molecule in the original generating orientation')
        layout.label(text='Without a validity mask, scan-bottom values remain unknown')

    def execute(self, context):
        from ..data import load_dataset
        from ..surface_projection import import_projection
        from .external_results import store_analysis
        from .static_reference import capture_reference
        from .geometry import current_geometry
        try:
            reference = context.object
            capture_reference(reference)
            source = load_dataset(bpy.path.abspath(reference['qc_dataset']))
            current_geometry(reference, source)
            data = import_projection(source, bpy.path.abspath(self.data_path), bpy.path.abspath(self.settings_path),
                                     bpy.path.abspath(self.log_path), bpy.path.abspath(self.mask_path) if self.mask_path.strip() else None)
            directory = store_analysis(data)
            obj = create_view(directory, data, reference)
            for selected in context.selected_objects:
                selected.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj
        except (ValueError, OSError, KeyError, MemoryError, TypeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_projection_settings(bpy.types.Operator):
    bl_idname = 'qcblender.projection_settings'
    bl_label = 'Surface Projection Display'
    bl_description = 'Change only the depth-map display; missed points stay blank and unknown points never contribute to contours or automatic color limits'
    bl_options = {'REGISTER', 'UNDO'}

    palette: EnumProperty(name='Projection palette', items=[('VIRIDIS', 'Viridis', ''), ('CIVIDIS', 'Cividis', '')])
    manual_range: BoolProperty(name='Manual depth range', default=False)
    minimum: FloatProperty(name='Minimum depth (Å)', default=-6.)
    maximum: FloatProperty(name='Maximum depth (Å)', default=0.)
    show_atoms: BoolProperty(name='Show projected atoms', default=True)
    show_unknown: BoolProperty(name='Show unknown points in gray', default=True)
    show_legend: BoolProperty(name='Show depth legend', default=True)
    show_contours: BoolProperty(name='Show projection contours', default=False)
    contour_levels: StringProperty(name='Depth levels (Å; blank = automatic)', default='')
    contour_width: FloatProperty(name='Projection contour width', default=.015, min=.001, max=.2)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'projection'

    def invoke(self, context, event):
        for key, value in settings(context.object).items():
            setattr(self, key, value)
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.prop(self, 'palette')
        layout.prop(self, 'manual_range')
        row = layout.row()
        row.enabled = self.manual_range
        row.prop(self, 'minimum')
        row.prop(self, 'maximum')
        for key in ('show_atoms', 'show_unknown', 'show_legend', 'show_contours'):
            layout.prop(self, key)
        box = layout.column()
        box.enabled = self.show_contours
        box.prop(self, 'contour_levels')
        box.prop(self, 'contour_width')

    def execute(self, context):
        from ..data import load_dataset
        try:
            obj = context.object
            data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
            config = {key: getattr(self, key) for key in self.__annotations__}
            apply_settings(obj, data, config)
        except (ValueError, OSError, KeyError, MemoryError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_projection_point(bpy.types.Operator):
    bl_idname = 'qcblender.projection_point'
    bl_label = 'Inspect Projection Point'
    bl_description = 'Read an original depth and its validity at the sorted zero-based grid indexes'
    bl_options = {'REGISTER', 'UNDO'}

    ix: IntProperty(name='X index (0-based)', min=0)
    iy: IntProperty(name='Y index (0-based)', min=0)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'projection'

    def invoke(self, context, event):
        record = json.loads(context.object['qc_projection_point'])
        self.ix, self.iy = record['ix'], record['iy']
        return context.window_manager.invoke_props_dialog(self, width=360)

    def execute(self, context):
        from ..data import load_dataset
        try:
            obj = context.object
            _set_point(obj, load_dataset(bpy.path.abspath(obj['qc_dataset'])), self.ix, self.iy)
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_projection(bpy.types.Panel):
    bl_label = 'Surface Distance Projection'
    bl_idname = 'QCBLENDER_PT_projection'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'projection'

    def draw(self, context):
        from .source_browser import cached_metadata
        obj, layout = context.object, ui_layout(self.layout)
        analysis = cached_metadata(obj).get('analysis', {})
        if not analysis:
            layout.operator('qcblender.refresh_sources')
            return
        scan = analysis['scan']
        layout.label(text=iface('Grid: {nx} × {ny} | Depth in Å', nx=scan['nx'], ny=scan['ny']))
        counts = analysis['counts']
        layout.label(text=iface('Valid {valid} | Missed {missed} | Unknown {unknown}', **counts))
        layout.operator('qcblender.projection_settings')
        layout.operator('qcblender.projection_point')
        point = json.loads(obj['qc_projection_point'])
        layout.label(text=iface('Point ({ix}, {iy}): X {x:.6g}, Y {y:.6g} Å', **{key: point[key] for key in ('ix', 'iy', 'x', 'y')}))
        layout.label(text=iface('Depth: {depth:.8g} Å | {state}', depth=point['depth'], state=iface(point['state'])))
        layout.operator('qcblender.export_data')
