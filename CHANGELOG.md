# Changelog

All notable changes to Expense Ledger are recorded here (Rules 33). Dates use DD-Mon-YYYY.

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
