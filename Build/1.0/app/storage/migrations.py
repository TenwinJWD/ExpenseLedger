"""Keeps the files the app saves in step with the app version (data version, not app version).

state.json in the AppData folder records the data version the files are in. At start-up,
run() compares it with DATA_VERSION. If the files are older, it first copies them to
AppData\\Backups, then runs each migration in order (1 to 2, 2 to 3, ...). If a migration
fails, the state is not advanced, the backup stays, and MigrationError is raised.

How to ship a format change in a new release:
  1. Raise DATA_VERSION by one.
  2. Write a function that upgrades the files from the old version to the new one, and add it to MIGRATIONS
     under the old version number.
  3. A migration that changes the Excel files (context.data_dir) must back them up itself first.
Files from before this feature (no state.json) are the baseline, version 1.
"""

import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from app.core import config
from app.storage.excel_store import safe_owner

DATA_VERSION = 2
STATE_FILE = "state.json"
BACKUP_FOLDER = "Backups"
KEEP_BACKUPS = 5
BACKED_UP = ("account.json", "subheads.json", "main_entries.json", "settings.json", "Defaults")

_logger = logging.getLogger("expenseledger")


@dataclass(frozen=True)
class MigrationContext:
    app_data: Path  # login, sub-heads, default list, log
    data_dir: Path  # the daily Excel ledger files


Migration = Callable[[MigrationContext], None]

def _name_daily_files_with_username(context: MigrationContext) -> None:
    """Version 1 to 2: daily files are named <DD-Mon-YYYY>_<username>.xlsx, so each user's file is told apart.

    The account's username is used. With no account there are no files of ours to rename. Existing files are
    copied to Backups first and then renamed; a file that already has the new name is left alone.
    """
    try:
        data = json.loads((context.app_data / "account.json").read_text(encoding="utf-8"))
        owner = safe_owner(data["username"])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return
    if not owner or not context.data_dir.exists():
        return
    old_files = [path for path in context.data_dir.rglob("*.xlsx") if "_" not in path.stem and ".tmp" not in path.name]
    if not old_files:
        return
    copy_root = context.app_data / BACKUP_FOLDER / f"v1-to-v2-excel-{datetime.now():%Y%m%d-%H%M%S}"
    for path in old_files:
        target = copy_root / path.relative_to(context.data_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    for path in old_files:
        renamed = path.with_name(f"{path.stem}_{owner}.xlsx")
        if not renamed.exists():
            path.rename(renamed)


# Key = the data version the migration upgrades FROM. The function upgrades the files to key + 1.
MIGRATIONS: dict[int, Migration] = {1: _name_daily_files_with_username}


class MigrationError(Exception):
    """A migration failed. The files were backed up first."""


class DataTooNewError(Exception):
    """The files were saved by a newer version of the app than this one."""


def read_state(app_data: Path) -> dict:
    """The saved state, or the baseline when there is none (or it cannot be read)."""
    path = app_data / STATE_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("data_version"), int) and data["data_version"] >= 1:
            return data
    except FileNotFoundError:
        pass
    except (OSError, json.JSONDecodeError):
        _logger.warning("state.json could not be read; treating the files as data version 1")
    return {"data_version": 1}


def write_state(app_data: Path, data_version: int) -> None:
    state = {"data_version": data_version, "app_version": config.APP_VERSION, "updated": datetime.now().isoformat(timespec="seconds")}
    temp_path = app_data / (STATE_FILE + ".tmp")
    temp_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(temp_path, app_data / STATE_FILE)


def backup(app_data: Path, from_version: int, to_version: int) -> Path:
    """Copy the files that a migration may change, then drop the oldest backups."""
    root = app_data / BACKUP_FOLDER
    folder = root / f"v{from_version}-to-v{to_version}-{datetime.now():%Y%m%d-%H%M%S}"
    folder.mkdir(parents=True, exist_ok=True)
    for name in BACKED_UP:
        source = app_data / name
        if source.is_dir():
            shutil.copytree(source, folder / name, dirs_exist_ok=True)
        elif source.is_file():
            shutil.copy2(source, folder / name)
    existing = sorted(path for path in root.iterdir() if path.is_dir())
    for stale in existing[:-KEEP_BACKUPS]:
        shutil.rmtree(stale, ignore_errors=True)
    return folder


def run(context: MigrationContext, target: int = DATA_VERSION, migrations: dict[int, Migration] | None = None) -> int:
    """Bring the files up to the target data version. Returns the version they are now in."""
    migrations = MIGRATIONS if migrations is None else migrations
    stored = read_state(context.app_data)["data_version"]
    if stored > target:
        raise DataTooNewError(f"files are data version {stored}, this app understands up to {target}")
    if stored == target:
        if not (context.app_data / STATE_FILE).exists():
            write_state(context.app_data, target)
        return target

    backup_folder = backup(context.app_data, stored, target)
    _logger.info("Upgrading saved files from data version %s to %s (backup: %s)", stored, target, backup_folder.name)
    for version in range(stored, target):
        step = migrations.get(version)
        if step is None:
            raise MigrationError(f"no migration from data version {version}")
        try:
            step(context)
        except Exception as error:
            _logger.exception("Migration from data version %s failed", version)
            raise MigrationError(str(error)) from error
        write_state(context.app_data, version + 1)
    return target
