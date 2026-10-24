# PRD: Expense Ledger (Windows Desktop App)

Version: 1.1
Status: Draft (revised from Customer Requirement Specification CX-REQ-2026-v1.0)
Owner: [Your Name]

---

## 1. Purpose

A Windows desktop app that records daily collection and expense entries under two main heads, keeps every entry in Excel files organized by date, and shows the entries in an Expense Report with search, date range and column filters, inline editing, totals, and monthly and yearly summary cards.

The app is installed separately on each device. Each installation has its own local data and its own login.

---

## 2. Target User

- Primary: a single person (or small office) who records daily entries on a Windows 10 PC.
- Skill level of the builder: beginner. The code must stay simple, readable, and well-commented.

---

## 3. Goals

1. Record each daily entry quickly, with a main head, a sub-head, and debit or credit amounts.
2. Let the user add and remove sub-heads without editing code.
3. Show all recorded entries in an Expense Report that can be filtered by date range, main head, sub-head, and each column, searched by name, particulars, or amount, and summarized by month and by year.
4. Let the user correct an entry in place and delete it only after confirmation.
5. Store every entry in a readable Excel file, organized by date.
6. Protect the app with a login.
7. Ship as a standalone `.exe` and as an `.msi` installer.

---

## 4. Main Heads and Sub-Heads

### 4.1 Main Heads (fixed in v1)

| Code | Label | Default |
|------|-------|---------|
| MH 1 | Treesa Agencies | No |
| MH 2 | Daily Collection | Yes (selected when the entry screen opens) |

### 4.2 Sub-Heads (managed by the user)

- Sub-heads are the choices in the Sub-Head dropdown. They are not fixed in code.
- Seed sub-heads (from the specification, labels as given): Primary Sub Head, Secondary Sub Head, Auxiliary Sub Head, Special Collection.
- The user can add a sub-head with the **+** button and remove one with the **−** button (FR-8, FR-9).
- The default sub-head lists are kept in `%APPDATA%\ExpenseLedger\Defaults\default.js` (a copy of the seed file is installed with the program): `treesa` for MH 1 and `daily` for MH 2. Every extra sub-head the user adds is also written into the list of the selected Main Head in that file (FR-8).
- A sub-head marked as mandatory cannot be removed. Which sub-heads are mandatory is still to be confirmed (see Section 10).

---

## 5. Non-Goals (Version 1)

- No cloud sync or website (planned for a later version).
- No multi-user access on one device (planned for a later version).
- No bank integration.
- No dashboard with income, expense, or balance totals (moved to Future Scope; not in the specification).
- No budgets, reminders, or recurring entries.
- No mobile app.
- No CSV or PDF export (PDF is in Future Scope).

---

## 6. Functional Requirements

### 6.1 Login
- FR-1: The app opens on a login screen before any data is shown.
- FR-2: On first run, the user creates one account (username and password).
- FR-3: Passwords are never stored as plain text.
- FR-4: After 5 failed attempts, the login is locked for 5 minutes.
- FR-5: A "Logout" option is available on every page.

### 6.2 Navigation
- FR-6: After login, the main window shows a sidebar with: Main Entry, Expense Report, Logout.
- FR-7: Main Entry is the default page after login.

### 6.3 Main Entry (Sub-Heads and Entry Form)
- FR-8: **Add sub-head.** Clicking **+** opens a popup where the user types a new sub-head name. Duplicates (case-insensitive) are rejected. A new sub-head is also written to `%APPDATA%\ExpenseLedger\Defaults\default.js`, in the `treesa` list for MH 1 or the `daily` list for MH 2, as `{ label, value }`.
- FR-9: **Remove sub-head.** Clicking **−** removes a non-mandatory sub-head from the dropdown. Removing it does not change old entries (see Rule 14).
- FR-10: **Main Head.** The Main Head selector shows MH 1 (Treesa Agencies) and MH 2 (Daily Collection). MH 2 is selected when the screen opens.
- FR-11: **Sub-Head dropdown.** Shows the first item "-Select-" and then the active sub-heads. It is set to "-Select-" when the screen opens and stays there until the user chooses a sub-head.
- FR-12: **Field enabling.** The Date, Name, Particulars, Debit, and Credit fields are disabled until the Sub-Head is set to something other than "-Select-". The Submit button is disabled until the form is valid (FR-14).
- FR-13: **Form fields:**
  - Date: DD-Mon-YYYY (example: 20-Oct-2026). The user can type a date or pick it from a date picker. Typing `20/10/2026` is accepted and shown as `20-Oct-2026`. Required.
  - Name: text, up to 100 characters. Required.
  - Particulars: text, up to 200 characters. Required.
  - Debit: amount, 0.00 or more, up to 2 decimal places. Default 0.00. Required.
  - Credit: amount, 0.00 or more, up to 2 decimal places. Default 0.00. Required.
- FR-14: **Submit rule.** Submit is enabled only when: a Sub-Head other than "-Select-" is chosen, every field has a valid value, and Debit or Credit is greater than 0.00 (Section 10, assumption A3).
- FR-15: **Submit.** Saves the entry to the correct Excel file (Section 6.5). After a successful save, the transaction fields are cleared; Main Head and Sub-Head stay as they were. A confirmation message is shown.
- FR-16: **Errors.** Each error appears under its field. Errors do not block typing.
- FR-17: **Clear.** Resets the transaction fields. Main Head and Sub-Head are not changed.

### 6.4 Expense Report
- FR-18: The report shows all submitted entries, oldest first. Columns: Date, Main Head, Sub-Head, Name, Particulars, Debit, Credit, Actions. Main Head shows the name (Treesa Agencies or Daily Collection), not the code.
- FR-18a: **Pagination.** The table shows 10 rows per page by default. The user can choose 10, 25, or 50 rows per page. Prev and Next move between pages, and page number buttons jump to a page. Applying or clearing filters, or changing the rows per page, returns to page 1. The line "Showing x to y of z entries" shows the current range. The totals row covers all matching rows, not only the current page.
- FR-19: **Filters.** Clicking **Filter Report** applies all of the following; **Clear Filters** resets them.
  - Date Range: All Dates (default), This Month, Last Month, This Year, or Custom Range with From and To (DD-Mon-YYYY or DD/MM/YYYY). Relative ranges use the current date (assumption A11).
  - Main Head: All Main Heads (default), Treesa Agencies, Daily Collection.
  - Sub-Head: All Sub-Heads (default), or one sub-head. The list follows the Main Head filter.
  - Name and Particulars: contains the typed text (not case-sensitive).
  - Debit From / Debit To and Credit From / Credit To: amount range, inclusive, up to 2 decimals.
- FR-19a: **Search.** One search box matches the Name or Particulars text, or an amount. Typing `2500`, `2500.00`, or `2,500` finds 2,500.00. Search is combined with the other filters.
- FR-20: **Totals row.** Shows the total Debit and total Credit of the rows currently shown (after filters).
- FR-21: **Amount in words.** Removed in version 1.1. The totals are shown as numbers only. Assumption A6 is closed.
- FR-21a: **Monthly Summary (6 cards).** For the month selected in the Monthly Summary selector (default: the latest month that has entries):
  1. Debit (Total Amount): total of all Debit.
  2. Most Debited Sub-Head: the sub-head with the highest total Debit, with that amount.
  3. Least Debited Sub-Head: the sub-head with the lowest total Debit, with that amount.
  4. Credit (Total Amount): total of all Credit.
  5. Most Credited Sub-Head: the sub-head with the highest total Credit, with that amount.
  6. Least Credited Sub-Head: the sub-head with the lowest total Credit, with that amount.
- FR-21b: **Yearly Summary (6 cards).** The same six cards for the year selected in the Yearly Summary selector (default: the latest year that has entries).
- FR-21c: The summary cards ignore the report filters. Only sub-heads with at least one entry in the period are ranked. Ties are broken by sub-head name (assumption A11).
- FR-22: **Edit.** Clicking the pencil icon turns the row's Date, Name, Particulars, Debit, and Credit into input fields. Main Head and Sub-Head are also dropdowns in inline edit (customer change request). The Sub-Head list follows the chosen Main Head, and a Sub-Head must be selected before the row can be saved. The icon changes to a checkmark. Clicking the checkmark saves the change with the same validation as FR-13 and FR-14, and the icon changes back to a pencil.
- FR-23: **Delete.** Clicking the delete icon opens a popup: "Are you sure you want to delete this row?". The row is deleted only after the user confirms.

### 6.5 Data Storage in Excel
- FR-24: Each day with entries has its own Excel file.
- FR-25: File location pattern (the day is the entry's date):
  ```
  <DataFolder>\<YYYY>\<MM-Mon>\<DD-Mon-YYYY>.xlsx
  Example: Documents\ExpenseLedger\2026\10-Oct\20-Oct-2026.xlsx
  ```
- FR-26: Each file has one sheet named "Entries" with these columns:
  ID | Main Head | Sub Head | Date | Name | Particulars | Debit | Credit | Created At
- FR-27: The file is created automatically the first time an entry is saved for that day.
- FR-28: Dates inside the file use DD-Mon-YYYY.
- FR-29: If an Excel file is open in Excel when saving, the app shows a clear message and keeps the entry in the form.
- FR-30: If an entry's date is changed in the Expense Report, the row moves to the Excel file for the new date.
- FR-31: Sub-head names and main head codes are stored with each entry, so old entries still show their original sub-head after the sub-head is removed.

### 6.6 Date Format (Global Rule)
- FR-32: DD-Mon-YYYY is used everywhere on screen, in Excel files, in folder names, and in logs.
- FR-33: Accepted typed input: DD-Mon-YYYY (`20-Oct-2026`) and DD/MM/YYYY (`20/10/2026`). Both are converted to DD-Mon-YYYY when accepted.

### 6.7 Developer Signature
- FR-34: The developer's name, **Tenwin James**, is shown in the app as a signature: as a footer at the bottom of the sidebar on every page, and in the About text of the login screen.
- FR-35: The same name is set as the author in the program's file properties (`ExpenseLedger.exe`, Company and Copyright) and as the publisher in the `.msi` installer (Add/Remove programs shows it as the publisher).
- FR-36: The name comes from one constant (`APP_AUTHOR` in `config.py`), so it is changed in one place only.

### 6.8 Change Password
- FR-37: A **Change Password** button is in the sidebar, above Logout, on every page. It is not a page; it opens a popup (PRD FR-6 still lists only Main Entry, Expense Report, and Logout as pages).
- FR-38: The popup asks for the **current password**, the **new password**, and the **new password again**. Save is disabled until all three are filled.
- FR-39: The current password must be correct. A wrong current password counts toward the same 5-attempt lock as login (FR-4), and it shows how many tries are left.
- FR-40: The new password must be at least 8 characters (FR-2), must differ from the current password, and must match the confirmation.
- FR-41: On success, the new password replaces the old one (only its hash is stored, FR-3), the failed-attempt count is reset, the popup closes, and a message "Password changed." is shown. The user stays logged in.

---

## 7. Non-Functional Requirements

- NFR-1 Platform: Windows 10 (64-bit) and later.
- NFR-2 Python version: 3.11 or newer for development.
- NFR-3 Performance: Saving an entry and loading the Expense Report should each take less than 1 second for up to 10,000 entries.
- NFR-4 Reliability: No entry is lost if the app closes unexpectedly while saving.
- NFR-5 Security: Passwords are hashed with PBKDF2 (standard library). Login data is stored in the user's AppData folder, not in the project or the Excel data folder.
- NFR-6 Usability: Every page must be usable with mouse and keyboard (Tab key moves between fields, Enter submits the form when it is enabled).
- NFR-7 Maintainability: Code is split into layers (see Architecture.md) so the storage layer can be replaced later.
- NFR-8 Fonts: The app uses font files bundled in its program folder. They are loaded for this program only, with no system-wide install and no administrator rights. Each font file must allow redistribution (the SIL Open Font License is acceptable). If a font file is missing, the app falls back to Segoe UI and shows no error.
- NFR-9 No file locations on screen: No screen, message, popup, or tooltip shows a folder, AppData path, or file name. Messages refer to things the user knows, such as a date or a name. Locations are documented only in the planning documents and the user guide.

---

## 8. Deliverables

| # | Deliverable | Format |
|---|-------------|--------|
| 1 | Expense Ledger application | Source code (Python) |
| 2 | Standalone program | `ExpenseLedger.exe` (PyInstaller) |
| 3 | Installer | `ExpenseLedger-1.0.0.msi` |
| 4 | Uninstall file | `uninstall.bat` (removes the program, keeps user data, asks for confirmation; also installed to the program folder) |
| 5 | Documentation | PRD.md, Architecture.md, Rules.md, Design.md, Tasks.md |

---

## 9. Future Scope (Version 2+)

- Dashboard with total debit, total credit, and balance for a period.
- FastAPI backend with PostgreSQL database.
- Next.js website as a second frontend.
- Multiple users with separate accounts and data.
- Sync between desktop app and website.
- Reports export (PDF).

Version 1 must be built so that the storage layer can be swapped for PostgreSQL without rewriting the screens.

---

## 10. Assumptions and Open Questions

These were not stated in the specification. Each one needs a yes or no from the customer before the related task is built.

| # | Topic | Assumption used in this document | Status |
|---|-------|----------------------------------|--------|
| A1 | Login and Excel storage | Kept from the earlier PRD, because the specification does not mention them | Confirm |
| A2 | Dashboard | Removed from v1 (not in the specification) and moved to Future Scope | Confirm |
| A3 | Debit and Credit rule | At least one of Debit or Credit must be greater than 0.00 | Confirm |
| A4 | Mandatory sub-heads | None are mandatory; all four seed sub-heads can be removed | Confirm which are mandatory |
| A5 | Sub-head removal | Removing a sub-head hides it from the dropdown and keeps it on old entries (no data loss) | Confirm |
| A6 | Amount in words | Removed in v1.1 (customer asked to remove the words lines from the Expense Report) | Closed |
| A7 | Name and particulars length | Name up to 100 characters; particulars up to 200 characters | Confirm |
| A8 | Report order and main head filter default | Oldest first; main head filter defaults to All Main Heads | Confirm |
| A9 | Clear after submit | Transaction fields cleared; main head and sub-head kept | Confirm |
| A10 | Sub-Head dropdown under Daily Collection | Enabled the same way as under Treesa Agencies (customer correction overrides the specification's "disabled if Daily active") | Confirmed by customer |
| A11 | Report date range and summary cards | Relative ranges (This/Last Month, This Year) use the current date. Monthly and yearly cards use their own selectors, default to the latest month/year with entries, and rank only sub-heads with entries in the period; ties are broken by name. Search matches amounts by digits (`2500` finds 2,500.00). | Confirm |

---

## 11. Success Criteria

- The user can add a daily entry (main head, sub-head, date, name, particulars, amount) in under 30 seconds.
- Submit stays disabled until the sub-head and all fields are valid.
- Typing `20/10/2026` shows `20-Oct-2026` in the form and in the report.
- A new sub-head added with **+** appears in the dropdown right away and is written to the matching list in `%APPDATA%\ExpenseLedger\Defaults\default.js`.
- Expense Report totals match the sum of the Excel files.
- Typing `2500` in the search box finds the entries with 2,500.00, and the date range, main head, and sub-head filters narrow the table as expected.
- The monthly and yearly summary cards match a manual check of the entries for that month or year.
- The MSI installs and uninstalls cleanly on a Windows 10 machine without Python.
