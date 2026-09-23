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
        source = Path(bpy.path.abspath(self.cube_path)).resolve(strict=True)
        if source.suffix.lower() not in ('.cube', '.cub'):
            raise ValueError('Choose one Cube field')
        self._table = context.object
        self._directory = Path(bpy.path.abspath(self._table['qc_dataset'])).resolve(strict=True)
        self._digest = hashlib.sha256((self._directory / 'manifest.json').read_bytes()).hexdigest()
        return Job('import_nocv', source=str(source), table_dataset=str(self._directory),
                   table_sha256=self._digest, pair_number=self.pair_number,
                   spin=self.spin, unit=self.unit)

    def accept(self, context, report):
        from .views import field_view
        if self._table.name not in bpy.data.objects or hashlib.sha256((self._directory / 'manifest.json').read_bytes()).hexdigest() != self._digest:
            raise ValueError('ETS-NOCV table changed during Cube import')
        directory = self._job.directory / 'dataset'
        obj = field_view(directory, self._table.parent)
        obj['qc_analysis_role'] = 'nocv_field'
        obj['qc_ets_table_source'] = self._table['qc_source_sha256']
        self.report({'INFO'}, 'Signed deformation density imported for the selected ETS-NOCV pair')
