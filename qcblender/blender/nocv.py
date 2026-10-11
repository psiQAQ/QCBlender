"""Explicit ETS-NOCV pair Cube import into native signed isosurfaces."""
import hashlib
from pathlib import Path
from functools import lru_cache
import json

import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty

from .ui import AsyncOperation


@lru_cache(maxsize=32)
def _pair_items(pairs, spin):
    return [(str(number), str(number), 'Original pair number')
            for number in sorted({row['pair'] for row in json.loads(pairs) if row['spin'] == spin})]


@lru_cache(maxsize=16)
def _spin_items(pairs):
    found = {row['spin'] for row in json.loads(pairs)}
    return [(spin, spin, '') for spin in ('Total', 'Alpha', 'Beta') if spin in found]


def _pairs(context):
    from .source_browser import cached_metadata
    return json.dumps(cached_metadata(context.object).get('analysis', {}).get('pairs', []), sort_keys=True)


def spin_choices(self, context):
    return _spin_items(_pairs(context))


def pair_choices(self, context):
    return _pair_items(_pairs(context), self.spin)


def limit_nocv_pair(self, context):
    items = pair_choices(self, context)
    if not items:
        return
    numbers = [int(item[0]) for item in items]
    chosen = min(numbers, key=lambda number: (abs(number - self.pair_number), number))
    if self.pair_number != chosen:
        self.pair_number = chosen
    self.pair_choice = str(chosen)


def choose_pair(self, context):
    if self.pair_choice and self.pair_number != int(self.pair_choice):
        self.pair_number = int(self.pair_choice)


class QCBLENDER_OT_import_nocv(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_nocv_field'
    bl_label = 'Import NOCV Pair Cube'
    bl_options = {'REGISTER', 'UNDO'}

    cube_path: StringProperty(name='Signed pair Cube', subtype='FILE_PATH')
    pair_number: IntProperty(name='Pair number', min=1, default=1, update=limit_nocv_pair, options={'HIDDEN'})
    spin: EnumProperty(name='Spin', items=spin_choices, update=limit_nocv_pair)
    pair_choice: EnumProperty(name='Pair number', items=pair_choices, update=choose_pair)
    unit: StringProperty(name='Deformation density unit', default='electron/bohr^3')

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'nocv_field')

    def invoke(self, context, event):
        limit_nocv_pair(self, context)
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        for name in ('cube_path', 'spin', 'pair_choice', 'unit'):
            self.layout.prop(self, name)
        self.layout.label(text='Pair and spin must match one row in the active ETS-NOCV table')

    def begin(self, context):
        from .jobs import Job
        from .source_browser import read_metadata
        from .static_reference import capture_reference
        self._reference_snapshot = capture_reference(context.object)
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
        from .static_reference import validate_reference
        validate_reference(self._reference_snapshot)
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
