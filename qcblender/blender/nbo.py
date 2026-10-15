"""NBO records from a selected Gaussian Log calculation."""
from ..i18n import error_text, iface, ui_layout
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import bpy
from bpy.props import IntProperty, StringProperty

from .ui import AsyncOperation
from .index_ranges import bounded_int, limit_property


@lru_cache(maxsize=16)
def inspected_jobs(summary):
    return json.loads(summary).get('jobs', []) if summary else []


def job_bounds(self, context):
    return 1, len(inspected_jobs(self.summary)) if self.summary else None


def block_bounds(self, context):
    jobs = inspected_jobs(self.summary)
    return 1, jobs[self.job_number - 1]['nbo_blocks'] if 1 <= self.job_number <= len(jobs) else None


def limit_job(self, context):
    limit_property(self, 'job_number', job_bounds, context)
    limit_property(self, 'block_number', block_bounds, context)


def clear_inspection(self, context):
    self.summary = ''


class QCBLENDER_OT_import_nbo(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_nbo'
    bl_label = 'Import Gaussian NBO Records'
    bl_description = 'Inspect a Gaussian Log or Out file, choose its calculation and NBO block, then import NBO and E(2) records against the active static QC reference'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name='Gaussian Log / Out', subtype='FILE_PATH', update=clear_inspection)
    summary: StringProperty(options={'HIDDEN'}, update=limit_job)
    job_number: IntProperty(name='Gaussian job (1-based)', default=1, min=1, update=limit_job)
    block_number: bounded_int('block_number', block_bounds, name='NBO block within job (1-based)', default=1, min=1)

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'nbo')

    def invoke(self, context, event):
        self._preview_gui = True
        limit_job(self, context)
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        ui_layout(self.layout).prop(self, 'filepath')
        if self.summary:
            ui_layout(self.layout).prop(self, 'job_number')
            ui_layout(self.layout).label(text=iface('Jobs 1-{value0}', value0=job_bounds(self, context)[1]))
            row = ui_layout(self.layout).row()
            count = block_bounds(self, context)[1]
            row.enabled = bool(count)
            row.prop(self, 'block_number')
            ui_layout(self.layout).label(text=iface('NBO blocks 1-{count}', count=count) if count else iface('This job has no NBO summary'))
        else:
            ui_layout(self.layout).label(text='Confirm to inspect available Gaussian jobs and NBO blocks')
        ui_layout(self.layout).label(text='Active QC view supplies the reference geometry')

    def begin(self, context):
        from .jobs import Job
        from .static_reference import capture_reference
        self._reference_snapshot = capture_reference(context.object)
        source = Path(bpy.path.abspath(self.filepath)).resolve(strict=True)
        if source.suffix.lower() not in ('.log', '.out'):
            raise ValueError('Choose a Gaussian .log or .out file')
        self._inspecting = getattr(self, '_preview_gui', False) and not self.summary
        if self._inspecting:
            return Job('inspect_source', source=str(source), include_nbo=True)
        if self.summary:
            limit_job(self, context)
            if not block_bounds(self, context)[1]:
                raise ValueError('Choose a Gaussian job containing an NBO summary')
        self._reference = context.object
        self._reference_path = Path(bpy.path.abspath(self._reference['qc_dataset'])).resolve(strict=True)
        self._reference_digest = hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest()
        return Job('import_nbo', source=str(source), job_index=self.job_number - 1,
                   block_index=self.block_number - 1, reference_dataset=str(self._reference_path),
                   reference_sha256=self._reference_digest,
                   source_sha256=json.loads(self.summary)['source']['sha256'] if self.summary else '')

    def accept(self, context, report):
        from ..data import load_dataset
        from .views import bind
        from .static_reference import validate_reference

        self._reference = validate_reference(self._reference_snapshot)
        if self._inspecting:
            bpy.ops.qcblender.import_nbo('INVOKE_DEFAULT', filepath=self.filepath, summary=json.dumps(report))
            return
        directory = self._job.directory / 'dataset'
        data = load_dataset(directory)
        mesh = bpy.data.meshes.new('QC NBO records')
        obj = bpy.data.objects.new('QC NBO: ' + data.metadata['source']['filename'], mesh)
        context.collection.objects.link(obj)
        obj.parent = self._reference
        bind(obj, directory, data)
        obj['qc_view_kind'] = 'nbo'
        obj['qc_nbo_index'] = 1
        obj['qc_e2_index'] = 1
        from .record_ranges import refresh_record_ranges
        refresh_record_ranges(obj, data.metadata)
        context.view_layer.objects.active = obj
        for selected in context.selected_objects:
            selected.select_set(False)
        obj.select_set(True)
        self.report({'INFO'}, error_text('NBO and E(2) records imported; no canonical MO mapping inferred'))


class QCBLENDER_PT_nbo(bpy.types.Panel):
    bl_label = 'NBO Records'
    bl_idname = 'QCBLENDER_PT_nbo'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'nbo'

    def draw(self, context):
        from .source_browser import cached_metadata
        obj = context.object
        result = cached_metadata(obj).get('analysis')
        if not result:
            ui_layout(self.layout).label(text='Source records are not loaded or the binding is broken; refresh sources', icon='INFO')
            ui_layout(self.layout).operator('qcblender.refresh_sources')
            return
        layout = ui_layout(self.layout)
        layout.label(text=iface('Job {value0}, NBO block {value1}', value0=result['job_number'], value1=result['block_number']))
        layout.label(text=iface('{value0} orbitals; {value1} E(2) records', value0=len(result['orbitals']), value1=len(result['interactions'])))
        layout.label(text='NBOs are not mapped to canonical MOs')
        row = layout.row()
        row.enabled = bool(result['orbitals'])
        row.prop(obj, '["qc_nbo_index"]', text='NBO row (1-based)')
        index = int(obj['qc_nbo_index']) - 1
        if 0 <= index < len(result['orbitals']):
            orbital = result['orbitals'][index]
            box = layout.box()
            box.label(text=f"{orbital['number']} {orbital['type']} ({orbital['subindex']})")
            box.label(text=', '.join(f"{atom['symbol']}{atom['number']}" for atom in orbital['atoms']))
            box.label(text=iface('Occupancy {value0:.6g}', value0=orbital['occupancy']))
            box.label(text=iface('Energy {value0:.6g} hartree', value0=orbital['energy_hartree']))
            box.label(text=iface('Source line {value0}', value0=orbital['source_line']))
        if result['interactions']:
            layout.prop(obj, '["qc_e2_index"]', text='E(2) row (1-based)')
            index = int(obj['qc_e2_index']) - 1
            if 0 <= index < len(result['interactions']):
                interaction = result['interactions'][index]
                box = layout.box()
                box.label(text=f"{interaction['donor']} → {interaction['acceptor']}")
                box.label(text=iface('E(2) {value0:.6g} kcal/mol', value0=interaction['e2_kcal_mol']))
                box.label(text=iface('ΔE {value0:.6g} hartree', value0=interaction['delta_e_hartree']))
                box.label(text=iface('F(i,j) {value0:.6g} hartree', value0=interaction['fij_hartree']))
                box.label(text=iface('Source line {value0}', value0=interaction['source_line']))
