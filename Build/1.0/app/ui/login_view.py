"""Login screen (Design.md Section 4; PRD FR-1, FR-4)."""

from typing import Callable

import customtkinter as ctk

from app.core import theme
from app.services.auth_service import AuthService, format_lock_message
from app.storage.account_store import CorruptAccountFileError
from app.ui import widgets
from app.ui.gradient import GradientCanvas


class LoginView(GradientCanvas):
    """Centered login card on the gradient page. Enter in either field logs in."""

    def __init__(self, master, auth: AuthService, on_success: Callable[[], None], notice: str = "") -> None:
        super().__init__(master, theme.PAGE_TOP, theme.PAGE_BOTTOM, bg=theme.PAGE_BOTTOM)
        self.auth = auth
        self.on_success = on_success
        self._refresh_job = None

        # The card keeps a fixed size; without this it shrinks to fit its contents.
        card = widgets.card(self, width=420, height=440)
        card.pack_propagate(False)
        card.place(relx=0.5, rely=0.5, anchor="center")

        widgets.label(card, "Expense Ledger", size=theme.FONT_SIZE_PAGE_TITLE).pack(pady=(24, 2))
        widgets.label(card, "Please log in", color=theme.TEXT_MUTED).pack(pady=(0, 16))

        body = widgets.box(card, theme.BG_CARD)
        body.pack(fill="x", padx=24, pady=(0, 24))

        widgets.field_label(body, "Username", required=False).pack(fill="x", pady=(0, 6))
        self.username = widgets.entry(body)
        self.username.pack(fill="x")
        self.username.focus_set()

        widgets.field_label(body, "Password", required=False).pack(fill="x", pady=(14, 6))
        self.password = widgets.entry(body, show="*")
        self.password.pack(fill="x")

        self.notice = ctk.CTkLabel(body, text=notice, font=widgets.text_font(theme.FONT_SIZE_BODY), text_color=theme.CREDIT, anchor="w", wraplength=340)
        self.notice.pack(fill="x", pady=(12, 0))
        self.error = widgets.error_label(body)
        self.error.pack(fill="x", pady=(4, 0))

        self.button = widgets.primary_button(body, "Login", self._submit)
        self.button.pack(fill="x", pady=(14, 0))

        self.username.bind("<Return>", lambda _event: self._submit())
        self.password.bind("<Return>", lambda _event: self._submit())
        self._refresh_lock()

    def _submit(self) -> None:
        if str(self.button.cget("state")) == "disabled":
            return
        try:
            result = self.auth.login(self.username.get(), self.password.get())
        except CorruptAccountFileError:
            self.error.configure(text="The login data could not be read. Contact the account owner.")
            return
        if result.ok:
            self.on_success()
            return
        self.password.delete(0, "end")
        self.notice.configure(text="")
        self.error.configure(text=result.message)
        self._refresh_lock()

    def _refresh_lock(self) -> None:
        """Disable Login and show the countdown while locked (PRD FR-4)."""
        self._refresh_job = None
        try:
            seconds = self.auth.lock_remaining_seconds()
        except CorruptAccountFileError:
            return
        if seconds > 0:
            self.button.configure(state="disabled")
            self.error.configure(text=format_lock_message(seconds))
            self._refresh_job = self.after(1000, self._refresh_lock)
        else:
            self.button.configure(state="normal")
            if self.error.cget("text").startswith("Too many attempts"):
                self.error.configure(text="")

    def destroy(self) -> None:
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)
        super().destroy()
