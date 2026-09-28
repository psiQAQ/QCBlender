"""Rebuild regression scenes from verified local inputs using the installed extension."""
import importlib
from pathlib import Path
import sys
import time

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.local_inputs import input_path

MODULE = 'bl_ext.user_default.qcblender'


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def job(action, **kwargs):
    pending = module('blender.jobs').Job(action, **kwargs)
    deadline = time.monotonic() + 900
    try:
        while time.monotonic() < deadline:
            result = pending.poll()
            if result is not None:
                if result['status'] != 'succeeded':
                    raise RuntimeError(result)
                return pending.directory / 'dataset'
            time.sleep(.1)
        raise TimeoutError(str(pending.directory))
    except BaseException:
        pending.cancel()
        raise


def active(obj):
    module('blender.layers').activate(bpy.context, obj)
    module('blender.source_browser').refresh_source(obj)


def real_fields(root=None):
    """Actual density/ESP on a modest grid; display tests do not require a fine surface."""
    source = job('import', source=str(input_path('complex-examples/Trp_polar.fchk', root)))
    positions = module('data').load_dataset(source).arrays['positions']
    origin = positions.min(axis=0) - 2.5
    spacing = .7
    grid = dict(origin=origin.tolist(), steps=(np.eye(3) * spacing).tolist(),
                shape=(np.ceil((positions.max(axis=0) + 2.5 - origin) / spacing).astype(int) + 1).tolist())
    atoms = module('blender.views').atom_view(source)
    fields = {}
    for key in ('electron_number_density', 'electrostatic_potential'):
        directory = job('evaluate', dataset=str(source), grid=grid,
                        parameters={'quantity': key, 'memory_mb': 512})
        fields[key] = module('blender.views').field_view(directory, atoms)
    return fields


def paired_dataset(method, root=None):
    directory = job('import', source=str(input_path('sop/c07-c09-research/file/PhenolDimer.fchk', root)))
    atoms = module('blender.views').atom_view(directory)
    folder = input_path('sop/c07-c09-research/phenol-2026-09-27/' + method.lower(), root)
    geometry, color, unit = ('dg_inter.cub', 'sl2r.cub', 'electron/bohr^4') if method == 'IGMH' else (
        'func2.cub', 'func1.cub', 'a.u. (electron^-0.1 bohr^-0.7)')
    paired = job('import_pair', geometry_source=str(folder / geometry), color_source=str(folder / color),
                 method=method, geometry_unit=unit, color_unit='electron/bohr^3',
                 iri_exponent=1.1 if method == 'IRI' else None,
                 reference_dataset=str(directory), reference_sha256=atoms['qc_dataset_sha256'])
    return paired, atoms


def prepare(case, root=None):
    """Replace the test scene. Call only in a dedicated acceptance process."""
    bpy.ops.preferences.addon_enable(module=MODULE)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    views = module('blender.views')
    if case in ('C04', 'C08'):
        fields = real_fields(root)
        surface, color = fields['electron_number_density'], fields['electrostatic_potential']
        module('blender.scalars').add_mapping(surface, color, -.05, .05)
        color.hide_render = True
        color.hide_set(True)
        active(surface)
        if case == 'C08':
            active(color)
            folder = input_path('sop/multiwfn-local/C08', root)
            assert bpy.ops.qcblender.import_esp_analysis(
                extrema_path=str(folder / 'surfanalysis.pdb'), area_path=str(folder / 'stdout.log'),
                center_unit='kcal/mol') == {'FINISHED'}
    elif case == 'C07':
        paired, atoms = paired_dataset('IGMH', root)
        data = module('data').load_dataset(paired)
        surface, color = (views.field_view(paired, atoms, i) for i in (0, 1))
        module('blender.scalars').add_mapping(surface, color, -.05, .05)
        color.hide_set(True)
        color.hide_render = True
        module('blender.external_fields').scatter_view(paired, data, atoms)
        active(surface)
    elif case == 'NBO':
        source = input_path('log-examples/water_neutral_nbo_opt_freq.out', root)
        directory = job('import', source=str(source), job_index=1)
        atoms = views.atom_view(directory)
        result = job('import_nbo', source=str(source), job_index=1, block_index=0,
                     reference_dataset=str(directory), reference_sha256=atoms['qc_dataset_sha256'])
        data = module('data').load_dataset(result)
        obj = bpy.data.objects.new('QC NBO records', bpy.data.meshes.new('QC NBO records'))
        bpy.context.collection.objects.link(obj)
        obj.parent = atoms
        views.bind(obj, result, data)
        obj['qc_view_kind'], obj['qc_nbo_index'], obj['qc_e2_index'] = 'nbo', 1, 1
        active(obj)
    elif case == 'C09':
        atoms = views.atom_view(job('import', source=str(input_path('complex-examples/Trp_polar.fchk', root))))
        active(atoms)
        folder = input_path('sop/multiwfn-local/C09', root)
        assert bpy.ops.qcblender.import_aim_analysis(cps_path=str(folder / 'CPs.pdb'),
            paths_path=str(folder / 'paths.pdb'), properties_path=str(folder / 'CPprop.txt')) == {'FINISHED'}
    elif case in ('C10', 'C11'):
        folder = input_path('sop/c10-c13/peroxide-irc-pyscf', root)
        assert bpy.ops.qcblender.import_irc_path(manifest_path=str(folder / 'steps.csv')) == {'FINISHED'}
        atoms = next(obj for obj in bpy.context.scene.objects if obj.get('qc_irc'))
        active(atoms)
        if case == 'C11':
            assert bpy.ops.qcblender.import_irc_mayer(manifest_path=str(folder / 'mayer-pyscf.csv')) == {'FINISHED'}
    elif case in ('C12', 'C13'):
        base = input_path('sop/c10-c13', root)
        fchk = base / 'multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/COBH3.fch'
        atoms = views.atom_view(job('import', source=str(fchk)))
        active(atoms)
        folder = base / 'multiwfn-cobh3-20260927'
        assert bpy.ops.qcblender.import_ets_nocv(output_path=str(folder / 'COBH3-ETS-NOCV.txt'), energy_unit='kcal/mol') == {'FINISHED'}
        if case == 'C13':
            table = next(obj for obj in bpy.context.scene.objects if obj.get('qc_analysis_role') == 'ets_nocv')
            directory = job('import_nocv', source=str(folder / 'COBH3-NOCV-pair1.cub'),
                table_dataset=bpy.path.abspath(table['qc_dataset']), table_sha256=table['qc_dataset_sha256'],
                pair_number=1, spin='Total', unit='electron/bohr^3')
            views.field_view(directory, atoms)
    else:
        raise ValueError(f'No raw-input fixture builder for {case}')
    module('blender.source_browser').refresh_loaded_sources()
