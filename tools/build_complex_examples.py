"""Rebuild one real showcase through the installed extension in a fresh Blender."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
OUT = ROOT / 'outputs/complex-examples'
MODULE = 'bl_ext.user_default.qcblender'
parser = argparse.ArgumentParser()
parser.add_argument('case', choices=('orbitals', 'vibration', 'polar', 'interaction'))
parser.add_argument('--animation', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
bpy.ops.preferences.addon_enable(module=MODULE)
jobs, views, project, storage, graph, layers, scalars, fog, inspection = [
    importlib.import_module(MODULE + '.' + name) for name in
    ('blender.jobs', 'blender.views', 'blender.project', 'data', 'blender.graph',
     'blender.layers', 'blender.scalars', 'blender.fog', 'blender.inspection')]
folder = OUT / args.case
folder.mkdir(exist_ok=True)
report = {'case': args.case, 'status': 'Running', 'jobs': [], 'renders': [], 'checks': {}}
started = time.monotonic()


def job(action, **kwargs):
    start = time.monotonic()
    pending = jobs.Job(action, **kwargs)
    try:
        while (result := pending.poll()) is None:
            if time.monotonic() - start > 900:
                raise TimeoutError(str(pending.directory))
            time.sleep(.2)
        assert result['status'] == 'succeeded', result
    except BaseException:
        pending.cancel()
        raise
    report['jobs'].append({'action': action, 'parameters': kwargs,
                           'seconds': time.monotonic()-start, 'result': result})
    print('Completed', action, kwargs.get('parameters', kwargs.get('source', '')), flush=True)
    return pending.directory / 'dataset'


def imported(name):
    return job('import', source=str(input_path('complex-examples/' + name)))


def controls(obj):
    modifier = graph.view_modifier(obj)
    return modifier, {s.name: s.identifier for s in modifier.node_group.interface.items_tree
                      if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}


def set_controls(obj, **values):
    modifier, names = controls(obj)
    for key, value in values.items():
        modifier[names[key]] = value
    obj.update_tag()
    bpy.context.view_layer.update()


def hide(obj):
    obj.hide_render = True
    obj.hide_set(True)


def atoms_at(directory, offset=(0, 0, 0)):
    obj = views.atom_view(directory)
    coords = storage.load_dataset(directory).arrays['positions']
    center = coords.mean(axis=0)
    _, _, axes = np.linalg.svd(coords-center, full_matrices=False)
    if np.linalg.det(axes) < 0:
        axes[2] *= -1
    obj.matrix_world = Matrix.Translation(offset) @ Matrix(axes).to_4x4() @ Matrix.Translation(-Vector(center))
    set_controls(obj, Quality=3)
    return obj


def field(directory, atoms, quantity, **parameters):
    coords = storage.load_dataset(directory).arrays['positions']
    origin = coords.min(axis=0)-2.5
    spacing = .23 if args.case == 'orbitals' else .28
    shape = (np.ceil((coords.max(axis=0)+2.5-origin)/spacing).astype(int)+1).tolist()
    grid = {'origin': origin.tolist(), 'steps': (np.eye(3)*spacing).tolist(), 'shape': shape}
    result = job('evaluate', dataset=str(directory), grid=grid,
                 parameters={'quantity': quantity, 'memory_mb': 512, **parameters})
    return views.field_view(result, atoms)


def caption(body, x, y, size=.25):
    text = bpy.data.curves.new('Case caption', 'FONT')
    text.body, text.size = body, size
    obj = bpy.data.objects.new(body.split('\n')[0], text)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, 3)
    ink = views.material('Caption ink', (.015, .025, .04, 1))
    ink.node_tree.nodes.clear()
    output = ink.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emission = ink.node_tree.nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (.015, .025, .04, 1)
    ink.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
    text.materials.append(ink)
    return obj


def render(name):
    scene.render.filepath = str(folder / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(scene.render.filepath, check_existing=False)
    pixels = np.asarray(image.pixels[:]).reshape(-1, 4)
    assert np.std(pixels[:, :3]) > .025, 'Render appears uniform'
    bpy.data.images.remove(image)
    report['renders'].append(name + '.png')


def mesh_count(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return len(mesh.vertices)
    finally:
        evaluated.to_mesh_clear()


for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1400, 900, 100
scene.render.image_settings.file_format = 'PNG'
scene.world.use_nodes = True
world_nodes, world_links = scene.world.node_tree.nodes, scene.world.node_tree.links
world_nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1)
world_nodes['Background'].inputs['Strength'].default_value = .25
backdrop = world_nodes.new('ShaderNodeBackground')
backdrop.inputs['Color'].default_value = (.9, .9, .9, 1)
ray = world_nodes.new('ShaderNodeLightPath')
mix = world_nodes.new('ShaderNodeMixShader')
world_links.new(ray.outputs['Is Camera Ray'], mix.inputs[0])
world_links.new(world_nodes['Background'].outputs[0], mix.inputs[1])
world_links.new(backdrop.outputs[0], mix.inputs[2])
world_links.new(mix.outputs[0], world_nodes['World Output'].inputs['Surface'])
scene.view_settings.view_transform = 'Standard'
camera = bpy.data.objects.new('Showcase camera', bpy.data.cameras.new('Showcase camera'))
scene.collection.objects.link(camera)
camera.location = (0, 0, 28)
camera.data.type, camera.data.ortho_scale = 'ORTHO', 24
scene.camera = camera
for pos in ((-6, -4, 12), (6, 5, 9)):
    light = bpy.data.objects.new('Softbox', bpy.data.lights.new('Softbox', 'AREA'))
    scene.collection.objects.link(light)
    light.location = pos
    light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    light.data.energy, light.data.size = 300, 8

if args.case == 'orbitals':
    directory = imported('dvb_un_sp.fchk')
    source = storage.load_dataset(directory)
    left, right = atoms_at(directory, (-5.5, 0, 0)), atoms_at(directory, (5.5, 0, 0))
    left.name, right.name = 'DVB cation - orbital', 'DVB cation - spin density'
    alpha = field(directory, left, 'orbital_amplitude', spin='alpha', orbital=35)
    beta = field(directory, left, 'orbital_amplitude', spin='beta', orbital=34)
    hide(beta)
    spin = field(directory, right, 'spin_density')
    set_controls(alpha, Isovalue=.045)
    set_controls(spin, Isovalue=.002)
    density_views = [field(directory, right, q) for q in ('electron_number_density', 'alpha_density', 'beta_density')]
    values = [storage.load_dataset(bpy.path.abspath(o['qc_dataset'])).arrays['field_values'] for o in density_views]
    spin_data = storage.load_dataset(bpy.path.abspath(spin['qc_dataset']))
    np.testing.assert_allclose(values[0], values[1]+values[2], atol=1e-10)
    np.testing.assert_allclose(spin_data.arrays['field_values'], values[1]-values[2], atol=1e-10)
    for obj in density_views:
        hide(obj)
    report['checks']['density_spin_identities'] = 'Passed'
    report['electron_count'] = source.metadata['electron_count']
    report['checks']['occupations'] = 'Passed' if np.sum(source.arrays['mo_occs']) == 69 else 'Failed'
    assert report['checks']['occupations'] == 'Passed'
    caption('DVB radical cation | UB3LYP / STO-3G | +1, doublet', -10, 5.5, .36)
    caption('Alpha SOMO 35 | +/-0.045 bohr^-3/2\nBlue / red: orbital phase', -10, -4.7)
    spin_caption = caption('Spin density: alpha - beta\n+/-0.002 electron/bohr^3', 1, -4.7)
    caption('Illustrative basis | native editable geometry nodes', -10, -6.1, .22)
    render('orbitals-spin')
    for style, name in ((1, 'wire'), (2, 'points')):
        set_controls(alpha, **{'Style (0 solid, 1 wire, 2 points)': style})
        assert mesh_count(alpha) > 100
        render('orbital-' + name)
    set_controls(alpha, **{'Style (0 solid, 1 wire, 2 points)': 0})
    mist = fog.fog_view(spin)
    fog_modifier, fog_sockets = controls(mist)
    fog_material = fog_modifier[fog_sockets['Material']]
    for node in fog_material.node_tree.nodes:
        if node.get('qc_control') in ('Opacity Scale', 'Color Minimum', 'Color Maximum'):
            node.outputs[0].default_value = {'Opacity Scale': 180., 'Color Minimum': -.004, 'Color Maximum': .004}[node['qc_control']]
    hide(spin)
    spin_caption.data.body = 'Spin density: volume fog\nOptical opacity scale 180 (display only)'
    render('spin-fog')
    spin_caption.data.body = 'Spin density: alpha - beta\n+/-0.002 electron/bohr^3'
    hide(mist)
    spin.hide_render = False
    spin.hide_set(False)
    inspection.add_clip(alpha)
    before = mesh_count(alpha)
    center = source.arrays['positions'].mean(axis=0)
    set_controls(alpha, **{'Plane Enabled': True, 'Plane Origin': center.tolist()})
    assert 0 < mesh_count(alpha) < before
    set_controls(alpha, **{'Plane Enabled': False, 'Link Thresholds': False, 'Negative Isovalue': .035})
    assert mesh_count(alpha) > 0
    set_controls(alpha, **{'Link Thresholds': True})
    layers.activate(bpy.context, alpha)
    bpy.context.scene.cursor.location = alpha.qc_settings.volume.matrix_world @ Vector(center)
    assert bpy.ops.qcblender.probe_field() == {'FINISHED'}
    report['probe'] = json.loads(alpha['qc_probe'])
    report['checks']['clip_phase_thresholds_cursor'] = 'Passed'
    assert bpy.ops.qcblender.layer_action(action='DUPLICATE', target=alpha.name) == {'FINISHED'}
    duplicate = bpy.context.object
    set_controls(duplicate, Isovalue=.08)
    assert controls(alpha)[0][controls(alpha)[1]['Isovalue']] != .08
    assert bpy.ops.qcblender.layer_action(action='UP', target=duplicate.name) == {'FINISHED'}
    assert bpy.ops.qcblender.layer_action(action='REMOVE', target=duplicate.name) == {'FINISHED'}
    report['checks']['layer_duplicate_order_remove_independence'] = 'Passed'

elif args.case == 'polar':
    directory = imported('Trp_polar.fchk')
    log = imported('Trp_polar.log')
    source = storage.load_dataset(directory)
    left, right = atoms_at(directory, (-5, 0, 0)), atoms_at(log, (5, 0, 0))
    density = field(directory, left, 'electron_number_density')
    esp = field(directory, left, 'electrostatic_potential')
    set_controls(density, Isovalue=.004)
    scalars.add_mapping(density, esp, -.05, .05)
    hide(esp)
    layers.activate(bpy.context, right)
    assert bpy.ops.qcblender.color_charge(method='mulliken', minimum=-.6, maximum=.6) == {'FINISHED'}
    assert bpy.ops.qcblender.show_dipole() == {'FINISHED'}
    dipole = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'dipole')
    set_controls(dipole, **{'Angstrom per Debye': 1.5})
    set_controls(right, **{'Style (0 ball-stick, 1 space-fill, 2 bonds)': 1, 'VDW Scale': .5})
    # Slice and atom-field mapping are editable alternative views, initially hidden.
    layers.activate(bpy.context, esp)
    assert bpy.ops.qcblender.create_slice(resolution=81, minimum=-.05, maximum=.05) == {'FINISHED'}
    section = bpy.context.object
    set_controls(section, Center=source.arrays['positions'].mean(axis=0).tolist(),
                 Rotation=tuple(left.matrix_world.inverted().to_euler()), Width=8., Height=5.)
    hide(section)
    mapped_atoms = layers.copy_layer(left, bpy.context.collection)
    scalars.add_mapping(mapped_atoms, esp, -.05, .05)
    hide(mapped_atoms)
    caption('Tryptophan | RHF / STO-3G | 27 atoms, neutral singlet', -10, 5.5, .34)
    polar_caption = caption('Density 0.004 electron/bohr^3\nESP: -0.05 (red) to +0.05 (blue) hartree/e', -10, -4.8, .24)
    caption('Mulliken charges: -0.6 to +0.6 e\nDipole from matched log | display: 1.5 angstrom/D', 1, -4.8, .24)
    render('density-esp-charges')
    report['checks']['matched_log_fchk'] = 'Passed (see source-inspection.json)'
    report['checks']['charge_slice_atom_mapping'] = 'Passed'
    report['dipole_e_bohr'] = source.arrays['dipole'].tolist()
    # Show the slice separately so it is inspectable without an opaque surface covering it.
    hide(density)
    section.hide_render = False
    section.hide_set(False)
    polar_caption.data.body = 'ESP slice through mean atomic position\n-0.05 (red) to +0.05 (blue) hartree/e'
    render('esp-slice')
    polar_caption.data.body = 'Density 0.004 electron/bohr^3\nESP: -0.05 (red) to +0.05 (blue) hartree/e'
    hide(section)
    density.hide_render = False
    density.hide_set(False)

elif args.case == 'interaction':
    directory = imported('chemtools-h2o_dimer_pbe_sto3g.fchk')
    atoms = atoms_at(directory)
    atoms.matrix_world = Matrix.Rotation(.65, 4, 'Y') @ atoms.matrix_world
    fields = []
    for filename, quantity, unit in [('rdg-display.cube', 'External RDG (density filtered)', 'dimensionless'),
                                     ('signed-density.cube', 'External sign(lambda2)*rho', 'electron/bohr^3')]:
        raw = job('import', source=str(OUT / 'external-fields' / filename))
        declared = job('declare_field', dataset=str(raw), field_array='cube_0', quantity='custom',
                       custom_quantity=quantity, custom_unit=unit)
        original, interpreted = storage.load_dataset(raw), storage.load_dataset(declared)
        np.testing.assert_array_equal(original.arrays['cube_0'], interpreted.arrays['cube_0'])
        np.testing.assert_allclose(original.arrays['positions'], storage.load_dataset(directory).arrays['positions'], atol=1e-8)
        fields.append(views.field_view(declared, atoms))
    surface, coloring = fields
    set_controls(surface, Isovalue=.5, **{'Negative Phase': False})
    scalars.add_mapping(surface, coloring, -.035, .02)
    set_controls(surface, **{'Color Center': 0.})
    hide(coloring)
    assert mesh_count(surface) > 20
    # Standard NCI colors: attraction blue, near-zero green, repulsion red.
    for mat in bpy.data.materials:
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'VALTORGB' and len(node.color_ramp.elements) == 3:
                    for element, color in zip(node.color_ramp.elements, ((.05,.15,.85,1),(.1,.7,.25,1),(.85,.08,.05,1))):
                        element.color = color
    camera.data.ortho_scale = 9
    caption('Water dimer | PBE / STO-3G', -4, 2.4, .25)
    caption('RDG = 0.5 | color: sign(lambda2)*rho\n-0.035 blue / 0 green / +0.02 red [electron/bohr^3]', -4, -2.1, .16)
    caption('External fields | density window 1e-6 to 0.05 electron/bohr^3', -4, -2.7, .12)
    render('hydrogen-bond-rdg')
    report['checks']['external_cube_values_coordinates_and_mapping'] = 'Passed'

else:
    directory = imported('dvb_ir.out')
    source = storage.load_dataset(directory)
    atoms = atoms_at(directory, (-2, 0, 0))
    assert len(atoms.qc_settings.modes) == 54
    mode = int(np.argmax(source.arrays['mode_ir_intensities']))
    atoms.qc_settings.active_mode = mode
    set_controls(atoms, Animate=True, **{'Show Displacement Vectors': True, 'Amplitude (angstrom)': .35})
    scene.render.fps, scene.frame_start, scene.frame_end, scene.frame_step = 24, 0, 47, 1
    caption('Neutral DVB | B3LYP / STO-3G | 54 normal modes', -10, 5.5, .34)
    caption(f'Mode {mode+1} | {atoms["qc_mode_frequency_cm-1"]:.4f} cm^-1', -10, -4.7)
    caption('Amplitude 0.35 angstrom | playback 1 Hz (not physical time)', -10, -5.5, .23)
    scene.frame_set(6)
    render('vibration-ir')
    report.update(mode=mode+1, frequency_cm_1=atoms['qc_mode_frequency_cm-1'], amplitude_angstrom=.35, playback_hz=1)
    report['checks']['54_modes_IR_source'] = 'Passed'
    if args.animation:
        scene.render.resolution_percentage = 60
        scene.cycles.samples = 12
        scene.render.filepath = str(folder / 'frames/frame-')
        (folder / 'frames').mkdir(exist_ok=True)
        bpy.ops.render.render(animation=True)
        frames = [folder / f'frames/frame-{i:04d}.png' for i in range(48)]
        assert all(p.exists() for p in frames)
        assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in frames}) > 20
        # Blender's native sequencer encodes the rendered frames; no extra package.
        scene.sequence_editor_create()
        strip = scene.sequence_editor.strips.new_image('Vibration frames', str(frames[0]), channel=1, frame_start=0)
        for frame in frames[1:]:
            strip.elements.append(frame.name)
        scene.render.image_settings.media_type = 'VIDEO'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.filepath = str(folder / 'vibration-ir.mp4')
        bpy.ops.render.render(animation=True)
        scene.sequence_editor_clear()
        scene.render.image_settings.media_type = 'IMAGE'
        scene.render.image_settings.file_format = 'PNG'
        scene.render.resolution_percentage = 100
        scene.cycles.samples = 24
        report['checks']['48_frame_animation'] = 'Passed'
    scene.frame_set(6)

# Serialize parameter settings and evaluated geometry, not just a successful save call.
report['layers'] = []
for obj in layers.display_layers(scene):
    entry = {'name': obj.name, 'kind': obj['qc_view_kind'], 'visible_render': not obj.hide_render}
    if obj.modifiers:
        modifier, names = controls(obj)
        entry['parameters'] = {k: (list(modifier[v]) if hasattr(modifier.get(v), 'to_list') else modifier.get(v))
                               for k, v in names.items() if not isinstance(modifier.get(v), bpy.types.ID)}
    if obj['qc_view_kind'] in ('field', 'atoms', 'slice'):
        entry['vertices'] = mesh_count(obj)
    report['layers'].append(entry)
scene['qc_case'] = args.case
scene.render.filepath = str(folder / 'reopened.png')
project.save_project(folder / (args.case + '.blend'))
report.update(status='Passed', blender=bpy.app.version_string, seconds=time.monotonic()-started,
              blend=args.case + '.blend', human_acceptance='Not Run')
(folder / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CASE PASSED', args.case, flush=True)
