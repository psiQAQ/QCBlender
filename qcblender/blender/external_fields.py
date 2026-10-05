"""User assigned roles for externally calculated paired Cube fields."""
import json
from pathlib import Path

import bpy
from bpy.props import EnumProperty, FloatProperty, StringProperty

from .ui import AsyncOperation


def paired_record(directory, data, parent):
    from .external_results import table_view
    return table_view(directory, data, parent, 'QC paired field data', 'paired')


class QCBLENDER_OT_import_paired_field(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_paired_field'
    bl_label = 'Import IGMH / IRI Cube Pair'
    bl_options = {'REGISTER', 'UNDO'}

    method: EnumProperty(name='Analysis', items=[('IGMH', 'IGMH', ''), ('IRI', 'IRI', '')])
    geometry_source: StringProperty(name='Geometry Cube', subtype='FILE_PATH')
    color_source: StringProperty(name='sign(lambda2)rho Cube', subtype='FILE_PATH')
    geometry_unit: StringProperty(name='Geometry value unit', default='')
    color_unit: StringProperty(name='Color value unit', default='')
    iri_exponent: FloatProperty(name='IRI density exponent a', default=0.0, min=0.0)
    igmh_component: EnumProperty(name='IGMH component', items=[
        ('unknown', '未声明 / unknown', '分量身份未核实'),
        ('inter', 'inter', '用户声明为片段间分量'),
        ('intra', 'intra', '用户声明为片段内分量'),
        ('total', 'total', '用户声明为总分量')], default='unknown')
    igmh_fragments: StringProperty(name='Fragment atoms (JSON)', default='')
    igmh_declaration_source: StringProperty(name='Declaration source (optional)', default='', maxlen=500)
    color_minimum: FloatProperty(name='Color minimum', default=-.05)
    color_maximum: FloatProperty(name='Color maximum', default=.05)

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'paired')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=550)

    def draw(self, context):
        for name in ('method', 'geometry_source', 'color_source', 'geometry_unit',
                     'color_unit'):
            self.layout.prop(self, name)
        if self.method == 'IRI':
            self.layout.prop(self, 'iri_exponent')
            self.layout.label(text='Typical IRI: |grad rho| / rho^1.1; declare the exponent used')
        else:
            self.layout.label(text='Typical IGMH delta-g: electron/bohr^4')
            self.layout.prop(self, 'igmh_component')
            self.layout.prop(self, 'igmh_fragments')
            self.layout.prop(self, 'igmh_declaration_source')
            self.layout.label(text='源 Cube 原子顺序，1基整数，例如 [[1,2,3],[4,5,6]]；片段可选')
            self.layout.label(text='分量与片段均为用户声明（user_assigned）')
        self.layout.label(text='Typical sign(lambda2)rho: electron/bohr^3; Cube units are not declared')
        for name in ('color_minimum', 'color_maximum'):
            self.layout.prop(self, name)
        self.layout.label(text='Active QC view supplies the calculation and geometry association')

    def begin(self, context):
        import hashlib
        from .jobs import Job
        from .static_reference import capture_reference
        self._reference_snapshot = capture_reference(context.object)
        if self.color_minimum >= self.color_maximum:
            raise ValueError('Color minimum must be below maximum')
        if any(not unit.strip() or unit.strip().lower() in ('unknown', 'dimensionless')
               for unit in (self.geometry_unit, self.color_unit)):
            raise ValueError('Declare both field units from the calculation; Cube headers do not provide them')
        if self.method == 'IRI' and self.iri_exponent <= 0:
            raise ValueError('Declare the IRI density exponent from the calculation')
        paths = [Path(bpy.path.abspath(p)).resolve(strict=True)
                 for p in (self.geometry_source, self.color_source)]
        fragments = None
        if self.method == 'IGMH' and self.igmh_fragments.strip():
            try:
                fragments = json.loads(self.igmh_fragments)
            except ValueError as error:
                raise ValueError('片段成员需要 JSON 二维列表，例如 [[1,2,3],[4,5,6]]') from error
        if paths[0] == paths[1]:
            raise ValueError('Choose two distinct Cube files for geometry and color')
        self._reference = context.object
        self._reference_path = Path(bpy.path.abspath(self._reference['qc_dataset'])).resolve(strict=True)
        self._reference_digest = hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest()
        return Job('import_pair', geometry_source=str(paths[0]), color_source=str(paths[1]),
                   method=self.method, geometry_unit=self.geometry_unit, color_unit=self.color_unit,
                   iri_exponent=self.iri_exponent if self.method == 'IRI' else None,
                   igmh_component=self.igmh_component if self.method == 'IGMH' else 'unknown',
                   igmh_fragments=fragments,
                   igmh_declaration_source=self.igmh_declaration_source if self.method == 'IGMH' else '',
                   reference_dataset=str(self._reference_path), reference_sha256=self._reference_digest)

    def accept(self, context, report):
        from ..association import compare_sources
        from ..data import load_dataset
        from .scalars import add_mapping
        from .views import field_view
        from .static_reference import validate_reference

        self._reference = validate_reference(self._reference_snapshot)

        directory = self._job.directory / 'dataset'
        data = load_dataset(directory)
        association = compare_sources(load_dataset(self._reference_path), data)
        parent = self._reference
        geometry = field_view(directory, parent, 0)
        color = field_view(directory, parent, 1)
        color.hide_set(True)
        color.hide_render = True
        geometry['qc_analysis'] = json.dumps(dict(data.metadata['analysis'], reference=association))
        add_mapping(geometry, color, self.color_minimum, self.color_maximum)
        paired_record(directory, data, parent)
        for warning in data.metadata['analysis'].get('igmh_declaration', {}).get('warnings', []):
            self.report({'WARNING'}, warning)
        self.report({'INFO'}, 'Imported paired external Cube fields and data records')


class QCBLENDER_PT_igmh_declaration(bpy.types.Panel):
    bl_label = 'IGMH 来源声明'
    bl_idname = 'QCBLENDER_PT_igmh_declaration'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'

    @classmethod
    def poll(cls, context):
        from .capabilities import record
        from .source_browser import cached_metadata
        return (context.object is not None and
                (cached_metadata(context.object).get('analysis', {}).get('kind') == 'IGMH'
                 or record(context.object, 'qc_analysis').get('kind') == 'IGMH'))

    def draw(self, context):
        from ..external_fields import igmh_declaration_record
        from .source_browser import cached_metadata
        analysis = cached_metadata(context.object).get('analysis')
        if not analysis:
            self.layout.label(text='请刷新来源以读取 IGMH 声明', icon='INFO')
            self.layout.operator('qcblender.refresh_sources')
            return
        declaration = igmh_declaration_record(analysis)
        component = declaration.get('component', 'unknown')
        self.layout.label(text='分量：' + (component if component != 'unknown' else '未声明 / unknown'))
        self.layout.label(text='声明状态：' + declaration.get('status', 'unverified'))
        self.layout.label(text='声明性质：' + declaration.get('interpretation', 'unverified'))
        self.layout.label(text='声明来源：' + (declaration.get('source') or '未填写'))
        fragments = declaration.get('fragments', [])
        if fragments:
            self.layout.label(text='成员索引：源 Cube 原子顺序，1基整数')
            for index, fragment in enumerate(fragments, 1):
                self.layout.label(text=f'片段 {index}：' + json.dumps(fragment))
        else:
            self.layout.label(text='片段成员：未声明')
        for warning in declaration.get('warnings', []):
            self.layout.label(text=warning, icon='INFO')
