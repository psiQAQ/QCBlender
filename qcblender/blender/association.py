import json

import bpy
import numpy as np
from bpy.props import BoolProperty, FloatProperty
from mathutils import Matrix

from ..association import compare_sources
from ..data import load_dataset
from .geometry import current_geometry


def _association_record(obj):
    try:
        record = json.loads(obj.get('qc_association', '{}'))
    except (TypeError, ValueError) as error:
        raise ValueError('Geometry association is damaged; associate the views again') from error
    if (not isinstance(record, dict) or not isinstance(record.get('status'), str)
            or not isinstance(record.get('reference_source'), str)
            or not isinstance(record.get('moving_source'), str)):
        raise ValueError('Geometry association is damaged; associate the views again')
    try:
        rotation = np.asarray(record['rotation_rows'], dtype=float)
        translation = np.asarray(record['translation_angstrom'], dtype=float)
        mapping = record['atom_mapping']
        tolerance, error = record['tolerance_angstrom'], record['max_error_angstrom']
        valid = (rotation.shape == (3, 3) and translation.shape == (3,)
                 and np.isfinite(rotation).all() and np.isfinite(translation).all()
                 and np.allclose(rotation.T @ rotation, np.eye(3), rtol=0, atol=1e-8)
                 and np.isclose(np.linalg.det(rotation), 1., rtol=0, atol=1e-8)
                 and isinstance(mapping, list) and bool(mapping)
                 and all(type(number) is int for number in mapping)
                 and mapping == list(range(len(mapping)))
                 and type(tolerance) in (int, float) and np.isfinite(tolerance) and tolerance > 0
                 and type(error) in (int, float) and np.isfinite(error) and error >= 0)
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise ValueError('Geometry association transform is damaged; associate the views again')
    if record.get('version') == 2:
        for key in ('reference_geometry', 'moving_geometry'):
            geometry = record.get(key)
            if (not isinstance(geometry, dict) or not all(name in geometry for name in
                    ('source_sha256', 'dataset_sha256', 'kind', 'step', 'selected_job', 'coordinate_unit'))
                    or geometry['coordinate_unit'] != 'angstrom'
                    or geometry['kind'] not in ('source', 'optimization', 'irc')):
                raise ValueError('Geometry association identities are damaged; associate the views again')
            digests = (geometry['source_sha256'], geometry['dataset_sha256'])
            valid = (all(isinstance(value, str) and len(value) == 64
                         and all(character in '0123456789abcdef' for character in value) for value in digests)
                     and (geometry['selected_job'] is None or
                          (type(geometry['selected_job']) is int and geometry['selected_job'] >= 0))
                     and geometry['source_sha256'] == record[key.replace('_geometry', '_source')])
            if geometry['kind'] == 'source':
                valid = valid and geometry['step'] is None and 'step_record' not in geometry
            else:
                valid = (valid and type(geometry['step']) is int and geometry['step'] > 0
                         and isinstance(geometry.get('step_record'), dict) and bool(geometry['step_record']))
            if not valid:
                raise ValueError('Geometry association identities are damaged; associate the views again')
    return record


def require_current_association(moving, expected_reference):
    """Authorize an explicit association to this exact atom view and configuration."""
    if moving is None or expected_reference is None:
        raise ValueError('Geometry association needs both atom views; associate the views again')
    record = _association_record(moving)
    if (record.get('version') != 2 or record.get('status') != 'geometry_matched'
            or moving.qc_settings.association_reference != expected_reference):
        raise ValueError('Geometry association is not current; associate the views again')
    reference_positions, reference_geometry = current_geometry(expected_reference)
    moving_positions, moving_geometry = current_geometry(moving)
    if (record['reference_geometry'] != reference_geometry or record['moving_geometry'] != moving_geometry
            or record['reference_source'] != reference_geometry['source_sha256']
            or record['moving_source'] != moving_geometry['source_sha256']
            or record.get('atom_mapping') != list(range(len(moving_positions)))):
        raise ValueError('Geometry association identities changed; associate the views again')
    try:
        tolerance = float(record['tolerance_angstrom'])
        rotation = np.asarray(record['rotation_rows'], dtype=float)
        translation = np.asarray(record['translation_angstrom'], dtype=float)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('Geometry association transform is damaged; associate the views again') from error
    if (not np.isfinite(tolerance) or tolerance <= 0 or rotation.shape != (3, 3)
            or translation.shape != (3,) or not np.isfinite(rotation).all()
            or not np.isfinite(translation).all()
            or not np.allclose(rotation.T @ rotation, np.eye(3), rtol=0, atol=1e-8)
            or not np.isclose(np.linalg.det(rotation), 1., rtol=0, atol=1e-8)
            or reference_positions.shape != moving_positions.shape
            or np.linalg.norm(moving_positions @ rotation + translation - reference_positions,
                              axis=1).max() > tolerance + 1e-9):
        raise ValueError('Geometry association transform no longer matches; associate the views again')
    return record


def require_field_atom_view(field_view, data=None):
    """Validate the field's actual atom parent, including its current configuration."""
    from .source_browser import bound_field
    bound_field(field_view)
    parent = field_view.parent
    if parent is None or parent.get('qc_view_kind') != 'atoms':
        raise ValueError('This field needs its bound atom view for explicit geometry association')
    if data is None:
        data = load_dataset(bpy.path.abspath(field_view['qc_dataset']))
    atom_data = load_dataset(bpy.path.abspath(parent['qc_dataset']))
    positions, geometry = current_geometry(parent, atom_data)
    if (geometry['source_sha256'] != data.metadata['source']['sha256']
            or geometry['selected_job'] != data.metadata.get('selected_job')
            or not np.array_equal(atom_data.arrays['atomic_numbers'], data.arrays['atomic_numbers'])
            or positions.shape != data.arrays['positions'].shape
            or not np.allclose(positions, data.arrays['positions'], rtol=0, atol=1e-5)):
        raise ValueError('Field configuration differs from its current atom view')
    return parent


def prepare_association_invalidation(changed_obj, next_geometry):
    """Prepare every affected JSON before a step change writes any scene state."""
    _, previous_geometry = current_geometry(changed_obj)
    if previous_geometry == next_geometry:
        return ()
    prepared = []
    for obj in bpy.data.objects:
        if (obj != changed_obj and obj.qc_settings.association_reference != changed_obj) or 'qc_association' not in obj:
            continue
        record = _association_record(obj)
        record.update(status='stale', invalidation_reason='Scientific geometry step changed; associate the views again')
        prepared.append((obj, json.dumps(record)))
    return tuple(prepared)


def apply_association_invalidation(prepared):
    """Commit prevalidated strings after a successful geometry step change."""
    for obj, serialized in prepared:
        obj['qc_association'] = serialized


def association_summary(obj):
    """Describe stored verification state without reading scientific arrays."""
    try:
        record = _association_record(obj)
    except ValueError as error:
        return {'status': 'invalid', 'action': str(error)}
    if record.get('version') != 2 or obj.qc_settings.association_reference is None:
        return dict(record, status='unverified', action='Associate the views again')
    if record.get('status') != 'geometry_matched':
        return dict(record, action='Associate the views again')
    return record


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
            reference_data = load_dataset(bpy.path.abspath(reference['qc_dataset']))
            moving_data = load_dataset(bpy.path.abspath(moving['qc_dataset']))
            _, reference_geometry = current_geometry(reference, reference_data)
            _, moving_geometry = current_geometry(moving, moving_data)
            result = compare_sources(reference_data, moving_data, allow_rigid=self.allow_rigid,
                                     tolerance_angstrom=self.tolerance,
                                     reference_kind=reference_geometry['kind'], reference_step=reference_geometry['step'],
                                     moving_kind=moving_geometry['kind'], moving_step=moving_geometry['step'])
            result.update(reference_geometry=reference_geometry, moving_geometry=moving_geometry)
            serialized = json.dumps(result)
            transform = Matrix(result['rotation_rows']).transposed().to_4x4()
            transform.translation = result['translation_angstrom']
        except (ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        moving.matrix_world = reference.matrix_world @ transform
        moving['qc_association'] = serialized
        moving.qc_settings.association_reference = reference
        self.report({'INFO'}, 'Atom order and geometry matched; each source retains its own properties')
        return {'FINISHED'}
