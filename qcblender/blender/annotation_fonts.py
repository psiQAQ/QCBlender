"""Use the Blender-distributed CJK font for portable annotation text."""
from pathlib import Path

import bpy


def annotation_font():
    """Return a packed CJK font; do not alter any user's selected font."""
    path = Path(bpy.utils.system_resource('DATAFILES')) / 'fonts/Noto Sans CJK Regular.woff2'
    if not path.is_file():
        raise ValueError('The Blender-distributed CJK annotation font is missing')
    font = bpy.data.fonts.load(str(path), check_existing=True)
    if font.packed_file is None:
        font.pack()
    if font.packed_file is None:
        raise ValueError('The CJK annotation font could not be packed into the project')
    return font
