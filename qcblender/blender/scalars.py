"""Native grid sampling, signed color maps and planar scalar slices."""
from ..i18n import enum_items, error_text, iface, ui_layout
from .node_identity import node_socket, socket_name
import json
from functools import lru_cache

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, StringProperty
import numpy as np

from ..association import compare_sources
from ..data import load_dataset
from .views import bind, material, node_by_type, socket
from .graph import view_modifier, tag_view, geometry_output, frame_nodes
from .legend_layout import LAYOUT


def scalar_material(opacity_attribute=False):
    mat = material('QC scalar color map', (.5, .5, .5, 1))
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = node_by_type(nodes, 'ShaderNodeBsdfPrincipled')
    output = node_by_type(nodes, 'ShaderNodeOutputMaterial')
    if opacity_attribute:
        opacity = nodes.new('ShaderNodeAttribute')
        opacity.attribute_name = 'qc_opacity'
        links.new(node_socket(opacity.outputs, 'Fac'), node_socket(shader.inputs, 'Alpha'))
    value = nodes.new('ShaderNodeAttribute')
    value.attribute_name = 'qc_color_fraction'
    valid = nodes.new('ShaderNodeAttribute')
    valid.attribute_name = 'qc_sample_valid'
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp['qc_role'] = 'color_ramp'
    ramp.color_ramp.elements[0].color = (.8, .03, .02, 1)
    ramp.color_ramp.elements[1].color = (.03, .18, .8, 1)
    ramp.color_ramp.elements.new(.5).color = (.95, .95, .95, 1)
    invert = nodes.new('ShaderNodeValue')
    invert['qc_role'] = 'color_invert'
    invert.label = 'Reverse color map (0 or 1)'
    reverse = nodes.new('ShaderNodeMath')
    reverse.operation = 'SUBTRACT'
    links.new(node_socket(invert.outputs, 0), node_socket(reverse.inputs, 0))
    links.new(node_socket(value.outputs, 'Fac'), node_socket(reverse.inputs, 1))
    absolute = nodes.new('ShaderNodeMath')
    absolute.operation = 'ABSOLUTE'
    links.new(node_socket(reverse.outputs, 0), node_socket(absolute.inputs, 0))
    links.new(node_socket(absolute.outputs, 0), node_socket(ramp.inputs, 'Fac'))
    missing = nodes.new('ShaderNodeMixRGB')
    node_socket(missing.inputs, 1).default_value = (1, 0, 1, 1)
    links.new(node_socket(valid.outputs, 'Fac'), node_socket(missing.inputs, 0))
    links.new(node_socket(ramp.outputs, 'Color'), node_socket(missing.inputs, 2))
    links.new(node_socket(missing.outputs, 0), node_socket(shader.inputs, 'Base Color'))
    legend = nodes.new('ShaderNodeAttribute')
    legend.attribute_name = 'qc_legend'
    emission = nodes.new('ShaderNodeEmission')
    links.new(node_socket(missing.outputs, 0), node_socket(emission.inputs, 'Color'))
    mix = nodes.new('ShaderNodeMixShader')
    links.new(node_socket(legend.outputs, 'Fac'), node_socket(mix.inputs, 0))
    links.new(node_socket(shader.outputs, 'BSDF'), node_socket(mix.inputs, 1))
    links.new(node_socket(emission.outputs, 'Emission'), node_socket(mix.inputs, 2))
    links.new(node_socket(mix.outputs, 0), node_socket(output.inputs, 'Surface'))
    return mat


def color_fraction(tree, inputs, value, minimum, center, maximum):
    nodes, links = tree.nodes, tree.links
    lower, upper = nodes.new('ShaderNodeMapRange'), nodes.new('ShaderNodeMapRange')
    for mapping, start, end, low, high in [(lower, minimum, center, 0, .5), (upper, center, maximum, .5, 1)]:
        mapping.clamp = True
        links.new(value, node_socket(mapping.inputs, 'Value'))
        links.new(node_socket(inputs.outputs, start), node_socket(mapping.inputs, 'From Min'))
        links.new(node_socket(inputs.outputs, end), node_socket(mapping.inputs, 'From Max'))
        node_socket(mapping.inputs, 'To Min').default_value, node_socket(mapping.inputs, 'To Max').default_value = low, high
    below = nodes.new('ShaderNodeMath')
    below.operation = 'LESS_THAN'
    links.new(value, node_socket(below.inputs, 0))
    links.new(node_socket(inputs.outputs, center), node_socket(below.inputs, 1))
    choose = nodes.new('GeometryNodeSwitch')
    choose.input_type = 'FLOAT'
    links.new(node_socket(below.outputs, 0), node_socket(choose.inputs, 'Switch'))
    links.new(node_socket(lower.outputs, 'Result'), node_socket(choose.inputs, 'True'))
    links.new(node_socket(upper.outputs, 'Result'), node_socket(choose.inputs, 'False'))
    return node_socket(choose.outputs, 'Output')


def add_legend(obj, color_material, minimum, center, maximum, title, *, tree=None, text_material=None,
               destination=None):
    """Legend geometry reads the same range sockets and material as the colored view."""
    from .assets import math

    modifier = view_modifier(obj)
    tree = modifier.node_group if tree is None else tree
    nodes, links = tree.nodes, tree.links
    for name, kind, value in [('Show Legend', 'NodeSocketBool', False),
                              ('Legend Position', 'NodeSocketVector', (3., 0., 0.)),
                              ('Legend Length', 'NodeSocketFloat', 2.),
                              ('Legend Width', 'NodeSocketFloat', .18),
                              ('Legend Text Size', 'NodeSocketFloat', .16),
                              ('Legend Decimals', 'NodeSocketInt', 5),
                              ('Legend Vertical', 'NodeSocketBool', False),
                              ('Legend Rotation', 'NodeSocketVector', (0., 0., 0.))]:
        existing = [entry for entry in tree.interface.items_tree
                    if entry.item_type == 'SOCKET' and entry.in_out == 'INPUT' and socket_name(entry) == name]
        if existing:
            if len(existing) != 1 or existing[0].socket_type != kind:
                raise ValueError('Existing legend input is ambiguous: ' + name)
            item = existing[0]
        else:
            item = socket(tree, name, kind, default=value,
                          minimum=0.001 if name in ('Legend Length', 'Legend Width', 'Legend Text Size') else
                          0 if name == 'Legend Decimals' else None)
        if tree == modifier.node_group and not existing:
            modifier[item.identifier] = value
    inputs = next(n for n in nodes if n.type == 'GROUP_INPUT')
    output = next(n for n in nodes if n.type == 'GROUP_OUTPUT')
    destination = node_socket(output.inputs, 'Geometry') if destination is None else destination
    original = destination.links[0].from_socket

    def component(coefficients):
        parts = [math(tree, 'MULTIPLY', node_socket(inputs.outputs, name), factor)
                 for name, factor in zip(('Legend Length', 'Legend Width', 'Legend Text Size'), coefficients[:3])
                 if factor]
        if coefficients[3]:
            parts.append(coefficients[3])
        result = parts[0]
        for part in parts[1:]:
            result = math(tree, 'ADD', result, part)
        return result

    def offset(label):
        vectors = []
        for orientation in ('horizontal', 'vertical'):
            vector = nodes.new('ShaderNodeCombineXYZ')
            for axis, coefficients in zip(('X', 'Y'), LAYOUT[orientation][label]):
                links.new(component(coefficients), node_socket(vector.inputs, axis))
            vectors.append(node_socket(vector.outputs, 'Vector'))
        choice = nodes.new('GeometryNodeSwitch')
        choice.input_type = 'VECTOR'
        links.new(node_socket(inputs.outputs, 'Legend Vertical'), node_socket(choice.inputs, 'Switch'))
        links.new(vectors[0], node_socket(choice.inputs, 'False'))
        links.new(vectors[1], node_socket(choice.inputs, 'True'))
        return node_socket(choice.outputs, 'Output')
    grid = nodes.new('GeometryNodeMeshGrid')
    links.new(node_socket(inputs.outputs, 'Legend Length'), node_socket(grid.inputs, 'Size X'))
    links.new(node_socket(inputs.outputs, 'Legend Width'), node_socket(grid.inputs, 'Size Y'))
    node_socket(grid.inputs, 'Vertices X').default_value = 65
    node_socket(grid.inputs, 'Vertices Y').default_value = 2
    position = nodes.new('GeometryNodeInputPosition')
    xyz = nodes.new('ShaderNodeSeparateXYZ')
    links.new(node_socket(position.outputs, 'Position'), node_socket(xyz.inputs, 'Vector'))
    fraction = nodes.new('ShaderNodeMapRange')
    links.new(math(tree, 'MULTIPLY', node_socket(inputs.outputs, 'Legend Length'), -.5), node_socket(fraction.inputs, 'From Min'))
    links.new(math(tree, 'MULTIPLY', node_socket(inputs.outputs, 'Legend Length'), .5), node_socket(fraction.inputs, 'From Max'))
    links.new(node_socket(xyz.outputs, 'X'), node_socket(fraction.inputs, 'Value'))
    geometry = node_socket(grid.outputs, 'Mesh')
    for name, kind, value in [('qc_color_fraction', 'FLOAT', node_socket(fraction.outputs, 'Result')),
                               ('qc_sample_valid', 'BOOLEAN', True), ('qc_legend', 'BOOLEAN', True)]:
        store = nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        node_socket(store.inputs, 'Name').default_value = name
        links.new(geometry, node_socket(store.inputs, 'Geometry'))
        if value is True:
            node_socket(store.inputs, 'Value').default_value = True
        else:
            links.new(value, node_socket(store.inputs, 'Value'))
        geometry = node_socket(store.outputs, 'Geometry')
    assign = nodes.new('GeometryNodeSetMaterial')
    node_socket(assign.inputs, 'Material').default_value = color_material
    links.new(geometry, node_socket(assign.inputs, 'Geometry'))
    vertical = nodes.new('GeometryNodeTransform')
    node_socket(vertical.inputs, 'Rotation').default_value = (0, 0, 1.5707963267948966)
    links.new(node_socket(assign.outputs, 'Geometry'), node_socket(vertical.inputs, 'Geometry'))
    bar = nodes.new('GeometryNodeSwitch')
    bar.input_type = 'GEOMETRY'
    links.new(node_socket(inputs.outputs, 'Legend Vertical'), node_socket(bar.inputs, 'Switch'))
    links.new(node_socket(assign.outputs, 'Geometry'), node_socket(bar.inputs, 'False'))
    links.new(node_socket(vertical.outputs, 'Geometry'), node_socket(bar.inputs, 'True'))
    legend = nodes.new('GeometryNodeJoinGeometry')
    links.new(node_socket(bar.outputs, 'Output'), node_socket(legend.inputs, 'Geometry'))
    if text_material is None:
        text_material = material('QC legend text', (.015, .015, .015, 1))
        emission = text_material.node_tree.nodes.new('ShaderNodeEmission')
        node_socket(emission.inputs, 'Color').default_value = (.015, .015, .015, 1)
        material_output = node_by_type(text_material.node_tree.nodes, 'ShaderNodeOutputMaterial')
        text_material.node_tree.links.new(node_socket(emission.outputs, 0), node_socket(material_output.inputs, 'Surface'))
    title_node = None
    for label, role in [(minimum, 'minimum'), (center, 'center'),
                        (maximum, 'maximum'), (None, 'title')]:
        text = nodes.new('GeometryNodeStringToCurves')
        links.new(node_socket(inputs.outputs, 'Legend Text Size'), node_socket(text.inputs, 'Size'))
        if label:
            number = nodes.new('FunctionNodeValueToString')
            number.label = label
            links.new(node_socket(inputs.outputs, 'Legend Decimals'), node_socket(number.inputs, 'Decimals'))
            links.new(node_socket(inputs.outputs, label), node_socket(number.inputs, 'Value'))
            links.new(node_socket(number.outputs, 'String'), node_socket(text.inputs, 'String'))
        else:
            text.label = 'QC Legend Title'
            node_socket(text.inputs, 'String').default_value = title
            title_node = text
        realize = nodes.new('GeometryNodeRealizeInstances')
        links.new(node_socket(text.outputs, 'Curve Instances'), node_socket(realize.inputs, 'Geometry'))
        fill = nodes.new('GeometryNodeFillCurve')
        links.new(node_socket(realize.outputs, 'Geometry'), node_socket(fill.inputs, 'Curve'))
        transform = nodes.new('GeometryNodeTransform')
        links.new(offset(role), node_socket(transform.inputs, 'Translation'))
        links.new(node_socket(fill.outputs, 'Mesh'), node_socket(transform.inputs, 'Geometry'))
        text_assign = nodes.new('GeometryNodeSetMaterial')
        node_socket(text_assign.inputs, 'Material').default_value = text_material
        links.new(node_socket(transform.outputs, 'Geometry'), node_socket(text_assign.inputs, 'Geometry'))
        links.new(node_socket(text_assign.outputs, 'Geometry'), node_socket(legend.inputs, 'Geometry'))
    transform = nodes.new('GeometryNodeTransform')
    links.new(node_socket(legend.outputs, 'Geometry'), node_socket(transform.inputs, 'Geometry'))
    links.new(node_socket(inputs.outputs, 'Legend Position'), node_socket(transform.inputs, 'Translation'))
    links.new(node_socket(inputs.outputs, 'Legend Rotation'), node_socket(transform.inputs, 'Rotation'))
    show = nodes.new('GeometryNodeSwitch')
    show.input_type = 'GEOMETRY'
    links.new(node_socket(inputs.outputs, 'Show Legend'), node_socket(show.inputs, 'Switch'))
    links.new(node_socket(transform.outputs, 'Geometry'), node_socket(show.inputs, 'True'))
    join = nodes.new('GeometryNodeJoinGeometry')
    links.new(original, node_socket(join.inputs, 'Geometry'))
    links.new(node_socket(show.outputs, 'Output'), node_socket(join.inputs, 'Geometry'))
    links.new(node_socket(join.outputs, 'Geometry'), destination)
    tree['qc_legend_layout'] = 1
    return title_node


def color_title(field):
    name = {'electrostatic_potential': 'ESP', 'orbital_amplitude': 'MO amplitude',
            'electron_number_density': 'Electron density', 'spin_density': 'Spin density'}.get(
                field['quantity'], field['quantity'])
    return name + ' [' + field['unit'] + ']'


def color_record(source, field, field_source):
    return json.dumps({'source': source['qc_source_sha256'], 'field_source': dict(field_source),
                       'field_dataset_sha256': source['qc_dataset_sha256'],
                       'field': {key: field.get(key) for key in
                                 ('array', 'quantity', 'unit', 'orbital', 'spin', 'source_number')},
                       'quantity': field['quantity'], 'unit': field['unit'],
                       'interpolation': 'trilinear', 'missing_color': 'magenta'})


def add_mapping(target, source, low, high):
    if not np.isfinite([low, high]).all() or low >= high:
        raise ValueError('Color minimum must be finite and below color maximum')
    from .source_browser import bound_field
    volume, field, _, field_source = bound_field(source)
    modifier = view_modifier(target)
    tree = modifier.node_group
    if tree.get('qc_charge_mapping'):
        raise ValueError('This view already uses atomic charge for color; use a separate atom view for scalar mapping')
    if (tree.get('qc_color_mapping') or target.get('qc_color_source')
            or any(n.bl_idname == 'GeometryNodeGroup' and n.node_tree
                   and n.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2' for n in tree.nodes)):
        raise ValueError('This view already has a scalar mapping; use Select Color Field to replace it')
    output = geometry_output(tree)
    if len(output.links) != 1 or sum(n.type == 'GROUP_INPUT' for n in tree.nodes) != 1:
        raise ValueError('Target view has no unique supported geometry input and output')
    for name, value in [('Color Minimum', low), ('Color Center', (low + high) / 2), ('Color Maximum', high)]:
        item = socket(tree, name, 'NodeSocketFloat', default=value)
        modifier[item.identifier] = value
    nodes, links = tree.nodes, tree.links
    inputs = next(n for n in nodes if n.type == 'GROUP_INPUT')
    geometry = output.links[0].from_socket
    existing_nodes = set(nodes)
    info = nodes.new('GeometryNodeObjectInfo')
    info.transform_space = 'RELATIVE'
    node_socket(info.inputs, 'Object').default_value = volume
    position = nodes.new('GeometryNodeInputPosition')
    from .assets import sample_group, color_group
    sampler = nodes.new('GeometryNodeGroup')
    sampler.node_tree = sample_group()
    links.new(node_socket(info.outputs, 'Geometry'), node_socket(sampler.inputs, 'Volume'))
    links.new(node_socket(position.outputs, 'Position'), node_socket(sampler.inputs, 'Position'))
    assign = nodes.new('GeometryNodeGroup')
    assign.node_tree = color_group()
    links.new(node_socket(sampler.outputs, 'Value'), node_socket(assign.inputs, 'Value'))
    links.new(node_socket(sampler.outputs, 'Valid'), node_socket(assign.inputs, 'Valid'))
    for name in ('Color Minimum', 'Color Center', 'Color Maximum'):
        links.new(node_socket(inputs.outputs, name), node_socket(assign.inputs, name))
    color_material = scalar_material(opacity_attribute=True)
    node_socket(assign.inputs, 'Material').default_value = color_material
    links.new(geometry, node_socket(assign.inputs, 'Geometry'))
    links.new(node_socket(assign.outputs, 'Geometry'), output)
    frame_nodes(tree, [node for node in nodes if node not in existing_nodes], 'Scalar: sampling and colors')
    existing_nodes = set(nodes)
    add_legend(target, color_material, 'Color Minimum', 'Color Center', 'Color Maximum', color_title(field))
    frame_nodes(tree, [node for node in nodes if node not in existing_nodes], 'Legend: range and labels')
    tree['qc_color_mapping'] = True
    tag_view(tree)
    target['qc_color_source'] = color_record(source, field, field_source)
    target.update_tag()


def compare_color_sources(target, source):
    """Use the same scientific association check for first binding and replacement."""
    from .source_browser import bound_field, read_metadata
    from .association import require_current_association, require_field_atom_view
    from .geometry import current_geometry
    bound_field(source)
    read_metadata(target)
    reference = load_dataset(bpy.path.abspath(target['qc_dataset']))
    if target.get('qc_source_sha256') != reference.metadata['source']['sha256']:
        raise ValueError('Target view differs from its saved source identity')
    moving = load_dataset(bpy.path.abspath(source['qc_dataset']))
    reference_geometry = {'kind': 'source', 'step': None}
    if target.get('qc_view_kind') == 'atoms':
        _, reference_geometry = current_geometry(target, reference)
        reference_view = target
    else:
        reference_view = (require_field_atom_view(target, reference)
                          if target.parent and target.parent.get('qc_view_kind') == 'atoms' else None)
    moving_view = (require_field_atom_view(source, moving)
                   if source.parent and source.parent.get('qc_view_kind') == 'atoms' else None)
    explicit_alignment = (reference_view is not None and moving_view is not None
                          and moving_view != reference_view and 'qc_association' in moving_view
                          and moving_view.qc_settings.association_reference == reference_view)
    if explicit_alignment:
        require_current_association(moving_view, reference_view)
    return compare_sources(reference, moving, allow_rigid=explicit_alignment,
                           reference_kind=reference_geometry['kind'], reference_step=reference_geometry['step'])


def replace_mapping(target, source):
    from .source_browser import bound_field, color_mapping, mapped_field
    volume, field, _, new_field_source = bound_field(source)
    info, title = color_mapping(target)
    previous_volume, _, _ = mapped_field(target)
    old_title = node_socket(title.inputs, 'String').default_value
    old_binding = target['qc_color_source']
    try:
        node_socket(info.inputs, 'Object').default_value = volume
        node_socket(title.inputs, 'String').default_value = color_title(field)
        target['qc_color_source'] = color_record(source, field, new_field_source)
        target.update_tag()
    except Exception:
        node_socket(info.inputs, 'Object').default_value = previous_volume
        node_socket(title.inputs, 'String').default_value = old_title
        target['qc_color_source'] = old_binding
        raise


def color_field_candidates(context):
    from .source_browser import bound_field
    candidates = []
    if context is None or context.scene is None:
        return candidates
    for obj in context.scene.objects:
        try:
            volume, field, meta, source = bound_field(obj)
        except (ValueError, OSError, KeyError, TypeError):
            continue
        job = meta.get('selected_job')
        segment = f' | Job {job + 1}' if type(job) is int and job >= 0 else ''
        orbital = field.get('orbital')
        orbital_label = (f' | {orbital.get("spin", "?")} MO {orbital.get("source_number", "?")}'
                         if isinstance(orbital, dict) else '')
        label = (f'{obj.name}: {field["quantity"]} [{field["unit"]}]'
                 f' | {source.get("filename", "unknown")} | {source["sha256"][:12]}'
                 f'{segment}{orbital_label}')
        jobs = meta.get('jobs', [])
        candidates.append({'name': obj.name, 'label': label, 'source': source,
                           'field': field, 'field_record': obj['qc_field'],
                           'job': job, 'job_record': jobs[job] if type(job) is int and 0 <= job < len(jobs) else None,
                           'object_pointer': obj.as_pointer(), 'volume_pointer': volume.as_pointer(),
                           'dataset_sha256': obj['qc_dataset_sha256']})
    return candidates


@lru_cache(maxsize=32)
def cached_color_choices(summary):
    # Blender retains dynamic Enum strings after the items callback returns.
    return [(row['name'], row['label'], row['source']['sha256']) for row in json.loads(summary)]


def color_field_choices(self, context):
    summary = self.candidate_summary or json.dumps(color_field_candidates(context))
    choices = []
    for row, (identifier, label, description) in zip(json.loads(summary), cached_color_choices(summary)):
        field, source = row['field'], row['source']
        label = (f"{row['name']}: {field['quantity']} [{field['unit']}]"
                 f" | {source.get('filename', 'unknown')} | {source['sha256'][:12]}")
        job = row['job']
        if type(job) is int and job >= 0:
            label += ' | ' + iface('Job {number}', number=job + 1)
        orbital = field.get('orbital')
        if isinstance(orbital, dict):
            label += f" | {orbital.get('spin', '?')} MO {orbital.get('source_number', '?')}"
        choices.append((identifier, label, description))
    return enum_items(choices)


class QCBLENDER_OT_select_color_field(bpy.types.Operator):
    bl_idname = 'qcblender.select_color_field'
    bl_label = 'Select Color Field'
    bl_options = {'REGISTER', 'UNDO'}
    source_name: EnumProperty(name='Field', items=color_field_choices)
    target_name: StringProperty(options={'HIDDEN'})
    target_pointer: StringProperty(options={'HIDDEN'})
    candidate_summary: StringProperty(options={'HIDDEN'})
    minimum: FloatProperty(name='Color minimum (field unit)', default=-.05)
    maximum: FloatProperty(name='Color maximum (field unit)', default=.05)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.get('qc_view_kind') in ('field', 'slice', 'atoms')
                and bool(context.object.get('qc_dataset')))

    def invoke(self, context, event):
        candidates = color_field_candidates(context)
        if not candidates:
            self.report({'ERROR'}, error_text('No bound scalar field views are available in this scene'))
            return {'CANCELLED'}
        self.target_name = context.object.name
        self.target_pointer = str(context.object.as_pointer())
        self.candidate_summary = json.dumps(candidates)
        self.source_name = candidates[0]['name']
        return context.window_manager.invoke_props_dialog(self, width=680)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.prop(self, 'source_name')
        candidates = json.loads(self.candidate_summary) if self.candidate_summary else color_field_candidates(context)
        selected = next((row for row in candidates if row['name'] == self.source_name), None)
        if selected:
            field, source_record = selected['field'], selected['source']
            box = layout.box()
            box.label(text=iface('Source file: {value0}', value0=source_record['filename']))
            box.label(text=iface('SHA-256: {value0}', value0=source_record['sha256']))
            job = selected['job']
            box.label(text=iface('Calculation: Job {number}', number=job + 1) if type(job) is int and job >= 0
                      else iface('Calculation: not recorded'))
            if selected['job_record']:
                segment = selected['job_record']
                box.label(text=iface('Route: {value0} | status: {value1}', value0=segment.get("route", "not recorded"), value1=segment.get("status", "unknown")))
                box.label(text=iface('Source lines: {value0}–{value1}', value0=segment.get("line_start", "?"), value1=segment.get("line_end", "?")))
            box.label(text=iface('Field: {value0} [{value1}] | array {value2}', value0=field["quantity"], value1=field["unit"], value2=field["array"]))
            orbital = field.get('orbital')
            if isinstance(orbital, dict):
                box.label(text=iface('Orbital: {value0} MO {value1}', value0=orbital.get("spin", "unknown"), value1=orbital.get("source_number", "unknown")))
                box.label(text=iface('Occupation: {value0} | Energy: {value1} Eh', value0=orbital.get("occupation", "unknown"), value1=orbital.get("energy_hartree", "unknown")))
            elif field.get('orbital_source_number') is not None:
                box.label(text=iface('Orbital source number: {value0}', value0=field["orbital_source_number"]))
        layout.prop(self, 'minimum')
        layout.prop(self, 'maximum')
        layout.label(text='Range is used only for the first mapping; replacement keeps the current range')

    def execute(self, context):
        from .source_browser import bound_field
        target = context.object
        try:
            if target is None or (self.target_name and target.name != self.target_name) or (
                    self.target_pointer and str(target.as_pointer()) != self.target_pointer):
                raise ValueError('Active target changed while choosing the color field')
            candidates = json.loads(self.candidate_summary) if self.candidate_summary else color_field_candidates(context)
            selected = next((row for row in candidates if row['name'] == self.source_name), None)
            source = context.scene.objects.get(self.source_name)
            if source is None or selected is None:
                raise ValueError('Selected color field view is no longer available')
            volume, field, _, field_source = bound_field(source)
            if (source.as_pointer() != selected['object_pointer']
                    or volume.as_pointer() != selected['volume_pointer']
                    or source['qc_dataset_sha256'] != selected['dataset_sha256']
                    or source['qc_field'] != selected['field_record']
                    or field != selected['field'] or field_source != selected['source']):
                raise ValueError('Selected color field changed while the dialog was open')
            compare_color_sources(target, source)
            tree = view_modifier(target).node_group
            if tree.get('qc_color_mapping') or target.get('qc_color_source'):
                replace_mapping(target, source)
            else:
                add_mapping(target, source, self.minimum, self.maximum)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_map_scalar(bpy.types.Operator):
    bl_idname = 'qcblender.map_scalar'
    bl_label = 'Map Selected Field to Active Surface'
    bl_options = {'REGISTER', 'UNDO'}
    minimum: FloatProperty(name='Color minimum (field unit)', default=-.05)
    maximum: FloatProperty(name='Color maximum (field unit)', default=.05)

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.get('qc_view_kind') in ('field', 'slice', 'atoms')
                and len(context.selected_objects) == 2)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        target = context.object
        source = next(o for o in context.selected_objects if o != target)
        try:
            if 'qc_field' not in source:
                raise ValueError('Select two scalar field views, with the receiving surface active')
            compare_color_sources(target, source)
            add_mapping(target, source, self.minimum, self.maximum)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_slice(bpy.types.Operator):
    bl_idname = 'qcblender.create_slice'
    bl_label = 'Create Scalar Slice'
    bl_options = {'REGISTER', 'UNDO'}
    resolution: IntProperty(name='Samples per axis', default=201, min=2, max=1001)
    minimum: FloatProperty(name='Color minimum (field unit)', default=-.05)
    maximum: FloatProperty(name='Color maximum (field unit)', default=.05)

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'slice')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        source = context.object
        from mathutils import Matrix
        from ..planes import plane_frame
        from .profile import profile_source
        try:
            volume, field = profile_source(source, 'GEOMETRY')
            data = load_dataset(bpy.path.abspath(source['qc_dataset']))
            world = source.parent.matrix_world if source.parent else Matrix.Identity(4)
            center, axes, width, height = plane_frame(
                field, 'ij', np.asarray(world.inverted() @ volume.matrix_world), .5)
            rotation = Matrix(axes.tolist()).to_euler('XYZ')
        except (ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        mesh = bpy.data.meshes.new('QC slice carrier')
        obj = bpy.data.objects.new('QC scalar slice', mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = source.parent
        bind(obj, bpy.path.abspath(source['qc_dataset']), data)
        obj['qc_field'] = source['qc_field']
        obj['qc_view_kind'] = 'slice'
        obj.qc_settings.volume = source.qc_settings.volume
        tree = bpy.data.node_groups.new('QC Slice v1', 'GeometryNodeTree')
        socket(tree, 'Center', 'NodeSocketVector', default=tuple(center))
        socket(tree, 'Rotation', 'NodeSocketVector', default=tuple(rotation))
        socket(tree, 'Width', 'NodeSocketFloat', default=width, minimum=.001)
        socket(tree, 'Height', 'NodeSocketFloat', default=height, minimum=.001)
        socket(tree, 'Resolution', 'NodeSocketInt', default=self.resolution, minimum=2)
        socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
        nodes, links = tree.nodes, tree.links
        inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
        from .assets import slice_group
        slice_node = nodes.new('GeometryNodeGroup')
        slice_node.node_tree = slice_group()
        for name in ('Center', 'Rotation', 'Width', 'Height', 'Resolution'):
            links.new(node_socket(inputs.outputs, name), node_socket(slice_node.inputs, name))
        links.new(node_socket(slice_node.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
        frame_nodes(tree, list(nodes), 'Slice: plane placement', (0, 0))
        obj.modifiers.new('QC Slice', 'NODES').node_group = tree
        try:
            add_mapping(obj, source, self.minimum, self.maximum)
        except (ValueError, OSError, KeyError) as error:
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
            bpy.data.node_groups.remove(tree)
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        from .interaction import save_plane_definition
        save_plane_definition(obj, 'ij', .5)
        return {'FINISHED'}
