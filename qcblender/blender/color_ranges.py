"""One-shot color ranges on the existing scalar mapping inputs."""
import json
import math

import bpy
from bpy.props import FloatProperty

from .graph import view_modifier
from .jobs import Job
from .source_browser import binding_key, color_mapping, mapped_field
from .ui import AsyncOperation

RANGE_NAMES = ('Color Minimum', 'Color Center', 'Color Maximum')


def range_inputs(obj):
    color_mapping(obj)
    modifier = view_modifier(obj)
    tree = modifier.node_group
    color = next(node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
                 and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2')
    identifiers = []
    for name in RANGE_NAMES:
        inputs = [s for s in tree.interface.items_tree if s.item_type == 'SOCKET'
                  and s.in_out == 'INPUT' and s.name == name and s.socket_type == 'NodeSocketFloat']
        links = color.inputs[name].links
        if (len(inputs) != 1 or inputs[0].identifier not in modifier or len(links) != 1
                or links[0].from_node.type != 'GROUP_INPUT'
                or links[0].from_socket.identifier != inputs[0].identifier):
            raise ValueError('Color range inputs are missing or customized')
        identifiers.append(inputs[0].identifier)
    return modifier, identifiers


def apply_range(obj, values):
    if len(values) != 3 or not all(math.isfinite(value) for value in values) or not values[0] < values[1] < values[2]:
        raise ValueError('Require finite color minimum < center < maximum')
    modifier, identifiers = range_inputs(obj)
    before = [modifier[key] for key in identifiers]
    try:
        for key, value in zip(identifiers, values):
            modifier[key] = value
        obj.update_tag()
    except Exception:
        for key, value in zip(identifiers, before):
            modifier[key] = value
        raise


def color_source(obj):
    volume, field, _ = mapped_field(obj)
    token = (volume.as_pointer(), binding_key(volume), volume['qc_field'], obj['qc_color_source'])
    return volume, field, token


class QCBLENDER_OT_symmetric_color_range(bpy.types.Operator):
    bl_idname = 'qcblender.symmetric_color_range'
    bl_label = 'Set Zero-Centered Color Range'
    bl_options = {'REGISTER', 'UNDO'}
    radius: FloatProperty(name='Positive limit R (field unit)', default=.05, min=0)

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_color_source'))

    def invoke(self, context, event):
        try:
            modifier, keys = range_inputs(context.object)
            self.radius = max(abs(float(modifier[keys[0]])), abs(float(modifier[keys[2]])))
        except (ValueError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'radius')
        unit = json.loads(context.object['qc_color_source']).get('unit', 'unknown')
        self.layout.label(text='−R / 0 / +R [' + unit + ']')

    def execute(self, context):
        try:
            apply_range(context.object, (-self.radius, 0., self.radius))
        except (ValueError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_read_color_range(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.read_color_range'
    bl_label = 'Read Valid Color Field Range'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_color_source'))

    def begin(self, context):
        self._target = context.object
        modifier, keys = range_inputs(self._target)
        self._tree = modifier.node_group
        self._before = tuple(modifier[key] for key in keys)
        volume, self._field, self._binding = color_source(self._target)
        directory, digest = binding_key(volume)
        return Job('field_range', dataset=directory, dataset_sha256=digest,
                   field_array=self._field['array'])

    def accept(self, context, report):
        if context.object != self._target or self._target.name not in context.scene.objects:
            raise ValueError('Active view changed; color range was not applied')
        volume, field, token = color_source(self._target)
        modifier, keys = range_inputs(self._target)
        if (token != self._binding or modifier.node_group != self._tree
                or tuple(modifier[key] for key in keys) != self._before
                or report.get('dataset_sha256') != binding_key(volume)[1]
                or any(report.get(key) != field[key] for key in ('quantity', 'unit'))
                or report.get('field_array') != field['array']):
            raise ValueError('Color source or range changed during reading; result was not applied')
        apply_range(self._target, [report[key] for key in ('minimum', 'center', 'maximum')])
        self.report({'INFO'}, f"Read {report['valid_count']} valid grid points [{field['unit']}]")
