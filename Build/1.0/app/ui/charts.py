"""A grouped bar chart for the Dashboard: debit and credit side by side for each month or day.

Drawn on a Tk canvas, so it needs no extra package. Hovering over a group shows its numbers.
"""

import tkinter as tk
from decimal import Decimal

from app.core import money, theme
from app.services.report_service import Bar

TICK_COUNT = 4
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 8, 12, 34, 26
MIN_LABEL_SPACING = 26  # pixels a label needs; groups closer than this show every second label


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


class BarChart(tk.Canvas):
    """Debit (red) and credit (green) bars for each Bar. Call show() to set the data."""

    def __init__(self, master, height: int = 240, **kwargs) -> None:
        super().__init__(master, height=height, bg=theme.BG_CARD, highlightthickness=0, bd=0, **kwargs)
        self.bars: list[Bar] = []
        self.title = ""
        self._plot = (0, 0, 0, 0)
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
            self.create_line(left, y, right, y, fill=theme.ROW_BORDER if index else theme.INPUT_BORDER)
            self.create_text(left - 6, y, text=f"{value:,}", anchor="e", fill=theme.TEXT_MUTED, font=font)

        group = (right - left) / max(1, len(self.bars))
        bar_width = max(2.0, min(group * 0.34, 22.0))
        every = 1 if group >= MIN_LABEL_SPACING else 2
        for index, bar in enumerate(self.bars):
            centre = left + group * (index + 0.5)
            for offset, value, colour in ((-bar_width / 2, bar.debit, theme.DEBIT), (bar_width / 2, bar.credit, theme.CREDIT)):
                if value > 0:
                    y = lower - (lower - upper) * float(value) / top
                    self.create_rectangle(centre + offset - bar_width / 2, y, centre + offset + bar_width / 2, lower, fill=colour, outline="")
            if index % every == 0:
                self.create_text(centre, lower + 12, text=bar.label, fill=theme.TEXT_MUTED, font=font)

    def _legend(self, width: int) -> None:
        font = (theme.FONT_FAMILY, 11, "bold")
        x = width - PAD_RIGHT
        for text, colour in (("Credit", theme.CREDIT), ("Debit", theme.DEBIT)):
            label = self.create_text(x, 14, text=text, anchor="e", fill=theme.TEXT, font=font)
            left = self.bbox(label)[0]
            self.create_rectangle(left - 16, 9, left - 6, 19, fill=colour, outline="")
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
        centre_x = left + (right - left) / len(self.bars) * (index + 0.5)
        half = (right - left) / len(self.bars) / 2
        column = self.create_rectangle(centre_x - half, upper, centre_x + half, lower, fill=theme.PRIMARY_LIGHT, outline="", tags="hover")
        self.tag_lower(column)
        note = self.create_text(left + 4, upper + 4, text=text, anchor="nw", fill=theme.TEXT, font=(theme.FONT_FAMILY, 11, "bold"), tags="hover")
        box = self.bbox(note)
        backing = self.create_rectangle(box[0] - 6, box[1] - 3, box[2] + 6, box[3] + 3, fill=theme.BG_CARD, outline=theme.INPUT_BORDER, tags="hover")
        self.tag_raise(note, backing)
