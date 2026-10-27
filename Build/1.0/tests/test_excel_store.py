"""Tests for app/storage/excel_store.py and the save path in app/services/entry_service.py (Roadmap Tasks T6.7).

Every test writes to a temporary folder (Rules 29), never to the real Desktop folder.
"""

from datetime import date, datetime
from decimal import Decimal

import openpyxl
import pytest

from app.core.models import Entry
from app.services.entry_service import EntryService
from app.storage.excel_store import HEADERS, SHEET_NAME, ExcelFileLockedError, ExcelStore


def make_entry(store: ExcelStore, entry_date=date(2026, 10, 20), name="Lenin", debit="2500.00", credit="0.00", main_head="MH 2"):
    return Entry(
        id=store.next_id(entry_date),
        main_head=main_head,
        sub_head="Lenin",
        entry_date=entry_date,
        name=name,
        particulars="Morning collection",
        debit=Decimal(debit),
        credit=Decimal(credit),
        created_at=datetime(2026, 10, 20, 14, 5),
    )


@pytest.fixture
def store(tmp_path):
    return ExcelStore(tmp_path / "ExpenseLedger")


def test_file_path_follows_the_folder_pattern(store):
    path = store.file_path_for(date(2026, 10, 20))
    assert path.parts[-3:] == ("2026", "10-Oct", "20-Oct-2026.xlsx")


def test_first_save_creates_file_with_header_row(store):
    store.append_entry(make_entry(store))
    workbook = openpyxl.load_workbook(store.file_path_for(date(2026, 10, 20)))
    assert workbook.sheetnames == [SHEET_NAME]
    header = [cell.value for cell in workbook[SHEET_NAME][1]]
    assert tuple(header) == HEADERS


def test_row_stores_text_dates_and_numeric_amounts(store):
    store.append_entry(make_entry(store))
    sheet = openpyxl.load_workbook(store.file_path_for(date(2026, 10, 20)))[SHEET_NAME]
    row = [cell.value for cell in sheet[2]]
    assert row[0] == "E20261020-001"
    assert row[1] == "Daily Collection"
    assert row[3] == "20-Oct-2026"
    assert row[6] == 2500.0
    assert row[8] == "20-Oct-2026 14:05"


def test_second_entry_same_day_gets_next_id(store):
    store.append_entry(make_entry(store))
    second = make_entry(store, name="Mohandas")
    assert second.id == "E20261020-002"
    store.append_entry(second)
    assert len(store.read_all_entries()) == 2


def test_read_all_returns_every_row_with_decimals(store):
    store.append_entry(make_entry(store, debit="2500.50", credit="0"))
    store.append_entry(make_entry(store, entry_date=date(2026, 10, 21), name="RAK"))
    entries = store.read_all_entries()
    assert [entry.name for entry in entries] == ["Lenin", "RAK"]
    assert entries[0].debit == Decimal("2500.50")
    assert entries[0].main_head == "MH 2"
    assert entries[0].created_at == datetime(2026, 10, 20, 14, 5)


def test_update_in_place_keeps_the_same_file(store):
    original = make_entry(store)
    store.append_entry(original)
    original.name = "Changed Name"
    original.debit = Decimal("999.00")
    store.update_entry(original, old_date=date(2026, 10, 20))
    saved = store.read_all_entries()
    assert len(saved) == 1
    assert saved[0].name == "Changed Name"
    assert saved[0].debit == Decimal("999.00")


def test_update_with_new_date_moves_the_row(store):
    original = make_entry(store)
    store.append_entry(original)
    original.entry_date = date(2026, 10, 25)
    store.update_entry(original, old_date=date(2026, 10, 20))
    # The old day's file is kept (Rules 16) but holds no entries any more.
    assert store.file_path_for(date(2026, 10, 25)).exists()
    old_sheet = openpyxl.load_workbook(store.file_path_for(date(2026, 10, 20)))[SHEET_NAME]
    assert old_sheet.max_row == 1
    assert store.read_all_entries()[0].entry_date == date(2026, 10, 25)
    assert len(store.read_all_entries()) == 1


def test_delete_removes_only_that_row(store):
    first = make_entry(store)
    store.append_entry(first)
    second = make_entry(store, name="Vivek")
    store.append_entry(second)
    store.delete_entry(first.id, date(2026, 10, 20))
    remaining = store.read_all_entries()
    assert [entry.name for entry in remaining] == ["Vivek"]


def test_locked_file_raises_and_nothing_is_lost(store):
    store.append_entry(make_entry(store))
    path = store.file_path_for(date(2026, 10, 20))
    with open(path, "rb"):  # stands in for Excel holding the file open
        with pytest.raises(ExcelFileLockedError):
            store.append_entry(make_entry(store, name="Blocked"))
    assert not path.with_name(path.stem + ".tmp.xlsx").exists()
    assert [entry.name for entry in store.read_all_entries()] == ["Lenin"]
    store.append_entry(make_entry(store, name="Retry"))
    assert [entry.name for entry in store.read_all_entries()] == ["Lenin", "Retry"]


def test_service_reports_locked_file_as_a_message_and_keeps_the_entry_in_the_form(store):
    service = EntryService(store)
    assert service.save_entry("MH 2", "Lenin", date(2026, 10, 20), "Lenin", "Morning", Decimal("10"), Decimal("0")).ok
    path = store.file_path_for(date(2026, 10, 20))
    with open(path, "rb"):
        result = service.save_entry("MH 2", "Lenin", date(2026, 10, 20), "Blocked", "Morning", Decimal("10"), Decimal("0"))
    assert not result.ok
    assert result.message == (
        "The Excel file for 20-Oct-2026 is open. Close it in Excel and click Submit again. "
        "Your entry has not been lost."
    )


def test_read_all_on_empty_folder_returns_nothing(tmp_path):
    assert ExcelStore(tmp_path / "missing").read_all_entries() == []
