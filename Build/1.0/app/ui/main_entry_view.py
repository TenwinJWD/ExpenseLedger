"""Main Entry page (Design.md Section 5; PRD FR-7 to FR-17).

One page serves every Main Entry: the sidebar item picks it (show). The "Transactions" list is the
Main Entry's sub-head list. The form stays disabled until one is chosen, and Submit stays disabled until
the form is valid. Errors show under a field only after the user has left that field.
"""

import tkinter as tk
from datetime import date
from typing import Callable

import customtkinter as ctk

from app.core import config, dates, models, money, theme
from app.core.validation import check_entry
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.services.subhead_service import SubheadService
from app.ui import widgets
from app.ui.expense_report_view import ExpenseReportView

SELECT = "-Select-"
TRANSACTION_FIELDS = ("date", "name", "particulars", "debit", "credit")


class MainEntryView(ctk.CTkFrame):
    """The entry form of one Main Entry, with the Transactions choice above it."""

    def __init__(self, master, main_entries: MainEntryService, subheads: SubheadService, entries: EntryService, notify: Callable[[str], None] = lambda _text: None) -> None:
        super().__init__(master, fg_color="transparent")
        self.main_entries = main_entries
        self.subheads = subheads
        self.entries = entries
        self.main_head = models.DEFAULT_MAIN_HEAD
        self.touched: set[str] = set()

        self.sub_var = ctk.StringVar(value=SELECT)
        self.date_var = ctk.StringVar()
        self.name_var = ctk.StringVar()
        self.particulars_var = ctk.StringVar()
        self.debit_var = ctk.StringVar(value="")
        self.credit_var = ctk.StringVar(value="")
        for variable in (self.date_var, self.name_var, self.particulars_var, self.debit_var, self.credit_var):
            variable.trace_add("write", lambda *_args: self._update_state())

        self.grid_columnconfigure(0, weight=1)
        form = widgets.card(self)
        form.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        form.grid_columnconfigure((0, 1), weight=1, uniform="fields")  # every field is half the width of the card
        self._build_head_and_subhead(form)
        self._build_fields(form)
        self._build_buttons(form)

        self.message = ctk.CTkLabel(self, text="", font=widgets.text_font(theme.FONT_SIZE_BODY), corner_radius=theme.BUTTON_RADIUS, padx=14, pady=10, anchor="w")
        self.message.grid(row=1, column=0, sticky="ew", padx=24, pady=(14, 0))
        self.message.grid_remove()

        # The entries of this Main Entry, under the form. show() points it at the open Main Entry.
        self.table = ExpenseReportView(self, main_entries, subheads, entries, notify=notify, locked_head=self.main_head)
        self.table.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        self._reload_subheads("")
        self._update_state()

    # ----- layout -----

    def _build_head_and_subhead(self, form) -> None:
        header = ctk.CTkFrame(form, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 0))
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", fill="x", expand=True)
        widgets.label(titles, "New Transaction", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w")
        self.subtitle = widgets.label(titles, "", color=theme.TEXT_MUTED)
        self.subtitle.pack(anchor="w")

        # Two equal columns: Transactions and Date, Name and Particulars, Debit and Credit.
        sub_cell = self._field(form, 2, 0, "Transactions", required=False, span=1, tip="The choices for this Main Entry. Pick one to enable the form. Modify Fields (in the sidebar) edits the list.")
        row = ctk.CTkFrame(sub_cell, fg_color="transparent")
        row.pack(fill="x")
        self.sub_menu = widgets.SelectBox(row, values=[SELECT], variable=self.sub_var, command=self._on_sub_change, width=220)
        self.sub_menu.pack(side="left", fill="x", expand=True)
        self.sub_hint = widgets.label(form, "Select a Transaction to enable entry.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED)
        self.sub_hint.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(6, 0))

    def _build_fields(self, form) -> None:
        # Date sits beside Sub-Head; Name and Particulars share a row; Debit and Credit share the last row.
        self.date_cell = self._field(form, 2, 1, "Date", required=True, span=1, tip="The day of the transaction, as DD/MM/YYYY. Use the calendar button to pick it.")
        date_row = ctk.CTkFrame(self.date_cell, fg_color="transparent")
        date_row.pack(fill="x")
        self.date_entry = widgets.entry(date_row, placeholder="DD/MM/YYYY", textvariable=self.date_var)
        self.date_entry.pack(fill="x")
        # The calendar button sits inside the field's right end, so the field is as wide as all the others.
        self.date_button = widgets.secondary_button(date_row, theme.ICON_CALENDAR, self._open_calendar, width=34, font=widgets.icon_font(14))
        self.date_button.configure(height=28, border_width=0, fg_color=theme.BG_INPUT)
        self.date_button.place(relx=1.0, rely=0.5, x=-8, anchor="e")
        self.date_error = widgets.error_label(self.date_cell, fixed=True)
        self.date_error.pack(fill="x")
        self.date_entry.bind("<FocusOut>", lambda _event: self._on_blur("date"))

        self.name_cell = self._field(form, 4, 0, "Name", required=True, span=1, tip="Who paid or was paid for this entry.")
        self.name_entry = widgets.entry(self.name_cell, textvariable=self.name_var)
        self.name_entry.pack(fill="x")
        self.name_error = widgets.error_label(self.name_cell, fixed=True)
        self.name_error.pack(fill="x")
        self.name_entry.bind("<FocusOut>", lambda _event: self._on_blur("name"))

        self.particulars_cell = self._field(form, 4, 1, "Particulars", required=True, span=1, tip="A short description of what the entry is for.")
        self.particulars_entry = widgets.entry(self.particulars_cell, textvariable=self.particulars_var)
        self.particulars_entry.pack(fill="x")
        self.particulars_error = widgets.error_label(self.particulars_cell, fixed=True)
        self.particulars_error.pack(fill="x")
        self.particulars_entry.bind("<FocusOut>", lambda _event: self._on_blur("particulars"))

        self.debit_cell = self._field(form, 5, 0, "Debit", required=True, span=1, color=theme.DEBIT, tip="Money paid out. Enter an amount, or leave blank if this entry is a credit.")
        self.debit_entry = widgets.entry(self.debit_cell, textvariable=self.debit_var, justify="right", placeholder="0.00")
        self.debit_entry.pack(fill="x")
        self.debit_error = widgets.error_label(self.debit_cell, fixed=True)
        self.debit_error.pack(fill="x")
        self.debit_entry.bind("<FocusOut>", lambda _event: self._on_blur("debit"))

        self.credit_cell = self._field(form, 5, 1, "Credit", required=True, span=1, color=theme.CREDIT, tip="Money received. Enter an amount, or leave blank if this entry is a debit.")
        self.credit_entry = widgets.entry(self.credit_cell, textvariable=self.credit_var, justify="right", placeholder="0.00")
        self.credit_entry.pack(fill="x")
        self.credit_error = widgets.error_label(self.credit_cell, fixed=True)
        self.credit_error.pack(fill="x")
        self.credit_entry.bind("<FocusOut>", lambda _event: self._on_blur("credit"))

        self.amount_hint = widgets.label(form, "Enter a Debit or Credit amount greater than 0.00.", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED)
        self.amount_hint.grid(row=6, column=0, columnspan=2, sticky="w", padx=20, pady=(4, 0))

        for entry in (self.name_entry, self.particulars_entry, self.debit_entry, self.credit_entry):
            entry.bind("<Return>", lambda _event: self._submit())

    def _field(self, form, row: int, column: int, text: str, required: bool, span: int = 1, color: str = theme.TEXT, tip: str = "") -> ctk.CTkFrame:
        cell = ctk.CTkFrame(form, fg_color="transparent")
        cell.grid(row=row, column=column, columnspan=span, sticky="new", padx=20, pady=(12, 0))
        widgets.field_label(cell, text, required=required, color=color, tip=tip).pack(fill="x", pady=(0, 6))
        return cell

    def _build_buttons(self, form) -> None:
        bar = ctk.CTkFrame(form, fg_color="transparent")
        bar.grid(row=7, column=0, columnspan=2, sticky="e", padx=20, pady=(18, 20))
        self.clear_button = widgets.cancel_button(bar, "Cancel", self._clear)
        self.clear_button.pack(side="left", padx=(0, 10))
        self.submit_button = widgets.primary_button(bar, "Submit", self._submit, state="disabled", width=160)
        self.submit_button.pack(side="left")

    # ----- data -----

    def show(self, main_head: str) -> None:
        """Open the form for a Main Entry. Each Main Entry has its own list, so the choice goes back to -Select-."""
        if main_head != self.main_head:
            self.main_head = main_head
            self._clear_transaction()
            self._hide_message()
            self.sub_var.set(SELECT)
            self.table.set_main_head(main_head)

    def refresh(self) -> None:
        """Reload the sub-heads each time the page opens (Architecture 4.4)."""
        self.subtitle.configure(text=f"Record an entry for {self.main_entries.label(self.main_head)}")
        self._reload_subheads(self.sub_var.get())
        self._update_state()
        self.table.refresh()

    def _reload_subheads(self, keep: str) -> None:
        names = self.subheads.active_names(self.main_head)
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
        self.sub_hint.configure(text="" if has_sub_head else "Select a Transaction to enable entry.")

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
        self.amount_hint.configure(text="Enter a Debit or Credit amount greater than 0.00." if has_sub_head and check.both_zero else "")
        self.submit_button.configure(state="normal" if check.valid else "disabled")

    def _show_error(self, label: ctk.CTkLabel, field: str, errors: dict[str, str]) -> None:
        text = errors.get(field, "") if field in self.touched else ""
        if field == "date" and text:
            text = "Use DD/MM/YYYY."  # short, so the Date column never grows
        label.configure(text=text)

    def _submit(self) -> None:
        if str(self.submit_button.cget("state")) == "disabled":
            return
        head = self.main_head
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
        self.table.refresh()

    def _clear(self) -> None:
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
