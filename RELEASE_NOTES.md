# Expense Ledger 1.0.0

First release of Expense Ledger, a Windows desktop app for recording daily collection and expense entries in Excel files and reviewing them in an Expense Report.

Developed by Tenwin James.

## Downloads

- `ExpenseLedger-Setup-1.0.0.exe`: single setup program. Shows the license and installs for the current user, with no administrator rights.
- `ExpenseLedger-1.0.0.msi`: installer with a choice of "Just me" (default) or "Anyone who uses this computer". Adds a desktop shortcut and a Start Menu entry.

## What's new

- **Login:** one account, created on first run. The password is stored only as a PBKDF2 hash. Five wrong tries lock the login for 5 minutes, and the lock survives a restart.
- **Change Password** from the sidebar, with the same lock as login.
- **Main Entry:** Main Head (Treesa Agencies or Daily Collection), sub-head, date (typed as `DD-Mon-YYYY` or `DD/MM/YYYY`, or picked from a calendar), name, particulars, debit, and credit. Submit is enabled only for a valid entry.
- **Sub-heads:** add (+) and remove (−). Removed sub-heads are hidden but kept for old entries.
- **Excel storage:** each entry is saved to a daily Excel file. If the file is open in Excel, the entry stays in the form.
- **Expense Report:** search by name, particulars, or amount; filters for date range, Main Head, Sub-Head, name, particulars, and debit and credit amounts; totals; monthly and yearly summary cards; pagination (10, 25, or 50 rows per page).
- **Edit and delete** rows in the report, with confirmation before deleting.
- **Uninstall** removes the program and the login. Entries and sub-heads are kept, and a reinstall asks for a new user and password.

## Known limits

- The first Expense Report load takes about 4 seconds at 10,000 entries. Later loads are fast.
- Forgotten passwords cannot be reset in this version.
- Gradients in the design are shown as solid colours; Tk cannot draw them.
- The installers are not yet digitally signed, so Windows may show a SmartScreen warning. Code signing is being set up through the SignPath Foundation.

## Privacy

All data stays on your computer. The app has no network access and no telemetry. See [PRIVACY.md](PRIVACY.md).

## License

MIT. See [LICENSE](LICENSE).
