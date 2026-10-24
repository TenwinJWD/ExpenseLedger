# Architecture: Expense Ledger (Version 1.1)

Version: 1.1
Status: Draft
Read after: PRD.md

---

## 1. Overview

The app is a single Python desktop program with a window built using CustomTkinter. It has four layers. Each layer talks only to the layer directly below it.

```
+----------------------------------------------+
|  UI layer      (screens, widgets, popups)    |   app/ui/
+----------------------------------------------+
|  Service layer (entries, sub-heads, report)  |   app/services/
+----------------------------------------------+
|  Storage layer (Excel files, JSON files)     |   app/storage/
+----------------------------------------------+
|  Core          (config, paths, dates, money) |   app/core/
+----------------------------------------------+
```

Why this shape (PRD NFR-7): the screens never open an Excel file. If the data later moves to PostgreSQL (Version 2), only the `storage/` layer changes.

---

## 2. Technology Choices

| Need | Choice | Reason |
|------|--------|--------|
| Language | Python 3.11+ | PRD NFR-2 |
| Window and widgets | CustomTkinter | PRD |
| Date picker | tkcalendar (`DateEntry`) | Ready-made calendar popup; PRD FR-13 |
| Excel read and write | openpyxl | Pure Python, no Excel install needed |
| Password hashing | `hashlib.pbkdf2_hmac` (standard library) | PRD NFR-5, no extra package |
| Settings and sub-heads | JSON files (standard library `json`) | Easy to read and edit by hand |
| Money math | `decimal.Decimal` | Avoids float rounding errors |
| Tests | `pytest` (dev only) | Simple syntax for beginners |
| EXE build | PyInstaller | PRD deliverable 2 |
| MSI build | WiX Toolset v4 (recommended) | Creates a real `.msi`; final choice is made in task T9.3 |

Runtime dependencies (in `requirements.txt`): `customtkinter`, `openpyxl`, `tkcalendar`.
Dev dependencies (in `requirements-dev.txt`): `pytest`, `pyinstaller`.

A new library needs an update to this section first (see Rules.md).

---

## 3. Folder Structure

```
ExpenseLedger/
├── main.py                       Entry point: starts the app
├── requirements.txt              Runtime packages
├── requirements-dev.txt          Test and build packages
├── .gitignore                    Ignores venv, build, dist, and user data
├── Roadmap/                      All planning documents (PRD, Architecture, ...)
├── installer/
│   ├── uninstall.bat             Removes the installed program; keeps user data
│   └── (WiX installer files)     Added in Phase 9 (T9.4)
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py             App name, version, lock settings, field limits, seed sub-heads
│   │   ├── paths.py              Locations of AppData and the Excel data folder
│   │   ├── fonts.py              Loads the bundled font files for this program only (NFR-8)
│   │   ├── fonts/                Bundled font files (.ttf), shipped with the program
│   │   ├── dates.py              DD-Mon-YYYY format, parsing of DD/MM/YYYY, month names
│   │   ├── money.py              Parse and format amounts
│   │   ├── models.py             Entry, SubHead data classes; MAIN_HEADS constant
│   │   └── validation.py         Rules for the entry form and the report edit
│   ├── storage/
│   │   ├── excel_store.py        Read, write, update, and delete rows in daily .xlsx files
│   │   ├── subhead_store.py      Read and write sub-heads (JSON)
│   │   ├── defaults_store.py     Append added sub-heads to AppData Defaults\default.js
│   │   └── account_store.py      Read and write the login file (JSON)
│   ├── services/
│   │   ├── auth_service.py       Create account, check password, lockout
│   │   ├── password_hash.py      PBKDF2 hashing and checking
│   │   ├── entry_service.py      Save, update, and delete entries; load for the report
│   │   ├── subhead_service.py    Add and remove sub-heads (duplicate and mandatory checks)
│   │   └── report_service.py     Filter, search, sort, total, and summarize entries for the report
│   └── ui/
│       ├── main_window.py        Window, sidebar, page switching
│       ├── login_view.py         Login screen
│       ├── create_account_view.py First-run account screen
│       ├── main_entry_view.py    Main Entry page (main head, sub-head, form)
│       ├── subhead_popup.py      Add sub-head popup (+) and remove confirmation (−)
│       ├── expense_report_view.py Expense Report page (search, filters, summary cards, table, totals)
│       ├── confirm_popup.py      "Are you sure you want to delete this row?"
│       └── widgets.py            Shared styled widgets (cards, buttons, messages)
└── tests/
    ├── test_dates.py
    ├── test_money.py
    ├── test_validation.py
    ├── test_password_hash.py
    ├── test_auth_service.py
    ├── test_subhead_service.py
    ├── test_excel_store.py
    └── test_report_service.py
```

Build outputs (not in Git): `build/`, `dist/`, `installer/output/`.

---

## 4. Layer Responsibilities

### 4.1 Core (`app/core/`)
- No UI code and no file writes.
- `config.py` holds every fixed value: app name, version `1.0.0`, `APP_AUTHOR = "Tenwin James"` (PRD FR-36), `MAX_LOGIN_ATTEMPTS = 5`, `LOCK_MINUTES = 5`, `NAME_MAX_LENGTH = 100`, `PARTICULARS_MAX_LENGTH = 200`, `SUBHEAD_MAX_LENGTH = 40`, `MIN_PASSWORD_LENGTH = 8`, and the seed sub-heads.
- `fonts.py` registers each `.ttf` file in the `fonts/` folder for this process only, with the Windows call `AddFontResourceEx` and the `FR_PRIVATE` flag, through `ctypes`. It runs once at startup, before any window is created. It needs no admin rights and installs nothing system-wide. If a file cannot be loaded, it logs the problem to `app.log` and the app uses Segoe UI.
- `paths.py` returns:
  - Login and sub-head files: `%APPDATA%\ExpenseLedger\`
  - Excel data: `Documents\ExpenseLedger\` (PRD FR-25)
- `dates.py` is the only place that formats or parses dates (PRD FR-32). It:
  - formats a date as `20-Oct-2026`;
  - parses typed text in `DD-Mon-YYYY` or `DD/MM/YYYY` (PRD FR-33);
  - uses its own month name list, not `strftime("%b")`, because `%b` depends on the Windows language setting.
- `money.py`:
  - parses typed text into `Decimal` with at most 2 decimal places (commas are allowed, for example `2,500.00`);
  - formats amounts as `2,500.00`.
  - Amount in words is not used in v1.1 (PRD FR-21).
- `models.py`:
  - `MAIN_HEADS` is a fixed list of `(code, label)` pairs: `("MH 1", "Treesa Agencies")`, `("MH 2", "Daily Collection")`.
  - `Entry` fields: id, main_head_code, sub_head_name, date, name, particulars, debit (Decimal), credit (Decimal), created_at.
  - `SubHead` fields: name, mandatory flag, active flag.
- `validation.py` returns a dictionary of field name to error message. It also returns whether the Submit button should be enabled (FR-14). The UI shows each message under its field (FR-16).

### 4.2 Storage (`app/storage/`)
- `excel_store.py`
  - `file_path_for(date)` returns `<DataFolder>\<YYYY>\<MM-Mon>\<DD-Mon-YYYY>.xlsx`.
  - `append_entry(entry)` creates the file if missing (FR-27), writes the header row, adds the row, and saves.
  - `read_all_entries()` reads every daily file and returns `Entry` objects for the report.
  - `update_entry(entry, old_date)` changes a row. If the date changed, it removes the row from the old file and appends it to the new file (FR-30).
  - `delete_entry(entry_id, date)` removes a row.
  - Saving uses a temporary file and then replaces the real file, so a crash during save does not corrupt the Excel file (NFR-4).
  - If the file is locked by Excel, it raises `ExcelFileLockedError`. The service passes this up so the UI can show the FR-29 message.
- `subhead_store.py` reads and writes `subheads.json` in AppData. It only saves the list; it does not decide rules.
- `defaults_store.py` appends `{ label, value }` entries to the `treesa` or `daily` list in `%APPDATA%\ExpenseLedger\Defaults\default.js`. It inserts the entry before the closing `]);` of that list, keeps the file's existing format, and never removes or edits existing entries. The `value` is the label in lower case with each run of characters other than letters and digits replaced by `_` (the same rule as `toEntries` in the file).
- `account_store.py` reads and writes `account.json` in AppData (username, password hash, salt, failed attempt count, lock-until time).

### 4.3 Services (`app/services/`)
- `auth_service.py`: `create_account`, `login`, `change_password`, and `is_locked`. Lock time is stored in `account.json`, so closing and reopening the app does not reset the lock. `change_password(current, new)` is described in Section 6.8.
- `entry_service.py`: validates input (via core), builds an `Entry`, and calls `excel_store`. Its `save_entry`, `update_entry`, and `delete_entry` functions are the only way the UI changes data.
- `subhead_service.py`:
  - `add_subhead(name, main_head)` rejects empty, too long, and duplicate names (case-insensitive) (FR-8). After saving `subheads.json`, it calls `defaults_store` to write the name to `%APPDATA%\ExpenseLedger\Defaults\default.js` (`treesa` for MH 1, `daily` for MH 2).
  - `remove_subhead(name)` refuses mandatory sub-heads and otherwise sets `active = False` (FR-9, Rule 14).
  - `active_subheads()` returns the names for the dropdown.
- `report_service.py`:
  - `filter_entries(entries, filters)` applies the date range, Main Head, Sub-Head, Name, Particulars, Debit and Credit ranges, and the search box (FR-19, FR-19a). Search matches name or particulars text, or amount digits.
  - `sort_oldest_first(entries)` orders the rows (FR-18).
  - `totals(entries)` sums Debit and Credit with `Decimal` (FR-20).
  - `summarize(entries)` returns the six summary values for one period: total debit, most and least debited sub-head, total credit, most and least credited sub-head. Only sub-heads with at least one entry are ranked (FR-21a, FR-21b, FR-21c).
  - `date_range_bounds(range_name, today)` turns This Month, Last Month, This Year, and Custom Range into start and end dates.
  - The Monthly and Yearly summaries are separate calls to `summarize` with the entries for the selected month or year. They do not use the report filters.

### 4.4 UI (`app/ui/`)
- The UI calls services only. It never imports `openpyxl`.
- `main_window.py` owns the sidebar (Main Entry, Expense Report, Logout) and shows one page at a time (FR-6, FR-7).
- `main_entry_view.py`:
  - sets the Main Head to MH 2 and the Sub-Head to "-Select-" when it opens (FR-10, FR-11);
  - enables and disables the transaction fields and the Submit button using `validation.py` (FR-12, FR-14);
  - converts typed dates to DD-Mon-YYYY when the field loses focus or Submit is pressed (FR-33).
- `subhead_popup.py` shows the add popup for **+** and the removal confirmation for **−**.
- `expense_report_view.py` keeps a row in edit mode when its pencil is clicked. The checkmark runs the same validation as the form (FR-22).
- Each page is a class with a `refresh()` method. `main_window` calls `refresh()` when the page is opened.

---

## 5. Data Files

### 5.1 Daily Excel file (the ledger)
- Location: `Documents\ExpenseLedger\2026\10-Oct\20-Oct-2026.xlsx`
- One sheet named `Entries`.
- Header row and columns (FR-26): `ID | Main Head | Sub Head | Date | Name | Particulars | Debit | Credit | Created At`
- `Main Head` stores the label (for example `Daily Collection`).
- `Date` and `Created At` are stored as text: `20-Oct-2026` and `20-Oct-2026 14:05` (FR-28).
- `Debit` and `Credit` are numbers with two decimal places.
- `ID` format: `E20261020-001` (the date, then a running number for that day's file).
- `Sub Head` is stored as text, so old entries still show after the sub-head is removed (FR-31).

### 5.2 Sub-heads: `%APPDATA%\ExpenseLedger\subheads.json`
```json
{
  "subheads": [
    { "name": "Primary Sub Head", "mandatory": false, "active": true },
    { "name": "Secondary Sub Head", "mandatory": false, "active": true },
    { "name": "Auxiliary Sub Head", "mandatory": false, "active": true },
    { "name": "Special Collection", "mandatory": false, "active": true }
  ]
}
```
Seed values are in `config.py`. They are written to `subheads.json` the first time the app starts, if the file does not exist. The `mandatory` flags are placeholders until the customer confirms them (PRD A4).

### 5.3 Login file: `%APPDATA%\ExpenseLedger\account.json`
```json
{
  "username": "owner",
  "password_hash": "<hex>",
  "salt": "<hex>",
  "iterations": 600000,
  "failed_attempts": 0,
  "locked_until": null
}
```
Plain-text passwords are never written (PRD FR-3). The file is never placed in the Excel data folder (NFR-5).

---

## 6. Key Flows

### 6.1 Startup
1. `main.py` creates the app window.
2. If `account.json` does not exist, show the create account screen (FR-2).
3. Otherwise show the login screen (FR-1).
4. After a successful login, show the sidebar and open Main Entry (FR-7).

### 6.2 Enable the entry form
1. Main Entry opens with MH 2 selected and the Sub-Head at "-Select-".
2. While the Sub-Head is "-Select-", Date, Name, Particulars, Debit, Credit, and Submit are disabled.
3. When the user picks a sub-head, the transaction fields are enabled.
4. Submit is enabled only when `validation.py` reports no errors and Debit or Credit is greater than 0.00.
5. If the user sets the Sub-Head back to "-Select-", the fields are disabled again and their values are cleared (PRD A9).

### 6.3 Save an entry
1. The form calls `entry_service.save_entry(form_values)`.
2. `validation.py` checks every field. Any error returns to the form; nothing is written.
3. The date text is converted to DD-Mon-YYYY (FR-33).
4. `excel_store.append_entry` writes the row.
5. If the file is locked, the form keeps all values and shows the FR-29 message.
6. On success, the form shows a confirmation and clears the transaction fields (PRD A9).

### 6.4 Add or remove a sub-head
1. **+** opens the add popup. `subhead_service.add_subhead` checks the name, saves `subheads.json`, and then writes the new entry to `%APPDATA%\ExpenseLedger\Defaults\default.js` through `defaults_store`.
2. The Sub-Head dropdown refreshes right away (FR-8).
3. **−** asks for confirmation. `subhead_service.remove_subhead` refuses mandatory items. Otherwise the item is set to inactive and is removed from the dropdown (FR-9).

### 6.5 Expense Report
1. `report_service` reads all entries with `excel_store.read_all_entries()`.
2. Filters and search apply when **Filter Report** is clicked, or when Enter is pressed in the search box (FR-19, FR-19a). Invalid filter values (bad dates, amounts, or a From amount above a To amount) show a message and are not applied.
3. Totals are summed with `Decimal` over the rows shown (FR-20).
4. The Monthly and Yearly summary cards call `summarize` for the selected month and year (FR-21a, FR-21b). They are not affected by the report filters.

### 6.6 Edit or delete a report row
1. Pencil: the row switches to input fields, including the Main Head and Sub-Head dropdowns (PRD FR-22). Choosing a Main Head refreshes the Sub-Head list. Checkmark: validate (a Sub-Head must be chosen) and call `entry_service.update_entry`. A Main Head or Sub-Head change does not move the row to another file, since only the date decides the file (FR-30). Esc cancels the edit (not in the specification; a design choice noted in Design.md Section 6.1).
2. Delete: show `confirm_popup`. Only after **Yes** is `entry_service.delete_entry` called (FR-23).

### 6.7 Login lockout
1. A wrong password increases `failed_attempts` and saves the file.
2. At 5 failures, `locked_until` is set to now + 5 minutes.
3. While locked, the login button is disabled and the remaining time is shown.
4. A correct password resets `failed_attempts` to 0.

### 6.8 Change password
1. The popup calls `auth_service.change_password(current, new, confirm)`.
2. If the account is locked, refuse and show the remaining time (same as login).
3. Check the current password with `password_hash.check_password`. A wrong one increases `failed_attempts`, and at 5 the lock is set (PRD FR-39). Show the tries left.
4. Check the new password: at least `MIN_PASSWORD_LENGTH`, different from the current one, and equal to the confirmation (PRD FR-40).
5. Hash the new password with a new random salt (`password_hash.hash_password`), save `password_hash`, `salt`, and `iterations` in `account.json`, reset `failed_attempts` to 0, and save the file (PRD FR-41).
6. The old hash and salt are overwritten. Nothing else in `account.json` changes, and no other data file is touched.

---

## 7. Performance (NFR-3)

- The Expense Report reads every daily file, and the date range filter narrows the rows only after they are read. Reading every file is the main risk to the 1-second target. Opening only the files inside a chosen date range is a possible later improvement, not part of v1.1.
- Mitigation if the test in task T8.3 is slower than 1 second: keep an in-memory cache of the report rows keyed by file path and modified time, refreshed on save, update, and delete. Do not change the storage design for this.

---

## 8. Error Handling

- No bare `except:`. Catch the specific error (for example `PermissionError` or `json.JSONDecodeError`).
- Show users a plain message. Write the technical details to `app.log` in AppData. Dates in the log also use DD-Mon-YYYY.
- If `subheads.json` or `account.json` is corrupt, show a clear message and do not overwrite the file.
- `%APPDATA%\ExpenseLedger\Defaults\default.js` is the working copy. On first run, if it does not exist, the app copies the seed `default.js` installed with the program into AppData. The file lives in AppData, not in `Program Files`, so it can be written without administrator rights and it is kept when the program is uninstalled.
- If the AppData `default.js` cannot be written (locked, read-only, or the list is not found), the sub-head is still saved in `subheads.json` and the user sees a plain message. The file is never replaced with a blank one.

---

## 9. Packaging (Phase 9)

- EXE: PyInstaller, one-folder build first (easier to debug), then one-file if it works. Output: `dist\ExpenseLedger.exe`.
- MSI: built from the EXE with WiX Toolset v4. It installs to `Program Files\ExpenseLedger` and adds a Start Menu shortcut. On uninstall it removes the program files only. It keeps all user data in `Documents\ExpenseLedger` (Excel entries) and `%APPDATA%\ExpenseLedger` (login, sub-heads, `Defaults\default.js`, log). Version 1.1 has no option to delete data during uninstall.
- Uninstall: two ways, both keep user data.
  - Windows: Settings > Apps > Installed apps > Expense Ledger > Uninstall (the MSI registers the program).
  - `installer/uninstall.bat`: asks for confirmation, finds the MSI product code under the Windows uninstall list, and runs `msiexec /x`. It reports success, cancel, or an error code. WiX installs a copy into the program folder and adds a Start Menu shortcut "Uninstall Expense Ledger".
- Version number `1.0.0` is set in `config.py` and in the WiX file.
- Developer signature: `APP_AUTHOR` ("Tenwin James") is the single source. It is used in the sidebar footer and login About text (FR-34). The PyInstaller version-info file sets CompanyName and LegalCopyright to the same name, so the EXE Properties show it (FR-35). The WiX file sets `Manufacturer` and the publisher to the same name.
- PyInstaller must include the `tkcalendar` data files. Check this in task T9.1.
- PyInstaller must also include the `fonts/` folder as data files, so the font files are inside the program folder. The WiX installer copies that folder too. On uninstall the font files are removed with the program, since they are not user data.

---

## 10. Decisions Still Open

| # | Question | Default used in this document | Decide by |
|---|----------|-------------------------------|-----------|
| 1 | Should the user change the Excel data folder? | No. Fixed to `Documents\ExpenseLedger` in v1. | Phase 1 |
| 2 | MSI tool | WiX Toolset v4 | Task T9.3 |
| 3 | Password reset | Not in v1 (PRD risk table: v1.1) | Phase 10 |
| 4 | Mandatory sub-heads and currency name | See PRD Section 10 (A4, A6) | Customer |

---

## 11. Version 2 Readiness

- `storage/` is the only layer that knows about Excel and JSON files. A future `storage/postgres_store.py` can replace `excel_store.py` with the same method names, and the services and screens stay the same.
- Services return plain data classes (`Entry`, `SubHead`), not Excel rows, so the screens do not depend on the file format.
