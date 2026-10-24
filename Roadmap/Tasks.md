# Tasks: Expense Ledger (Version 1.1)

Version: 1.1
Status: Draft
Read after: PRD.md, Architecture.md, Rules.md, Design.md

How to use this file:
- Work the tasks in order. Each task has an ID (for example T0.1).
- Tick the box `[x]` only when the Definition of Done (Roadmap.md Section 9) is met.
- Each task lists the PRD requirements it covers and the files it touches.
- Commit one task at a time, with the task ID in the message (Rules 34).

---

## Phase 0 – Setup

Goal: a working Python environment. Milestone: none (prepares M1).

- [ ] **T0.1 Install Python 3.11+.** Install from python.org and tick "Add to PATH". Check with `python --version` in a new terminal.
- [x] **T0.2 Create the virtual environment.** Run `python -m venv .venv` in the project folder and activate it.
- [ ] **T0.3 Write `requirements.txt`.** List `customtkinter`, `openpyxl`, and `tkcalendar` with exact versions.
- [ ] **T0.4 Write `requirements-dev.txt`.** List `pytest` and `pyinstaller` with exact versions. Include `-r requirements.txt` at the top.
- [ ] **T0.5 Install packages.** Run `pip install -r requirements-dev.txt` with no errors.
- [ ] **T0.6 Write `.gitignore`.** Ignore `.venv/`, `build/`, `dist/`, `installer/output/`, `__pycache__/`, `*.xlsx` under the data folder, `account.json`, and `subheads.json` (Rules 22).
- [ ] **T0.7 Check CustomTkinter and the date picker.** Run a 3-line test window with a `tkcalendar` DateEntry. Close it. Confirms both GUI libraries work on this PC.

---

## Phase 1 – Foundation

Goal: folders, paths, date and money helpers, and an empty window. Milestone: **M1 – Hello Window**.

- [ ] **T1.1 Create the folder structure.** Create `app/core`, `app/storage`, `app/services`, `app/ui`, and `tests`. Add `__init__.py` to each `app` folder (Architecture Section 3).
- [ ] **T1.2 Write `config.py`.** App name `Expense Ledger`, version `1.0.0`, `MAX_LOGIN_ATTEMPTS = 5`, `LOCK_MINUTES = 5`, `NAME_MAX_LENGTH = 100`, `PARTICULARS_MAX_LENGTH = 200`, `SUBHEAD_MAX_LENGTH = 40`, `MIN_PASSWORD_LENGTH = 8`, `APP_AUTHOR = "Tenwin James"`, and the seed sub-heads (Rules 6). Covers FR-36.
- [ ] **T1.2a Write `theme.py`.** One constant per colour name in Design.md Section 1.1 (for example `BG_CARD`, `PRIMARY`, `TEXT`), and the font weights and sizes from Design.md Section 1.2. No other file uses a colour value directly (Rule 37).
- [ ] **T1.3 Write `models.py` constants.** `MAIN_HEADS` with MH 1 (Treesa Agencies) and MH 2 (Daily Collection). Default main head is MH 2. Covers PRD FR-10.
- [ ] **T1.4 Write `paths.py`.** Return the AppData folder (`%APPDATA%\ExpenseLedger`) and the Excel data folder (`Documents\ExpenseLedger`). Create them if missing. Covers NFR-5, FR-25.
- [ ] **T1.4a Choose and add the font files.** Confirm the font family (proposed Inter, OFL) and put its `.ttf` files for each weight used in `fonts/`. Check the license file is kept with them. Covers NFR-8.
- [ ] **T1.4b Write `fonts.py`.** Register each `.ttf` in `fonts/` for this process only with `AddFontResourceEx` (`FR_PRIVATE`) through `ctypes`, once at startup. If a file fails, log it and use Segoe UI. Covers NFR-8.
- [ ] **T1.4c Test `fonts.py`.** Check that a label set to the bundled font shows it, and that a missing file falls back without an error. Must pass.
- [ ] **T1.5 Write `dates.py`.** Format a date as DD-Mon-YYYY; parse `DD-Mon-YYYY` and `DD/MM/YYYY`; build the `YYYY` and `MM-Mon` folder names. Use the fixed month list (Rules 12). Covers FR-32, FR-33.
- [ ] **T1.6 Test `dates.py`.** `tests/test_dates.py` covers `20-Oct-2026`, `20/10/2026`, `1/2/2026` (rejected or accepted as decided in the test), `31/02/2026` (rejected), invalid text, and leap day. Must pass.
- [ ] **T1.7 Write `money.py`.** Parse text to `Decimal` with at most 2 decimals (commas allowed); format as `2,500.00`. No amount-in-words (removed in v1.1, PRD FR-21). Covers FR-20.
- [ ] **T1.8 Test `money.py`.** `tests/test_money.py` covers parsing (with and without commas), rejection of 3 decimals and negatives, and formatting for 0, 2,500, 14,200, 122,500. Must pass.
- [ ] **T1.9 Write `main.py` with an empty window.** Opens a CustomTkinter window titled "Expense Ledger" with a blank page.
- [ ] **T1.10 Check M1.** Run `python main.py`. Window opens and closes cleanly. Milestone M1 reached.

---

## Phase 2 – Login

Goal: account creation and login with lockout. Milestone: **M2 – Secure Entry**.

- [ ] **T2.1 Write `password_hash.py`.** `hash_password(password) -> (hash, salt)` and `check_password(password, hash, salt) -> bool`. PBKDF2-SHA256, 16-byte salt, 600,000 iterations, `hmac.compare_digest` (Rules 19, 20). Covers FR-3, NFR-5.
- [ ] **T2.2 Test `password_hash.py`.** Correct password passes, wrong password fails, same password gives different hashes. Must pass.
- [ ] **T2.3 Write `account_store.py`.** Read and write `account.json` in AppData. If the file is corrupt, raise an error and do not overwrite (Rules 18).
- [ ] **T2.4 Write `auth_service.py` – create account.** Save username and hash. Refuse if an account already exists. Covers FR-2.
- [ ] **T2.5 Write `auth_service.py` – login and lockout.** Count failures. At 5 failures set `locked_until` to now + 5 minutes and save it. Reset the count on success. Covers FR-4.
- [ ] **T2.6 Test auth service.** Tests use a temporary folder (Rules 29). Cover: create account, correct login, 4 wrong then correct, 5 wrong then locked, lock survives a new service object (simulated restart), lock expires after 5 minutes (fake clock). Must pass.
- [ ] **T2.7 Build the create account screen.** Per Design.md section 3. Covers FR-2, FR-16.
- [ ] **T2.8 Build the login screen.** Per Design.md section 4. Disable the button and show the countdown when locked. Covers FR-1, FR-4.
- [ ] **T2.9 Route startup.** No account file → create account screen. Account exists → login screen. Successful login → main window. Covers FR-1, FR-2.
- [ ] **T2.10 Check M2.** Create an account, restart the app, log in, fail 5 times, confirm lockout. Milestone M2 reached.
- [ ] **T2.11 Write `auth_service.change_password`.** Check the lock, check the current password (a wrong one counts toward the lock), check the new password rules, then save a new hash and salt and reset the failed count. Covers FR-39, FR-40, FR-41.
- [ ] **T2.12 Test change password.** `tests/test_auth_service.py`: correct change, wrong current password counts and locks after 5, new password equal to the old one is rejected, new password under 8 characters is rejected, mismatched confirmation is rejected, login works with the new password and fails with the old one. Must pass.
- [ ] **T2.13 Build the Change Password popup.** Per Design.md section 2. Save is disabled until all fields are filled. Errors show under each field. Covers FR-37, FR-38.
- [ ] **T2.14 Add the sidebar button.** Change Password sits above Logout on every page. Covers FR-37.
- [ ] **T2.15 Check change password.** Change the password, restart the app, log in with the new one. Milestone M2 still holds.

---

## Phase 3 – Navigation

Goal: sidebar and page switching. Milestone: **M3 – Navigable App**.

- [ ] **T3.1 Build the sidebar.** Per Design.md section 2: app name, version, three items in order (Main Entry, Expense Report, Logout), and the footer "Developed by Tenwin James" below Logout, read from `APP_AUTHOR`. Covers FR-6, FR-34.
- [ ] **T3.2 Build page switching.** `main_window.py` shows one page at a time and calls `refresh()` on the page each time it opens. Covers FR-7.
- [ ] **T3.3 Add placeholder pages.** Main Entry and Expense Report each show their title and description from Design.md. Main Entry is the default page. Covers FR-7.
- [ ] **T3.4 Active item highlight.** The current page is highlighted in the sidebar (Design.md section 2).
- [ ] **T3.5 Logout.** Logout appears on every page and returns to the login screen. Covers FR-5.
- [ ] **T3.6 Check M3.** Click through both pages and log out. Milestone M3 reached.

---

## Phase 4 – Sub-Heads

Goal: a sub-head list that the user can add to and remove from. No entry form yet.

- [ ] **T4.1 Write `subhead_store.py`.** Read and write `subheads.json` in AppData. Create it from the seed values in `config.py` if it does not exist (Architecture Section 5.2). Corrupt file → error, no overwrite (Rules 18).
- [ ] **T4.2 Write the `SubHead` model.** Name, mandatory flag, active flag, in `models.py`.
- [ ] **T4.3 Write `subhead_service.py` – add.** Trim spaces. Reject empty names and names over 40 characters. Reject duplicates case-insensitively. Covers FR-8.
- [ ] **T4.4 Write `subhead_service.py` – remove.** Refuse mandatory sub-heads. Otherwise set `active = False`. Never remove the item from the file (Rules 14). Covers FR-9.
- [ ] **T4.5 Write `subhead_service.py` – active list.** Return active names in order, for the dropdown. Covers FR-11.
- [ ] **T4.6 Test sub-head service.** `tests/test_subhead_service.py`: add, duplicate with different case rejected, empty and too-long names rejected, mandatory cannot be removed, removed item is inactive and not in the active list, nothing is deleted. Must pass.
- [ ] **T4.6a Write `defaults_store.py`.** Append `{ label, value }` to the `treesa` or `daily` list in `%APPDATA%\ExpenseLedger\Defaults\default.js` (created on first run from the copy installed with the program), before the closing `]);` of that list. Create `value` with the `toEntries` slug rule. Append only; do not touch other entries. If the file or list cannot be found, raise an error and leave the file unchanged (Rules 18a). Call it from `add_subhead`. Covers FR-8.
- [ ] **T4.6b Test `defaults_store`.** Use a copy of `default.js` in a temporary folder: a new label is added to the right list, the `value` slug is correct, existing entries are unchanged, and a missing list leaves the file unchanged. Must pass.
- [ ] **T4.7 Build the add popup (+).** Per Design.md section 5.4. Covers FR-8.
- [ ] **T4.8 Build the remove popup (−).** Per Design.md section 5.5. Disabled for mandatory items and "-Select-". Covers FR-9.

---

## Phase 5 – Main Entry

Goal: validated entry form with the Main Head, Sub-Head, and enable and disable rules. Milestone: **M4 – Usable Form**.

- [ ] **T5.1 Write `validation.py` – entry form.** Check: Sub-Head chosen (not "-Select-"), date valid, name present and up to 100 characters, particulars present and up to 200 characters, Debit and Credit valid amounts, Debit or Credit greater than 0.00. Returns field errors and a submit-enabled flag. Covers FR-13, FR-14, FR-16.
- [ ] **T5.2 Test validation.** `tests/test_validation.py` covers each rule, both amounts at 0.00 (invalid), one amount above 0.00 (valid), negative, 3 decimals, name at 100 and 101 characters, date formats. Must pass.
- [ ] **T5.3 Build the Main Head selector.** Two radio options; Daily Collection selected on open (FR-10, Design.md 5.1).
- [ ] **T5.4 Build the Sub-Head dropdown.** Shows "-Select-" first, then `subhead_service.active_subheads()`. Opens at "-Select-" (FR-11). Covers the +/− buttons from Phase 4.
- [ ] **T5.5 Enable and disable fields.** Date, Name, Particulars, Debit, Credit, and Submit are disabled until a sub-head is chosen. Helper text shows while "-Select-" is selected (FR-12, Rule 24).
- [ ] **T5.6 Clear fields when sub-head returns to "-Select-".** Values are cleared and fields disabled again (PRD A9, Architecture 6.2).
- [ ] **T5.7 Build the date field.** Text box with the `tkcalendar` picker button. Typed `20/10/2026` converts to `20-Oct-2026` on focus-out. Invalid text shows the error from Design.md 5.3. Covers FR-13, FR-33.
- [ ] **T5.8 Build Debit and Credit fields.** Default 0.00. Accept digits and one decimal point, max 2 decimals. Covers FR-13.
- [ ] **T5.9 Enable Submit only when valid.** Submit follows `validation.py` (FR-14). Show the hint when both amounts are 0.00.
- [ ] **T5.10 Show inline errors.** Each error shows under its field in `ERROR` text (Rules 25). Covers FR-16.
- [ ] **T5.11 Build Clear.** Resets the transaction fields only (FR-17).
- [ ] **T5.12 Save to memory with a confirmation.** On Submit, validate and show the success message. Store the entry in memory for now; Excel comes in Phase 6. Covers FR-15 (temporary).
- [ ] **T5.13 Keyboard support.** Tab order matches Design.md section 5. Enter submits when enabled. Covers NFR-6.
- [ ] **T5.14 Check M4.** Enter a daily collection and a Treesa Agencies entry. Check that fields stay disabled until a sub-head is chosen and that Submit is disabled until the form is valid. Milestone M4 reached.

---

## Phase 6 – Excel Storage

Goal: daily Excel files saved and read. Milestone: **M5 – Data on Disk**.

- [ ] **T6.1 Write `excel_store.file_path_for(date)`.** Returns `<DataFolder>\<YYYY>\<MM-Mon>\<DD-Mon-YYYY>.xlsx`. Covers FR-24, FR-25.
- [ ] **T6.2 Create a new daily file.** When no file exists for the date, create the folder, a workbook with sheet `Entries`, and the header row `ID | Main Head | Sub Head | Date | Name | Particulars | Debit | Credit | Created At`. Covers FR-26, FR-27.
- [ ] **T6.3 Append a row.** ID as `E<YYYYMMDD>-<NNN>`. Debit and Credit as numbers with 2 decimals. Dates as DD-Mon-YYYY text. Covers FR-26, FR-28.
- [ ] **T6.4 Handle the Excel file being open.** Catch `PermissionError` on save. Raise `ExcelFileLockedError`. Show the warning from Design.md section 5.6, keep all form values, and do not lose the entry. Covers FR-29. Risk table: "Excel file is open while saving."
- [ ] **T6.5 Make saves safe.** Write to a temporary file in the same folder, then replace the real file. Covers NFR-4, Rules 16.
- [ ] **T6.6 Read all entries.** `read_all_entries()` opens every daily file and returns `Entry` objects with `Decimal` amounts. Covers the report data path.
- [ ] **T6.7 Update and delete rows.** `update_entry` changes a row, and moves it to another file if the date changed (FR-30). `delete_entry` removes a row by ID. Both work on the file for the entry's date.
- [ ] **T6.8 Test Excel storage.** `tests/test_excel_store.py` using a temporary folder (Rules 29). Cover: file created, header correct, row appended, second entry same day, file path for a date, read-all returns all rows, update in place, update that changes the date moves the row, delete, and the lock error when the file is open (simulate by holding the file open). Must pass.
- [ ] **T6.9 Wire Submit to Excel.** Replace the temporary memory save from T5.12 with `entry_service.save_entry` writing to Excel. Covers FR-15.
- [ ] **T6.10 Check M5.** Save an entry, open the file in Excel, confirm the row and the path `2026\10-Oct\20-Oct-2026.xlsx`. Milestone M5 reached.

---

## Phase 7 – Expense Report

Goal: the report with search, filters, totals, monthly and yearly summary cards, inline edit, and delete. Milestone: **M6 – Full Report**.

- [ ] **T7.1 Write `report_service.py` – filters.** `filter_entries` with the date range (All, This Month, Last Month, This Year, Custom), Main Head (All, Treesa Agencies, Daily Collection), Sub-Head (All, or a name), Name and Particulars contains, and Debit and Credit min/max. Covers FR-19.
- [ ] **T7.2 Write `report_service.py` – search.** Matches Name or Particulars text, or an amount by digits (`2500`, `2500.00`, `2,500` find 2,500.00). Combined with the filters. Covers FR-19a.
- [ ] **T7.3 Write `report_service.py` – order and totals.** Oldest first. Totals of Debit and Credit with `Decimal`. Covers FR-18, FR-20.
- [ ] **T7.4 Write `report_service.py` – summary.** `summarize(entries)` returns total Debit, most and least debited sub-head (with amount), total Credit, most and least credited sub-head (with amount). Only sub-heads with entries are ranked; ties by name. Covers FR-21a, FR-21b, FR-21c.
- [ ] **T7.5 Test report service.** `tests/test_report_service.py`: each filter alone and combined, date range boundaries, invalid custom range rejected, search by name, particulars, and amount (`2500` finds 2,500.00), order, totals, summary values for a month and a year, ties, empty result, removed sub-head still shown on old entries. Must pass.
- [ ] **T7.6 Build the report table.** Columns Date, Main Head (name), Sub-Head, Name, Particulars, Debit, Credit, Actions. Empty state text. Covers FR-18.
- [ ] **T7.7 Build the search box and filter bar.** Search box, Date Range selector with From and To fields (shown for Custom Range), Main Head and Sub-Head dropdowns, Name and Particulars boxes, Debit and Credit From/To boxes, CLEAR FILTERS and FILTER REPORT buttons. An invalid filter shows a message and is not applied. Covers FR-19, FR-19a.
- [ ] **T7.8 Build the totals row.** Totals of the rows shown, under the table. The amount-in-words lines are not built (removed in v1.1). Covers FR-20, FR-21.
- [ ] **T7.9 Build the Monthly and Yearly summary cards.** Two sections, each with a heading, a one-line note that the values follow the selected month or year, a period selector (default latest with entries), and six cards as in Design.md section 6. Cards ignore the report filters. Covers FR-21a, FR-21b, FR-21c.
- [ ] **T7.10 Build inline edit.** Pencil switches the row to inputs (Date, Main Head and Sub-Head as dropdowns, Name, Particulars, Debit, Credit). Changing the Main Head refreshes the Sub-Head list; a Sub-Head must be selected; the current Sub-Head stays in the list even if removed. Checkmark saves with the same validation as Main Entry; Esc cancels. Covers FR-22.
- [ ] **T7.11 Build the delete popup.** Delete opens the confirmation popup. Only **DELETE** removes the row. Covers FR-23, Rules 17.
- [ ] **T7.12 Refresh on open.** The report reloads every time the page is opened, and the summary cards update with it. Covers FR-18, FR-21a.
- [ ] **T7.13 Check M6.** Compare the totals and the monthly and yearly cards with a manual sum of the Excel files. Milestone M6 reached.

---

## Phase 8 – Testing

Goal: tests pass and speed is checked.

- [ ] **T8.1 Run the full test suite.** `pytest` passes with no failures.
- [ ] **T8.2 Run the manual screen checklist.** Design.md section 8, all items ticked.
- [ ] **T8.3 Speed test.** Create 10,000 entries across a year of daily files. Saving one entry and loading the Expense Report each take under 1 second (NFR-3). If not, apply the cache in Architecture Section 7.
- [ ] **T8.4 Keyboard-only test.** Complete login, enter an entry, filter the report, and edit a row using the keyboard only (NFR-6).
- [ ] **T8.5 Success criteria check.** Confirm PRD Section 11: entry in under 30 seconds; Submit enable rule; typed `20/10/2026` shows `20-Oct-2026`; new sub-head appears right away; report totals match Excel.
- [ ] **T8.6 Fix defects found.** Each bug gets a note in the commit message. Re-run T8.1 after fixes.
- [ ] **T8.7 Check no file locations on screen.** Go through every screen, popup, message, and tooltip. None shows a folder, an AppData path, or a file name (PRD NFR-9, Rule 36). The only file-related text allowed is the date in the Excel warning. Must pass.

---

## Phase 9 – Packaging

Goal: EXE and MSI. Milestone: **M7 – Installable**.

- [ ] **T9.1 Build the EXE early.** PyInstaller one-folder build of `main.py`. Include `tkcalendar` data files and the `fonts/` folder (NFR-8). Output `dist\ExpenseLedger\ExpenseLedger.exe`. Fix hidden import problems now (Roadmap risk: beginner gets stuck on packaging). Add a PyInstaller version-info file with CompanyName and LegalCopyright set to `APP_AUTHOR` and check them in the EXE Properties (FR-35).
- [ ] **T9.2 Test the EXE.** Run it from a folder with no Python installed. Login, enter an entry, and the report all work, including the date picker.
- [ ] **T9.3 Choose the MSI tool.** Confirm WiX Toolset v4 (Architecture Section 2) or pick another. Record the decision in Architecture Section 10.
- [ ] **T9.4 Write the installer definition.** Installs to `Program Files\ExpenseLedger`, Start Menu shortcut, uninstall keeps user data (Architecture Section 9). Set Manufacturer and publisher to "Tenwin James" (FR-35).
- [ ] **T9.5 Build `ExpenseLedger-1.0.0.msi`.** Output in `installer\output\`.
- [ ] **T9.5a Write the uninstall file.** `installer\uninstall.bat` (already written). Check that it finds the installed product, asks for Y before uninstalling, keeps `Documents\ExpenseLedger` and `%APPDATA%\ExpenseLedger`, and shows a clear message for success, cancel, and error. Include it in the WiX file so it is copied to the program folder with a Start Menu shortcut. Covers PRD deliverable 4.
- [ ] **T9.6 Test install and uninstall.** On a clean Windows 10 PC (or a clean virtual machine) with no Python: install, run, uninstall with both the Windows Apps list and `uninstall.bat`. Confirm the data folders are still there afterwards. Covers M7.
- [ ] **T9.7 Check SmartScreen note.** Write the warning steps for the User Guide (Roadmap risk table).

---

## Phase 10 – Release

Goal: Version 1.0 installed on your devices. Milestone: **M8 – Release 1.0**.

- [ ] **T10.1 Confirm open assumptions.** Get the customer's answers to PRD Section 10 (A1 to A9) and update the code and documents to match.
- [ ] **T10.2 Write `README.md` (User Guide).** Install steps, first run, enter entries, manage sub-heads, the Expense Report, data file locations, what to do if the Excel file is open, and the warning that there is no password reset in v1.0. End the guide with "Developed by Tenwin James".
- [ ] **T10.3 Write `CHANGELOG.md`.** Entry for 1.0.0 listing the features (Rules 33).
- [ ] **T10.4 Final document review.** Check PRD.md, Architecture.md, Rules.md, Design.md, and Tasks.md match the built app. Update any that differ.
- [ ] **T10.5 Install on your devices.** Install the MSI on every device you use. Covers M8.
- [ ] **T10.6 Update the progress tracker.** Mark phases complete in Roadmap.md Section 11 with the actual finish date (Roadmap Section 10).

---

## Version 2 (Planned, not started)

See PRD.md Section 9 (Future Scope) and Roadmap.md Section 7 for phases V2.1 to V2.8. Planning starts only after Phase 10 is complete.
