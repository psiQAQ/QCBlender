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
        if paths[0] == paths[1]:
            raise ValueError('Choose two distinct Cube files for geometry and color')
        self._reference = context.object
        self._reference_path = Path(bpy.path.abspath(self._reference['qc_dataset'])).resolve(strict=True)
        self._reference_digest = hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest()
        return Job('import_pair', geometry_source=str(paths[0]), color_source=str(paths[1]),
                   method=self.method, geometry_unit=self.geometry_unit, color_unit=self.color_unit,
                   iri_exponent=self.iri_exponent if self.method == 'IRI' else None,
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
        self.report({'INFO'}, 'Imported paired external Cube fields and data records')
