"""Loads the Nunito font files shipped in assets/fonts for this program only (not installed on the PC).

Windows keeps a font added with the "private" flag until the program closes. Tk finds it by family name.
"""

import sys

from app.core import paths

FONT_FILES = ("Nunito-Regular.ttf", "Nunito-Bold.ttf")
FR_PRIVATE = 0x10


def load_fonts() -> bool:
    """True when both Nunito files were loaded. False on another system or a missing file: use the fallback font."""
    if sys.platform != "win32":
        return False
    import ctypes

    loaded = 0
    for name in FONT_FILES:
        path = paths.asset_file("fonts") / name
        if path.exists() and ctypes.windll.gdi32.AddFontResourceExW(str(path), FR_PRIVATE, 0):
            loaded += 1
    return loaded == len(FONT_FILES)
