"""Ordered IRC geometry and energy views with imported Mayer overlays."""
import json

import bpy
from bpy.props import EnumProperty, StringProperty


def curve_view(directory, data, parent, values, name, role, y_offset, unit):
    from .views import bind, material
    count = len(values)
    low, high = min(values), max(values)
    span = high - low or 1
    coordinates = [(4 * index / max(1, count - 1), 0, 3 * (value - low) / span)
                   for index, value in enumerate(values)]
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = .02
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(count - 1)
    for point, xyz in zip(spline.points, coordinates):
        point.co = (*xyz, 1)
    curve.materials.append(material(name, (.12, .34, .78, 1)))
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = (0, y_offset, 0)
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'analysis'
    obj['qc_analysis_role'] = role
    obj['qc_chart'] = json.dumps({'unit': unit, 'minimum': low, 'maximum': high,
                                  'step_count': count, 'x': 'ordered IRC step'})
    return obj, coordinates


def cursor_view(directory, data, parent, coordinate, name, role, y_offset):
    from .external_results import point_view
    obj = point_view(directory, data, parent, [{'position_angstrom': coordinate}],
                     name, (.95, .2, .12, 1), role)
    obj.location = (0, y_offset, 0)
    return obj


class QCBLENDER_OT_import_irc(bpy.types.Operator):
    bl_idname = 'qcblender.import_irc_path'
    bl_label = 'Import Ordered IRC FCHK Path'
    bl_options = {'REGISTER', 'UNDO'}
    manifest_path: StringProperty(name='CSV manifest: step,fchk', subtype='FILE_PATH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        self.layout.prop(self, 'manifest_path')
        self.layout.label(text='CSV rows are the exact, 1-based step order')

    def execute(self, context):
        from ..irc import import_irc
        from .external_results import store_analysis
        from .graph import view_modifier
        from .views import atom_view
        try:
            data = import_irc(bpy.path.abspath(self.manifest_path))
            directory = store_analysis(data)
            root = atom_view(directory)
            root['qc_irc_step'] = 1
            root['qc_irc'] = True
            modifier = view_modifier(root)
            style = next(item for item in modifier.node_group.interface.items_tree
                         if item.item_type == 'SOCKET' and item.name == 'Style (0 ball-stick, 1 space-fill, 2 bonds)')
            modifier[style.identifier] = 1
            energies = data.arrays['irc_energies'].tolist()
            curve, coordinates = curve_view(directory, data, root, energies, 'QC IRC energy',
                                            'irc_energy', -5, 'hartree')
            cursor_view(directory, data, root, coordinates[0], 'QC IRC selected step', 'irc_cursor', -5)
        except (ValueError, OSError, KeyError, TypeError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_irc_step(bpy.types.Operator):
    bl_idname = 'qcblender.irc_step'
    bl_label = 'Change IRC Step'
    bl_options = {'REGISTER', 'UNDO'}
    direction: EnumProperty(items=[('PREV', 'Previous', ''), ('NEXT', 'Next', '')])

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and (obj.get('qc_irc') or (obj.parent and obj.parent.get('qc_irc')))

    def execute(self, context):
        from ..data import load_dataset
        root = context.object if context.object.get('qc_irc') else context.object.parent
        try:
            data = load_dataset(bpy.path.abspath(root['qc_dataset']))
            step = int(root['qc_irc_step']) + (1 if self.direction == 'NEXT' else -1)
            if not 1 <= step <= len(data.arrays['irc_energies']):
                raise ValueError('IRC step is outside the imported path')
            positions = data.arrays['irc_positions'][step - 1]
            root.data.vertices.foreach_set('co', positions.ravel())
            root.data.attributes['qc_equilibrium_position'].data.foreach_set('vector', positions.ravel())
            root.data.update()
            root['qc_irc_step'] = step
            for child in root.children:
                if child.get('qc_analysis_role') in ('irc_cursor', 'irc_mayer_cursor'):
                    line = next((item for item in root.children
                                 if item.get('qc_analysis_role') == ('irc_energy' if child['qc_analysis_role'] == 'irc_cursor' else 'irc_mayer_curve')), None)
                    if line is not None:
                        child.data.vertices[0].co = line.data.splines[0].points[step - 1].co[:3]
                        child.data.update()
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_import_irc_mayer(bpy.types.Operator):
    bl_idname = 'qcblender.import_irc_mayer'
    bl_label = 'Import IRC Mayer Bond Orders'
    bl_options = {'REGISTER', 'UNDO'}
    manifest_path: StringProperty(name='CSV manifest: step,mayer_output', subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_irc')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        self.layout.prop(self, 'manifest_path')

    def execute(self, context):
        from ..data import load_dataset
        from ..irc import import_irc_mayer
        from .external_results import store_analysis, table_view
        try:
            root = context.object
            if any(child.get('qc_analysis_role') == 'irc_mayer' for child in root.children):
                raise ValueError('This IRC path already has a Mayer import')
            path = load_dataset(bpy.path.abspath(root['qc_dataset']))
            result = import_irc_mayer(path, bpy.path.abspath(self.manifest_path))
            directory = store_analysis(result)
            obj = table_view(directory, result, root, 'QC IRC Mayer orders', 'irc_mayer')
            obj['qc_pair_a'], obj['qc_pair_b'] = map(int, result.arrays['mayer_pairs'][0])
            context.view_layer.objects.active = obj
            root.select_set(False)
            obj.select_set(True)
            bpy.ops.qcblender.plot_irc_mayer()
        except (ValueError, OSError, KeyError, TypeError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_plot_irc_mayer(bpy.types.Operator):
    bl_idname = 'qcblender.plot_irc_mayer'
    bl_label = 'Plot Selected Mayer Pair'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_analysis_role') == 'irc_mayer'

    def execute(self, context):
        from ..data import load_dataset
        obj = context.object
        try:
            data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
            pair = sorted((int(obj['qc_pair_a']), int(obj['qc_pair_b'])))
            matches = [index for index, value in enumerate(data.arrays['mayer_pairs']) if value.tolist() == pair]
            if len(matches) != 1:
                raise ValueError('Selected atom pair is absent from Mayer results')
            root = obj.parent
            for child in list(root.children):
                if child.get('qc_analysis_role') in ('irc_mayer_curve', 'irc_mayer_cursor'):
                    bpy.data.objects.remove(child, do_unlink=True)
            values = data.arrays['mayer_orders'][:, matches[0]].tolist()
            curve, coordinates = curve_view(bpy.path.abspath(obj['qc_dataset']), data, root, values,
                                            f'QC Mayer {pair[0]}-{pair[1]}', 'irc_mayer_curve', -10, 'dimensionless')
            cursor_view(bpy.path.abspath(obj['qc_dataset']), data, root, coordinates[int(root['qc_irc_step']) - 1],
                        'QC Mayer selected step', 'irc_mayer_cursor', -10)
            obj['qc_mayer_pair_index'] = matches[0]
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_irc(bpy.types.Panel):
    bl_label = 'IRC Path'
    bl_idname = 'QCBLENDER_PT_irc'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and (obj.get('qc_irc') or (obj.parent and obj.parent.get('qc_irc')))

    def draw(self, context):
        from ..data import load_dataset
        obj = context.object
        root = obj if obj.get('qc_irc') else obj.parent
        data = load_dataset(bpy.path.abspath(root['qc_dataset']))
        step = int(root['qc_irc_step'])
        layout = self.layout
        layout.label(text=f"Step {step} / {len(data.arrays['irc_energies'])}")
        layout.label(text=f"Energy: {data.arrays['irc_energies'][step-1]:.10f} hartree")
        row = layout.row(align=True)
        row.operator('qcblender.irc_step', text='Previous').direction = 'PREV'
        row.operator('qcblender.irc_step', text='Next').direction = 'NEXT'
        if root == obj:
            layout.operator('qcblender.import_irc_mayer', text='Import Mayer Results')
        if obj.get('qc_analysis_role') == 'irc_mayer':
            layout.prop(obj, '["qc_pair_a"]', text='Atom A (1-based)')
            layout.prop(obj, '["qc_pair_b"]', text='Atom B (1-based)')
            layout.operator('qcblender.plot_irc_mayer', text='Plot Pair')
            mayer = load_dataset(bpy.path.abspath(obj['qc_dataset']))
            index = obj.get('qc_mayer_pair_index')
            if index is not None:
                layout.label(text=f"Mayer order: {mayer.arrays['mayer_orders'][step-1, index]:.6g}")
