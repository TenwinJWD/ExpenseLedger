"""Sub-head rules: add, rename, remove, and list the sub-heads for each Main Entry (PRD FR-8, FR-9, FR-11).

The entry form calls these "Transactions". Removing never deletes: the sub-head is set to inactive and
stays for old entries (Rules 14). Adding a name that was removed earlier brings that sub-head back instead
of making a copy. Renaming keeps the old name in former_names, so old rows are shown under the new name.
"""

from app.core import config
from app.core.models import SubHead, list_name_for
from app.core.validation import name_error
from app.services.auth_service import Result
from app.storage.defaults_store import DefaultsListNotFoundError, DefaultsStore
from app.storage.subhead_store import SubheadStore


class SubheadService:
    """The sub-head list of every Main Entry."""

    def __init__(self, store: SubheadStore, defaults: DefaultsStore | None = None) -> None:
        self.store = store
        self.defaults = defaults

    def items(self, main_head: str) -> list[SubHead]:
        """All sub-heads for a Main Entry, active and removed, in file order."""
        data = self.store.load()
        return [SubHead(**item) for item in data.get(list_name_for(main_head), [])]

    def active_names(self, main_head: str) -> list[str]:
        """Names for the dropdown: active sub-heads only, in order (FR-11)."""
        return [item.name for item in self.items(main_head) if item.active]

    def add_subhead(self, main_head: str, name: str) -> Result:
        """Add a sub-head to the list of the Main Entry (FR-8)."""
        name = name.strip()
        error = self._name_error(name)
        if error:
            return Result(False, error)

        list_name = list_name_for(main_head)
        data = self.store.load()
        items = data.setdefault(list_name, [])
        for item in items:
            if item["name"].lower() == name.lower():
                if item["active"]:
                    return Result(False, "This Sub-Head already exists.")
                item["active"] = True  # bring back a removed sub-head instead of duplicating it
                self.store.save(data)
                return Result(True)
            if name.lower() in (former.lower() for former in item.get("former_names", [])):
                return Result(False, "This name was used before by another Sub-Head. Please choose a different name.")

        items.append({"name": name, "mandatory": False, "active": True})
        self.store.save(data)

        if self.defaults is not None:
            try:
                self.defaults.append_label(list_name, name)
            except DefaultsListNotFoundError:
                return Result(True, "Added. The sub-head list file could not be updated.")
        return Result(True)

    def rename_subhead(self, main_head: str, old_name: str, new_name: str) -> Result:
        """Change a sub-head's name. Old rows keep the name they were saved with and are shown under the new one."""
        new_name = new_name.strip()
        error = self._name_error(new_name)
        if error:
            return Result(False, error)
        data = self.store.load()
        items = data.get(list_name_for(main_head), [])
        target = next((item for item in items if item["name"] == old_name), None)
        if target is None:
            return Result(False, "This Sub-Head is not in the list.")
        if target["name"] == new_name:
            return Result(True)
        for item in items:
            taken = [item["name"].lower()] + [former.lower() for former in item.get("former_names", [])]
            if item is not target and new_name.lower() in taken:
                return Result(False, "This Sub-Head already exists.")
        former = [old for old in target.get("former_names", []) if old.lower() != new_name.lower()]
        target["former_names"] = former + [old_name]
        target["name"] = new_name
        self.store.save(data)
        return Result(True)

    def remove_subhead(self, main_head: str, name: str) -> Result:
        """Hide a sub-head from the dropdown. Mandatory sub-heads cannot be removed (FR-9)."""
        data = self.store.load()
        for item in data.get(list_name_for(main_head), []):
            if item["name"] == name:
                if item["mandatory"]:
                    return Result(False, "This Sub-Head cannot be removed.")
                item["active"] = False
                self.store.save(data)
                return Result(True)
        return Result(False, "This Sub-Head is not in the list.")

    def renamed_map(self, main_head: str) -> dict[str, str]:
        """Old name -> current name, for every sub-head of the Main Entry that was renamed."""
        names = {}
        for item in self.items(main_head):
            for former in item.former_names:
                names.setdefault(former, item.name)
        for item in self.items(main_head):
            names.pop(item.name, None)  # a name in use today is never an old name
        return names

    @staticmethod
    def _name_error(name: str) -> str:
        return name_error(name, config.SUBHEAD_MAX_LENGTH)
