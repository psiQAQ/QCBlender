"""Output choices and scale-invariant lighting, without Blender dependencies."""

from dataclasses import dataclass
import math


PRESET_VERSION = 1
BACKGROUNDS = ('WHITE', 'BLACK', 'TRANSPARENT', 'CUSTOM')


@dataclass(frozen=True)
class QualityPreset:
    engine: str
    samples: int
    adaptive_threshold: float | None


QUALITY_PRESETS = {
    'PREVIEW': QualityPreset('BLENDER_EEVEE', 64, None),
    'STANDARD': QualityPreset('CYCLES', 128, .02),
    'HIGH': QualityPreset('CYCLES', 512, .005),
}


def output_plan(*, quality='STANDARD', background='WHITE', background_color=(1., 1., 1.),
                resolution_x=1920, resolution_y=1080, resolution_percentage=100,
                denoise=True):
    """Validate explicit user choices before any Blender state changes."""
    if quality not in QUALITY_PRESETS:
        raise ValueError('Unknown output quality: ' + str(quality))
    if background not in BACKGROUNDS:
        raise ValueError('Unknown output background: ' + str(background))
    for label, value, maximum in [('resolution_x', resolution_x, 65536),
                                  ('resolution_y', resolution_y, 65536),
                                  ('resolution_percentage', resolution_percentage, 100)]:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
            raise ValueError(f'{label} must be an integer from 1 to {maximum}')
    try:
        color = tuple(float(value) for value in background_color)
    except (TypeError, ValueError) as error:
        raise ValueError('Background color must contain three finite values in [0, 1]') from error
    if len(color) != 3 or any(not math.isfinite(value) or not 0 <= value <= 1 for value in color):
        raise ValueError('Background color must contain three finite values in [0, 1]')
    if not isinstance(denoise, bool):
        raise ValueError('Denoising must be enabled or disabled')
    color = {'WHITE': (1., 1., 1.), 'BLACK': (0., 0., 0.)}.get(background, color)
    return {'version': PRESET_VERSION, 'quality': quality, 'background': background,
            'background_color': color, 'resolution_x': resolution_x,
            'resolution_y': resolution_y, 'resolution_percentage': resolution_percentage,
            'denoise': denoise}


def lighting_layout(points, right=(1., 0., 0.), up=(0., 1., 0.), back=(0., 0., 1.)):
    """Place three neutral area lights in camera axes around the subject bounds.

    Coordinates and area sizes scale with the largest projected subject span L;
    wattage scales with L squared, preserving irradiance under uniform scaling.
    The camera's local +Z points back towards the viewer.
    """
    try:
        points = [tuple(float(value) for value in point) for point in points]
        basis = [tuple(float(value) for value in axis) for axis in (right, up, back)]
    except (TypeError, ValueError) as error:
        raise ValueError('Subject points and camera axes must be finite 3D coordinates') from error
    if (not points or any(len(point) != 3 for point in points + basis)
            or any(not math.isfinite(value) for point in points + basis for value in point)):
        raise ValueError('Subject points and camera axes must be finite 3D coordinates')
    dot = lambda first, second: sum(a * b for a, b in zip(first, second))
    if any(abs(dot(first, second) - (1. if i == j else 0.)) > 1e-5
           for i, first in enumerate(basis) for j, second in enumerate(basis)):
        raise ValueError('Camera axes must be orthonormal')
    projected = [tuple(dot(point, axis) for axis in basis) for point in points]
    low = tuple(min(point[i] for point in projected) for i in range(3))
    high = tuple(max(point[i] for point in projected) for i in range(3))
    scale = max(b - a for a, b in zip(low, high))
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('Subject bounds must have positive extent')
    midpoint = tuple((a + b) / 2 for a, b in zip(low, high))
    center = tuple(sum(midpoint[j] * basis[j][i] for j in range(3)) for i in range(3))
    lights = []
    for role, offset, wattage, size in [('KEY', (.75, 1., 1.25), 24., .6),
                                        ('FILL', (-1., .25, .75), 14., .5),
                                        ('RIM', (.25, .75, -1.), 20., .4)]:
        location = tuple(center[i] + scale * sum(offset[j] * basis[j][i] for j in range(3))
                         for i in range(3))
        energy = wattage * scale * scale
        if not all(math.isfinite(value) for value in (*location, energy)) or energy <= 0:
            raise ValueError('Subject scale exceeds the supported lighting range')
        lights.append({'role': role, 'location': location, 'energy': energy, 'size': size * scale})
    return {'center': center, 'scale': scale, 'lights': lights}
