"""Localize known QC rows while retaining Blender's native property editor."""
import bpy
from bpy.props import StringProperty
import rna_prop_ui

from ..i18n import iface, tip
from ..property_labels import LABELS

_original_draw = None
_panel = None


class QCBLENDER_OT_property_help(bpy.types.Operator):
    bl_idname = 'qcblender.property_help'
    bl_label = 'QCBlender'
    bl_options = {'INTERNAL'}
    property_key: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def description(cls, context, properties):
        key = properties.property_key
        record = LABELS.get(key)
        return key + ('\n' + tip(record[1]) if record else '')

    def execute(self, context):
        key = self.property_key
        record = LABELS.get(key)
        def draw(menu, context):
            menu.layout.label(text=key, translate=False)
            if record:
                menu.layout.label(text=tip(record[1]), translate=False)
        context.window_manager.popup_menu(draw, title=iface(record[0]) if record else key, icon='INFO')
        return {'FINISHED'}


class _PropertyLayout:
    def __init__(self, layout):
        object.__setattr__(self, '_layout', layout)

    def __setattr__(self, key, value):
        setattr(self._layout, key, value)

    def __getattr__(self, name):
        original = getattr(self._layout, name)
        if name == 'label':
            def label(*args, **kwargs):
                key = kwargs.get('text')
                if key in LABELS and kwargs.get('translate') is False:
                    props = self._layout.operator('qcblender.property_help', text=iface(LABELS[key][0]),
                                                  translate=False, emboss=False)
                    props.property_key = key
                    return None
                return original(*args, **kwargs)
            return label
        if name in {'row', 'column', 'split', 'box', 'grid_flow', 'column_flow'}:
            def container(*args, **kwargs):
                return _PropertyLayout(original(*args, **kwargs))
            return container
        return original


def _draw(self, context):
    obj, _ = rna_prop_ui.rna_idprop_context_value(context, self._context_path, self._property_type)
    if obj is None or not any(key in LABELS for key in obj.keys()):
        return _original_draw(self, context)
    rna_prop_ui.draw(_PropertyLayout(self.layout), context, self._context_path, self._property_type)


def register():
    global _original_draw, _panel
    from bl_ui.properties_object import OBJECT_PT_custom_props
    if _original_draw is not None:
        raise RuntimeError('QCBlender property presentation already registered')
    _panel = OBJECT_PT_custom_props
    _original_draw = _panel.draw
    _panel.draw = _draw


def unregister():
    global _original_draw, _panel
    if _panel is not None and _panel.draw is _draw:
        _panel.draw = _original_draw
    _original_draw = None
    _panel = None
