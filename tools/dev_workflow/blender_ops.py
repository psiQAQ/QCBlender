"""Fixed Blender operations shared by the development CLI and existing MCP."""
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import time
import zipfile


READ_ACTIONS = {'identity', 'snapshot', 'assert'}
ACTIONS = READ_ACTIONS | {'import', 'annotation.add', 'annotation.edit',
                          'trajectory.set', 'render', 'save', 'install', 'quit'}


def _bpy():
    import bpy
    return bpy


def _package():
    names = [addon.module for addon in _bpy().context.preferences.addons
             if addon.module.startswith('bl_ext.') and addon.module.endswith('.qcblender')]
    if len(names) != 1:
        raise RuntimeError(f'Expected one enabled QCBlender extension, got {names}')
    return names[0]


def _module(name):
    return importlib.import_module(_package() + '.' + name)


def _finished(result):
    if result != {'FINISHED'}:
        raise RuntimeError(f'Blender operation did not finish: {result}')


def _identity():
    bpy = _bpy()
    packages = [addon.module for addon in bpy.context.preferences.addons
                if addon.module.startswith('bl_ext.') and addon.module.endswith('.qcblender')]
    return {'pid': os.getpid(), 'blender': bpy.app.version_string,
            'binary': bpy.app.binary_path, 'filepath': bpy.data.filepath,
            'dirty': bpy.data.is_dirty, 'packages': packages}


def _plain(value):
    if value is None or isinstance(value, (str, float, int, bool)):
        return value
    if isinstance(value, _bpy().types.ID):
        return {'type': value.bl_rna.identifier, 'identity': value.get('qc_asset_id', value.name)}
    if hasattr(value, 'items'):
        return {key: _plain(item) for key, item in value.items()}
    return [_plain(item) for item in value]


def _tree(tree):
    return {'nodes': [{'name': node.name, 'type': node.bl_idname,
                       'inputs': [(socket.identifier, _plain(socket.default_value))
                                  for socket in node.inputs if hasattr(socket, 'default_value')]}
                      for node in tree.nodes],
            'links': sorted((link.from_node.name, link.from_socket.identifier,
                             link.to_node.name, link.to_socket.identifier) for link in tree.links)}


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _snapshot():
    import numpy as np
    bpy = _bpy()
    objects, datasets, locations = {}, {}, {}
    for obj in bpy.data.objects:
        item = {'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
                'matrix': [list(row) for row in obj.matrix_world],
                'properties': {key: _plain(value) for key, value in obj.items() if key != 'qc_dataset'},
                'selected': obj.select_get(), 'hide_viewport': obj.hide_viewport,
                'hidden': obj.hide_get(), 'hide_render': obj.hide_render,
                'materials': [mat.name if mat else None for mat in obj.data.materials]
                             if obj.data and hasattr(obj.data, 'materials') else [],
                'modifiers': [{'type': mod.type, 'properties': _plain(dict(mod.items())),
                               'node_group': mod.node_group.name if mod.type == 'NODES' and mod.node_group else None}
                              for mod in obj.modifiers]}
        if obj.type == 'MESH':
            coordinates = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
            obj.data.vertices.foreach_get('co', coordinates)
            item.update(coordinates_sha256=_digest(coordinates.tobytes()), vertices=len(obj.data.vertices),
                        edges=[list(edge.vertices) for edge in obj.data.edges])
            item['attributes'] = {attr.name: {'domain': attr.domain, 'type': attr.data_type,
                'values': [_plain(getattr(value, 'value', getattr(value, 'vector', getattr(value, 'color', None))))
                           for value in attr.data]} for attr in obj.data.attributes if not attr.name.startswith('.')}
        elif obj.type == 'FONT':
            item.update(body=obj.data.body, size=obj.data.size, font=obj.data.font.name)
        elif obj.type == 'CURVE':
            item.update(bevel_depth=obj.data.bevel_depth,
                        splines=[{'type': spline.type, 'points': [list(point.co) for point in spline.points]}
                                 for spline in obj.data.splines])
        objects[obj.name] = item
        if obj.get('qc_dataset'):
            directory = Path(bpy.path.abspath(obj['qc_dataset'])).resolve(strict=True)
            locations[obj.name] = str(directory)
            data = _module('data').load_dataset(directory)
            datasets[obj.name] = {'metadata_sha256': _digest(json.dumps(data.metadata, sort_keys=True).encode()),
                'arrays': {key: {'shape': list(array.shape), 'dtype': array.dtype.str,
                                 'sha256': _digest(array.tobytes())} for key, array in data.arrays.items()}}
    groups = {}
    for tree in bpy.data.node_groups:
        groups[tree.name] = {**_tree(tree), 'asset_id': tree.get('qc_asset_id'),
            'interface': [(item.identifier, item.in_out, item.socket_type,
                           _plain(getattr(item, 'default_value', None)))
                          for item in tree.interface.items_tree if item.item_type == 'SOCKET']}
    view = bpy.context.preferences.view
    active = bpy.context.view_layer.objects.active
    return {'identity': {**_identity(), 'datasets': locations}, 'state': {
        'active': active.name if active else None, 'frame': bpy.context.scene.frame_current,
        'objects': objects, 'datasets': datasets, 'groups': groups,
        'materials': {mat.name: {'color': list(mat.diffuse_color), 'use_nodes': mat.use_nodes,
                                'fake_user': mat.use_fake_user,
                                'tree': _tree(mat.node_tree) if mat.node_tree else None}
                      for mat in bpy.data.materials},
        'fonts': {font.name: {'packed_sha256': _digest(bytes(font.packed_file.data)) if font.packed_file else None}
                  for font in bpy.data.fonts},
        'preferences': {'language': view.language, 'translate_interface': view.use_translate_interface,
                        'translate_tooltips': view.use_translate_tooltips},
        'screens': {screen.name: [(area.type, area.ui_type, area.width, area.height) for area in screen.areas]
                    for screen in bpy.data.screens}}}


def _object(name):
    obj = _bpy().data.objects[name]
    _module('blender.layers').activate(_bpy().context, obj)
    return obj


def _import(args):
    source = Path(args['source']).resolve(strict=True)
    job = _module('blender.jobs').Job('import', source=str(source), job_index=args.get('job_index', 0))
    deadline = time.monotonic() + args.get('timeout', 180)
    while time.monotonic() < deadline:
        report = job.poll()
        if report is not None:
            if report['status'] != 'succeeded':
                raise RuntimeError(f'Scientific import failed: {report}')
            break
        time.sleep(.1)
    else:
        cancellation = job.cancel()
        raise TimeoutError(f'Scientific import timed out; cancellation: {cancellation}')
    directory = job.directory / 'dataset'
    data = _module('data').load_dataset(directory)
    for field in data.metadata.get('fields', []):
        _module('blender.native_volume').check_field_cache(directory, field)
    obj = _module('blender.views').atom_view(directory)
    _module('blender.trajectory').initialize_trajectory(obj, data)
    if args.get('name'):
        obj.name = args['name']
    fields = [_module('blender.views').field_view(directory, obj, index).name
              for index in range(len(data.metadata.get('fields', [])))]
    return {'object': obj.name, 'fields': fields, 'dataset': str(directory), 'worker': report}


def _annotation(action, args):
    obj = _object(args['object'])
    properties = dict(args['properties'])
    if action == 'annotation.edit':
        entry = next(json.loads(child['qc_annotation']) for child in obj.children
                     if child.type == 'FONT' and child.get('qc_annotation')
                     and json.loads(child['qc_annotation'])['id'] == properties['annotation_id'])
        properties = {**{key: entry.get(key, _module('blender.annotations').STYLE_DEFAULTS.get(key))
                         for key in ('size', 'offset', 'decimals', 'show_leader', 'line_width', 'visible',
                                     *_module('blender.annotations').STYLE_DEFAULTS)}, **properties}
    operator = _bpy().ops.qcblender.add_annotation if action == 'annotation.add' else _bpy().ops.qcblender.edit_annotation
    _finished(operator('EXEC_DEFAULT', **properties))
    _bpy().context.view_layer.update()
    return {'object': obj.name, 'annotations': [json.loads(child['qc_annotation']) for child in obj.children
                                               if child.type == 'FONT' and child.get('qc_annotation')]}


def _install(args):
    path = Path(args['filepath']).resolve(strict=True)
    with zipfile.ZipFile(path) as archive:
        files = [name for name in archive.namelist() if not name.endswith('/')]
        manifests = [name for name in files if PurePosixPath(name).name == 'blender_manifest.toml']
        if len(manifests) != 1:
            raise ValueError('Candidate must contain one extension manifest')
        prefix = manifests[0][:-len('blender_manifest.toml')]
        if any(not name.startswith(prefix) or '..' in PurePosixPath(name).parts
               or PurePosixPath(name).is_absolute() for name in files):
            raise ValueError('Candidate contains an invalid extension member path')
        _finished(_bpy().ops.extensions.package_install_files(filepath=str(path), repo=args.get('repo', 'user_default'),
                                                            enable_on_install=True, overwrite=True))
        module = importlib.import_module(_package())
        directory = Path(module.__file__).resolve().parent
        for name in files:
            if (directory / name[len(prefix):]).read_bytes() != archive.read(name):
                raise RuntimeError(f'Installed extension differs from candidate: {name}')
    _finished(_bpy().ops.wm.save_userpref())
    return {'package': module.__name__, 'directory': str(directory), 'files': len(files),
            'candidate_sha256': _digest(path.read_bytes())}


def _assert(args):
    if 'expected' in args:
        expected = args['expected']
        actual = _snapshot()
        # JSON roundtrip also normalizes tuples from RNA to saved JSON lists.
        if json.loads(json.dumps(expected['state'])) != json.loads(json.dumps(actual['state'])):
            raise AssertionError('Scene snapshot differs from the expected state')
        return {'snapshot_matches': True}
    bpy = _bpy()
    owner = bpy.data.objects[args['object']]
    labels = [child for child in owner.children if child.type == 'FONT' and child.get('qc_annotation')]
    entries = [json.loads(label['qc_annotation']) for label in labels]
    if 'annotation_count' in args and len(labels) != args['annotation_count']:
        raise AssertionError(f'Expected {args["annotation_count"]} annotations, got {len(labels)}')
    if 'kinds' in args and sorted(entry['kind'] for entry in entries) != sorted(args['kinds']):
        raise AssertionError('Annotation kinds differ')
    if args.get('faces_camera'):
        if bpy.context.scene.camera is None:
            raise AssertionError('Scene has no camera')
        bpy.context.view_layer.update()
        camera = bpy.context.scene.camera.matrix_world.to_quaternion()
        if any(label.matrix_world.to_quaternion().rotation_difference(camera).angle > 1e-5 for label in labels):
            raise AssertionError('Annotation does not face the camera')
    checked_arcs = 0
    if args.get('arc_midpoints'):
        import math
        import numpy as np
        positions, _ = _module('blender.geometry').current_geometry(owner)
        for entry in entries:
            if entry['kind'] not in ('ANGLE', 'DIHEDRAL') or entry.get('undefined_reason'):
                continue
            points = positions[np.asarray(entry['source_atom_numbers']) - 1]
            first = points[0] - points[1]
            if entry['kind'] == 'ANGLE':
                last = points[2] - points[1]
                first, last = first / np.linalg.norm(first), last / np.linalg.norm(last)
                normal = np.cross(first, last)
                sine = np.linalg.norm(normal)
                if sine <= 1e-10:
                    raise AssertionError('Use a non-collinear angle for the independent midpoint check')
                normal /= sine
                angle, center = math.atan2(sine, np.dot(first, last)), points[1]
            else:
                normal = points[2] - points[1]
                normal /= np.linalg.norm(normal)
                last = points[3] - points[2]
                first -= np.dot(first, normal) * normal
                last -= np.dot(last, normal) * normal
                first, last = first / np.linalg.norm(first), last / np.linalg.norm(last)
                angle = math.atan2(np.dot(normal, np.cross(first, last)), np.dot(first, last))
                if angle <= -math.pi:
                    angle = math.pi
                center = (points[1] + points[2]) / 2
            expected = center + entry['arc_radius'] * (math.cos(angle / 2) * first
                                                       + math.sin(angle / 2) * np.cross(normal, first))
            parts = {json.loads(child['qc_annotation'])['role']: child for child in owner.children
                     if child.get('qc_annotation') and json.loads(child['qc_annotation'])['id'] == entry['id']}
            arc = parts['ARC'].data.splines[0].points
            np.testing.assert_allclose(arc[len(arc) // 2].co[:3], expected, rtol=0, atol=2e-6)
            np.testing.assert_allclose(parts['LEADER'].data.splines[0].points[0].co[:3], expected, rtol=0, atol=2e-6)
            checked_arcs += 1
        if not checked_arcs:
            raise AssertionError('No defined angle or dihedral arc to check')
    return {'object': owner.name, 'annotation_count': len(labels), 'kinds': [entry['kind'] for entry in entries],
            'arc_midpoints_checked': checked_arcs}


def dispatch(request: dict) -> dict:
    """Execute a named operation; writes require the current process's exact PID."""
    action = request['action']
    if action not in ACTIONS:
        raise ValueError(f'Unsupported Blender action: {action}')
    expected = request.get('expected_pid')
    if action not in READ_ACTIONS or expected is not None:
        if type(expected) is not int or expected != os.getpid():
            raise ValueError(f'Blender PID mismatch: expected {expected}, actual {os.getpid()}')
    args = request.get('args', {})
    if action == 'identity':
        result = _identity()
    elif action == 'snapshot':
        result = _snapshot()
    elif action == 'import':
        result = _import(args)
    elif action.startswith('annotation.'):
        result = _annotation(action, args)
    elif action == 'trajectory.set':
        obj = _object(args['object'])
        data = _module('data').load_dataset(_bpy().path.abspath(obj['qc_dataset']))
        _module('blender.trajectory').set_frame(obj, data, args['frame'])
        _bpy().context.view_layer.update()
        result = {'object': obj.name, 'frame': obj['qc_trajectory_frame']}
    elif action == 'render':
        scene = _bpy().context.scene
        path = Path(args['filepath']).resolve()
        if path.suffix.lower() != '.png':
            raise ValueError('Render filepath must have a .png extension')
        path.parent.mkdir(parents=True, exist_ok=True)
        for key in ('resolution_x', 'resolution_y', 'resolution_percentage', 'engine'):
            if key in args:
                setattr(scene.render, key, args[key])
        if 'samples' in args:
            scene.cycles.samples = args['samples']
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = 'PNG'
        _finished(_bpy().ops.render.render(write_still=True))
        result = {'filepath': str(path), 'sha256': _digest(path.read_bytes())}
    elif action == 'save':
        path = _module('blender.project').save_project(args['filepath'])
        result = {'filepath': str(path), 'qcdata': str(path.with_suffix('.qcdata'))}
    elif action == 'assert':
        result = _assert(args)
    elif action == 'install':
        result = _install(args)
    else:
        bpy = _bpy()
        if not bpy.data.filepath or bpy.data.is_dirty or not Path(bpy.data.filepath).is_file():
            raise RuntimeError('Save the project before quitting Blender')
        # Return the response before the main loop performs normal shutdown.
        def quit_saved():
            if bpy.data.is_dirty:
                raise RuntimeError('Project changed before scheduled quit')
            _finished(bpy.ops.wm.quit_blender())
            return None
        bpy.app.timers.register(quit_saved, first_interval=.2)
        result = {'quit_scheduled': True, 'filepath': bpy.data.filepath}
    return {'status': 'Passed', 'action': action, 'pid': os.getpid(), 'result': result}
