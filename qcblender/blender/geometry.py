"""Read a bound atom view's real calculation geometry on explicit operations."""
import bpy

from ..data import load_dataset
from ..geometry import scientific_geometry
from .source_browser import read_metadata


def current_geometry(obj, data=None):
    """Return (positions in source angstrom, provenance); never evaluated geometry."""
    if obj is None or obj.type != 'MESH' or obj.get('qc_view_kind') != 'atoms' or obj.mode != 'OBJECT':
        raise ValueError('Select a QC atom view in Object mode')
    metadata = read_metadata(obj)
    if data is None:
        data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
    if (data.metadata != metadata or obj.get('qc_source_sha256') != metadata['source']['sha256']
            or obj.get('qc_source_job', -1) != metadata.get('selected_job', -1)):
        raise ValueError('Atom view source identity differs from its Dataset')
    numbers = data.arrays['atomic_numbers'].tolist()
    if len(obj.data.vertices) != len(numbers):
        raise ValueError('Atom mesh no longer matches the source calculation')
    for name, expected in (('qc_atom_id', list(range(len(numbers)))), ('qc_atomic_number', numbers)):
        attr = obj.data.attributes.get(name)
        if (attr is None or attr.domain != 'POINT' or attr.data_type != 'INT'
                or [value.value for value in attr.data] != expected):
            raise ValueError('Atom identities or ordering changed: ' + name)
    optimization = obj.get('qc_optimization_step')
    irc = bool(obj.get('qc_irc'))
    if optimization is not None and irc:
        raise ValueError('Atom view has conflicting optimization and IRC identities')
    kind = 'optimization' if optimization is not None else 'irc' if irc else 'source'
    step = optimization if kind == 'optimization' else obj.get('qc_irc_step') if irc else None
    positions, record = scientific_geometry(data, kind, step)
    record['dataset_sha256'] = obj['qc_dataset_sha256']
    return positions, record
