"""Transaction List page (Design.md Section 6; PRD FR-18 to FR-23, FR-18a, FR-19a).

The same view is also placed under the entry form of each Main Entry. There it is locked to that Main Entry
(locked_head) and shows only the Search, Date Range, Sub-Head, Debit and Credit filters, without Import and Export.

Order on the page: the filter card, then the table with pagination, newest entry first. The Monthly and
Yearly Summary cards now live on the Dashboard.
"""

import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk

from app.core import config, dates, money, theme
from app.core.models import Entry
from app.core.validation import check_entry
from app.services import exchange_service, pdf_report, report_service as rs
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.services.subhead_service import SubheadService
from app.ui import widgets

ALL_RANGES = (("All Dates", "all"), ("This Month", "this-month"), ("Last Month", "last-month"),
              ("This Year", "this-year"), ("Custom Range", "custom"))
ALL_MAIN_ENTRIES = "All Main Entries"
ALL_SUB_HEADS = "All Transactions"
SELECT = "-Select-"
COLUMN_WEIGHTS = (1, 3, 3, 4, 3, 1, 1, 1, 1)
COLUMN_MIN_WIDTHS = (140, 130, 130, 130, 120, 90, 90, 84, 110)  # screen pixels, not scaled units
CELL_PADX = 5
FIELD_HEIGHT = 32  # the filter fields are shorter than the form fields
FIELD_FONT = 14
LINE_COLOUR = theme.ROW_BORDER  # the line under the table heading
HEADERS = ("Date", "Main Entry", "Transactions", "Name", "Particulars", "Debit", "Credit", "User", "Actions")
COLUMN_COUNT = len(HEADERS)
AMOUNT_COLUMNS = (5, 6)
ACTIONS_COLUMN = COLUMN_COUNT - 1
HEAD_COLUMN = 1  # the Main Entry column; left out when the table is locked to one Main Entry

FILTER_TIPS = {
    "Search": "Finds rows where the name, particulars or an amount contains this text.",
    "Date Range": "Shows only entries inside this period. Custom Range lets you type From and To dates.",
    "From": "First day to include, as DD/MM/YYYY.",
    "To": "Last day to include, as DD/MM/YYYY.",
    "Main Entry": "Shows only entries under this Main Entry.",
    "Transactions": "Shows only entries under this Transaction.",
    "Name": "Shows only rows whose name contains this text.",
    "Particulars": "Shows only rows whose particulars contain this text.",
    "Debit From": "Smallest debit amount to include.",
    "Debit To": "Largest debit amount to include.",
    "Credit From": "Smallest credit amount to include.",
    "Credit To": "Largest credit amount to include.",
}


class ExpenseReportView(ctk.CTkFrame):
    """The whole Transaction List page. refresh() reloads the rows each time the page opens (FR-18)."""

    def __init__(self, master, main_entries: MainEntryService, subheads: SubheadService, entries: EntryService, notify: Callable[[str], None] = lambda _text: None, locked_head: str | None = None) -> None:
        super().__init__(master, fg_color="transparent")
        self.notify = notify
        self.locked_head = locked_head  # the Main Entry this table is limited to, or None for all of them
        self.main_entries = main_entries
        self.subheads = subheads
        self.entries = entries
        self.all_rows: list[Entry] = []
        self.filters = rs.Filters(main_head=locked_head or "ALL")
        self.resolved = rs.ResolvedFilters(main_head=locked_head or "ALL")
        self.page = 1
        self.page_size = config.DEFAULT_PAGE_SIZE
        self.editing_key: tuple[str, str] | None = None
        self.edit_widgets: dict = {}
        self.delete_target: Entry | None = None

        self.grid_columnconfigure(0, weight=1)
        self.filter_card = self._build_filters()
        self.filter_card.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 14))

        self.table_card = widgets.card(self)
        self.table_card.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)
        # The table has its own dark outline, with lines between the rows and the columns (drawn in _render_table).
        self.rows = ctk.CTkFrame(self.table_card, fg_color="transparent", corner_radius=0)
        self.rows.grid(row=1, column=0, sticky="nsew", padx=16, pady=(10, 16))
        self._build_toolbar()
        self._build_pager()
        self.grid_rowconfigure(1, weight=1)

    # ----- layout -----

    def _build_filters(self) -> ctk.CTkFrame:
        card = widgets.card(self)
        card.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="filters")

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=(14, 0))
        titles = ctk.CTkFrame(head, fg_color="transparent")
        titles.pack(side="left", fill="x", expand=True)
        widgets.label(titles, "Filters", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w")
        widgets.label(titles, "Newest entry first", color=theme.TEXT_MUTED).pack(anchor="w")
        widgets.primary_button(head, "Filter Report", self._apply_filters, width=150).pack(side="right")
        widgets.cancel_button(head, "Clear Filters", self._clear_filters, width=140).pack(side="right", padx=(0, 10))

        widgets.field_label(card, "Search", tip=FILTER_TIPS["Search"], size=theme.FONT_SIZE_LABEL).grid(row=1, column=0, columnspan=4 if self.locked_head else 3, sticky="w", padx=(20, 8), pady=(8, 0))
        self.search = widgets.entry(card, placeholder="Search by name, particulars, or amount", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.search.grid(row=2, column=0, columnspan=4 if self.locked_head else 3, sticky="ew", padx=(20, 20) if self.locked_head else (20, 8), pady=(3, 0))
        self.search.bind("<Return>", lambda _event: self._apply_filters())
        self.head_menu = self._menu(card, [ALL_MAIN_ENTRIES], self._on_head_change)

        self.range_menu = self._menu(card, [label for label, _value in ALL_RANGES], self._on_range_change)
        self.sub_menu = self._menu(card, [ALL_SUB_HEADS], lambda _choice: None)
        self.name_filter = widgets.entry(card, placeholder="Contains...", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.particulars_filter = widgets.entry(card, placeholder="Contains...", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.from_entry = widgets.entry(card, placeholder="DD/MM/YYYY", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.to_entry = widgets.entry(card, placeholder="DD/MM/YYYY", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.debit_from = widgets.entry(card, placeholder="0.00", justify="right", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.debit_to = widgets.entry(card, placeholder="0.00", justify="right", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.credit_from = widgets.entry(card, placeholder="0.00", justify="right", height=FIELD_HEIGHT, font_size=FIELD_FONT)
        self.credit_to = widgets.entry(card, placeholder="0.00", justify="right", height=FIELD_HEIGHT, font_size=FIELD_FONT)

        tints = {"Debit From": theme.DEBIT, "Debit To": theme.DEBIT, "Credit From": theme.CREDIT, "Credit To": theme.CREDIT}
        if self.locked_head:
            layout = [
                (3, 0, (("Date Range", self.range_menu), ("Transactions", self.sub_menu))),
                (5, 0, (("From", self.from_entry), ("To", self.to_entry))),  # shown only for Custom Range
                (7, 0, (("Debit From", self.debit_from), ("Debit To", self.debit_to), ("Credit From", self.credit_from), ("Credit To", self.credit_to))),
            ]
        else:
            layout = [
                (1, 3, (("Main Entry", self.head_menu),)),
                (3, 4, (("Date Range", self.range_menu), ("Transactions", self.sub_menu), ("Name", self.name_filter), ("Particulars", self.particulars_filter))),
                (5, 0, (("From", self.from_entry), ("To", self.to_entry))),  # shown only for Custom Range
                (7, 0, (("Debit From", self.debit_from), ("Debit To", self.debit_to), ("Credit From", self.credit_from), ("Credit To", self.credit_to))),
            ]
        self.custom_widgets = []
        for grid_row, first_column, group in layout:
            for offset, (text, widget) in enumerate(group):
                column = first_column if len(group) == 1 else offset
                span = 2 if self.locked_head and text == "Transactions" else 1  # the long names need the room
                label = widgets.field_label(card, text, color=tints.get(text, theme.TEXT), tip=FILTER_TIPS[text], size=theme.FONT_SIZE_LABEL)
                if text == "Main Entry":
                    label.grid(row=grid_row, column=column, sticky="w", padx=(8, 20), pady=(8, 0))
                    widget.grid(row=grid_row + 1, column=column, sticky="ew", padx=(8, 20), pady=(3, 0))
                else:
                    label.grid(row=grid_row, column=column, columnspan=span, sticky="w", padx=(20, 20 if column == 3 else 8), pady=(8, 0))
                    widget.grid(row=grid_row + 1, column=column, columnspan=span, sticky="ew", padx=(20, 20 if column == 3 else 8), pady=(3, 0))
                if text in ("From", "To"):
                    self.custom_widgets += [label, widget]

        self.filter_error = widgets.error_label(card)
        self.filter_error.grid(row=9, column=0, columnspan=4, sticky="ew", padx=20, pady=(2, 8))
        self._on_range_change(ALL_RANGES[0][0])
        return card

    def _menu(self, parent, values, command) -> widgets.SelectBox:
        return widgets.SelectBox(parent, values=values, command=command, width=220, height=FIELD_HEIGHT, font_size=FIELD_FONT)

    def _build_toolbar(self) -> None:
        """Export and import, above the table. Export saves the rows the filters currently show."""
        bar = ctk.CTkFrame(self.table_card, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 0))
        widgets.label(bar, "Transactions", size=theme.FONT_SIZE_CARD_TITLE).pack(side="left")
        if self.locked_head:
            return
        widgets.secondary_button(bar, "Import CSV", self._import_csv, width=130).pack(side="right")
        widgets.secondary_button(bar, "Export PDF", lambda: self._export("pdf"), width=130).pack(side="right", padx=(0, 10))
        widgets.secondary_button(bar, "Export CSV", lambda: self._export("csv"), width=130).pack(side="right", padx=(0, 10))

    def _build_pager(self) -> None:
        bar = ctk.CTkFrame(self.table_card, fg_color=theme.SURFACE_SOFT, corner_radius=14)
        bar.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        bar.grid_columnconfigure(0, weight=1)
        self.pager_info = widgets.label(bar, "", size=theme.FONT_SIZE_BODY, color=theme.TEXT_MUTED)
        self.pager_info.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        controls = ctk.CTkFrame(bar, fg_color="transparent")
        controls.grid(row=0, column=1, sticky="e", padx=16, pady=10)
        widgets.label(controls, "Rows per page", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED).pack(side="left", padx=(0, 6))
        self.size_menu = self._menu(controls, [str(size) for size in config.PAGE_SIZE_CHOICES], self._on_page_size)
        self.size_menu.set(str(self.page_size))
        self.size_menu.configure(width=80)
        self.size_menu.pack(side="left", padx=(0, 12))
        self.prev_button = widgets.secondary_button(controls, "‹ Prev", lambda: self._go_page(self.page - 1), width=80)
        self.prev_button.pack(side="left", padx=4)
        self.page_numbers = ctk.CTkFrame(controls, fg_color="transparent")
        self.page_numbers.pack(side="left", padx=4)
        self.next_button = widgets.secondary_button(controls, "Next ›", lambda: self._go_page(self.page + 1), width=80)
        self.next_button.pack(side="left", padx=4)
        self.pager = bar

    # ----- data and rendering -----

    def refresh(self) -> None:
        """Reload the rows and the choices each time the page opens (FR-18, FR-11)."""
        self.all_rows = self.entries.all_entries()
        if not self.locked_head:
            self._refresh_head_menu()
        self._refresh_sub_head_menu()
        self._render_table()

    def _refresh_head_menu(self) -> None:
        names = [item.name for item in self.main_entries.items()]
        self.head_menu.configure(values=[ALL_MAIN_ENTRIES] + names)
        if self.head_menu.get() not in names:
            self.head_menu.set(ALL_MAIN_ENTRIES)

    def _head_choice_id(self) -> str:
        """The id of the Main Entry chosen in the filter (or the one this table is locked to), or ALL."""
        if self.locked_head:
            return self.locked_head
        choice = self.head_menu.get()
        return "ALL" if choice == ALL_MAIN_ENTRIES else self.main_entries.id_for_label(choice)

    def _refresh_sub_head_menu(self) -> None:
        names = []
        chosen = self._head_choice_id()
        heads = [item.id for item in self.main_entries.items()] if chosen == "ALL" else [chosen]
        for head in heads:
            for item in self.subheads.items(head):
                if item.name not in names:
                    names.append(item.name)
        self.sub_menu.configure(values=[ALL_SUB_HEADS] + names)
        current = self.sub_menu.get()
        self.sub_menu.set(current if current in names else ALL_SUB_HEADS)

    def _apply_filters(self) -> None:
        self.filters = self._read_filters()
        resolved, error = rs.resolve_filters(self.filters, date.today())
        self.filter_error.configure(text=error)
        if resolved is None:
            return
        self.resolved = resolved
        self.page = 1
        self.editing_key = None
        self._render_table()

    def _read_filters(self) -> rs.Filters:
        range_value = dict(ALL_RANGES).get(self.range_menu.get(), "all")
        sub = self.sub_menu.get()
        return rs.Filters(
            date_range=range_value,
            from_text=self.from_entry.get(),
            to_text=self.to_entry.get(),
            main_head=self._head_choice_id(),
            sub_head="ALL" if sub == ALL_SUB_HEADS else sub,
            name_text=self.name_filter.get(),
            particulars_text=self.particulars_filter.get(),
            debit_min=self.debit_from.get(),
            debit_max=self.debit_to.get(),
            credit_min=self.credit_from.get(),
            credit_max=self.credit_to.get(),
            search_text=self.search.get(),
        )

    def _clear_filters(self) -> None:
        self.search.delete(0, "end")
        self.range_menu.set(ALL_RANGES[0][0])
        self.from_entry.delete(0, "end")
        self.to_entry.delete(0, "end")
        self.head_menu.set(ALL_MAIN_ENTRIES)
        self.sub_menu.set(ALL_SUB_HEADS)
        for widget in (self.name_filter, self.particulars_filter, self.debit_from, self.debit_to, self.credit_from, self.credit_to):
            widget.delete(0, "end")
        self._on_range_change(ALL_RANGES[0][0])
        self.filter_error.configure(text="")
        self.filters = rs.Filters(main_head=self._head_choice_id())
        self.resolved = rs.ResolvedFilters(main_head=self._head_choice_id())
        self.page = 1
        self.editing_key = None
        self._refresh_sub_head_menu()
        self._render_table()

    def set_main_head(self, main_head: str) -> None:
        """Lock the table to another Main Entry: the filters start again and the next refresh() loads its rows."""
        if main_head == self.locked_head:
            return
        self.locked_head = main_head
        self.edit_widgets = {}
        self._clear_filters()

    def _on_range_change(self, choice: str) -> None:
        custom = choice == "Custom Range"
        for widget in self.custom_widgets:
            widget.grid() if custom else widget.grid_remove()

    def _on_head_change(self, _choice: str) -> None:
        self.sub_menu.set(ALL_SUB_HEADS)
        self._refresh_sub_head_menu()

    def _on_page_size(self, choice: str) -> None:
        self.page_size = int(choice)
        self.page = 1
        self.editing_key = None
        self._render_table()

    def _go_page(self, page: int) -> None:
        self.page = page
        self.editing_key = None
        self._render_table()

    def _visible_rows(self) -> list[Entry]:
        return rs.sort_newest_first(rs.filter_entries(self.all_rows, self.resolved))

    def _render_table(self) -> None:
        rows = self._visible_rows()
        page_rows, self.page = rs.page_slice(rows, self.page, self.page_size)
        for child in self.rows.winfo_children():
            child.destroy()
        self.edit_widgets = {}
        for column, weight in enumerate(COLUMN_WEIGHTS):
            hidden = self.locked_head and column == HEAD_COLUMN
            self.rows.grid_columnconfigure(column, weight=0 if hidden else weight, minsize=0 if hidden else COLUMN_MIN_WIDTHS[column])
        # The header and the total sit on tinted bars drawn behind their labels, in the same grid as the rows,
        # so every column lines up.
        for column in range(COLUMN_COUNT):
            if self.locked_head and column == HEAD_COLUMN:
                continue
            # Small muted capitals over the columns, with a hairline under them.
            widgets.EllipsisLabel(self.rows, HEADERS[column].upper(), size=theme.FONT_SIZE_LABEL - 1, color=theme.TEXT_MUTED, anchor="e" if column in AMOUNT_COLUMNS else "w").grid(row=0, column=column, sticky="ew", padx=CELL_PADX, pady=(2, 8))
        tk.Frame(self.rows, bg=LINE_COLOUR, height=1, bd=0, highlightthickness=0).grid(row=0, column=0, columnspan=COLUMN_COUNT, sticky="sew")

        if not rows:
            widgets.label(self.rows, "No entries match these filters.", color=theme.TEXT_MUTED).grid(row=1, column=0, columnspan=COLUMN_COUNT, pady=28)
        for index, entry in enumerate(page_rows, start=1):
            # Data rows sit on the odd grid rows; the even rows hold the line under each row.
            # Each row sits on its own rounded card, drawn first so the cells stack on top of it.
            ctk.CTkFrame(self.rows, fg_color=theme.SURFACE_SOFT, corner_radius=12, height=1).grid(row=2 * index - 1, column=0, columnspan=COLUMN_COUNT, sticky="nsew")
            if entry.key == self.editing_key:
                self._edit_row(2 * index - 1, entry)
            else:
                self._view_row(2 * index - 1, entry)
            tk.Frame(self.rows, bg=theme.BG_CARD, height=4, bd=0, highlightthickness=0).grid(row=2 * index, column=0, columnspan=COLUMN_COUNT, sticky="ew")

        debit, credit = rs.totals(rows)
        total_row = 2 * len(page_rows) + 1
        ctk.CTkFrame(self.rows, fg_color=theme.PRIMARY_LIGHT, corner_radius=14, height=1).grid(row=total_row, column=0, columnspan=COLUMN_COUNT, sticky="nsew")
        widgets.label(self.rows, f"Total (all {len(rows)} matching rows)", fg_color=theme.PRIMARY_LIGHT, width=0).grid(row=total_row, column=0, columnspan=5, sticky="w", padx=CELL_PADX, pady=(10, 10))
        widgets.label(self.rows, money.format_amount(debit), color=theme.DEBIT, fg_color=theme.PRIMARY_LIGHT, width=0).grid(row=total_row, column=5, sticky="e", padx=CELL_PADX, pady=(10, 10))
        widgets.label(self.rows, money.format_amount(credit), color=theme.CREDIT, fg_color=theme.PRIMARY_LIGHT, width=0).grid(row=total_row, column=6, sticky="e", padx=CELL_PADX, pady=(10, 10))
        self._render_pager(len(rows), page_rows)

    def _link(self, parent, text: str, command, colour: str = theme.TEXT) -> ctk.CTkButton:
        return ctk.CTkButton(parent, text=text, command=command, width=40, height=24, corner_radius=12, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, text_color=colour, font=widgets.text_font(theme.FONT_SIZE_LABEL + 1, bold=False))

    def _view_row(self, row: int, entry: Entry) -> None:
        values = (
            dates.format_date_slash(entry.entry_date),
            self.main_entries.label(entry.main_head),
            entry.sub_head,
            entry.name,
            entry.particulars,
            money.format_amount(entry.debit),
            money.format_amount(entry.credit),
            entry.owner,
        )
        for column, text in enumerate(values):
            if self.locked_head and column == HEAD_COLUMN:
                continue
            colour = theme.DEBIT if column == 5 else theme.CREDIT if column == 6 else theme.TEXT
            widgets.EllipsisLabel(self.rows, text, size=theme.FONT_SIZE_LABEL + 1, bold=False, color=colour, fg_color=theme.SURFACE_SOFT, anchor="e" if column in AMOUNT_COLUMNS else "w").grid(row=row, column=column, sticky="ew", padx=CELL_PADX, pady=4)
        if not self.entries.is_mine(entry):  # imported from another user: read-only
            return
        actions = ctk.CTkFrame(self.rows, fg_color=theme.SURFACE_SOFT)
        actions.grid(row=row, column=ACTIONS_COLUMN, sticky="w", padx=8)
        self._link(actions, "Edit", lambda e=entry: self._start_edit(e)).pack(side="left")
        widgets.label(actions, "·", color=theme.TEXT_MUTED).pack(side="left")
        self._link(actions, "Delete", lambda e=entry: self._open_delete(e)).pack(side="left")

    def _edit_row(self, row: int, entry: Entry) -> None:
        widgets_map = {}

        def new_cell(column: int) -> ctk.CTkFrame:
            cell = ctk.CTkFrame(self.rows, fg_color=theme.SURFACE_SOFT)
            cell.grid(row=row, column=column, sticky="ew", padx=4, pady=4)
            return cell

        date_cell = new_cell(0)
        date_entry = widgets.entry(date_cell, height=32)
        date_entry.insert(0, dates.format_date_slash(entry.entry_date))
        date_entry.pack(fill="x")
        date_error = widgets.error_label(date_cell)
        date_error.pack(fill="x")
        widgets_map["date"] = (date_entry, date_error)

        if not self.locked_head:
            head_cell = new_cell(1)
            head_menu = self._menu(head_cell, self._edit_head_values(entry.main_head), self._edit_head_changed)
            head_menu.set(self.main_entries.label(entry.main_head))
            head_menu.pack(fill="x")
            head_error = widgets.error_label(head_cell)
            head_error.pack(fill="x")
            widgets_map["main_head"] = (head_menu, head_error)

        sub_cell = new_cell(2)
        sub_menu = self._menu(sub_cell, self._edit_sub_values(entry.main_head, entry.sub_head), lambda _choice: None)
        sub_menu.set(entry.sub_head)
        sub_menu.pack(fill="x")
        sub_error = widgets.error_label(sub_cell)
        sub_error.pack(fill="x")
        widgets_map["sub_head"] = (sub_menu, sub_error)

        for column, key, text in ((3, "name", entry.name), (4, "particulars", entry.particulars), (5, "debit", money.format_amount(entry.debit)), (6, "credit", money.format_amount(entry.credit))):
            cell = new_cell(column)
            text_entry = widgets.entry(cell, height=32, justify="right" if key in ("debit", "credit") else "left")
            text_entry.insert(0, text)
            text_entry.pack(fill="x")
            error = widgets.error_label(cell)
            error.pack(fill="x")
            widgets_map[key] = (text_entry, error)

        actions = ctk.CTkFrame(self.rows, fg_color=theme.SURFACE_SOFT)
        actions.grid(row=row, column=ACTIONS_COLUMN, sticky="w", padx=8)
        ctk.CTkButton(actions, text=theme.ICON_CONFIRM, font=widgets.icon_font(12), width=32, height=28, fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER, text_color=theme.ON_PRIMARY, command=lambda e=entry: self._save_edit(e)).pack(side="left")
        widgets.label(actions, "Esc cancels", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED).pack(side="left", padx=(6, 0))
        self.edit_widgets = widgets_map
        self.bind("<Escape>", lambda _event: self._cancel_edit())
        for widget, _error in widgets_map.values():
            widget.bind("<Escape>", lambda _event: self._cancel_edit())

    def _edit_head_values(self, current: str) -> list[str]:
        return [item.name for item in self.main_entries.items() if item.active or item.id == current]

    def _edit_sub_values(self, main_head: str, current: str) -> list[str]:
        names = [item.name for item in self.subheads.items(main_head) if item.active or item.name == current]
        return [SELECT] + names

    def _edit_head_changed(self, choice: str) -> None:
        code = self.main_entries.id_for_label(choice)
        sub_menu = self.edit_widgets["sub_head"][0]
        sub_menu.configure(values=self._edit_sub_values(code, ""))
        sub_menu.set(SELECT)

    def _start_edit(self, entry: Entry) -> None:
        self.editing_key = entry.key
        self._render_table()

    def _cancel_edit(self) -> None:
        if self.editing_key is None:
            return
        self.editing_key = None
        self._render_table()

    def _save_edit(self, original: Entry) -> None:
        widgets_map = self.edit_widgets
        head_code = self.locked_head or self.main_entries.id_for_label(widgets_map["main_head"][0].get())
        sub_choice = widgets_map["sub_head"][0].get()
        check = check_entry(
            sub_choice != SELECT,
            widgets_map["date"][0].get(),
            widgets_map["name"][0].get(),
            widgets_map["particulars"][0].get(),
            widgets_map["debit"][0].get(),
            widgets_map["credit"][0].get(),
        )
        # Each message goes under its own field (Rule 25).
        for key in ("date", "name", "particulars", "debit", "credit"):
            widgets_map[key][1].configure(text=check.errors.get(key, ""))
        widgets_map["sub_head"][1].configure(text="Select a Sub-Head." if sub_choice == SELECT else "")
        if check.both_zero:
            widgets_map["credit"][1].configure(text="Debit or Credit must be above 0.00.")
        if not check.valid or check.values is None or sub_choice == SELECT:
            return

        values = check.values
        updated = Entry(
            id=original.id,
            main_head=head_code,
            sub_head=sub_choice,
            entry_date=values["date"],
            name=values["name"],
            particulars=values["particulars"],
            debit=values["debit"],
            credit=values["credit"],
            created_at=original.created_at,
            owner=original.owner,
        )
        result = self.entries.update_entry(updated, original.entry_date)
        if not result.ok:
            widgets_map["date"][1].configure(text=result.message)
            return
        self.editing_key = None
        self.refresh()

    # ----- export and import -----

    def _export(self, kind: str) -> None:
        """Save the rows the filters currently show (all rows when no filter is set) as CSV or PDF."""
        self.filter_error.configure(text="")
        rows = rs.sort_oldest_first(rs.filter_entries(self.all_rows, self.resolved))
        if not rows:
            self.filter_error.configure(text="There are no entries to export.")
            return
        owner = self.entries.current_owner()
        chosen = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            title=f"Export {kind.upper()}",
            defaultextension=f".{kind}",
            filetypes=[(f"{kind.upper()} file", f"*.{kind}")],
            initialfile=f"{config.APP_NAME.replace(' ', '')}_{owner or 'entries'}_{dates.format_date(date.today())}.{kind}",
        )
        if not chosen:
            return
        try:
            if kind == "csv":
                exchange_service.export_csv(Path(chosen), rows, self.main_entries, owner)
            else:
                pdf_report.export_pdf(Path(chosen), rows, self.main_entries, owner)
        except OSError:
            self.filter_error.configure(text="The file could not be saved. If it is open in another program, close it and try again.")
            return
        self.notify(f"Exported {len(rows)} entries.")

    def _import_csv(self) -> None:
        """Add the rows of a CSV exported by another user. They are kept apart from the user's own rows and cannot be edited."""
        self.filter_error.configure(text="")
        chosen = filedialog.askopenfilename(parent=self.winfo_toplevel(), title="Import CSV", filetypes=[("CSV file", "*.csv")])
        if not chosen:
            return
        parsed = exchange_service.read_csv(Path(chosen), self.main_entries)
        if parsed.problem:
            self.filter_error.configure(text=parsed.problem)
            return
        result, added, skipped = self.entries.import_entries(parsed.entries)
        if not result.ok:
            self.filter_error.configure(text=result.message)
            return
        self.refresh()
        message = f"Imported {added} new entries."
        self.notify(message + (f" {skipped} were already there." if skipped else ""))

    # ----- delete (PRD FR-23) -----

    def _open_delete(self, entry: Entry) -> None:
        self.delete_target = entry
        popup = ctk.CTkToplevel(self, fg_color=theme.BG_CARD)
        popup.title("Delete Row")
        widgets.set_window_icon(popup)
        popup.geometry("420x200")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)
        widgets.label(body, "Delete Row", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w", pady=(0, 12))
        widgets.label(body, "Are you sure you want to delete this row?", wraplength=360, justify="left").pack(anchor="w")
        problem = widgets.error_label(body)
        problem.pack(fill="x", pady=(6, 0))
        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(20, 0))
        widgets.cancel_button(buttons, "Cancel", popup.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        def confirm() -> None:
            result = self.entries.delete_entry(entry.id, entry.entry_date)
            if not result.ok:
                problem.configure(text=result.message)
                return
            popup.destroy()
            self.refresh()

        widgets.danger_button(buttons, "Delete", confirm).pack(side="left", expand=True, fill="x", padx=(6, 0))
        popup.bind("<Escape>", lambda _event: popup.destroy())

    # ----- pager (FR-18a) -----

    def _render_pager(self, total: int, page_rows: list[Entry]) -> None:
        if total == 0:
            self.pager_info.configure(text="")
            self.pager.grid_remove()
            return
        self.pager.grid()
        first = (self.page - 1) * self.page_size + 1
        last = first + len(page_rows) - 1
        self.pager_info.configure(text=f"Showing {first} to {last} of {total} entries")
        pages = max(1, -(-total // self.page_size))
        self.prev_button.configure(state="disabled" if self.page <= 1 else "normal")
        self.next_button.configure(state="disabled" if self.page >= pages else "normal")
        for child in self.page_numbers.winfo_children():
            child.destroy()
        numbers = [p for p in range(1, pages + 1) if p == 1 or p == pages or abs(p - self.page) <= 2]
        last_number = 0
        for number in numbers:
            if number - last_number > 1:
                widgets.label(self.page_numbers, "…", color=theme.TEXT_MUTED).pack(side="left", padx=2)
            active = number == self.page
            ctk.CTkButton(
                self.page_numbers, text=str(number), width=32, height=32, corner_radius=16,
                fg_color=theme.HIGHLIGHT if active else theme.BG_CARD,
                hover_color=theme.HIGHLIGHT_HOVER if active else theme.PRIMARY_LIGHT,
                border_color=theme.INPUT_BORDER, border_width=0 if active else 1,
                text_color=theme.ON_HIGHLIGHT if active else theme.TEXT,
                font=widgets.text_font(theme.FONT_SIZE_BODY),
                command=lambda n=number: self._go_page(n),
            ).pack(side="left", padx=2)
            last_number = number
