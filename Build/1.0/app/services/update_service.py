"""Checks whether a newer version of the app is available.

The app reads one small JSON file from config.UPDATE_URL, for example:
    {"version": "1.1.0", "url": "https://example.com/ExpenseLedger-Setup-1.1.0.exe", "notes": "What is new"}
Nothing is sent except the request for that file. With UPDATE_URL empty, the app never connects.
The app only tells the user and opens the download page. It never downloads or runs anything itself.
"""

import json
import logging
import urllib.request
from dataclasses import dataclass

from app.core import config

_logger = logging.getLogger("expenseledger")


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    url: str
    notes: str


def parse_version(text: str) -> tuple[int, ...] | None:
    """'1.2.0' -> (1, 2, 0). None when the text is not dotted numbers."""
    try:
        parts = tuple(int(part) for part in text.strip().split("."))
    except (ValueError, AttributeError):
        return None
    return parts if parts and all(part >= 0 for part in parts) else None


def is_newer(candidate: str, current: str) -> bool:
    new, old = parse_version(candidate), parse_version(current)
    if new is None or old is None:
        return False
    width = max(len(new), len(old))
    return new + (0,) * (width - len(new)) > old + (0,) * (width - len(old))


def parse_manifest(raw: bytes | str, current: str) -> UpdateInfo | None:
    """The update described by the file, or None when it is not newer, or not valid. Downloads must be https."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    version, url, notes = data.get("version"), data.get("url"), data.get("notes", "")
    if not isinstance(version, str) or not isinstance(url, str) or not isinstance(notes, str):
        return None
    if not url.lower().startswith("https://") or not is_newer(version, current):
        return None
    return UpdateInfo(version=version.strip(), url=url, notes=notes[:300])


def check_for_update(url: str, current: str = config.APP_VERSION, timeout: float = config.UPDATE_TIMEOUT_SECONDS, opener=urllib.request.urlopen) -> UpdateInfo | None:
    """Fetch the file and compare. Any problem (no internet, bad file) just means no update is shown."""
    if not url.lower().startswith("https://"):
        return None
    try:
        with opener(url, timeout=timeout) as response:
            raw = response.read(config.UPDATE_MAX_BYTES)
    except Exception as error:  # an update check must never disturb the app
        _logger.info("Update check skipped: %s", type(error).__name__)
        return None
    return parse_manifest(raw, current)
