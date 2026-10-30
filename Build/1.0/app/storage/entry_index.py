"""A SQLite copy of the rows in the daily Excel files, so the lists do not have to open every workbook.

The Excel files stay the real data. This index is only a cache and can be deleted at any time: it is then
rebuilt from the files. For each file it remembers the modified time and size; a file whose stamp differs
(saved here, edited in Excel, copied in, or removed) is read again and the others are served from SQLite.

Rows are stored as parsed values. The Main Entry is kept as the name written in Excel, not its id, so a
Main Entry renamed later is still resolved by the caller at read time.
"""

import logging
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from app.core.models import Entry

SCHEMA_VERSION = 1
_logger = logging.getLogger("expenseledger")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS files (rel TEXT PRIMARY KEY, mtime_ns INTEGER NOT NULL, size INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS entries (
    rel TEXT NOT NULL REFERENCES files(rel) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    id TEXT NOT NULL, main_head TEXT NOT NULL, sub_head TEXT NOT NULL, entry_date TEXT NOT NULL,
    name TEXT NOT NULL, particulars TEXT NOT NULL, debit TEXT NOT NULL, credit TEXT NOT NULL,
    created_at TEXT NOT NULL, owner TEXT NOT NULL,
    PRIMARY KEY (rel, position)
);
CREATE INDEX IF NOT EXISTS entries_by_date ON entries (entry_date, id);
"""

Stamp = tuple[int, int]  # (modified time in ns, size in bytes)


class EntryIndex:
    """Rows per Excel file, keyed by the file's path relative to the data folder."""

    def __init__(self, database: Path | None, root: Path) -> None:
        """database None keeps the index in memory only (used by tests and as the fallback)."""
        self._root = str(root)
        self._connection = self._open(database)

    # ----- opening -----

    def _open(self, database: Path | None) -> sqlite3.Connection:
        if database is None:
            return self._connect(":memory:")
        try:
            return self._connect(database)
        except sqlite3.DatabaseError:
            _logger.warning("The entry index could not be read; rebuilding it")
            for suffix in ("", "-wal", "-shm", "-journal"):
                Path(str(database) + suffix).unlink(missing_ok=True)
            try:
                return self._connect(database)
            except sqlite3.DatabaseError:
                _logger.warning("The entry index cannot be used; keeping it in memory")
                return self._connect(":memory:")

    def _connect(self, database) -> sqlite3.Connection:
        connection = sqlite3.connect(database)
        try:
            return self._prepare(connection)
        except sqlite3.DatabaseError:
            connection.close()  # Windows will not delete a file that is still open
            raise

    def _prepare(self, connection: sqlite3.Connection) -> sqlite3.Connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA synchronous = NORMAL")  # the index can always be rebuilt, so it need not wait for the disk
        connection.executescript(_SCHEMA)
        stored = dict(connection.execute("SELECT key, value FROM meta"))
        if stored.get("schema") != str(SCHEMA_VERSION) or stored.get("root") != self._root:
            # A different app version or data folder: nothing in the index can be trusted.
            connection.execute("DELETE FROM files")
            connection.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)", [("schema", str(SCHEMA_VERSION)), ("root", self._root)])
            connection.commit()
        return connection

    def close(self) -> None:
        self._connection.close()

    # ----- syncing -----

    def changed_since(self, current: dict[str, Stamp]) -> list[str]:
        """The files that are new or whose stamp differs from the one saved. Files no longer there are dropped."""
        saved = {rel: (mtime, size) for rel, mtime, size in self._connection.execute("SELECT rel, mtime_ns, size FROM files")}
        with self._connection:
            for rel in saved.keys() - current.keys():
                self._connection.execute("DELETE FROM files WHERE rel = ?", (rel,))
        return [rel for rel, stamp in current.items() if saved.get(rel) != stamp]

    def replace_file(self, rel: str, stamp: Stamp, rows: list[Entry]) -> None:
        """Save the rows of one file together with its stamp, replacing what was there."""
        with self._connection:
            self._connection.execute("DELETE FROM files WHERE rel = ?", (rel,))  # cascades to its rows
            self._connection.execute("INSERT INTO files VALUES (?, ?, ?)", (rel, stamp[0], stamp[1]))
            self._connection.executemany(
                "INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (rel, position, row.id, row.main_head, row.sub_head, row.entry_date.isoformat(), row.name,
                     row.particulars, str(row.debit), str(row.credit), row.created_at.isoformat(), row.owner)
                    for position, row in enumerate(rows)
                ],
            )

    def forget_file(self, rel: str) -> None:
        """Drop a file from the index so the next read parses it again."""
        with self._connection:
            self._connection.execute("DELETE FROM files WHERE rel = ?", (rel,))

    # ----- reading -----

    def all_entries(self) -> list[Entry]:
        cursor = self._connection.execute(
            "SELECT id, main_head, sub_head, entry_date, name, particulars, debit, credit, created_at, owner "
            "FROM entries ORDER BY entry_date, id, owner"
        )
        return [
            Entry(
                id=row[0], main_head=row[1], sub_head=row[2], entry_date=date.fromisoformat(row[3]), name=row[4],
                particulars=row[5], debit=Decimal(row[6]), credit=Decimal(row[7]),
                created_at=datetime.fromisoformat(row[8]), owner=row[9],
            )
            for row in cursor
        ]
