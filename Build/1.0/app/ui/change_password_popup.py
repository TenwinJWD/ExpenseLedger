"""Change Password popup (Design.md 2.1; PRD FR-37 to FR-41)."""

from typing import Callable

import customtkinter as ctk

from app.core import config, theme
from app.services.auth_service import AuthService
from app.ui import widgets


class ChangePasswordPopup(ctk.CTkToplevel):
    """Modal popup. Save stays disabled until all three fields have a value (FR-38)."""

    def __init__(self, master, auth: AuthService, on_saved: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.BG_CARD)
        self.auth = auth
        self.on_saved = on_saved
        self.title("Change Password")
        self.geometry("420x440")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.current_var = ctk.StringVar()
        self.new_var = ctk.StringVar()
        self.repeat_var = ctk.StringVar()
        for variable in (self.current_var, self.new_var, self.repeat_var):
            variable.trace_add("write", lambda *_args: self._update_save_state())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)

        widgets.label(body, "Change Password", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w", pady=(0, 12))

        widgets.field_label(body, "Current password", required=True).pack(fill="x", pady=(0, 6))
        self.current = widgets.entry(body, show="*", textvariable=self.current_var)
        self.current.pack(fill="x")
        self.current_error = widgets.error_label(body)
        self.current_error.pack(fill="x")

        widgets.field_label(body, "New password", required=True).pack(fill="x", pady=(10, 6))
        self.new = widgets.entry(body, show="*", textvariable=self.new_var)
        self.new.pack(fill="x")
        widgets.label(body, f"At least {config.MIN_PASSWORD_LENGTH} characters, different from the current password.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED, wraplength=360, justify="left").pack(fill="x", pady=(4, 0))
        self.new_error = widgets.error_label(body)
        self.new_error.pack(fill="x")

        widgets.field_label(body, "Confirm new password", required=True).pack(fill="x", pady=(10, 6))
        self.repeat = widgets.entry(body, show="*", textvariable=self.repeat_var)
        self.repeat.pack(fill="x")
        self.repeat_error = widgets.error_label(body)
        self.repeat_error.pack(fill="x")

        self.form_error = widgets.error_label(body)
        self.form_error.pack(fill="x", pady=(4, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(12, 0))
        widgets.secondary_button(buttons, "Cancel", self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.save_button = widgets.primary_button(buttons, "Save", self._save, state="disabled")
        self.save_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.repeat.bind("<Return>", lambda _event: self._save())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.current.focus_set()

    def _update_save_state(self) -> None:
        filled = all(variable.get() for variable in (self.current_var, self.new_var, self.repeat_var))
        self.save_button.configure(state="normal" if filled else "disabled")

    def _save(self) -> None:
        if str(self.save_button.cget("state")) == "disabled":
            return
        for error in (self.current_error, self.new_error, self.repeat_error, self.form_error):
            error.configure(text="")
        result = self.auth.change_password(self.current.get(), self.new.get(), self.repeat.get())
        if result.ok:
            self.on_saved()
            self.destroy()
            return
        self._show_error(result.message)

    def _show_error(self, message: str) -> None:
        """Put each message under the field it belongs to (Rule 25)."""
        if message.startswith("Wrong current") or message.startswith("Too many"):
            if message.startswith("Too many"):
                self.form_error.configure(text=message)
            else:
                self.current_error.configure(text=message)
        elif message.startswith("Passwords do not match"):
            self.repeat_error.configure(text=message)
        elif message.startswith("Use at least") or message.startswith("The new password"):
            self.new_error.configure(text=message)
        else:
            self.form_error.configure(text=message)
