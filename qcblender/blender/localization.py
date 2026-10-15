"""Refresh generated presentation after preferences, load, or graph changes."""
import bpy
from bpy.app.handlers import persistent

_owner = object()
_active = False
_signature = None


def _inventory():
    from ..i18n import interface_language
    return (interface_language(), tuple((tree.as_pointer(), len(tree.nodes), len(tree.interface.items_tree))
            for tree in bpy.data.node_groups if tree.get('qc_view_graph') or tree.get('qc_asset_id')))


def _refresh():
    global _signature
    if not _active:
        return None
    from .node_identity import refresh_localization
    refresh_localization()
    _signature = _inventory()
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()
    return None


def queue_refresh(*args):
    if _active and not bpy.app.timers.is_registered(_refresh):
        bpy.app.timers.register(_refresh, first_interval=0.05)


def _subscribe():
    bpy.msgbus.clear_by_owner(_owner)
    for name in ('language', 'use_translate_interface', 'use_translate_tooltips'):
        bpy.msgbus.subscribe_rna(key=(bpy.types.PreferencesView, name), owner=_owner,
                                args=(), notify=queue_refresh, options={'PERSISTENT'})


@persistent
def _loaded(*args):
    _subscribe()
    queue_refresh()


@persistent
def _changed(*args):
    if _active and _inventory() != _signature:
        queue_refresh()


def register():
    global _active
    _active = True
    _subscribe()
    bpy.app.handlers.load_post.append(_loaded)
    bpy.app.handlers.depsgraph_update_post.append(_changed)
    bpy.app.handlers.undo_post.append(_loaded)
    bpy.app.handlers.redo_post.append(_loaded)
    queue_refresh()


def unregister():
    global _active, _signature
    _active = False
    bpy.msgbus.clear_by_owner(_owner)
    if bpy.app.timers.is_registered(_refresh):
        bpy.app.timers.unregister(_refresh)
    for handlers, callback in ((bpy.app.handlers.load_post, _loaded),
                               (bpy.app.handlers.depsgraph_update_post, _changed),
                               (bpy.app.handlers.undo_post, _loaded), (bpy.app.handlers.redo_post, _loaded)):
        if callback in handlers:
            handlers.remove(callback)
    _signature = None
