"""Tests for app/storage/defaults_store.py (Roadmap Tasks T4.6b). Uses a temporary copy of the seed file."""

import re
import shutil
from pathlib import Path

import pytest

from app.storage.defaults_store import DefaultsListNotFoundError, DefaultsStore, value_for_label

SEED = Path(__file__).resolve().parents[1] / "seed" / "default.js"


@pytest.fixture
def copy_path(tmp_path):
    path = tmp_path / "default.js"
    shutil.copyfile(SEED, path)
    return path


def labels_in(text: str, list_name: str) -> list[str]:
    """The plain label strings inside one list of the file."""
    block = text.split(f"export const {list_name} = toEntries([", 1)[1].split("\n]);", 1)[0]
    return re.findall(r'"([^"]*)"', block)


def test_new_label_goes_to_the_right_list(copy_path):
    DefaultsStore(copy_path).append_label("treesa", "Brand New Head")
    text = copy_path.read_text(encoding="utf-8")
    assert "Brand New Head" in labels_in(text, "treesa")
    assert "Brand New Head" not in labels_in(text, "daily")


def test_value_slug_follows_the_file_rule():
    assert value_for_label("GST & Tax") == "gst_and_tax"
    assert value_for_label("Direct Route Emmanuvel, Cochin") == "direct_route_emmanuvel_cochin"
    assert value_for_label("  Spaced  ") == "spaced"


def test_existing_entries_are_unchanged(copy_path):
    before = labels_in(copy_path.read_text(encoding="utf-8"), "daily")
    DefaultsStore(copy_path).append_label("daily", "Another One")
    after = labels_in(copy_path.read_text(encoding="utf-8"), "daily")
    assert after[:-1] == before
    assert after[-1] == "Another One"


def test_rest_of_file_is_kept(copy_path):
    original = copy_path.read_text(encoding="utf-8")
    DefaultsStore(copy_path).append_label("treesa", "Keep The Rest")
    updated = copy_path.read_text(encoding="utf-8")
    assert updated.startswith(original.split("export const treesa")[0])
    assert updated.endswith(original.split("\n]);\n", 1)[1])


def test_missing_list_leaves_file_unchanged(copy_path):
    original = copy_path.read_text(encoding="utf-8")
    with pytest.raises(DefaultsListNotFoundError):
        DefaultsStore(copy_path).append_label("nope", "Anything")
    assert copy_path.read_text(encoding="utf-8") == original


def test_missing_file_raises(tmp_path):
    with pytest.raises(DefaultsListNotFoundError):
        DefaultsStore(tmp_path / "missing.js").append_label("treesa", "Anything")


def test_quotes_in_label_are_refused(copy_path):
    original = copy_path.read_text(encoding="utf-8")
    with pytest.raises(DefaultsListNotFoundError):
        DefaultsStore(copy_path).append_label("treesa", 'Bad "label"')
    assert copy_path.read_text(encoding="utf-8") == original


def test_ensure_copy_does_not_replace_existing_file(tmp_path):
    target = tmp_path / "AppData" / "default.js"
    target.parent.mkdir(parents=True)
    target.write_text("keep me", encoding="utf-8")
    DefaultsStore(target).ensure_copy(SEED)
    assert target.read_text(encoding="utf-8") == "keep me"


def test_ensure_copy_creates_file_from_seed(tmp_path):
    target = tmp_path / "AppData" / "Defaults" / "default.js"
    DefaultsStore(target).ensure_copy(SEED)
    assert target.read_text(encoding="utf-8") == SEED.read_text(encoding="utf-8")
