"""Check display defaults statically or inside the installed native Blender.

Native mode requires an existing field view in the open acceptance scene. It creates
new atom, field and slice views without changing the existing view's parameters.
Run Python with --static-only, or Blender with --python this_file -- --output-dir DIR.
Quality controls atom tessellation and surface point representation, not field
resolution. Slice resolution changes display sampling, not the source field grid.
"""
import argparse
import ast
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '071a71703482a191393b4dde0a7483e1a5ca093b'
EXPECTED_ASSET_SOURCES = {'asset_catalog.py': '343cec907f02c6898c3b48f855554e342153bb116ecaa3e113190758f853bb6d',
 'blender/assets.py': '194ea7028e364a9a7dd12c20db7692878e90eafb79c2b7e55602feac670b7aa6',
 'blender/fog.py:fog_group': '098c41880b037b2c2310d411a8d7c588b41ca29d44d7634bbba5f5dbf3f472e4',
 'blender/graph.py:arrange': '470c561c78b717be8812da73c3c6b076b6470a18b6077407db76700ed646435a',
 'blender/inspection.py:CLIP_INPUTS': 'f9a5eb40aabeada002648764506d0b5de17a37bf14d61a0b7101dc13545aec1c',
 'blender/inspection.py:clip_group': 'd6d2a0688dcc81d70d02659fa9422a2d2878ae321e90ce27dfad9ec627c275c4',
 'blender/inspection.py:clip_mask': 'a1d4c0ddababb41faa58bcc191a7e471d1a25b738a94b307d3d02be42f08e890',
 'blender/scalars.py:color_fraction': 'd010a4402aac544c32bb7afdc3c590e07f7ce1b74873aa3ada8b061f76060f7a',
 'blender/views.py:atom_selection': 'e92e5ee2c08c223b216b28af3b39784e8fd0566e765ab09656b0abc54c09cba5',
 'blender/views.py:group_sockets': 'ea216b8aaf415519f755daa0565798c13ff512e2f35406cb32cd732d82a1d790',
 'blender/views.py:isosurface_group': '10e8d3be2ff15933b18733e5bde69d182177b55d150df9d71b53e93045ddafa7',
 'blender/views.py:socket': '29865d1c8a5b20a3039877a46fecb7fd3a149ec41567af14e19a456f7f6a2eb3'}


def asset_sources(package):
    for key, expected in EXPECTED_ASSET_SOURCES.items():
        path, _, name = key.partition(':')
        tree = ast.parse((package / path).read_text(encoding='utf-8'))
        node = tree if not name else next(
            n for n in tree.body if getattr(n, 'name', '') == name
            or isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in n.targets))
        actual = hashlib.sha256(ast.dump(node).encode()).hexdigest()
        assert actual == expected, (key, actual, expected)
    return 'Passed'


def socket_default(function, name):
    calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == 'socket'
             and len(n.args) > 1 and isinstance(n.args[1], ast.Constant)
             and n.args[1].value == name]
    assert len(calls) == 1, (function.name, name)
    return ast.literal_eval(next(k.value for k in calls[0].keywords if k.arg == 'default'))


def static_checks(package):
    views = ast.parse((package / 'blender/views.py').read_text(encoding='utf-8'))
    functions = {n.name: n for n in views.body if isinstance(n, ast.FunctionDef)}
    assert socket_default(functions['atom_view'], 'Quality') == 3
    for name in ('field_view', 'isosurface_group'):
        assert socket_default(functions[name], 'Adaptivity') == 0
        assert socket_default(functions[name], 'Smooth Normals') is True
        assert socket_default(functions[name], 'Quality') == 2
    scalars = ast.parse((package / 'blender/scalars.py').read_text(encoding='utf-8'))
    operator = next(n for n in scalars.body if isinstance(n, ast.ClassDef)
                    and n.name == 'QCBLENDER_OT_slice')
    prop = next(n for n in operator.body if isinstance(n, ast.AnnAssign)
                and n.target.id == 'resolution')
    assert ast.literal_eval(next(k.value for k in prop.annotation.keywords if k.arg == 'default')) == 201
    return {'display_defaults': 'Passed', 'public_asset_sources': asset_sources(package)}


def native_checks(args, report):
    import bpy
    import numpy as np

    bpy.ops.preferences.addon_enable(module=args.module)
    package = importlib.import_module(args.module)
    package_path = Path(package.__file__).resolve().parent
    report['installed_source_checks'] = static_checks(package_path)
    report['blender'] = bpy.app.version_string
    report['installed_package'] = str(package_path)
    module = lambda name: importlib.import_module(args.module + '.' + name)
    views, storage = module('blender.views'), module('data')
    graph = module('blender.graph')

    def inputs(obj):
        return {s.name: s for s in graph.view_modifier(obj).node_group.interface.items_tree
                if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}

    def mesh_counts(obj):
        obj.update_tag()
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            return [len(mesh.vertices), len(mesh.polygons)]
        finally:
            evaluated.to_mesh_clear()

    original = bpy.data.objects.get(args.field_object) if args.field_object else next(
        (o for o in bpy.context.scene.objects if o.get('qc_view_kind') == 'field'), None)
    assert original is not None and original.get('qc_view_kind') == 'field', 'Open a field acceptance scene first'
    original_mod = graph.view_modifier(original)
    original_defaults = {s.name: s.default_value for s in inputs(original).values()
                         if s.socket_type in ('NodeSocketInt', 'NodeSocketFloat', 'NodeSocketBool')}
    original_values = {s.identifier: original_mod.get(s.identifier) for s in inputs(original).values()}
    original_groups = set(bpy.data.node_groups)

    atoms = storage.Dataset(
        {'source': {'filename': 'display-precision-synthetic',
                    'sha256': hashlib.sha256(b'display-precision-synthetic').hexdigest()},
         'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': []},
        {'atomic_numbers': np.array([6, 1], dtype=np.int32),
         'positions': np.array([[0., 0., 0.], [2., 0., 0.]]),
         'bonds': np.empty((0, 2), dtype=np.int32)})
    directory = args.output_dir / 'synthetic-atoms.qcdata'
    assert not directory.exists(), 'Use a fresh output directory'
    storage.save_dataset(atoms, directory)
    atom = views.atom_view(directory)
    controls = inputs(atom)
    assert controls['Quality'].default_value == 3
    assert [v.value for v in atom.data.attributes['qc_atom_id'].data] == [0, 1]
    assert [v.value for v in atom.data.attributes['qc_atomic_number'].data] == [6, 1]
    np.testing.assert_allclose([v.co[:] for v in atom.data.vertices], atoms.arrays['positions'])
    assert atom['qc_source_sha256'] == atoms.metadata['source']['sha256']
    default_counts = mesh_counts(atom)
    modifier = graph.view_modifier(atom)
    modifier[controls['Quality'].identifier] = 2
    lower_counts = mesh_counts(atom)
    assert default_counts == [324, 640], default_counts
    assert lower_counts == [84, 160], lower_counts
    modifier[controls['Quality'].identifier] = 3
    assert mesh_counts(atom) == default_counts
    report['atoms'] = {'status': 'Passed', 'source_atom_count': 2,
                       'source_ids': [0, 1], 'quality_3_counts': default_counts,
                       'quality_2_counts': lower_counts}

    field = views.field_view(bpy.path.abspath(original['qc_dataset']),
                             index=storage.load_dataset(bpy.path.abspath(original['qc_dataset'])).metadata['fields'].index(json.loads(original['qc_field'])))
    field_inputs = inputs(field)
    assert field_inputs['Adaptivity'].default_value == 0
    assert field_inputs['Smooth Normals'].default_value is True
    assert field_inputs['Quality'].default_value == 2
    assert bpy.ops.qcblender.create_slice.get_rna_type().properties['resolution'].default == 201
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    field.select_set(True)
    bpy.context.view_layer.objects.active = field
    assert bpy.ops.qcblender.create_slice() == {'FINISHED'}
    sliced = bpy.context.object
    assert sliced.get('qc_view_kind') == 'slice'
    assert inputs(sliced)['Resolution'].default_value == 201
    # Mapping can remove invalid source samples. Check the display grid before
    # mapping separately, then restore the existing output connection.
    slice_tree = graph.view_modifier(sliced).node_group
    output = next(n for n in slice_tree.nodes if n.type == 'GROUP_OUTPUT')
    original_socket = output.inputs['Geometry'].links[0].from_socket
    slice_node = next(n for n in slice_tree.nodes if n.type == 'GROUP'
                      and n.node_tree.get('qc_asset_id') == 'qc.slice.v1')
    try:
        slice_tree.links.new(slice_node.outputs['Geometry'], output.inputs['Geometry'])
        raw_counts = mesh_counts(sliced)
        assert raw_counts == [201 * 201, 200 * 200], raw_counts
    finally:
        slice_tree.links.new(original_socket, output.inputs['Geometry'])
    report['slice'] = {'status': 'Passed', 'samples_per_axis': 201,
                       'raw_display_grid_counts': raw_counts,
                       'mapped_mesh_counts': mesh_counts(sliced)}
    assert {s.name: s.default_value for s in inputs(original).values()
            if s.socket_type in ('NodeSocketInt', 'NodeSocketFloat', 'NodeSocketBool')} == original_defaults
    assert {s.identifier: original_mod.get(s.identifier) for s in inputs(original).values()} == original_values
    report['existing_field_parameters'] = 'Passed'

    catalog = module('asset_catalog').ASSETS
    assert len(catalog) == 9
    owners = {'isosurface_group': views, 'fog_group': module('blender.fog'),
              'clip_group': module('blender.inspection')}
    assets = module('blender.assets')
    signatures = {}
    for asset_id, (_, factory) in catalog.items():
        # Force a fresh factory call so existing scene groups cannot hide defaults.
        old = [g for g in bpy.data.node_groups if g.get('qc_asset_id') == asset_id]
        for group in old:
            del group['qc_asset_id']
        try:
            tree = getattr(owners.get(factory, assets), factory)()
        finally:
            for group in old:
                group['qc_asset_id'] = asset_id
        assert tree not in original_groups and tree['qc_asset_id'] == asset_id
        signatures[asset_id] = [[s.name, s.in_out, s.socket_type]
                               for s in tree.interface.items_tree if s.item_type == 'SOCKET']
        if asset_id in ('qc.atom_style.v1', 'qc.surface_style.v1', 'qc.isosurface.v3'):
            assert next(s.default_value for s in tree.interface.items_tree
                        if s.item_type == 'SOCKET' and s.name == 'Quality') == 2
        if asset_id == 'qc.slice.v1':
            assert next(s.default_value for s in tree.interface.items_tree
                        if s.item_type == 'SOCKET' and s.name == 'Resolution') == 101
    report['public_assets'] = {'status': 'Passed', 'signatures': signatures,
                               'implementation_baseline': BASELINE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only', action='store_true')
    parser.add_argument('--module', default='bl_ext.user_default.qcblender')
    parser.add_argument('--field-object')
    parser.add_argument('--output-dir', type=Path,
                        default=ROOT / 'outputs/evidence/2026-10-02/display-xyz-export/precision')
    arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = parser.parse_args(arguments)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {'status': 'Failed', 'baseline': BASELINE,
              'native_blender': 'Not Run', 'independent_human_acceptance': 'Not Run'}
    try:
        report['static'] = static_checks(ROOT / 'qcblender')
        if not args.static_only:
            native_checks(args, report)
            report['native_blender'] = 'Passed'
        report['status'] = 'Passed'
    except Exception as error:
        report['error'] = str(error)
        if not args.static_only:
            report['native_blender'] = 'Failed'
        raise
    finally:
        filename = 'static.json' if args.static_only else 'native.json'
        (args.output_dir / filename).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
