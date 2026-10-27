"""Sub-head rules: add, remove, and list the sub-heads for each Main Head (PRD FR-8, FR-9, FR-11).

Removing never deletes: the sub-head is set to inactive and stays for old entries (Rules 14).
Adding a name that was removed earlier brings that sub-head back instead of making a copy.
"""

from app.core import config
from app.core.models import MAIN_HEAD_LIST_NAME, SubHead
from app.services.auth_service import Result
from app.storage.defaults_store import DefaultsListNotFoundError, DefaultsStore
from app.storage.subhead_store import SubheadStore

FORBIDDEN_CHARACTERS = ('"', "\\")


class SubheadService:
    """The sub-head lists for both Main Heads."""

    def __init__(self, store: SubheadStore, defaults: DefaultsStore | None = None) -> None:
        self.store = store
        self.defaults = defaults

    def items(self, main_head: str) -> list[SubHead]:
        """All sub-heads for a Main Head, active and removed, in file order."""
        data = self.store.load()
        return [SubHead(**item) for item in data[MAIN_HEAD_LIST_NAME[main_head]]]

    def active_names(self, main_head: str) -> list[str]:
        """Names for the dropdown: active sub-heads only, in order (FR-11)."""
        return [item.name for item in self.items(main_head) if item.active]

    def add_subhead(self, main_head: str, name: str) -> Result:
        """Add a sub-head to the list of the Main Head (FR-8)."""
        name = name.strip()
        error = self._name_error(name)
        if error:
            return Result(False, error)

        list_name = MAIN_HEAD_LIST_NAME[main_head]
        data = self.store.load()
        items = data[list_name]
        for item in items:
            if item["name"].lower() == name.lower():
                if item["active"]:
                    return Result(False, "This Sub-Head already exists.")
                item["active"] = True  # bring back a removed sub-head instead of duplicating it
                self.store.save(data)
                return Result(True)

        items.append({"name": name, "mandatory": False, "active": True})
        self.store.save(data)

        if self.defaults is not None:
            try:
                self.defaults.append_label(list_name, name)
            except DefaultsListNotFoundError:
                return Result(True, "Added. The sub-head list file could not be updated.")
        return Result(True)

    def remove_subhead(self, main_head: str, name: str) -> Result:
        """Hide a sub-head from the dropdown. Mandatory sub-heads cannot be removed (FR-9)."""
        list_name = MAIN_HEAD_LIST_NAME[main_head]
        data = self.store.load()
        for item in data[list_name]:
            if item["name"] == name:
                if item["mandatory"]:
                    return Result(False, "This Sub-Head cannot be removed.")
                item["active"] = False
                self.store.save(data)
                return Result(True)
        return Result(False, "This Sub-Head is not in the list.")

    @staticmethod
    def _name_error(name: str) -> str:
        """Return the message for an invalid name, or an empty string if the name is fine."""
        if not name:
            return "Enter a name."
        if len(name) > config.SUBHEAD_MAX_LENGTH:
            return f"Use up to {config.SUBHEAD_MAX_LENGTH} characters."
        if any(character in name for character in FORBIDDEN_CHARACTERS):
            return "Quotation marks and backslashes cannot be used."
        return ""
