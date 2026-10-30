"""Data classes and the starting Main Entries (Architecture Section 4.1)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

# The two Main Entries every install starts with (PRD Section 4.1). The user can rename, add, and remove
# them on the Modify Fields page. The id is stored with each entry; the name is shown and saved in Excel.
DEFAULT_MAIN_ENTRIES = (
    {"id": "MH 1", "name": "Treesa Agencies"},
    {"id": "MH 2", "name": "Daily Collection"},
)
DEFAULT_MAIN_HEAD = "MH 2"  # Daily Collection is the first one open when the entry page opens (FR-10).


# Name of the sub-head list the first two Main Entries use in subheads.json (PRD FR-8). A new Main Entry
# uses its id in lower case without spaces ("MH 3" -> "mh3").
_FIRST_LIST_NAMES = {"MH 1": "treesa", "MH 2": "daily"}


def list_name_for(main_head: str) -> str:
    return _FIRST_LIST_NAMES.get(main_head) or main_head.lower().replace(" ", "")


@dataclass
class MainEntry:
    """A Main Entry (a sidebar item). Removed ones are inactive, never deleted, so old rows keep their name."""

    id: str
    name: str
    active: bool = True
    former_names: list[str] = field(default_factory=list)


@dataclass
class SubHead:
    """A sub-head in one Main Head's list. Removed sub-heads are inactive, never deleted (Rules 14)."""

    name: str
    mandatory: bool = False
    active: bool = True
    former_names: list[str] = field(default_factory=list)  # old names after a rename; old rows still use them


@dataclass
class Entry:
    """One ledger row (PRD FR-26)."""

    id: str
    main_head: str
    sub_head: str
    entry_date: date
    name: str
    particulars: str
    debit: Decimal
    credit: Decimal
    created_at: datetime = field(default_factory=datetime.now)
    owner: str = ""  # the user whose file the row is in; empty means a file from before usernames were added

    @property
    def key(self) -> tuple[str, str]:
        """Two users can both have E20261020-001, so a row is told apart by owner and ID together."""
        return (self.owner.lower(), self.id)
