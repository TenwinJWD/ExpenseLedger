"""Locations of the files the app uses.

Two folders (Architecture Section 5):
- AppData folder: login, sub-heads, the default-list copy, and the log. Never the Excel data.
- Data folder: the daily Excel ledger files, on the Desktop.

These paths are used only in code. The app never shows them on screen (PRD NFR-9, Rule 36).
"""

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


def data_dir() -> Path:
    """Return Desktop\\ExpenseLedger, creating it if it does not exist."""
    folder = Path.home() / "Desktop" / APP_FOLDER_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def account_file() -> Path:
    """The login file (username, password hash, salt, lock state)."""
    return app_data_dir() / "account.json"


def subheads_file() -> Path:
    """The sub-head lists for both Main Heads."""
    return app_data_dir() / "subheads.json"


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
