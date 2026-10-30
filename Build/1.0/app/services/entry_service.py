"""Entry rules: save a validated entry to the daily Excel file, and read entries back (PRD FR-14, FR-15, FR-29).

The screens call save_entry(). The Excel store does the file work.
"""

from datetime import date, datetime
from decimal import Decimal

from app.core import dates
from app.core.models import Entry
from app.services.auth_service import Result
from app.storage.excel_store import ExcelFileLockedError, ExcelStore


class EntryService:
    """Saves and reads the entries."""

    def __init__(self, store: ExcelStore, subheads=None) -> None:
        self.store = store
        self.subheads = subheads  # when given, rows saved under an old sub-head name show the new name

    def save_entry(
        self,
        main_head: str,
        sub_head: str,
        entry_date: date,
        name: str,
        particulars: str,
        debit: Decimal,
        credit: Decimal,
    ) -> Result:
        """Save one entry to the file for its date. A locked file keeps the entry in the form."""
        entry = Entry(
            id=self.store.next_id(entry_date),
            main_head=main_head,
            sub_head=sub_head,
            entry_date=entry_date,
            name=name,
            particulars=particulars,
            debit=debit,
            credit=credit,
            created_at=datetime.now(),
        )
        try:
            self.store.append_entry(entry)
        except ExcelFileLockedError:
            return Result(False, _locked_message(entry_date))
        return Result(True)

    def all_entries(self) -> list[Entry]:
        entries = self.store.read_all_entries()
        if self.subheads is not None:
            renamed: dict[str, dict[str, str]] = {}
            for entry in entries:
                if entry.main_head not in renamed:
                    renamed[entry.main_head] = self.subheads.renamed_map(entry.main_head)
                entry.sub_head = renamed[entry.main_head].get(entry.sub_head, entry.sub_head)
        return entries

    def is_mine(self, entry: Entry) -> bool:
        """Only the logged-in user's own rows can be changed. Rows imported from other users are read-only."""
        return self.store.is_mine(entry)

    def current_owner(self) -> str:
        return self.store.current_owner()

    def import_entries(self, entries: list[Entry]) -> tuple[Result, int, int]:
        """Save rows from a CSV into the data folder. Returns (result, added, already_there)."""
        try:
            added, skipped = self.store.import_entries(entries)
        except ExcelFileLockedError:
            return Result(False, "An Excel file in the data folder is open. Close it in Excel and import again."), 0, 0
        return Result(True), added, skipped

    def update_entry(self, entry: Entry, old_date: date) -> Result:
        """Save changes made in the report's inline edit (PRD FR-22)."""
        try:
            self.store.update_entry(entry, old_date)
        except ExcelFileLockedError:
            return Result(False, _locked_message(entry.entry_date))
        return Result(True)

    def delete_entry(self, entry_id: str, entry_date: date) -> Result:
        """Delete one row, only after the user confirmed (PRD FR-23)."""
        try:
            self.store.delete_entry(entry_id, entry_date)
        except ExcelFileLockedError:
            return Result(False, _locked_message(entry_date))
        return Result(True)


def _locked_message(entry_date: date) -> str:
    return (
        f"The Excel file for {dates.format_date(entry_date)} is open. "
        "Close it in Excel and click Submit again. Your entry has not been lost."
    )
