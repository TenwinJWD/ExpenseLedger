"""Gradient drawing for the Windows app (Design.md 1.3; matches the mockup's CSS gradients).

Tkinter cannot paint CSS gradients, so they are drawn here:
- GradientCanvas paints a vertical gradient behind its contents and repaints on resize.
- GradientBar paints a horizontal gradient with several colour stops, and lays widgets on it.
- gradient_color() gives the colour at any height, so widgets on top can match it.
"""

import tkinter as tk

import customtkinter as ctk


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


def stops_color(stops: tuple[str, ...], fraction: float) -> str:
    """The colour at a fraction (0 to 1) along a gradient with several colour stops, evenly spaced."""
    fraction = max(0.0, min(1.0, fraction))
    if len(stops) == 1:
        return stops[0]
    position = fraction * (len(stops) - 1)
    index = min(int(position), len(stops) - 2)
    return gradient_color(stops[index], stops[index + 1], position - index)


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


class GradientBar(tk.Canvas):
    """A horizontal gradient strip (the top navbar). Widgets are added to its left or right end.

    Widgets cannot be see-through over a gradient, so each one gets the gradient's colour at its own
    position as its corner colour. The colours are set again whenever the bar is resized.
    """

    STEP = 3

    def __init__(self, master, stops: tuple[str, ...], height: int) -> None:
        super().__init__(master, highlightthickness=0, bd=0, bg=stops[0])
        self.stops = stops
        scale = ctk.ScalingTracker.get_widget_scaling(self)
        self.configure(height=round(height * scale))
        self._items: list[tuple[tk.Widget, str, int, int, int]] = []  # widget, side, window id, gap before, gap after
        self._painted_width = 0
        self.bind("<Configure>", lambda _event: self.paint())

    def add(self, widget, side: str = "left", before: int = 0, after: int = 0) -> None:
        """Place a widget at the next free spot on the left or the right. Gaps are in screen units."""
        window = self.create_window(0, 0, window=widget, anchor="w" if side == "left" else "e")
        self._items.append((widget, side, window, before, after))
        self.after_idle(self.layout)

    def colour_at(self, x: float) -> str:
        return stops_color(self.stops, x / max(1, self.winfo_width()))

    def paint(self) -> None:
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        if width != self._painted_width:
            self._painted_width = width
            self.delete("gradient")
            for x in range(0, width, self.STEP):
                self.create_rectangle(x, 0, x + self.STEP, height, fill=self.colour_at(x), outline="", tags="gradient")
            self.tag_lower("gradient")
        self.layout()

    def layout(self) -> None:
        if not self.winfo_exists():
            return
        scale = ctk.ScalingTracker.get_widget_scaling(self)
        width, height = self.winfo_width(), self.winfo_height()
        left, right = 0.0, float(width)
        for widget, side, window, before, after in self._items:
            size = widget.winfo_reqwidth()
            if side == "left":
                x = left + before * scale
                left = x + size + after * scale
                centre = x + size / 2
            else:
                x = right - before * scale
                right = x - size - after * scale
                centre = x - size / 2
            self.coords(window, x, height / 2)
            try:
                widget.configure(bg_color=self.colour_at(centre))
            except (tk.TclError, ValueError):
                pass  # a plain tkinter widget: it keeps the colour it was made with
