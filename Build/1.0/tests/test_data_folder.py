"""The data folder is chosen per Windows user and remembered in that user's AppData."""

import pytest

from app.core import paths


@pytest.fixture
def profile(tmp_path, monkeypatch):
    """A fake Windows profile: its own AppData and home folder."""
    monkeypatch.setenv("APPDATA", str(tmp_path / "AppData"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return tmp_path


def test_nothing_saved_means_no_choice_yet(profile):
    assert paths.saved_data_dir() is None


def test_without_a_choice_the_data_folder_is_the_desktop_folder(profile):
    assert paths.data_dir() == paths.default_data_dir()
    assert paths.data_dir().is_dir()


def test_a_saved_choice_is_used_and_created(profile):
    chosen = profile / "MyLedger"
    paths.save_data_dir(chosen)
    assert paths.saved_data_dir() == chosen
    assert paths.data_dir() == chosen
    assert chosen.is_dir()


def test_two_users_keep_separate_choices(tmp_path, monkeypatch):
    for user in ("anu", "binu"):
        monkeypatch.setenv("APPDATA", str(tmp_path / user / "AppData"))
        paths.save_data_dir(tmp_path / user / "Ledger")
    monkeypatch.setenv("APPDATA", str(tmp_path / "anu" / "AppData"))
    assert paths.saved_data_dir() == tmp_path / "anu" / "Ledger"
    monkeypatch.setenv("APPDATA", str(tmp_path / "binu" / "AppData"))
    assert paths.saved_data_dir() == tmp_path / "binu" / "Ledger"


def test_an_unreadable_settings_file_means_no_choice(profile):
    paths.settings_file().write_text("not json", encoding="utf-8")
    assert paths.saved_data_dir() is None
    paths.settings_file().write_text('{"data_dir": ""}', encoding="utf-8")
    assert paths.saved_data_dir() is None


def test_a_usable_folder_has_no_problem_and_leaves_no_test_file(profile):
    folder = profile / "Ledger"
    assert paths.folder_problem(folder) == ""
    assert list(folder.iterdir()) == []


def test_a_folder_that_cannot_be_created_is_reported(profile):
    blocker = profile / "afile"
    blocker.write_text("x", encoding="utf-8")
    assert paths.folder_problem(blocker / "inside") != ""
