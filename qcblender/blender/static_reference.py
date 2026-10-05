"""External reference guards for the bound object and its parent chain."""
import hashlib
from pathlib import Path

from ..static_reference import STATIC_REFERENCE_REASON, dynamic_reference


def reference_chain(obj):
    while obj is not None:
        yield obj
        obj = obj.parent


def cached_reference_reason(obj, cached_metadata):
    """Drawing and polling must use saved properties and already cached metadata."""
    for node in reference_chain(obj):
        if node.get('qc_dataset') and (dynamic_reference(cached_metadata(node))
                or node.get('qc_optimization_available') or node.get('qc_optimization_step')
                or node.get('qc_trajectory_frame') or node.get('qc_irc_step')):
            return STATIC_REFERENCE_REASON
    return ''


def binding(obj):
    return tuple(obj.get(key) for key in ('qc_dataset', 'qc_dataset_sha256', 'qc_source_sha256'))


def capture_reference(obj):
    """Read every bound ancestor before a worker starts or any objects are created."""
    import bpy
    from .source_browser import read_metadata
    if obj is None or not obj.get('qc_dataset'):
        raise ValueError('Dataset link is missing')
    nodes = []
    for node in reference_chain(obj):
        directory, digest = None, None
        if node.get('qc_dataset'):
            metadata = read_metadata(node)
            if metadata['source'].get('sha256') != node.get('qc_source_sha256'):
                raise ValueError('Reference source differs from the saved binding')
            if dynamic_reference(metadata) or cached_reference_reason(node, lambda unused: {}):
                raise ValueError(STATIC_REFERENCE_REASON)
            directory = Path(bpy.path.abspath(node['qc_dataset'])).resolve(strict=True)
            digest = hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest()
            if digest != node.get('qc_dataset_sha256'):
                raise ValueError('Reference calculation changed after binding')
        nodes.append((node.as_pointer(), binding(node), directory, digest, node))
    return tuple(nodes)


def validate_reference(snapshot):
    """Find the original RNA object by pointer, then recheck topology and datasets."""
    import bpy
    try:
        if snapshot[0][4].as_pointer() != snapshot[0][0]:
            raise ValueError('Reference object changed during import')
    except ReferenceError as error:
        raise ValueError('Reference object was removed during import') from error
    by_pointer = {obj.as_pointer(): obj for obj in bpy.data.objects}
    obj = by_pointer.get(snapshot[0][0])
    if obj is None:
        raise ValueError('Reference object changed during import')
    chain = list(reference_chain(obj))
    if len(chain) != len(snapshot):
        raise ValueError('Reference parent chain changed during import')
    for node, (pointer, saved_binding, directory, digest, original) in zip(chain, snapshot):
        try:
            if original.as_pointer() != pointer:
                raise ValueError('Reference parent changed during import')
        except ReferenceError as error:
            raise ValueError('Reference parent was removed during import') from error
        if node.as_pointer() != pointer or binding(node) != saved_binding:
            raise ValueError('Reference binding changed during import')
        if directory is not None:
            if (Path(bpy.path.abspath(node['qc_dataset'])).resolve(strict=True) != directory
                    or hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest() != digest):
                raise ValueError('Reference calculation changed during import')
    capture_reference(obj)
    return obj
