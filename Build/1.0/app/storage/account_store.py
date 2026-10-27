"""Reads and writes the login file, account.json in the AppData folder (Architecture 5.3).

A corrupt file is reported, never overwritten (Rules 18). Saves go to a temporary
file first and then replace the real file, so a crash cannot leave half a file.
"""

import json
import os
from pathlib import Path

REQUIRED_KEYS = ("username", "password_hash", "salt", "iterations", "failed_attempts", "locked_until")


class CorruptAccountFileError(Exception):
    """The login file exists but cannot be read."""


class AccountStore:
    """Load and save the account record as a dictionary."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> dict | None:
        """Return the account record, or None if no account exists yet."""
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CorruptAccountFileError(str(error)) from error
        if not isinstance(data, dict) or any(key not in data for key in REQUIRED_KEYS):
            raise CorruptAccountFileError("missing fields")
        return data

    def save(self, data: dict) -> None:
        """Write the account record. The real file is replaced only after the new copy is complete."""
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(temp_path, self.path)
