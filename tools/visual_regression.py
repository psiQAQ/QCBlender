"""Compare fixed-render RGB pixels without changing reference images."""
import numpy as np


THRESHOLDS = {'mean_absolute_error': .003, 'pixel_channel_delta': 8 / 255,
              'changed_pixel_fraction': .01}


def compare_pixels(actual, expected, regions, thresholds=THRESHOLDS):
    if actual.shape != expected.shape or actual.ndim != 3 or actual.shape[2] != 3:
        raise ValueError('Visual images must have matching height, width and RGB channels')
    if not np.isfinite(actual).all() or not np.isfinite(expected).all():
        raise ValueError('Visual images contain non-finite pixels')
    if min(actual.min(), expected.min()) < 0 or max(actual.max(), expected.max()) > 1:
        raise ValueError('Visual pixels must be normalized to [0, 1]')
    height, width, _ = actual.shape
    results = {}
    for name, bounds in {'full': [0, 0, width, height], **regions}.items():
        if len(bounds) != 4 or any(type(value) is not int for value in bounds):
            raise ValueError('Visual regions require four integer pixel coordinates')
        left, top, right, bottom = bounds
        if not 0 <= left < right <= width or not 0 <= top < bottom <= height:
            raise ValueError('Visual region lies outside the image: ' + name)
        delta = np.abs(actual[top:bottom, left:right] - expected[top:bottom, left:right])
        mae = float(delta.mean())
        changed = float((delta.max(axis=2) > thresholds['pixel_channel_delta']).mean())
        results[name] = {'mean_absolute_error': mae, 'changed_pixel_fraction': changed,
                         'status': 'Passed' if mae <= thresholds['mean_absolute_error']
                         and changed <= thresholds['changed_pixel_fraction'] else 'Failed'}
    return {'status': 'Passed' if all(row['status'] == 'Passed' for row in results.values()) else 'Failed',
            'regions': results, 'thresholds': dict(thresholds)}


def check_identity(actual, expected):
    for key in ('environment', 'scene', 'input_sha256', 'scientific_arrays'):
        if actual[key] != expected[key]:
            raise ValueError('Visual reference identity differs: ' + key)
