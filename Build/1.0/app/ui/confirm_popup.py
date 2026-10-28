"""A small yes/no popup for removing something. The action runs only after the user confirms."""

from typing import Callable

import customtkinter as ctk

from app.core import theme
from app.services.auth_service import Result
from app.ui import widgets


class ConfirmPopup(ctk.CTkToplevel):
    """Title, a question, a note, and Cancel / confirm buttons. The action returns a Result; a failure message stays in the popup."""

    def __init__(self, master, title: str, question: str, note: str, confirm_text: str, action: Callable[[], Result], on_done: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.BG_CARD)
        self.action = action
        self.on_done = on_done
        self.title(title)
        widgets.set_window_icon(self)
        self.geometry("420x250")
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self.grab_set()

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)
        widgets.label(body, title, size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w", pady=(0, 12))
        widgets.label(body, question, wraplength=360, justify="left").pack(anchor="w")
        widgets.label(body, note, size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED, wraplength=360, justify="left").pack(anchor="w", pady=(6, 0))
        self.error = widgets.error_label(body)
        self.error.pack(fill="x", pady=(6, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(12, 0))
        widgets.secondary_button(buttons, "Cancel", self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        widgets.danger_button(buttons, confirm_text, self._confirm).pack(side="left", expand=True, fill="x", padx=(6, 0))
        self.bind("<Escape>", lambda _event: self.destroy())

    def _confirm(self) -> None:
        result = self.action()
        if not result.ok:
            self.error.configure(text=result.message)
            return
        self.on_done()
        self.destroy()
