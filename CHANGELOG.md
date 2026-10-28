# Changelog

All notable changes to Expense Ledger are recorded here (Rules 33). Dates use DD-Mon-YYYY.

## 1.0.1 – 28-Oct-2026

### Changed
- Release 1.0.1.

## Unreleased

### Changed
- New light theme and the Nunito font, from the mockups in `Design/design`. The sidebar now lists Dashboard, Main Entry (one item per Main Entry) and Transaction List; the user icon at the top right opens Change Password and Logout.
- The Expense Report is now the Transaction List, newest entry first. Its Monthly and Yearly Summary cards moved to the Dashboard.
- The Sub-Head choice on the entry form is called Transactions.

### Added
- Dashboard with the Monthly and Yearly Summary cards and a bar chart for each.
- Modify Fields page: add, rename, and remove Main Entries and the Transactions items of each Main Entry. The two fixed Main Heads are now just the starting Main Entries (`main_entries.json`); removed ones are hidden, and renamed ones keep their old rows.
- Upgrades: the version is set once, in `app/core/config.py`. `build.ps1` passes it to the exe properties, the MSI and the setup EXE.
- Saved files now carry a data version (`state.json`). On start-up the app backs up the login and sub-head files to `Backups` and runs any needed migrations before opening. Files saved by a newer version are refused instead of being changed.
- Update check: when `UPDATE_URL` in `config.py` is set, the app reads a small version file in the background and shows an "Update to X" button in the sidebar. It is off by default.
- All-users install: the setup program now installs once for every Windows user on the PC (it asks for administrator approval). A new `ExpenseLedger-<version>-AllUsers.msi` is built alongside the other two.
- Each user chooses the folder for their Excel ledger on the first run. The choice is saved in that user's own AppData, so every Windows user and every PC has a separate login, data and view. Version 1.0 users keep `Desktop\ExpenseLedger` without being asked.
- Uninstall from the Start Menu shortcut now asks for confirmation in a message-box window and shows the result the same way. There is no terminal window (`uninstall.ps1`; `uninstall.bat` only starts it).
- Tooltips on field headings, DD/MM/YYYY dates on screen, larger bold text, and a re-ordered Expense Report.

## 1.0.1 – 28-Oct-2026

### Changed
- Release 1.0.1.

## 1.0.0 – 27-Oct-2026

Developed by Tenwin James.

### Added
- Login with one account. The password is stored only as a PBKDF2 hash. Five wrong tries lock the login for 5 minutes, and the lock survives a restart.
- Create Account on first run.
- Change Password from the sidebar, with the same lock as login.
- Main Entry: Main Head (Treesa Agencies or Daily Collection, Daily Collection by default), sub-head dropdown, date (typed as DD-Mon-YYYY or DD/MM/YYYY, or picked from a calendar), name, particulars, debit, and credit. Submit is enabled only for a valid entry.
- Add (+) and remove (−) sub-heads. Removed sub-heads are hidden but kept for old entries.
- Saving each entry to a daily Excel file on the Desktop (`Desktop\ExpenseLedger\<YYYY>\<MM-Mon>\<DD-Mon-YYYY>.xlsx`). If the file is open in Excel, the entry stays in the form.
- Expense Report: search by name, particulars, or amount; filters for date range, Main Head, Sub-Head, name, particulars, and debit and credit amounts; totals; monthly and yearly summary cards; pagination (10, 25, or 50 rows per page).
- Inline edit of a row (Main Head and Sub-Head are dropdowns) and delete with confirmation.
- Developer signature, Tenwin James, in the sidebar, in the file properties, and in the installer.
- Setup program (`ExpenseLedger-Setup-1.0.0.exe`): a single file that shows the license and installs for the current user, with no administrator rights.
- Uninstall removes the login, so a reinstall asks for a new user and password. Entries and sub-heads are kept.
- Installer (`ExpenseLedger-1.0.0.msi`) with a choice of "Just me" (default, current user) or "Anyone who uses this computer" (all users). A desktop shortcut and a Start Menu entry are added. An uninstall file (`uninstall.bat`). Uninstall removes the program and keeps all data.

### Known limits
- The first Expense Report load takes about 4 seconds at 10,000 entries. Later loads are fast.
- Forgotten passwords cannot be reset in this version.
- Gradients in the design are shown as solid colours; Tk cannot draw them.
- The program is not digitally signed, so Windows may show a SmartScreen warning.
