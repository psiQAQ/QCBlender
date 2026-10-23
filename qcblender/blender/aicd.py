"""AICD native field view, bounded arrows and original-sample inspection."""
import hashlib
import json
import math
from pathlib import Path

import bpy
from bpy.props import BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, StringProperty
import numpy as np

from ..aicd import arrow_samples, field_direction, sample_record
from ..data import load_dataset
from ..i18n import error_text, iface, ui_layout
from .ui import AsyncOperation


def settings(obj):
    return json.loads(obj['qc_aicd_settings'])


def _part(root, obj, role):
    obj.parent = root
    obj['qc_aicd_part'] = role
    obj.hide_select = True
    return obj


def _arrows_mesh(positions, vectors, scale, radius):
    vertices, faces = [], []
    circle = np.linspace(0, 2*np.pi, 10, endpoint=False)
    for position, vector in zip(positions, vectors):
        length = np.linalg.norm(vector)*scale
        if length == 0:
            continue
        z = vector/np.linalg.norm(vector)
        helper = np.eye(3)[np.argmin(abs(z))]
        x = np.cross(helper, z)
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        r = min(radius, length*.08)
        start = len(vertices)
        for depth, width in ((0, r), (.72*length, r), (.72*length, 2.5*r)):
            vertices.extend(position+depth*z+width*(math.cos(a)*x+math.sin(a)*y) for a in circle)
        vertices.append(position+length*z)
        for i in range(10):
            j = (i+1) % 10
            faces.extend(((start+i, start+j, start+10+j, start+10+i),
                          (start+10+i, start+10+j, start+20+j, start+20+i),
                          (start+20+i, start+20+j, start+30)))
        faces.append(tuple(start+i for i in reversed(range(10))))
    mesh = bpy.data.meshes.new('QC AICD arrows')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return mesh


def _replace_mesh(obj, mesh):
    previous = obj.data
    for mat in previous.materials:
        mesh.materials.append(mat)
    obj.data = mesh
    if previous.users == 0:
        bpy.data.meshes.remove(previous)


def apply_settings(obj, data, config):
    from .surface_projection import _input
    from .node_identity import node_socket
    direction = field_direction(config['field'])
    if not math.isfinite(config['length_scale']) or config['length_scale'] <= 0:
        raise ValueError('AICD arrow length scale must be positive and finite')
    positions, vectors, ids = arrow_samples(data, config['isovalue'], direction, config['arrow_limit'])
    parts = {child.get('qc_aicd_part'): child for child in obj.children}
    if not {'surface', 'atoms', 'arrows', 'field_marker', 'label'} <= parts.keys():
        raise ValueError('AICD display parts are missing; recreate the view')
    mesh = _arrows_mesh(positions, vectors, config['length_scale'], .018)
    _input(parts['surface'], 'Isovalue', config['isovalue'])
    _input(parts['surface'], 'Negative Phase', False)
    _input(parts['surface'], 'Positive Opacity', config['opacity'])
    _replace_mesh(parts['arrows'], mesh)
    parts['arrows']['qc_aicd_grid_ids'] = ids.tolist()
    for role, color in [('surface', config['surface_color']), ('arrows', config['arrow_color'])]:
        if role == 'surface':
            from .graph import view_modifier
            from .node_identity import socket_name
            modifier = view_modifier(parts[role])
            item = next(s for s in modifier.node_group.interface.items_tree
                        if s.item_type == 'SOCKET' and s.in_out == 'INPUT'
                        and socket_name(s, modifier.node_group) == 'Positive Material')
            mat = modifier.get(item.identifier) or item.default_value
        else:
            mat = parts[role].data.materials[0]
        shader = next(n for n in mat.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
        node_socket(shader.inputs, 'Base Color').default_value = (*color, 1.)
    for role, key in [('surface', 'show_surface'), ('arrows', 'show_arrows'), ('atoms', 'show_atoms')]:
        parts[role].hide_viewport = parts[role].hide_render = not config[key]
    marker_position = data.arrays['positions'].min(axis=0)-np.array([.8, .8, 0.])
    _replace_mesh(parts['field_marker'], _arrows_mesh([marker_position], [direction], 1.2, .035))
    parts['label'].location = marker_position+np.array([0., -.4, .1])
    parts['label'].data.body = (iface('AICD {component} | Aniso {isovalue:g}',
        component=iface(data.metadata['analysis']['component']), isovalue=config['isovalue'])+'\n'+
        iface('Unit field: ({x:.3g}, {y:.3g}, {z:.3g})', x=direction[0], y=direction[1], z=direction[2]))
    obj['qc_aicd_settings'] = json.dumps({**config, 'field': direction.tolist()}, sort_keys=True)
    index = json.loads(obj.get('qc_aicd_point', '{"index":0}'))['index']
    obj['qc_aicd_point'] = json.dumps(sample_record(data, index, direction))
    obj['qc_aicd_arrow_count'] = len(ids)
    obj.update_tag()


def create_view(directory, data, reference, isovalue):
    from .views import atom_view, bind, field_view, material
    from .annotation_fonts import annotation_font
    arrow_samples(data, isovalue, (0, 0, 1), 0)
    root = bpy.data.objects.new('QC AICD '+data.metadata['analysis']['component'], bpy.data.meshes.new('QC AICD controls'))
    bpy.context.collection.objects.link(root)
    bind(root, directory, data)
    root['qc_view_kind'] = 'aicd'
    root['qc_analysis_role'] = 'aicd'
    root.matrix_world = reference.matrix_world.copy()
    _part(root, atom_view(directory), 'atoms')
    surface = _part(root, field_view(directory, root), 'surface')
    _part(root, surface.qc_settings.volume, 'volume')
    for role, color in [('arrows', (.9, .08, .025, 1.)), ('field_marker', (.1, .15, .8, 1.))]:
        mesh = bpy.data.meshes.new('QC AICD '+role)
        mesh.materials.append(material('QC AICD '+role, color))
        obj = bpy.data.objects.new('QC AICD '+role, mesh)
        bpy.context.collection.objects.link(obj)
        _part(root, obj, role)
    curve = bpy.data.curves.new('QC AICD field label', 'FONT')
    curve.size, curve.font = .8, annotation_font()
    curve.materials.append(material('QC AICD label', (.02, .02, .02, 1.)))
    label = bpy.data.objects.new('QC AICD field label', curve)
    bpy.context.collection.objects.link(label)
    _part(root, label, 'label')
    config = {'isovalue': isovalue, 'field': [0., 0., 1.], 'arrow_limit': 1000, 'length_scale': 3.,
              'show_surface': True, 'show_arrows': True, 'show_atoms': True, 'opacity': .45,
              'surface_color': [.9, .65, .08], 'arrow_color': [.9, .08, .025]}
    apply_settings(root, data, config)
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    return root


class QCBLENDER_OT_import_aicd(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.import_aicd'
    bl_label = 'Import AICD Tensors'
    bl_description = 'Verify a Gaussian CSGT source declaration against its input, log, tensor dump and selected static atoms, then import an independent AICD view'
    bl_options = {'REGISTER', 'UNDO'}

    source: StringProperty(name='AICD source JSON', subtype='FILE_PATH')
    isovalue: FloatProperty(name='Aniso isovalue (response a.u.)', default=0.)
    spacing: FloatProperty(name='AICD grid spacing (Å)', default=.25, min=.0001)
    padding: FloatProperty(name='AICD grid padding (Å)', default=2.5, min=0.)
    memory_mb: IntProperty(name='Memory budget (MiB)', default=512, min=32, max=16384)

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'aicd')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)

    def draw(self, context):
        layout = ui_layout(self.layout)
        for key in self.__annotations__:
            layout.prop(self, key)
        layout.label(text='Declare an isovalue explicitly; no value is inferred from other programs')
        layout.label(text='Source JSON binds input, log and dump hashes; pi/sigma requires orbital evidence')
        layout.label(text='Use the static molecule in the original generating orientation')

    def begin(self, context):
        from .jobs import Job
        from .static_reference import capture_reference
        from .geometry import current_geometry
        self._reference_snapshot = capture_reference(context.object)
        current_geometry(context.object)
        if not math.isfinite(self.isovalue) or self.isovalue <= 0:
            raise ValueError('Choose a positive AICD isovalue below the valid grid maximum')
        directory = Path(bpy.path.abspath(context.object['qc_dataset'])).resolve(strict=True)
        return Job('import_aicd', source=str(Path(bpy.path.abspath(self.source)).resolve(strict=True)),
                   isovalue=self.isovalue, spacing=self.spacing, padding=self.padding, memory_mb=self.memory_mb,
                   reference_dataset=str(directory), reference_sha256=hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest())

    def accept(self, context, report):
        from .static_reference import validate_reference
        from .geometry import current_geometry
        reference = validate_reference(self._reference_snapshot)
        current_geometry(reference)
        directory = self._job.directory/'dataset'
        data = load_dataset(directory)
        create_view(directory, data, reference, self.isovalue)


class QCBLENDER_OT_aicd_settings(bpy.types.Operator):
    bl_idname = 'qcblender.aicd_settings'
    bl_label = 'AICD Display'
    bl_description = 'Set Aniso surface and unit field response arrows without changing the original tensors'
    bl_options = {'REGISTER', 'UNDO'}

    isovalue: FloatProperty(name='Aniso isovalue (response a.u.)', default=0.)
    field: FloatVectorProperty(name='Field direction in generating coordinates', size=3, default=(0, 0, 1))
    arrow_limit: IntProperty(name='Maximum AICD arrows', default=1000, min=0, max=1000)
    length_scale: FloatProperty(name='Arrow scale (Å per response a.u.)', default=3., min=.0001)
    show_surface: BoolProperty(name='Show Aniso surface', default=True)
    show_arrows: BoolProperty(name='Show current response arrows', default=True)
    show_atoms: BoolProperty(name='Show reference atoms', default=True)
    opacity: FloatProperty(name='Aniso surface opacity', default=.45, min=0, max=1)
    surface_color: FloatVectorProperty(name='Aniso surface color', size=3, subtype='COLOR', default=(.9, .65, .08), min=0, max=1)
    arrow_color: FloatVectorProperty(name='Current arrow color', size=3, subtype='COLOR', default=(.9, .08, .025), min=0, max=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'aicd'

    def invoke(self, context, event):
        for key, value in settings(context.object).items():
            setattr(self, key, value)
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = ui_layout(self.layout)
        for key in self.__annotations__:
            layout.prop(self, key)
        layout.label(text='Field is normalized; arrow length is display-only')

    def execute(self, context):
        try:
            config = {key: list(getattr(self, key)) if key in ('field', 'surface_color', 'arrow_color') else getattr(self, key)
                      for key in self.__annotations__}
            apply_settings(context.object, load_dataset(bpy.path.abspath(context.object['qc_dataset'])), config)
        except (ValueError, OSError, KeyError, MemoryError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_aicd_point(bpy.types.Operator):
    bl_idname = 'qcblender.aicd_point'
    bl_label = 'Inspect AICD Sample'
    bl_description = 'Read original coordinates, quadrature weight, all tensor components, Aniso and the response to the current unit field'
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name='Original sample index (0-based)', default=0, min=0)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'aicd'

    def invoke(self, context, event):
        self.index = json.loads(context.object['qc_aicd_point'])['index']
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        try:
            obj = context.object
            obj['qc_aicd_point'] = json.dumps(sample_record(load_dataset(bpy.path.abspath(obj['qc_dataset'])), self.index, settings(obj)['field']))
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_aicd(bpy.types.Panel):
    bl_label = 'AICD Source and Response'
    bl_idname = 'QCBLENDER_PT_aicd'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'aicd'

    def draw(self, context):
        from .source_browser import cached_metadata
        obj, layout = context.object, ui_layout(self.layout)
        a = cached_metadata(obj).get('analysis', {})
        if not a:
            layout.operator('qcblender.refresh_sources')
            return
        layout.label(text=iface('Contribution: {value}', value=iface(a['component'])))
        layout.label(text=iface('Orbitals: {value}', value=', '.join(map(str, a['orbitals'])) or iface('all')))
        layout.label(text=a['program']+' / '+a['version'], translate=False)
        if a['component'] in ('pi', 'sigma'):
            layout.label(text='Orbital numbers verified; pi/sigma assignment is user-declared')
        layout.label(text=iface('Samples: {count} | Arrows: {arrows}', count=a['sample_count'], arrows=obj['qc_aicd_arrow_count']))
        layout.label(text='Units: coordinates Å; tensor and response a.u.')
        layout.operator('qcblender.aicd_settings')
        layout.operator('qcblender.aicd_point')
        p = json.loads(obj['qc_aicd_point'])
        layout.label(text=iface('Original sample {index} | Block {block}:{local_index}', **{k:p[k] for k in ('index', 'block', 'local_index')}))
        layout.label(text=iface('Position (Å)')+': '+', '.join(f'{v:.6g}' for v in p['position_angstrom']), translate=False)
        layout.label(text='J: '+', '.join(f'{v:.6g}' for v in p['current']), translate=False)
        layout.label(text=iface('Weight {weight:.6g} | Aniso {aniso:.6g}', weight=p['weight'], aniso=p['aniso']))
        layout.label(text='Tensor rows: current x/y/z; columns: field x/y/z')
        for row in p['tensor']:
            layout.label(text=', '.join(f'{v:.6g}' for v in row), translate=False)
        layout.operator('qcblender.export_data')
