"""Share entries between users: write the Transaction List to a CSV file, and read such a file back.

Each user keeps their own Excel files. To see another user's work, that user exports a CSV and the others import it.
Every row carries its owner, so the imported rows are saved in files named with that owner and never mixed with
the importer's own. Importing the same CSV twice adds nothing (rows are matched by owner and ID).
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.core import config, dates, money
from app.core.models import Entry
from app.storage.excel_store import ID_PATTERN, safe_owner

CSV_HEADERS = ("Owner", "ID", "Date", "Main Entry", "Sub-Head", "Name", "Particulars", "Debit", "Credit", "Created At")
_FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")


@dataclass
class CsvImport:
    """What reading a CSV gave: the rows, or the first problem found (rows is empty then)."""

    entries: list[Entry]
    problem: str = ""


def export_csv(path: Path, entries: list[Entry], main_entries, own_owner: str) -> None:
    """Write the entries to a CSV that Excel opens correctly (UTF-8 with a byte-order mark)."""
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)
        for entry in entries:
            writer.writerow([
                _guard(entry.owner or own_owner),
                entry.id,
                dates.format_date(entry.entry_date),
                _guard(main_entries.label(entry.main_head)),
                _guard(entry.sub_head),
                _guard(entry.name),
                _guard(entry.particulars),
                f"{entry.debit:.2f}",
                f"{entry.credit:.2f}",
                f"{dates.format_date(entry.created_at.date())} {entry.created_at:%H:%M}",
            ])


def read_csv(path: Path, main_entries) -> CsvImport:
    """Read and check a CSV written by export_csv. Nothing is imported if any row is wrong."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or any(name not in reader.fieldnames for name in CSV_HEADERS):
                return CsvImport([], "This is not an export from this app: the column headings do not match.")
            entries = []
            for line, row in enumerate(reader, start=2):
                entry_or_error = _entry_from_row(row, main_entries)
                if isinstance(entry_or_error, str):
                    return CsvImport([], f"Line {line}: {entry_or_error}")
                entries.append(entry_or_error)
    except (OSError, UnicodeDecodeError, csv.Error):
        return CsvImport([], "This file could not be read.")
    if not entries:
        return CsvImport([], "The file has no entries.")
    return CsvImport(entries)


def _entry_from_row(row: dict, main_entries) -> Entry | str:
    """The entry for one CSV row, or a message saying what is wrong with it."""
    owner = safe_owner(_unguard(row["Owner"]))
    if not owner:
        return "Owner is missing."
    if not ID_PATTERN.match(row["ID"].strip()):
        return "ID is not valid."
    entry_date = dates.parse_date(row["Date"])
    if entry_date is None:
        return "Date is not valid."
    main_head, sub_head = _unguard(row["Main Entry"]).strip(), _unguard(row["Sub-Head"]).strip()
    name, particulars = _unguard(row["Name"]).strip(), _unguard(row["Particulars"]).strip()
    if not main_head or not sub_head or not name or not particulars:
        return "Main Entry, Sub-Head, Name and Particulars are all required."
    if len(sub_head) > config.SUBHEAD_MAX_LENGTH or len(name) > config.NAME_MAX_LENGTH or len(particulars) > config.PARTICULARS_MAX_LENGTH:
        return "A value is longer than the app allows."
    debit, credit = money.parse_amount(row["Debit"]), money.parse_amount(row["Credit"])
    if debit is None or credit is None:
        return "Debit or Credit is not a valid amount."
    return Entry(
        id=row["ID"].strip(),
        main_head=main_entries.id_for_label(main_head),
        sub_head=sub_head,
        entry_date=entry_date,
        name=name,
        particulars=particulars,
        debit=debit,
        credit=credit,
        created_at=_created_at(row["Created At"], entry_date),
        owner=owner,
    )


def _created_at(text: str, fallback_date) -> datetime:
    try:
        date_text, time_text = text.strip().rsplit(" ", 1)
        day = dates.parse_date(date_text)
        hour, minute = (int(part) for part in time_text.split(":"))
        return datetime(day.year, day.month, day.day, hour, minute)
    except (ValueError, AttributeError):
        return datetime(fallback_date.year, fallback_date.month, fallback_date.day)


def _guard(text: str) -> str:
    """Stop Excel running a cell as a formula when it opens the CSV: text starting with = + - @ gets a leading quote."""
    return "'" + text if text.startswith(_FORMULA_STARTS) else text


def _unguard(text: str) -> str:
    return text[1:] if text.startswith("'") and text[1:].startswith(_FORMULA_STARTS) else text
