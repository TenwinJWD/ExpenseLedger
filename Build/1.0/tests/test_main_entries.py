"""Tests for the editable Main Entries and the renamed Transactions fields (Modify Fields page).

Every test writes to a temporary folder (Rules 29).
"""

import json
from datetime import date, datetime
from decimal import Decimal

import pytest

from app.core import config
from app.core.models import Entry
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.services.subhead_service import SubheadService
from app.storage.excel_store import ExcelStore
from app.storage.main_entry_store import CorruptMainEntryFileError, MainEntryStore
from app.storage.subhead_store import SubheadStore


@pytest.fixture
def heads(tmp_path):
    return MainEntryService(MainEntryStore(tmp_path / "main_entries.json"))


@pytest.fixture
def subheads(tmp_path):
    return SubheadService(SubheadStore(tmp_path / "subheads.json"))


# ----- Main Entries -----

def test_first_run_has_the_two_starting_entries(heads, tmp_path):
    assert [(item.id, item.name) for item in heads.active()] == [("MH 1", "Treesa Agencies"), ("MH 2", "Daily Collection")]
    assert (tmp_path / "main_entries.json").exists()


def test_add_gets_the_next_id_and_appears_last(heads):
    assert heads.add("  PD Agencies ").ok
    assert [item.id for item in heads.active()] == ["MH 1", "MH 2", "MH 3"]
    assert heads.label("MH 3") == "PD Agencies"


def test_ids_are_not_reused_after_a_removal(heads):
    heads.add("PD Agencies")
    heads.remove("MH 3")
    heads.add("Manjeri")
    assert heads.label("MH 4") == "Manjeri"


@pytest.mark.parametrize(
    "name, message",
    [
        ("", "Enter a name."),
        ("x" * (config.MAIN_ENTRY_MAX_LENGTH + 1), f"Use up to {config.MAIN_ENTRY_MAX_LENGTH} characters."),
        ('Bad "quote"', "Quotation marks and backslashes cannot be used."),
        ("treesa agencies", "This Main Entry already exists."),
    ],
)
def test_add_rejects_bad_names(heads, name, message):
    result = heads.add(name)
    assert not result.ok and result.message == message


def test_rename_keeps_the_id_and_remembers_the_old_name(heads):
    assert heads.rename("MH 1", "Treesa Traders").ok
    assert heads.label("MH 1") == "Treesa Traders"
    assert heads.id_for_label("Treesa Traders") == "MH 1"
    assert heads.id_for_label("Treesa Agencies") == "MH 1"  # rows saved before the rename


def test_rename_to_another_entrys_name_is_refused(heads):
    assert heads.rename("MH 1", "Daily Collection").message == "This Main Entry already exists."


def test_a_name_used_before_cannot_be_taken_by_a_new_entry(heads):
    heads.rename("MH 1", "Treesa Traders")
    assert not heads.add("Treesa Agencies").ok


def test_remove_hides_but_keeps_the_name_for_old_rows(heads):
    assert heads.remove("MH 1").ok
    assert [item.id for item in heads.active()] == ["MH 2"]
    assert heads.label("MH 1") == "Treesa Agencies"


def test_the_last_active_entry_cannot_be_removed(heads):
    heads.remove("MH 1")
    result = heads.remove("MH 2")
    assert not result.ok and result.message == "At least one Main Entry must stay."


def test_adding_a_removed_name_brings_it_back(heads):
    heads.remove("MH 1")
    assert heads.add("Treesa Agencies").ok
    assert [item.id for item in heads.active()] == ["MH 1", "MH 2"]


def test_unknown_excel_label_is_its_own_id(heads):
    assert heads.id_for_label("Typed In Excel") == "Typed In Excel"
    assert heads.label("Typed In Excel") == "Typed In Excel"


def test_corrupt_file_is_reported_and_not_overwritten(tmp_path):
    path = tmp_path / "main_entries.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(CorruptMainEntryFileError):
        MainEntryStore(path).load()
    assert path.read_text(encoding="utf-8") == "{not json"


# ----- Transactions fields (sub-heads) of any Main Entry -----

def test_a_new_main_entry_starts_with_an_empty_list_of_its_own(subheads):
    assert subheads.active_names("MH 3") == []
    assert subheads.add_subhead("MH 3", "Fuel").ok
    assert subheads.active_names("MH 3") == ["Fuel"]
    assert "Fuel" not in subheads.active_names("MH 1")


def test_a_file_with_an_extra_list_still_loads(tmp_path, subheads):
    subheads.add_subhead("MH 3", "Fuel")
    data = json.loads((tmp_path / "subheads.json").read_text(encoding="utf-8"))
    assert "mh3" in data and "treesa" in data and "daily" in data
    assert SubheadStore(tmp_path / "subheads.json").load()["mh3"][0]["name"] == "Fuel"


def test_rename_subhead_keeps_the_position_and_the_old_name(subheads):
    names = subheads.active_names("MH 2")
    assert subheads.rename_subhead("MH 2", "Lenin", "Lenin K").ok
    renamed = subheads.active_names("MH 2")
    assert renamed[names.index("Lenin")] == "Lenin K" and len(renamed) == len(names)
    assert subheads.renamed_map("MH 2") == {"Lenin": "Lenin K"}


@pytest.mark.parametrize("new_name, message", [("", "Enter a name."), ("MOHANDAS", "This Sub-Head already exists.")])
def test_rename_subhead_rejects_bad_names(subheads, new_name, message):
    result = subheads.rename_subhead("MH 2", "Lenin", new_name)
    assert not result.ok and result.message == message


def test_a_renamed_away_name_cannot_be_added_again(subheads):
    subheads.rename_subhead("MH 2", "Lenin", "Lenin K")
    assert not subheads.add_subhead("MH 2", "Lenin").ok


def test_renaming_back_clears_the_old_name_mapping(subheads):
    subheads.rename_subhead("MH 2", "Lenin", "Lenin K")
    subheads.rename_subhead("MH 2", "Lenin K", "Lenin")
    assert subheads.renamed_map("MH 2") == {"Lenin K": "Lenin"}


# ----- Excel keeps working across renames -----

def make_entry(store, main_head, sub_head="Lenin"):
    return Entry(
        id=store.next_id(date(2026, 10, 20)),
        main_head=main_head,
        sub_head=sub_head,
        entry_date=date(2026, 10, 20),
        name="Name",
        particulars="Particulars",
        debit=Decimal("10.00"),
        credit=Decimal("0.00"),
        created_at=datetime(2026, 10, 20, 9, 0),
    )


def test_rows_saved_before_a_rename_are_read_under_the_new_names(tmp_path, heads, subheads):
    store = ExcelStore(tmp_path / "data", heads)
    service = EntryService(store, subheads)
    store.append_entry(make_entry(store, "MH 1", sub_head="Salary"))
    heads.rename("MH 1", "Treesa Traders")
    subheads.rename_subhead("MH 1", "Salary", "Salary and Wages")

    [entry] = service.all_entries()
    assert (entry.main_head, entry.sub_head) == ("MH 1", "Salary and Wages")


def test_a_new_main_entry_round_trips_through_excel(tmp_path, heads):
    heads.add("PD Agencies")
    store = ExcelStore(tmp_path / "data", heads)
    store.append_entry(make_entry(store, "MH 3"))
    assert [entry.main_head for entry in store.read_all_entries()] == ["MH 3"]


def test_a_removed_main_entry_still_reads_back(tmp_path, heads):
    store = ExcelStore(tmp_path / "data", heads)
    store.append_entry(make_entry(store, "MH 1"))
    heads.remove("MH 1")
    assert [entry.main_head for entry in store.read_all_entries()] == ["MH 1"]
