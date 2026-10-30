"""Locations of the files the app uses.

Two folders (Architecture Section 5):
- AppData folder: login, sub-heads, the default-list copy, and the log. Never the Excel data.
- Data folder: the daily Excel ledger files. Each Windows user chooses it on the first run (settings.json in
  the AppData folder remembers it). Without a choice it is Desktop\\ExpenseLedger.

These paths are used only in code. The app never shows them on screen (PRD NFR-9, Rule 36).
"""

import json
import os
from pathlib import Path

from app.core import config

APP_FOLDER_NAME = "ExpenseLedger"


def app_data_dir() -> Path:
    """Return %APPDATA%\\ExpenseLedger, creating it if it does not exist."""
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    folder = Path(base) / APP_FOLDER_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder


SETTINGS_FILE_NAME = "settings.json"
PROBE_FILE_NAME = ".expenseledger-write-test"


def settings_file() -> Path:
    """This user's settings: the folder they chose for the Excel files."""
    return app_data_dir() / SETTINGS_FILE_NAME


def default_data_dir() -> Path:
    """Desktop\\ExpenseLedger, the folder used when none was chosen (and by version 1.0)."""
    return Path.home() / "Desktop" / APP_FOLDER_NAME


def saved_data_dir() -> Path | None:
    """The folder this user chose, or None when nothing was saved yet (or the file cannot be read)."""
    try:
        data = json.loads(settings_file().read_text(encoding="utf-8"))
        folder = data.get("data_dir") if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None
    return Path(folder) if isinstance(folder, str) and folder.strip() else None


def _read_settings() -> dict:
    try:
        data = json.loads(settings_file().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_settings(data: dict) -> None:
    """The real file is replaced only after the new copy is complete."""
    temp_path = settings_file().with_suffix(".tmp")
    temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(temp_path, settings_file())


def save_data_dir(folder: Path) -> None:
    """Remember the chosen folder for this Windows user."""
    _write_settings({**_read_settings(), "data_dir": str(folder)})


def folder_problem(folder: Path) -> str:
    """Why the folder cannot hold the ledger files, or an empty string when it can."""
    try:
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / PROBE_FILE_NAME
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError:
        return "This folder cannot be used. Please choose another folder that you can save files in."
    return ""


def data_dir() -> Path:
    """Return this user's data folder, creating it if it does not exist."""
    folder = saved_data_dir() or default_data_dir()
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def account_file() -> Path:
    """The login file (username, password hash, salt, lock state)."""
    return app_data_dir() / "account.json"


def entry_index_file() -> Path:
    """The SQLite index of the Excel files. Only a cache: deleting it just makes the next start slower."""
    return app_data_dir() / "entries-index.db"


def subheads_file() -> Path:
    """The sub-head lists for both Main Heads."""
    return app_data_dir() / "subheads.json"


def main_entries_file() -> Path:
    """The Main Entries (the sidebar items under Main Entry)."""
    return app_data_dir() / "main_entries.json"


def log_file() -> Path:
    """The plain-text log. Dates in it use DD-Mon-YYYY (PRD FR-32)."""
    return app_data_dir() / "app.log"


def default_list_file() -> Path:
    """The working copy of the sub-head list file, kept in AppData (PRD FR-8)."""
    folder = app_data_dir() / "Defaults"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "default.js"


def asset_file(name: str) -> Path:
    """A file shipped with the program in the assets folder, such as the app icon."""
    return Path(__file__).resolve().parents[2] / "assets" / name


def seed_default_file() -> Path:
    """The seed copy of the sub-head list file, shipped with the program (Architecture 5.2)."""
    return Path(__file__).resolve().parents[2] / "seed" / "default.js"
