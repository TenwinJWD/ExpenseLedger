"""Daily Excel ledger files (PRD FR-22 to FR-31; Architecture 5.1).

Each day with entries has its own file: <root>\\<YYYY>\\<MM-Mon>\\<DD-Mon-YYYY>.xlsx,
with one sheet named "Entries". Dates are stored as text (DD-Mon-YYYY), amounts as numbers.

Saves go to a temporary file first and then replace the real file (Rules 16). If Excel
has the file open, Windows refuses the replace, and ExcelFileLockedError is raised so the
form can keep the entry (PRD FR-29, Rules 15).
"""

import os
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import openpyxl

from app.core import dates
from app.core.models import MAIN_HEADS, Entry

SHEET_NAME = "Entries"
HEADERS = ("ID", "Main Head", "Sub Head", "Date", "Name", "Particulars", "Debit", "Credit", "Created At")
ID_PATTERN = re.compile(r"^E(\d{8})-(\d{3})$")
CENT = Decimal("0.01")


class ExcelFileLockedError(Exception):
    """The daily file is open in Excel, so it cannot be replaced. Nothing was lost."""


class ExcelStore:
    """Reads and writes the daily workbook files under one root folder."""

    def __init__(self, root: Path) -> None:
        self.root = root
        # Parsed rows per file, reused until the file changes on disk (Architecture 7).
        self._cache: dict[Path, tuple[int, list[Entry]]] = {}

    # ----- file locations -----

    def file_path_for(self, entry_date: date) -> Path:
        return self.root / dates.year_folder_name(entry_date) / dates.month_folder_name(entry_date) / f"{dates.format_date(entry_date)}.xlsx"

    # ----- writing -----

    def next_id(self, entry_date: date) -> str:
        """The next ID for the day: E<YYYYMMDD>-<NNN>, one more than the highest number used that day."""
        highest = 0
        path = self.file_path_for(entry_date)
        if path.exists():
            _workbook, sheet = self._open(path)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                match = ID_PATTERN.match(str(row[0] or ""))
                if match:
                    highest = max(highest, int(match.group(2)))
        return f"E{entry_date:%Y%m%d}-{highest + 1:03d}"

    def append_entry(self, entry: Entry) -> None:
        path = self.file_path_for(entry.entry_date)
        if path.exists():
            workbook, sheet = self._open(path)
        else:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = SHEET_NAME
            sheet.append(list(HEADERS))
        sheet.append(self._to_row(entry))
        self._save(workbook, path)

    def update_entry(self, entry: Entry, old_date: date) -> None:
        """Change a saved entry. If its date changed, the row moves to the file for the new date (FR-30)."""
        if old_date != entry.entry_date:
            self.delete_entry(entry.id, old_date)
            self.append_entry(entry)
            return
        path = self.file_path_for(old_date)
        workbook, sheet = self._open(path)
        row_number = self._find_row(sheet, entry.id)
        for column, value in enumerate(self._to_row(entry), start=1):
            sheet.cell(row=row_number, column=column, value=value)
        self._save(workbook, path)

    def delete_entry(self, entry_id: str, entry_date: date) -> None:
        path = self.file_path_for(entry_date)
        workbook, sheet = self._open(path)
        sheet.delete_rows(self._find_row(sheet, entry_id))
        self._save(workbook, path)

    # ----- reading -----

    def read_all_entries(self) -> list[Entry]:
        """Every entry in every daily file under the root, oldest first."""
        entries: list[Entry] = []
        if not self.root.exists():
            return entries
        for path in sorted(self.root.rglob("*.xlsx")):
            if ".tmp" in path.name:
                continue
            entries.extend(self._entries_of(path))
        entries.sort(key=lambda entry: (entry.entry_date, entry.id))
        return entries

    def _entries_of(self, path: Path) -> list[Entry]:
        """The rows of one file. Reuses the parsed rows while the file's modified time is unchanged."""
        stamp = path.stat().st_mtime_ns
        cached = self._cache.get(path)
        if cached and cached[0] == stamp:
            return list(cached[1])
        _workbook, sheet = self._open(path)
        rows = [self._from_row(row) for row in sheet.iter_rows(min_row=2, values_only=True) if row[0] is not None]
        self._cache[path] = (stamp, rows)
        return list(rows)

    # ----- helpers -----

    @staticmethod
    def _open(path: Path):
        workbook = openpyxl.load_workbook(path)
        sheet = workbook[SHEET_NAME] if SHEET_NAME in workbook.sheetnames else workbook.active
        return workbook, sheet

    @staticmethod
    def _find_row(sheet, entry_id: str) -> int:
        for row_number in range(2, sheet.max_row + 1):
            if sheet.cell(row=row_number, column=1).value == entry_id:
                return row_number
        raise KeyError(f"entry {entry_id} not found")

    @staticmethod
    def _save(workbook, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(path.stem + ".tmp.xlsx")
        workbook.save(temp_path)
        try:
            os.replace(temp_path, path)
        except PermissionError as error:
            temp_path.unlink(missing_ok=True)
            raise ExcelFileLockedError(str(error)) from error

    @staticmethod
    def _to_row(entry: Entry) -> list:
        created = f"{dates.format_date(entry.created_at.date())} {entry.created_at:%H:%M}"
        return [
            entry.id,
            MAIN_HEADS[entry.main_head],
            entry.sub_head,
            dates.format_date(entry.entry_date),
            entry.name,
            entry.particulars,
            float(entry.debit),
            float(entry.credit),
            created,
        ]

    @staticmethod
    def _from_row(row) -> Entry:
        main_head_label = str(row[1])
        main_head = next(code for code, label in MAIN_HEADS.items() if label == main_head_label)
        created_text = str(row[8])
        created_date_text, created_time_text = created_text.rsplit(" ", 1)
        created_date = dates.parse_date(created_date_text)
        hour, minute = (int(part) for part in created_time_text.split(":"))
        return Entry(
            id=str(row[0]),
            main_head=main_head,
            sub_head=str(row[2]),
            entry_date=dates.parse_date(str(row[3])),
            name=str(row[4]),
            particulars=str(row[5]),
            debit=Decimal(str(row[6])).quantize(CENT),
            credit=Decimal(str(row[7])).quantize(CENT),
            created_at=datetime(created_date.year, created_date.month, created_date.day, hour, minute),
        )
