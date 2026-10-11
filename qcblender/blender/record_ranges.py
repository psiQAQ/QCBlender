"""Per-object row ranges from explicitly refreshed scientific metadata."""


def _bound_property(obj, name, count):
    if name not in obj:
        return
    upper = max(1, count)
    obj.id_properties_ui(name).update(min=1, max=upper, soft_min=1, soft_max=upper)
    obj[name] = min(upper, max(1, int(obj[name])))


def _refresh_view_ranges(obj, meta):
    from .graph import view_modifier

    try:
        modifier = view_modifier(obj)
    except ValueError:
        # User-edited graphs without a unique QC modifier have no range upgrade.
        return
    tree = modifier.node_group
    if tree.get('qc_asset_id'):
        return
    limits = {'Style (0 ball-stick, 1 space-fill, 2 bonds)': (0, 2),
              'Style (0 solid, 1 wire, 2 points)': (0, 2)}
    count = meta.get('_atom_count')
    if obj.get('qc_view_kind') == 'atoms' and type(count) is int and count >= 0:
        limits.update({'First Atom (1-based)': (1, max(1, count)),
                       'Last Atom (0 = all)': (0, count)})
    if tree.users > 1:
        tree = tree.copy()
        modifier.node_group = tree
    for item in tree.interface.items_tree:
        if (item.item_type != 'SOCKET' or item.in_out != 'INPUT'
                or item.socket_type != 'NodeSocketInt' or item.name not in limits):
            continue
        lower, upper = limits[item.name]
        item.min_value, item.max_value = lower, upper
        if item.identifier in modifier:
            modifier.id_properties_ui(item.identifier).update(
                min=lower, max=upper, soft_min=lower, soft_max=upper)
            modifier[item.identifier] = min(upper, max(lower, int(modifier[item.identifier])))


def refresh_record_ranges(obj, meta):
    """Bound existing row selectors without reading arrays or source files."""
    analysis = meta.get('analysis', {})
    role = obj.get('qc_analysis_role', obj.get('qc_view_kind'))
    if obj.get('qc_view_kind') in ('atoms', 'field') and obj.get('qc_dataset'):
        _refresh_view_ranges(obj, meta)
    if role == 'nbo':
        _bound_property(obj, 'qc_nbo_index', len(analysis.get('orbitals', [])))
        _bound_property(obj, 'qc_e2_index', len(analysis.get('interactions', [])))
        return
    if role == 'irc_mayer':
        count = meta.get('_atom_count')
        if type(count) is int and count >= 0:
            _bound_property(obj, 'qc_pair_a', count)
            _bound_property(obj, 'qc_pair_b', count)
        return
    if role in ('esp_maximum', 'esp_minimum'):
        count = sum(row['kind'] == role[4:] for row in analysis.get('extrema', []))
    elif role in ('aim_C', 'aim_N', 'aim_O', 'aim_F'):
        count = sum(row['type'] == role[4:] for row in analysis.get('critical_points', []))
    elif role in ('esp_area', 'aim_paths', 'ets_nocv'):
        key = {'esp_area': 'area_bins', 'aim_paths': 'paths', 'ets_nocv': 'pairs'}[role]
        count = len(analysis.get(key, []))
    else:
        return
    _bound_property(obj, 'qc_analysis_index', count)
