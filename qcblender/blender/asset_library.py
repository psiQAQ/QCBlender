"""Register the shipped node library and conservatively tidy legacy asset marks."""

import json
from pathlib import Path

import bpy

from ..asset_catalog import ASSETS


LIBRARY_NAME = 'QCBlender Nodes'
LIBRARY_DIR = Path(__file__).resolve().parents[1] / 'assets'
LIBRARY_FILE = LIBRARY_DIR / 'nodes.blend'

_LEGACY_DESCRIPTIONS = {
    'qc.isosurface.v3': 'Signed QC scalar isosurfaces with validity mask; input coordinates in angstrom',
    'qc.volume_fog.v1': 'QC volume display; optical transfer is controlled by the supplied material',
}


def register():
    if not LIBRARY_FILE.is_file():
        raise FileNotFoundError(f'QC node asset library is missing: {LIBRARY_FILE}')
    libraries = bpy.context.preferences.filepaths.asset_libraries
    if any(Path(item.path).resolve() == LIBRARY_DIR.resolve() for item in libraries):
        return
    name = LIBRARY_NAME
    if any(item.name == name for item in libraries):
        name += ' (extension)'
    libraries.new(name=name, directory=str(LIBRARY_DIR))


def unregister():
    libraries = bpy.context.preferences.filepaths.asset_libraries
    for item in tuple(libraries):
        if item.name in (LIBRARY_NAME, LIBRARY_NAME + ' (extension)') and Path(item.path).resolve() == LIBRARY_DIR.resolve():
            libraries.remove(item)


class _Unverifiable(Exception):
    pass


def _value(value, seen):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bpy.types.NodeTree):
        if value.get('qc_asset_id') not in ASSETS:
            raise _Unverifiable('unknown nested node group')
        return _group_signature(value, seen)
    if hasattr(value, 'bl_rna'):
        raise _Unverifiable(f'unsupported pointer: {value.bl_rna.identifier}')
    try:
        return tuple(_value(part, seen) for part in value)
    except TypeError as error:
        raise _Unverifiable(f'unsupported property: {type(value).__name__}') from error


def _properties(value, seen, excluded=()):
    result = []
    for prop in value.bl_rna.properties:
        if prop.is_readonly or prop.identifier in excluded or prop.identifier == 'rna_type':
            continue
        result.append((prop.identifier, _value(getattr(value, prop.identifier), seen)))
    return tuple(result)


def _sockets(sockets, seen):
    return tuple(sorted(((sock.identifier, sock.name, _properties(sock, seen))
                         for sock in sockets), key=lambda row: (row[0], row[1])))


def _group_signature(group, seen=None):
    if seen is None:
        seen = set()
    if group.as_pointer() in seen:
        raise _Unverifiable('cyclic node group')
    seen.add(group.as_pointer())
    try:
        interface = tuple(sorted(
            ((item.name, item.identifier, item.in_out, item.socket_type,
              _properties(item, seen, ('name', 'identifier', 'in_out', 'socket_type', 'parent')))
             for item in group.interface.items_tree if item.item_type == 'SOCKET'),
            key=lambda row: (row[1], row[2])))
        nodes = tuple(sorted((node.name, node.bl_idname, _properties(node, seen),
                              _sockets(node.inputs, seen), _sockets(node.outputs, seen),
                              tuple(sorted((key, _value(value, seen)) for key, value in node.items())))
                             for node in group.nodes))
        links = tuple(sorted((link.from_node.name, link.from_socket.identifier,
                              link.to_node.name, link.to_socket.identifier) for link in group.links))
        custom = tuple(sorted((key, _value(value, seen)) for key, value in group.items()))
        return (group.get('qc_asset_id'), interface, nodes, links, custom)
    finally:
        seen.remove(group.as_pointer())


def _legacy_description(asset_id, group):
    return _LEGACY_DESCRIPTIONS.get(
        asset_id, group.name + '; source data remains unchanged; coordinates in angstrom')


def preview_legacy_assets():
    """Return (name, status) without modifying project node groups."""
    if not LIBRARY_FILE.is_file():
        raise FileNotFoundError(LIBRARY_FILE)
    with bpy.data.libraries.load(str(LIBRARY_FILE), link=False) as (source, target):
        target.node_groups = list(source.node_groups)
    loaded = [group for group in target.node_groups if group is not None]
    standards = {group.get('qc_asset_id'): group for group in loaded
                 if group.get('qc_asset_id') in ASSETS}
    results = []
    try:
        for group in bpy.data.node_groups:
            if group in loaded or group.library is not None or group.asset_data is None:
                continue
            asset_id = group.get('qc_asset_id')
            if asset_id not in ASSETS:
                continue
            status = 'custom or modified; skipped'
            reference = standards.get(asset_id)
            if (reference is not None and group.bl_idname == 'GeometryNodeTree'
                    and group.asset_data.description == _legacy_description(asset_id, group)
                    and str(group.asset_data.catalog_id) == '00000000-0000-0000-0000-000000000000'):
                try:
                    if _group_signature(group) == _group_signature(reference):
                        status = 'standard; clear asset mark'
                except _Unverifiable:
                    pass
            results.append((group.name, status))
    finally:
        for group in reversed(loaded):
            bpy.data.node_groups.remove(group, do_unlink=True)
    return results


class QCBLENDER_OT_cleanup_legacy_node_assets(bpy.types.Operator):
    bl_idname = 'qcblender.cleanup_legacy_node_assets'
    bl_label = 'Preview and Tidy Legacy QC Node Assets'
    bl_options = {'REGISTER', 'UNDO'}

    preview: bpy.props.StringProperty(options={'HIDDEN'})

    def invoke(self, context, event):
        self.preview = json.dumps(preview_legacy_assets())
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        column = self.layout.column()
        rows = json.loads(self.preview)
        if not rows:
            column.label(text='No legacy QC asset marks found')
        for name, status in rows:
            column.label(text=f'{name}: {status}')

    def execute(self, context):
        if not self.preview:
            self.report({'ERROR'}, 'Preview the assets before tidying')
            return {'CANCELLED'}
        before = [tuple(row) for row in json.loads(self.preview)]
        current = preview_legacy_assets()
        if current != before:
            self.report({'ERROR'}, 'Node assets changed since preview; preview again')
            return {'CANCELLED'}
        names = {name for name, status in current if status == 'standard; clear asset mark'}
        for name in names:
            bpy.data.node_groups[name].asset_clear()
        self.report({'INFO'}, f'Cleared {len(names)} unchanged legacy QC asset marks')
        return {'FINISHED'}
