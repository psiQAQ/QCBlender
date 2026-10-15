"""Build the extension's data-only node asset library inside Blender."""

import argparse
from pathlib import Path
import sys


def main():
    import bpy

    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    package_root = args.package_root.resolve()
    sys.path.insert(0, str(package_root.parent))

    from qcblender.asset_catalog import ASSETS, catalog_id, catalog_text
    from qcblender.blender import assets, fog, inspection, views
    from qcblender.blender.node_identity import localize_tree

    factories = {'sample_group': assets.sample_group,
                 'selection_group': assets.selection_group,
                 'atom_style_group': assets.atom_style_group,
                 'surface_style_group': assets.surface_style_group,
                 'isosurface_group': views.isosurface_group,
                 'fog_group': fog.fog_group,
                 'color_group': assets.color_group,
                 'slice_group': assets.slice_group,
                 'clip_group': inspection.clip_group}
    groups = set()
    for asset_id, (category, factory_name) in ASSETS.items():
        group = factories[factory_name]()
        if group.get('qc_asset_id') != asset_id:
            raise RuntimeError(f'Wrong node asset identity: {asset_id}')
        group.asset_mark()
        group.asset_data.catalog_id = catalog_id(category)
        group.asset_data.description = 'Reusable QC display node group'
        groups.add(group)
    if len(groups) != len(ASSETS):
        raise RuntimeError('Node assets must have distinct datablocks')

    destination = package_root / 'assets'
    destination.mkdir(exist_ok=True)
    # The canonical root library remains the compatibility/rebuild entry point.
    for group in groups:
        localize_tree(group, 'en_US')
    (destination / 'blender_assets.cats.txt').write_text(catalog_text('en_US'), encoding='utf-8')
    bpy.data.libraries.write(str(destination / 'nodes.blend'), groups, fake_user=True)
    for language in ('en_US', 'zh_HANS'):
        localized = destination / language
        localized.mkdir(exist_ok=True)
        for group in groups:
            localize_tree(group, language)
        (localized / 'blender_assets.cats.txt').write_text(catalog_text(language), encoding='utf-8')
        bpy.data.libraries.write(str(localized / 'nodes.blend'), groups, fake_user=True)
    print(f'Built {len(groups)} QC node assets in {destination}')


if __name__ == '__main__':
    main()
