"""Classify existing view inputs for the QCBlender sidebar."""

GROUPS = ('几何表示', '颜色映射', '材质', '空间观察', '高级参数')

STYLES = {
    'atoms': ('球棍', '空间填充', '键线'),
    'field': ('实面', '线框', '点'),
}
STYLE_SOCKETS = {
    'atoms': 'Style (0 ball-stick, 1 space-fill, 2 bonds)',
    'field': 'Style (0 solid, 1 wire, 2 points)',
}

_GEOMETRY = {
    'Selection', 'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)',
    'Isovalue', 'Link Thresholds', 'Negative Isovalue', 'Positive Phase', 'Negative Phase',
    'Adaptivity', 'Smooth Normals', 'Atom Radius', 'Bond Radius', 'VDW Scale',
    'Wire Radius', 'Point Radius', 'Quality', 'Center', 'Rotation', 'Width', 'Height',
    'Resolution', 'Show Displacement Vectors', 'Vector Radius',
}
_COLOR = {'Color Minimum', 'Color Center', 'Color Maximum',
          'Charge Minimum', 'Charge Center', 'Charge Maximum', 'Show Legend'}
_MATERIAL = {'Material', 'Positive Material', 'Negative Material',
             'Positive Opacity', 'Negative Opacity'}
_SPATIAL = {'Legend Position', 'Plane Enabled', 'Plane Origin', 'Plane Normal',
            'Box Enabled', 'Box Minimum', 'Box Maximum'}


def socket_group(name, kind, values, quantity=''):
    """Return a section, or None when this socket has no effect in this state."""
    style = values.get('Style (0 ball-stick, 1 space-fill, 2 bonds)',
                       values.get('Style (0 solid, 1 wire, 2 points)', 0))
    field_style = 'Style (0 solid, 1 wire, 2 points)' in values
    if name == 'Geometry':
        return None
    if name in STYLE_SOCKETS.values():
        return '几何表示'
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
    if name == 'Legend Position' and not values.get('Show Legend', False):
        return None
    if name in _GEOMETRY:
        return '几何表示'
    if name in _COLOR:
        return '颜色映射'
    if name in _MATERIAL or kind == 'NodeSocketMaterial':
        return '材质'
    if name in _SPATIAL:
        return '空间观察'
    return '高级参数'


def socket_label(name, quantity='', unit=''):
    if name == 'Quality':
        return '显示精细度'
    if name == 'Resolution':
        return '显示采样数/轴'
    if name == 'Plane Normal':
        return 'Plane Normal [视图局部方向，无量纲]'
    if name == 'Positive Phase':
        return '显示正相位' if quantity == 'orbital_amplitude' else '显示正值'
    if name == 'Negative Phase':
        return '显示负相位' if quantity == 'orbital_amplitude' else '显示负值'
    if name in ('Isovalue', 'Negative Isovalue'):
        return ('正值阈值' if name == 'Isovalue' else '负值阈值') + f' [{unit or "单位未知"}]'
    if name.endswith('Radius') or name in ('Width', 'Height', 'Vector Radius'):
        return name + ' [Å]'
    if name in ('Center', 'Legend Position', 'Plane Origin', 'Box Minimum', 'Box Maximum'):
        return name + ' [视图局部 Å]'
    if name in ('Color Minimum', 'Color Center', 'Color Maximum'):
        return name + f' [{unit or "单位未知"}]'
    if name in ('Charge Minimum', 'Charge Center', 'Charge Maximum'):
        return name + ' [e]'
    return name


if __name__ == '__main__':
    atom = {'Style (0 ball-stick, 1 space-fill, 2 bonds)': 1}
    field = {'Style (0 solid, 1 wire, 2 points)': 2, 'Negative Phase': True,
             'Link Thresholds': False}
    assert socket_group('Atom Radius', 'NodeSocketFloat', atom) is None
    assert socket_group('VDW Scale', 'NodeSocketFloat', atom) == '几何表示'
    assert socket_group('Quality', 'NodeSocketInt', field) == '几何表示'
    assert socket_group('Wire Radius', 'NodeSocketFloat', field) is None
    assert socket_group('Negative Isovalue', 'NodeSocketFloat', field, 'orbital_amplitude') == '几何表示'
    assert socket_group('Plane Origin', 'NodeSocketVector', {'Plane Enabled': False}) is None
    assert socket_group('custom_input', 'NodeSocketFloat', {}) == '高级参数'
    assert socket_group('Style (custom)', 'NodeSocketInt', {}) == '高级参数'
    assert socket_label('Negative Phase', 'orbital_amplitude') == '显示负相位'
    assert socket_label('Isovalue', unit='hartree/e').endswith('[hartree/e]')
