"""Modify Fields page: edit the Main Entries and the Transactions fields of one Main Entry.

Two cards, each with an Add row above a table. Edit changes a name in place; Remove asks first.
Old rows keep working: a renamed name is remembered, and a removed one is only hidden (Rules 14).
"""

from typing import Callable

import customtkinter as ctk

from app.core import config, models, theme
from app.services.main_entry_service import MainEntryService
from app.services.subhead_service import SubheadService
from app.ui import widgets
from app.ui.confirm_popup import ConfirmPopup


class ModifyFieldsView(ctk.CTkFrame):
    """Card 1 lists the Main Entries. Card 2 lists the Transactions fields of the Main Entry chosen at its top."""

    def __init__(self, master, main_entries: MainEntryService, subheads: SubheadService, on_back: Callable[[], None], on_entries_changed: Callable[[], None], notify: Callable[[str], None]) -> None:
        super().__init__(master, fg_color="transparent")
        self.main_entries = main_entries
        self.subheads = subheads
        self.on_back = on_back
        self.on_entries_changed = on_entries_changed
        self.notify = notify
        self.main_head = models.DEFAULT_MAIN_HEAD
        self.editing_entry: str | None = None
        self.editing_field: str | None = None

        self.grid_columnconfigure(0, weight=1)
        widgets.secondary_button(self, "‹ Back to Main Entry", lambda: self.on_back(), width=190).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 0))
        self.entries_card = self._card(1, "Main Entries", "These are the entries listed under Main Entry in the sidebar.", "New Main Entry name", config.MAIN_ENTRY_MAX_LENGTH, self._add_entry)
        self.fields_card = self._card(2, "Transactions Fields", "These are the choices in the Transactions list of the entry form.", "New Transactions field name", config.SUBHEAD_MAX_LENGTH, self._add_field)

        # Card 2 says which Main Entry's fields it shows, and lets the user switch.
        self.scope_menu = widgets.SelectBox(self.fields_card["head"], values=[""], command=self._on_scope, width=220)
        self.scope_menu.pack(side="right")

    # ----- layout -----

    def _card(self, row: int, title: str, description: str, placeholder: str, max_length: int, on_add: Callable[[], None]) -> dict:
        card = widgets.card(self)
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(16, 0))
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(18, 4))
        titles = ctk.CTkFrame(head, fg_color="transparent")
        titles.pack(side="left", fill="x", expand=True)
        widgets.label(titles, title, size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w")
        widgets.label(titles, description, color=theme.TEXT_MUTED).pack(anchor="w")

        add_row = ctk.CTkFrame(card, fg_color="transparent")
        add_row.pack(fill="x", padx=20, pady=(12, 0))
        entry = widgets.entry(add_row, placeholder=placeholder)
        entry.pack(side="left", fill="x", expand=True)
        add_button = widgets.primary_button(add_row, "Add", on_add, width=100)
        add_button.pack(side="left", padx=(10, 0))
        entry.bind("<Return>", lambda _event: on_add())
        error = widgets.error_label(card)
        error.pack(fill="x", padx=20, pady=(4, 0))

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=20, pady=(4, 20))
        table.grid_columnconfigure(0, weight=1)
        return {"card": card, "head": head, "entry": entry, "error": error, "table": table}

    # ----- data -----

    def show(self, main_head: str) -> None:
        """Open the page for the Main Entry the user came from."""
        self.main_head = main_head
        self.editing_entry = None
        self.editing_field = None
        self.refresh()

    def refresh(self) -> None:
        items = self.main_entries.items()
        active = [item for item in items if item.active]
        if self.main_head not in [item.id for item in active] and active:
            self.main_head = active[0].id
        self.scope_menu.configure(values=[item.name for item in active])
        self.scope_menu.set(self.main_entries.label(self.main_head))
        self._render_entries(active)
        self._render_fields()

    def _on_scope(self, choice: str) -> None:
        self.main_head = next((item.id for item in self.main_entries.active() if item.name == choice), self.main_head)
        self.editing_field = None
        self.fields_card["error"].configure(text="")
        self._render_fields()

    # ----- tables -----

    def _render_table(self, card: dict, names: list[str], editing: str | None, on_edit, on_save, on_cancel, on_remove) -> None:
        table = card["table"]
        for child in table.winfo_children():
            child.destroy()
        header = ctk.CTkFrame(table, fg_color=theme.SURFACE_TINT, corner_radius=8)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        widgets.label(header, "Name", size=theme.FONT_SIZE_BODY).grid(row=0, column=0, sticky="w", padx=14, pady=8)
        widgets.label(header, "Actions", size=theme.FONT_SIZE_BODY).grid(row=0, column=1, sticky="e", padx=(0, 60), pady=8)
        if not names:
            widgets.label(table, "Nothing here yet. Add one above.", color=theme.TEXT_MUTED).grid(row=1, column=0, pady=18)
        for index, name in enumerate(names, start=1):
            line = ctk.CTkFrame(table, fg_color="transparent")
            line.grid(row=index, column=0, sticky="ew")
            line.grid_columnconfigure(0, weight=1)
            ctk.CTkFrame(line, height=1, fg_color=theme.ROW_BORDER).grid(row=2, column=0, columnspan=2, sticky="ew")
            actions = ctk.CTkFrame(line, fg_color="transparent", height=1)
            actions.grid(row=0, column=1, sticky="e", padx=(8, 8))
            if name == editing:
                # The entry and the Save / Cancel links share row 0, so they line up; the message goes under the entry.
                field = widgets.entry(line, height=34)
                field.insert(0, name)
                field.grid(row=0, column=0, sticky="ew", padx=(8, 8), pady=6)
                field.focus_set()
                problem = widgets.error_label(line)
                problem.grid(row=1, column=0, sticky="w", padx=(12, 0))
                field.bind("<Return>", lambda _event, f=field, p=problem, old=name: on_save(old, f.get(), p))
                field.bind("<Escape>", lambda _event: on_cancel())
                self._link(actions, "Save", lambda f=field, p=problem, old=name: on_save(old, f.get(), p), theme.PRIMARY).pack(side="left")
                self._link(actions, "Cancel", on_cancel, theme.TEXT_MUTED).pack(side="left")
            else:
                widgets.label(line, name, color=theme.TEXT).grid(row=0, column=0, sticky="w", padx=14, pady=10)
                self._link(actions, "Edit", lambda n=name: on_edit(n), theme.PRIMARY).pack(side="left")
                self._link(actions, "Remove", lambda n=name: on_remove(n), theme.DEBIT).pack(side="left")

    @staticmethod
    def _link(parent, text: str, command, colour: str) -> ctk.CTkButton:
        return ctk.CTkButton(parent, text=text, command=command, width=64, height=30, corner_radius=8, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, text_color=colour, font=widgets.text_font(theme.FONT_SIZE_BODY))

    def _render_entries(self, active: list[models.MainEntry]) -> None:
        editing_name = self.main_entries.label(self.editing_entry) if self.editing_entry else None
        self._render_table(
            self.entries_card,
            [item.name for item in active],
            editing_name,
            on_edit=self._edit_entry,
            on_save=self._save_entry,
            on_cancel=self._cancel_entry,
            on_remove=self._remove_entry,
        )

    def _render_fields(self) -> None:
        self._render_table(
            self.fields_card,
            self.subheads.active_names(self.main_head),
            self.editing_field,
            on_edit=self._edit_field,
            on_save=self._save_field,
            on_cancel=self._cancel_field,
            on_remove=self._remove_field,
        )

    # ----- Main Entries -----

    def _id_of(self, name: str) -> str | None:
        return next((item.id for item in self.main_entries.active() if item.name == name), None)

    def _add_entry(self) -> None:
        card = self.entries_card
        result = self.main_entries.add(card["entry"].get())
        card["error"].configure(text=result.message)
        if result.ok:
            card["entry"].delete(0, "end")
            self.notify("Main Entry added.")
            self._entries_changed()

    def _edit_entry(self, name: str) -> None:
        self.editing_entry = self._id_of(name)
        self.refresh()

    def _cancel_entry(self) -> None:
        self.editing_entry = None
        self.entries_card["error"].configure(text="")
        self.refresh()

    def _save_entry(self, old_name: str, new_name: str, problem) -> None:
        result = self.main_entries.rename(self._id_of(old_name) or "", new_name)
        if not result.ok:
            problem.configure(text=result.message)
            return
        self.editing_entry = None
        self.notify("Main Entry renamed.")
        self._entries_changed()

    def _remove_entry(self, name: str) -> None:
        main_head = self._id_of(name)
        if main_head is None:
            return
        ConfirmPopup(
            self,
            "Remove Main Entry",
            f'Remove "{name}" from the sidebar?',
            "Entries already saved under it stay in the Transaction List.",
            "Remove",
            action=lambda: self.main_entries.remove(main_head),
            on_done=lambda: (self.notify("Main Entry removed."), self._entries_changed()),
        )

    def _entries_changed(self) -> None:
        self.on_entries_changed()
        self.refresh()

    # ----- Transactions fields -----

    def _add_field(self) -> None:
        card = self.fields_card
        result = self.subheads.add_subhead(self.main_head, card["entry"].get())
        card["error"].configure(text=result.message if not result.ok else "")
        if result.ok:
            card["entry"].delete(0, "end")
            self.notify("Field added.")
            self._render_fields()

    def _edit_field(self, name: str) -> None:
        self.editing_field = name
        self._render_fields()

    def _cancel_field(self) -> None:
        self.editing_field = None
        self.fields_card["error"].configure(text="")
        self._render_fields()

    def _save_field(self, old_name: str, new_name: str, problem) -> None:
        result = self.subheads.rename_subhead(self.main_head, old_name, new_name)
        if not result.ok:
            problem.configure(text=result.message)
            return
        self.editing_field = None
        self.notify("Field renamed.")
        self._render_fields()

    def _remove_field(self, name: str) -> None:
        ConfirmPopup(
            self,
            "Remove Field",
            f'Remove "{name}" from the Transactions list?',
            "Old entries keep this name.",
            "Remove",
            action=lambda: self.subheads.remove_subhead(self.main_head, name),
            on_done=lambda: (self.notify("Field removed."), self._render_fields()),
        )
