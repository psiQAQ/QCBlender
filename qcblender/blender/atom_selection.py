"""Local atom masks on independent QC atom display layers."""
import json

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty

from ..atom_selection import combine_numbers, evaluate_steps, parse_numbers, select_numbers
from .geometry import current_geometry
from .graph import view_modifier


ATTRIBUTE = 'qc_local_selection'
RECORD = 'qc_local_selection_record'


def _source(socket):
    if len(socket.links) != 1:
        raise ValueError('QC atom selection has an unsupported connection')
    return socket.links[0].from_socket


def _preflight(obj):
    from .copy_display import _state

    _state(obj)  # Reject unknown display graphs before touching mesh or nodes.
    modifier = view_modifier(obj)
    tree = modifier.node_group
    if tree.users != 1 or obj.data.users != 1 or tree.get('qc_atom_visibility') != 1:
        raise ValueError('Local selection needs an independent QC atom graph and hydrogen gate')
    groups = {}
    for key in ('qc.atom_selection.v1', 'qc.atom_style.v1'):
        found = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
                 and node.node_tree and node.node_tree.get('qc_asset_id') == key]
        if len(found) != 1:
            raise ValueError('QC atom selection graph is missing or ambiguous')
        groups[key] = found[0]
    selected, style = groups['qc.atom_selection.v1'], groups['qc.atom_style.v1']
    inputs = [node for node in tree.nodes if node.type == 'GROUP_INPUT']
    if len(inputs) != 1 or any(
            _source(selected.inputs[name]) != inputs[0].outputs[name]
            for name in ('Selection', 'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)')):
        raise ValueError('QC source selection controls are disconnected')
    visibility = _source(style.inputs['Selection']).node
    if (visibility.bl_idname != 'ShaderNodeMath' or visibility.operation != 'MULTIPLY'
            or _source(style.inputs['Selection']) != visibility.outputs[0]):
        raise ValueError('QC hydrogen gate is unsupported')
    hydrogen = _source(visibility.inputs[1]).node
    hydrogen_attr = obj.data.attributes.get('qc_atom_visible')
    if (hydrogen.bl_idname != 'GeometryNodeInputNamedAttribute' or hydrogen.data_type != 'BOOLEAN'
            or hydrogen.inputs['Name'].default_value != 'qc_atom_visible'
            or hydrogen_attr is None or hydrogen_attr.domain != 'POINT'
            or hydrogen_attr.data_type != 'BOOLEAN' or len(hydrogen_attr.data) != len(obj.data.vertices)):
        raise ValueError('QC hydrogen gate is unsupported')
    previous = _source(visibility.inputs[0])
    local = None
    if previous.node.get('qc_local_selection_gate'):
        local = previous.node
        mask = _source(local.inputs[1]).node
        if (local.bl_idname != 'ShaderNodeMath' or local.operation != 'MULTIPLY'
                or previous != local.outputs[0] or mask.bl_idname != 'GeometryNodeInputNamedAttribute'
                or mask.data_type != 'BOOLEAN' or mask.inputs['Name'].default_value != ATTRIBUTE
                or not mask.get('qc_local_selection_attribute')):
            raise ValueError('QC local selection gate is unsupported')
        previous = _source(local.inputs[0])
    if previous != selected.outputs['Selection']:
        raise ValueError('QC source selection is disconnected')
    attr = obj.data.attributes.get(ATTRIBUTE)
    if bool(attr) != bool(local):
        raise ValueError('QC local selection mask and graph disagree')
    if attr and (attr.domain != 'POINT' or attr.data_type != 'BOOLEAN'
                 or len(attr.data) != len(obj.data.vertices)):
        raise ValueError('QC local selection mask is invalid')
    return tree, visibility, selected.outputs['Selection'], attr


def _read_record(obj, attr):
    if RECORD not in obj:
        if attr and not all(item.value for item in attr.data):
            raise ValueError('QC local selection record is missing')
        return {'steps': []}
    record = json.loads(obj[RECORD])
    if (not isinstance(record, dict) or not isinstance(record.get('steps'), list)
            or not isinstance(record.get('fixed_numbers'), list)):
        raise ValueError('QC local selection record is invalid')
    if attr is None:
        raise ValueError('QC local selection mask is missing')
    if attr and [index for index, item in enumerate(attr.data, 1) if item.value] != record['fixed_numbers']:
        raise ValueError('QC local selection record differs from its mask')
    if not record['steps'] and not all(item.value for item in attr.data):
        raise ValueError('QC local selection query is missing')
    return record


def _write(obj, selected, record, state):
    tree, visibility, previous, attr = state
    old_values = [item.value for item in attr.data] if attr else None
    old_record = obj.get(RECORD)
    created = []
    try:
        if attr is None:
            attr = obj.data.attributes.new(ATTRIBUTE, 'BOOLEAN', 'POINT')
            mask = tree.nodes.new('GeometryNodeInputNamedAttribute')
            created.append(mask)
            mask.data_type = 'BOOLEAN'
            mask.inputs['Name'].default_value = ATTRIBUTE
            mask['qc_local_selection_attribute'] = 1
            gate = tree.nodes.new('ShaderNodeMath')
            created.append(gate)
            gate.operation = 'MULTIPLY'
            gate['qc_local_selection_gate'] = 1
            tree.links.new(previous, gate.inputs[0])
            tree.links.new(mask.outputs['Attribute'], gate.inputs[1])
            tree.links.new(gate.outputs[0], visibility.inputs[0])
        attr.data.foreach_set('value', [index in selected for index in range(1, len(attr.data) + 1)])
        if record is None:
            if RECORD in obj:
                del obj[RECORD]
        else:
            obj[RECORD] = json.dumps(record, sort_keys=True)
        obj.data.update()
        obj.update_tag()
    except Exception:
        if old_values is None:
            for node in reversed(created):
                tree.nodes.remove(node)
            if attr is not None:
                obj.data.attributes.remove(attr)
            tree.links.new(previous, visibility.inputs[0])
        else:
            attr.data.foreach_set('value', old_values)
        if old_record is None:
            if RECORD in obj:
                del obj[RECORD]
        else:
            obj[RECORD] = old_record
        obj.data.update()
        obj.update_tag()
        raise


def _selection(obj, mode, numbers='', use_radius=False, radius=5., include_seeds=True):
    positions, source = current_geometry(obj)
    state = _preflight(obj)
    record = _read_record(obj, state[3])
    if record['steps'] and any(record['source'].get(key) != source[key]
                               for key in ('dataset_sha256', 'source_sha256', 'selected_job')):
        raise ValueError('QC local selection source identity has changed')
    count = len(positions)
    if mode == 'CLEAR':
        if state[3] is None and RECORD not in obj:
            return tuple(range(1, count + 1))
        selected, saved = tuple(range(1, count + 1)), None
    elif mode == 'RECOMPUTE':
        if not record['steps']:
            raise ValueError('No local selection query to recompute')
        selected = evaluate_steps(positions, record['steps'])
        saved = {**record, 'fixed_numbers': list(selected), 'source': source}
    else:
        if mode == 'INVERT':
            step = {'mode': mode}
            members = ()
        else:
            seeds = parse_numbers(numbers, count)
            step = {'mode': mode, 'seeds': list(seeds), 'radius': radius if use_radius else None,
                    'include_seeds': bool(include_seeds)}
            members = select_numbers(positions, seeds, step['radius'], include_seeds)
        current = record.get('fixed_numbers', list(range(1, count + 1)))
        selected = combine_numbers(current, members, mode, count)
        steps = [*record['steps'], step] if mode != 'REPLACE' else [step]
        saved = {'steps': steps, 'fixed_numbers': list(selected), 'source': source}
    _write(obj, selected, saved, state)
    return selected


def copy_selection(source, target):
    """Copy a saved local mask to a new standard atom view of the same Dataset."""
    source_positions, source_record = current_geometry(source)
    target_positions, target_record = current_geometry(target)
    if (len(source_positions) != len(target_positions)
            or any(source_record[key] != target_record[key]
                   for key in ('dataset_sha256', 'source_sha256', 'selected_job'))):
        raise ValueError('Atom views do not share the same source binding')
    target_state = _preflight(target)
    attr = source.data.attributes.get(ATTRIBUTE)
    if attr and (attr.domain != 'POINT' or attr.data_type != 'BOOLEAN'
                 or len(attr.data) != len(source_positions)):
        raise ValueError('QC local selection source mask is invalid')
    record = _read_record(source, attr)
    if not record['steps']:
        return
    if any(record['source'].get(key) != source_record[key]
           for key in ('dataset_sha256', 'source_sha256', 'selected_job')):
        raise ValueError('QC local selection source identity has changed')
    _write(target, tuple(record['fixed_numbers']), record, target_state)


class QCBLENDER_OT_local_selection(bpy.types.Operator):
    bl_idname = 'qcblender.local_selection'
    bl_label = 'Local Atom Selection'
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(items=[(key, label, '') for key, label in (
        ('REPLACE', 'Replace'), ('UNION', 'Union'), ('INTERSECT', 'Intersect'),
        ('DIFFERENCE', 'Difference'), ('INVERT', 'Invert'), ('CLEAR', 'Clear'),
        ('RECOMPUTE', 'Recompute'))], default='REPLACE')
    numbers: StringProperty(name='Source atom numbers (1-based)', default='')
    use_radius: BoolProperty(name='Include distance neighborhood', default=False)
    radius: FloatProperty(name='Radius (Å)', default=5., min=0.)
    include_seeds: BoolProperty(name='Include seed atoms', default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'atoms'

    def invoke(self, context, event):
        if self.mode in ('CLEAR', 'RECOMPUTE', 'INVERT'):
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.prop(self, 'mode')
        if self.mode not in ('CLEAR', 'RECOMPUTE', 'INVERT'):
            self.layout.prop(self, 'numbers')
            self.layout.prop(self, 'use_radius')
            if self.use_radius:
                self.layout.prop(self, 'radius')
                self.layout.prop(self, 'include_seeds')

    def execute(self, context):
        try:
            _selection(context.object, self.mode, self.numbers, self.use_radius,
                       self.radius, self.include_seeds)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_local_selection_layer(bpy.types.Operator):
    bl_idname = 'qcblender.local_selection_layer'
    bl_label = 'New Local Atom Layer'
    bl_options = {'REGISTER', 'UNDO'}

    numbers: StringProperty(name='Source atom numbers (1-based)', default='')
    use_radius: BoolProperty(name='Include distance neighborhood', default=False)
    radius: FloatProperty(name='Radius (Å)', default=5., min=0.)
    include_seeds: BoolProperty(name='Include seed atoms', default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'atoms'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.prop(self, 'numbers')
        self.layout.prop(self, 'use_radius')
        if self.use_radius:
            self.layout.prop(self, 'radius')
            self.layout.prop(self, 'include_seeds')

    def execute(self, context):
        from .layers import activate, copy_layer, display_layers

        source = context.object
        try:
            if source.get('qc_irc'):
                raise ValueError('IRC path supports local selection in place; do not duplicate the path')
            positions, _ = current_geometry(source)
            _preflight(source)
            seeds = parse_numbers(self.numbers, len(positions))
            select_numbers(positions, seeds, self.radius if self.use_radius else None,
                           self.include_seeds)  # Check empty results before copying.
            original_orders = {layer: layer.get('qc_layer_order') for layer in display_layers(context.scene)}
            before = set(context.collection.objects)
            datablocks = {name: set(getattr(bpy.data, name)) for name in
                          ('node_groups', 'meshes', 'curves', 'materials')}
            try:
                copied = copy_layer(source, context.collection)
                _selection(copied, 'REPLACE', self.numbers, self.use_radius,
                           self.radius, self.include_seeds)
                copied.name = source.name + ' / Local Selection'
                layers = display_layers(context.scene)
                layers.remove(copied)
                layers.insert(layers.index(source) + 1, copied)
                for index, layer in enumerate(dict.fromkeys(layers)):
                    layer['qc_layer_order'] = index
                activate(context, copied)
            except Exception:
                for layer, order in original_orders.items():
                    if order is None:
                        if 'qc_layer_order' in layer:
                            del layer['qc_layer_order']
                    else:
                        layer['qc_layer_order'] = order
                for obj in set(context.collection.objects) - before:
                    bpy.data.objects.remove(obj, do_unlink=True)
                for name, previous in datablocks.items():
                    collection = getattr(bpy.data, name)
                    for block in set(collection) - previous:
                        if block.users == 0:
                            collection.remove(block)
                activate(context, source)
                raise
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}
