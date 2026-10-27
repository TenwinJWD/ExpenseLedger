"""Data classes and fixed Main Head values (Architecture Section 4.1)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

# Main Head code -> label (PRD Section 4.1). The code is stored; the label is shown.
MAIN_HEADS = {
    "MH 1": "Treesa Agencies",
    "MH 2": "Daily Collection",
}
DEFAULT_MAIN_HEAD = "MH 2"  # Daily Collection is selected when the entry page opens (FR-10).

# Name of the list each Main Head uses in the sub-head file (PRD FR-8).
MAIN_HEAD_LIST_NAME = {
    "MH 1": "treesa",
    "MH 2": "daily",
}


@dataclass
class SubHead:
    """A sub-head in one Main Head's list. Removed sub-heads are inactive, never deleted (Rules 14)."""

    name: str
    mandatory: bool = False
    active: bool = True


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
