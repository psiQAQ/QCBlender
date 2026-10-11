"""Frozen ColorRamp data; importing this module needs no Blender or color library.

Viridis and Cividis: MolecularNodes, GPL-3.0-or-later,
molecularnodes/nodes/geometry/color_matplotlib.py at
2eb05987d0fa60678ea2d793c95fe4bc886270af. The adopted data are unchanged at
f88961b28828dfb32697748b575298dec20af3af. See THIRD_PARTY.md.
The values are Blender ramp RGBA values, used directly without sRGB conversion.
"""
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class ColorPreset:
    label: str
    elements: tuple
    interpolation: str = 'LINEAR'
    color_mode: str = 'RGB'
    hue_interpolation: str = 'NEAR'


PRESETS = MappingProxyType({
    'QC_DEFAULT': ColorPreset('QC Default', (
        (0., (.8, .03, .02, 1.)),
        (.5, (.95, .95, .95, 1.)),
        (1., (.03, .18, .8, 1.)),
    )),
    'VIRIDIS': ColorPreset('Viridis', (
        (0.0, (0.056964, 0.0, 0.084614, 1.0)),
        (0.033127, (0.063545, 0.003412, 0.116646, 1.0)),
        (0.091617, (0.066458, 0.013306, 0.169059, 1.0)),
        (0.178541, (0.059207, 0.041897, 0.242128, 1.0)),
        (0.295513, (0.033152, 0.106746, 0.269137, 1.0)),
        (0.439554, (0.019165, 0.21278, 0.277688, 1.0)),
        (0.583146, (0.007237, 0.371209, 0.2478, 1.0)),
        (0.693999, (0.037512, 0.512948, 0.170768, 1.0)),
        (0.786693, (0.149213, 0.628924, 0.090451, 1.0)),
        (0.864936, (0.35698, 0.713773, 0.032054, 1.0)),
        (0.928568, (0.624903, 0.754318, 0.007932, 1.0)),
        (0.975252, (0.861662, 0.786243, 0.009231, 1.0)),
        (1.0, (1.0, 0.800834, 0.019509, 1.0)),
    ), 'B_SPLINE'),
    'CIVIDIS': ColorPreset('Cividis', (
        (0.0, (0.0, 0.016467, 0.075244, 1.0)),
        (0.030621, (0.0, 0.021184, 0.103398, 1.0)),
        (0.079477, (0.0, 0.030102, 0.164417, 1.0)),
        (0.090894, (0.000187, 0.031563, 0.163847, 1.0)),
        (0.18086, (0.028134, 0.054017, 0.151467, 1.0)),
        (0.291146, (0.073707, 0.091234, 0.149138, 1.0)),
        (0.402322, (0.133844, 0.141348, 0.163683, 1.0)),
        (0.519735, (0.216215, 0.210928, 0.191532, 1.0)),
        (0.644381, (0.346179, 0.308209, 0.180823, 1.0)),
        (0.769231, (0.524198, 0.437177, 0.145954, 1.0)),
        (0.884914, (0.740223, 0.593282, 0.094374, 1.0)),
        (0.987296, (0.985118, 0.768256, 0.033705, 1.0)),
        (1.0, (0.992194, 0.807711, 0.038779, 1.0)),
    )),
})


def get_preset(identifier):
    try:
        return PRESETS[identifier]
    except KeyError:
        raise ValueError(f'Unknown color preset: {identifier}') from None
