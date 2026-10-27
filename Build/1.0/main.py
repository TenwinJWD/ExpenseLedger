"""Start the Expense Ledger app.

Start-up order (Architecture 6.1): prepare the sub-head files, create the account if
none exists (otherwise log in), then open the main window. Only this file knows where
the files live.
"""

from tkinter import messagebox

import customtkinter as ctk

from app.core import app_log, paths
from app.services.auth_service import AuthService
from app.services.entry_service import EntryService
from app.services.subhead_service import SubheadService
from app.storage.account_store import AccountStore
from app.storage.excel_store import ExcelStore
from app.storage.defaults_store import DefaultsListNotFoundError, DefaultsStore
from app.storage.migrations import DataTooNewError, MigrationContext, MigrationError, run as run_migrations
from app.storage.subhead_store import SubheadStore
from app.ui.main_window import App


def _stop(message: str) -> None:
    messagebox.showerror("Expense Ledger", message)


def main() -> None:
    app_log.setup()
    ctk.set_appearance_mode("dark")

    # Bring the saved files up to this version's format (backed up first). Stop rather than risk the data.
    try:
        run_migrations(MigrationContext(app_data=paths.app_data_dir(), data_dir=paths.data_dir()))
    except DataTooNewError:
        _stop("These files were saved by a newer version of Expense Ledger. Please install the latest version.")
        return
    except MigrationError:
        _stop("Expense Ledger could not update your saved files. Nothing was changed. Please contact the developer.")
        return

    defaults = DefaultsStore(paths.default_list_file())
    try:
        defaults.ensure_copy(paths.seed_default_file())
    except DefaultsListNotFoundError:
        defaults = None  # the app still works; only the list file is not updated

    auth = AuthService(AccountStore(paths.account_file()))
    subheads = SubheadService(SubheadStore(paths.subheads_file()), defaults)
    entries = EntryService(ExcelStore(paths.data_dir()))
    app = App(auth, subheads, entries)
    app.mainloop()


if __name__ == "__main__":
    main()
