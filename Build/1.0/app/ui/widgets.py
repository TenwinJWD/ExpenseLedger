"""Shared styled widgets, built from the theme (Design.md Sections 1 and 7; Rules 37)."""

import calendar
import tkinter as tk
from datetime import date, timedelta
from typing import Callable

import customtkinter as ctk

from app.core import paths, theme


def text_font(size: int = theme.FONT_SIZE_BODY, bold: bool = True) -> ctk.CTkFont:
    """Font for text. Tkinter offers only normal and bold, so every weight above normal shows as bold."""
    return ctk.CTkFont(family=theme.FONT_FAMILY, size=size, weight="bold" if bold else "normal")


def set_window_icon(window) -> None:
    """Give a window the app icon. Calling iconbitmap also stops CustomTkinter from putting its own blue icon
    on the window a moment after it opens. A missing icon file keeps the default icon."""
    try:
        window.iconbitmap(str(paths.asset_file("app.ico")))
    except tk.TclError:
        pass


def box(parent, color: str = theme.BG_CARD) -> tk.Frame:
    """A plain layout container. CustomTkinter frames default to 200 px tall, which stretches layouts."""
    return tk.Frame(parent, bg=color, highlightthickness=0, bd=0)


def icon_font(size: int = 12) -> ctk.CTkFont:
    """Font for the icon glyphs (Segoe MDL2 Assets)."""
    return ctk.CTkFont(family=theme.ICON_FONT, size=size)


def card(parent, **kwargs) -> ctk.CTkFrame:
    """A raised card with a soft outline (Design.md 1.3)."""
    return ctk.CTkFrame(
        parent,
        fg_color=theme.BG_CARD,
        border_color=theme.BORDER_SOFT,
        border_width=2,
        corner_radius=theme.CARD_RADIUS,
        **kwargs,
    )


def label(parent, text: str, size: int = theme.FONT_SIZE_BODY, color: str = theme.TEXT, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=text_font(size), text_color=color, **kwargs)


def field_label(parent, text: str, required: bool = False, color: str = theme.TEXT, tip: str = ""):
    """Field label. A required field gets an asterisk (Design.md 3).
    With a tip, an info icon sits beside the heading and shows the tip on hover."""
    shown = text + (" *" if required else "")
    holder = ctk.CTkFrame(parent, fg_color="transparent") if tip else parent
    heading = ctk.CTkLabel(holder, text=shown, font=text_font(theme.FONT_SIZE_BODY), text_color=color, anchor="w")
    if not tip:
        return heading
    heading.pack(side="left")
    info = ctk.CTkLabel(holder, text=theme.ICON_INFO, font=icon_font(13), text_color=theme.BTN_TOP, cursor="question_arrow")
    info.pack(side="left", padx=(6, 0))
    Tooltip(info, tip)
    return holder


class Tooltip:
    """A small text box that shows next to a widget while the pointer is over it."""

    KEY_COLOUR = "#010203"

    def __init__(self, widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.window: ctk.CTkToplevel | None = None
        self._watch_job = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<Destroy>", lambda _event: self._close(), add="+")

    def _show(self, _event=None) -> None:
        if self.window is not None:
            return
        # A Toplevel is square, so the corners are made by painting the window in a key colour,
        # making that colour see-through, and drawing a rounded frame on top.
        window = ctk.CTkToplevel(self.widget, fg_color=self.KEY_COLOUR)
        window.overrideredirect(True)
        window.attributes("-topmost", True)
        window.attributes("-transparentcolor", self.KEY_COLOUR)
        bubble = ctk.CTkFrame(window, fg_color=theme.BG_INPUT, border_color=theme.DROPDOWN_BORDER, border_width=1, corner_radius=12)
        bubble.pack()
        ctk.CTkLabel(bubble, text=self.text, justify="left", wraplength=300, font=text_font(theme.FONT_SIZE_LABEL), text_color=theme.TEXT).pack(padx=12, pady=8)
        window.withdraw()  # placed off-screen first, so it never flashes outside the app window
        window.update_idletasks()
        top = self.widget.winfo_toplevel()
        left, upper = top.winfo_rootx(), top.winfo_rooty()
        right, lower = left + top.winfo_width(), upper + top.winfo_height()
        width, height = window.winfo_reqwidth(), window.winfo_reqheight()
        x = max(left + 8, min(self.widget.winfo_rootx() + 22, right - width - 8))
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        if y + height > lower - 8:
            above = self.widget.winfo_rooty() - height - 4
            y = above if above >= upper + 8 else max(upper + 8, lower - height - 8)
        window.geometry(f"+{x}+{y}")
        window.deiconify()
        self.window = window
        self._watch_job = self.widget.after(60, self._watch)

    def _pointer_over_icon(self) -> bool:
        try:
            x, y = self.widget.winfo_pointerxy()
            left, top = self.widget.winfo_rootx(), self.widget.winfo_rooty()
            return left <= x < left + self.widget.winfo_width() and top <= y < top + self.widget.winfo_height()
        except tk.TclError:
            return False

    def _watch(self) -> None:
        """Close the tip as soon as the pointer is off the icon. Leave events alone are unreliable on
        CustomTkinter labels, which are built from two widgets, so the pointer position is checked too."""
        self._watch_job = None
        if self.window is None:
            return
        if self._pointer_over_icon():
            self._watch_job = self.widget.after(60, self._watch)
        else:
            self._close()

    def _hide(self, _event=None) -> None:
        if self.window is not None and not self._pointer_over_icon():
            self._close()

    def _close(self) -> None:
        if self._watch_job is not None:
            try:
                self.widget.after_cancel(self._watch_job)
            except tk.TclError:
                pass
            self._watch_job = None
        if self.window is not None:
            self.window.destroy()
            self.window = None


def entry(parent, show: str = "", placeholder: str = "", **kwargs) -> ctk.CTkEntry:
    kwargs.setdefault("height", theme.INPUT_HEIGHT)  # table cells pass a smaller height
    return ctk.CTkEntry(
        parent,
        corner_radius=theme.INPUT_RADIUS,
        fg_color=theme.BG_INPUT,
        border_color=theme.INPUT_BORDER,
        border_width=2,
        text_color=theme.TEXT,
        placeholder_text_color=theme.TEXT_MUTED,
        font=text_font(theme.FONT_SIZE_BODY),
        show=show,
        placeholder_text=placeholder,
        **kwargs,
    )


def primary_button(parent, text: str, command, **kwargs):
    """Blue action button with the gradient (Design.md 7). Drawn by GradientButton."""
    from app.ui.gradient import GradientButton  # imported here: gradient.py imports this module

    return GradientButton(parent, text=text, command=command, width=kwargs.get("width", 160), state=kwargs.get("state", "normal"))


def secondary_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    """White button with a blue outline and blue text (the mockup's Cancel, Add, Remove, Modify Fields)."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=theme.BUTTON_HEIGHT,
        corner_radius=theme.BUTTON_RADIUS,
        fg_color=theme.BG_CARD,
        hover_color=theme.PRIMARY_LIGHT,
        border_color=theme.PRIMARY,
        border_width=2,
        text_color=theme.PRIMARY,
        text_color_disabled=theme.DISABLED_TEXT,
        font=kwargs.pop("font", None) or text_font(theme.FONT_SIZE_BODY),
        **kwargs,
    )


def danger_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    """Filled button for Remove and Delete in a confirmation popup (Design.md 7)."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=theme.BUTTON_HEIGHT,
        corner_radius=theme.BUTTON_RADIUS,
        fg_color=theme.PRIMARY,
        hover_color=theme.PRIMARY_HOVER,
        text_color="#FFFFFF",
        font=kwargs.pop("font", None) or text_font(theme.FONT_SIZE_BODY),
        **kwargs,
    )


def _fit_inside_window(window, anchor, width: int, height: int, _search: int = 0) -> tuple[int, int, int]:
    """Place a popup under the anchor widget, lined up with its left edge, always inside the app window.
    It goes below the field when it fits there. Otherwise it goes above the field when there is more room
    up there, and as a last resort it is shortened to the room that is left. Returns (x, y, height)."""
    window.update_idletasks()
    left, upper = window.winfo_rootx(), window.winfo_rooty()
    right, lower = left + window.winfo_width(), upper + window.winfo_height()
    x = max(left + 8, min(anchor.winfo_rootx(), right - width - 8))
    below = anchor.winfo_rooty() + anchor.winfo_height() + 4
    room_below = lower - 8 - below
    room_above = anchor.winfo_rooty() - 4 - (upper + 8)
    if height <= room_below:
        return x, below, height
    if room_above > room_below:
        height = max(60, min(height, room_above))
        return x, anchor.winfo_rooty() - 4 - height, height
    height = max(60, room_below)
    return x, below, height


def _set_popup_geometry(popup, x: int, y: int, width: int, height: int) -> None:
    """Set a popup's position and size. CustomTkinter scales the size by the display scaling but
    not the position, so the width and height are divided by that scale and the position is used as read."""
    scale = ctk.ScalingTracker.get_widget_scaling(popup)
    popup.geometry(f"{round(width / scale)}x{round(height / scale)}+{round(x)}+{round(y)}")


class SelectBox(ctk.CTkFrame):
    """A styled dropdown. It opens a list with hover highlights, and a search box for long lists.

    It works like CTkOptionMenu (get, set, configure(values=...)), so screens can swap one for the other.
    The list is a borderless window placed under the box, and it closes on a click elsewhere or on Esc.
    """

    SEARCH_THRESHOLD = 8
    ROW_HEIGHT = 38
    MAX_LIST_HEIGHT = 300

    def __init__(self, master, values=(), variable: ctk.StringVar | None = None, command=None, width: int = 260, state: str = "normal") -> None:
        super().__init__(master, fg_color="transparent", width=width, height=theme.INPUT_HEIGHT)
        self.pack_propagate(False)
        self._values = list(values) or [""]
        self._command = command
        self._variable = variable if variable is not None else ctk.StringVar(value=self._values[0])
        if self._variable.get() not in self._values:
            self._variable.set(self._values[0])
        self._popup: ctk.CTkToplevel | None = None
        self._follow_job = None
        self._button = ctk.CTkButton(
            self,
            text=self._variable.get(),
            anchor="w",
            height=theme.INPUT_HEIGHT,
            corner_radius=theme.INPUT_RADIUS,
            fg_color=theme.BG_INPUT,
            hover_color=theme.SURFACE_TINT,
            border_color=theme.INPUT_BORDER,
            border_width=2,
            text_color=theme.TEXT,
            text_color_disabled=theme.DISABLED_TEXT,
            font=text_font(theme.FONT_SIZE_BODY),
            command=self._toggle,
        )
        self._button.pack(fill="both", expand=True)
        self._arrow = ctk.CTkLabel(self._button, text="", text_color=theme.TEXT_MUTED, font=icon_font(10), fg_color="transparent")
        self._arrow.place(relx=1.0, rely=0.5, x=-12, anchor="e")
        self._variable.trace_add("write", lambda *_args: self._sync())
        self.set_state(state)

    # ----- CTkOptionMenu-style API -----

    def get(self) -> str:
        return self._variable.get()

    def set(self, value: str) -> None:
        self._variable.set(value)

    def configure(self, values=None, state=None, width=None, **_kwargs) -> None:
        if values is not None:
            self._values = list(values) or [""]
            if self._variable.get() not in self._values:
                self._variable.set(self._values[0])
            else:
                self._sync()
        if state is not None:
            self.set_state(state)
        if width is not None:
            super().configure(width=width)

    def set_state(self, state: str) -> None:
        self._button.configure(state=state)
        self._arrow.configure(text_color=theme.DISABLED_TEXT if state == "disabled" else theme.TEXT_MUTED)

    # ----- internals -----

    def _sync(self) -> None:
        self._button.configure(text=self._variable.get())

    def _toggle(self) -> None:
        if self._popup is not None:
            self._close()
        else:
            self._open()

    def _open(self) -> None:
        top = self.winfo_toplevel()
        # A Toplevel is square, so the rounded corners come from a key colour made see-through (as in Tooltip).
        popup = ctk.CTkToplevel(top, fg_color=Tooltip.KEY_COLOUR)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-transparentcolor", Tooltip.KEY_COLOUR)
        panel = ctk.CTkFrame(popup, fg_color=theme.BG_CARD, border_color=theme.DROPDOWN_BORDER, border_width=2, corner_radius=14)
        panel.pack(fill="both", expand=True)
        width = self._button.winfo_width()
        needs_search = len(self._values) > self.SEARCH_THRESHOLD
        search_height = 44 if needs_search else 0
        list_height = min(len(self._values) * self.ROW_HEIGHT + 12, self.MAX_LIST_HEIGHT)
        # The height is worked out in CustomTkinter units, but the placement check uses screen pixels.
        scale = ctk.ScalingTracker.get_widget_scaling(popup)
        total_pixels, search_pixels = round((list_height + search_height) * scale), round(search_height * scale)
        x, y, total_pixels = _fit_inside_window(top, self._button, width, total_pixels, search_pixels)
        list_height = total_pixels / scale - search_height
        _set_popup_geometry(popup, x, y, width, list_height + search_height)
        self._popup = popup
        popup.bind("<Escape>", lambda _event: self._close())
        self._follow_job = self.after(30, self._follow)

        query_box = None
        if needs_search:
            query_box = ctk.CTkEntry(
                panel, height=34, corner_radius=8, fg_color=theme.BG_INPUT, border_color=theme.INPUT_BORDER,
                text_color=theme.TEXT, placeholder_text="Search", placeholder_text_color=theme.TEXT_MUTED,
                font=text_font(theme.FONT_SIZE_BODY),
            )
            query_box.pack(fill="x", padx=10, pady=(10, 4))
            query_box.bind("<KeyRelease>", lambda _event: self._fill(list_frame, query_box.get()))
            query_box.focus_set()

        list_frame = ctk.CTkScrollableFrame(panel, fg_color=theme.BG_CARD, corner_radius=0, height=list_height)
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self._fill(list_frame, "")
        top.bind("<Button-1>", self._close_if_outside, add="+")

    def _fill(self, frame, query: str) -> None:
        for child in frame.winfo_children():
            child.destroy()
        current = self._variable.get()
        matches = [value for value in self._values if query.lower() in value.lower()] or ["No matches"]
        for value in matches:
            if value == "No matches":
                text_label(frame, value, theme.TEXT_MUTED).pack(anchor="w", padx=12, pady=8)
                continue
            selected = value == current
            row = box(frame, theme.BG_CARD)
            row.pack(fill="x", padx=4, pady=1)
            ctk.CTkButton(
                row,
                text=value,
                anchor="w",
                height=self.ROW_HEIGHT - 4,
                corner_radius=8,
                fg_color=theme.PRIMARY_LIGHT if selected else "transparent",
                hover_color=theme.PRIMARY_LIGHT,
                text_color=theme.TEXT,
                font=text_font(theme.FONT_SIZE_BODY),
                command=lambda chosen=value: self._choose(chosen),
            ).pack(side="left", fill="x", expand=True)
            if selected:
                ctk.CTkLabel(row, text="", font=icon_font(12), text_color=theme.BTN_TOP, fg_color="transparent").pack(side="right", padx=10)

    def _choose(self, value: str) -> None:
        self._variable.set(value)
        self._close()
        if self._command is not None:
            self._command(value)

    def _close(self) -> None:
        if self._follow_job is not None:
            self.after_cancel(self._follow_job)
            self._follow_job = None
        if self._popup is not None:
            self._popup.destroy()
            self._popup = None

    def _follow(self) -> None:
        """Keep the open list under its field while the page scrolls or the window moves."""
        self._follow_job = None
        if self._popup is None:
            return
        if not self._button.winfo_ismapped():
            self._close()
            return
        x, y, _height = _fit_inside_window(self.winfo_toplevel(), self._button, self._popup.winfo_width(), self._popup.winfo_height())
        if (self._popup.winfo_rootx(), self._popup.winfo_rooty()) != (x, y):
            self._popup.geometry(f"+{x}+{y}")
        self._follow_job = self.after(30, self._follow)

    def _close_if_outside(self, event) -> None:
        """Close the list when the click lands outside both the list and this box."""
        if self._popup is None:
            return
        clicked = str(event.widget)
        if clicked.startswith(str(self._popup)) or clicked.startswith(str(self)):
            return
        self._close()


class DatePopup(ctk.CTkToplevel):
    """A styled calendar that opens under a button. Pick a day, Today, or Esc to close.

    Shows one month at a time with previous and next arrows. The selected day is blue,
    today has an outline, and days from the neighbouring months are dimmed.
    """

    CELL = 50
    WEEKDAYS = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")

    def __init__(self, anchor, initial: date | None, on_pick: Callable[[date], None]) -> None:
        top = anchor.winfo_toplevel()
        super().__init__(top, fg_color=Tooltip.KEY_COLOUR)  # see-through corners, as in Tooltip
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", Tooltip.KEY_COLOUR)
        self.on_pick = on_pick
        self.anchor_widget = anchor
        self.selected = initial or date.today()
        self.shown = date(self.selected.year, self.selected.month, 1)
        self.top = top
        panel = ctk.CTkFrame(self, fg_color=theme.BG_CARD, border_color=theme.INPUT_BORDER, border_width=2, corner_radius=14)
        panel.pack(fill="both", expand=True)
        frame = ctk.CTkFrame(panel, fg_color=theme.BG_CARD, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=14, pady=14)
        header = box(frame, theme.BG_CARD)
        header.pack(fill="x")
        ctk.CTkButton(header, text="‹", width=32, height=32, corner_radius=8, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, text_color=theme.TEXT, font=text_font(16), command=lambda: self._shift(-1)).pack(side="left")
        self.title_label = ctk.CTkLabel(header, text="", font=text_font(theme.FONT_SIZE_CARD_TITLE), text_color=theme.TEXT)
        self.title_label.pack(side="left", expand=True)
        ctk.CTkButton(header, text="›", width=32, height=32, corner_radius=8, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, text_color=theme.TEXT, font=text_font(16), command=lambda: self._shift(1)).pack(side="right")

        self.grid_frame = box(frame, theme.BG_CARD)
        self.grid_frame.pack(pady=(10, 6))

        footer = box(frame, theme.BG_CARD)
        footer.pack(fill="x")
        ctk.CTkButton(footer, text="Today", height=30, corner_radius=8, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, border_color=theme.INPUT_BORDER, border_width=1, text_color=theme.TEXT, font=text_font(theme.FONT_SIZE_LABEL), command=self._pick_today).pack(side="left")

        self._follow_job = None
        self._render()
        self._place()
        self._follow_job = self.after(30, self._follow)
        self.bind("<Escape>", lambda _event: self.close())
        self.top.bind("<Button-1>", self._close_if_outside, add="+")
        self.focus_set()

    def _target(self) -> tuple[int, int]:
        """Where the calendar goes: under its button, or above it when there is no room below,
        and always inside the app window."""
        self.update_idletasks()
        top, anchor = self.top, self.anchor_widget
        left, upper = top.winfo_rootx(), top.winfo_rooty()
        right, lower = left + top.winfo_width(), upper + top.winfo_height()
        width, height = self.winfo_reqwidth(), self.winfo_reqheight()
        x = max(left + 8, min(anchor.winfo_rootx(), right - width - 8))
        y = anchor.winfo_rooty() + anchor.winfo_height() + 6
        if y + height > lower - 8:
            above = anchor.winfo_rooty() - height - 6
            y = above if above >= upper + 8 else max(upper + 8, lower - height - 8)
        return x, y

    def _place(self) -> None:
        x, y = self._target()
        self.geometry(f"+{x}+{y}")

    def _shift(self, months: int) -> None:
        month_index = self.shown.month - 1 + months
        self.shown = date(self.shown.year + month_index // 12, month_index % 12 + 1, 1)
        self._render()

    def _render(self) -> None:
        self.title_label.configure(text=f"{calendar.month_name[self.shown.month]} {self.shown.year}")
        for child in self.grid_frame.winfo_children():
            child.destroy()
        for column, name in enumerate(self.WEEKDAYS):
            text_label(self.grid_frame, name, theme.TEXT_MUTED).grid(row=0, column=column, padx=2, pady=(0, 4))
        today = date.today()
        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(self.shown.year, self.shown.month)
        while len(weeks) < 6:  # always six rows, so the calendar keeps the same size in every month
            last = weeks[-1][-1]
            weeks.append([last + timedelta(days=offset) for offset in range(1, 8)])
        for row, week in enumerate(weeks, start=1):
            for column, day in enumerate(week):
                in_month = day.month == self.shown.month
                chosen = day == self.selected
                ctk.CTkButton(
                    self.grid_frame,
                    text=str(day.day),
                    width=self.CELL,
                    height=self.CELL - 4,
                    corner_radius=8,
                    fg_color=theme.PRIMARY if chosen else "transparent",
                    hover_color=theme.PRIMARY_HOVER if chosen else theme.PRIMARY_LIGHT,
                    border_color=theme.BTN_TOP if day == today and not chosen else theme.BG_CARD,
                    border_width=1 if day == today and not chosen else 0,
                    text_color="#FFFFFF" if chosen else (theme.TEXT if in_month else theme.DISABLED_TEXT),
                    font=text_font(theme.FONT_SIZE_CARD_TITLE - 2, chosen),
                    command=lambda picked=day: self._choose(picked),
                ).grid(row=row, column=column, padx=2, pady=2)

    def _choose(self, day: date) -> None:
        self.on_pick(day)
        self.close()

    def _pick_today(self) -> None:
        self._choose(date.today())

    def _close_if_outside(self, event) -> None:
        clicked = str(event.widget)
        if clicked.startswith(str(self)) or clicked.startswith(str(self.anchor_widget)):
            return
        self.close()

    def _follow(self) -> None:
        """Keep the calendar under its button while the page scrolls or the window moves."""
        self._follow_job = None
        if not self.anchor_widget.winfo_ismapped():
            self.close()
            return
        x, y = self._target()
        if (self.winfo_rootx(), self.winfo_rooty()) != (x, y):
            self.geometry(f"+{x}+{y}")
        self._follow_job = self.after(30, self._follow)

    def close(self) -> None:
        if self._follow_job is not None:
            self.after_cancel(self._follow_job)
            self._follow_job = None
        if self.winfo_exists():
            self.destroy()


def text_label(parent, text: str, color: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=text_font(theme.FONT_SIZE_BODY), text_color=color)


def error_label(parent, fixed: bool = False) -> ctk.CTkLabel:
    """Red message under a field. Empty text hides it visually. A fixed one keeps its height, so the form never shifts."""
    extra = {"height": 22} if fixed else {}
    return ctk.CTkLabel(parent, text="", font=text_font(theme.FONT_SIZE_LABEL), text_color=theme.ERROR, anchor="w", **extra)
