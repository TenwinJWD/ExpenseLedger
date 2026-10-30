"""Tests for per-user file names, CSV export and import, the PDF export, and the version 1 to 2 file rename."""

import json
from datetime import date, datetime
from decimal import Decimal

import openpyxl
import pytest

from app.core.models import Entry
from app.services import exchange_service, pdf_report
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.storage import migrations
from app.storage.excel_store import ExcelStore, safe_owner
from app.storage.main_entry_store import MainEntryStore


def make_store(root, username):
    return ExcelStore(root, owner=lambda: username)


def save(store, name="Lenin", entry_date=date(2026, 10, 20), debit="10.00", credit="0.00"):
    EntryService(store).save_entry("MH 2", "Lenin", entry_date, name, "Morning", Decimal(debit), Decimal(credit))


@pytest.fixture
def main_entries(tmp_path):
    return MainEntryService(MainEntryStore(tmp_path / "main_entries.json"))


def test_file_name_has_the_date_then_the_username(tmp_path):
    store = make_store(tmp_path, "tenwin")
    assert store.file_path_for(date(2026, 10, 20)).name == "20-Oct-2026_tenwin.xlsx"
    save(store)
    assert store.file_path_for(date(2026, 10, 20)).exists()


def test_username_is_made_safe_for_a_file_name():
    assert safe_owner("  a/b:c*  ") == "a_b_c_"
    assert safe_owner("Mary Ann") == "Mary Ann"


def test_two_users_the_same_day_get_separate_files_with_the_same_id(tmp_path):
    first, second = make_store(tmp_path, "asha"), make_store(tmp_path, "babu")
    save(first, "Lenin")
    save(second, "Vivek")
    names = sorted(path.name for path in tmp_path.rglob("*.xlsx"))
    assert names == ["20-Oct-2026_asha.xlsx", "20-Oct-2026_babu.xlsx"]
    rows = first.read_all_entries()
    assert [(row.owner, row.id) for row in rows] == [("asha", "E20261020-001"), ("babu", "E20261020-001")]
    assert [first.is_mine(row) for row in rows] == [True, False]


def test_a_user_changes_only_their_own_file(tmp_path):
    first, second = make_store(tmp_path, "asha"), make_store(tmp_path, "babu")
    save(first, "Lenin")
    save(second, "Vivek")
    mine = next(row for row in first.read_all_entries() if first.is_mine(row))
    mine.name = "Changed"
    first.update_entry(mine, mine.entry_date)
    assert {row.owner: row.name for row in first.read_all_entries()} == {"asha": "Changed", "babu": "Vivek"}
    first.delete_entry(mine.id, mine.entry_date)
    assert [row.owner for row in first.read_all_entries()] == ["babu"]


def test_csv_round_trip_into_another_users_folder(tmp_path, main_entries):
    source = make_store(tmp_path / "asha_pc", "asha")
    save(source, "Lenin", debit="2500.50")
    save(source, "=cmd|calc", entry_date=date(2026, 10, 21))
    csv_path = tmp_path / "out.csv"
    exchange_service.export_csv(csv_path, source.read_all_entries(), main_entries, "asha")
    assert "'=cmd|calc" in csv_path.read_text(encoding="utf-8-sig")  # Excel will not run it

    parsed = exchange_service.read_csv(csv_path, main_entries)
    assert parsed.problem == ""
    target = make_store(tmp_path / "babu_pc", "babu")
    save(target, "Own row")
    assert target.import_entries(parsed.entries) == (2, 0)
    rows = target.read_all_entries()
    assert sorted((row.owner, row.name) for row in rows) == [("asha", "=cmd|calc"), ("asha", "Lenin"), ("babu", "Own row")]
    lenin = next(row for row in rows if row.name == "Lenin")
    assert lenin.debit == Decimal("2500.50") and not target.is_mine(lenin)
    sheet = openpyxl.load_workbook(target.file_path_for(date(2026, 10, 21), "asha"))["Entries"]
    assert sheet["E2"].data_type == "s"  # stored as text, not as a formula


def test_importing_the_same_csv_twice_adds_nothing(tmp_path, main_entries):
    source = make_store(tmp_path / "a", "asha")
    save(source)
    csv_path = tmp_path / "out.csv"
    exchange_service.export_csv(csv_path, source.read_all_entries(), main_entries, "asha")
    target = make_store(tmp_path / "b", "babu")
    entries = exchange_service.read_csv(csv_path, main_entries).entries
    assert target.import_entries(entries) == (1, 0)
    assert target.import_entries(entries) == (0, 1)
    assert len(target.read_all_entries()) == 1


def test_a_bad_row_stops_the_whole_import(tmp_path, main_entries):
    source = make_store(tmp_path / "a", "asha")
    save(source)
    csv_path = tmp_path / "out.csv"
    exchange_service.export_csv(csv_path, source.read_all_entries(), main_entries, "asha")
    csv_path.write_text(csv_path.read_text(encoding="utf-8-sig").replace("10.00", "ten"), encoding="utf-8")
    parsed = exchange_service.read_csv(csv_path, main_entries)
    assert parsed.entries == [] and parsed.problem.startswith("Line 2:")


def test_a_csv_from_something_else_is_refused(tmp_path, main_entries):
    path = tmp_path / "other.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    assert "not an export" in exchange_service.read_csv(path, main_entries).problem


def test_pdf_export_writes_a_pdf(tmp_path, main_entries):
    entries = [
        Entry("E20261020-001", "MH 2", "Lenin", date(2026, 10, 20), f"Name {number}", "Morning", Decimal("10.00"), Decimal("0.00"),
              datetime(2026, 10, 20, 9, 0), "asha")
        for number in range(80)  # enough rows to need a second page
    ]
    path = tmp_path / "out.pdf"
    pdf_report.export_pdf(path, entries, main_entries, "asha", today=date(2026, 10, 29))
    data = path.read_bytes()
    assert data.startswith(b"%PDF") and data.count(b"/Type /Page\n") >= 2


def test_migration_renames_old_files_with_the_username(tmp_path):
    app_data, data_dir = tmp_path / "app", tmp_path / "data"
    app_data.mkdir()
    (app_data / "account.json").write_text(json.dumps({"username": "asha"}), encoding="utf-8")
    old = data_dir / "2026" / "10-Oct" / "20-Oct-2026.xlsx"
    old.parent.mkdir(parents=True)
    old.write_bytes(b"x")
    migrations.MIGRATIONS[1](migrations.MigrationContext(app_data, data_dir))
    assert not old.exists()
    assert (old.parent / "20-Oct-2026_asha.xlsx").exists()
    backed_up = list((app_data / migrations.BACKUP_FOLDER).rglob("20-Oct-2026.xlsx"))
    assert len(backed_up) == 1
