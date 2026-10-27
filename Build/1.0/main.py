"""Start the Expense Ledger app.

Start-up order (Architecture 6.1): prepare the sub-head files, create the account if
none exists (otherwise log in), then open the main window. Only this file knows where
the files live.
"""

import customtkinter as ctk

from app.core import app_log, paths
from app.services.auth_service import AuthService
from app.services.entry_service import EntryService
from app.services.subhead_service import SubheadService
from app.storage.account_store import AccountStore
from app.storage.excel_store import ExcelStore
from app.storage.defaults_store import DefaultsListNotFoundError, DefaultsStore
from app.storage.subhead_store import SubheadStore
from app.ui.main_window import App


def main() -> None:
    app_log.setup()
    ctk.set_appearance_mode("dark")

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
