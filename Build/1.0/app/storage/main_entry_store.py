"""Reads and writes the Main Entries, main_entries.json in the AppData folder.

The first run creates the file with the two starting Main Entries. A removed Main Entry stays in the
file with active set to false, so old rows keep their name (Rules 14). A corrupt file is reported and
is never overwritten (Rules 18).
"""

import json
import os
from pathlib import Path

from app.core import models

ITEM_KEYS = ("id", "name", "active")


class CorruptMainEntryFileError(Exception):
    """The Main Entry file exists but cannot be read."""


def seed_data() -> list[dict]:
    return [{"id": item["id"], "name": item["name"], "active": True, "former_names": []} for item in models.DEFAULT_MAIN_ENTRIES]


class MainEntryStore:
    """Load and save the list of Main Entries."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[dict]:
        """Return the Main Entries. The first run creates the file from the starting values."""
        if not self.path.exists():
            data = seed_data()
            self.save(data)
            return data
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CorruptMainEntryFileError(str(error)) from error
        self._check_shape(data)
        return data

    def save(self, data: list[dict]) -> None:
        """Write the list. The real file is replaced only after the new copy is complete."""
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temp_path, self.path)

    @staticmethod
    def _check_shape(data: object) -> None:
        if not isinstance(data, list) or not data:
            raise CorruptMainEntryFileError("not a list")
        for item in data:
            if not isinstance(item, dict) or any(key not in item for key in ITEM_KEYS):
                raise CorruptMainEntryFileError("bad item")
