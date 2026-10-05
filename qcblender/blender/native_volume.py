"""Validate display caches with Blender before changing scene or project bindings."""
import os
from pathlib import Path

import bpy

from ..data import resolve_asset, volume_cache


REQUIRED_GRIDS = frozenset(('qc_value', 'qc_negative', 'qc_valid'))


def check_field_cache(directory, scalar):
    """Keep asset containment and checksum checks, and include native read failures."""
    relative = Path(scalar.get('vdb', 'field.vdb'))
    candidate = Path(directory).resolve() / relative
    try:
        cache = resolve_asset(directory, str(relative))
    except OSError as error:
        # Missing/denied caches still receive a native diagnostic, only inside the
        # dataset boundary. Unsafe references retain the storage validation error.
        if not relative.is_absolute() and not relative.drive and '..' not in relative.parts:
            if candidate.parent.resolve().is_relative_to(Path(directory).resolve()):
                check_volume(candidate)
        raise ValueError(f'Volume cache "{candidate}": {error}') from error
    check_volume(cache)
    try:
        return volume_cache(directory, scalar)
    except (OSError, ValueError) as error:
        raise ValueError(f'Volume cache "{cache}": {error}') from error


def check_volume(path):
    """Read required grids using an unlinked Volume and release it on every outcome."""
    volume = bpy.data.volumes.new('QC cache readability check')
    try:
        volume.filepath = str(path)
        try:
            loaded = volume.grids.load()
        except (RuntimeError, OSError) as error:
            raise ValueError(_message(path, str(error), shorter_location=True)) from error
        reason = volume.grids.error_message
        if not loaded or reason:
            raise ValueError(_message(path, reason or 'Blender grids.load() returned False', shorter_location=True))
        names = {grid.name for grid in volume.grids}
        missing = REQUIRED_GRIDS - names
        if missing:
            raise ValueError(_message(path, 'Missing required VDB grids: ' + ', '.join(sorted(missing))))
        return names
    finally:
        bpy.data.volumes.remove(volume)


def _message(path, reason, shorter_location=False):
    message = f'Blender cannot read volume cache "{path}": {reason}'
    if shorter_location and os.name == 'nt':
        message += '. If the file exists, try a shorter project location and retry'
    return message
