"""On-demand provenance inspection; drawing never reads scientific arrays."""
import hashlib
import json
import textwrap
from functools import lru_cache

import bpy
from bpy.props import EnumProperty, StringProperty

from ..data import SCHEMA, filesystem_path

_metadata = {}


def source_object(obj):
    if not obj.get('qc_dataset') and obj.get('qc_view_kind') in ('spectrum', 'dipole'):
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


def color_volume(obj):
    from .graph import view_modifier
    tree = view_modifier(obj).node_group
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
    links = sampler.inputs['Volume'].links
    if len(links) != 1 or links[0].from_node.bl_idname != 'GeometryNodeObjectInfo':
        raise ValueError('Color volume node link is missing')
    volume = links[0].from_node.inputs['Object'].default_value
    if volume is None:
        raise ValueError('Color volume object is missing')
    return volume


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
        return context.object is not None and bool(context.object.get('qc_view_kind') or context.object.get('qc_dataset'))

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
