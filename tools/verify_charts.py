"""Pure-Python checks for contours and profile layout."""

from pathlib import Path
import hashlib
import sys
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qcblender.contours import contour_report, levels_from_samples, plane_positions, trace_contours
from qcblender.plot_layout import profile_layout


plane = plane_positions((0, 0, 0), (1, 0, 0), (0, 1, 0), 2)
assert plane.shape == (2, 2, 3)
assert len(levels_from_samples(np.array([[0., 10.]]), np.ones((1, 2), bool))) == 9
assert levels_from_samples(np.array([[0., 10.]]), np.ones((1, 2), bool), '3, 1') == [1., 3.]
try:
    levels_from_samples(np.array([[0., 10.]]), np.ones((1, 2), bool), list(range(65)))
except ValueError:
    pass
else:
    raise AssertionError('More than 64 contour levels must be rejected')

# Each saddle orientation must produce two disjoint segments with the right edge pairing.
high_center = trace_contours(np.array([[2., -1.], [-1., 2.]]), np.ones((2, 2), bool), plane, 0.)
low_center = trace_contours(np.array([[1., -2.], [-2., 1.]]), np.ones((2, 2), bool), plane, 0.)
assert len(high_center) == len(low_center) == 2


def edge(point):
    x, y, _ = point
    return 'left' if x == 0 else 'right' if x == 1 else 'bottom' if y == 0 else 'top'


assert {frozenset(map(edge, (line[0], line[-1]))) for line in high_center} == {
    frozenset(('bottom', 'right')), frozenset(('top', 'left'))}
assert {frozenset(map(edge, (line[0], line[-1]))) for line in low_center} == {
    frozenset(('bottom', 'left')), frozenset(('top', 'right'))}
assert len(trace_contours(np.array([[1., -1.], [-1., 1.]]),
                          np.ones((2, 2), bool), plane, 0.)) == 4
assert not trace_contours(np.array([[0., 1.], [1., 0.]]),
                          np.array([[True, True], [False, True]]), plane, .5)

field = {'array': 'scalar', 'valid_mask': 'mask', 'origin': [0., 0., 0.],
         'steps': [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]}
volume = np.fromfunction(lambda x, y, z: x+y+z, (2, 2, 2), dtype=float)
dataset = SimpleNamespace(arrays={'scalar': volume, 'mask': np.ones((2, 2, 2), bool)},
                          metadata={'fields': [field]})
request = {'dataset': 'unused', 'dataset_sha256': hashlib.sha256(b'manifest').hexdigest(),
           'field': field, 'plane': {'origin': [0, 0, 0], 'axis_u': [1, 0, 0],
                                    'axis_v': [0, 1, 0], 'resolution': 3},
           'levels': '0.5', 'identity': 'test-id'}
with patch.object(Path, 'read_bytes', return_value=b'manifest'):
    report = contour_report(request, lambda _: dataset)
assert report['status'] == 'succeeded' and report['identity'] == 'test-id'
assert report['sample_count'] == report['valid_count'] == 9 and report['paths'][0]['lines']

layout = profile_layout([0., 1., 2., 3.], [0., 1., 9., 3.], [True, True, False, True])
assert len(layout['paths']) == 1 and layout['width'] == 4. and layout['height'] == 3.
assert layout['paths'][0][-1][0] == 4. / 3.
cropped = profile_layout([0., 1., 2.], [0., 1., 2.], [True]*3,
                         {'x_auto': False, 'x_min': .5, 'x_max': 1.5,
                          'y_auto': False, 'y_min': .5, 'y_max': 1.5})
assert len(cropped['paths']) == 1 and cropped['paths'][0][0] == (0., 0., 0.)
assert cropped['paths'][0][-1] == (4., 0., 3.)
print('CHARTS_PASSED')
