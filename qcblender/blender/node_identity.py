"""Stable QC node identities and conservative, reversible display localization.

``qc_sockets`` remains the canonical input-name to identifier mapping. The
versioned display record tracks only generated text and output identities;
changing a managed label makes it user-owned until explicitly restored.
"""
import json
import re

from ..translations_nodes import MESSAGES

_KEY = 'qc_node_locale'
_VERSION = 1
_REVERSE = {}
for _message, _translation in MESSAGES.items():
    _REVERSE.setdefault(_translation, _message)


def _record(tree):
    value = tree.get(_KEY, '')
    if not value:
        return {'version': _VERSION, 'outputs': {}, 'display': {}}
    record = json.loads(value)
    if record.get('version') != _VERSION:
        raise ValueError('Unsupported QC node localization version')
    return record


def _save(tree, record):
    tree[_KEY] = json.dumps(record, ensure_ascii=False, sort_keys=True)


def _canonical(message):
    return _REVERSE.get(message, message)


def _tree_for_socket(item):
    node = getattr(item, 'node', None)
    nested = getattr(node, 'node_tree', None)
    return nested if nested is not None else getattr(item, 'id_data', None)


def socket_name(item, tree=None):
    """Resolve an interface or group-node socket to its canonical role name."""
    tree = tree if tree is not None else _tree_for_socket(item)
    identifier = getattr(item, 'identifier', None)
    node = getattr(item, 'node', None)
    if node is not None and getattr(node, 'type', '') not in ('GROUP', 'GROUP_INPUT', 'GROUP_OUTPUT'):
        return item.name
    if tree is not None and hasattr(tree, 'get'):
        inputs = json.loads(tree.get('qc_sockets', '{}'))
        outputs = _record(tree)['outputs']
        direction = getattr(item, 'in_out', None)
        if direction is None and node is not None:
            direction = ('OUTPUT' if getattr(node, 'type', '') == 'GROUP_OUTPUT' else
                         'INPUT' if getattr(node, 'type', '') == 'GROUP_INPUT' else
                         'OUTPUT' if getattr(item, 'is_output', False) else 'INPUT')
        maps = (outputs,) if direction == 'OUTPUT' else (inputs,) if direction == 'INPUT' else (inputs, outputs)
        for mapping in maps:
            for name, stable_id in mapping.items():
                if stable_id == identifier:
                    return name
    return _canonical(item.name)


def node_socket(sockets, key):
    """Look up group sockets by canonical identity; built-in sockets stay native."""
    if isinstance(key, int):
        return sockets[key]
    if len(sockets):
        node = getattr(sockets[0], 'node', None)
        if node is not None and getattr(node, 'type', '') not in ('GROUP', 'GROUP_INPUT', 'GROUP_OUTPUT'):
            return sockets[key]
    matches = [item for item in sockets if socket_name(item) == key]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(f'Ambiguous QC socket role: {key}')
    # Blender collections accept identifiers as well as names. Keep that API.
    return sockets[key]


def interface_socket(tree, name, direction='INPUT'):
    matches = [item for item in tree.interface.items_tree
               if item.item_type == 'SOCKET' and item.in_out == direction
               and socket_name(item, tree) == name]
    if len(matches) != 1:
        raise ValueError(f'Expected one QC {direction} socket: {name}')
    return matches[0]


def remember_sockets(tree):
    """Capture new sockets without replacing identities after display changes."""
    inputs = json.loads(tree.get('qc_sockets', '{}'))
    record = _record(tree)
    for item in tree.interface.items_tree:
        if item.item_type != 'SOCKET':
            continue
        mapping = inputs if item.in_out == 'INPUT' else record['outputs']
        if item.identifier not in mapping.values():
            name = _canonical(item.name)
            if name in mapping and mapping[name] != item.identifier:
                raise ValueError(f'Duplicate QC socket role: {name}')
            mapping[name] = item.identifier
    tree['qc_sockets'] = json.dumps(inputs, sort_keys=True)
    _save(tree, record)


def _translate(source, language):
    return MESSAGES.get(source, source) if language == 'zh_HANS' else source


def _managed(owner, attribute, key, record, language, source=None, suffix=''):
    current = getattr(owner, attribute)
    entries = record['display']
    entry = entries.get(key)
    if entry is None:
        source = _canonical(current) if source is None else source
        if source not in MESSAGES:
            return
        entry = entries[key] = {'source': source, 'last': current, 'suffix': suffix}
    if current != entry['last']:
        return  # Preserve an editable name/label changed by its owner.
    translated = _translate(entry['source'], language) + entry.get('suffix', '')
    setattr(owner, attribute, translated)
    entry['last'] = getattr(owner, attribute)  # Blender may append a suffix.


def localize_tree(tree, language=None, _seen=None):
    """Translate recognized generated text without changing values or topology."""
    if language is None:
        from ..i18n import interface_language
        language = interface_language()
    if language not in ('en_US', 'zh_HANS'):
        raise ValueError('Unsupported QC node display language')
    if getattr(tree, 'library', None) is not None:
        return
    if _seen is None:
        _seen = set()
    identity = tree.as_pointer() if hasattr(tree, 'as_pointer') else id(tree)
    if identity in _seen:
        return
    _seen.add(identity)
    remember_sockets(tree)
    record = _record(tree)
    # Automatic Blender suffixes belong to the generated name, not its role.
    base = re.sub(r'\.\d{3}$', '', tree.name)
    if base in MESSAGES or base in _REVERSE:
        _managed(tree, 'name', 'tree', record, language, _canonical(base), tree.name[len(base):])
    for index, item in enumerate(tree.interface.items_tree):
        if item.item_type == 'SOCKET':
            source = socket_name(item, tree)
            _managed(item, 'name', 'socket:' + item.identifier, record, language, source)
        elif item.item_type == 'PANEL':
            key = 'panel:' + str(getattr(item, 'identifier', index))
            _managed(item, 'name', key, record, language)
    for node in tree.nodes:
        if node.type == 'FRAME' and _canonical(node.label) in MESSAGES:
            node['qc_frame_role'] = node.get('qc_frame_role', _canonical(node.label))
        if node.label:
            _managed(node, 'label', 'node:' + node.name, record, language)
        nested = getattr(node, 'node_tree', None)
        if nested is not None and nested.get('qc_asset_id'):
            localize_tree(nested, language, _seen)
    asset_data = getattr(tree, 'asset_data', None)
    if asset_data is not None:
        _managed(asset_data, 'description', 'description', record, language)
    record['language'] = language
    _save(tree, record)


def refresh_localization():
    """Refresh managed graphs; the caller owns the timer/handler lifecycle."""
    import bpy
    from ..i18n import interface_language
    language = interface_language()
    for tree in tuple(bpy.data.node_groups):
        if tree.get('qc_view_graph') or tree.get('qc_asset_id'):
            localize_tree(tree, language)
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            tree = getattr(modifier, 'node_group', None)
            if tree is not None and tree.get('qc_view_graph'):
                record = _record(tree)
                _managed(modifier, 'name', 'modifier', record, language)
                _save(tree, record)
    for material in bpy.data.materials:
        if material.use_nodes and any(node.get('qc_role') or node.get('qc_control')
                                      for node in material.node_tree.nodes):
            # Shader trees have no interface on older Blender versions.
            tree = material.node_tree
            if hasattr(tree, 'interface'):
                localize_tree(tree, language)
    from .asset_library import refresh_library_language
    refresh_library_language(language)


def frame_role(node):
    return node.get('qc_frame_role', _canonical(node.label))


def label_role(node):
    """A managed label's original role is independent of an owner rename."""
    tree = getattr(node, 'id_data', None)
    if tree is not None:
        entry = _record(tree)['display'].get('node:' + node.name)
        if entry is not None:
            return entry['source']
    return _canonical(node.label)


def adopt_generated_copy(tree):
    """Call only immediately after a copy made by the plugin itself.

    This accounts for Blender's automatic suffix at a known creation boundary;
    a copied owner-defined name remains owner-defined. Refresh never guesses.
    """
    record = _record(tree)
    entry = record['display'].get('tree')
    if entry is None:
        return
    base = re.sub(r'\.\d{3}$', '', tree.name)
    if base not in (entry['source'], MESSAGES.get(entry['source'])):
        return
    entry['last'] = tree.name
    entry['suffix'] = tree.name[len(base):]
    _save(tree, record)


def canonical_display(tree, key, current):
    """Normalize only a proven generated display edit for structural comparison.

    A user rename or forged/stale last value is retained in the signature.
    All graph attributes, defaults, identifiers, nodes and links still compare.
    """
    entry = _record(tree)['display'].get(key)
    if entry is None or current != entry['last']:
        return current
    source, suffix = entry['source'], entry.get('suffix', '')
    if source not in MESSAGES or current not in (source + suffix, MESSAGES[source] + suffix):
        return current
    return source + suffix


def socket_identity_signature(tree):
    """Normalize missing legacy identity records, but retain a corrupted map."""
    actual = {'INPUT': {}, 'OUTPUT': {}}
    for item in tree.interface.items_tree:
        if item.item_type == 'SOCKET':
            name = canonical_display(tree, 'socket:' + item.identifier, item.name)
            actual[item.in_out][name] = item.identifier
    stored_input = json.loads(tree.get('qc_sockets', '{}'))
    stored_output = _record(tree)['outputs']
    return (actual, stored_input if stored_input and stored_input != actual['INPUT'] else None,
            stored_output if stored_output and stored_output != actual['OUTPUT'] else None)
