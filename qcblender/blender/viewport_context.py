"""Resolve explicit Properties targets and a 3D View in the same window."""
from dataclasses import dataclass

import bpy


def target_object(context):
    """A pinned Properties Object is the target, even if another object is active."""
    area = getattr(context, 'area', None)
    if area is not None and area.type == 'PROPERTIES':
        space = area.spaces.active
        if getattr(space, 'use_pin_id', False):
            pinned = space.pin_id
            return pinned if isinstance(pinned, bpy.types.Object) else None
    return getattr(context, 'object', None)


class _TargetContext:
    def __init__(self, context):
        self.object = target_object(context)
        self._context = context

    def __getattr__(self, name):
        return getattr(self._context, name)


def target_context(context):
    """Use the explicit object for read-only eligibility checks without changing RNA."""
    return _TargetContext(context)


@dataclass(frozen=True)
class ViewportContext:
    window: object
    screen: object
    area: object
    region: object
    view: object

    def validate(self):
        if (self.window.screen != self.screen or self.area not in tuple(self.screen.areas)
                or self.area.type != 'VIEW_3D' or self.region not in tuple(self.area.regions)
                or self.region.type != 'WINDOW'):
            raise ValueError('The selected 3D View changed during probing; start the probe again')

    def contains(self, event):
        return (self.region.x <= event.mouse_x < self.region.x + self.region.width
                and self.region.y <= event.mouse_y < self.region.y + self.region.height)


def viewport_context(context):
    """Keep the invoking 3D View; Properties uses the largest same-window view."""
    window = getattr(context, 'window', None)
    if window is None:
        raise ValueError('A 3D View in the same window is required')
    screen = window.screen
    current = getattr(context, 'area', None)
    if current is None or current.type not in ('VIEW_3D', 'PROPERTIES'):
        raise ValueError('Open this action from a 3D View or Object Properties')
    if current.type == 'VIEW_3D':
        area = current
        if area not in tuple(screen.areas):
            raise ValueError('A 3D View in the same window is required')
    else:
        areas = [area for area in screen.areas if area.type == 'VIEW_3D']
        if not areas:
            raise ValueError('A 3D View in the same window is required')
        # max returns the first matching area on a tie, preserving screen order.
        area = max(areas, key=lambda item: item.width * item.height)
    region = getattr(context, 'region', None) if area == current else None
    if region is None or region.type != 'WINDOW':
        region = next((item for item in area.regions if item.type == 'WINDOW'), None)
    if region is None:
        raise ValueError('3D viewport window is unavailable')
    if area == current and region == getattr(context, 'region', None):
        view = getattr(context, 'region_data', None)
    else:
        view = None
    if view is None:
        # Region-specific context also handles the selected pane in quad view.
        with context.temp_override(window=window, area=area, region=region):
            view = bpy.context.region_data
    if view is None:
        raise ValueError('A VIEW_3D viewing direction is required')
    return ViewportContext(window, screen, area, region, view)
