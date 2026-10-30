"""A line chart for the Dashboard: a smooth debit line and credit line over each month or day.

Drawn on a Tk canvas, so it needs no extra package. Hovering over a point shows its numbers.
"""

import tkinter as tk
from decimal import Decimal

from app.core import money, theme
from app.services.report_service import Bar
from app.ui.gradient import gradient_color

TICK_COUNT = 4
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 8, 12, 34, 26
MIN_LABEL_SPACING = 26  # pixels a label needs; points closer than this show every second label
CURVE_STEPS = 8  # straight pieces drawn between two points to make the curve
FILL_TINT = 0.86  # how far the area under a line is faded towards the card colour


def nice_axis(highest: Decimal) -> tuple[int, int]:
    """(step, top) for the value axis: a round step and a top that is TICK_COUNT steps, covering the highest value."""
    value = max(float(highest), 1.0)
    rough = value / TICK_COUNT
    magnitude = 10 ** (len(str(int(rough))) - 1)
    for tenths in (10, 20, 25, 50, 100):  # steps of 1, 2, 2.5, 5, and 10 times the magnitude, kept whole
        if magnitude * tenths % 10:
            continue
        step = magnitude * tenths // 10
        if step * TICK_COUNT >= value:
            return step, step * TICK_COUNT
    return 10 * magnitude, 10 * magnitude * TICK_COUNT


def smooth_curve(xs: list[float], ys: list[float]) -> list[float]:
    """Flat [x, y, x, y, ...] points of a smooth curve through the given points.

    A monotone cubic curve: it never goes above or below the points it joins, so a line between two zero
    days stays on the baseline instead of dipping under it.
    """
    count = len(xs)
    if count < 3:
        return [value for pair in zip(xs, ys) for value in pair]
    slopes = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(count - 1)]
    tangents = [slopes[0]] + [0.0 if slopes[i - 1] * slopes[i] <= 0 else (slopes[i - 1] + slopes[i]) / 2 for i in range(1, count - 1)] + [slopes[-1]]
    for i, slope in enumerate(slopes):
        if slope == 0:
            tangents[i] = tangents[i + 1] = 0.0
            continue
        a, b = tangents[i] / slope, tangents[i + 1] / slope
        if a * a + b * b > 9:
            scale = 3 / (a * a + b * b) ** 0.5
            tangents[i], tangents[i + 1] = scale * a * slope, scale * b * slope
    points: list[float] = []
    for i in range(count - 1):
        width = xs[i + 1] - xs[i]
        for step in range(CURVE_STEPS):
            t = step / CURVE_STEPS
            h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
            points += [xs[i] + t * width, h00 * ys[i] + h10 * width * tangents[i] + h01 * ys[i + 1] + h11 * width * tangents[i + 1]]
    points += [xs[-1], ys[-1]]
    return points


class LineChart(tk.Canvas):
    """Debit (red) and credit (green) lines for each Bar. Call show() to set the data."""

    def __init__(self, master, height: int = 240, **kwargs) -> None:
        super().__init__(master, height=height, bg=theme.BG_CARD, highlightthickness=0, bd=0, **kwargs)
        self.bars: list[Bar] = []
        self.title = ""
        self._plot = (0, 0, 0, 0)
        self._xs: list[float] = []
        self._ys: dict[str, list[float]] = {}
        self.bind("<Configure>", lambda _event: self._draw())
        self.bind("<Motion>", self._hover)
        self.bind("<Leave>", lambda _event: self.delete("hover"))

    def show(self, bars: list[Bar], title: str = "") -> None:
        self.bars = bars
        self.title = title
        self._draw()

    # ----- drawing -----

    def _draw(self) -> None:
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < 120 or height < 100:
            return
        self._legend(width)
        highest = max((max(bar.debit, bar.credit) for bar in self.bars), default=Decimal("0"))
        if highest <= 0:
            self.create_text(width / 2, height / 2, text="No entries in this period.", fill=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 12))
            self._plot = (0, 0, 0, 0)
            return
        step, top = nice_axis(highest)
        font = (theme.FONT_FAMILY, 10)
        label_width = max(len(f"{top:,}") * 7, 28)
        left, right = PAD_LEFT + label_width + 6, width - PAD_RIGHT
        upper, lower = PAD_TOP, height - PAD_BOTTOM
        self._plot = (left, upper, right, lower)

        for index in range(TICK_COUNT + 1):
            value = step * index
            y = lower - (lower - upper) * value / top
            self.create_line(left, y, right, y, fill=theme.ROW_BORDER, dash=(2, 4) if index else ())
            self.create_text(left - 6, y, text=f"{value:,}", anchor="e", fill=theme.TEXT_MUTED, font=font)

        count = len(self.bars)
        group = (right - left) / max(1, count)
        every = 1 if group >= MIN_LABEL_SPACING else 2
        self._xs = [left + group * (index + 0.5) for index in range(count)]
        self._ys = {
            kind: [lower - (lower - upper) * float(getattr(bar, kind)) / top for bar in self.bars]
            for kind in ("debit", "credit")
        }
        for index, bar in enumerate(self.bars):
            if index % every == 0:
                self.create_text(self._xs[index], lower + 12, text=bar.label, fill=theme.TEXT_MUTED, font=font)

        for kind, colour in (("debit", theme.DEBIT), ("credit", theme.CREDIT)):
            self._draw_series(kind, colour, lower)

    def _draw_series(self, kind: str, colour: str, lower: float) -> None:
        xs, ys = self._xs, self._ys[kind]
        if not any(getattr(bar, kind) > 0 for bar in self.bars):
            return
        curve = smooth_curve(xs, ys)
        if len(curve) >= 4:
            # The soft area under the line: the curve closed down to the baseline, in a faded tint of the line colour.
            self.create_polygon(*curve, xs[-1], lower, xs[0], lower, fill=gradient_color(colour, theme.BG_CARD, FILL_TINT), outline="")
            self.create_line(*curve, fill=colour, width=3, capstyle="round", joinstyle="round")
        for index, bar in enumerate(self.bars):
            if getattr(bar, kind) > 0:
                self.create_oval(xs[index] - 4, ys[index] - 4, xs[index] + 4, ys[index] + 4, fill=theme.BG_CARD, outline=colour, width=2)

    def _legend(self, width: int) -> None:
        font = (theme.FONT_FAMILY, 11, "bold")
        x = width - PAD_RIGHT
        for text, colour in (("Credit", theme.CREDIT), ("Debit", theme.DEBIT)):
            label = self.create_text(x, 14, text=text, anchor="e", fill=theme.TEXT, font=font)
            left = self.bbox(label)[0]
            self.create_oval(left - 16, 9, left - 6, 19, fill=colour, outline="")
            x = left - 28
        if self.title:
            self.create_text(PAD_LEFT, 14, text=self.title, anchor="w", fill=theme.TEXT, font=font)

    # ----- hover -----

    def _hover(self, event) -> None:
        self.delete("hover")
        left, upper, right, lower = self._plot
        if right <= left or not (left <= event.x <= right) or not self.bars:
            return
        index = min(len(self.bars) - 1, int((event.x - left) / ((right - left) / len(self.bars))))
        bar = self.bars[index]
        text = f"{bar.label}   Debit {money.format_amount(bar.debit)}   Credit {money.format_amount(bar.credit)}"
        centre_x = self._xs[index]
        guide = self.create_line(centre_x, upper, centre_x, lower, fill=theme.INPUT_BORDER, dash=(4, 4), tags="hover")
        self.tag_lower(guide)
        for kind, colour in (("debit", theme.DEBIT), ("credit", theme.CREDIT)):
            y = self._ys[kind][index]
            self.create_oval(centre_x - 6, y - 6, centre_x + 6, y + 6, fill=colour, outline=theme.BG_CARD, width=2, tags="hover")
        note = self.create_text(left + 4, upper + 4, text=text, anchor="nw", fill=theme.TEXT, font=(theme.FONT_FAMILY, 11, "bold"), tags="hover")
        box = self.bbox(note)
        backing = self.create_rectangle(box[0] - 6, box[1] - 3, box[2] + 6, box[3] + 3, fill=theme.BG_CARD, outline=theme.INPUT_BORDER, tags="hover")
        self.tag_raise(note, backing)
