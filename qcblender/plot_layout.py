"""Linear profile chart layout; scientific samples remain unchanged."""

import numpy as np


DEFAULT_LAYOUT = {'width': 4., 'height': 3., 'line_width': .02,
                  'x_auto': True, 'y_auto': True, 'x_min': 0., 'x_max': 1.,
                  'y_min': 0., 'y_max': 1., 'x_ticks': 5, 'y_ticks': 5,
                  'precision': 3}


def _clip(first, second, bounds):
    x0, y0 = first
    dx, dy = np.asarray(second) - first
    xmin, xmax, ymin, ymax = bounds
    start, end = 0., 1.
    for p, q in ((-dx, x0-xmin), (dx, xmax-x0), (-dy, y0-ymin), (dy, ymax-y0)):
        if abs(p) < 1e-15:
            if q < 0:
                return None
        else:
            ratio = q / p
            if p < 0:
                start = max(start, ratio)
            else:
                end = min(end, ratio)
    if start > end:
        return None
    return ((x0 + start*dx, y0 + start*dy), (x0 + end*dx, y0 + end*dy))


def profile_layout(distance, values, valid, settings=None):
    distance = np.asarray(distance, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    valid = np.asarray(valid, dtype=bool)
    if (distance.ndim != 1 or distance.shape != values.shape or valid.shape != values.shape
            or len(distance) < 2 or not np.isfinite(distance).all()
            or not np.isfinite(values[valid]).all() or np.any(np.diff(distance) <= 0)
            or not valid.any()):
        raise ValueError('Profile distances, values and validity are inconsistent')
    config = dict(DEFAULT_LAYOUT, **(settings or {}))
    width, height, line_width = (float(config[key]) for key in ('width', 'height', 'line_width'))
    if not all(np.isfinite(value) and value > 0 for value in (width, height, line_width)):
        raise ValueError('Profile size and line width must be finite positive values')
    x_ticks, y_ticks, precision = (int(config[key]) for key in ('x_ticks', 'y_ticks', 'precision'))
    if (not 2 <= x_ticks <= 20 or not 2 <= y_ticks <= 20 or not 0 <= precision <= 8
            or any(type(config[key]) is not int for key in ('x_ticks', 'y_ticks', 'precision'))):
        raise ValueError('Use 2–20 ticks and 0–8 decimal places')
    xmin, xmax = (float(distance[0]), float(distance[-1])) if config['x_auto'] else (
        float(config['x_min']), float(config['x_max']))
    ymin, ymax = ((float(values[valid].min()), float(values[valid].max()))
                  if config['y_auto'] else (float(config['y_min']), float(config['y_max'])))
    if config['y_auto'] and ymin == ymax:
        ymax = ymin + 1.
    if not all(np.isfinite(value) for value in (xmin, xmax, ymin, ymax)) or xmin >= xmax or ymin >= ymax:
        raise ValueError('Manual profile axis ranges must be finite and increasing')

    def display(point):
        return ((point[0] - xmin) * width / (xmax - xmin), 0.,
                (point[1] - ymin) * height / (ymax - ymin))

    paths, current = [], []
    for index in range(len(distance) - 1):
        segment = (_clip((distance[index], values[index]), (distance[index+1], values[index+1]),
                         (xmin, xmax, ymin, ymax)) if valid[index] and valid[index+1] else None)
        if segment is None:
            if len(current) >= 2:
                paths.append(current)
            current = []
            continue
        first, second = map(display, segment)
        if first == second:
            continue
        if current and np.linalg.norm(np.subtract(current[-1], first)) > 1e-10:
            paths.append(current)
            current = []
        if not current:
            current.append(first)
        current.append(second)
    if len(current) >= 2:
        paths.append(current)

    def ticks(low, high, count, scale):
        return [(float(value), float(index * scale / (count-1)),
                 f'{value:.{precision}f}') for index, value in enumerate(np.linspace(low, high, count))]

    return {'paths': paths, 'width': width, 'height': height, 'line_width': line_width,
            'x_range': (xmin, xmax), 'y_range': (ymin, ymax),
            'x_ticks': ticks(xmin, xmax, x_ticks, width),
            'y_ticks': ticks(ymin, ymax, y_ticks, height)}
