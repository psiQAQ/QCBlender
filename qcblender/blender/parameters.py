"""Classify existing view inputs for native Properties sections."""

GROUP_LABELS = {'geometry': 'Geometry Representation', 'color': 'Color Mapping',
                'legend': 'Legend Layout', 'material': 'Material',
                'spatial': 'Spatial View', 'advanced': 'Advanced Parameters'}
GROUPS = tuple(GROUP_LABELS)
_LEGEND = {'Show Legend', 'Legend Position', 'Legend Length', 'Legend Width',
           'Legend Text Size', 'Legend Decimals', 'Legend Vertical', 'Legend Rotation'}

STYLES = {
    'atoms': ('Ball and Stick', 'Space Filling', 'Bonds'),
    'field': ('Solid', 'Wireframe', 'Points'),
}
STYLE_SOCKETS = {
    'atoms': 'Style (0 ball-stick, 1 space-fill, 2 bonds)',
    'field': 'Style (0 solid, 1 wire, 2 points)',
}

_GEOMETRY = {
    'Selection', 'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)',
    'Isovalue', 'Link Thresholds', 'Negative Isovalue', 'Positive Phase', 'Negative Phase',
    'Adaptivity', 'Smooth Normals', 'Atom Radius', 'Bond Radius', 'VDW Scale',
    'Wire Radius', 'Point Radius', 'Quality',
    'Resolution', 'Show Displacement Vectors', 'Vector Radius',
}
_COLOR = {'Color Minimum', 'Color Center', 'Color Maximum',
          'Charge Minimum', 'Charge Center', 'Charge Maximum', 'Show Legend'}
_MATERIAL = {'Material', 'Positive Material', 'Negative Material',
             'Positive Opacity', 'Negative Opacity'}
_SPATIAL = {'Center', 'Rotation', 'Width', 'Height', 'Legend Position', 'Plane Enabled', 'Plane Origin', 'Plane Normal',
            'Box Enabled', 'Box Minimum', 'Box Maximum'}


def socket_group(name, kind, values, quantity=''):
    """Return a section, or None when this socket has no effect in this state."""
    style = values.get('Style (0 ball-stick, 1 space-fill, 2 bonds)',
                       values.get('Style (0 solid, 1 wire, 2 points)', 0))
    field_style = 'Style (0 solid, 1 wire, 2 points)' in values
    if name == 'Geometry':
        return None
    if name in STYLE_SOCKETS.values():
        return 'geometry'
    if name in ('Atom Radius',) and style != 0:
        return None
    if name in ('Bond Radius',) and style == 1:
        return None
    if name == 'VDW Scale' and style != 1:
        return None
    if name == 'Wire Radius' and style != 1:
        return None
    if name == 'Point Radius' and style != 2:
        return None
    if name == 'Quality' and (style != 2 if field_style else style == 2):
        return None
    if name in ('Link Thresholds', 'Negative Isovalue') and not values.get('Negative Phase', True):
        return None
    if name in ('Positive Opacity', 'Positive Material') and not values.get('Positive Phase', True):
        return None
    if name in ('Negative Phase', 'Negative Isovalue', 'Negative Opacity', 'Negative Material'):
        if quantity in ('electron_number_density', 'alpha_density', 'beta_density'):
            return None
        if name == 'Negative Isovalue' and values.get('Link Thresholds', True):
            return None
        if name in ('Negative Opacity', 'Negative Material') and not values.get('Negative Phase', True):
            return None
    if name in ('Plane Origin', 'Plane Normal') and not values.get('Plane Enabled', False):
        return None
    if name in ('Box Minimum', 'Box Maximum') and not values.get('Box Enabled', False):
        return None
    if name in _LEGEND:
        return 'legend' if name == 'Show Legend' or values.get('Show Legend', False) else None
    if name in _GEOMETRY:
        return 'geometry'
    if name in _COLOR:
        return 'color'
    if name in _MATERIAL or kind == 'NodeSocketMaterial':
        return 'material'
    if name in _SPATIAL:
        return 'spatial'
    return 'advanced'


def socket_label(name, quantity='', unit=''):
    from ..i18n import iface
    if name == 'Quality':
        return iface('Display Detail')
    if name == 'Resolution':
        return iface('Display Samples per Axis')
    if name == 'Positive Phase':
        return iface('Show Positive Phase' if quantity == 'orbital_amplitude' else 'Show Positive Values')
    if name == 'Negative Phase':
        return iface('Show Negative Phase' if quantity == 'orbital_amplitude' else 'Show Negative Values')
    if name in ('Isovalue', 'Negative Isovalue'):
        return iface('Positive Isovalue' if name == 'Isovalue' else 'Negative Isovalue') + f' [{unit or iface("Unknown Unit")}]'
    legend_labels = {'Show Legend': 'Show Legend', 'Legend Position': 'Position',
                     'Legend Length': 'Length', 'Legend Width': 'Width',
                     'Legend Text Size': 'Text Size', 'Legend Decimals': 'Decimal Places',
                     'Legend Vertical': 'Vertical', 'Legend Rotation': 'Rotation'}
    label = iface(legend_labels.get(name, name))
    if name in ('Legend Position', 'Legend Length', 'Legend Width', 'Legend Text Size'):
        return iface('{label} [layout units]', label=label)
    if name == 'Plane Normal':
        return iface('{label} [view-local direction, dimensionless]', label=label)
    if name.endswith('Radius') or name in ('Width', 'Height'):
        return label + ' [Å]'
    if name in ('Center', 'Plane Origin', 'Box Minimum', 'Box Maximum'):
        return iface('{label} [view-local Å]', label=label)
    if name in ('Color Minimum', 'Color Center', 'Color Maximum'):
        return label + f' [{unit or iface("Unknown Unit")}]'
    if name in ('Charge Minimum', 'Charge Center', 'Charge Maximum'):
        return label + ' [e]'
    return label


if __name__ == '__main__':
    atom = {'Style (0 ball-stick, 1 space-fill, 2 bonds)': 1}
    field = {'Style (0 solid, 1 wire, 2 points)': 2, 'Negative Phase': True,
             'Link Thresholds': False}
    assert socket_group('Atom Radius', 'NodeSocketFloat', atom) is None
    assert socket_group('VDW Scale', 'NodeSocketFloat', atom) == 'geometry'
    assert socket_group('Quality', 'NodeSocketInt', field) == 'geometry'
    assert socket_group('Wire Radius', 'NodeSocketFloat', field) is None
    assert socket_group('Negative Isovalue', 'NodeSocketFloat', field, 'orbital_amplitude') == 'geometry'
    assert socket_group('Plane Origin', 'NodeSocketVector', {'Plane Enabled': False}) is None
    assert socket_group('Center', 'NodeSocketVector', {}) == 'spatial'
    assert socket_group('custom_input', 'NodeSocketFloat', {}) == 'advanced'
    assert socket_group('Style (custom)', 'NodeSocketInt', {}) == 'advanced'
    assert socket_label('Negative Phase', 'orbital_amplitude') in ('显示负相位', 'Show Negative Phase')
    assert socket_label('Isovalue', unit='hartree/e').endswith('[hartree/e]')
