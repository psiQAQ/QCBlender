"""Snapshot or compare a saved SOP project in Blender, including portable resources.

CLI: blender project.blend --background --python this_file -- snapshot --report new.json
     blender moved.blend --background --python this_file -- compare --expected old.json --report new.json
MCP/runpy callers may call capture_project() and compare_snapshots() directly.
This does not save, install, launch Blender, or contact the original calculation files.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys


SCHEMA = 'qcblender.sop-project.v1'
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from qcblender.data import filesystem_path, unprefixed_path


def digest(path):
    with filesystem_path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def resolved_path(path):
    """Resolve with the Windows I/O prefix, then use ordinary syntax for identity."""
    return unprefixed_path(filesystem_path(path).resolve(strict=True))


def project_reference(path, root):
    """Normalize a real runtime reference, never arbitrary source/provenance strings."""
    path, root = resolved_path(path), resolved_path(root)
    if not path.is_relative_to(root):
        raise ValueError(f'Runtime resource outside saved project: {path}')
    return path.relative_to(root).as_posix()


def canonical_snapshot(raw, bindings, resources, persistent):
    state = deepcopy(raw['state'])
    state.pop('screens', None)
    state.pop('active', None)
    for obj in state['objects'].values():
        obj.pop('selected', None)
        for modifier in obj.get('modifiers', []):
            if modifier.get('type') != 'NODES':
                continue
            properties = modifier['properties']
            for key, value in properties.items():
                if key.endswith('_use_attribute') and key.removesuffix('_use_attribute') in properties:
                    # Blender 5.1 reads saved bool ID properties back as integer flags.
                    if type(value) not in (bool, int) or value not in (0, 1):
                        raise ValueError(f'Invalid node attribute flag: {key}: {value!r}')
                    properties[key] = bool(value)
    state.update(bindings=bindings, resources=resources, persistent=persistent)
    # JSON is also the on-disk representation; normalize RNA tuples to lists.
    return {'schema': SCHEMA, 'state': json.loads(json.dumps(state, allow_nan=False))}


def differences(expected, actual, path='state'):
    """Return exact leaf changes, without tolerances or ignored scientific fields."""
    if type(expected) is not type(actual):
        return [path]
    if isinstance(expected, dict):
        result = []
        for key in sorted(expected.keys() | actual.keys()):
            child = f'{path}.{key}'
            result.extend([child] if key not in expected or key not in actual else
                          differences(expected[key], actual[key], child))
        return result
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return [path + '.length']
        return [change for index, (left, right) in enumerate(zip(expected, actual))
                for change in differences(left, right, f'{path}[{index}]')]
    return [] if expected == actual else [path]


def compare_snapshots(expected, actual):
    if expected.get('schema') != SCHEMA or actual.get('schema') != SCHEMA:
        raise ValueError('Unsupported SOP project snapshot schema')
    changed = differences(expected['state'], actual['state'])
    return {'status': 'Failed' if changed else 'Passed', 'differences': changed}


def _rna_json_value(value, property_path):
    """Retain signed RNA infinities (e.g. empty-curve bounds), never erase them."""
    if isinstance(value, float):
        if math.isnan(value):
            raise ValueError(f'NaN RNA property: {property_path}')
        if math.isinf(value):
            return {'$qcblender.rna_float': '-Infinity' if value < 0 else '+Infinity'}
    if isinstance(value, (list, tuple)):
        return [_rna_json_value(item, f'{property_path}[{index}]') for index, item in enumerate(value)]
    if isinstance(value, dict):
        return {key: _rna_json_value(item, f'{property_path}.{key}') for key, item in value.items()}
    return value


def _rna(value, plain, excluded=()):
    result = {}
    for prop in value.bl_rna.properties:
        key = prop.identifier
        if prop.is_readonly or key in excluded or prop.type == 'COLLECTION':
            continue
        item = getattr(value, key)
        if prop.type == 'POINTER':
            if item is None or not hasattr(item, 'name'):
                continue
        result[key] = _rna_json_value(sorted(item) if isinstance(item, set) else plain(item), key)
    return result


def _used_snapshot(ops, bpy, objects, trees, materials, fonts):
    # Scope the existing collector to actual Blender datablocks. Unused orphan
    # datasets must not be loaded merely because they remain in bpy.data.
    class View:
        def __init__(self, original, **overrides):
            self.original, self.overrides = original, overrides

        def __getattr__(self, name):
            return self.overrides[name] if name in self.overrides else getattr(self.original, name)

    scoped = View(bpy, data=View(bpy.data, objects=list(objects.values()),
        node_groups=[tree for tree in trees.values() if tree.bl_idname == 'GeometryNodeTree'],
        materials=list(materials.values()), fonts=[bpy.data.fonts[name] for name in fonts]))
    original = ops._bpy
    try:
        ops._bpy = lambda: scoped
        return ops._snapshot()
    finally:
        ops._bpy = original


def capture_project():
    """Check the current saved project and capture only persistent used data.

    Native VDB checks create and release an unlinked temporary Volume; they do
    not save changes. Source paths inside dataset metadata remain provenance;
    manifests and arrays retain their exact hashes and are never rewritten.
    """
    import bpy
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.dev_workflow import blender_ops as ops
    storage = ops._module('data')
    native = ops._module('blender.native_volume')
    project = resolved_path(bpy.data.filepath)
    if project.suffix.lower() != '.blend':
        raise ValueError('Open a saved .blend project before checking')
    root, data_root = project.parent, project.with_suffix('.qcdata')
    bindings, resources = {}, {}

    def file_record(path):
        relative = project_reference(path, root)
        path = filesystem_path(root / relative)
        if not path.is_file():
            raise ValueError(f'Runtime resource is not a file: {path}')
        resources[relative] = {'bytes': path.stat().st_size, 'sha256': digest(path)}
        return relative

    def datablock_file(block):
        packed = getattr(block, 'packed_file', None)
        if packed is not None:
            return {'packed_sha256': hashlib.sha256(bytes(packed.data)).hexdigest()}
        path = getattr(block, 'filepath', '')
        if path == '<builtin>':
            return {'builtin': path}
        if not path:
            raise ValueError(f'Used resource has no file or packed data: {block.name}')
        return {'path': file_record(bpy.path.abspath(path, library=block.library))}

    objects = {obj.name: obj for scene in bpy.data.scenes for obj in scene.objects}
    indexed = set()
    for obj in objects.values():
        if not obj.get('qc_dataset'):
            continue
        directory = resolved_path(bpy.path.abspath(obj['qc_dataset']))
        if not directory.is_relative_to(resolved_path(data_root)):
            raise ValueError(f'Dataset outside matching .qcdata: {obj.name}: {directory}')
        manifest = directory / 'manifest.json'
        if digest(manifest) != obj['qc_dataset_sha256']:
            raise ValueError(f'Dataset manifest differs from object binding: {obj.name}')
        bindings[obj.name] = project_reference(directory, root)
        indexed.add(directory.relative_to(resolved_path(data_root)).as_posix())
        data = storage.load_dataset(directory)
        ops._module('blender.source_browser').cache_dataset(obj, data)
        file_record(manifest)
        manifest_data = json.loads(filesystem_path(manifest).read_text(encoding='utf-8'))
        for record in manifest_data['arrays'].values():
            file_record(storage.resolve_asset(directory, record['path']))
        for scalar in data.metadata.get('fields', []):
            file_record(native.check_field_cache(directory, scalar))
    scene_index = data_root / 'manifest.json'
    index = json.loads(filesystem_path(scene_index).read_text(encoding='utf-8'))
    if (index.get('format') != 'qcblender.scene' or index.get('schema') != '0.1'
            or set(index.get('datasets', [])) != indexed):
        raise ValueError('Scene dataset index differs from the bound saved datasets')
    file_record(scene_index)

    plain = ops._plain
    persistent = {'objects': {}, 'trees': {}, 'materials': {}, 'fonts': {},
                  'images': {}, 'volumes': {}, 'libraries': {}, 'scenes': {}}
    trees, materials, libraries = {}, {}, {}

    def library(block):
        if block.library:
            lib = block.library
            libraries[lib.name] = lib

    def tree_record(tree):
        if tree is None or tree.name in trees:
            return
        trees[tree.name] = tree
        library(tree)
        for socket in tree.interface.items_tree if hasattr(tree, 'interface') else ():
            value = getattr(socket, 'default_value', None)
            if isinstance(value, bpy.types.Material):
                materials[value.name] = value
        nodes = {}
        for node in tree.nodes:
            record = _rna(node, plain, ('location', 'width', 'height', 'select', 'show_options',
                'show_preview', 'show_texture', 'hide', 'use_custom_color', 'color', 'label', 'parent'))
            if hasattr(node, 'color_ramp'):
                ramp = node.color_ramp
                record['color_ramp'] = {'interpolation': ramp.interpolation,
                    'color_mode': ramp.color_mode, 'hue_interpolation': ramp.hue_interpolation,
                    'elements': [[item.position, list(item.color)] for item in ramp.elements]}
            if getattr(node, 'node_tree', None):
                tree_record(node.node_tree)
            for socket in node.inputs:
                value = getattr(socket, 'default_value', None)
                if isinstance(value, bpy.types.Material):
                    materials[value.name] = value
            image = getattr(node, 'image', None)
            if image is not None:
                if image.source == 'GENERATED' and not image.packed_file:
                    from array import array
                    persistent['images'][image.name] = {'generated_size': list(image.size),
                        'pixels_sha256': hashlib.sha256(array('f', image.pixels[:]).tobytes()).hexdigest()}
                else:
                    persistent['images'][image.name] = datablock_file(image)
                library(image)
            nodes[node.name] = record
        persistent['trees'][tree.name] = {'nodes': nodes, 'custom': plain(dict(tree.items())),
            'tree': ops._tree(tree), 'interface': [
                [item.identifier, item.in_out, item.socket_type,
                 plain(getattr(item, 'default_value', None))]
                for item in tree.interface.items_tree if item.item_type == 'SOCKET']}

    for obj in objects.values():
        library(obj)
        record = {}
        if hasattr(obj, 'qc_settings'):
            record['qc_settings'] = _rna(obj.qc_settings, plain)
        if hasattr(obj, 'qc_result_browser'):
            record['qc_result_browser'] = _rna(obj.qc_result_browser, plain)
        if obj.type == 'MESH':
            record['polygons'] = [list(face.vertices) for face in obj.data.polygons]
        if obj.type in ('FONT', 'CURVE', 'CAMERA', 'LIGHT'):
            record['data'] = _rna(obj.data, plain, ('name',))
            if hasattr(obj.data, 'dof'):
                record['depth_of_field'] = _rna(obj.data.dof, plain)
        if obj.type == 'FONT':
            for key in ('font', 'font_bold', 'font_italic', 'font_bold_italic'):
                font = getattr(obj.data, key)
                if font is not None:
                    persistent['fonts'][font.name] = datablock_file(font)
                    library(font)
        if obj.type == 'VOLUME':
            volume = obj.data
            native.check_volume(bpy.path.abspath(volume.filepath, library=volume.library))
            persistent['volumes'][volume.name] = {'resource': datablock_file(volume),
                                                 'display': _rna(volume.display, plain)}
        if obj.data:
            library(obj.data)
            for material in obj.data.materials if hasattr(obj.data, 'materials') else ():
                if material:
                    materials[material.name] = material
        for modifier in obj.modifiers:
            if modifier.type == 'NODES':
                tree_record(modifier.node_group)
                for value in modifier.values():
                    if isinstance(value, bpy.types.Material):
                        materials[value.name] = value
        persistent['objects'][obj.name] = record
    for scene in bpy.data.scenes:
        persistent['scenes'][scene.name] = {'camera': plain(scene.camera),
            'render': _rna(scene.render, plain, ('filepath', 'bake')),
            'frame': scene.frame_current,
            'world': _rna(scene.world, plain) if scene.world else None}
        if hasattr(scene, 'cycles'):
            persistent['scenes'][scene.name]['cycles'] = _rna(scene.cycles, plain)
        if scene.world:
            tree_record(scene.world.node_tree)
            library(scene.world)
        tree_record(scene.compositing_node_group)
    pending = set(materials)
    while pending:
        for name in sorted(pending):
            material = materials[name]
            library(material)
            persistent['materials'][name] = _rna(material, plain, ('name',))
            tree_record(material.node_tree)
        pending = materials.keys() - persistent['materials'].keys()
    for lib in libraries.values():
        persistent['libraries'][lib.name] = datablock_file(lib)
    raw = _used_snapshot(ops, bpy, objects, trees, materials, persistent['fonts'])
    result = canonical_snapshot(raw, bindings, resources, persistent)
    result['project'] = str(project)
    result['execution'] = {'pid': ops._identity()['pid'], 'blender': bpy.app.version_string,
                           'source_metadata_paths': 'provenance only; exact metadata hashes retained'}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('snapshot', 'compare'))
    parser.add_argument('--expected', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(argv)
    if filesystem_path(args.report).exists():
        raise FileExistsError(f'Choose a new report path: {args.report}')
    report = {'status': 'Failed', 'action': args.action}
    try:
        actual = capture_project()
        report['snapshot'] = actual
        if args.action == 'compare':
            if not args.expected:
                raise ValueError('compare requires --expected')
            expected = json.loads(filesystem_path(args.expected).read_text(encoding='utf-8'))
            report.update(compare_snapshots(expected.get('snapshot', expected), actual))
        else:
            report['status'] = 'Passed'
    except (OSError, ValueError, KeyError, RuntimeError, TypeError) as error:
        report['error'] = f'{type(error).__name__}: {error}'
    filesystem_path(args.report.parent).mkdir(parents=True, exist_ok=True)
    filesystem_path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                           encoding='utf-8', newline='\n')
    print(json.dumps({'status': report['status'], 'report': str(args.report),
                      'differences': report.get('differences', []), 'error': report.get('error')}, ensure_ascii=False))
    return report


if __name__ == '__main__':
    arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    raise SystemExit(main(arguments)['status'] != 'Passed')
