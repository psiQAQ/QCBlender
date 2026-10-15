"""Apply an explicit preset to an existing scalar or charge material."""
from ..i18n import error_text, iface, ui_layout
import json

import bpy
from bpy.props import EnumProperty, StringProperty

from ..color_presets import PRESETS, get_preset
from .copy_display import _state, _material_role


def ramp_snapshot(ramp):
    return {
        'color_mode': ramp.color_mode,
        'interpolation': ramp.interpolation,
        'hue_interpolation': ramp.hue_interpolation,
        'elements': tuple((item.position, tuple(item.color)) for item in ramp.elements),
    }


def _write_ramp(ramp, state):
    # One element must remain in Blender. Rebuild in position order, including
    # coincident positions from a user's original ramp when restoring a snapshot.
    while len(ramp.elements) > 1:
        ramp.elements.remove(ramp.elements[-1])
    position, color = state['elements'][0]
    ramp.elements[0].position = position
    ramp.elements[0].color = color
    for position, color in state['elements'][1:]:
        ramp.elements.new(position).color = color
    for name in ('color_mode', 'interpolation', 'hue_interpolation'):
        setattr(ramp, name, state[name])


def preset_target(obj, role):
    """Resolve and validate the displayed material without changing any data."""
    if obj is None or obj.get('qc_view_kind') not in ('atoms', 'field', 'slice'):
        raise ValueError('Select a standard scalar or charge QC view')
    if role not in ('scalar_map', 'charge_map'):
        raise ValueError('Color presets require scalar_map or charge_map')
    state = _state(obj)
    if role not in state['materials']:
        raise ValueError(f'The active view has no {role} material')
    mat = state['materials'][role][0]
    node = _material_role(mat, role)['color_ramp']
    for data in (obj, mat, mat.node_tree):
        if data.library is not None or not data.is_editable:
            raise ValueError(f'{data.name}: linked or read-only target cannot be edited')
    ramp = node.color_ramp
    if any(ramp.is_property_readonly(name) for name in
           ('color_mode', 'interpolation', 'hue_interpolation')):
        raise ValueError(f'{mat.name}: ColorRamp is read-only')
    tree = state['modifier'].node_group
    # ID session UIDs survive undo; raw pointers are used only while a dialog is open.
    identity = json.dumps((obj.session_uid, mat.session_uid, mat.node_tree.session_uid,
                           tree.session_uid, node.name, role))
    pointers = (obj.as_pointer(), mat.as_pointer(), mat.node_tree.as_pointer(),
                tree.as_pointer(), node.as_pointer())
    return {'material': mat, 'node': node, 'identity': identity, 'pointers': pointers}


def apply_preset(obj, role, identifier, *, expected_identity='', expected_pointers=None):
    """Preflight the target, then atomically replace only the ramp configuration."""
    preset = get_preset(identifier)
    target = preset_target(obj, role)
    if ((expected_identity and expected_identity != target['identity'])
            or (expected_pointers is not None and expected_pointers != target['pointers'])):
        raise ValueError('Color preset target changed; reopen the preset dialog')
    ramp = target['node'].color_ramp
    before = ramp_snapshot(ramp)
    after = {name: getattr(preset, name) for name in before}
    try:
        _write_ramp(ramp, after)
    except Exception as error:
        # RNA mutations can fail after removing elements; restore all ramp fields
        # before propagating the original error to the caller.
        try:
            _write_ramp(ramp, before)
        except Exception as restore_error:
            raise RuntimeError(f'Color preset failed: {error}; restoration failed: {restore_error}') from error
        raise
    return target


class QCBLENDER_OT_apply_color_preset(bpy.types.Operator):
    bl_idname = 'qcblender.apply_color_preset'
    bl_label = 'Apply Color Ramp Preset'
    bl_description = 'Replace the material color ramp on confirmation; shared views update together'
    bl_options = {'REGISTER', 'UNDO'}

    material_role: EnumProperty(items=[('scalar_map', 'Scalar map', ''),
                                       ('charge_map', 'Charge map', '')],
                                default='scalar_map', options={'HIDDEN'})
    preset: EnumProperty(name='Color Ramp Preset', items=[(key, value.label, '')
                         for key, value in PRESETS.items()], default='QC_DEFAULT')
    target_identity: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    target_label: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') in ('atoms', 'field', 'slice')

    def invoke(self, context, event):
        try:
            target = preset_target(context.object, self.material_role)
            self.target_identity = target['identity']
            self.target_label = target['material'].name
            self._dialog_pointers = target['pointers']
        except (ValueError, KeyError, TypeError, AttributeError, ReferenceError, RuntimeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        ui_layout(self.layout).label(text=iface('Target material: {value0}', value0=self.target_label))
        ui_layout(self.layout).label(text='All views and legends sharing this material update together.')
        ui_layout(self.layout).label(text='Confirm to replace the current stops and interpolation; cancel to keep them.')
        ui_layout(self.layout).prop(self, 'preset')

    def cancel(self, context):
        self.target_identity = ''
        if hasattr(self, '_dialog_pointers'):
            del self._dialog_pointers

    def execute(self, context):
        try:
            target = apply_preset(context.object, self.material_role, self.preset,
                                  expected_identity=self.target_identity,
                                  expected_pointers=getattr(self, '_dialog_pointers', None))
            self.target_identity = target['identity']
            self.target_label = target['material'].name
            if hasattr(self, '_dialog_pointers'):
                del self._dialog_pointers
        except (ValueError, OSError, KeyError, TypeError, AttributeError, ReferenceError, RuntimeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}
