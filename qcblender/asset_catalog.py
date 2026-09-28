"""Stable catalog identities for the nine reusable QC node groups."""

from uuid import UUID, uuid5


NAMESPACE = UUID('0c783d7e-c62e-4d77-9f9f-22adfb969687')

# The paths are Blender catalog paths; the keys are persistent node group IDs.
CATEGORIES = (
    '数据/采样', '原子选择', '表示', '表示/原子与键', '表示/表面',
    '表示/体积', '颜色映射', '空间', '空间/切片', '空间/裁剪',
)
ASSETS = {
    'qc.sample.v1': ('数据/采样', 'sample_group'),
    'qc.atom_selection.v1': ('原子选择', 'selection_group'),
    'qc.atom_style.v1': ('表示/原子与键', 'atom_style_group'),
    'qc.surface_style.v1': ('表示/表面', 'surface_style_group'),
    'qc.isosurface.v3': ('表示/表面', 'isosurface_group'),
    'qc.volume_fog.v1': ('表示/体积', 'fog_group'),
    'qc.color_scalar.v2': ('颜色映射', 'color_group'),
    'qc.slice.v1': ('空间/切片', 'slice_group'),
    'qc.clip.v1': ('空间/裁剪', 'clip_group'),
}


def catalog_id(path):
    return str(uuid5(NAMESPACE, path))


def catalog_text():
    return ('# Blender Asset Catalog Definition File\nVERSION 1\n\n'
            + ''.join(f'{catalog_id(path)}:{path}:{path.rsplit("/", 1)[-1]}\n'
                      for path in CATEGORIES))
