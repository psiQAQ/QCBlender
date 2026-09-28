"""NBO records from a selected Gaussian Log calculation."""
import hashlib
from pathlib import Path

import bpy
from bpy.props import IntProperty, StringProperty

from .ui import AsyncOperation


class QCBLENDER_OT_import_nbo(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_nbo'
    bl_label = 'Import Gaussian NBO Records'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name='Gaussian Log / Out', subtype='FILE_PATH')
    job_number: IntProperty(name='Gaussian job (1-based)', default=1, min=1)
    block_number: IntProperty(name='NBO block within job (1-based)', default=1, min=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None and 'qc_dataset' in context.object

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        for name in ('filepath', 'job_number', 'block_number'):
            self.layout.prop(self, name)
        self.layout.label(text='Active QC view supplies the reference geometry')

    def begin(self, context):
        from .jobs import Job
        source = Path(bpy.path.abspath(self.filepath)).resolve(strict=True)
        if source.suffix.lower() not in ('.log', '.out'):
            raise ValueError('Choose a Gaussian .log or .out file')
        self._reference = context.object
        self._reference_path = Path(bpy.path.abspath(self._reference['qc_dataset'])).resolve(strict=True)
        self._reference_digest = hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest()
        return Job('import_nbo', source=str(source), job_index=self.job_number - 1,
                   block_index=self.block_number - 1, reference_dataset=str(self._reference_path),
                   reference_sha256=self._reference_digest)

    def accept(self, context, report):
        from ..data import load_dataset
        from .views import bind

        if self._reference.name not in bpy.data.objects or hashlib.sha256((self._reference_path / 'manifest.json').read_bytes()).hexdigest() != self._reference_digest:
            raise ValueError('Reference calculation changed during NBO import')
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
        context.view_layer.objects.active = obj
        for selected in context.selected_objects:
            selected.select_set(False)
        obj.select_set(True)
        self.report({'INFO'}, 'NBO and E(2) records imported; no canonical MO mapping inferred')


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
            self.layout.label(text='来源未读取或关联断裂，请刷新来源', icon='INFO')
            self.layout.operator('qcblender.refresh_sources')
            return
        layout = self.layout
        layout.label(text=f"Job {result['job_number']}, NBO block {result['block_number']}")
        layout.label(text=f"{len(result['orbitals'])} orbitals; {len(result['interactions'])} E(2) records")
        layout.label(text='NBOs are not mapped to canonical MOs')
        layout.prop(obj, '["qc_nbo_index"]', text='NBO row (1-based)')
        index = int(obj['qc_nbo_index']) - 1
        if 0 <= index < len(result['orbitals']):
            orbital = result['orbitals'][index]
            box = layout.box()
            box.label(text=f"{orbital['number']} {orbital['type']} ({orbital['subindex']})")
            box.label(text=', '.join(f"{atom['symbol']}{atom['number']}" for atom in orbital['atoms']))
            box.label(text=f"Occupancy {orbital['occupancy']:.6g}")
            box.label(text=f"Energy {orbital['energy_hartree']:.6g} hartree")
            box.label(text=f"Source line {orbital['source_line']}")
        if result['interactions']:
            layout.prop(obj, '["qc_e2_index"]', text='E(2) row (1-based)')
            index = int(obj['qc_e2_index']) - 1
            if 0 <= index < len(result['interactions']):
                interaction = result['interactions'][index]
                box = layout.box()
                box.label(text=f"{interaction['donor']} → {interaction['acceptor']}")
                box.label(text=f"E(2) {interaction['e2_kcal_mol']:.6g} kcal/mol")
                box.label(text=f"ΔE {interaction['delta_e_hartree']:.6g} hartree")
                box.label(text=f"F(i,j) {interaction['fij_hartree']:.6g} hartree")
                box.label(text=f"Source line {interaction['source_line']}")
