import json

import bpy
from bpy.props import BoolProperty, FloatProperty
from mathutils import Matrix

from ..association import compare_sources
from ..data import load_dataset


class QCBLENDER_OT_associate(bpy.types.Operator):
    bl_idname = 'qcblender.associate_sources'
    bl_label = 'Associate Selected Geometry to Active'
    bl_options = {'REGISTER', 'UNDO'}
    allow_rigid: BoolProperty(name='Align rigid rotation/translation', default=False)
    tolerance: FloatProperty(name='Maximum atom deviation (angstrom)', default=.001, min=1e-6, max=.1)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and len(context.selected_objects) == 2
                and all(o.get('qc_view_kind') == 'atoms' for o in context.selected_objects))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        reference = context.object
        moving = next(o for o in context.selected_objects if o != reference)
        try:
            result = compare_sources(load_dataset(bpy.path.abspath(reference['qc_dataset'])),
                                     load_dataset(bpy.path.abspath(moving['qc_dataset'])),
                                     allow_rigid=self.allow_rigid, tolerance_angstrom=self.tolerance)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        transform = Matrix(result['rotation_rows']).transposed().to_4x4()
        transform.translation = result['translation_angstrom']
        moving.matrix_world = reference.matrix_world @ transform
        moving['qc_association'] = json.dumps(result)
        self.report({'INFO'}, 'Atom order and geometry matched; each source retains its own properties')
        return {'FINISHED'}
