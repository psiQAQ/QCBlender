def register():
    from . import auto_load
    auto_load.register()
    import bpy
    from .blender.properties import QCViewSettings
    bpy.types.Object.qc_settings = bpy.props.PointerProperty(type=QCViewSettings)
    from .blender.source_browser import refresh_loaded_sources
    from .blender.editor_ui import object_context_menu
    bpy.app.handlers.load_post.append(refresh_loaded_sources)
    bpy.app.handlers.save_post.append(refresh_loaded_sources)
    bpy.types.VIEW3D_MT_object_context_menu.append(object_context_menu)
    refresh_loaded_sources()


def unregister():
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
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_context_menu)
    _metadata.clear()
    if hasattr(bpy.types.Object, 'qc_settings'):
        del bpy.types.Object.qc_settings
    auto_load.unregister()
