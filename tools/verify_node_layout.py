"""Real Blender baseline, layout-only regression, and cold-open checks."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--reference-root', type=Path, required=True)
parser.add_argument('--phase', choices=('baseline', 'check', 'reopen'), required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
sys.path[:0] = [str(ROOT), str(args.reference_root / 'outputs/science')]
import qcblender
from qcblender.blender import asset_library, assets, views, scalars, properties, atomic_properties, fog, inspection
from qcblender.blender.graph import view_modifier
from qcblender.data import Dataset, save_dataset, load_dataset
from qcblender.readers import read_source
from qcblender.worker import write_volume
from tools.local_inputs import input_path

# Register source code against a read-only reference library in our own run directory.
library = OUT / 'library'
library.mkdir(exist_ok=True)
with zipfile.ZipFile(args.reference_root / 'outputs/candidates/current/qcblender-0.0.1.zip') as archive:
    entry = next(name for name in archive.namelist() if name.endswith('/assets/nodes.blend') or name == 'assets/nodes.blend')
    (library / 'nodes.blend').write_bytes(archive.read(entry))
asset_library.LIBRARY_DIR = library
asset_library.LIBRARY_FILE = library / 'nodes.blend'
qcblender.register()


def layout(tree):
    return {n.name: [list(n.location), n.parent.name if n.parent else None, n.label, n.width]
            for n in tree.nodes}


def interface(tree):
    return [[s.name, s.identifier, s.in_out, s.socket_type]
            for s in tree.interface.items_tree if s.item_type == 'SOCKET']


def evaluated(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        values = {'vertices': [list(v.co) for v in mesh.vertices],
                  'polygons': [list(p.vertices) for p in mesh.polygons]}
        for name in ('qc_scalar_value', 'qc_sample_valid', 'qc_color_fraction'):
            attr = mesh.attributes.get(name)
            if attr:
                values[name] = [v.value for v in attr.data]
        return values
    finally:
        evaluated.to_mesh_clear()


def state():
    return {o.name: {'interface': interface(view_modifier(o).node_group), 'result': evaluated(o)}
            for o in bpy.context.scene.objects if o.get('qc_view_kind') in ('atoms', 'field', 'slice')}


def public_signatures():
    groups = [factory() for factory in (assets.sample_group, assets.selection_group, assets.atom_style_group,
        assets.surface_style_group, views.isosurface_group, fog.fog_group, assets.color_group,
        assets.slice_group, inspection.clip_group)]
    assert all(not any(node.type == 'FRAME' for node in group.nodes) for group in groups)
    return {group['qc_asset_id']: hashlib.sha256(repr(asset_library._group_signature(group)).encode()).hexdigest()
            for group in groups}


def array_hashes():
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in (OUT / 'atoms', OUT / 'field') for path in sorted(folder.rglob('*')) if path.is_file()}


def customized(tree):
    frame = tree.nodes.new('NodeFrame')
    frame.label = 'User frame'
    frame.location = (-1700, 850)
    node = tree.nodes.new('ShaderNodeValue')
    node.parent = frame
    node.location = (73, -111)
    node.label = 'User note'
    node.width = 257
    return layout(tree)


def preserved(tree, before):
    after = layout(tree)
    assert all(after[name] == expected for name, expected in before.items()), (before, after)


def assert_frames():
    labels = set()
    for obj in bpy.context.scene.objects:
        if obj.get('qc_view_kind') not in ('atoms', 'field', 'slice'):
            continue
        for node in view_modifier(obj).node_group.nodes:
            if node.type == 'FRAME' and node.label != 'User frame':
                assert node.parent is None
                children = [n for n in view_modifier(obj).node_group.nodes if n.parent == node]
                assert children and len({tuple(n.location) for n in children}) == len(children)
                labels.add(node.label)
    assert {'Atoms: selection and representation', 'Field: source and isosurface',
            'Scalar: sampling and colors', 'Legend: range and labels', 'Charge: attributes and colors',
            'Modes: displacement and animation', 'Slice: plane placement'} <= labels, labels
    return sorted(labels)


if args.phase == 'reopen':
    report = json.loads((OUT / 'check.json').read_text(encoding='utf-8'))
    assert state() == report['state']
    assert {o.name: layout(view_modifier(o).node_group) for o in bpy.context.scene.objects
            if o.get('qc_view_kind') in ('atoms', 'field', 'slice')} == report['layout']
    actual_public = public_signatures()
    assert actual_public == report['public'], {key: [report['public'][key], value] for key, value in actual_public.items() if value != report['public'][key]}
    assert array_hashes() == report['arrays']
    assert_frames()
    (OUT / 'reopen.json').write_text(json.dumps({'status': 'Passed', 'blender': bpy.app.version_string}), encoding='utf-8')
    print('NODE_LAYOUT_REOPEN_PASSED')
    raise SystemExit(0)

baseline = json.loads((OUT / 'baseline.json').read_text(encoding='utf-8')) if args.phase == 'check' else None
if baseline:
    bpy.ops.wm.open_mainfile(filepath=str(OUT / 'baseline.blend'))
    assert state() == baseline['state']
    assert {o.name: layout(view_modifier(o).node_group) for o in bpy.context.scene.objects
            if o.get('qc_view_kind') in ('atoms', 'field', 'slice')} == baseline['layout']
    assert public_signatures() == baseline['public']
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
# Remove the loaded legacy outer graphs, but retain public assets to check factory reuse.
for tree in list(bpy.data.node_groups):
    if not tree.get('qc_asset_id'):
        bpy.data.node_groups.remove(tree)

if not baseline:
    source = input_path('log-examples/water_neutral_nbo_opt_freq.out', args.reference_root)
    data = read_source(source, job_index=1)
    save_dataset(data, OUT / 'atoms')
    x, y, z = np.meshgrid(*[np.linspace(-2, 2, 9)] * 3, indexing='ij')
    values = x * np.exp(-x*x-y*y-z*z)
    field = {'quantity': 'analytic_scalar', 'unit': 'test-unit', 'array': 'values', 'valid_mask': 'valid',
             'origin': [-2, -2, -2], 'steps': (np.eye(3)*.5).tolist(), 'shape': [9,9,9],
             'coordinate_unit': 'angstrom', 'vdb': 'field.vdb'}
    analytic = Dataset({'source': {'filename': 'analytic signed grid', 'sha256': hashlib.sha256(values.tobytes()).hexdigest()},
        'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': [field]},
        {'positions': np.array([[0.,0,0]]), 'atomic_numbers': np.array([1], dtype=np.int32),
         'values': values, 'valid': np.ones_like(values, dtype=bool)})
    (OUT / 'field').mkdir(exist_ok=True)
    write_volume(analytic, OUT / 'field/field.vdb')
    field['vdb_sha256'] = hashlib.sha256((OUT / 'field/field.vdb').read_bytes()).hexdigest()
    save_dataset(analytic, OUT / 'field')

atoms = views.atom_view(OUT / 'atoms')
atoms.name = 'Layout atoms'
surface = views.field_view(OUT / 'field')
surface.name = 'Layout surface'
public = public_signatures()
arrays = array_hashes()
before = customized(view_modifier(surface).node_group)
scalars.add_mapping(surface, surface, -.3, .3)
if baseline:
    preserved(view_modifier(surface).node_group, before)
bpy.context.view_layer.objects.active = surface
assert bpy.ops.qcblender.create_slice(resolution=7, minimum=-.3, maximum=.3) == {'FINISHED'}
bpy.context.object.name = 'Layout slice'
before = customized(view_modifier(atoms).node_group)
bpy.context.view_layer.objects.active = atoms
assert bpy.ops.qcblender.color_charge(method='mulliken', minimum=-.4, maximum=.4) == {'FINISHED'}
if baseline:
    preserved(view_modifier(atoms).node_group, before)
assert public_signatures() == public
assert array_hashes() == arrays
report = {'status': 'Passed', 'blender': bpy.app.version_string, 'source_root': str(ROOT),
          'state': state(), 'public': public, 'arrays': arrays,
          'layout': {o.name: layout(view_modifier(o).node_group) for o in bpy.context.scene.objects
                     if o.get('qc_view_kind') in ('atoms', 'field', 'slice')}}
if baseline:
    assert report['state'] == baseline['state']
    assert report['public'] == baseline['public']
    assert report['arrays'] == baseline['arrays']
    report['frame_labels'] = assert_frames()
    # Newly added animation nodes must also preserve a deliberately edited existing graph.
    plain = views.atom_view(OUT / 'field')
    before = customized(view_modifier(plain).node_group)
    properties.add_animation_nodes(plain)
    preserved(view_modifier(plain).node_group, before)
    bpy.data.objects.remove(plain, do_unlink=True)
    # A connected custom branch and nested user frames survive a later mapping insertion.
    probe = views.field_view(OUT / 'field')
    tree = view_modifier(probe).node_group
    customized(tree)
    outer = tree.nodes.new('NodeFrame')
    outer.location = (-500, 600)
    user_frame = next(node for node in tree.nodes if node.type == 'FRAME' and node.label == 'User frame')
    user_frame.parent = outer
    transform = tree.nodes.new('GeometryNodeTransform')
    transform.parent = user_frame
    transform.location = (90, -400)
    output = next(node for node in tree.nodes if node.type == 'GROUP_OUTPUT').inputs['Geometry']
    tree.links.new(output.links[0].from_socket, transform.inputs['Geometry'])
    tree.links.new(transform.outputs['Geometry'], output)
    before = layout(tree)
    retained_links = {(link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier)
                      for link in tree.links if link.to_socket != output}
    scalars.add_mapping(probe, probe, -.3, .3)
    preserved(tree, before)
    actual_links = {(link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier)
                    for link in tree.links}
    assert retained_links <= actual_links
    bpy.data.objects.remove(probe, do_unlink=True)
    from qcblender.blender.graph import frame_nodes
    public_tree = assets.color_group()
    try:
        frame_nodes(public_tree, list(public_tree.nodes), 'Rejected public layout')
    except ValueError:
        pass
    else:
        raise AssertionError('Public asset accepted outer-view layout')
    assert public_signatures() == public
phase = args.phase
(OUT / f'{phase}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'{phase}.blend'))
print('NODE_LAYOUT_' + phase.upper() + '_PASSED')
