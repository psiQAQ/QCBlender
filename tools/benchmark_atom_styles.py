"""Measure one atom carrier: creation, real node evaluation and mesh extraction.

Run with Blender --background --factory-startup --python-exit-code 1 --python
THIS_FILE -- --output NEW_DIR --profile-root FRESH_PROFILE [--candidate ZIP].
Use the isolated BLENDER_USER_CONFIG/BLENDER_USER_EXTENSIONS/TEMP/TMP layout
required by benchmark_fields.py. This script never starts or kills Blender.
Synthetic repeated CH4 geometry is an engineering load, not a new scientific
system or evidence of independent scientific acceptance.
"""
import argparse
import ctypes
import itertools
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import benchmark_fields as bench
from tools.package_identity import extension_manifest

STYLES = {'ball-stick': 0, 'space-fill': 1, 'bonds': 2}
STYLE_SOCKET = 'Style (0 ball-stick, 1 space-fill, 2 bonds)'


def styles(value):
    result = value.split(',')
    if not result or len(set(result)) != len(result) or any(item not in STYLES for item in result):
        raise argparse.ArgumentTypeError('Use distinct styles from ball-stick,space-fill,bonds')
    return result


def parser():
    result = bench.parser(__doc__, 'atoms', '32,128,512')
    result.set_defaults(repeats=3)
    result.add_argument('--qualities', type=bench.integers, default=[1, 3])
    result.add_argument('--styles', type=styles, default=list(STYLES))
    result.add_argument('--max-cases', type=bench.positive, default=100)
    result.add_argument('--max-trials', type=bench.positive, default=1000,
                        help='Includes warmups and both cold/warm conditions')
    result.add_argument('--max-estimated-vertices', type=bench.positive, default=2_000_000,
                        help='Conservative per-carrier geometry budget; override explicitly')
    result.add_argument('--max-estimated-total-vertices', type=bench.positive, default=100_000_000)
    return result


def validate_budget(args):
    if args.warmups < 0:
        raise ValueError('Warmups cannot be negative')
    if any(count < 5 or count > 1_000_000 for count in args.atoms):
        raise ValueError('Atom counts must be between 5 and 1000000')
    if any(quality < 1 or quality > 6 for quality in args.qualities):
        raise ValueError('Quality must be between 1 and 6')
    cases = list(itertools.product(args.atoms, args.styles, args.qualities))
    trials = len(cases) * (args.warmups + args.repeats) * 2
    # Upper bound for the current ico spheres plus an intentionally generous
    # tube allowance. This is a safety estimate, never a measured mesh count.
    vertices = [count * ((10 * 4 ** (quality - 1) + 2 if style != 'bonds' else 0) + 32)
                for count, style, quality in cases]
    total = sum(vertices) * (args.warmups + args.repeats) * 2
    if (len(cases) > args.max_cases or trials > args.max_trials
            or max(vertices) > args.max_estimated_vertices or total > args.max_estimated_total_vertices):
        raise ValueError('Matrix exceeds explicit case/trial/geometry budget')
    return {'cases': len(cases), 'trials_including_warmups': trials,
            'estimated_max_vertices': max(vertices), 'estimated_total_vertices': total,
            'limits': {'cases': args.max_cases, 'trials': args.max_trials,
                       'estimated_vertices_per_carrier': args.max_estimated_vertices,
                       'estimated_total_vertices': args.max_estimated_total_vertices},
            'estimate': 'Ico sphere vertices plus 32 tube vertices per atom; not measured output'}


def generate_geometry(numbers, positions, bonds, count):
    """Repeat seed order on a separated cubic lattice, retaining in-copy bonds.

    Exactly count atoms are retained; the final seed copy may be truncated.
    Bonds are copied from the imported seed, never inferred between copies.
    This pure-Python function does not modify any supplied sequence.
    """
    if len(numbers) != 5 or sorted(numbers) != [1, 1, 1, 1, 6]:
        raise ValueError('Expected the frozen five-atom CH4 seed')
    if len(positions) != len(numbers) or any(len(point) != 3 for point in positions):
        raise ValueError('Seed coordinate layout is invalid')
    if any(not math.isfinite(float(value)) for point in positions for value in point):
        raise ValueError('Seed positions must be finite')
    if type(count) is not int or not 5 <= count <= 1_000_000:
        raise ValueError('Atom count must be between 5 and 1000000')
    carbon = numbers.index(6)
    expected = {tuple(sorted((carbon, index))) for index in range(5) if index != carbon}
    if (len(bonds) != 4 or any(len(edge) != 2 for edge in bonds)
            or {tuple(sorted(edge)) for edge in bonds} != expected):
        raise ValueError('Expected the frozen seed four C-H bonds')
    copies = (count + 4) // 5
    side = math.ceil(copies ** (1 / 3))
    while side ** 3 < copies:
        side += 1
    # Fixed rule, recorded in generated metadata; seed coordinates stay intact.
    span = max(max(point[axis] for point in positions) - min(point[axis] for point in positions)
               for axis in range(3))
    spacing = max(8., span + 6.)
    output_numbers, output_positions, output_bonds = [], [], []
    for copy in range(copies):
        offset = [(copy % side) * spacing, ((copy // side) % side) * spacing,
                  (copy // (side * side)) * spacing]
        start = len(output_numbers)
        keep = min(5, count - start)
        output_numbers.extend(numbers[:keep])
        output_positions.extend([[float(point[axis]) + offset[axis] for axis in range(3)]
                                 for point in positions[:keep]])
        output_bonds.extend([[start + a, start + b] for a, b in bonds if a < keep and b < keep])
    return {'atomic_numbers': output_numbers, 'positions': output_positions, 'bonds': output_bonds}, {
        'algorithm': 'repeat-seed-cubic-lattice-v1', 'seed_atoms': 5, 'seed_bonds': 4,
        'copies': copies, 'lattice_side': side, 'spacing_angstrom': spacing,
        'retained_atoms_in_last_copy': (count - 1) % 5 + 1,
        'bond_rule': 'Copy seed bonds with retained endpoints; no inter-copy bonds',
        'scientific_scope': 'Synthetic engineering geometry; not a new calculated scientific system'}


def file_identity(directory):
    """Hash every dataset file, including manifest bytes; detect extra files."""
    return {path.relative_to(directory).as_posix(): bench.sha256(path)
            for path in sorted(directory.rglob('*')) if path.is_file()}


def memory():
    """Current and lifetime peak Windows process working set, in MiB."""
    if os.name != 'nt':
        raise RuntimeError('This baseline requires Windows GetProcessMemoryInfo')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = bench.wintypes.HANDLE
    get_info = ctypes.WinDLL('psapi', use_last_error=True).GetProcessMemoryInfo
    get_info.argtypes = [bench.wintypes.HANDLE, ctypes.POINTER(bench.MemoryCounters), bench.wintypes.DWORD]
    get_info.restype = bench.wintypes.BOOL
    counters = bench.MemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    if not get_info(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return {'current_working_set_mib': counters.WorkingSetSize / 1024 ** 2,
            'process_lifetime_peak_working_set_mib': counters.PeakWorkingSetSize / 1024 ** 2}


def timed(action, timeout):
    before = memory()
    start = time.perf_counter()
    value = action()
    seconds = time.perf_counter() - start
    after = memory()
    if seconds > timeout:
        raise TimeoutError(f'Blocking stage exceeded {timeout}s after return: {seconds}s')
    return value, {'seconds': seconds, 'memory_before': before, 'memory_after': after,
                   **after}


def create(directory, style, quality):
    obj = bench.module('blender.views').atom_view(directory)
    modifier = bench.module('blender.graph').view_modifier(obj)
    sockets = {item.name: item.identifier for item in modifier.node_group.interface.items_tree
               if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    modifier[sockets[STYLE_SOCKET]] = STYLES[style]
    modifier[sockets['Quality']] = quality
    obj.data.update()
    obj.update_tag(refresh={'OBJECT', 'DATA'})
    return obj


def evaluate(obj):
    import bpy
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    graph.update()
    evaluated = obj.evaluated_get(graph)
    # Touch evaluated data here, before to_mesh, so the evaluation stage cannot
    # succeed from a modifier write alone or defer its entire work to extraction.
    return {'vertices': len(evaluated.data.vertices), 'edges': len(evaluated.data.edges),
            'polygons': len(evaluated.data.polygons)}


def extract(obj):
    import bpy
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=bpy.context.evaluated_depsgraph_get())
    try:
        return {'meshes': 1, 'vertices': len(mesh.vertices), 'edges': len(mesh.edges),
                'polygons': len(mesh.polygons), 'material_slots': len(mesh.materials)}
    finally:
        evaluated.to_mesh_clear()


def validate_carrier(obj, arrays):
    import numpy as np
    mesh = obj.data
    if len(mesh.vertices) != len(arrays['atomic_numbers']) or len(mesh.edges) != len(arrays['bonds']):
        raise ValueError('Source atom/edge count changed')
    for name, expected in (('qc_atom_id', range(len(mesh.vertices))),
                           ('qc_atomic_number', arrays['atomic_numbers'])):
        attribute = mesh.attributes.get(name)
        if (attribute is None or attribute.domain != 'POINT' or attribute.data_type != 'INT'
                or [item.value for item in attribute.data] != list(expected)):
            raise ValueError('Source atom identity changed: ' + name)
    coords = np.empty(len(mesh.vertices) * 3, dtype=float)
    mesh.vertices.foreach_get('co', coords)
    if not np.allclose(coords.reshape(-1, 3), arrays['positions'], rtol=1e-6, atol=1e-5):
        raise ValueError('Source carrier positions changed')
    edges = {tuple(sorted(edge.vertices)) for edge in mesh.edges}
    if edges != {tuple(sorted(edge)) for edge in arrays['bonds']}:
        raise ValueError('Source carrier bond endpoints changed')


def graph_counts(obj):
    """Count reachable groups once, plus the actually referenced material tree."""
    tree = bench.module('blender.graph').view_modifier(obj).node_group
    groups, materials = {}, {}
    pending = [tree]
    while pending:
        group = pending.pop()
        if group.as_pointer() in groups:
            continue
        groups[group.as_pointer()] = group
        for node in group.nodes:
            nested = getattr(node, 'node_tree', None)
            if nested is not None:
                pending.append(nested)
        for item in group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.socket_type == 'NodeSocketMaterial':
                material = item.default_value
                if material:
                    materials[material.as_pointer()] = material
    return {'geometry_node_groups': len(groups), 'geometry_nodes': sum(len(g.nodes) for g in groups.values()),
            'materials': len(materials),
            'material_nodes': sum(len(mat.node_tree.nodes) for mat in materials.values() if mat.use_nodes)}


class OwnedScene:
    """Only delete data created by this benchmark; keep reusable assets for warm."""
    def __init__(self):
        import bpy
        if bpy.data.filepath:
            raise ValueError('Use --factory-startup without a loaded user project')
        if any(group.get('qc_asset_id') for group in bpy.data.node_groups):
            raise ValueError('Cold condition requires no preexisting QC node assets; use a fresh factory startup')
        self.previous = bpy.context.window.scene
        self.scene = bpy.data.scenes.new('QC atom benchmark')
        bpy.context.window.scene = self.scene
        self.original = {name: {item.as_pointer() for item in getattr(bpy.data, name)}
                         for name in ('objects', 'meshes', 'node_groups', 'materials')}

    def clear(self, retain_assets=False):
        import bpy
        for obj in list(self.scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for _ in range(4):
            for name in ('meshes', 'node_groups', 'materials'):
                collection = getattr(bpy.data, name)
                for item in list(collection):
                    if item.as_pointer() in self.original[name] or item.users:
                        continue
                    if retain_assets and name == 'node_groups' and item.get('qc_asset_id'):
                        continue
                    collection.remove(item)

    def close(self):
        import bpy
        self.clear()
        bpy.context.window.scene = self.previous
        bpy.data.scenes.remove(self.scene)


def main():
    args = parser().parse_args(bench.cli_arguments())
    budget = validate_budget(args)
    report = bench.setup(args, 'atom-styles')
    scene = None
    try:
        bench.enable(args, report)
        installed = Path(report['provenance']['installed_root'])
        manifest = installed / 'blender_manifest.toml'
        if bench.sha256(manifest) != bench.sha256(ROOT / 'qcblender/blender_manifest.toml'):
            raise ValueError('Installed extension manifest differs from checkout')
        report['environment']['qcblender_version'] = extension_manifest(ROOT)['version']
        report['provenance']['installed_manifest_sha256'] = bench.sha256(manifest)
        report['provenance']['tool_sha256']['benchmark_atom_styles.py'] = bench.sha256(__file__)
        report['provenance']['product_tree'] = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD:qcblender'], cwd=ROOT, text=True).strip()
        report['provenance']['product_tracked_changes'] = subprocess.check_output(
            ['git', 'status', '--porcelain', '--', 'qcblender'], cwd=ROOT, text=True).splitlines()
        if report['provenance']['product_tracked_changes']:
            raise ValueError('Product source must match the recorded Git tree')
        report['parameters'] = {'atoms': args.atoms, 'styles': args.styles, 'qualities': args.qualities,
                                'repeats': args.repeats, 'warmups': args.warmups, 'timeout': args.timeout,
                                'budget': budget, 'atom_radius': .25, 'bond_radius': .07, 'vdw_scale': 1.,
                                'bond_profile_resolution': 8}
        report['timing_definition'] = {
            'creation': 'atom_view including Dataset load, attributes, graph/material construction and Style/Quality writes; no explicit depsgraph update',
            'evaluation': 'view_layer.update + depsgraph.update + evaluated_get and evaluated mesh counts; real Geometry Nodes work',
            'extraction': 'to_mesh of completed evaluated object, counts, and to_mesh_clear; no graph edits',
            'cold': 'Fresh carrier and freshly rebuilt benchmark node assets; process stays alive; OS caches not flushed',
            'warm': 'Fresh carrier reusing node assets from its paired cold trial; Dataset is read again; OS caches not flushed',
            'warmups': 'Complete cold/warm pairs excluded from summary; every formal pair still rebuilds its cold assets',
            'memory': 'GetProcessMemoryInfo in this Blender process, current WorkingSetSize at stage boundaries and process-lifetime PeakWorkingSetSize; lifetime peak is not reset or attributable to an individual stage',
            'timeout': 'Blocking native calls checked after return; caller must enforce any hard process deadline',
            'validation': 'Input hashes, raw carrier IDs/elements/positions/bonds and mesh repeatability checked outside timers',
            'position_tolerance': {'relative': 1e-6, 'absolute_angstrom': 1e-5},
            'quality_bonds': 'Current bond tube resolution is fixed at 8; Quality changes sphere subdivision, including when spheres are hidden',
        }
        # Read the frozen seed in this process. The usual Job import launches
        # another Blender worker; this benchmark deliberately keeps one process.
        seed, report['initial_import'] = timed(lambda: bench.module('readers').read_source(bench.SOURCE), args.timeout)
        if seed.metadata['source']['sha256'] != report['source']['sha256']:
            raise ValueError('Imported seed source differs from the recorded input')
        source = args.output / 'seed.qcdata'
        bench.module('data').save_dataset(seed, source)
        seed_identity = file_identity(source)
        report['seed_dataset'] = {'path': str(source), 'files': seed_identity}
        report['generated_datasets'], report['scientific_identity'], report['summary'] = {}, {}, {}
        scene = OwnedScene()
        for count in args.atoms:
            generated, parameters = generate_geometry(seed.arrays['atomic_numbers'].tolist(),
                seed.arrays['positions'].tolist(), seed.arrays['bonds'].tolist(), count)
            import numpy as np
            arrays = {key: np.asarray(value, dtype=np.float64 if key == 'positions' else np.int32)
                      for key, value in generated.items()}
            metadata = {'title': f'Engineering CH4 repetitions: {count} atoms',
                        'source': {'filename': 'synthetic-repeat-of-' + bench.SOURCE.name,
                                   'sha256': report['source']['sha256']},
                        'coordinate_unit': 'angstrom', 'calculation_status': 'synthetic-engineering',
                        'fields': [], 'benchmark_generation': parameters}
            directory = args.output / f'atoms-{count}.qcdata'
            bench.module('data').save_dataset(bench.module('data').Dataset(metadata, arrays), directory)
            identity = file_identity(directory)
            report['scientific_identity'][str(count)] = identity
            report['generated_datasets'][str(count)] = {'path': str(directory), 'atoms': count,
                'bonds': len(arrays['bonds']), 'generation': parameters, 'files': identity}
            for style, quality in itertools.product(args.styles, args.qualities):
                case = f'{count}/{style}/quality-{quality}'
                expected_mesh = None
                for iteration in range(args.warmups + args.repeats):
                    pair = {'case': case, 'iteration': iteration, 'atoms': count,
                            'bonds': len(arrays['bonds']), 'style': style, 'quality': quality,
                            'blender_process_id': os.getpid()}
                    (report['warmups'] if iteration < args.warmups else report['trials']).append(pair)
                    for condition in ('cold', 'warm'):
                        scene.clear(retain_assets=condition == 'warm')
                        trial = pair[condition] = {}
                        obj, trial['creation'] = timed(lambda: create(directory, style, quality), args.timeout)
                        evaluated, trial['evaluation'] = timed(lambda: evaluate(obj), args.timeout)
                        mesh, trial['extraction'] = timed(lambda: extract(obj), args.timeout)
                        trial.update(evaluated_mesh=mesh, graph=graph_counts(obj),
                                     carrier_objects=len(scene.scene.objects))
                        if trial['carrier_objects'] != 1:
                            raise ValueError('Expected exactly one benchmark carrier object')
                        if (mesh['vertices'] <= 0 or mesh['polygons'] <= 0
                                or any(mesh[key] != evaluated[key] for key in ('vertices', 'edges', 'polygons'))):
                            raise ValueError('Expected a real nonempty evaluated mesh matching extraction')
                        if expected_mesh is not None and mesh != expected_mesh:
                            raise ValueError('Evaluated mesh changed across identical cold/warm trials')
                        expected_mesh = mesh
                        validate_carrier(obj, arrays)
                        if (file_identity(directory) != identity or file_identity(source) != seed_identity
                                or bench.sha256(bench.SOURCE) != report['source']['sha256']):
                            raise ValueError('Generated Dataset, seed Dataset or original input changed')
                        bench.save(args.output, report)
                formal = [record for record in report['trials'] if record['case'] == case]
                for condition, stage in itertools.product(('cold', 'warm'), ('creation', 'evaluation', 'extraction')):
                    report['summary'][f'{case}/{condition}/{stage}'] = bench.summary(
                        [record[condition][stage] for record in formal])
        scene.close()
        scene = None
        report['status'] = 'Passed'
        if args.baseline:
            report['comparison'] = bench.compare(report, args.baseline)
        bench.save(args.output, report)
    except BaseException as error:
        report.update(status='Failed', error=f'{type(error).__name__}: {error}')
        if hasattr(error, 'job_directory'):
            report['failed_job_directory'] = error.job_directory
        bench.save(args.output, report)
        raise
    finally:
        if scene is not None:
            scene.close()


if __name__ == '__main__':
    main()
