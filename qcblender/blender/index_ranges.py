"""Per-instance limits for numeric scientific record selectors."""
from bpy.props import IntProperty


def clamp(value, lower, upper):
    return max(lower, min(int(value), max(lower, int(upper))))


def limit_property(owner, name, bounds, context):
    lower, upper = bounds(owner, context)
    if upper is None:
        return
    value = clamp(getattr(owner, name), lower, upper)
    if getattr(owner, name) != value:
        setattr(owner, name, value)


def bounded_int(property_name, bounds, **kwargs):
    def update(owner, context):
        limit_property(owner, property_name, bounds, context)
    return IntProperty(update=update, **kwargs)


def object_count(context, key):
    obj = context.object
    return int(obj.get(key, 0)) if obj is not None else 0


def orbital_bounds(owner, context):
    from .source_browser import cached_metadata
    info = cached_metadata(context.object).get('orbitals', {})
    channel = 'norba' if owner.spin == 'alpha' or info.get('kind') == 'restricted' else 'norbb'
    count = info.get(channel)
    return 1, count


def limit_orbital(owner, context):
    limit_property(owner, 'orbital', orbital_bounds, context)


def step_bounds(owner, context):
    return 1, object_count(context, 'qc_optimization_count')


def frame_bounds(owner, context):
    return 1, object_count(context, 'qc_trajectory_count')


def atom_count(obj):
    from .source_browser import cached_metadata
    if obj is None or obj.get('qc_view_kind') != 'atoms':
        return 0
    meta = cached_metadata(obj)
    if meta.get('_atom_count') is not None:
        return int(meta['_atom_count'])
    return len(obj.data.vertices) if obj.type == 'MESH' else 0


def atom_bounds(owner, context):
    return 1, atom_count(context.object)


def plane_atom_bounds(owner, context):
    import bpy
    obj = bpy.data.objects.get(owner.configuration)
    return 1, atom_count(obj) if obj is not None else None


def limit_plane_atoms(owner, context):
    for name in ('atom_1', 'atom_2', 'atom_3'):
        limit_property(owner, name, plane_atom_bounds, context)


def collection_index(name, collection, **kwargs):
    def get(owner):
        return clamp(owner.get(name, 0), 0, len(getattr(owner, collection)) - 1)

    def set(owner, value):
        owner[name] = clamp(value, 0, len(getattr(owner, collection)) - 1)
    return IntProperty(default=0, min=0, get=get, set=set, **kwargs)
