"""Main Entry rules: list, add, rename, and remove the Main Entries (the sidebar items under Main Entry).

Removing never deletes: the Main Entry is set to inactive and stays for old rows (Rules 14). Excel keeps
the name a row was saved with, so a renamed Main Entry remembers its former names and old rows still find it.
"""

from app.core import config
from app.core.models import MainEntry
from app.core.validation import name_error
from app.services.auth_service import Result
from app.storage.main_entry_store import MainEntryStore


def _names_taken(item: dict) -> list[str]:
    """Every name this item uses or used, in lower case."""
    return [item["name"].lower()] + [former.lower() for former in item.get("former_names", [])]


class MainEntryService:
    """The Main Entries, in the order they are listed in the sidebar."""

    def __init__(self, store: MainEntryStore) -> None:
        self.store = store

    def items(self) -> list[MainEntry]:
        """All Main Entries, active and removed, in file order."""
        return [
            MainEntry(item["id"], item["name"], bool(item["active"]), list(item.get("former_names", [])))
            for item in self.store.load()
        ]

    def active(self) -> list[MainEntry]:
        return [item for item in self.items() if item.active]

    def label(self, main_head: str) -> str:
        """The name shown for an id. An id the file does not know is shown as it is."""
        for item in self.items():
            if item.id == main_head:
                return item.name
        return main_head

    def id_for_label(self, label: str) -> str:
        """The id for a name read from Excel: the current name, or a former one. An unknown name is its own id."""
        for item in self.items():
            if item.name == label or label in item.former_names:
                return item.id
        return label

    def add(self, name: str) -> Result:
        """Add a Main Entry, or bring back a removed one with the same name."""
        name = name.strip()
        error = name_error(name, config.MAIN_ENTRY_MAX_LENGTH)
        if error:
            return Result(False, error)
        data = self.store.load()
        for item in data:
            if item["name"].lower() == name.lower():
                if item["active"]:
                    return Result(False, "This Main Entry already exists.")
                item["active"] = True
                self.store.save(data)
                return Result(True)
            if name.lower() in _names_taken(item):
                return Result(False, "This name was used before by another Main Entry. Please choose a different name.")
        used = [int(item["id"].split()[-1]) for item in data if item["id"].startswith("MH ") and item["id"].split()[-1].isdigit()]
        data.append({"id": f"MH {max(used, default=0) + 1}", "name": name, "active": True, "former_names": []})
        self.store.save(data)
        return Result(True)

    def rename(self, main_head: str, name: str) -> Result:
        name = name.strip()
        error = name_error(name, config.MAIN_ENTRY_MAX_LENGTH)
        if error:
            return Result(False, error)
        data = self.store.load()
        target = next((item for item in data if item["id"] == main_head), None)
        if target is None:
            return Result(False, "This Main Entry is not in the list.")
        if target["name"] == name:
            return Result(True)
        if any(item is not target and name.lower() in _names_taken(item) for item in data):
            return Result(False, "This Main Entry already exists.")
        former = [old for old in target.get("former_names", []) if old.lower() != name.lower()]
        target["former_names"] = former + [target["name"]]
        target["name"] = name
        self.store.save(data)
        return Result(True)

    def remove(self, main_head: str) -> Result:
        """Hide a Main Entry from the sidebar. At least one must stay."""
        data = self.store.load()
        target = next((item for item in data if item["id"] == main_head), None)
        if target is None:
            return Result(False, "This Main Entry is not in the list.")
        if target["active"] and sum(1 for item in data if item["active"]) <= 1:
            return Result(False, "At least one Main Entry must stay.")
        target["active"] = False
        self.store.save(data)
        return Result(True)
