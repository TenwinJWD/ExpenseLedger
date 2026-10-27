"""Gradient drawing for the Windows app (Design.md 1.3; matches the mockup's CSS gradients).

Tkinter cannot paint CSS gradients, so they are drawn here:
- GradientCanvas paints a vertical gradient behind its contents and repaints on resize.
- gradient_color() gives the colour at any height, so widgets on top can match it.
- GradientButton draws the rounded primary button as a gradient image with a PNG built in code.
Nothing here needs Pillow: the PNG is written with the standard library.
"""

import struct
import tkinter as tk
import zlib
from typing import Callable

import customtkinter as ctk

from app.core import theme
from app.ui import widgets


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgb_to_hex(rgb) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in rgb))


def gradient_color(top: str, bottom: str, fraction: float) -> str:
    """The colour at a fraction (0 = top, 1 = bottom) of a vertical gradient."""
    start, end = hex_to_rgb(top), hex_to_rgb(bottom)
    fraction = max(0.0, min(1.0, fraction))
    return rgb_to_hex(start[i] + (end[i] - start[i]) * fraction for i in range(3))


class GradientCanvas(tk.Canvas):
    """A canvas that paints a vertical gradient and repaints when it is resized."""

    STEP = 2  # pixels per band; 2 keeps the gradient smooth and the redraw fast

    def __init__(self, master, top: str, bottom: str, **kwargs) -> None:
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self.top = top
        self.bottom = bottom
        self.bind("<Configure>", lambda _event: self.paint())

    def paint(self) -> None:
        self.delete("gradient")
        height = max(1, self.winfo_height())
        width = max(1, self.winfo_width())
        for y in range(0, height, self.STEP):
            colour = gradient_color(self.top, self.bottom, y / height)
            self.create_rectangle(0, y, width, y + self.STEP, fill=colour, outline="", tags="gradient")
        self.tag_lower("gradient")
        self.on_repaint()

    def on_repaint(self) -> None:
        """Hook for subclasses that move widgets when the size changes."""

    def colour_at(self, y: float) -> str:
        height = max(1, self.winfo_height())
        return gradient_color(self.top, self.bottom, y / height)


# ----- rounded gradient image for the primary button -----

def _png_rounded_gradient(width: int, height: int, radius: int, top: str, bottom: str) -> bytes:
    """A PNG with a rounded vertical gradient. Corners outside the radius are transparent."""
    rows = bytearray()
    top_rgb, bottom_rgb = hex_to_rgb(top), hex_to_rgb(bottom)
    for y in range(height):
        t = y / max(1, height - 1)
        colour = [round(top_rgb[i] + (bottom_rgb[i] - top_rgb[i]) * t) for i in range(3)]
        rows.append(0)  # PNG filter type: none
        for x in range(width):
            alpha = 255
            cx = min(max(x, radius), width - 1 - radius)
            cy = min(max(y, radius), height - 1 - radius)
            if (x - cx) ** 2 + (y - cy) ** 2 > radius * radius:
                alpha = 0
            rows.extend((colour[0], colour[1], colour[2], alpha))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b"")


class GradientButton(tk.Canvas):
    """The blue primary button: rounded, with a vertical gradient, hover, and disabled states.

    It behaves like the CustomTkinter button it replaces: configure(state=...), cget("state"), and command.
    """

    RADIUS = theme.BUTTON_RADIUS

    def __init__(self, master, text: str, command: Callable[[], None], width: int = 160, height: int = theme.BUTTON_HEIGHT, state: str = "normal", bg: str = theme.BG_CARD, **_kwargs) -> None:
        super().__init__(master, width=width, height=height, highlightthickness=0, bd=0, bg=bg, cursor="hand2")
        self.text = text
        self.command = command
        self._state = state
        self._hover = False
        self._images: dict[tuple, tk.PhotoImage] = {}
        self._image_item = self.create_image(0, 0, anchor="nw")
        self._label_item = self.create_text(0, 0, text=text, fill="#FFFFFF", font=(theme.FONT_FAMILY, theme.FONT_SIZE_BODY, "bold"))
        self.bind("<Configure>", lambda _event: self._paint())
        self.bind("<Enter>", lambda _event: self._set_hover(True))
        self.bind("<Leave>", lambda _event: self._set_hover(False))
        self.bind("<ButtonRelease-1>", lambda _event: self._press())

    # CustomTkinter-style API used by the screens
    def configure(self, **kwargs) -> None:
        if "state" in kwargs:
            self._state = kwargs.pop("state")
            self._paint()
        if "text" in kwargs:
            self.text = kwargs.pop("text")
            self.itemconfigure(self._label_item, text=self.text)
        if kwargs:
            super().configure(**kwargs)

    def cget(self, key: str):
        if key == "state":
            return self._state
        return super().cget(key)

    def _set_hover(self, hovering: bool) -> None:
        self._hover = hovering
        self._paint()

    def _press(self) -> None:
        if self._state != "disabled" and self.command is not None:
            self.command()

    def _paint(self) -> None:
        width, height = max(2, self.winfo_width()), max(2, self.winfo_height())
        if self._state == "disabled":
            top, bottom, text_colour = theme.DISABLED_BG, theme.DISABLED_BG, theme.DISABLED_TEXT
        elif self._hover:
            top, bottom, text_colour = theme.PRIMARY_HOVER, theme.PRIMARY_HOVER, "#FFFFFF"
        else:
            top, bottom, text_colour = theme.BTN_TOP, theme.BTN_BOTTOM, "#FFFFFF"
        key = (width, height, top, bottom)
        if key not in self._images:
            data = _png_rounded_gradient(width, height, self.RADIUS, top, bottom)
            self._images[key] = tk.PhotoImage(data=data)
            if len(self._images) > 8:
                self._images.pop(next(iter(self._images)))
        self.itemconfigure(self._image_item, image=self._images[key])
        self.coords(self._image_item, 0, 0)
        self.itemconfigure(self._label_item, fill=text_colour)
        self.coords(self._label_item, width / 2, height / 2)
