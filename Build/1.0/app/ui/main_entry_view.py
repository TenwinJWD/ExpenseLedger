"""Main Entry page (Design.md Section 5; PRD FR-7 to FR-17).

The form stays disabled until a sub-head is chosen, and Submit stays disabled until
the form is valid. Errors show under a field only after the user has left that field.
"""

import tkinter as tk
from datetime import date

import customtkinter as ctk

from app.core import config, dates, models, money, theme
from app.core.validation import check_entry
from app.services.entry_service import EntryService
from app.services.subhead_service import SubheadService
from app.ui import widgets
from app.ui.subhead_popup import AddSubheadPopup, RemoveSubheadPopup

SELECT = "-Select-"
TRANSACTION_FIELDS = ("date", "name", "particulars", "debit", "credit")


class MainEntryView(ctk.CTkFrame):
    """The entry form, with the Main Head and Sub-Head choices above it."""

    def __init__(self, master, subheads: SubheadService, entries: EntryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.subheads = subheads
        self.entries = entries
        self.touched: set[str] = set()

        self.head_var = ctk.StringVar(value=models.DEFAULT_MAIN_HEAD)
        self.sub_var = ctk.StringVar(value=SELECT)
        self.date_var = ctk.StringVar()
        self.name_var = ctk.StringVar()
        self.particulars_var = ctk.StringVar()
        self.debit_var = ctk.StringVar(value="")
        self.credit_var = ctk.StringVar(value="")
        for variable in (self.date_var, self.name_var, self.particulars_var, self.debit_var, self.credit_var):
            variable.trace_add("write", lambda *_args: self._update_state())

        self.grid_columnconfigure(0, weight=1)
        widgets.label(self, "Main Entry", size=theme.FONT_SIZE_PAGE_TITLE).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 0))
        widgets.label(self, "Record a daily collection or a Treesa Agencies entry", color=theme.TEXT_MUTED).grid(row=1, column=0, sticky="w", padx=24, pady=(2, 16))

        form = widgets.card(self)
        form.grid(row=2, column=0, sticky="ew", padx=24)
        form.grid_columnconfigure(tuple(range(6)), weight=1, uniform="fields")
        self._build_head_and_subhead(form)
        self._build_fields(form)
        self._build_buttons(form)

        self.message = ctk.CTkLabel(self, text="", font=widgets.text_font(theme.FONT_SIZE_BODY), corner_radius=theme.BUTTON_RADIUS, padx=14, pady=10, anchor="w")
        self.message.grid(row=3, column=0, sticky="ew", padx=24, pady=(14, 0))
        self.message.grid_remove()

        self._reload_subheads("")
        self._update_state()

    # ----- layout -----

    def _build_head_and_subhead(self, form) -> None:
        widgets.field_label(form, "Main Head", tip="Choose Daily Collection or Treesa Agencies. Each has its own Sub-Head list.").grid(row=0, column=0, columnspan=6, sticky="w", padx=20, pady=(20, 6))
        heads = ctk.CTkFrame(form, fg_color="transparent")
        heads.grid(row=1, column=0, columnspan=6, sticky="w", padx=20)
        for code, label in models.MAIN_HEADS.items():
            ctk.CTkRadioButton(
                heads,
                text=label,
                variable=self.head_var,
                value=code,
                command=self._on_head_change,
                fg_color=theme.PRIMARY,
                hover_color=theme.PRIMARY_HOVER,
                text_color=theme.TEXT,
                font=widgets.text_font(theme.FONT_SIZE_BODY),
            ).pack(side="left", padx=(0, 28))

        # Sub-Head and Date share one row: Sub-Head takes four of the six columns, Date two.
        sub_cell = self._field(form, 2, 0, "Sub-Head", required=False, span=4, tip="The category for this entry. Pick one to enable the form. Add creates a new one; Remove deletes the selected one.")
        row = ctk.CTkFrame(sub_cell, fg_color="transparent")
        row.pack(fill="x")
        self.remove_button = widgets.secondary_button(row, "Remove", self._open_remove, width=100)
        self.remove_button.pack(side="right")
        self.add_button = widgets.secondary_button(row, "Add", self._open_add, width=70)
        self.add_button.pack(side="right", padx=(8, 8))
        self.sub_menu = widgets.SelectBox(row, values=[SELECT], variable=self.sub_var, command=self._on_sub_change, width=220)
        self.sub_menu.pack(side="left", fill="x", expand=True)
        self.sub_hint = widgets.label(form, "Select a Sub-Head to enable entry.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED)
        self.sub_hint.grid(row=3, column=0, columnspan=6, sticky="w", padx=20, pady=(6, 0))

    def _build_fields(self, form) -> None:
        # Date sits beside Sub-Head; Name and Particulars share a row; Debit and Credit share the last row.
        self.date_cell = self._field(form, 2, 4, "Date", required=True, span=2, tip="The day of the transaction, as DD/MM/YYYY. Use the calendar button to pick it.")
        date_row = ctk.CTkFrame(self.date_cell, fg_color="transparent")
        date_row.pack(fill="x")
        self.date_entry = widgets.entry(date_row, placeholder="DD/MM/YYYY", textvariable=self.date_var)
        self.date_entry.pack(side="left", fill="x", expand=True)
        self.date_button = widgets.secondary_button(date_row, theme.ICON_CALENDAR, self._open_calendar, width=36, font=widgets.icon_font(14))
        self.date_button.pack(side="left", padx=(8, 0))
        self.date_error = widgets.error_label(self.date_cell)
        self.date_error.pack(fill="x")
        self.date_entry.bind("<FocusOut>", lambda _event: self._on_blur("date"))

        self.name_cell = self._field(form, 4, 0, "Name", required=True, span=2, tip="Who paid or was paid for this entry.")
        self.name_entry = widgets.entry(self.name_cell, textvariable=self.name_var)
        self.name_entry.pack(fill="x")
        self.name_error = widgets.error_label(self.name_cell)
        self.name_error.pack(fill="x")
        self.name_entry.bind("<FocusOut>", lambda _event: self._on_blur("name"))

        self.particulars_cell = self._field(form, 4, 2, "Particulars", required=True, span=4, tip="A short description of what the entry is for.")
        self.particulars_entry = widgets.entry(self.particulars_cell, textvariable=self.particulars_var)
        self.particulars_entry.pack(fill="x")
        self.particulars_error = widgets.error_label(self.particulars_cell)
        self.particulars_error.pack(fill="x")
        self.particulars_entry.bind("<FocusOut>", lambda _event: self._on_blur("particulars"))

        self.debit_cell = self._field(form, 5, 0, "Debit", required=True, span=3, color=theme.DEBIT, tip="Money paid out. Enter an amount, or leave blank if this entry is a credit.")
        self.debit_entry = widgets.entry(self.debit_cell, textvariable=self.debit_var, justify="right", placeholder="0.00")
        self.debit_entry.pack(fill="x")
        self.debit_error = widgets.error_label(self.debit_cell)
        self.debit_error.pack(fill="x")
        self.debit_entry.bind("<FocusOut>", lambda _event: self._on_blur("debit"))

        self.credit_cell = self._field(form, 5, 3, "Credit", required=True, span=3, color=theme.CREDIT, tip="Money received. Enter an amount, or leave blank if this entry is a debit.")
        self.credit_entry = widgets.entry(self.credit_cell, textvariable=self.credit_var, justify="right", placeholder="0.00")
        self.credit_entry.pack(fill="x")
        self.credit_error = widgets.error_label(self.credit_cell)
        self.credit_error.pack(fill="x")
        self.credit_entry.bind("<FocusOut>", lambda _event: self._on_blur("credit"))

        self.amount_hint = widgets.label(form, "Enter a Debit or Credit amount greater than 0.00.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED)
        self.amount_hint.grid(row=6, column=0, columnspan=6, sticky="w", padx=20, pady=(4, 0))

        for entry in (self.name_entry, self.particulars_entry, self.debit_entry, self.credit_entry):
            entry.bind("<Return>", lambda _event: self._submit())

    def _field(self, form, row: int, column: int, text: str, required: bool, span: int = 1, color: str = theme.TEXT, tip: str = "") -> ctk.CTkFrame:
        cell = ctk.CTkFrame(form, fg_color="transparent")
        cell.grid(row=row, column=column, columnspan=span, sticky="new", padx=20, pady=(12, 0))
        widgets.field_label(cell, text, required=required, color=color, tip=tip).pack(fill="x", pady=(0, 6))
        return cell

    def _build_buttons(self, form) -> None:
        bar = ctk.CTkFrame(form, fg_color="transparent")
        bar.grid(row=7, column=0, columnspan=6, sticky="e", padx=20, pady=(18, 20))
        self.clear_button = widgets.secondary_button(bar, "Clear", self._clear)
        self.clear_button.pack(side="left", padx=(0, 10))
        self.submit_button = widgets.primary_button(bar, "Submit", self._submit, state="disabled", width=160)
        self.submit_button.pack(side="left")

    # ----- data -----

    def refresh(self) -> None:
        """Reload the sub-heads each time the page opens (Architecture 4.4)."""
        self._reload_subheads(self.sub_var.get())
        self._update_state()

    def _reload_subheads(self, keep: str) -> None:
        names = self.subheads.active_names(self.head_var.get())
        self.sub_menu.configure(values=[SELECT] + names)
        self.sub_var.set(keep if keep in names else SELECT)

    def _chosen_sub_head(self) -> str | None:
        choice = self.sub_var.get()
        return None if choice == SELECT else choice

    def _clear_transaction(self) -> None:
        self.date_var.set("")
        self.name_var.set("")
        self.particulars_var.set("")
        self.debit_var.set("")
        self.credit_var.set("")
        self.touched.clear()

    # ----- events -----

    def _on_head_change(self) -> None:
        # The two Main Heads have different sub-head lists, so the choice goes back to -Select-.
        self._reload_subheads("")
        self._clear_transaction()
        self._hide_message()
        self._update_state()

    def _on_sub_change(self, choice: str) -> None:
        if choice == SELECT:
            self._clear_transaction()
        self._hide_message()
        self._update_state()

    def _on_blur(self, field: str) -> None:
        self.touched.add(field)
        if field == "date":
            parsed = dates.parse_date(self.date_var.get())
            if parsed is not None:
                self.date_var.set(dates.format_date_slash(parsed))
        if field in ("debit", "credit"):
            amount = money.parse_amount(self.debit_var.get() if field == "debit" else self.credit_var.get())
            if amount is not None:
                (self.debit_var if field == "debit" else self.credit_var).set(money.format_amount(amount))
        self._update_state()

    def _update_state(self) -> None:
        has_sub_head = self._chosen_sub_head() is not None
        field_state = "normal" if has_sub_head else "disabled"
        for entry in (self.date_entry, self.name_entry, self.particulars_entry, self.debit_entry, self.credit_entry):
            entry.configure(state=field_state)
        self.date_button.configure(state=field_state)
        self.sub_hint.grid_remove() if has_sub_head else self.sub_hint.grid()
        self.remove_button.configure(state="normal" if has_sub_head else "disabled")

        check = check_entry(
            has_sub_head,
            self.date_var.get(),
            self.name_var.get(),
            self.particulars_var.get(),
            self.debit_var.get(),
            self.credit_var.get(),
        )
        self._show_error(self.date_error, "date", check.errors)
        self._show_error(self.name_error, "name", check.errors)
        self._show_error(self.particulars_error, "particulars", check.errors)
        self._show_error(self.debit_error, "debit", check.errors)
        self._show_error(self.credit_error, "credit", check.errors)
        self.amount_hint.grid_remove() if not (has_sub_head and check.both_zero) else self.amount_hint.grid()
        self.submit_button.configure(state="normal" if check.valid else "disabled")

    def _show_error(self, label: ctk.CTkLabel, field: str, errors: dict[str, str]) -> None:
        label.configure(text=errors.get(field, "") if field in self.touched else "")

    def _submit(self) -> None:
        if str(self.submit_button.cget("state")) == "disabled":
            return
        head = self.head_var.get()
        check = check_entry(
            self._chosen_sub_head() is not None,
            self.date_var.get(),
            self.name_var.get(),
            self.particulars_var.get(),
            self.debit_var.get(),
            self.credit_var.get(),
        )
        if not check.valid or check.values is None:
            self._update_state()
            return
        values = check.values
        result = self.entries.save_entry(
            head,
            self._chosen_sub_head(),
            values["date"],
            values["name"],
            values["particulars"],
            values["debit"],
            values["credit"],
        )
        if not result.ok:
            self._show_message(result.message, kind="warning")
            return
        self._clear_transaction()
        self._show_message(f"Entry saved to {dates.format_date_slash(values['date'])}.", kind="success")
        self._update_state()

    def _clear(self) -> None:
        self._clear_transaction()
        self._hide_message()
        self._update_state()

    # ----- sub-head popups (PRD FR-8, FR-9) -----

    def _open_add(self) -> None:
        AddSubheadPopup(self, self.subheads, self.head_var.get(), on_added=self._on_added)

    def _on_added(self, name: str, warning: str) -> None:
        self._reload_subheads(name)
        self._update_state()
        if warning:
            self._show_message(warning, kind="warning")

    def _open_remove(self) -> None:
        name = self._chosen_sub_head()
        if name is None:
            return
        RemoveSubheadPopup(self, self.subheads, self.head_var.get(), name, on_removed=self._on_removed)

    def _on_removed(self) -> None:
        self._reload_subheads("")
        self._clear_transaction()
        self._hide_message()
        self._update_state()

    # ----- calendar (PRD FR-13) -----

    def _open_calendar(self) -> None:
        """Open the styled calendar under the date field. The chosen day fills the field (FR-13)."""
        def chosen(day: date) -> None:
            self.date_var.set(dates.format_date_slash(day))
            self.touched.add("date")
            self._update_state()

        widgets.DatePopup(self.date_button, dates.parse_date(self.date_var.get()), on_pick=chosen)

    # ----- message bar (Design.md 7) -----

    def _show_message(self, text: str, kind: str) -> None:
        colours = {
            "success": (theme.SUCCESS_BG, theme.CREDIT),
            "warning": (theme.WARNING_BG, theme.WARNING),
            "error": (theme.ERROR_BG, theme.ERROR),
        }
        background, foreground = colours[kind]
        self.message.configure(text=text, fg_color=background, text_color=foreground)
        self.message.grid()

    def _hide_message(self) -> None:
        self.message.grid_remove()
