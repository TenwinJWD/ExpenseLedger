"""Logging and crash handling.

Writes the plain-text log (paths.log_file) with dates as DD-Mon-YYYY (PRD FR-32). Any error the
program does not handle is written to the log with its traceback, and the user sees a short
message with no file names or folders (PRD NFR-9).
"""

import logging
import sys
import tkinter
from logging.handlers import RotatingFileHandler
from tkinter import messagebox

from app.core import paths

LOG_NAME = "expenseledger"
MAX_BYTES = 512 * 1024
BACKUP_COUNT = 2
CRASH_MESSAGE = "Something went wrong. Your saved entries are safe. Please close and open Expense Ledger again."

_logger = logging.getLogger(LOG_NAME)


def setup() -> None:
    """Start logging to the log file and catch errors nobody handled. Never stops the app."""
    try:
        handler = RotatingFileHandler(
            paths.log_file(), maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%d-%b-%Y %H:%M:%S"))
        _logger.addHandler(handler)
        _logger.setLevel(logging.INFO)
    except OSError:
        _logger.addHandler(logging.NullHandler())  # no log is better than no app
    sys.excepthook = _on_error
    tkinter.Tk.report_callback_exception = _on_tk_error
    _logger.info("Expense Ledger started")


def _on_error(exc_type, exc, tb) -> None:
    _logger.error("Unhandled error", exc_info=(exc_type, exc, tb))
    sys.__excepthook__(exc_type, exc, tb)


def _on_tk_error(_widget, exc_type, exc, tb) -> None:
    _logger.error("Error in a screen action", exc_info=(exc_type, exc, tb))
    try:
        messagebox.showerror("Expense Ledger", CRASH_MESSAGE)
    except tkinter.TclError:
        pass
