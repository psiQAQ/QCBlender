"""Discover UI classes and register their RNA dependencies in order."""

import importlib
import inspect
import pkgutil

import bpy

_registered = []


def discover():
    from . import blender
    bases = (bpy.types.Panel, bpy.types.Operator, bpy.types.PropertyGroup,
             bpy.types.AddonPreferences, bpy.types.UIList)
    classes = set()
    for info in pkgutil.walk_packages(blender.__path__, blender.__name__ + '.'):
        module = importlib.import_module(info.name)
        for value in vars(module).values():
            if (inspect.isclass(value) and value.__module__ == module.__name__
                    and issubclass(value, bases)):
                classes.add(value)
    by_id = {c.bl_idname: c for c in classes if hasattr(c, 'bl_idname')}
    pending = {}
    for cls in classes:
        deps = set()
        for annotation in getattr(cls, '__annotations__', {}).values():
            if isinstance(annotation, bpy.props._PropertyDeferred):
                target = annotation.keywords.get('type')
                if target in classes:
                    deps.add(target)
        parent = by_id.get(getattr(cls, 'bl_parent_id', None))
        if parent is not None:
            deps.add(parent)
        pending[cls] = deps
    ordered = []
    while pending:
        ready = sorted((c for c, deps in pending.items() if not deps), key=lambda c: c.__name__)
        if not ready:
            raise RuntimeError('Cyclic QCBlender RNA registration dependencies')
        for cls in ready:
            ordered.append(cls)
            del pending[cls]
        for deps in pending.values():
            deps.difference_update(ready)
    return ordered


def register():
    if _registered:
        raise RuntimeError('QCBlender is already registered')
    try:
        for cls in discover():
            bpy.utils.register_class(cls)
            _registered.append(cls)
    except Exception:
        unregister()
        raise


def unregister():
    while _registered:
        cls = _registered[-1]
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
        _registered.pop()
