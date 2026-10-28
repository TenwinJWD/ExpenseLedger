"""Reads and writes the sub-head lists, subheads.json in the AppData folder (Architecture 5.2).

The file has one list per Main Entry ("treesa" and "daily" for the first two; a new Main Entry gets its own). A removed sub-head
stays in the file with active set to false (Rules 14). A corrupt file is reported and is
never overwritten (Rules 18).
"""

import json
import os
from pathlib import Path

from app.core import config

ITEM_KEYS = ("name", "mandatory", "active")


class CorruptSubheadFileError(Exception):
    """The sub-head file exists but cannot be read."""


def seed_data() -> dict[str, list[dict]]:
    """The starting lists, from the seed values in config.py."""
    seeds = {
        "treesa": config.SEED_SUBHEADS_TREESA,
        "daily": config.SEED_SUBHEADS_DAILY,
    }
    return {
        list_name: [{"name": name, "mandatory": False, "active": True} for name in names]
        for list_name, names in seeds.items()
    }


class SubheadStore:
    """Load and save both sub-head lists as one dictionary."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict[str, list[dict]]:
        """Return the lists. The first run creates the file from the seed values."""
        if not self.path.exists():
            data = seed_data()
            self.save(data)
            return data
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CorruptSubheadFileError(str(error)) from error
        self._check_shape(data)
        return data

    def save(self, data: dict[str, list[dict]]) -> None:
        """Write the lists. The real file is replaced only after the new copy is complete."""
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temp_path, self.path)

    @staticmethod
    def _check_shape(data: object) -> None:
        if not isinstance(data, dict):
            raise CorruptSubheadFileError("not an object")
        for list_name, items in data.items():
            if not isinstance(items, list):
                raise CorruptSubheadFileError(f"bad list {list_name}")
            for item in items:
                if not isinstance(item, dict) or any(key not in item for key in ITEM_KEYS):
                    raise CorruptSubheadFileError(f"bad item in {list_name}")
