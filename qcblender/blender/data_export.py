"""User initiated exports of scientific data to an explicit result directory."""
from pathlib import Path
import uuid
from functools import lru_cache, partial

import bpy
from bpy.props import EnumProperty, StringProperty

from .ui import AsyncOperation


def resolve_output_directory(context, override=''):
    from ..data_export import default_output_directory
    if override:
        path = Path(bpy.path.abspath(override))
        if not path.is_absolute():
            raise ValueError('Choose an absolute export directory')
        return path
    addon_id = __package__.rsplit('.', 1)[0]
    addon = context.preferences.addons.get(addon_id)
    preference = getattr(addon.preferences, 'data_output_directory', '') if addon else ''
    return default_output_directory(preference, bpy.data.filepath)


@lru_cache(maxsize=32)
def _enum_items(kinds):
    return [(kind, '当前视图参数摘要' if kind == 'SUMMARY' else kind,
             'Export view-summary.md and metadata.json' if kind == 'SUMMARY' else 'Export original scientific records')
            for kind in kinds]


def export_choices(self, context):
    from .source_browser import cached_metadata
    try:
        meta = cached_metadata(context.object)
        kinds = []
        if 'modes' in meta:
            kinds.append('IR')
        if meta.get('optimization', {}).get('status') == 'available':
            kinds.append('optimization')
        analysis = meta.get('analysis', {}).get('kind')
        if analysis == 'IRC':
            kinds.append('IRC')
        if analysis == 'IRC-Mayer':
            kinds.append('Mayer')
        if 'profile' in meta:
            kinds.append('profile')
        if analysis in ('IGMH', 'IRI'):
            kinds.append('paired')
        if analysis == 'ESP':
            kinds.append('ESP_AREA')
        if context.object is not None:
            from .source_browser import source_object
            if source_object(context.object).get('qc_dataset'):
                kinds.append('SUMMARY')
        return _enum_items(tuple(kinds))
    except (ValueError, OSError, KeyError, TypeError, AttributeError):
        return []


class QCBLENDER_OT_export_data(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.export_data'
    bl_label = 'Export Scientific Data'

    directory: StringProperty(name='Output directory', subtype='DIR_PATH', options={'SKIP_SAVE'})
    kind: EnumProperty(name='Data', items=export_choices)
    scope: EnumProperty(name='Rows', items=[('ALL', 'All source records', ''),
        ('FILTERED', 'Current filter', 'Paired field values or ESP area bins')], default='ALL')

    @classmethod
    def poll(cls, context):
        from .source_browser import source_object
        return context.object is not None and bool(source_object(context.object).get('qc_dataset'))

    def invoke(self, context, event):
        try:
            from .source_browser import refresh_source
            meta = refresh_source(context.object)
            if 'error' in meta:
                raise ValueError(meta['error'])
            self.directory = str(resolve_output_directory(context, self.directory))
            choices = export_choices(self, context)
            if not choices:
                raise ValueError('This Dataset has no supported export records')
            self.kind = choices[0][0]
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=560)

    def draw(self, context):
        self.layout.prop(self, 'directory')
        self.layout.prop(self, 'kind')
        if self.kind in ('paired', 'ESP_AREA'):
            self.layout.prop(self, 'scope')
        self.layout.label(text='Creates a unique result folder containing ' +
                               ('view-summary.md and metadata.json' if self.kind == 'SUMMARY' else 'CSV and metadata.json'))
        if self.kind == 'SUMMARY':
            self.layout.label(text='Captures stored node/material inputs; unresolved records are partial/unverified')
        if self.kind == 'paired':
            self.layout.label(text='Exports every matching valid voxel; Esc cancels while running')

    def begin(self, context):
        from .source_browser import read_metadata, source_object
        from .jobs import Job
        read_metadata(context.object)
        obj = source_object(context.object)
        path = Path(bpy.path.abspath(obj['qc_dataset'])).resolve(strict=True)
        if self.kind not in [item[0] for item in export_choices(self, context)]:
            raise ValueError('Select available scientific data to export')
        filters = {}
        scope = self.scope if self.kind in ('paired', 'ESP_AREA') else 'ALL'
        if scope == 'FILTERED':
            from .result_browser import _scatter_parameters, _bound
            state = obj.qc_result_browser
            if self.kind == 'paired':
                filters = _scatter_parameters(state)
            else:
                filters = {'center_min': _bound(state, 'value', 'low'),
                           'center_max': _bound(state, 'value', 'high'), 'mode': state.area_range_mode}
        self._output_directory = str(resolve_output_directory(context, self.directory))
        self._export_token = uuid.uuid4().hex
        parameters = {}
        if self.kind == 'SUMMARY':
            from .view_summary import capture_view_summary
            parameters['view_snapshot'] = capture_view_summary(context.object, context.scene.frame_current)
        job = Job('export_data', dataset=str(path), dataset_sha256=obj['qc_dataset_sha256'],
                  output_directory=self._output_directory, kind=self.kind, scope=scope,
                  filters=filters, export_token=self._export_token, **parameters)
        from ..data_export import cleanup_staging
        job.cleanup_after_exit = partial(cleanup_staging, self._output_directory, self._export_token)
        return job

    def accept(self, context, report):
        self.report({'INFO'}, 'Data exported: ' + report['directory'])

    def cleanup_export(self):
        if hasattr(self, '_export_token'):
            from ..data_export import cleanup_staging
            cleanup_staging(self._output_directory, self._export_token)

    def cancel(self, context):
        if hasattr(self, '_job'):
            super().cancel(context)
        else:
            self.cleanup_export()
