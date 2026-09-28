"""Object Properties browser for external result display state."""
import hashlib
import json
from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty

from .ui import AsyncOperation


class QCBLENDER_PG_result_browser(bpy.types.PropertyGroup):
    swap_axes: BoolProperty(name='Swap scatter axes', default=False)
    x_low_on: BoolProperty(name='X minimum', default=False)
    x_high_on: BoolProperty(name='X maximum', default=False)
    y_low_on: BoolProperty(name='Y minimum', default=False)
    y_high_on: BoolProperty(name='Y maximum', default=False)
    x_low: FloatProperty(name='X from')
    x_high: FloatProperty(name='X to')
    y_low: FloatProperty(name='Y from')
    y_high: FloatProperty(name='Y to')
    source_number: IntProperty(name='Source number (0 = all)', min=0)
    esp_kind: EnumProperty(name='Type', items=[('ALL', 'All', ''),
        ('maximum', 'Maximum', ''), ('minimum', 'Minimum', '')])
    aim_type: EnumProperty(name='Type', items=[('ALL', 'All', ''), ('C', 'Nuclear', ''),
        ('N', 'Bond', ''), ('O', 'Ring', ''), ('F', 'Cage', '')])
    aim_numeric_key: StringProperty(name='Numeric CP property', default='')
    value_low_on: BoolProperty(name='Value minimum', default=False)
    value_high_on: BoolProperty(name='Value maximum', default=False)
    value_low: FloatProperty(name='Value from')
    value_high: FloatProperty(name='Value to')
    marker_size: FloatProperty(name='Highlight radius (Å)', default=.12, min=.01, max=2)
    show_labels: BoolProperty(name='Show source label', default=True)
    show_points: BoolProperty(name='Show matching points', default=True)
    row_index: IntProperty(name='Match (1-based)', default=1, min=1)
    orbital_type: EnumProperty(name='Orbital type', items=[('ALL', 'All', ''), ('BD', 'BD', ''),
        ('BD*', 'BD*', ''), ('CR', 'CR', ''), ('LP', 'LP', ''), ('LP*', 'LP*', ''),
        ('RY', 'RY', ''), ('RY*', 'RY*', ''), ('LV', 'LV', ''), ('3C', '3C', ''), ('3C*', '3C*', '')])
    occupancy_low_on: BoolProperty(name='Occupancy minimum', default=False)
    occupancy_high_on: BoolProperty(name='Occupancy maximum', default=False)
    occupancy_low: FloatProperty(name='Occupancy from')
    occupancy_high: FloatProperty(name='Occupancy to')
    donor: IntProperty(name='Donor number (0 = all)', min=0)
    acceptor: IntProperty(name='Acceptor number (0 = all)', min=0)
    e2_low_on: BoolProperty(name='E(2) minimum', default=False)
    e2_high_on: BoolProperty(name='E(2) maximum', default=False)
    e2_low: FloatProperty(name='E(2) from')
    e2_high: FloatProperty(name='E(2) to')
    nbo_orbital_sort: EnumProperty(name='Orbital order', items=[
        ('source', 'Source order', ''), ('number', 'Source number', ''),
        ('type', 'Type, then number', ''),
        ('occupancy_desc', 'Occupancy, high to low', '')])
    nbo_interaction_sort: EnumProperty(name='E(2) order', items=[
        ('source', 'Source order', ''), ('donor', 'Donor, then acceptor', ''),
        ('acceptor', 'Acceptor, then donor', ''),
        ('e2_desc', 'E(2), high to low', '')])
    area_range_mode: EnumProperty(name='Area bin selection', items=[
        ('center', 'Center in range', 'Select bins whose recorded center is in range'),
        ('source_interval', 'Recorded interval overlaps range',
         'Select whole bins whose recorded Begin/End interval overlaps the range')])
    spin: EnumProperty(name='Spin', items=[('ALL', 'All', ''), ('Total', 'Total', ''),
                                            ('Alpha', 'Alpha', ''), ('Beta', 'Beta', '')])
    eigen_side: EnumProperty(name='Eigenvalue', items=[('either', 'Either', ''),
        ('positive', 'Positive orbital', ''), ('negative', 'Negative orbital', '')])
    eigen_low_on: BoolProperty(name='Eigenvalue minimum', default=False)
    eigen_high_on: BoolProperty(name='Eigenvalue maximum', default=False)
    eigen_low: FloatProperty(name='Eigenvalue from')
    eigen_high: FloatProperty(name='Eigenvalue to')
    sort_by: EnumProperty(name='Sort', items=[('pair', 'Pair', ''), ('pair_energy', 'Pair energy', ''),
        ('positive_eigenvalue', 'Positive eigenvalue', ''),
        ('negative_eigenvalue', 'Negative eigenvalue', '')])


def attach_properties():
    bpy.types.Object.qc_result_browser = PointerProperty(type=QCBLENDER_PG_result_browser)


def detach_properties():
    if hasattr(bpy.types.Object, 'qc_result_browser'):
        del bpy.types.Object.qc_result_browser


def _bound(state, prefix, end):
    return getattr(state, prefix + '_' + end) if getattr(state, prefix + '_' + end + '_on') else None


def _scatter_parameters(state):
    x_field, y_field = (0, 1) if state.swap_axes else (1, 0)
    return {'x_field': x_field, 'y_field': y_field,
            'x_min': _bound(state, 'x', 'low'), 'x_max': _bound(state, 'x', 'high'),
            'y_min': _bound(state, 'y', 'low'), 'y_max': _bound(state, 'y', 'high')}


def _source_identity(obj, meta):
    return {'dataset_sha256': obj['qc_dataset_sha256'],
            'source_sha256': meta['source']['sha256'], 'role': obj.get('qc_analysis_role', obj.get('qc_view_kind'))}


def _focus_visibility(part, visible):
    hidden = not visible
    if 'qc_layer_restore_viewport' in part:
        part['qc_layer_restore_viewport'] = hidden
    if 'qc_layer_restore_render' in part:
        part['qc_layer_restore_render'] = hidden
    part.hide_set(hidden)
    part.hide_render = hidden


def _save_state(obj, meta, state):
    obj['qc_result_displaystate'] = json.dumps(state, sort_keys=True)
    obj['qc_result_source_identity'] = json.dumps(_source_identity(obj, meta), sort_keys=True)


def _records(analysis, role, state):
    from ..result_filters import area_selection, nbo_selection, nocv_selection, point_selection

    low, high = _bound(state, 'value', 'low'), _bound(state, 'value', 'high')
    if role in ('esp_area',):
        return area_selection(analysis, low, high, state.area_range_mode)
    if role.startswith(('esp_', 'aim_')) and role != 'aim_paths':
        chosen = state.esp_kind if role.startswith('esp_') else state.aim_type
        source_kind = role.split('_', 1)[1]
        kind = source_kind if chosen == 'ALL' else chosen
        indexes = point_selection(analysis, state.source_number or None, kind, low, high,
                                  state.aim_numeric_key if role.startswith('aim_') else None)
        result = {'indexes': indexes if kind == source_kind else [],
                  'type_mismatch': kind != source_kind}
        if role.startswith('aim_'):
            result['value_key'] = state.aim_numeric_key
        return result
    if role == 'ets_nocv':
        return {'indexes': nocv_selection(analysis, state.source_number or None,
            None if state.spin == 'ALL' else state.spin,
            _bound(state, 'eigen', 'low'), _bound(state, 'eigen', 'high'), low, high,
            state.eigen_side, state.sort_by)}
    if role == 'nbo':
        selected = nbo_selection(analysis, state.source_number or None,
            None if state.orbital_type == 'ALL' else state.orbital_type,
            _bound(state, 'occupancy', 'low'), _bound(state, 'occupancy', 'high'),
            state.donor or None, state.acceptor or None,
            _bound(state, 'e2', 'low'), _bound(state, 'e2', 'high'),
            state.nbo_orbital_sort, state.nbo_interaction_sort)
        return dict(selected, orbital_sort=state.nbo_orbital_sort,
                    interaction_sort=state.nbo_interaction_sort)
    raise ValueError('No record browser for this object')


def _focus(context, obj, row, state, analysis):
    from mathutils import Vector
    from ..result_filters import point_label
    from .views import material

    marker = next((child for child in obj.children if child.get('qc_result_focus')), None)
    if marker is None:
        mesh = bpy.data.meshes.new('QC result focus')
        mesh.from_pydata([(0, 0, 0)], [], [])
        marker = bpy.data.objects.new('QC result focus', mesh)
        obj.users_collection[0].objects.link(marker)
        marker.parent = obj
        marker['qc_result_focus'] = True
        tree = bpy.data.node_groups.new('QC result focus points', 'GeometryNodeTree')
        tree.is_modifier = True
        tree.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        nodes, links = tree.nodes, tree.links
        dots = nodes.new('GeometryNodeMeshToPoints')
        dots.mode = 'VERTICES'
        assign = nodes.new('GeometryNodeSetMaterial')
        assign.inputs['Material'].default_value = material('QC selected result', (1, .85, .05, 1))
        links.new(nodes.new('NodeGroupInput').outputs['Geometry'], dots.inputs['Mesh'])
        links.new(dots.outputs['Points'], assign.inputs['Geometry'])
        links.new(assign.outputs['Geometry'], nodes.new('NodeGroupOutput').inputs['Geometry'])
        marker.modifiers.new('QC Result Focus', 'NODES').node_group = tree
        label_curve = bpy.data.curves.new('QC result label', 'FONT')
        label = bpy.data.objects.new('QC result label', label_curve)
        obj.users_collection[0].objects.link(label)
        label.parent = marker
        label['qc_result_label'] = True
    marker.location = Vector(row['position_angstrom'])
    dots = next(node for node in marker.modifiers['QC Result Focus'].node_group.nodes
                if node.bl_idname == 'GeometryNodeMeshToPoints')
    dots.inputs['Radius'].default_value = state.marker_size
    _focus_visibility(marker, True)
    label = next(child for child in marker.children if child.get('qc_result_label'))
    label.data.body = point_label(analysis, row, state.aim_numeric_key)
    label.data.size = state.marker_size * 2
    label.location = (state.marker_size * 1.5, 0, 0)
    _focus_visibility(label, state.show_labels)
    from .layers import sync_chart_children
    sync_chart_children(obj)
    world = obj.matrix_world @ Vector(row['position_angstrom'])
    for area in context.screen.areas if context.screen is not None else ():
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_location = world
            break


def _writable_mesh(obj):
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    return obj.data


class QCBLENDER_OT_apply_result_filter(bpy.types.Operator):
    bl_idname = 'qcblender.apply_result_filter'
    bl_label = 'Apply Result Filter'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'result_filter')

    def execute(self, context):
        from .source_browser import read_metadata

        obj = context.object
        try:
            meta = read_metadata(obj)
            analysis = meta['analysis']
            role = obj.get('qc_analysis_role', obj.get('qc_view_kind'))
            state = obj.qc_result_browser
            result = _records(analysis, role, state)
            if role.startswith(('esp_', 'aim_')) and role != 'esp_area':
                key = 'extrema' if analysis['kind'] == 'ESP' else 'critical_points'
                indexes = result['indexes']
                selected = [analysis[key][i]['position_angstrom'] for i in indexes]
                mesh = _writable_mesh(obj)
                mesh.clear_geometry()
                mesh.from_pydata(selected if state.show_points else [], [], [])
                mesh.update()
                marker = next((child for child in obj.children if child.get('qc_result_focus')), None)
                if indexes and state.row_index <= len(indexes):
                    _focus(context, obj, analysis[key][indexes[state.row_index - 1]], state, analysis)
                elif marker:
                    _focus_visibility(marker, False)
                    for child in marker.children:
                        if child.get('qc_result_label'):
                            _focus_visibility(child, False)
                    from .layers import sync_chart_children
                    sync_chart_children(obj)
            elif role == 'esp_area':
                bins = analysis['area_bins']
                indexes = result['indexes']
                centers = [bins[i]['center'] for i in indexes]
                areas = [bins[i]['area'] for i in indexes]
                low = min((row['center'] for row in bins), default=0)
                width = max((row['center'] for row in bins), default=1) - low or 1
                height = max((row['area'] for row in bins), default=1) or 1
                vertices, faces = [], []
                for center, area in zip(centers, areas):
                    x, y = (center - low) / width * 4, area / height * 3
                    half = min(.4, 1.6 / len(bins))
                    start = len(vertices)
                    vertices.extend([(x-half, 0, 0), (x+half, 0, 0),
                                     (x+half, 0, y), (x-half, 0, y)])
                    faces.append((start, start+1, start+2, start+3))
                mesh = _writable_mesh(obj)
                mesh.clear_geometry()
                mesh.from_pydata(vertices, [], faces)
                mesh.update()
            elif role == 'nbo':
                if result['orbitals']:
                    obj['qc_nbo_index'] = result['orbitals'][min(state.row_index, len(result['orbitals'])) - 1] + 1
                if result['interactions']:
                    obj['qc_e2_index'] = result['interactions'][min(state.row_index, len(result['interactions'])) - 1] + 1
            elif role == 'ets_nocv' and result['indexes'] and state.row_index <= len(result['indexes']):
                row = analysis['pairs'][result['indexes'][state.row_index - 1]]
                matches = []
                for candidate in context.scene.objects:
                    if candidate.get('qc_analysis_role') != 'nocv_field' or candidate.get('qc_ets_table_source') != obj.get('qc_source_sha256'):
                        continue
                    record = read_metadata(candidate).get('analysis', {})
                    if (record.get('pair', {}).get('pair'), record.get('spin'), record.get('table_source')) == (row['pair'], row['spin'], obj.get('qc_source_sha256')):
                        matches.append(candidate)
                if len(matches) > 1:
                    raise ValueError('Several NOCV views match this pair and spin; choose a unique view')
                if matches:
                    target = matches[0]
                    for selected in context.selected_objects:
                        selected.select_set(False)
                    target.select_set(True)
                    context.view_layer.objects.active = target
                    self.report({'INFO'}, f"Located NOCV pair {row['pair']} {row['spin']}")
                else:
                    self.report({'INFO'}, 'No existing NOCV field view matches this pair and spin')
            _save_state(obj, meta, result)
            if result.get('type_mismatch'):
                self.report({'INFO'}, 'Selected type belongs to another display layer; this layer has no matches')
            else:
                self.report({'INFO'}, 'Result display updated; source records unchanged')
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_filter_result_scatter(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.filter_result_scatter'
    bl_label = 'Update Result Scatter'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'result_scatter')

    def begin(self, context):
        from .jobs import Job
        from .source_browser import read_metadata

        view = context.object
        meta = read_metadata(view)
        self._target_name = view.name
        self._target_pointer = view.as_pointer()
        self._binding = (view['qc_dataset'], view['qc_dataset_sha256'],
                         view.get('qc_source_sha256'), view.get('qc_view_kind'))
        self._source_identity = _source_identity(view, meta)
        self._field_identity = json.dumps(meta['fields'], sort_keys=True)
        parent = view.parent
        self._parent_pointer = parent.as_pointer() if parent else None
        self._parent_binding = ((parent.get('qc_dataset'), parent.get('qc_dataset_sha256'),
                                 parent.get('qc_source_sha256'), parent.get('qc_field'))
                                if parent else None)
        path = Path(bpy.path.abspath(view['qc_dataset'])).resolve(strict=True)
        digest = hashlib.sha256((path / 'manifest.json').read_bytes()).hexdigest()
        if digest != view['qc_dataset_sha256']:
            raise ValueError('Scatter source changed after binding')
        self._request = dict(dataset=str(path), dataset_sha256=digest,
                             **_scatter_parameters(view.qc_result_browser))
        return Job('result_scatter', **self._request)

    def accept(self, context, report):
        import numpy as np
        from ..result_filters import verified_scatter_points
        from .source_browser import read_metadata

        view = bpy.data.objects.get(self._target_name)
        if view is None or view.as_pointer() != self._target_pointer:
            raise ValueError('Scatter view was removed or renamed during filtering')
        if ((view.get('qc_dataset'), view.get('qc_dataset_sha256'),
             view.get('qc_source_sha256'), view.get('qc_view_kind')) != self._binding):
            raise ValueError('Scatter view binding changed during filtering')
        parent = view.parent
        if ((parent.as_pointer() if parent else None) != self._parent_pointer
                or ((parent.get('qc_dataset'), parent.get('qc_dataset_sha256'),
                     parent.get('qc_source_sha256'), parent.get('qc_field')) if parent else None)
                != self._parent_binding):
            raise ValueError('Scatter source object changed during filtering')
        controls = _scatter_parameters(view.qc_result_browser)
        if controls != {key: self._request[key] for key in controls}:
            raise ValueError('Scatter axes or filters changed during filtering')
        path = Path(bpy.path.abspath(view['qc_dataset'])).resolve(strict=True)
        if (str(path) != self._request['dataset']
                or hashlib.sha256((path / 'manifest.json').read_bytes()).hexdigest()
                != self._request['dataset_sha256']):
            raise ValueError('Scatter source changed during filtering')
        meta = read_metadata(view)
        if (_source_identity(view, meta) != self._source_identity
                or json.dumps(meta['fields'], sort_keys=True) != self._field_identity):
            raise ValueError('Scatter field identity changed during filtering')
        points_path = self._job.directory / 'scatter.npy'
        points = verified_scatter_points(points_path, report,
                                         self._request['x_field'], self._request['y_field'])
        fields = meta['fields']
        minimum = points.min(axis=0) if len(points) else np.zeros(2)
        maximum = points.max(axis=0) if len(points) else np.zeros(2)
        span = maximum - minimum
        span[span == 0] = 1
        scaled = (points - minimum) / span * 4
        mesh = _writable_mesh(view)
        mesh.clear_geometry()
        mesh.from_pydata([(float(x), 0, float(y)) for x, y in scaled], [], [])
        mesh.update()
        x_field, y_field = self._request['x_field'], self._request['y_field']
        view['qc_scatter'] = json.dumps({'x_quantity': fields[x_field]['quantity'],
            'x_unit': fields[x_field]['unit'], 'y_quantity': fields[y_field]['quantity'],
            'y_unit': fields[y_field]['unit'], 'minimum': minimum.tolist(),
            'maximum': maximum.tolist(), 'sample_count': len(points),
            'matching_count': report['matching_count'], 'axis_scale': 'linear'})
        display = {key: self._request[key] for key in ('x_field', 'y_field',
                   'x_min', 'x_max', 'y_min', 'y_max')}
        _save_state(view, meta, dict(display, matching_count=report['matching_count'],
                                     displayed_count=report['displayed_count']))
        self.report({'INFO'}, f"Scatter: {report['matching_count']} matched, {report['displayed_count']} displayed")


class QCBLENDER_PT_result_browser(bpy.types.Panel):
    bl_label = 'External Result Browser'
    bl_idname = 'QCBLENDER_PT_result_browser'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and (obj.get('qc_view_kind') in ('scatter', 'nbo') or
            obj.get('qc_analysis_role') in ('esp_maximum', 'esp_minimum', 'esp_area',
                'aim_C', 'aim_N', 'aim_O', 'aim_F', 'aim_paths', 'ets_nocv'))

    def draw(self, context):
        from .capabilities import action_button, record
        from .source_browser import cached_metadata

        obj, layout = context.object, self.layout
        state = obj.qc_result_browser
        meta = cached_metadata(obj)
        if not meta or meta.get('error'):
            layout.label(text=meta.get('error', 'Refresh Sources to browse records'), icon='ERROR')
            return
        analysis = meta.get('analysis', {})
        role = obj.get('qc_analysis_role', obj.get('qc_view_kind'))
        if role == 'aim_paths':
            paths = analysis.get('paths', [])
            layout.label(text=f'{len(paths)} recorded AIM paths')
            layout.prop(state, 'row_index', text='Path (1-based)')
            if state.row_index <= len(paths):
                path = paths[state.row_index - 1]
                layout.label(text=f"Source residue {path['residue']} | {len(path['points_angstrom'])} points")
            layout.label(text='Path geometry and visibility use the native object controls')
            return
        saved = record(obj, 'qc_result_displaystate')
        if saved and record(obj, 'qc_result_source_identity') != _source_identity(obj, meta):
            layout.label(text='Display state belongs to another source; apply the filter again', icon='ERROR')
            saved = {}
        if role == 'scatter':
            layout.prop(state, 'swap_axes')
            for axis in ('x', 'y'):
                row = layout.row(align=True)
                row.prop(state, axis + '_low_on', text='')
                row.prop(state, axis + '_low', text=axis.upper() + ' from')
                row.prop(state, axis + '_high_on', text='')
                row.prop(state, axis + '_high', text='to')
            action_button(layout, context, 'result_scatter', 'qcblender.filter_result_scatter', '更新散点')
            if saved:
                layout.label(text=f"Matched {saved.get('matching_count', 0)} | displayed {saved.get('displayed_count', 0)}")
            return
        if role != 'esp_area':
            layout.prop(state, 'source_number', text='Source number' if role != 'ets_nocv' else 'Pair number')
        if role.startswith(('esp_', 'aim_')) and role != 'esp_area':
            layout.label(text=f"Source type: {role.split('_', 1)[1]} | switch layer for other types")
            if role.startswith('esp_'):
                _draw_range(layout, state, 'value', f"ESP value [{analysis.get('extrema_unit', 'unit unknown')}]")
            else:
                layout.prop(state, 'aim_numeric_key')
                _draw_range(layout, state, 'value', 'Selected CP property value')
                layout.label(text='Use the exact numeric key from the CP source record')
            layout.prop(state, 'marker_size')
            layout.prop(state, 'show_labels')
            layout.prop(state, 'show_points')
        elif role == 'esp_area':
            layout.prop(state, 'area_range_mode')
            if (state.area_range_mode == 'source_interval'
                    and any(row.get('begin') is None or row.get('end') is None
                            for row in analysis.get('area_bins', []))):
                layout.label(text='This table has no recorded Begin/End bounds', icon='ERROR')
            label = ('Recorded interval overlap' if state.area_range_mode == 'source_interval'
                     else 'Center')
            _draw_range(layout, state, 'value', f"{label} [{analysis.get('distribution_center_unit', 'unit unknown')}]")
            if state.area_range_mode == 'source_interval':
                layout.label(text='Whole source bins are selected; areas are not split')
        elif role == 'nbo':
            layout.prop(state, 'orbital_type')
            _draw_range(layout, state, 'occupancy', 'Occupancy')
            layout.prop(state, 'nbo_orbital_sort')
            layout.prop(state, 'donor')
            layout.prop(state, 'acceptor')
            _draw_range(layout, state, 'e2', 'E(2) kcal/mol')
            layout.prop(state, 'nbo_interaction_sort')
        elif role == 'ets_nocv':
            layout.prop(state, 'spin')
            layout.prop(state, 'eigen_side')
            _draw_range(layout, state, 'eigen', 'Eigenvalue')
            _draw_range(layout, state, 'value', f"Pair energy [{analysis.get('energy_unit', 'unit unknown')}]")
            layout.prop(state, 'sort_by')
        layout.prop(state, 'row_index')
        action_button(layout, context, 'result_filter', 'qcblender.apply_result_filter', '应用筛选')
        if saved:
            if role == 'esp_area':
                layout.label(text=f"Applied selection: {saved.get('selection_mode', 'center')}")
                layout.label(text=f"Total {saved.get('total_area', 0):.6g} | displayed {saved.get('displayed_area', 0):.6g} {analysis.get('area_unit', '')}")
                layout.label(text=f"Source percentages shown: {saved.get('displayed_source_percentage', 0):.6g}%")
                indexes = saved.get('indexes', [])
                if indexes and state.row_index <= len(indexes):
                    row = analysis['area_bins'][indexes[state.row_index - 1]]
                    for field in ('begin', 'end', 'center', 'area', 'percentage', 'source_line'):
                        value = row.get(field)
                        layout.label(text=f'{field}: {value if value is not None else "not recorded"}')
            elif role == 'nbo':
                layout.label(text=f"Orbitals {len(saved.get('orbitals', []))} | E(2) {len(saved.get('interactions', []))}")
                layout.label(text=f"Applied order: {saved.get('orbital_sort', 'source')} / {saved.get('interaction_sort', 'source')}")
                orbitals, interactions = saved.get('orbitals', []), saved.get('interactions', [])
                if orbitals and state.row_index <= len(orbitals):
                    row = analysis['orbitals'][orbitals[state.row_index - 1]]
                    layout.label(text=f"Orbital {row['number']} {row['type']} | occupancy {row['occupancy']:.6g}")
                    _draw_source_record(layout, row)
                if interactions and state.row_index <= len(interactions):
                    row = analysis['interactions'][interactions[state.row_index - 1]]
                    layout.label(text=f"{row['donor']} → {row['acceptor']} | E(2) {row['e2_kcal_mol']:.6g} kcal/mol")
                    _draw_source_record(layout, row)
            else:
                if saved.get('type_mismatch'):
                    layout.label(text='Selected type belongs to another display layer', icon='INFO')
                layout.label(text=f"Matching records: {len(saved.get('indexes', []))}")
                indexes = saved.get('indexes', [])
                if indexes and state.row_index <= len(indexes):
                    key = 'pairs' if role == 'ets_nocv' else 'extrema' if role.startswith('esp_') else 'critical_points'
                    row = analysis[key][indexes[state.row_index - 1]]
                    if role.startswith('aim_'):
                        from ..result_filters import point_label
                        layout.label(text=point_label(analysis, row, saved.get('value_key')))
                    for field in ('serial', 'kind', 'type', 'value', 'pair', 'spin', 'pair_energy',
                                  'positive_eigenvalue', 'negative_eigenvalue', 'source_line'):
                        if field in row:
                            layout.label(text=f'{field}: {row[field]}')


def _draw_source_record(layout, row):
    if 'source_line' in row:
        layout.label(text=f"Source line {row['source_line']}")
    if 'raw_line' in row:
        raw = row['raw_line']
        for offset in range(0, len(raw), 72):
            layout.label(text=raw[offset:offset + 72])


def _draw_range(layout, state, prefix, label):
    layout.label(text=label)
    row = layout.row(align=True)
    row.prop(state, prefix + '_low_on', text='')
    row.prop(state, prefix + '_low', text='From')
    row.prop(state, prefix + '_high_on', text='')
    row.prop(state, prefix + '_high', text='To')
