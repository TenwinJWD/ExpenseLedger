"""Start the Daily Fresh app.

Start-up order (Architecture 6.1): prepare the sub-head files, create the account if
none exists (otherwise log in), then open the main window. Only this file knows where
the files live.
"""

from tkinter import messagebox

import customtkinter as ctk

from app.core import app_log, config, fonts, paths, theme
from app.services.auth_service import AuthService
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.services.subhead_service import SubheadService
from app.storage.account_store import AccountStore
from app.storage.excel_store import ExcelStore
from app.storage.main_entry_store import MainEntryStore
from app.storage.defaults_store import DefaultsListNotFoundError, DefaultsStore
from app.storage.migrations import DataTooNewError, MigrationContext, MigrationError, run as run_migrations
from app.storage.subhead_store import SubheadStore
from app.ui.data_folder_dialog import ask_data_folder
from app.ui.main_window import App


def _choose_data_folder() -> bool:
    """Make sure this Windows user has a usable folder for the Excel files. False when they cancel.

    A new user is asked on the first run. A user who had version 1.0 (login but no choice saved) keeps
    Desktop\\ExpenseLedger without a question. A chosen folder that has gone missing is asked again.
    """
    saved = paths.saved_data_dir()
    if saved is not None and not paths.folder_problem(saved):
        return True
    if saved is None and paths.account_file().exists():
        paths.save_data_dir(paths.default_data_dir())
        return True
    notice = "" if saved is None else "The folder you chose before is not available. Please choose a folder."
    chosen = ask_data_folder(saved or paths.default_data_dir(), notice)
    if chosen is None:
        return False
    paths.save_data_dir(chosen)
    return True


def _stop(message: str) -> None:
    messagebox.showerror("Daily Fresh", message)


def main() -> None:
    app_log.setup()
    ctk.set_appearance_mode("light")
    ctk.set_widget_scaling(config.UI_SCALE)
    ctk.set_window_scaling(config.UI_SCALE)
    if not fonts.load_fonts():
        theme.FONT_FAMILY = theme.FALLBACK_FONT_FAMILY

    if not _choose_data_folder():
        return

    # Bring the saved files up to this version's format (backed up first). Stop rather than risk the data.
    try:
        run_migrations(MigrationContext(app_data=paths.app_data_dir(), data_dir=paths.data_dir()))
    except DataTooNewError:
        _stop("These files were saved by a newer version of Daily Fresh. Please install the latest version.")
        return
    except MigrationError:
        _stop("Daily Fresh could not update your saved files. Nothing was changed. Please contact the developer.")
        return

    defaults = DefaultsStore(paths.default_list_file())
    try:
        defaults.ensure_copy(paths.seed_default_file())
    except DefaultsListNotFoundError:
        defaults = None  # the app still works; only the list file is not updated

    auth = AuthService(AccountStore(paths.account_file()))
    subheads = SubheadService(SubheadStore(paths.subheads_file()), defaults)
    main_entries = MainEntryService(MainEntryStore(paths.main_entries_file()))
    entries = EntryService(ExcelStore(paths.data_dir(), main_entries), subheads)
    app = App(auth, main_entries, subheads, entries)
    app.mainloop()


if __name__ == "__main__":
    main()
