"""Add (+) and remove (−) sub-head popups (Design.md 5.4 and 5.5; PRD FR-8, FR-9).

The popups show the Main Head's list name in plain words. They never show a file location (NFR-9).
"""

from typing import Callable

import customtkinter as ctk

from app.core import config, models, theme
from app.services.subhead_service import SubheadService
from app.ui import widgets


class AddSubheadPopup(ctk.CTkToplevel):
    """Modal popup for a new sub-head. ADD stays disabled until a name is typed."""

    def __init__(self, master, service: SubheadService, main_head: str, on_added: Callable[[str, str], None]) -> None:
        super().__init__(master, fg_color=theme.BG_CARD)
        self.service = service
        self.main_head = main_head
        self.on_added = on_added
        self.title("Add Sub-Head")
        self.geometry("420x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.name_var = ctk.StringVar()
        self.name_var.trace_add("write", lambda *_args: self._update_add_state())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)

        widgets.label(body, "Add Sub-Head", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w", pady=(0, 12))
        widgets.field_label(body, "Sub-Head name", required=True).pack(fill="x", pady=(0, 6))
        self.entry = widgets.entry(body, placeholder=f"Up to {config.SUBHEAD_MAX_LENGTH} characters", textvariable=self.name_var)
        self.entry.pack(fill="x")
        self.error = widgets.error_label(body)
        self.error.pack(fill="x", pady=(4, 0))
        widgets.label(body, f"Adds to the {models.MAIN_HEADS[main_head]} list.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED).pack(anchor="w", pady=(8, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(16, 0))
        widgets.secondary_button(buttons, "Cancel", self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.add_button = widgets.primary_button(buttons, "Add", self._add, state="disabled")
        self.add_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.entry.bind("<Return>", lambda _event: self._add())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.entry.focus_set()

    def _update_add_state(self) -> None:
        self.add_button.configure(state="normal" if self.name_var.get().strip() else "disabled")

    def _add(self) -> None:
        if str(self.add_button.cget("state")) == "disabled":
            return
        name = self.name_var.get().strip()
        result = self.service.add_subhead(self.main_head, name)
        if not result.ok:
            self.error.configure(text=result.message)
            return
        self.on_added(name, result.message)
        self.destroy()


class RemoveSubheadPopup(ctk.CTkToplevel):
    """Confirmation before a sub-head is removed from the dropdown (FR-9)."""

    def __init__(self, master, service: SubheadService, main_head: str, name: str, on_removed: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.BG_CARD)
        self.service = service
        self.main_head = main_head
        self.name = name
        self.on_removed = on_removed
        self.title("Remove Sub-Head")
        self.geometry("420x250")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)

        widgets.label(body, "Remove Sub-Head", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w", pady=(0, 12))
        widgets.label(body, f'Remove "{name}" from the list?', wraplength=360, justify="left").pack(anchor="w")
        widgets.label(body, "Old entries keep this sub-head name.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED).pack(anchor="w", pady=(6, 0))
        self.error = widgets.error_label(body)
        self.error.pack(fill="x", pady=(6, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(16, 0))
        widgets.secondary_button(buttons, "Cancel", self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        widgets.danger_button(buttons, "Remove", self._remove).pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.bind("<Escape>", lambda _event: self.destroy())

    def _remove(self) -> None:
        result = self.service.remove_subhead(self.main_head, self.name)
        if not result.ok:
            self.error.configure(text=result.message)
            return
        self.on_removed()
        self.destroy()
