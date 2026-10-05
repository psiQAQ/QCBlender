import json
import os
from pathlib import Path
import uuid
import hashlib

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

from ..project import archive_project, copy_dataset
from ..data import filesystem_path, load_dataset, unprefixed_path
from .ui import AsyncOperation
from .native_volume import check_field_cache, check_volume


def rebind_dataset(original, replacement):
    original = unprefixed_path(filesystem_path(original).resolve())
    replacement = unprefixed_path(filesystem_path(replacement).resolve(strict=True))
    data = load_dataset(replacement)
    checked = set()
    for scalar in data.metadata.get('fields', []):
        cache = check_field_cache(replacement, scalar)
        checked.add(cache.resolve())
    for volume in bpy.data.volumes:
        path = Path(bpy.path.abspath(volume.filepath)).resolve()
        if path.is_relative_to(original):
            cache = replacement / path.relative_to(original)
            if cache not in checked:
                check_volume(cache)
                checked.add(cache)
    digest = hashlib.sha256(filesystem_path(replacement / 'manifest.json').read_bytes()).hexdigest()
    for obj in bpy.data.objects:
        if 'qc_dataset' in obj and Path(bpy.path.abspath(obj['qc_dataset'])).resolve() == original:
            obj['qc_dataset'] = str(replacement)
            obj['qc_dataset_sha256'] = digest
            if 'qc_field' in obj:
                previous = json.loads(obj['qc_field'])
                match = next((f for f in data.metadata.get('fields', []) if f['array'] == previous['array']), None)
                if match:
                    obj['qc_field'] = json.dumps(match)
    for volume in bpy.data.volumes:
        path = Path(bpy.path.abspath(volume.filepath)).resolve()
        if path.is_relative_to(original):
            volume.grids.unload()
            volume.filepath = str(replacement / path.relative_to(original))


class QCBLENDER_OT_rebuild_cache(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.rebuild_cache'
    bl_label = 'Rebuild Volume Cache'

    @classmethod
    def poll(cls, context):
        return context.object is not None and 'qc_field' in context.object

    def begin(self, context):
        from .jobs import Job
        self._original = Path(bpy.path.abspath(context.object['qc_dataset'])).resolve()
        self._digest = hashlib.sha256((self._original / 'manifest.json').read_bytes()).hexdigest()
        return Job('rebuild_cache', dataset=str(self._original), dataset_sha256=self._digest)

    def accept(self, context, report):
        if hashlib.sha256((self._original / 'manifest.json').read_bytes()).hexdigest() != self._digest:
            raise ValueError('Dataset changed during recovery; result retained without attaching')
        rebind_dataset(self._original, self._job.directory / 'dataset')
        self.report({'INFO'}, 'Rebuilt display cache from the saved scientific arrays')


class QCBLENDER_OT_relocate_dataset(bpy.types.Operator, ImportHelper):
    bl_idname = 'qcblender.relocate_dataset'
    bl_label = 'Relocate Scientific Dataset'
    filename_ext = '.json'
    filter_glob: StringProperty(default='manifest.json', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.object is not None and 'qc_dataset_sha256' in context.object

    def execute(self, context):
        try:
            manifest = unprefixed_path(filesystem_path(self.filepath).resolve(strict=True))
            if manifest.name != 'manifest.json' or hashlib.sha256(filesystem_path(manifest).read_bytes()).hexdigest() != context.object['qc_dataset_sha256']:
                raise ValueError('Select the manifest of the identical dataset; scientific content must match')
            rebind_dataset(bpy.path.abspath(context.object['qc_dataset']), manifest.parent)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def save_project(filepath):
    target = unprefixed_path(filesystem_path(filepath).resolve())
    if target.suffix.lower() != '.blend':
        raise ValueError('Project file must have a .blend extension')
    data_root = target.with_suffix('.qcdata')
    filesystem_path(data_root).mkdir(parents=True, exist_ok=True)
    mapping = {}
    objects = [o for o in bpy.data.objects if 'qc_dataset' in o]
    for obj in objects:
        source = unprefixed_path(filesystem_path(bpy.path.abspath(obj['qc_dataset'])).resolve(strict=True))
        if source not in mapping:
            destination = copy_dataset(source, data_root)
            data = load_dataset(destination)
            for scalar in data.metadata.get('fields', []):
                check_field_cache(destination, scalar)
            mapping[source] = destination
    # Validate the final paths that live Volume datablocks will use, before publishing
    # the scene index or changing any live binding.
    for volume in bpy.data.volumes:
        original = Path(bpy.path.abspath(volume.filepath)).resolve()
        for source, destination in mapping.items():
            if original.is_relative_to(source):
                check_volume(destination / original.relative_to(source))
                break
    previous_objects, previous_volumes = {}, {}
    scene_manifest = {'format': 'qcblender.scene', 'schema': '0.1',
                      'datasets': sorted(set(path.relative_to(data_root).as_posix() for path in mapping.values()))}
    pending = data_root / (uuid.uuid4().hex + '.pending.json')
    index = data_root / 'manifest.json'
    previous_index = filesystem_path(index).read_bytes() if filesystem_path(index).exists() else None
    index_published = False
    filesystem_path(pending).write_text(json.dumps(scene_manifest, indent=2), encoding='utf-8')
    try:
        for obj in objects:
            previous_objects[obj] = obj['qc_dataset']
            original = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
            obj['qc_dataset'] = '//' + mapping[original].relative_to(target.parent).as_posix()
        for volume in bpy.data.volumes:
            original = Path(bpy.path.abspath(volume.filepath)).resolve()
            for source, destination in mapping.items():
                if original.is_relative_to(source):
                    previous_volumes[volume] = volume.filepath
                    cache = destination / original.relative_to(source)
                    volume.filepath = bpy.path.relpath(str(cache), start=None if bpy.data.filepath else str(target.parent))
                    break
        os.replace(filesystem_path(pending), filesystem_path(index))
        index_published = True
        result = bpy.ops.wm.save_as_mainfile(filepath=str(target), check_existing=False)
        if result != {'FINISHED'}:
            raise RuntimeError('Blender did not save the project')
        for volume in previous_volumes:
            volume.grids.unload()
            volume.update_tag()
    except Exception:
        for obj, old in previous_objects.items():
            obj['qc_dataset'] = old
        for volume, old in previous_volumes.items():
            volume.filepath = old
        if index_published:
            if previous_index is None:
                filesystem_path(index).unlink()
            else:
                filesystem_path(pending).write_bytes(previous_index)
                os.replace(filesystem_path(pending), filesystem_path(index))
        raise
    finally:
        filesystem_path(pending).unlink(missing_ok=True)
    return target


class QCBLENDER_OT_save_project(bpy.types.Operator, ExportHelper):
    bl_idname = 'qcblender.save_project'
    bl_label = 'Save Portable QC Project'
    filename_ext = '.blend'
    filter_glob: StringProperty(default='*.blend', options={'HIDDEN'})

    def execute(self, context):
        try:
            save_project(self.filepath)
        except (ValueError, OSError, RuntimeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Saved .blend and matching .qcdata directory')
        return {'FINISHED'}


class QCBLENDER_OT_archive_project(bpy.types.Operator, ExportHelper):
    bl_idname = 'qcblender.archive_project'
    bl_label = 'Package QC Project'
    filename_ext = '.zip'
    filter_glob: StringProperty(default='*.zip', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def execute(self, context):
        try:
            archive_project(bpy.data.filepath, self.filepath)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Packaged the saved .blend and scientific data')
        return {'FINISHED'}
