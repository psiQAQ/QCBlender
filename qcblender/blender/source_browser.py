"""On-demand provenance inspection; drawing never reads scientific arrays."""
import hashlib
import json
import textwrap
from functools import lru_cache

import bpy
from bpy.props import EnumProperty, StringProperty

from ..data import SCHEMA, filesystem_path

_metadata = {}


def cached_metadata(obj):
    """Read the last explicitly refreshed metadata without filesystem access."""
    return _metadata.get(binding_key(obj), {}) if obj is not None else {}


@bpy.app.handlers.persistent
def refresh_loaded_sources(_unused=None):
    _metadata.clear()
    for obj in bpy.data.objects:
        source = source_object(obj)
        if source.get('qc_dataset') and binding_key(source) not in _metadata:
            refresh_source(source)


def source_object(obj):
    if not obj.get('qc_dataset') and (obj.get('qc_view_kind') in ('spectrum', 'dipole') or 'qc_annotation' in obj):
        if obj.parent and obj.parent.get('qc_view_kind') == 'atoms':
            return obj.parent
    return obj


def binding_key(obj):
    obj = source_object(obj)
    return (bpy.path.abspath(obj.get('qc_dataset', '')), obj.get('qc_dataset_sha256', ''))


def read_metadata(obj):
    path, expected = binding_key(obj)
    if not path:
        raise ValueError('Dataset link is missing')
    manifest = filesystem_path(path) / 'manifest.json'
    if manifest.stat().st_size > 16 * 1024**2:
        raise ValueError('Manifest exceeds size limit')
    raw = manifest.read_bytes()
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Dataset manifest differs from the saved binding')
    record = json.loads(raw)
    if not isinstance(record, dict) or record.get('format') != 'qcblender.project' or record.get('schema') != SCHEMA:
        raise ValueError('Unsupported QCBlender project schema')
    meta = record['metadata']
    if not isinstance(meta, dict) or not isinstance(meta.get('source'), dict):
        raise ValueError('Dataset source metadata is missing')
    for key in ('filename', 'sha256', 'parser'):
        value = meta['source'].get(key)
        if value is not None and not isinstance(value, str):
            raise ValueError('Invalid source metadata: ' + key)
    job = meta.get('selected_job')
    if job is not None and (type(job) is not int or job < 0):
        raise ValueError('Invalid selected calculation index')
    if not isinstance(meta.get('jobs', []), list) or not isinstance(meta.get('analysis', {}), dict):
        raise ValueError('Invalid calculation or analysis metadata')
    if any(not isinstance(job, dict) for job in meta.get('jobs', [])):
        raise ValueError('Invalid calculation record')
    analysis = meta.get('analysis', {})
    sources = analysis.get('sources', [])
    if not isinstance(sources, list) or any(not isinstance(source, dict) for source in sources):
        raise ValueError('Invalid external source records')
    for key in ('geometry_source', 'color_source'):
        if key in analysis and not isinstance(analysis[key], dict):
            raise ValueError('Invalid external source: ' + key)
    return meta


def refresh_source(obj):
    try:
        value = read_metadata(obj)
    except (OSError, ValueError, KeyError, TypeError) as error:
        value = {'error': str(error)}
    _metadata[binding_key(obj)] = value
    return value


def source_group(obj):
    obj = source_object(obj)
    meta = _metadata.get(binding_key(obj), {})
    source = meta.get('source', {})
    if obj.get('qc_field'):
        try:
            field = object_record(obj, 'qc_field')
        except (ValueError, TypeError):
            return (obj.name, 'invalid-field'), '关联无法读取'
        if field.get('role') == 'color':
            source = meta.get('analysis', {}).get('color_source', {})
            if not source:
                return (obj.name, 'unknown-color-source'), '着色来源未记录；请刷新'
    sha = source.get('sha256') or obj.get('qc_source_sha256', '')
    if not isinstance(sha, str):
        sha = ''
    job = meta.get('selected_job', obj.get('qc_source_job', -1))
    if type(job) is not int:
        job = -1
    name = source.get('filename', obj.get('qc_source_filename', '未记录'))
    # Unknown source identities stay separate, rather than merging by filename.
    identity = job if ('source' in meta or 'qc_source_job' in obj) else binding_key(obj)[0]
    key = (sha or obj.name, identity)
    label = f"{name} | {sha[:12] or '未记录'}"
    if job != -1:
        label += f' | Job {job+1}'
    if 'error' in meta:
        label += ' | 关联无法读取'
    return key, label


def bound_field(obj):
    """Read a scene-bound field's identity from its saved metadata, without arrays."""
    if obj.get('qc_view_kind') not in ('field', 'slice') or not obj.get('qc_dataset') or not obj.get('qc_field'):
        raise ValueError('Choose a bound scalar field view')
    volume = obj.qc_settings.volume
    if (volume is None or volume.get('qc_view_kind') != 'volume'
            or binding_key(volume) != binding_key(obj)
            or volume.get('qc_source_sha256') != obj.get('qc_source_sha256')):
        raise ValueError('Field volume differs from the selected view')
    field = object_record(obj, 'qc_field')
    if object_record(volume, 'qc_field') != field:
        raise ValueError('Field volume metadata differs from the selected view')
    meta = read_metadata(obj)
    if (field not in meta.get('fields', [])
            or obj.get('qc_source_sha256') != meta['source'].get('sha256')):
        raise ValueError('Field differs from the saved dataset identity')
    source = field_source(meta, field)
    digest = source.get('sha256') if isinstance(source, dict) else None
    if (not isinstance(digest, str) or len(digest) != 64
            or any(char not in '0123456789abcdefABCDEF' for char in digest)
            or not isinstance(source.get('filename'), str)):
        raise ValueError('Field-specific source identity is missing')
    return volume, field, meta, source


def color_mapping(obj):
    """Resolve the one QC scalar sampler, color group and legend on a saved view."""
    from .graph import geometry_output, view_modifier
    tree = view_modifier(obj).node_group
    if not tree.get('qc_color_mapping') or not obj.get('qc_color_source'):
        raise ValueError('View has no supported QC scalar mapping')
    colors = [n for n in tree.nodes if n.bl_idname == 'GeometryNodeGroup'
              and n.node_tree and n.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2']
    if len(colors) != 1:
        raise ValueError('Color mapping node is missing or ambiguous')
    links = colors[0].inputs['Value'].links
    if len(links) != 1:
        raise ValueError('Color sampling link is missing')
    sampler = links[0].from_node
    if sampler.bl_idname != 'GeometryNodeGroup' or not sampler.node_tree or sampler.node_tree.get('qc_asset_id') != 'qc.sample.v1':
        raise ValueError('Color sampling source is not a supported scalar sampler')
    if links[0].from_socket != sampler.outputs['Value'] or len(colors[0].inputs['Geometry'].links) != 1:
        raise ValueError('Color sampling or receiving geometry was customized')
    valid = colors[0].inputs['Valid'].links
    if len(valid) != 1 or valid[0].from_node != sampler or valid[0].from_socket != sampler.outputs['Valid']:
        raise ValueError('Color validity link is not the supported scalar sampler')
    links = sampler.inputs['Volume'].links
    if len(links) != 1 or links[0].from_node.bl_idname != 'GeometryNodeObjectInfo' or links[0].from_socket != links[0].from_node.outputs['Geometry']:
        raise ValueError('Color volume node link is missing')
    info = links[0].from_node
    if info.transform_space != 'RELATIVE' or info.inputs['Object'].default_value is None:
        raise ValueError('Color volume object is missing')
    position = sampler.inputs['Position'].links
    if (len(position) != 1 or position[0].from_node.bl_idname != 'GeometryNodeInputPosition'
            or position[0].from_socket != position[0].from_node.outputs['Position']):
        raise ValueError('Color sampling position is unsupported')
    output = geometry_output(tree)
    geometry_links = colors[0].outputs['Geometry'].links
    joins = [link.to_node for link in geometry_links
             if link.to_node.bl_idname == 'GeometryNodeJoinGeometry']
    if len(geometry_links) != 1 or len(joins) != 1 or len(output.links) != 1:
        raise ValueError('Color geometry is not connected through the supported legend')
    clip_nodes = [n for n in tree.nodes if n.bl_idname == 'GeometryNodeGroup'
                  and n.node_tree and n.node_tree.get('qc_asset_id') == 'qc.clip.v1']
    if bool(tree.get('qc_clipping')) != bool(clip_nodes) or len(clip_nodes) > 1:
        raise ValueError('Clipping graph is missing or ambiguous')
    clip = clip_nodes[0] if clip_nodes else None
    if clip:
        controls = ('Plane Enabled', 'Plane Origin', 'Plane Normal', 'Box Enabled', 'Box Minimum', 'Box Maximum')
        if any(len(clip.inputs[name].links) != 1 or
               clip.inputs[name].links[0].from_node.type != 'GROUP_INPUT' or
               clip.inputs[name].links[0].from_socket != clip.inputs[name].links[0].from_node.outputs[name]
               for name in controls):
            raise ValueError('Clipping controls differ from the supported QC graph')
        if len(clip.inputs['Geometry'].links) != 1 or len(clip.outputs['Geometry'].links) != 1:
            raise ValueError('Clipping geometry is disconnected or ambiguous')
    join_output = joins[0].outputs['Geometry']
    displayed = output.links[0].from_socket
    color_input = colors[0].inputs['Geometry'].links[0].from_socket
    if displayed != join_output:
        if (clip is None or displayed != clip.outputs['Geometry']
                or clip.inputs['Geometry'].links[0].from_socket != join_output):
            raise ValueError('Color geometry has an unsupported node after the legend')
    elif clip and color_input != clip.outputs['Geometry']:
        raise ValueError('Clipping node is not in the supported color geometry chain')
    title_path = [('Curve Instances', 'GeometryNodeRealizeInstances'),
                  ('Geometry', 'GeometryNodeFillCurve'),
                  ('Mesh', 'GeometryNodeTransform'),
                  ('Geometry', 'GeometryNodeSetMaterial'),
                  ('Geometry', 'GeometryNodeJoinGeometry'),
                  ('Geometry', 'GeometryNodeTransform'),
                  ('Geometry', 'GeometryNodeSwitch'),
                  ('Output', 'GeometryNodeJoinGeometry')]
    titles = []
    for title in tree.nodes:
        if title.bl_idname != 'GeometryNodeStringToCurves' or title.label != 'QC Legend Title' or title.inputs['String'].links:
            continue
        node = title
        for output_name, next_type in title_path:
            links = node.outputs[output_name].links
            if len(links) != 1 or links[0].to_node.bl_idname != next_type:
                break
            node = links[0].to_node
        else:
            if node == joins[0]:
                titles.append(title)
    if len(titles) != 1:
        raise ValueError('Color legend title is missing, customized or ambiguous')
    return info, titles[0]


def mapped_field(obj):
    """Validate the recorded field as well as the mapping graph before using it."""
    volume = color_mapping(obj)[0].inputs['Object'].default_value
    field = object_record(volume, 'qc_field')
    meta = read_metadata(volume)
    recorded = object_record(obj, 'qc_color_source')
    identity = {key: field.get(key) for key in ('array', 'quantity', 'unit', 'orbital', 'spin', 'source_number')}
    if (field not in meta.get('fields', [])
            or volume.get('qc_source_sha256') != meta['source'].get('sha256')
            or volume.get('qc_source_sha256') != recorded.get('source')
            or any(field.get(key) != recorded.get(key) for key in ('quantity', 'unit'))
            or recorded.get('field_dataset_sha256', volume.get('qc_dataset_sha256')) != volume.get('qc_dataset_sha256')
            or recorded.get('field') and recorded['field'] != identity
            or recorded.get('field_source') and recorded['field_source'] != field_source(meta, field)):
        raise ValueError('Existing color mapping differs from its saved binding')
    return volume, field, meta


def color_volume(obj):
    return mapped_field(obj)[0]


def object_record(obj, key):
    record = json.loads(obj[key])
    if not isinstance(record, dict):
        raise ValueError('Invalid object source record: ' + key)
    return record


def field_source(meta, field):
    if 'error' in meta:
        return meta
    role = field.get('role')
    if role in ('geometry', 'color'):
        return meta.get('analysis', {}).get(role + '_source', {'error': 'Field source role is not recorded'})
    return meta.get('source', meta)


def source_details(obj):
    meta = refresh_source(obj)
    if 'error' in meta:
        return [('Dataset', meta)]
    view_field = object_record(obj, 'qc_field') if obj.get('qc_field') else {}
    entries = [('Geometry / data source', dict(field_source(meta, view_field),
        calculation_status=meta.get('calculation_status'), selected_job=meta.get('selected_job'),
        coordinate_unit=meta.get('coordinate_unit')))]
    if 'qc_annotation' in obj:
        entries.append(('Scene annotation', object_record(obj, 'qc_annotation')))
        entries.append(('View association', {'association': 'parent atom view', 'object': source_object(obj).name}))
    if obj.get('qc_view_kind') in ('spectrum', 'dipole'):
        entries.append(('View association', {'association': 'parent atom view', 'object': source_object(obj).name}))
        if obj.get('qc_dipole_source'):
            entries.append(('Dipole', object_record(obj, 'qc_dipole_source')))
        if obj.get('qc_view_kind') == 'spectrum':
            entries.append(('Spectrum', {'frequency_display_scale': obj.get('qc_frequency_scale'),
                'intensity_unit': obj.get('qc_intensity_unit')}))
    selected = meta.get('selected_job')
    jobs = meta.get('jobs', [])
    if isinstance(selected, int) and 0 <= selected < len(jobs):
        entries.append(('Calculation', {k: jobs[selected].get(k) for k in
            ('id', 'route', 'status', 'line_start', 'line_end')}))
    if obj.get('qc_field'):
        field = object_record(obj, 'qc_field')
        entries.append(('Geometry field', {k: field.get(k) for k in ('quantity', 'unit', 'array', 'orbital', 'spin', 'source_number')}))
    if obj.get('qc_color_source'):
        color = object_record(obj, 'qc_color_source')
        entries.append(('Color binding', color))
        try:
            volume = color_volume(obj)
            field = object_record(volume, 'qc_field')
            if volume.get('qc_source_sha256') != color.get('source') or any(field.get(k) != color.get(k) for k in ('quantity', 'unit')):
                raise ValueError('Linked color field differs from the recorded source or quantity')
            color_meta = refresh_source(volume)
            if color.get('field_source') and color['field_source'] != field_source(color_meta, field):
                raise ValueError('Linked color field provenance differs from the recorded source')
            if color.get('field') and color['field'] != {key: field.get(key) for key in
                                                           ('array', 'quantity', 'unit', 'orbital', 'spin', 'source_number')}:
                raise ValueError('Linked color field identity differs from the recorded field')
            entries.append(('Color source', field_source(color_meta, field)))
            entries.append(('Color field', dict(selected_job=color_meta.get('selected_job'),
                **{k: field.get(k) for k in ('quantity', 'unit', 'array', 'orbital', 'spin', 'source_number')})))
        except (ValueError, KeyError, TypeError) as error:
            entries.append(('Color source', {'error': str(error)}))
    analysis = meta.get('analysis', {})
    if analysis:
        entries.append(('External association', {k: analysis.get(k) for k in
            ('kind', 'association', 'reference_source', 'method', 'surface_definition', 'surface_field',
             'extrema_unit', 'distribution_center_unit', 'area_unit', 'coordinate_unit', 'energy_unit')}))
        for key in ('geometry_source', 'color_source'):
            if key in analysis:
                entries.append((key, analysis[key]))
        for source in analysis.get('sources', []):
            entries.append(('External source', source))
    if obj.get('qc_optimization_record'):
        entries.append(('Optimization step', object_record(obj, 'qc_optimization_record')))
    if obj.get('qc_local_selection_record'):
        entries.append(('Fixed local display selection', object_record(obj, 'qc_local_selection_record')))
    if meta.get('profile'):
        profile = meta['profile']
        entries.append(('Profile source', profile['source_record']))
        entries.append(('Profile field', profile['field']))
        entries.append(('Profile sampling', {key: value for key, value in profile.items()
                                            if key not in ('source_record', 'field')}))
    if obj.get('qc_association'):
        entries.append(('Geometry association', object_record(obj, 'qc_association')))
    return entries


class QCBLENDER_OT_refresh_sources(bpy.types.Operator):
    bl_idname = 'qcblender.refresh_sources'
    bl_label = 'Refresh Sources'

    def execute(self, context):
        _metadata.clear()
        for obj in context.scene.objects:
            if source_object(obj).get('qc_dataset') and binding_key(obj) not in _metadata:
                refresh_source(obj)
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


@lru_cache(maxsize=16)
def detail_choices(details):
    return [(str(i), f'{i+1}. {title}', title)
            for i, (title, _) in enumerate(json.loads(details) if details else [])]


def source_detail_choices(self, context):
    return detail_choices(self.details)


class QCBLENDER_OT_source_details(bpy.types.Operator):
    bl_idname = 'qcblender.source_details'
    bl_label = 'Source Details'
    details: StringProperty(options={'HIDDEN'})
    section: EnumProperty(name='Source record', items=source_detail_choices)

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_view_kind') or context.object.get('qc_dataset') or context.object.get('qc_annotation'))

    def invoke(self, context, event):
        try:
            self.details = json.dumps(source_details(context.object), ensure_ascii=False)
            self.section = '0'
        except (ValueError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=740)

    def draw(self, context):
        self.layout.prop(self, 'section')
        title, record = json.loads(self.details)[int(self.section)]
        box = self.layout.box()
        box.label(text=title)
        for key, value in record.items():
            if key == 'selected_job' and isinstance(value, int):
                key, value = 'calculation_number', value + 1
            if value is None or value == '':
                value = '未记录'
            for line in textwrap.wrap(f'{key}: {value}', width=100):
                box.label(text=line)

    def execute(self, context):
        return {'FINISHED'}
