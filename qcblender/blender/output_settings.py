"""Apply output settings to one scene and persist its reversible baseline."""

import json
import uuid

import bpy
from bpy.props import BoolProperty, CollectionProperty, PointerProperty, StringProperty
from mathutils import Vector

from ..output_presets import QUALITY_PRESETS, lighting_layout, output_plan


OWNER = 'qc_output_owner'
ROLE = 'qc_output_role'
RNA_ERRORS = (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError)
_ORIGINAL_CAMERA_UNSET = object()


class QCOutputCollectionLink(bpy.types.PropertyGroup):
    collection: PointerProperty(type=bpy.types.Collection)
    scene_root: BoolProperty(default=False)


class QCOutputLightState(bpy.types.PropertyGroup):
    original: PointerProperty(type=bpy.types.Object)
    isolated: PointerProperty(type=bpy.types.Object)
    hidden: BoolProperty()
    links: CollectionProperty(type=QCOutputCollectionLink)


class QCOutputState(bpy.types.PropertyGroup):
    active: BoolProperty(default=False)
    owner: StringProperty()
    baseline_json: StringProperty()
    camera: PointerProperty(type=bpy.types.Object)
    original_camera: PointerProperty(type=bpy.types.Object)
    original_world: PointerProperty(type=bpy.types.World)
    output_world: PointerProperty(type=bpy.types.World)
    rig_collection: PointerProperty(type=bpy.types.Collection)
    lights: CollectionProperty(type=QCOutputLightState)


def _resolve(scene, path):
    value = scene
    parts = path.split('.')
    for part in parts[:-1]:
        value = getattr(value, part)
    return value, parts[-1]


def _has(scene, path):
    value = scene
    for part in path.split('.'):
        if not hasattr(value, part):
            return False
        value = getattr(value, part)
    return True


def _settings(scene):
    paths = ['render.engine', 'display_settings.display_device', 'view_settings.view_transform',
             'view_settings.look', 'view_settings.exposure', 'view_settings.gamma',
             'view_settings.use_curve_mapping', 'view_settings.use_white_balance',
             'render.resolution_x', 'render.resolution_y', 'render.resolution_percentage',
             'render.film_transparent', 'render.image_settings.file_format',
             'render.image_settings.color_mode', 'render.image_settings.color_depth',
             'render.image_settings.color_management', 'eevee.taa_render_samples',
             'cycles.samples', 'cycles.use_adaptive_sampling', 'cycles.adaptive_threshold',
             'cycles.use_denoising', 'cycles.denoiser', 'cycles.denoising_input_passes']
    return {path: getattr(*_resolve(scene, path)) for path in paths if _has(scene, path)}


def _write_settings(scene, values):
    for path, value in values.items():
        target, attribute = _resolve(scene, path)
        setattr(target, attribute, value)


def _collection_tree(root):
    result = set()

    def visit(collection):
        if collection in result:
            return
        result.add(collection)
        for child in collection.children:
            visit(child)
    visit(root)
    return result


def _collections(scene):
    return _collection_tree(scene.collection)


def _unsafe_collections(scene):
    shared = set().union(*(_collections(other) for other in bpy.data.scenes if other != scene))
    instanced = set().union(*(_collection_tree(obj.instance_collection) for obj in bpy.data.objects
                             if obj.instance_type == 'COLLECTION' and obj.instance_collection is not None))
    return shared | instanced


def _contains_light(collection, seen=None):
    seen = set() if seen is None else seen
    if collection in seen:
        return False
    seen.add(collection)
    return any(obj.type == 'LIGHT' or (obj.instance_type == 'COLLECTION' and obj.instance_collection
               and _contains_light(obj.instance_collection, seen)) for obj in collection.all_objects)


def _light_plan(scene):
    """Reject shared collection paths; isolate only objects with local links."""
    current = _collections(scene)
    unsafe = _unsafe_collections(scene)
    affected = {}

    def visit(collection, unsafe_path=False):
        unsafe_path = unsafe_path or collection in unsafe
        for obj in collection.objects:
            if obj.type == 'LIGHT' and obj.get(OWNER) != scene.qc_output.owner:
                if unsafe_path:
                    raise ValueError('Output lighting cannot isolate a light in a shared or instanced collection: '
                                     + obj.name)
                affected.setdefault(obj, set()).add(collection)
        for child in collection.children:
            visit(child, unsafe_path)
    visit(scene.collection)
    for obj in scene.objects:
        if (obj.instance_type == 'COLLECTION' and obj.instance_collection is not None
                and _contains_light(obj.instance_collection)):
            raise ValueError('Output lighting cannot isolate lights inside a collection instance: ' + obj.name)
    result = []
    for obj, links in affected.items():
        isolate = any(other != scene for other in obj.users_scene)
        if obj.library is not None or (isolate and any(link.library is not None for link in links)):
            raise ValueError('Output lighting requires editable local lights and collections: ' + obj.name)
        # External collection links are unaffected because only this scene's links are replaced.
        result.append((obj, tuple(links & current), isolate))
    return result


def _validate_owned(scene, *, require_world_graph=True):
    state = scene.qc_output
    collection = state.rig_collection
    if collection is not None:
        if collection.get(OWNER) != state.owner or collection not in _collections(scene):
            raise ValueError('The saved QC output light collection no longer belongs to this scene')
        if collection in _unsafe_collections(scene):
            raise ValueError('The QC output light collection is shared or instanced')
        roles = set()
        for obj in collection.all_objects:
            if obj.get(OWNER) != state.owner or obj.type != 'LIGHT' or obj.data.type != 'AREA':
                raise ValueError('The QC output light collection contains unrecognized objects')
            role = obj.get(ROLE)
            if role not in {'KEY', 'FILL', 'RIM'} or role in roles:
                raise ValueError('The QC output light collection contains unrecognized objects')
            roles.add(role)
            if obj.parent is not None or obj.constraints:
                raise ValueError('The QC output lights must remain unparented and unconstrained')
            if any(other != scene for other in obj.users_scene) or obj.data.users > 1:
                raise ValueError('A QC output light or its data is shared outside its rig')
    world = state.output_world
    if world is not None:
        if world.get(OWNER) != state.owner:
            raise ValueError('The saved QC output World no longer belongs to this scene')
        if any(other.world == world for other in bpy.data.scenes if other != scene):
            raise ValueError('The QC output World is shared with another scene')
        if require_world_graph:
            if (not world.use_nodes or any(world.node_tree.nodes.get(name) is None
                    or world.node_tree.nodes[name].type != 'BACKGROUND'
                    for name in ('QC Visible Background', 'QC Neutral Illumination'))):
                raise ValueError('The QC output World has been modified; restore the original settings first')


def _available_engines(scene):
    # RNA's context-free enum omits Python-registered engines such as Cycles.
    engines = {item.identifier for item in scene.render.bl_rna.properties['engine'].enum_items}
    pending = list(bpy.types.RenderEngine.__subclasses__())
    while pending:
        engine = pending.pop()
        if getattr(engine, 'is_registered', False) and getattr(engine, 'bl_idname', None):
            engines.add(engine.bl_idname)
        pending.extend(engine.__subclasses__())
    return engines


def validate_output(scene, *, quality='STANDARD', background='WHITE', background_color=(1., 1., 1.),
                    resolution_x=1920, resolution_y=1080, resolution_percentage=100, denoise=True):
    """Preflight all scene changes, without modifying scene or object data."""
    plan = output_plan(quality=quality, background=background, background_color=background_color,
                       resolution_x=resolution_x, resolution_y=resolution_y,
                       resolution_percentage=resolution_percentage, denoise=denoise)
    if scene.library is not None:
        raise ValueError('Output settings require an editable local scene')
    _validate_owned(scene)
    preset = QUALITY_PRESETS[quality]
    engines = _available_engines(scene)
    if preset.engine not in engines:
        raise ValueError('The requested render engine is unavailable: ' + preset.engine)
    required = (['eevee.taa_render_samples'] if quality == 'PREVIEW' else
                ['cycles.samples', 'cycles.use_adaptive_sampling', 'cycles.adaptive_threshold',
                 'cycles.use_denoising', 'cycles.denoiser', 'cycles.denoising_input_passes'])
    if any(not _has(scene, path) for path in required):
        raise ValueError('The requested render settings are unavailable in this Blender installation')
    for attribute in ('resolution_x', 'resolution_y', 'resolution_percentage'):
        prop = scene.render.bl_rna.properties[attribute]
        if not prop.hard_min <= plan[attribute] <= prop.hard_max:
            raise ValueError(f'{attribute} is outside Blender\'s supported range')
    _light_plan(scene)
    if scene.qc_output.active:
        for item in scene.qc_output.lights:
            if item.isolated is None and item.original is not None and any(
                    other != scene for other in item.original.users_scene):
                raise ValueError('An original light is now shared; restoring it would affect another scene')
    return plan


def _link_collection(link, scene):
    # A Scene's master collection is an embedded ID and cannot be an RNA pointer.
    return scene.collection if link.scene_root else link.collection


def _state_snapshot(state):
    return {'active': state.active, 'owner': state.owner, 'baseline_json': state.baseline_json,
            'camera': state.camera,
            'original_camera': state.original_camera, 'original_world': state.original_world,
            'output_world': state.output_world, 'rig_collection': state.rig_collection,
            'lights': [(item.original, item.isolated, item.hidden,
                        tuple(collection for link in item.links
                              if (collection := _link_collection(link, state.id_data)) is not None))
                       for item in state.lights]}


def _state_write(state, values):
    for key, value in values.items():
        if key != 'lights':
            setattr(state, key, value)
    state.lights.clear()
    for original, isolated, hidden, links in values['lights']:
        item = state.lights.add()
        item.original, item.isolated, item.hidden = original, isolated, hidden
        for collection in links:
            link = item.links.add()
            link.scene_root = collection == state.id_data.collection
            if not link.scene_root:
                link.collection = collection


def _new_world(owner, created):
    world = bpy.data.worlds.new('QC Output World')
    created.append(('worlds', world))
    world[OWNER] = owner
    world.use_nodes = True
    nodes, links = world.node_tree.nodes, world.node_tree.links
    nodes.clear()
    illumination = nodes.new('ShaderNodeBackground')
    illumination.name = 'QC Neutral Illumination'
    illumination.inputs['Color'].default_value = (.18, .18, .18, 1.)
    illumination.inputs['Strength'].default_value = .8
    background = nodes.new('ShaderNodeBackground')
    background.name = 'QC Visible Background'
    ray = nodes.new('ShaderNodeLightPath')
    mix = nodes.new('ShaderNodeMixShader')
    output = nodes.new('ShaderNodeOutputWorld')
    links.new(ray.outputs['Is Camera Ray'], mix.inputs[0])
    links.new(illumination.outputs[0], mix.inputs[1])
    links.new(background.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs['Surface'])
    return world


def _configure(scene, plan):
    preset = QUALITY_PRESETS[plan['quality']]
    values = {'render.engine': preset.engine, 'display_settings.display_device': 'sRGB',
              'view_settings.view_transform': 'Standard', 'view_settings.look': 'None',
              'view_settings.exposure': 0., 'view_settings.gamma': 1.,
              'view_settings.use_curve_mapping': False, 'view_settings.use_white_balance': False,
              'render.resolution_x': plan['resolution_x'], 'render.resolution_y': plan['resolution_y'],
              'render.resolution_percentage': plan['resolution_percentage'],
              'render.film_transparent': plan['background'] == 'TRANSPARENT',
              'render.image_settings.file_format': 'PNG',
              'render.image_settings.color_mode': 'RGBA' if plan['background'] == 'TRANSPARENT' else 'RGB',
              'render.image_settings.color_depth': '8',
              'render.image_settings.color_management': 'FOLLOW_SCENE'}
    if preset.engine == 'CYCLES':
        values.update({'cycles.samples': preset.samples, 'cycles.use_adaptive_sampling': True,
                       'cycles.adaptive_threshold': preset.adaptive_threshold,
                       'cycles.use_denoising': plan['denoise'], 'cycles.denoiser': 'OPENIMAGEDENOISE',
                       'cycles.denoising_input_passes': 'RGB_ALBEDO_NORMAL'})
    else:
        values['eevee.taa_render_samples'] = preset.samples
    _write_settings(scene, {path: value for path, value in values.items() if _has(scene, path)})


def _rig_snapshot(collection):
    if collection is None:
        return None
    return (collection.hide_render, [(obj, obj.matrix_world.copy(), obj.hide_render,
            obj.data.energy, obj.data.size, tuple(obj.data.color), obj.data.shape,
            obj.data.normalize if hasattr(obj.data, 'normalize') else None)
            for obj in collection.all_objects])


def _rig_restore(collection, snapshot):
    if snapshot is not None:
        collection.hide_render = snapshot[0]
        for obj, matrix, hidden, energy, size, color, shape, normalize in snapshot[1]:
            obj.matrix_world, obj.hide_render = matrix, hidden
            obj.data.energy, obj.data.size, obj.data.color, obj.data.shape = energy, size, color, shape
            if normalize is not None:
                obj.data.normalize = normalize


def _remove_created(created):
    for kind, value in reversed(created):
        getattr(bpy.data, kind).remove(value, do_unlink=True)


def apply_output(scene, camera, subject_points, *, quality='STANDARD', background='WHITE',
                 background_color=(1., 1., 1.), resolution_x=1920, resolution_y=1080,
                 resolution_percentage=100, denoise=True, original_camera=_ORIGINAL_CAMERA_UNSET):
    """Apply a preset atomically; callers own camera creation and its rollback.

    Pass the pre-application camera as ``original_camera`` when the caller has
    already activated a new camera. Saved RNA pointers survive rename/reopen.
    """
    plan = validate_output(scene, quality=quality, background=background,
                           background_color=background_color, resolution_x=resolution_x,
                           resolution_y=resolution_y, resolution_percentage=resolution_percentage,
                           denoise=denoise)
    if camera is None or camera.type != 'CAMERA' or camera.name not in scene.objects:
        raise ValueError('Output requires a camera in the current scene')
    rotation = camera.matrix_world.to_quaternion()
    axes = [rotation @ Vector(axis) for axis in ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))]
    layout = lighting_layout(subject_points, *axes)
    for spec in layout['lights']:
        for attribute in ('energy', 'size'):
            prop = bpy.types.AreaLight.bl_rna.properties[attribute]
            if not prop.hard_min <= spec[attribute] <= prop.hard_max:
                raise ValueError('Subject scale exceeds the supported lighting range')
    state = scene.qc_output
    saved = _state_snapshot(state)
    immediate = _settings(scene)
    previous_camera, previous_world = scene.camera, scene.world
    rig_before = _rig_snapshot(state.rig_collection)
    world_before = ({(name, socket): tuple(node.inputs[socket].default_value) if socket == 'Color'
                     else node.inputs[socket].default_value
                     for name in ('QC Visible Background', 'QC Neutral Illumination')
                     for node in [state.output_world.node_tree.nodes[name]] for socket in ('Color', 'Strength')}
                    if state.output_world is not None else None)
    created, swapped, hidden_before = [], [], []
    owner = state.owner or uuid.uuid4().hex
    records = list(saved['lights']) if state.active else []
    try:
        for obj, collections, isolate in _light_plan(scene):
            record = next((item for item in records if item[0] == obj), None)
            if isolate:
                local = obj.copy()
                created.append(('objects', local))
                local[OWNER], local[ROLE] = owner, 'ISOLATED'
                local.name = 'QC Output isolated ' + obj.name
                for collection in collections:
                    collection.objects.link(local)
                    collection.objects.unlink(obj)
                    swapped.append((collection, obj, local))
                local.hide_render = True
                records.append((obj, local, obj.hide_render, collections))
            else:
                hidden_before.append((obj, obj.hide_render))
                if record is None:
                    records.append((obj, None, obj.hide_render, ()))
                obj.hide_render = True
        collection = state.rig_collection
        if collection is None:
            collection = bpy.data.collections.new('QC Output Lights')
            created.append(('collections', collection))
            collection[OWNER] = owner
            scene.collection.children.link(collection)
        collection.hide_render = False
        for spec in layout['lights']:
            light = next((obj for obj in collection.objects if obj.get(ROLE) == spec['role']), None)
            if light is None:
                data = bpy.data.lights.new('QC Output ' + spec['role'], 'AREA')
                created.append(('lights', data))
                light = bpy.data.objects.new('QC Output ' + spec['role'], data)
                created.append(('objects', light))
                light[OWNER], light[ROLE] = owner, spec['role']
                collection.objects.link(light)
            light.hide_render = False
            light.location = spec['location']
            light.rotation_euler = (Vector(layout['center']) - light.location).to_track_quat('-Z', 'Y').to_euler()
            light.scale = (1., 1., 1.)
            light.data.shape, light.data.color = 'DISK', (1., 1., 1.)
            if hasattr(light.data, 'normalize'):
                light.data.normalize = True
            light.data.energy, light.data.size = spec['energy'], spec['size']
        world = state.output_world or _new_world(owner, created)
        visible = world.node_tree.nodes['QC Visible Background']
        visible.inputs['Color'].default_value = (*plan['background_color'], 1.)
        visible.inputs['Strength'].default_value = 1.
        neutral = world.node_tree.nodes['QC Neutral Illumination']
        neutral.inputs['Color'].default_value = (.18, .18, .18, 1.)
        neutral.inputs['Strength'].default_value = .8
        scene.camera, scene.world = camera, world
        _configure(scene, plan)
        result = dict(saved)
        if not state.active:
            result.update(baseline_json=json.dumps(immediate), original_world=previous_world,
                          original_camera=(previous_camera if original_camera is _ORIGINAL_CAMERA_UNSET
                                           else original_camera))
        result.update(active=True, owner=owner, output_world=world, rig_collection=collection, lights=records)
        _state_write(state, result)
    except RNA_ERRORS:
        _write_settings(scene, immediate)
        scene.camera, scene.world = previous_camera, previous_world
        for obj, hidden in hidden_before:
            obj.hide_render = hidden
        for collection, original, isolated in reversed(swapped):
            if original.name not in collection.objects:
                collection.objects.link(original)
            if isolated.name in collection.objects:
                collection.objects.unlink(isolated)
        _rig_restore(saved['rig_collection'], rig_before)
        if world_before is not None:
            for (name, socket), value in world_before.items():
                saved['output_world'].node_tree.nodes[name].inputs[socket].default_value = value
        _state_write(state, saved)
        _remove_created(created)
        raise
    warnings = []
    if (scene.render.use_compositing and (getattr(scene, 'compositing_node_group', None) is not None
                                         or getattr(scene, 'use_nodes', False))):
        warnings.append('The scene compositor is enabled and may change the final color or alpha')
    if plan['quality'] != 'PREVIEW' and scene.cycles.device == 'GPU':
        warnings.append('Cycles uses the current GPU setting; if no compatible device is available, '
                        'select CPU in Render Properties > Device')
    return {**plan, 'light_scale': layout['scale'], 'lights': len(layout['lights']), 'warnings': warnings}


def restore_output(scene):
    """Restore the first baseline; keep the QC rig hidden for later reuse."""
    state = scene.qc_output
    if not state.active:
        return {'restored': False}
    # Validate before restoring anything, including saved primitive data.
    values = json.loads(state.baseline_json)
    if not isinstance(values, dict) or any(not _has(scene, path) for path in values):
        raise ValueError('The saved output settings are incompatible with this Blender version')
    _validate_owned(scene, require_world_graph=False)
    unsafe = _unsafe_collections(scene)
    for item in state.lights:
        if item.isolated is not None:
            if item.isolated.get(OWNER) != state.owner:
                raise ValueError('A saved isolated light no longer belongs to QC output settings')
            if any(other != scene for other in item.isolated.users_scene):
                raise ValueError('An isolated QC light is now shared with another scene')
            for link in item.links:
                collection = _link_collection(link, scene)
                if collection is not None and collection not in _collections(scene):
                    raise ValueError('A saved light collection no longer belongs to this scene')
                if collection in unsafe:
                    raise ValueError('A saved light collection is now shared or instanced')
        elif item.original is not None and any(other != scene for other in item.original.users_scene):
            raise ValueError('An original light is now shared; restoring it would affect another scene')
    _write_settings(scene, values)
    scene.camera, scene.world = state.original_camera, state.original_world
    for item in state.lights:
        original, isolated = item.original, item.isolated
        if isolated is not None:
            for link in item.links:
                collection = _link_collection(link, scene)
                if collection is not None:
                    if original is not None and original.name not in collection.objects:
                        collection.objects.link(original)
                    if isolated.name in collection.objects:
                        collection.objects.unlink(isolated)
            # Remove only this feature's private object copy; its shared Light data stays intact.
            bpy.data.objects.remove(isolated, do_unlink=True)
        elif original is not None:
            original.hide_render = item.hidden
    if state.rig_collection is not None:
        state.rig_collection.hide_render = True
    state.active = False
    state.baseline_json = ''
    state.original_camera = None
    state.original_world = None
    state.lights.clear()
    return {'restored': True}
