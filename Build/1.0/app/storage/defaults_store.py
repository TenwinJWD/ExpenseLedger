"""Adds new sub-head labels to the list file, default.js (PRD FR-8, Rules 18a).

The file is JavaScript with one list per Main Head ("treesa" and "daily"). The list
holds plain label strings, and toEntries() in the file builds the { label, value }
pairs. This module only appends a new label string, before the closing "]);" of the
list, and keeps the rest of the file as it is. It never removes or edits an entry.
If the file or the list cannot be found, it raises an error and leaves the file unchanged.
"""

import os
import re
import shutil
from pathlib import Path


class DefaultsListNotFoundError(Exception):
    """The file or the list inside it cannot be found, so nothing was changed."""


def value_for_label(label: str) -> str:
    """The stored value, using the same rule as toEntries() in default.js."""
    value = label.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


class DefaultsStore:
    """Owns the working copy of default.js in the AppData folder."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def ensure_copy(self, seed_path: Path) -> None:
        """Copy the seed file into AppData on the first run. An existing copy is never replaced."""
        if self.path.exists():
            return
        if not seed_path.exists():
            raise DefaultsListNotFoundError("seed file missing")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed_path, self.path)

    def append_label(self, list_name: str, label: str) -> str:
        """Add the label at the end of the list. Returns the stored value."""
        if '"' in label or "\\" in label:
            raise DefaultsListNotFoundError("label has characters that cannot be stored")
        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as error:
            raise DefaultsListNotFoundError(str(error)) from error

        opening = f"export const {list_name} = toEntries(["
        start = text.find(opening)
        if start < 0:
            raise DefaultsListNotFoundError(f"list {list_name} not found")
        body_start = start + len(opening)
        closing = text.find("\n]);", body_start)
        if closing < 0:
            raise DefaultsListNotFoundError(f"list {list_name} has no closing line")

        body = text[body_start:closing].rstrip()
        if not body.endswith(","):
            body += ","
        updated = text[:body_start] + body + f'\n  "{label}"' + text[closing:]

        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(updated, encoding="utf-8")
        os.replace(temp_path, self.path)
        return value_for_label(label)
