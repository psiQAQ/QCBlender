_hooks_registered = False


def register():
    global _hooks_registered
    from . import auto_load
    auto_load.register()
    import bpy
    from .blender.properties import QCViewSettings
    bpy.types.Object.qc_settings = bpy.props.PointerProperty(type=QCViewSettings)
    from .blender.source_browser import refresh_loaded_sources
    from .blender.editor_ui import object_context_menu
    from .blender import asset_library, interaction
    try:
        asset_library.register()
        interaction.register_tool()
        bpy.app.handlers.load_post.append(refresh_loaded_sources)
        bpy.app.handlers.save_post.append(refresh_loaded_sources)
        bpy.types.VIEW3D_MT_object_context_menu.append(object_context_menu)
        _hooks_registered = True
        bpy.app.timers.register(refresh_loaded_sources, first_interval=0)
    except Exception:
        unregister()
        raise


def unregister():
    global _hooks_registered
    from . import auto_load
    from .blender.jobs import cancel_all
    from .blender.ui import cancel_operations
    cancel_operations()
    cancel_all()
    import bpy
    from .blender.source_browser import refresh_loaded_sources, _metadata
    from .blender.editor_ui import object_context_menu
    for handlers in (bpy.app.handlers.load_post, bpy.app.handlers.save_post):
        if refresh_loaded_sources in handlers:
            handlers.remove(refresh_loaded_sources)
    if bpy.app.timers.is_registered(refresh_loaded_sources):
        bpy.app.timers.unregister(refresh_loaded_sources)
    if _hooks_registered:
        bpy.types.VIEW3D_MT_object_context_menu.remove(object_context_menu)
        _hooks_registered = False
    from .blender import asset_library, interaction
    interaction.unregister_tool()
    asset_library.unregister()
    _metadata.clear()
    if hasattr(bpy.types.Object, 'qc_settings'):
        del bpy.types.Object.qc_settings
    auto_load.unregister()
