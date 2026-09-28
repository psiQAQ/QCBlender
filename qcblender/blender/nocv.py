"""Explicit ETS-NOCV pair Cube import into native signed isosurfaces."""
import hashlib
from pathlib import Path

import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty

from .ui import AsyncOperation


class QCBLENDER_OT_import_nocv(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_nocv_field'
    bl_label = 'Import NOCV Pair Cube'
    bl_options = {'REGISTER', 'UNDO'}

    cube_path: StringProperty(name='Signed pair Cube', subtype='FILE_PATH')
    pair_number: IntProperty(name='Pair number', min=1, default=1)
    spin: EnumProperty(name='Spin', items=[('Total', 'Total', ''), ('Alpha', 'Alpha', ''), ('Beta', 'Beta', '')])
    unit: StringProperty(name='Deformation density unit', default='electron/bohr^3')

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_analysis_role') == 'ets_nocv'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        for name in ('cube_path', 'pair_number', 'spin', 'unit'):
            self.layout.prop(self, name)
        self.layout.label(text='Pair and spin must match one row in the active ETS-NOCV table')

    def begin(self, context):
        from .jobs import Job
        from .source_browser import read_metadata
        source = Path(bpy.path.abspath(self.cube_path)).resolve(strict=True)
        if source.suffix.lower() not in ('.cube', '.cub'):
            raise ValueError('Choose one Cube field')
        table = context.object
        meta = read_metadata(table)
        if (table.get('qc_analysis_role') != 'ets_nocv'
                or meta.get('analysis', {}).get('kind') != 'ETS-NOCV'
                or table.get('qc_source_sha256') != meta.get('source', {}).get('sha256')
                or table.parent is None
                or meta['analysis'].get('reference_source') != table.parent.get('qc_source_sha256')):
            raise ValueError('ETS-NOCV table identity is invalid')
        self._table_name = table.name
        self._table_pointer = table.as_pointer()
        self._parent_pointer = table.parent.as_pointer() if table.parent else None
        self._parent_binding = (table.parent.get('qc_dataset'),
                                table.parent.get('qc_dataset_sha256'),
                                table.parent.get('qc_source_sha256'))
        self._binding = (table.get('qc_dataset'), table.get('qc_dataset_sha256'),
                         table.get('qc_source_sha256'), table.get('qc_analysis_role'))
        self._directory = Path(bpy.path.abspath(table['qc_dataset'])).resolve(strict=True)
        self._digest = hashlib.sha256((self._directory / 'manifest.json').read_bytes()).hexdigest()
        if self._digest != table.get('qc_dataset_sha256'):
            raise ValueError('ETS-NOCV table changed after binding')
        return Job('import_nocv', source=str(source), table_dataset=str(self._directory),
                   table_sha256=self._digest, pair_number=self.pair_number,
                   spin=self.spin, unit=self.unit)

    def accept(self, context, report):
        from .source_browser import read_metadata
        from .views import field_view
        table = bpy.data.objects.get(self._table_name)
        if (table is None or table.as_pointer() != self._table_pointer
                or (table.parent.as_pointer() if table.parent else None) != self._parent_pointer
                or (table.parent.get('qc_dataset'), table.parent.get('qc_dataset_sha256'),
                    table.parent.get('qc_source_sha256')) != self._parent_binding
                or (table.get('qc_dataset'), table.get('qc_dataset_sha256'),
                    table.get('qc_source_sha256'), table.get('qc_analysis_role')) != self._binding
                or Path(bpy.path.abspath(table['qc_dataset'])).resolve(strict=True) != self._directory
                or hashlib.sha256((self._directory / 'manifest.json').read_bytes()).hexdigest() != self._digest):
            raise ValueError('ETS-NOCV table changed during Cube import')
        meta = read_metadata(table)
        if (meta.get('analysis', {}).get('kind') != 'ETS-NOCV'
                or meta.get('source', {}).get('sha256') != table.get('qc_source_sha256')
                or meta['analysis'].get('reference_source') != table.parent.get('qc_source_sha256')):
            raise ValueError('ETS-NOCV table identity changed during Cube import')
        directory = self._job.directory / 'dataset'
        obj = field_view(directory, table.parent)
        obj['qc_analysis_role'] = 'nocv_field'
        obj['qc_ets_table_source'] = table['qc_source_sha256']
        obj['qc_ets_table_dataset_sha256'] = self._digest
        self.report({'INFO'}, 'Signed deformation density imported for the selected ETS-NOCV pair')
