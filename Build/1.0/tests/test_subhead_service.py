"""Tests for app/services/subhead_service.py (Roadmap Tasks T4.6). Uses a temporary folder (Rules 29)."""

import json

import pytest

from app.core import config
from app.services.subhead_service import SubheadService
from app.storage.subhead_store import SubheadStore


@pytest.fixture
def service(tmp_path):
    return SubheadService(SubheadStore(tmp_path / "subheads.json"))


def test_first_run_creates_file_with_seed_values(service, tmp_path):
    names = service.active_names("MH 1")
    assert names == list(config.SEED_SUBHEADS_TREESA)
    assert service.active_names("MH 2") == list(config.SEED_SUBHEADS_DAILY)
    assert (tmp_path / "subheads.json").exists()


def test_add_appends_new_sub_head(service):
    assert service.add_subhead("MH 2", "Route Nine").ok
    assert service.active_names("MH 2")[-1] == "Route Nine"


def test_add_is_per_main_head(service):
    service.add_subhead("MH 1", "Only Treesa")
    assert "Only Treesa" in service.active_names("MH 1")
    assert "Only Treesa" not in service.active_names("MH 2")


@pytest.mark.parametrize(
    "name, message",
    [
        ("", "Enter a name."),
        ("   ", "Enter a name."),
        ("x" * (config.SUBHEAD_MAX_LENGTH + 1), f"Use up to {config.SUBHEAD_MAX_LENGTH} characters."),
        ('Bad "quote"', "Quotation marks and backslashes cannot be used."),
        ("Bad\\slash", "Quotation marks and backslashes cannot be used."),
    ],
)
def test_add_rejects_invalid_names(service, name, message):
    result = service.add_subhead("MH 1", name)
    assert not result.ok
    assert result.message == message


def test_add_rejects_duplicate_case_insensitively(service):
    result = service.add_subhead("MH 2", "LENIN")
    assert not result.ok
    assert result.message == "This Sub-Head already exists."


def test_add_trims_spaces(service):
    service.add_subhead("MH 2", "   Spaced Name   ")
    assert "Spaced Name" in service.active_names("MH 2")


def test_remove_sets_inactive_and_hides_from_dropdown(service):
    assert service.remove_subhead("MH 2", "Lenin").ok
    assert "Lenin" not in service.active_names("MH 2")
    removed = [item for item in service.items("MH 2") if item.name == "Lenin"]
    assert len(removed) == 1 and removed[0].active is False


def test_remove_deletes_nothing(service):
    before = len(service.items("MH 2"))
    service.remove_subhead("MH 2", "Lenin")
    assert len(service.items("MH 2")) == before


def test_mandatory_sub_head_cannot_be_removed(tmp_path):
    store = SubheadStore(tmp_path / "subheads.json")
    data = store.load()
    data["daily"][0]["mandatory"] = True
    store.save(data)
    service = SubheadService(store)
    result = service.remove_subhead("MH 2", data["daily"][0]["name"])
    assert not result.ok
    assert result.message == "This Sub-Head cannot be removed."
    assert data["daily"][0]["name"] in service.active_names("MH 2")


def test_adding_a_removed_name_brings_it_back(service):
    service.remove_subhead("MH 2", "Lenin")
    assert service.add_subhead("MH 2", "Lenin").ok
    assert "Lenin" in service.active_names("MH 2")
    assert len([item for item in service.items("MH 2") if item.name == "Lenin"]) == 1


def test_corrupt_file_is_not_overwritten(tmp_path):
    path = tmp_path / "subheads.json"
    path.write_text("{ broken", encoding="utf-8")
    service = SubheadService(SubheadStore(path))
    with pytest.raises(Exception):
        service.active_names("MH 1")
    assert path.read_text(encoding="utf-8") == "{ broken"


def test_file_keeps_both_lists(service, tmp_path):
    service.add_subhead("MH 1", "New Treesa")
    saved = json.loads((tmp_path / "subheads.json").read_text(encoding="utf-8"))
    assert set(saved) == {"treesa", "daily"}
    assert any(item["name"] == "New Treesa" for item in saved["treesa"])
