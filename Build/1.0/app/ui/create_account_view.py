"""First-run screen to create the one account (Design.md Section 3; PRD FR-2)."""

from typing import Callable

import customtkinter as ctk

from app.core import config, theme
from app.services.auth_service import AuthService
from app.ui import widgets
from app.ui.gradient import GradientCanvas


class CreateAccountView(GradientCanvas):
    """Centered create-account card on the gradient page. Enter in the last field submits."""

    def __init__(self, master, auth: AuthService, on_done: Callable[[], None]) -> None:
        super().__init__(master, theme.PAGE_TOP, theme.PAGE_BOTTOM, bg=theme.PAGE_BOTTOM)
        self.auth = auth
        self.on_done = on_done

        # The card keeps a fixed size; without this it shrinks to fit its contents.
        card = widgets.card(self, width=420, height=560)
        card.pack_propagate(False)
        card.place(relx=0.5, rely=0.5, anchor="center")

        widgets.label(card, "Daily Fresh", size=theme.FONT_SIZE_PAGE_TITLE).pack(pady=(24, 2))
        widgets.label(card, "Create your account to get started", color=theme.TEXT_MUTED).pack(pady=(0, 16))

        body = widgets.box(card, theme.BG_CARD)
        body.pack(fill="x", padx=24, pady=(0, 24))

        widgets.field_label(body, "Username", required=True).pack(fill="x", pady=(0, 6))
        self.username = widgets.entry(body)
        self.username.pack(fill="x")
        self.username.focus_set()
        self.username_error = widgets.error_label(body)
        self.username_error.pack(fill="x")

        widgets.field_label(body, "Password", required=True).pack(fill="x", pady=(10, 6))
        self.password = widgets.entry(body, show="*")
        self.password.pack(fill="x")
        widgets.label(body, f"Use at least {config.MIN_PASSWORD_LENGTH} characters.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED).pack(fill="x", pady=(4, 0))

        widgets.field_label(body, "Confirm password", required=True).pack(fill="x", pady=(10, 6))
        self.repeat = widgets.entry(body, show="*")
        self.repeat.pack(fill="x")
        self.form_error = widgets.error_label(body)
        self.form_error.pack(fill="x", pady=(6, 0))

        self.button = widgets.primary_button(body, "Create Account", self._submit)
        self.button.pack(fill="x", pady=(12, 0))

        self.repeat.bind("<Return>", lambda _event: self._submit())

    def _submit(self) -> None:
        result = self.auth.create_account(self.username.get(), self.password.get(), self.repeat.get())
        self.username_error.configure(text="")
        self.form_error.configure(text="")
        if result.ok:
            self.on_done()
            return
        if result.message == "Username is required.":
            self.username_error.configure(text=result.message)
        else:
            self.form_error.configure(text=result.message)
