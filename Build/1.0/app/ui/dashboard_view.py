"""Dashboard page: the Monthly Summary and the Yearly Summary, each with a chart (moved from the Transaction List).

The six summary values come from report_service.summarize. They ignore the Transaction List filters.
The chart under the monthly cards shows each day of the month; the one under the yearly cards shows each month.
"""

import calendar
from datetime import date

import customtkinter as ctk

from app.core import money, theme
from app.core.models import Entry
from app.services import report_service as rs
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.ui import widgets
from app.ui.charts import BarChart

ALL_ENTRIES = "All Main Entries"


class DashboardView(ctk.CTkFrame):
    """refresh() reloads the rows each time the page opens (FR-18)."""

    def __init__(self, master, main_entries: MainEntryService, entries: EntryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.main_entries = main_entries
        self.entries = entries
        self.all_rows: list[Entry] = []

        self.grid_columnconfigure(0, weight=1)
        scope = ctk.CTkFrame(self, fg_color="transparent")
        scope.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        widgets.label(scope, "Showing", color=theme.TEXT_MUTED).pack(side="left", padx=(0, 10))
        self.scope_menu = widgets.SelectBox(scope, values=[ALL_ENTRIES], command=lambda _choice: self._render(), width=240)
        self.scope_menu.pack(side="left")

        self.month = self._summary_card(1, "Monthly Summary", "month")
        self.year = self._summary_card(2, "Yearly Summary", "year")

    # ----- layout -----

    def _summary_card(self, row: int, title: str, kind: str) -> dict:
        card = widgets.card(self)
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(16, 0) if row == 1 else (16, 24))
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(18, 10))
        widgets.label(head, title, size=theme.FONT_SIZE_CARD_TITLE).pack(side="left")
        menu = widgets.SelectBox(head, values=[""], command=lambda _choice: self._render(), width=180)
        menu.pack(side="right")

        chart = BarChart(card, height=250)
        chart.pack(fill="x", padx=20, pady=(0, 10))

        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=14, pady=(0, 18))
        for column in range(3):
            stats.grid_columnconfigure(column, weight=1, uniform=f"{kind}-stats")
        cells = []
        for index in range(6):
            cell = ctk.CTkFrame(stats, fg_color=theme.SURFACE_TINT, corner_radius=12)
            cell.grid(row=index // 3, column=index % 3, sticky="nsew", padx=6, pady=6)
            label = widgets.label(cell, "", size=theme.FONT_SIZE_BODY)
            label.pack(anchor="w", padx=16, pady=(12, 0))
            value = widgets.label(cell, "", size=theme.FONT_SIZE_VALUE, wraplength=230, justify="left")
            value.pack(anchor="w", padx=16, pady=(2, 0))
            sub = widgets.label(cell, "", size=theme.FONT_SIZE_BODY, color=theme.TEXT_MUTED)
            sub.pack(anchor="w", padx=16, pady=(0, 12))
            cells.append((label, value, sub))

        return {"menu": menu, "cells": cells, "chart": chart}

    # ----- data -----

    def refresh(self) -> None:
        labels = [ALL_ENTRIES] + [item.name for item in self.main_entries.items()]
        self.scope_menu.configure(values=labels)
        if self.scope_menu.get() not in labels:
            self.scope_menu.set(ALL_ENTRIES)
        self.all_rows = self.entries.all_entries()
        self._render()

    def _scoped_rows(self) -> list[Entry]:
        choice = self.scope_menu.get()
        if choice == ALL_ENTRIES:
            return self.all_rows
        main_head = self.main_entries.id_for_label(choice)
        return [entry for entry in self.all_rows if entry.main_head == main_head]

    def _render(self) -> None:
        rows = self._scoped_rows()
        today = date.today()

        months = sorted({(e.entry_date.year, e.entry_date.month) for e in rows}, reverse=True)
        month_labels = [f"{calendar.month_abbr[m]} {y}" for y, m in months] or [f"{calendar.month_abbr[today.month]} {today.year}"]
        self.month["menu"].configure(values=month_labels)
        if self.month["menu"].get() not in month_labels:
            self.month["menu"].set(month_labels[0])
        month_text = self.month["menu"].get()
        month_year, month_number = months[month_labels.index(month_text)] if months else (today.year, today.month)
        month_rows = rs.entries_in_month(rows, month_year, month_number)
        self._fill_cards(self.month["cells"], rs.summarize(month_rows))
        self.month["chart"].show(rs.daily_series(rows, month_year, month_number), f"Each day of {month_text}")

        years = sorted({e.entry_date.year for e in rows}, reverse=True)
        year_labels = [str(y) for y in years] or [str(today.year)]
        self.year["menu"].configure(values=year_labels)
        if self.year["menu"].get() not in year_labels:
            self.year["menu"].set(year_labels[0])
        year = int(self.year["menu"].get())
        self._fill_cards(self.year["cells"], rs.summarize(rs.entries_in_year(rows, year)))
        self.year["chart"].show(rs.monthly_series(rows, year), f"Each month of {year}")

    def _fill_cards(self, cells, summary: rs.Summary) -> None:
        values = [
            ("Debit (Total Amount)", money.format_amount(summary.debit_total), "", theme.DEBIT),
            ("Most Debited Sub-Head", *self._ranked_text(summary.most_debit, "debit"), theme.DEBIT),
            ("Least Debited Sub-Head", *self._ranked_text(summary.least_debit, "debit"), theme.DEBIT),
            ("Credit (Total Amount)", money.format_amount(summary.credit_total), "", theme.CREDIT),
            ("Most Credited Sub-Head", *self._ranked_text(summary.most_credit, "credit"), theme.CREDIT),
            ("Least Credited Sub-Head", *self._ranked_text(summary.least_credit, "credit"), theme.CREDIT),
        ]
        for (label, value, sub, colour), (label_widget, value_widget, sub_widget) in zip(values, cells):
            label_widget.configure(text=label)
            value_widget.configure(text=value, text_color=colour)
            sub_widget.configure(text=sub, text_color=colour if sub else theme.TEXT_MUTED)

    @staticmethod
    def _ranked_text(item: rs.Ranked | None, kind: str) -> tuple[str, str]:
        if item is None:
            return "—", "0.00"
        amount = item.debit if kind == "debit" else item.credit
        return item.name, money.format_amount(amount)
