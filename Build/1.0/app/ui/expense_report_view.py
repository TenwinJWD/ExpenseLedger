"""Expense Report page (Design.md Section 6; PRD FR-18 to FR-23, FR-18a, FR-19a, FR-21a to FR-21c).

Order on the page: the filter card, the table with pagination, then Monthly Summary and
Yearly Summary. The summary cards ignore the filters.
"""

import calendar
from datetime import date

import customtkinter as ctk

from app.core import config, dates, models, money, theme
from app.core.models import Entry
from app.core.validation import check_entry
from app.services import report_service as rs
from app.services.entry_service import EntryService
from app.services.subhead_service import SubheadService
from app.ui import widgets

ALL_RANGES = (("All Dates", "all"), ("This Month", "this-month"), ("Last Month", "last-month"),
              ("This Year", "this-year"), ("Custom Range", "custom"))
ALL_MAIN_HEADS = "All Main Heads"
ALL_SUB_HEADS = "All Sub-Heads"
SELECT = "-Select-"
COLUMN_WEIGHTS = (2, 3, 3, 3, 3, 2, 2, 2)
HEADERS = ("Date", "Main Head", "Sub-Head", "Name", "Particulars", "Debit", "Credit", "Actions")

FILTER_TIPS = {
    "Search": "Finds rows where the name, particulars or an amount contains this text.",
    "Date Range": "Shows only entries inside this period. Custom Range lets you type From and To dates.",
    "From": "First day to include, as DD/MM/YYYY.",
    "To": "Last day to include, as DD/MM/YYYY.",
    "Main Head": "Shows only entries under this Main Head.",
    "Sub-Head": "Shows only entries under this Sub-Head.",
    "Name": "Shows only rows whose name contains this text.",
    "Particulars": "Shows only rows whose particulars contain this text.",
    "Debit From": "Smallest debit amount to include.",
    "Debit To": "Largest debit amount to include.",
    "Credit From": "Smallest credit amount to include.",
    "Credit To": "Largest credit amount to include.",
}


class ExpenseReportView(ctk.CTkFrame):
    """The whole report page. refresh() reloads the rows each time the page opens (FR-18)."""

    def __init__(self, master, subheads: SubheadService, entries: EntryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.subheads = subheads
        self.entries = entries
        self.all_rows: list[Entry] = []
        self.filters = rs.Filters()
        self.resolved = rs.ResolvedFilters()
        self.page = 1
        self.page_size = config.DEFAULT_PAGE_SIZE
        self.editing_id: str | None = None
        self.edit_widgets: dict = {}
        self.delete_target: Entry | None = None

        self.grid_columnconfigure(0, weight=1)
        widgets.label(self, "Expense Report", size=theme.FONT_SIZE_PAGE_TITLE).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 0))
        widgets.label(self, "All submitted entries, oldest first", color=theme.TEXT_MUTED).grid(row=1, column=0, sticky="w", padx=24, pady=(2, 14))

        self.month_summary = self._summary_card(4, "Monthly Summary", "Values are based on the selected month. Independent of the filters.", "month")
        self.year_summary = self._summary_card(5, "Yearly Summary", "Values are based on the selected year. Independent of the filters.", "year")

        self.filter_card = self._build_filters()
        self.filter_card.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 14))

        self.table_card = widgets.card(self)
        self.table_card.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 14))
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)
        self.rows = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows.grid(row=1, column=0, sticky="nsew", padx=16, pady=(16, 0))
        self._build_pager()
        self.grid_rowconfigure(3, weight=1)

    # ----- layout -----

    def _summary_card(self, row: int, title: str, description: str, kind: str) -> ctk.CTkFrame:
        card = widgets.card(self)
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 14))
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(16, 10))
        titles = ctk.CTkFrame(head, fg_color="transparent")
        titles.pack(side="left", fill="x", expand=True)
        widgets.label(titles, title, size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w")
        widgets.label(titles, description, size=theme.FONT_SIZE_BODY, color=theme.TEXT_MUTED).pack(anchor="w")
        menu = widgets.SelectBox(head, values=[""], command=lambda _choice: self._render_summaries(), width=180)
        menu.pack(side="right")
        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=(0, 18))
        for column in range(3):
            stats.grid_columnconfigure(column, weight=1)
        cells = []
        for index in range(6):
            cell = ctk.CTkFrame(stats, fg_color=theme.PRIMARY_LIGHT, border_color=theme.BORDER_SOFT, border_width=1, corner_radius=12)
            cell.grid(row=index // 3, column=index % 3, sticky="nsew", padx=6, pady=6)
            label = widgets.label(cell, "", size=theme.FONT_SIZE_CARD_TITLE)
            label.pack(anchor="w", padx=14, pady=(12, 0))
            value = widgets.label(cell, "", size=theme.FONT_SIZE_VALUE)
            value.pack(anchor="w", padx=14, pady=(4, 0))
            sub = widgets.label(cell, "", size=theme.FONT_SIZE_BODY, color=theme.TEXT_MUTED)
            sub.pack(anchor="w", padx=14, pady=(2, 12))
            cells.append((label, value, sub))
        setattr(self, f"{kind}_menu", menu)
        setattr(self, f"{kind}_cells", cells)
        return card

    def _build_filters(self) -> ctk.CTkFrame:
        card = widgets.card(self)
        card.grid_columnconfigure((0, 1, 2, 3), weight=1)
        widgets.field_label(card, "Search", tip=FILTER_TIPS["Search"]).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(18, 6))
        self.search = widgets.entry(card, placeholder="Search by name, particulars, or amount")
        self.search.grid(row=1, column=0, columnspan=4, sticky="ew", padx=20)
        self.search.bind("<Return>", lambda _event: self._apply_filters())

        # Row 2 holds the labels and row 3 the widgets. From and To show only for Custom Range.
        widgets.field_label(card, "Date Range", tip=FILTER_TIPS["Date Range"]).grid(row=2, column=0, sticky="sw", padx=(20, 8), pady=(14, 0))
        self.from_label = widgets.field_label(card, "From", tip=FILTER_TIPS["From"])
        self.from_label.grid(row=2, column=1, sticky="sw", padx=(20, 8), pady=(14, 0))
        self.to_label = widgets.field_label(card, "To", tip=FILTER_TIPS["To"])
        self.to_label.grid(row=2, column=2, sticky="sw", padx=(20, 8), pady=(14, 0))
        self.range_menu = self._menu(card, [label for label, _value in ALL_RANGES], self._on_range_change)
        self.range_menu.grid(row=3, column=0, sticky="ew", padx=(20, 8), pady=(6, 0))
        self.from_entry = widgets.entry(card, placeholder="DD/MM/YYYY")
        self.from_entry.grid(row=3, column=1, sticky="ew", padx=(20, 8), pady=(6, 0))
        self.to_entry = widgets.entry(card, placeholder="DD/MM/YYYY")
        self.to_entry.grid(row=3, column=2, sticky="ew", padx=(20, 8), pady=(6, 0))

        self.head_menu = self._menu(card, [ALL_MAIN_HEADS] + list(models.MAIN_HEADS.values()), self._on_head_change)
        self.sub_menu = self._menu(card, [ALL_SUB_HEADS], lambda _choice: None)
        self.name_filter = widgets.entry(card, placeholder="Contains...")
        self.particulars_filter = widgets.entry(card, placeholder="Contains...")
        self.debit_from = widgets.entry(card, placeholder="0.00", justify="right")
        self.debit_to = widgets.entry(card, placeholder="0.00", justify="right")
        self.credit_from = widgets.entry(card, placeholder="0.00", justify="right")
        self.credit_to = widgets.entry(card, placeholder="0.00", justify="right")

        layout = [
            (("Main Head", self.head_menu), ("Sub-Head", self.sub_menu), ("Name", self.name_filter), ("Particulars", self.particulars_filter)),
            (("Debit From", self.debit_from), ("Debit To", self.debit_to), ("Credit From", self.credit_from), ("Credit To", self.credit_to)),
        ]
        grid_row = 4
        tints = {"Debit From": theme.DEBIT, "Debit To": theme.DEBIT, "Credit From": theme.CREDIT, "Credit To": theme.CREDIT}
        for group in layout:
            for column, (text, widget) in enumerate(group):
                widgets.field_label(card, text, color=tints.get(text, theme.TEXT), tip=FILTER_TIPS[text]).grid(row=grid_row, column=column, sticky="sw", padx=(20, 8), pady=(12, 0))
                widget.grid(row=grid_row + 1, column=column, sticky="ew", padx=(20, 8), pady=(6, 0))
            grid_row += 2

        self.filter_error = widgets.error_label(card)
        self.filter_error.grid(row=grid_row, column=0, columnspan=4, sticky="ew", padx=20, pady=(12, 0))
        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=grid_row + 1, column=0, columnspan=4, sticky="e", padx=20, pady=(12, 20))
        widgets.secondary_button(buttons, "Clear Filters", self._clear_filters, width=150).pack(side="left", padx=(0, 10))
        widgets.primary_button(buttons, "Filter Report", self._apply_filters, width=160).pack(side="left")
        self._on_range_change(ALL_RANGES[0][0])
        return card

    def _menu(self, parent, values, command) -> widgets.SelectBox:
        return widgets.SelectBox(parent, values=values, command=command, width=220)

    def _build_pager(self) -> None:
        bar = ctk.CTkFrame(self.table_card, fg_color=theme.SURFACE_TINT, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew", padx=0, pady=(12, 0))
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
        """Reload the rows and the sub-head choices each time the page opens (FR-18, FR-11)."""
        self.all_rows = self.entries.all_entries()
        self._refresh_sub_head_menu()
        self._render_summaries()
        self._render_table()

    def _refresh_sub_head_menu(self) -> None:
        names = []
        heads = list(models.MAIN_HEADS) if self.filters.main_head == "ALL" else [self.filters.main_head]
        for head in heads:
            for item in self.subheads.items(head):
                if item.name not in names:
                    names.append(item.name)
        self.sub_menu.configure(values=[ALL_SUB_HEADS] + names)
        current = self.sub_menu.get()
        self.sub_menu.set(current if current in names else ALL_SUB_HEADS)

    def _render_summaries(self) -> None:
        today = date.today()
        months = sorted({(e.entry_date.year, e.entry_date.month) for e in self.all_rows}, reverse=True)
        month_labels = [f"{calendar.month_abbr[m]} {y}" for y, m in months] or ["No entries"]
        self.month_menu.configure(values=month_labels)
        if self.month_menu.get() not in month_labels:
            self.month_menu.set(month_labels[0])
        years = sorted({e.entry_date.year for e in self.all_rows}, reverse=True)
        year_labels = [str(y) for y in years] or [str(today.year)]
        self.year_menu.configure(values=year_labels)
        if self.year_menu.get() not in year_labels:
            self.year_menu.set(year_labels[0])

        if months:
            year, month = months[month_labels.index(self.month_menu.get())]
            month_rows = rs.entries_in_month(self.all_rows, year, month)
            self._fill_cards(self.month_cells, rs.summarize(month_rows))
        else:
            self._fill_cards(self.month_cells, rs.summarize([]))
        year_rows = rs.entries_in_year(self.all_rows, int(self.year_menu.get())) if self.all_rows else []
        self._fill_cards(self.year_cells, rs.summarize(year_rows))

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

    def _apply_filters(self) -> None:
        self.filters = self._read_filters()
        resolved, error = rs.resolve_filters(self.filters, date.today())
        self.filter_error.configure(text=error)
        if resolved is None:
            return
        self.resolved = resolved
        self.page = 1
        self.editing_id = None
        self._render_table()

    def _read_filters(self) -> rs.Filters:
        range_value = dict(ALL_RANGES).get(self.range_menu.get(), "all")
        head = self.head_menu.get()
        head_code = next((code for code, label in models.MAIN_HEADS.items() if label == head), "ALL")
        sub = self.sub_menu.get()
        return rs.Filters(
            date_range=range_value,
            from_text=self.from_entry.get(),
            to_text=self.to_entry.get(),
            main_head=head_code,
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
        self.head_menu.set(ALL_MAIN_HEADS)
        self.sub_menu.set(ALL_SUB_HEADS)
        for widget in (self.name_filter, self.particulars_filter, self.debit_from, self.debit_to, self.credit_from, self.credit_to):
            widget.delete(0, "end")
        self._on_range_change(ALL_RANGES[0][0])
        self.filter_error.configure(text="")
        self.filters = rs.Filters()
        self.resolved = rs.ResolvedFilters()
        self.page = 1
        self.editing_id = None
        self._refresh_sub_head_menu()
        self._render_table()

    def _on_range_change(self, choice: str) -> None:
        custom = choice == "Custom Range"
        for widget in (self.from_label, self.from_entry, self.to_label, self.to_entry):
            widget.grid() if custom else widget.grid_remove()

    def _on_head_change(self, choice: str) -> None:
        head = next((code for code, label in models.MAIN_HEADS.items() if label == choice), None)
        names = []
        for code in ([head] if head else list(models.MAIN_HEADS)):
            for item in self.subheads.items(code):
                if item.name not in names:
                    names.append(item.name)
        self.sub_menu.configure(values=[ALL_SUB_HEADS] + names)
        self.sub_menu.set(ALL_SUB_HEADS)

    def _on_page_size(self, choice: str) -> None:
        self.page_size = int(choice)
        self.page = 1
        self.editing_id = None
        self._render_table()

    def _go_page(self, page: int) -> None:
        self.page = page
        self.editing_id = None
        self._render_table()

    def _visible_rows(self) -> list[Entry]:
        return rs.sort_oldest_first(rs.filter_entries(self.all_rows, self.resolved))

    def _render_table(self) -> None:
        rows = self._visible_rows()
        page_rows, self.page = rs.page_slice(rows, self.page, self.page_size)
        for child in self.rows.winfo_children():
            child.destroy()
        self.edit_widgets = {}
        for column, weight in enumerate(COLUMN_WEIGHTS):
            self.rows.grid_columnconfigure(column, weight=weight)
            header_colour = theme.DEBIT if column == 5 else theme.CREDIT if column == 6 else theme.TEXT_MUTED
            widgets.label(self.rows, HEADERS[column].upper(), size=theme.FONT_SIZE_LABEL, color=header_colour).grid(row=0, column=column, sticky="w", padx=8, pady=(4, 8))

        if not rows:
            widgets.label(self.rows, "No entries match these filters.", color=theme.TEXT_MUTED).grid(row=1, column=0, columnspan=8, pady=28)
        for index, entry in enumerate(page_rows, start=1):
            if entry.id == self.editing_id:
                self._edit_row(index, entry)
            else:
                self._view_row(index, entry)

        debit, credit = rs.totals(rows)
        total_row = len(page_rows) + 1
        ctk.CTkFrame(self.rows, height=1, fg_color=theme.ROW_BORDER).grid(row=total_row, column=0, columnspan=8, sticky="ew", pady=(10, 0))
        widgets.label(self.rows, f"TOTAL (all {len(rows)} matching rows)").grid(row=total_row + 1, column=0, columnspan=5, sticky="w", padx=8, pady=8)
        widgets.label(self.rows, money.format_amount(debit), color=theme.DEBIT).grid(row=total_row + 1, column=5, sticky="e", padx=8)
        widgets.label(self.rows, money.format_amount(credit), color=theme.CREDIT).grid(row=total_row + 1, column=6, sticky="e", padx=8)
        self._render_pager(len(rows), page_rows)

    def _view_row(self, row: int, entry: Entry) -> None:
        values = (
            dates.format_date_slash(entry.entry_date),
            models.MAIN_HEADS[entry.main_head],
            entry.sub_head,
            entry.name,
            entry.particulars,
            money.format_amount(entry.debit),
            money.format_amount(entry.credit),
        )
        for column, text in enumerate(values):
            colour = theme.DEBIT if column == 5 else theme.CREDIT if column == 6 else theme.TEXT
            widgets.label(self.rows, text, color=colour).grid(row=row, column=column, sticky="w", padx=8, pady=6)
        actions = ctk.CTkFrame(self.rows, fg_color="transparent")
        actions.grid(row=row, column=7, sticky="w", padx=8)
        ctk.CTkButton(actions, text=theme.ICON_EDIT, font=widgets.icon_font(12), width=32, height=28, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, text_color=theme.TEXT, command=lambda e=entry: self._start_edit(e)).pack(side="left")
        ctk.CTkButton(actions, text=theme.ICON_DELETE, font=widgets.icon_font(12), width=32, height=28, fg_color="transparent", hover_color=theme.PRIMARY_LIGHT, text_color=theme.TEXT, command=lambda e=entry: self._open_delete(e)).pack(side="left", padx=(4, 0))

    def _edit_row(self, row: int, entry: Entry) -> None:
        widgets_map = {}

        def new_cell(column: int) -> ctk.CTkFrame:
            cell = ctk.CTkFrame(self.rows, fg_color="transparent")
            cell.grid(row=row, column=column, sticky="ew", padx=4, pady=4)
            return cell

        date_cell = new_cell(0)
        date_entry = widgets.entry(date_cell, height=32)
        date_entry.insert(0, dates.format_date_slash(entry.entry_date))
        date_entry.pack(fill="x")
        date_error = widgets.error_label(date_cell)
        date_error.pack(fill="x")
        widgets_map["date"] = (date_entry, date_error)

        head_cell = new_cell(1)
        head_menu = self._menu(head_cell, list(models.MAIN_HEADS.values()), self._edit_head_changed)
        head_menu.set(models.MAIN_HEADS[entry.main_head])
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

        actions = ctk.CTkFrame(self.rows, fg_color="transparent")
        actions.grid(row=row, column=7, sticky="w", padx=8)
        ctk.CTkButton(actions, text=theme.ICON_CONFIRM, font=widgets.icon_font(12), width=32, height=28, fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER, text_color="#FFFFFF", command=lambda e=entry: self._save_edit(e)).pack(side="left")
        widgets.label(actions, "Esc cancels", size=theme.FONT_SIZE_LABEL, color=theme.TEXT_MUTED).pack(side="left", padx=(6, 0))
        self.edit_widgets = widgets_map
        self.bind("<Escape>", lambda _event: self._cancel_edit())
        for widget, _error in widgets_map.values():
            widget.bind("<Escape>", lambda _event: self._cancel_edit())

    def _edit_sub_values(self, main_head: str, current: str) -> list[str]:
        names = [item.name for item in self.subheads.items(main_head) if item.active or item.name == current]
        return [SELECT] + names

    def _edit_head_changed(self, choice: str) -> None:
        code = next((c for c, label in models.MAIN_HEADS.items() if label == choice), None)
        if code is None:
            return
        sub_menu = self.edit_widgets["sub_head"][0]
        sub_menu.configure(values=self._edit_sub_values(code, ""))
        sub_menu.set(SELECT)

    def _start_edit(self, entry: Entry) -> None:
        self.editing_id = entry.id
        self._render_table()

    def _cancel_edit(self) -> None:
        if self.editing_id is None:
            return
        self.editing_id = None
        self._render_table()

    def _save_edit(self, original: Entry) -> None:
        widgets_map = self.edit_widgets
        head_label = widgets_map["main_head"][0].get()
        head_code = next((c for c, label in models.MAIN_HEADS.items() if label == head_label), original.main_head)
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
        )
        result = self.entries.update_entry(updated, original.entry_date)
        if not result.ok:
            widgets_map["date"][1].configure(text=result.message)
            return
        self.editing_id = None
        self.refresh()

    # ----- delete (PRD FR-23) -----

    def _open_delete(self, entry: Entry) -> None:
        self.delete_target = entry
        popup = ctk.CTkToplevel(self, fg_color=theme.BG_CARD)
        popup.title("Delete Row")
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
        widgets.secondary_button(buttons, "Cancel", popup.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

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
                self.page_numbers, text=str(number), width=32, height=32, corner_radius=8,
                fg_color=theme.PRIMARY if active else theme.BG_CARD,
                hover_color=theme.PRIMARY_HOVER if active else theme.SURFACE_TINT,
                border_color=theme.INPUT_BORDER, border_width=0 if active else 1,
                text_color="#FFFFFF" if active else theme.TEXT,
                font=widgets.text_font(theme.FONT_SIZE_BODY),
                command=lambda n=number: self._go_page(n),
            ).pack(side="left", padx=2)
            last_number = number
