"""Scene display layers use native objects, node inputs and Blender undo."""
import bpy
from bpy.props import EnumProperty, StringProperty


def display_layers(scene):
    return sorted((obj for obj in scene.objects
                   if obj.get('qc_view_kind') in ('atoms', 'field', 'slice', 'fog', 'dipole', 'spectrum')),
                  key=lambda obj: (obj.get('qc_layer_order', 0), obj.name))


def activate(context, obj):
    for previous in context.selected_objects:
        previous.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def copy_layer(source, collection):
    obj = source.copy()
    obj.data = source.data.copy()
    collection.objects.link(obj)
    materials = {}

    def copy_material(mat):
        if mat not in materials:
            materials[mat] = mat.copy()
        return materials[mat]

    for index, mat in enumerate(obj.data.materials):
        if mat:
            obj.data.materials[index] = copy_material(mat)
    for modifier in obj.modifiers:
        if modifier.type != 'NODES' or modifier.node_group is None:
            continue
        modifier.node_group = modifier.node_group.copy()
        tree = modifier.node_group
        for item in tree.interface.items_tree:
            if item.item_type == 'SOCKET' and item.socket_type == 'NodeSocketMaterial':
                if item.default_value:
                    item.default_value = copy_material(item.default_value)
                mat = modifier.get(item.identifier)
                if mat:
                    modifier[item.identifier] = copy_material(mat)
        for node in tree.nodes:
            for input_socket in node.inputs:
                if input_socket.type == 'MATERIAL' and input_socket.default_value:
                    input_socket.default_value = copy_material(input_socket.default_value)
    # A copied vibration view needs its own IR selection colors.
    if source.get('qc_view_kind') == 'atoms' and source.qc_settings.spectrum:
        spectrum = copy_layer(source.qc_settings.spectrum, collection)
        spectrum.parent = obj
        obj.qc_settings.spectrum = spectrum
        for label in source.qc_settings.spectrum.children:
            if label.type == 'FONT':
                copied = label.copy()
                copied.data = label.data.copy()
                collection.objects.link(copied)
                copied.parent = spectrum
    return obj


class QCBLENDER_OT_layer_action(bpy.types.Operator):
    bl_idname = 'qcblender.layer_action'
    bl_label = 'Manage Display Layer'
    bl_options = {'REGISTER', 'UNDO'}
    target: StringProperty()
    action: EnumProperty(items=[('SELECT', 'Select', ''), ('DUPLICATE', 'Duplicate', ''),
        ('REMOVE', 'Remove', ''), ('UP', 'Move up', ''), ('DOWN', 'Move down', ''),
        ('VISIBILITY', 'Toggle viewport', '')])

    def execute(self, context):
        layers = display_layers(context.scene)
        obj = context.scene.objects.get(self.target)
        if obj not in layers:
            self.report({'ERROR'}, 'Display layer no longer exists in this scene')
            return {'CANCELLED'}
        if self.action == 'SELECT':
            activate(context, obj)
        elif self.action == 'VISIBILITY':
            obj.hide_set(not obj.hide_get())
        elif self.action == 'DUPLICATE':
            copied = copy_layer(obj, context.collection)
            layers.insert(layers.index(obj) + 1, copied)
            for index, layer in enumerate(layers):
                layer['qc_layer_order'] = index
            activate(context, copied)
        elif self.action == 'REMOVE':
            index = layers.index(obj)
            # Keep scientific source objects and other display layers in place.
            for child in list(obj.children):
                matrix = child.matrix_world.copy()
                child.parent = obj.parent
                child.matrix_world = matrix
            bpy.data.objects.remove(obj, do_unlink=True)
            remaining = display_layers(context.scene)
            if remaining:
                activate(context, remaining[min(index, len(remaining) - 1)])
        else:
            index = layers.index(obj)
            destination = index + (-1 if self.action == 'UP' else 1)
            if 0 <= destination < len(layers):
                layers[index], layers[destination] = layers[destination], layers[index]
                for rank, layer in enumerate(layers):
                    layer['qc_layer_order'] = rank
        return {'FINISHED'}


class QCBLENDER_OT_add_surface(bpy.types.Operator):
    bl_idname = 'qcblender.add_surface_layer'
    bl_label = 'Add Isosurface Layer'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.qc_settings.volume is not None

    def execute(self, context):
        import json
        from ..data import load_dataset
        from .views import field_view
        source = context.object
        directory = bpy.path.abspath(source['qc_dataset'])
        try:
            field = json.loads(source['qc_field'])
            data = load_dataset(directory)
            index = next(i for i, f in enumerate(data.metadata['fields']) if f['array'] == field['array'])
            obj = field_view(directory, source.parent, index)
        except (ValueError, OSError, KeyError, StopIteration) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        obj.matrix_world = source.matrix_world.copy()
        obj.qc_settings.volume.matrix_world = source.qc_settings.volume.matrix_world.copy()
        activate(context, obj)
        return {'FINISHED'}


class QCBLENDER_OT_new_current_view(bpy.types.Operator):
    bl_idname = 'qcblender.new_current_view'
    bl_label = 'Create Current-Version View (Keep Original)'
    bl_description = 'Create a standard view from the same dataset; preserve the original custom graph'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') in ('atoms', 'field', 'fog', 'slice')

    def execute(self, context):
        import json
        from .views import atom_view, field_view
        from .fog import fog_view
        from .graph import view_modifier
        from ..data import load_dataset
        source = context.object
        try:
            directory = bpy.path.abspath(source['qc_dataset'])
            kind = source['qc_view_kind']
            if kind == 'atoms':
                obj = atom_view(directory)
                obj.parent = source.parent
            elif kind == 'fog':
                obj = fog_view(source)
            elif kind == 'slice':
                if bpy.ops.qcblender.create_slice() != {'FINISHED'}:
                    return {'CANCELLED'}
                obj = context.object
            else:
                field = json.loads(source['qc_field'])
                data = load_dataset(directory)
                index = next(i for i, f in enumerate(data.metadata['fields']) if f['array'] == field['array'])
                obj = field_view(directory, source.parent, index)
                obj.qc_settings.volume.matrix_world = source.qc_settings.volume.matrix_world.copy()
            obj.matrix_world = source.matrix_world.copy()
            # Only transfer matching public parameters, never replace either graph.
            old, new = view_modifier(source), view_modifier(obj)
            values = {s.name: old.get(s.identifier, s.default_value) for s in old.node_group.interface.items_tree
                      if s.item_type == 'SOCKET' and s.in_out == 'INPUT' and hasattr(s, 'default_value')}
            for item in new.node_group.interface.items_tree:
                if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.name in values:
                    if kind == 'fog' and item.socket_type == 'NodeSocketMaterial':
                        continue  # Keep the current transfer graph; the original material remains on the original view.
                    value = values[item.name]
                    if item.socket_type == 'NodeSocketMaterial' and value:
                        value = value.copy()
                    new[item.identifier] = value
            activate(context, obj)
        except (ValueError, KeyError, OSError, StopIteration) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_layers(bpy.types.Panel):
    bl_label = 'Display Layers'
    bl_idname = 'QCBLENDER_PT_layers'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_order = -1

    def draw(self, context):
        layout = self.layout
        layout.ui_units_x = 18
        row = layout.row(align=True)
        row.operator('qcblender.new_current_view', text='New Current-Version View', icon='DUPLICATE')
        row = layout.row(align=True)
        row.operator('qcblender.add_surface_layer', text='Surface')
        row.operator('qcblender.create_fog', text='Fog')
        row.operator('qcblender.create_slice', text='Slice')
        for obj in display_layers(context.scene):
            row = layout.row(align=True)
            select = row.operator('qcblender.layer_action', text='', icon='RESTRICT_SELECT_OFF',
                                  depress=obj == context.object)
            select.target, select.action = obj.name, 'SELECT'
            row.prop(obj, 'name', text='')
            operator = row.operator('qcblender.layer_action', text='', icon='HIDE_ON' if obj.hide_get() else 'HIDE_OFF')
            operator.target, operator.action = obj.name, 'VISIBILITY'
            row.prop(obj, 'hide_render', text='', icon='RESTRICT_RENDER_ON' if obj.hide_render else 'RESTRICT_RENDER_OFF')
        obj = context.object
        if obj in display_layers(context.scene):
            row = layout.row(align=True)
            for action, text, icon in [('DUPLICATE', 'Duplicate', 'DUPLICATE'), ('REMOVE', 'Remove', 'X'),
                                       ('UP', '', 'TRIA_UP'), ('DOWN', '', 'TRIA_DOWN')]:
                operator = row.operator('qcblender.layer_action', text=text, icon=icon)
                operator.target, operator.action = obj.name, action
        layout.label(text='Select a layer; edit its inputs below')
