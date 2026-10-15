"""User assigned roles for externally calculated paired Cube fields."""
from ..i18n import error_text, iface, ui_layout
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
        ('unknown', 'Undeclared / unknown', 'Component identity is unverified'),
        ('inter', 'inter', 'User declares the interfragment component'),
        ('intra', 'intra', 'User declares the intrafragment component'),
        ('total', 'total', 'User declares the total component')], default='unknown')
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
            ui_layout(self.layout).prop(self, name)
        if self.method == 'IRI':
            ui_layout(self.layout).prop(self, 'iri_exponent')
            ui_layout(self.layout).label(text='Typical IRI: |grad rho| / rho^1.1; declare the exponent used')
        else:
            ui_layout(self.layout).label(text='Typical IGMH delta-g: electron/bohr^4')
            ui_layout(self.layout).prop(self, 'igmh_component')
            ui_layout(self.layout).prop(self, 'igmh_fragments')
            ui_layout(self.layout).prop(self, 'igmh_declaration_source')
            ui_layout(self.layout).label(text='Source Cube atom order, 1-based integers, e.g. [[1,2,3],[4,5,6]]; fragments are optional')
            ui_layout(self.layout).label(text='Component and fragments are user-assigned (user_assigned)')
        ui_layout(self.layout).label(text='Typical sign(lambda2)rho: electron/bohr^3; Cube units are not declared')
        for name in ('color_minimum', 'color_maximum'):
            ui_layout(self.layout).prop(self, name)
        ui_layout(self.layout).label(text='Active QC view supplies the calculation and geometry association')

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
                raise ValueError('Fragment members require a JSON list of lists, e.g. [[1,2,3],[4,5,6]]') from error
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
        from .native_volume import check_field_cache

        self._reference = validate_reference(self._reference_snapshot)

        directory = self._job.directory / 'dataset'
        data = load_dataset(directory)
        association = compare_sources(load_dataset(self._reference_path), data)
        for index in range(2):
            check_field_cache(directory, data.metadata['fields'][index])
        parent = self._reference
        geometry = field_view(directory, parent, 0)
        color = field_view(directory, parent, 1)
        color.hide_set(True)
        color.hide_render = True
        geometry['qc_analysis'] = json.dumps(dict(data.metadata['analysis'], reference=association))
        add_mapping(geometry, color, self.color_minimum, self.color_maximum)
        paired_record(directory, data, parent)
        for warning in data.metadata['analysis'].get('igmh_declaration', {}).get('warnings', []):
            self.report({'WARNING'}, error_text(warning))
        self.report({'INFO'}, error_text('Imported paired external Cube fields and data records'))


class QCBLENDER_PT_igmh_declaration(bpy.types.Panel):
    bl_label = 'IGMH Source Declaration'
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
            ui_layout(self.layout).label(text='Refresh sources to read the IGMH declaration', icon='INFO')
            ui_layout(self.layout).operator('qcblender.refresh_sources')
            return
        declaration = igmh_declaration_record(analysis)
        component = declaration.get('component', 'unknown')
        ui_layout(self.layout).label(text=iface('Component: {value0}', value0=component if component != 'unknown' else 'Undeclared / unknown'))
        ui_layout(self.layout).label(text=iface('Declaration status: {value0}', value0=declaration.get('status', 'unverified')))
        ui_layout(self.layout).label(text=iface('Declaration interpretation: {value0}', value0=declaration.get('interpretation', 'unverified')))
        ui_layout(self.layout).label(text=iface('Declaration source: {value0}', value0=declaration.get('source') or 'Not provided'))
        fragments = declaration.get('fragments', [])
        if fragments:
            ui_layout(self.layout).label(text='Member indices: source Cube atom order, 1-based integers')
            for index, fragment in enumerate(fragments, 1):
                ui_layout(self.layout).label(text=iface('Fragment {value0}：{value1}', value0=index, value1=json.dumps(fragment)))
        else:
            ui_layout(self.layout).label(text='Fragment members: undeclared')
        for warning in declaration.get('warnings', []):
            ui_layout(self.layout).label(text=warning, icon='INFO')
