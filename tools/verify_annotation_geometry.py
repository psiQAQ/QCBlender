"""Verify installed annotation geometry in an isolated Blender background process.

Fresh run: blender --background --factory-startup --python-exit-code 1
  --python tools/verify_annotation_geometry.py -- --output ABSOLUTE_DIRECTORY
  --dataset ABSOLUTE_MANIFEST_JSON
Cold read: blender --background ABSOLUTE_DIRECTORY/annotations.blend
  --python-exit-code 1 --python tools/verify_annotation_geometry.py --
  --output ABSOLUTE_DIRECTORY --reopen

Uses real bpy objects and installed extension modules. Geometry expectations are
calculated here from source positions, without importing measurement helpers.
GUI interaction, rendering, Undo/Redo and trajectory switching are separate runs.
"""
import argparse
import hashlib
import importlib
from itertools import permutations
import json
import math
from pathlib import Path
import sys
import traceback

MODULE = 'bl_ext.user_default.qcblender'
SCENE_KEY = 'qc_annotation_geometry_verification'
EXPECTED_ROLES = {
    'ATOM': {'LABEL', 'LEADER'},
    'DISTANCE': {'LABEL', 'LEADER', 'DASH'},
    'ANGLE': {'LABEL', 'LEADER', 'ARC'},
    'DIHEDRAL': {'LABEL', 'LEADER', 'ARC', 'PLANE_A', 'PLANE_B'},
}
STYLE_FIELDS = ('size', 'offset', 'decimals', 'show_leader', 'line_width', 'visible',
                'prefix_mode', 'prefix', 'show_measurement', 'measurement_width',
                'arc_radius', 'show_planes')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def groups(owner):
    result = {}
    for child in owner.children:
        if 'qc_annotation' not in child:
            continue
        entry = json.loads(child['qc_annotation'])
        members = result.setdefault(entry['id'], {})
        require(entry['role'] not in members, 'Duplicate annotation role')
        members[entry['role']] = (child, entry)
    return result


def activate(owner):
    import bpy
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    owner.hide_set(False)
    owner.select_set(True)
    bpy.context.view_layer.objects.active = owner


def science(owner):
    import bpy
    data = module('data').load_dataset(bpy.path.abspath(owner['qc_dataset']))
    return {name: {'shape': list(array.shape), 'dtype': str(array.dtype),
                   'sha256': hashlib.sha256(array.tobytes()).hexdigest()}
            for name, array in sorted(data.arrays.items())}


def independent_value(kind, points):
    """Source-coordinate definition, independent of the extension implementation."""
    import numpy as np
    if kind == 'DISTANCE':
        return float(np.linalg.norm(points[1] - points[0]))
    if kind == 'ANGLE':
        first, last = points[0] - points[1], points[2] - points[1]
        cosine = float(np.dot(first, last) / (np.linalg.norm(first) * np.linalg.norm(last)))
        return math.degrees(math.acos(max(-1., min(1., cosine))))
    axis = points[2] - points[1]
    axis = axis / np.linalg.norm(axis)
    first, last = points[0] - points[1], points[3] - points[2]
    first = first - np.dot(first, axis) * axis
    last = last - np.dot(last, axis) * axis
    require(min(np.linalg.norm(first), np.linalg.norm(last)) > 1e-9,
            'Dataset cannot define the chosen dihedral')
    value = math.degrees(math.atan2(float(np.dot(axis, np.cross(first, last))),
                                    float(np.dot(first, last))))
    return 180. if value <= -180. else value


def select_numbers(positions):
    import numpy as np
    require(len(positions) >= 4, 'Use a dataset with at least four source atoms')
    ids = range(min(12, len(positions)))
    distance = max(permutations(ids, 2), key=lambda pair: np.linalg.norm(positions[pair[1]] - positions[pair[0]]))
    angle = None
    dihedral = None
    for ordered in permutations(ids, 4):
        points = positions[list(ordered)]
        first, axis, last = points[0] - points[1], points[2] - points[1], points[3] - points[2]
        if min(np.linalg.norm(first), np.linalg.norm(axis), np.linalg.norm(last)) < 1e-8:
            continue
        if min(np.linalg.norm(np.cross(first, axis)), np.linalg.norm(np.cross(last, axis))) < 1e-8:
            continue
        angle = ordered[:3]
        dihedral = ordered
        if abs(math.sin(math.radians(independent_value('DIHEDRAL', points)))) > .1:
            break
    require(angle is not None and dihedral is not None, 'Use a dataset with a defined four-atom dihedral')
    return {kind: [index + 1 for index in ordered]
            for kind, ordered in {'ATOM': (0,), 'DISTANCE': distance, 'ANGLE': angle, 'DIHEDRAL': dihedral}.items()}


def spline_points(obj):
    import numpy as np
    return [np.array([point.co[:3] for point in spline.points]) for spline in obj.data.splines]


def shader_socket(shader, name):
    # Native identifiers stay canonical even when Blender displays translated names.
    return next(item for item in shader.inputs if item.identifier == name)


def initial_material_checks(owner):
    import numpy as np
    core_materials = []
    for members in groups(owner).values():
        label, entry = members['LABEL']
        require(entry['decimals'] == (4 if entry['kind'] in ('ATOM', 'DISTANCE') else 2),
                'Unexpected default decimal precision')
        core = label.data.materials[0]
        core_materials.append(core.as_pointer())
        require(core.name.startswith('QC annotation material'), 'Unexpected initial material identity')
        for role, (part, _) in members.items():
            if role.startswith('PLANE_'):
                continue
            require(len(part.data.materials) == 1 and part.data.materials[0] == core,
                    'Parts of one annotation must share its core material')
        shader = next(node for node in core.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
        np.testing.assert_allclose(shader_socket(shader, 'Base Color').default_value, (0, 0, 0, 1), atol=1e-7)
        require(shader_socket(shader, 'Metallic').default_value == 1, 'Default core Metallic must be one')
        if entry['kind'] == 'DIHEDRAL':
            plane = members['PLANE_A'][0].data.materials[0]
            require(plane == members['PLANE_B'][0].data.materials[0] and plane != core,
                    'Dihedral planes need another shared material')
            shader = next(node for node in plane.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
            np.testing.assert_allclose(shader_socket(shader, 'Base Color').default_value,
                                       (0, 0, 0, .2), atol=1e-7)
            np.testing.assert_allclose(shader_socket(shader, 'Alpha').default_value, .2, atol=1e-7)
            require(shader_socket(shader, 'Metallic').default_value == 0, 'Plane Metallic must be zero')
    require(len(set(core_materials)) == len(core_materials), 'Different annotations must have independent materials')


def verify_geometry(owner):
    import numpy as np
    positions, provenance = module('blender.geometry').current_geometry(owner)
    checked = []
    for identifier, members in groups(owner).items():
        label, entry = members['LABEL']
        kind, numbers = entry['kind'], entry['source_atom_numbers']
        require(set(members) == EXPECTED_ROLES[kind], 'Wrong native part roles for ' + kind)
        points = positions[np.asarray(numbers) - 1]
        anchor = points.mean(axis=0)
        np.testing.assert_allclose(label.location, anchor + entry['offset'], atol=3e-6)
        require(entry['geometry'] == provenance, 'Label lost its source-conformation provenance')
        for role, (part, record) in members.items():
            require(part.parent == owner and record['geometry'] == provenance, 'Part attached to wrong atom view')
            require(part.data.users == 1, 'Annotation native data must be independent')
            expected = 'FONT' if role == 'LABEL' else 'MESH' if role.startswith('PLANE_') else 'CURVE'
            require(part.type == expected, 'Wrong native Blender data type')
        leader = members['LEADER'][0]
        np.testing.assert_allclose(spline_points(leader)[0][-1], label.location, atol=3e-6)
        if kind not in ('ANGLE', 'DIHEDRAL'):
            np.testing.assert_allclose(spline_points(leader)[0][0], anchor, atol=3e-6)
        np.testing.assert_allclose(leader.data.bevel_depth, entry['line_width'] / 2, atol=1e-8)
        if kind == 'ATOM':
            tail = entry['symbols'][0]
        else:
            value = independent_value(kind, points)
            np.testing.assert_allclose(entry['value'], value, atol=1e-9, rtol=0)
            tail = f"{value:.{entry['decimals']}f} {'Å' if kind == 'DISTANCE' else '°'}"
        prefix = entry['prefix'] if entry['prefix_mode'] == 'CUSTOM' else (
            '' if kind == 'ATOM' else f"{kind.title()}({','.join(map(str, numbers))}) = ")
        expected_bodies = {prefix + tail}
        if kind != 'ATOM' and abs(value) < .5 * 10 ** -entry['decimals']:
            # Numerically planar coordinates can produce either signed zero;
            # the sign of an unresolvable zero is not a different measurement.
            unit = 'Å' if kind == 'DISTANCE' else '°'
            expected_bodies.update(prefix + f"{zero:.{entry['decimals']}f} {unit}" for zero in (0., -0.))
        require(label.data.body in expected_bodies, 'Wrong prefix, scientific number or unit')
        if kind == 'DISTANCE':
            dashed = members['DASH'][0]
            paths = spline_points(dashed)
            require(paths and all(path.shape == (2, 3) for path in paths), 'Distance needs native two-point dashes')
            endpoints = np.concatenate(paths)
            first, last = points
            np.testing.assert_allclose(endpoints[[0, -1]], [first, last], atol=3e-6)
            unit = (last - first) / np.linalg.norm(last - first)
            distances = (endpoints - first) @ unit
            np.testing.assert_allclose(endpoints, first + distances[:, None] * unit, atol=3e-6)
            np.testing.assert_allclose(np.diff(distances), np.linalg.norm(last - first) / (len(endpoints) - 1), atol=3e-6)
            np.testing.assert_allclose(endpoints, first + last - endpoints[::-1], atol=3e-6)
            np.testing.assert_allclose(dashed.data.bevel_depth, entry['measurement_width'] / 2, atol=1e-8)
        if kind in ('ANGLE', 'DIHEDRAL'):
            arc = members['ARC'][0]
            paths = spline_points(arc)
            if abs(value) < 1e-10:
                require(not paths and arc.hide_viewport and arc.hide_render, 'Zero arc must be hidden')
                np.testing.assert_allclose(spline_points(leader)[0][0], anchor, atol=3e-6)
            else:
                require(len(paths) == 1, 'Angle needs exactly one circular arc')
                vertices = paths[0]
                center = points[1] if kind == 'ANGLE' else (points[1] + points[2]) / 2
                first = points[0] - points[1]
                last = points[2] - points[1] if kind == 'ANGLE' else points[3] - points[2]
                if kind == 'DIHEDRAL':
                    normal = points[2] - points[1]
                    normal /= np.linalg.norm(normal)
                    first -= np.dot(first, normal) * normal
                    last -= np.dot(last, normal) * normal
                else:
                    normal = np.cross(first, last)
                    normal /= np.linalg.norm(normal)
                first /= np.linalg.norm(first)
                last /= np.linalg.norm(last)
                vectors = vertices - center
                np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), entry['arc_radius'], atol=3e-6)
                np.testing.assert_allclose(vectors @ normal, 0, atol=3e-6)
                np.testing.assert_allclose(vertices[[0, -1]], center + entry['arc_radius'] * np.array([first, last]), atol=3e-6)
                angles = np.unwrap(np.arctan2(np.cross(first, vectors) @ normal, vectors @ first))
                np.testing.assert_allclose(angles[-1], math.radians(value), atol=3e-6)
                require(len(vertices) % 2 == 1, 'Arc must contain its exact midpoint vertex')
                np.testing.assert_allclose(angles[len(vertices)//2], math.radians(value) / 2, atol=3e-6)
                np.testing.assert_allclose(spline_points(leader)[0][0], vertices[len(vertices)//2], atol=3e-6)
                require(np.all(np.diff(angles) * value >= -1e-7), 'Arc turns against the scientific signed angle')
            np.testing.assert_allclose(arc.data.bevel_depth, entry['measurement_width'] / 2, atol=1e-8)
        if kind == 'DIHEDRAL':
            for role, indexes in (('PLANE_A', [0, 1, 2]), ('PLANE_B', [1, 2, 3])):
                mesh = members[role][0].data
                require(len(mesh.vertices) == 3 and len(mesh.polygons) == 1, 'Dihedral plane is not one real triangle')
                require(tuple(mesh.polygons[0].vertices) == (0, 1, 2), 'Triangle connectivity differs')
                np.testing.assert_allclose([vertex.co[:] for vertex in mesh.vertices], points[indexes], atol=3e-6)
        checked.append({'id': identifier, 'kind': kind, 'source_atom_numbers': numbers, 'body': label.data.body})
    return checked


def edit(owner, identifier, **changes):
    import bpy
    activate(owner)
    entry = groups(owner)[identifier]['LABEL'][1]
    values = {name: entry[name] for name in STYLE_FIELDS if name in entry}
    values.update(changes)
    require(bpy.ops.qcblender.edit_annotation(annotation_id=identifier, **values) == {'FINISHED'}, 'Annotation edit failed')


def material_snapshot(material):
    """Native node identities, values and links, without the implementation snapshot."""
    result = {'name': material.name, 'use_nodes': material.use_nodes,
              'diffuse_color': list(material.diffuse_color), 'nodes': [], 'links': []}
    if material.node_tree is not None:
        for node in material.node_tree.nodes:
            inputs = []
            for item in node.inputs:
                if not hasattr(item, 'default_value'):
                    continue
                value = item.default_value
                if hasattr(value, 'to_list'):
                    value = value.to_list()
                elif not isinstance(value, (str, float, int, bool, type(None))):
                    value = list(value) if hasattr(value, '__iter__') else getattr(value, 'name', str(value))
                inputs.append((item.identifier, value))
            result['nodes'].append((node.name, node.bl_idname, inputs))
        result['links'] = sorted((link.from_node.name, link.from_socket.identifier,
                                  link.to_node.name, link.to_socket.identifier) for link in material.node_tree.links)
    return json.loads(json.dumps(result, ensure_ascii=False))


def owner_snapshot(owner):
    result = []
    for identifier, members in sorted(groups(owner).items()):
        for role, (part, entry) in sorted(members.items()):
            result.append({'id': identifier, 'role': role, 'name': part.name, 'entry': entry,
                           'matrix': [list(row) for row in part.matrix_basis],
                           'hidden': [part.hide_get(), part.hide_viewport, part.hide_render],
                           'material': [mat.name if mat else None for mat in part.data.materials],
                           'body': part.data.body if role == 'LABEL' else None})
    return json.loads(json.dumps(result, ensure_ascii=False))


def run(args, report):
    import bpy
    import numpy as np
    from mathutils import Euler

    require(bpy.app.background, 'Use a separate Blender background process; do not run in an active user scene')
    bpy.ops.preferences.addon_enable(module=MODULE)
    package = Path(importlib.import_module(MODULE).__file__).parent
    report.update(blender=bpy.app.version_string, installed_package=str(package),
                  installed_sources={name: sha256(package / name) for name in
                                     ('blender/annotations.py', 'annotation_geometry.py', 'measurements.py')})
    if args.reopen:
        require(SCENE_KEY in bpy.context.scene, 'Open the saved verification project before --reopen')
        expected = json.loads(bpy.context.scene[SCENE_KEY])
        for name, state in expected['owners'].items():
            owner = bpy.data.objects[name]
            require(owner_snapshot(owner) == state['snapshot'], 'Cold read changed annotation state: ' + name)
            require(science(owner) == state['science'], 'Cold read changed scientific arrays: ' + name)
            verify_geometry(owner)
            require(str(owner['qc_dataset']).startswith('//'), 'Saved dataset is not portable')
            for members in groups(owner).values():
                label = members['LABEL'][0]
                if any('\u2e80' <= letter <= '\u9fff' for letter in label.data.body):
                    require(label.data.font is not None and label.data.font.packed_file is not None,
                            'Cold read lost packed Chinese font')
        for name, state in expected['materials'].items():
            require(material_snapshot(bpy.data.materials[name]) == state, 'Cold read changed custom material nodes')
        report['cold_reopen'] = 'Passed'
        report['original_run_checks'] = expected['checks']
        return

    require(not bpy.data.filepath and not any(obj.get('qc_dataset') for obj in bpy.data.objects),
            'Start with --factory-startup and no user project')
    manifest = args.dataset.resolve(strict=True)
    require(manifest.name == 'manifest.json', '--dataset must name an existing manifest.json')
    report['input_manifest'] = {'path': str(manifest), 'sha256': sha256(manifest)}
    original = module('blender.views').atom_view(manifest.parent)
    original.name = 'Annotation verification source'
    untouched = module('blender.views').atom_view(manifest.parent)
    untouched.name = 'Annotation verification other owner'
    positions, record = module('blender.geometry').current_geometry(original)
    before_science = science(original)
    choices = select_numbers(positions)
    original.rotation_euler = Euler((.2, -.4, .1))
    initial_camera = bpy.context.scene.camera
    require(initial_camera is not None, 'Factory scene must supply the creation camera')
    initial_camera.rotation_euler = Euler((.5, .3, -.7))
    bpy.context.view_layer.update()
    identifiers = {}
    for kind, numbers in choices.items():
        activate(original)
        before = set(groups(original))
        require(bpy.ops.qcblender.add_annotation(kind=kind, atoms=','.join(map(str, numbers))) == {'FINISHED'}, 'Creation failed: ' + kind)
        created = set(groups(original)) - before
        require(len(created) == 1, 'Expected one annotation group')
        identifiers[kind] = created.pop()
    bpy.context.view_layer.update()
    creation_rotations = {}
    for members in groups(original).values():
        label, entry = members['LABEL']
        require(label.matrix_world.to_quaternion().rotation_difference(initial_camera.matrix_world.to_quaternion()).angle < 1e-5,
                'New label did not face the scene camera under a rotated parent: ' + entry['kind'])
        require(len(label.constraints) == 0, 'Creation added continuous camera tracking')
        creation_rotations[entry['id']] = tuple(label.rotation_quaternion)
    initial_camera.rotation_euler = Euler((-.2, .6, .4))
    bpy.context.view_layer.update()
    report['creation_faces_camera_once_rotated_parent'] = 'Passed'
    report['geometry'] = verify_geometry(original)
    initial_material_checks(original)
    report['native_geometry_and_default_materials'] = 'Passed'

    activate(untouched)
    bpy.context.scene.camera = None
    require(bpy.ops.qcblender.add_annotation(kind='ATOM', atoms='1', color=(.4, .7, .1)) == {'FINISHED'},
            'Creation-time color selection failed')
    bpy.context.scene.camera = initial_camera
    report['creation_without_camera'] = 'Passed'
    colored = next(iter(groups(untouched).values()))['LABEL'][0].data.materials[0]
    shader = next(node for node in colored.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
    np.testing.assert_allclose(shader_socket(shader, 'Base Color').default_value, (.4, .7, .1, 1), atol=1e-7)
    require(shader_socket(shader, 'Metallic').default_value == 1, 'Creation color changed default metallic')
    report['creation_color'] = 'Passed'

    # Explicit prefix values must remain user text, including Chinese and spaces.
    for prefix in ('氧间距：', '', '  '):
        edit(original, identifiers['DISTANCE'], prefix_mode='CUSTOM', prefix=prefix)
        verify_geometry(original)
    edit(original, identifiers['DISTANCE'], prefix_mode='DEFAULT', prefix='')
    for members in groups(original).values():
        label, entry = members['LABEL']
        np.testing.assert_allclose(label.rotation_quaternion, creation_rotations[entry['id']], atol=1e-7)
    report['camera_motion_and_edit_preserve_existing_orientation'] = 'Passed'
    report['custom_prefix_chinese_empty_spaces'] = 'Passed'

    # Share the actual material with an unrelated native object and customize its
    # shader graph. Layout edits and updates must not inspect or rewrite it.
    distance = groups(original)[identifiers['DISTANCE']]
    custom = distance['LABEL'][0].data.materials[0]
    sentinel_mesh = bpy.data.meshes.new('User material sentinel mesh')
    sentinel = bpy.data.objects.new('User material sentinel', sentinel_mesh)
    bpy.context.collection.objects.link(sentinel)
    sentinel_mesh.materials.append(custom)
    shader = next(node for node in custom.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
    shader_socket(shader, 'Base Color').default_value = (.7, .1, .2, 1)
    shader_socket(shader, 'Metallic').default_value = .35
    custom.node_tree.nodes.remove(shader)
    emission = custom.node_tree.nodes.new('ShaderNodeEmission')
    emission.inputs[0].default_value = (.2, .4, .7, 1)
    output = next(node for node in custom.node_tree.nodes if node.bl_idname == 'ShaderNodeOutputMaterial')
    custom.node_tree.links.new(emission.outputs[0], shader_socket(output, 'Surface'))
    custom_before = material_snapshot(custom)
    bindings = {role: part.data.materials[0] for role, (part, _) in distance.items()}
    edit(original, identifiers['DISTANCE'], offset=(.3, -.2, .4), line_width=.024, measurement_width=.018)
    module('blender.annotations').update_annotations(original, positions, record)
    require(material_snapshot(custom) == custom_before, 'Edit or update rewrote user shader nodes')
    require(all(groups(original)[identifiers['DISTANCE']][role][0].data.materials[0] == mat
                for role, mat in bindings.items()), 'Edit changed material slots')
    require(sentinel.data.materials[0] == custom, 'Unrelated material user was changed')
    verify_geometry(original)
    report['shared_custom_nodes_survive_edit_update'] = 'Passed'

    # Test each visibility switch separately, then restore all visible geometry.
    dihedral_id = identifiers['DIHEDRAL']
    for values in ({'show_leader': False}, {'show_measurement': False}, {'show_planes': False}, {'visible': False}):
        visibility = dict(show_leader=True, show_measurement=True, show_planes=True, visible=True)
        visibility.update(values)
        edit(original, dihedral_id, **visibility)
        members = groups(original)[dihedral_id]
        for role, (part, _) in members.items():
            hidden = (not values.get('visible', True) or role == 'LEADER' and not values.get('show_leader', True)
                      or role == 'ARC' and not values.get('show_measurement', True)
                      or role.startswith('PLANE_') and not values.get('show_planes', True))
            # A zero-value dihedral has no arc even when its switch is enabled.
            hidden = hidden or role == 'ARC' and len(part.data.splines) == 0
            require(part.hide_viewport == hidden and part.hide_render == hidden, 'Visibility switch affected wrong part')
    edit(original, dihedral_id, show_leader=True, show_measurement=True, show_planes=True, visible=True)
    report['independent_annotation_visibility'] = 'Passed'

    copied = module('blender.layers').copy_layer(original, bpy.context.collection)
    copied.name = 'Annotation verification copy'
    verify_geometry(copied)
    original_groups = list(groups(original).values())
    copied_groups = list(groups(copied).values())
    require(len(copied_groups) == len(original_groups), 'Copy lost annotation groups')
    for members in copied_groups:
        entry = members['LABEL'][1]
        source = next(group for group in original_groups if group['LABEL'][1]['kind'] == entry['kind'])
        for role, (part, _) in members.items():
            require(part.data != source[role][0].data, 'Copy reused annotation geometry datablock')
            require(part.data.materials[0] != source[role][0].data.materials[0], 'Copy reused original material')
        core = members['LABEL'][0].data.materials[0]
        require(all(part.data.materials[0] == core for role, (part, _) in members.items()
                    if not role.startswith('PLANE_')), 'Copy broke internal material sharing')
        copied_state = material_snapshot(core)
        source_state = material_snapshot(source['LABEL'][0].data.materials[0])
        copied_state.pop('name')
        source_state.pop('name')
        require(copied_state == source_state, 'Copy lost custom shader graph or socket values')
        if 'PLANE_A' in members:
            plane = members['PLANE_A'][0].data.materials[0]
            require(plane == members['PLANE_B'][0].data.materials[0] and plane != core,
                    'Copy lost the independent plane material group')
    require(len({group['LABEL'][0].data.materials[0].as_pointer() for group in copied_groups}) == len(copied_groups),
            'Copied annotations share materials across separate groups')
    report['copy_independent_data_and_material_groups'] = 'Passed'

    # Another owner has its own label; Face All must never rotate that label.
    activate(untouched)
    require(bpy.ops.qcblender.add_annotation(kind='ATOM', atoms='1') == {'FINISHED'}, 'Other-owner annotation creation failed')
    untouched_before = owner_snapshot(untouched)
    camera_data = bpy.data.cameras.new('Annotation verification camera')
    camera = bpy.data.objects.new('Annotation verification camera', camera_data)
    bpy.context.collection.objects.link(camera)
    camera.rotation_euler = Euler((.4, -.3, .8))
    bpy.context.scene.camera = camera
    bpy.context.view_layer.update()
    activate(original)
    nonlabels = {part.name: [list(row) for row in part.matrix_basis]
                 for members in groups(original).values() for role, (part, _) in members.items() if role != 'LABEL'}
    require(bpy.ops.qcblender.face_annotations(annotation_id=identifiers['ATOM']) == {'FINISHED'}, 'Single face failed')
    require(bpy.ops.qcblender.face_annotations() == {'FINISHED'}, 'Face all failed after single face')
    bpy.context.view_layer.update()
    expected_rotation = camera.matrix_world.to_quaternion()
    for members in groups(original).values():
        actual = members['LABEL'][0].matrix_world.to_quaternion()
        require(actual.rotation_difference(expected_rotation).angle < 1e-5, 'Face All missed a label')
    require(owner_snapshot(untouched) == untouched_before, 'Face All changed another owner')
    for name, matrix in nonlabels.items():
        np.testing.assert_allclose(bpy.data.objects[name].matrix_basis, matrix, atol=1e-8)
    report['face_all_current_owner_after_single_face'] = 'Passed'

    # Whole-layer hiding must carry all new roles, and restore per-part state.
    activate(copied)
    hidden_before = owner_snapshot(copied)
    for action in ('VISIBILITY', 'RENDER'):
        require(bpy.ops.qcblender.layer_action(target=copied.name, action=action) == {'FINISHED'}, 'Layer hide failed')
        for members in groups(copied).values():
            for part, _ in members.values():
                require(part.hide_get() if action == 'VISIBILITY' else part.hide_render, 'Layer hide missed annotation role')
        require(bpy.ops.qcblender.layer_action(target=copied.name, action=action) == {'FINISHED'}, 'Layer restore failed')
        require(owner_snapshot(copied) == hidden_before, 'Layer restore lost per-part state')
    report['layer_visibility_all_roles'] = 'Passed'

    # Removal must delete every native part but retain shared user material data.
    copied_id, members = next((key, group) for key, group in groups(copied).items()
                              if group['LABEL'][1]['kind'] == 'DIHEDRAL')
    names = {part.name for part, _ in members.values()}
    material_names = {mat.name for part, _ in members.values() for mat in part.data.materials}
    data_names = [(part.data.name, part.type == 'MESH') for part, _ in members.values()]
    activate(copied)
    require(bpy.ops.qcblender.remove_annotation(annotation_id=copied_id) == {'FINISHED'}, 'Annotation removal failed')
    require(not any(name in bpy.data.objects for name in names), 'Remove left annotation parts behind')
    require(all(name not in (bpy.data.meshes if mesh else bpy.data.curves) for name, mesh in data_names),
            'Remove left unused annotation geometry datablocks behind')
    require(all(name in bpy.data.materials for name in material_names), 'Remove purged annotation material data')
    require(custom.name in bpy.data.materials and material_snapshot(custom) == custom_before,
            'Delete altered user material')
    report['delete_complete_group_preserves_user_material'] = 'Passed'

    # Controlled legacy layout: real native LABEL/LEADER parts, distinct saved
    # materials, no new measurement role. No source arrays are modified.
    legacy = module('blender.views').atom_view(manifest.parent)
    legacy.name = 'Annotation verification legacy'
    activate(legacy)
    require(bpy.ops.qcblender.add_annotation(kind='DISTANCE', atoms=','.join(map(str, choices['DISTANCE']))) == {'FINISHED'},
            'Legacy fixture creation failed')
    legacy_id, members = next(iter(groups(legacy).items()))
    dashed = members['DASH'][0]
    dashed_data = dashed.data
    bpy.data.objects.remove(dashed, do_unlink=True)
    if dashed_data.users == 0:
        bpy.data.curves.remove(dashed_data)
    label, leader = members['LABEL'][0], members['LEADER'][0]
    label.data.materials.clear()
    label.data.materials.append(custom)
    old_leader_material = leader.data.materials[0]
    for role in ('LABEL', 'LEADER'):
        part, entry = members[role]
        entry['version'] = 1
        for name in ('prefix_mode', 'prefix', 'show_measurement', 'show_planes', 'measurement_width', 'arc_radius'):
            entry.pop(name, None)
        part['qc_annotation'] = json.dumps(entry, ensure_ascii=False)
    old_materials = {mat.name: material_snapshot(mat) for mat in (custom, old_leader_material)}
    module('blender.annotations').update_annotations(legacy, *module('blender.geometry').current_geometry(legacy))
    require(set(groups(legacy)[legacy_id]) == {'LABEL', 'LEADER'}, 'Ordinary update silently upgraded legacy parts')
    require(label.data.materials[0] == custom and leader.data.materials[0] == old_leader_material,
            'Ordinary update silently unified legacy materials')
    edit(legacy, legacy_id, offset=(.25, .25, .25))
    verify_geometry(legacy)
    require(label.data.materials[0] == custom and leader.data.materials[0] == old_leader_material,
            'First edit rewrote old materials')
    require(material_snapshot(custom) == old_materials[custom.name], 'First edit altered saved shader nodes')
    report['legacy_first_edit_adds_parts_without_material_migration'] = 'Passed'
    activate(legacy)
    require(bpy.ops.qcblender.unify_annotation_materials() == {'FINISHED'}, 'Explicit material unification failed')
    members = groups(legacy)[legacy_id]
    clone = members['LABEL'][0].data.materials[0]
    require(clone != custom and all(part.data.materials[0] == clone for part, _ in members.values()),
            'Explicit unification did not create one independent material')
    for name, state in old_materials.items():
        require(name in bpy.data.materials and bpy.data.materials[name].use_fake_user,
                'Old material is not retained for saving')
        require(material_snapshot(bpy.data.materials[name]) == state, 'Unification altered old material nodes')
    assignments = {role: part.data.materials[0].as_pointer() for role, (part, _) in members.items()}
    count = len(bpy.data.materials)
    require(bpy.ops.qcblender.unify_annotation_materials() == {'FINISHED'}, 'Second unification failed')
    require(len(bpy.data.materials) == count and assignments == {
        role: part.data.materials[0].as_pointer() for role, (part, _) in groups(legacy)[legacy_id].items()},
        'Material unification is not idempotent')
    report['explicit_unification_preserves_old_nodes_and_is_idempotent'] = 'Passed'

    # Keep a real Chinese-prefix label in the saved project for GUI reuse.
    edit(original, identifiers['ANGLE'], prefix_mode='CUSTOM', prefix='水分子角：')
    chinese_label = groups(original)[identifiers['ANGLE']]['LABEL'][0]
    require(chinese_label.data.body.startswith('水分子角：'), 'Chinese prefix was not stored')
    require(chinese_label.data.font is not None and chinese_label.data.font.packed_file is not None,
            'Chinese label font was not packed for a portable project')
    verify_geometry(original)
    verify_geometry(legacy)
    require(science(original) == before_science and science(copied) == before_science and science(untouched) == before_science,
            'Annotation operations changed scientific arrays')
    require(science(legacy) == before_science, 'Legacy operations changed scientific arrays')
    require(sha256(manifest) == report['input_manifest']['sha256'], 'Input manifest changed')
    report['scientific_arrays_unchanged'] = 'Passed'

    owners = (original, copied, untouched, legacy)
    expected = {'owners': {owner.name: {'snapshot': owner_snapshot(owner), 'science': science(owner)} for owner in owners},
                'materials': {name: material_snapshot(bpy.data.materials[name]) for name in old_materials},
                'checks': {name: value for name, value in report.items() if value == 'Passed'}}
    bpy.context.scene[SCENE_KEY] = json.dumps(expected, ensure_ascii=False)
    blend = args.output / 'annotations.blend'
    require(not blend.exists() and not blend.with_suffix('.qcdata').exists(), 'Use fresh output paths')
    module('blender.project').save_project(blend)
    require(blend.is_file() and blend.with_suffix('.qcdata').is_dir(), 'Self-contained save did not create both artifacts')
    report['self_contained_save'] = 'Passed'
    report['saved_project'] = {'path': str(blend), 'sha256': sha256(blend)}
    report['cold_reopen'] = 'Not Run: launch another Blender process with --reopen'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Absolute report/artifact directory')
    parser.add_argument('--dataset', type=Path, help='Existing absolute manifest.json; required for a fresh run')
    parser.add_argument('--reopen', action='store_true', help='Check the verification .blend already loaded at process startup')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    if not args.output.is_absolute() or (not args.reopen and (args.dataset is None or not args.dataset.is_absolute())):
        parser.error('Use absolute --output and --dataset paths')
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output / ('annotation-geometry-reopen.json' if args.reopen else 'annotation-geometry.json')
    if destination.exists():
        raise FileExistsError(destination)
    report = {'status': 'Failed', 'script_sha256': sha256(__file__),
              'gui_render_undo_redo': 'Not Run', 'xyz_optimization_irc_switching': 'Not Run'}
    try:
        run(args, report)
        report['status'] = 'Passed'
    except Exception:
        report['error'] = traceback.format_exc()
        raise
    finally:
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
