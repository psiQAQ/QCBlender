def register():
    from . import auto_load
    auto_load.register()
    import bpy
    from .blender.properties import QCViewSettings
    bpy.types.Object.qc_settings = bpy.props.PointerProperty(type=QCViewSettings)


def unregister():
    from . import auto_load
    from .blender.jobs import cancel_all
    from .blender.ui import cancel_operations
    cancel_operations()
    cancel_all()
    import bpy
    if hasattr(bpy.types.Object, 'qc_settings'):
        del bpy.types.Object.qc_settings
    auto_load.unregister()
