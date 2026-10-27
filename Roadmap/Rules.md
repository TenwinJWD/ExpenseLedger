# Rules: Expense Ledger (Version 1.1)

Version: 1.1
Status: Draft
Read after: Architecture.md

These rules apply to every line of code, every document, and every change. The builder is a beginner, so the rules favor simple code that is easy to read over clever code.

---

## 1. Code Style

1. **Rule 1 – Python 3.11+.** Use features available in Python 3.11. Do not use third-party packages that are not listed in `requirements.txt` or `requirements-dev.txt`.
2. **Rule 2 – Simple code first.** Write the plain, longer version if it is easier to read. Avoid one-line tricks, deep nesting, and lambdas that span more than one idea.
3. **Rule 3 – Comments explain why.** Every module starts with a short docstring saying what it does. Every function that is not obvious gets a one-to-three line comment. Do not comment what the code plainly says.
4. **Rule 4 – Naming.** Files and functions use `snake_case`. Classes use `PascalCase`. Fixed values use `UPPER_CASE` and live in `config.py` or `models.py`.
5. **Rule 5 – Type hints.** Every public function has type hints for its arguments and return value.
6. **Rule 6 – No magic numbers.** Numbers such as 5 (attempts), 5 (minutes), 100 (name length), 200 (particulars length) come from `config.py` with a name.

---

## 2. Layers and Structure

7. **Rule 7 – Layer direction.** The UI calls services only. Services call storage and core. Core imports nothing from the other layers. Storage never imports UI or services.
8. **Rule 8 – Only storage touches files.** `openpyxl`, `json`, and file paths are used only inside `app/storage/` and `app/core/paths.py`. This keeps the Version 2 move to PostgreSQL to one layer (PRD NFR-7).
9. **Rule 9 – One place for validation.** Form and report-edit rules live only in `app/core/validation.py`. The UI shows the messages it returns and does not repeat the checks.

---

## 3. Dates and Money

10. **Rule 10 – One date format.** Every date shown on screen, written to Excel, used in a folder name, or written to a log uses DD-Mon-YYYY (example: `20-Oct-2026`). Only `app/core/dates.py` formats or parses dates.
11. **Rule 11 – Typed dates are converted.** The user may type `DD-Mon-YYYY` or `DD/MM/YYYY`. Both are converted to DD-Mon-YYYY as soon as they are accepted. Any other text is an error.
12. **Rule 12 – No locale-based month names.** Do not use `strftime("%b")`. Month abbreviations come from the list in `dates.py`, so the output is the same on every Windows language setting.
13. **Rule 13 – Money uses Decimal.** Debit, credit, and totals are `decimal.Decimal`. Never use `float` for money. Round to two decimal places only when saving or showing.

---

## 4. Data Safety

14. **Rule 14 – Remove sub-heads by deactivating them.** A removed sub-head is marked inactive, not deleted. It leaves the dropdown, but old entries keep the sub-head name, so they still show correctly (PRD FR-9, FR-31).
15. **Rule 15 – Never lose an entry.** If a save fails, the form keeps every value the user typed. Show a message that says what to do next.
16. **Rule 16 – Atomic Excel saves.** Write the workbook to a temporary file in the same folder, then replace the real file. A crash during save must not leave a broken `.xlsx`.
17. **Rule 17 – Never auto-delete user data.** The app deletes an entry row only after the user confirms it in the delete popup. It never deletes an Excel file, a sub-head, or the account file on its own.
18a. **Rule 18a – Write added sub-heads to the AppData `default.js`.** Every sub-head added with **+** is also appended to the `treesa` (MH 1) or `daily` (MH 2) list in `%APPDATA%\ExpenseLedger\Defaults\default.js` as a new label string. The file's own `toEntries` rule gives the stored value. Only append; never edit or remove existing entries, and never replace the file if it cannot be parsed (PRD FR-8).
18. **Rule 18 – Corrupt files are not overwritten.** If `subheads.json` or `account.json` cannot be read, show a message and stop. Do not replace it with defaults silently.

---

## 5. Security

19. **Rule 19 – Hash passwords.** Use `hashlib.pbkdf2_hmac` with SHA-256, a random salt of 16 bytes (`secrets.token_bytes`), and at least 600,000 iterations. Never store, log, or print a plain password.
20. **Rule 20 – Compare hashes safely.** Use `hmac.compare_digest` to compare password hashes.
21. **Rule 21 – Account data in AppData.** `account.json` and `subheads.json` live in `%APPDATA%\ExpenseLedger\`. They never go in the project folder or the Excel data folder (NFR-5).
22. **Rule 22 – No secrets in Git.** Do not commit `account.json`, `subheads.json`, Excel files, `build/`, `dist/`, or `.venv/`. These are listed in `.gitignore`.

---

## 6. User Experience

23. **Rule 23 – Keyboard first.** Tab moves between fields in the order shown on screen. Enter in the form submits when Submit is enabled. Every button can be reached by keyboard (PRD NFR-6).
24. **Rule 24 – Disabled means disabled.** Fields and buttons that cannot be used are disabled, not hidden. The Submit button is enabled only when the form is valid (PRD FR-12, FR-14).
25. **Rule 25 – Errors next to fields.** Validation messages appear under the field that has the problem, in red. Do not use pop-ups for field errors. Pop-ups are used only for the delete confirmation and the sub-head popups.
26. **Rule 26 – Plain messages.** Write messages a non-technical user understands. Say what happened and what to do, for example: "The Excel file for 20-Oct-2026 is open. Close it in Excel and click Submit again. Your entry has not been lost."
27. **Rule 27 – Visual style from the specification.** Use the layout, labels, and icons in Design.md. Do not add new colors without updating Design.md.

---

## 7. Testing

28. **Rule 28 – Test the logic.** Every module in `app/core/`, `app/services/`, and `app/storage/` has tests in `tests/`. Tests run with `pytest` and must pass before a task is ticked.
29. **Rule 29 – Test with temporary folders.** Storage tests write to a temporary folder (`tmp_path` in pytest), never to the real `Documents\ExpenseLedger`.
30. **Rule 30 – Manual check for screens.** Each screen is checked by hand against Design.md and the PRD requirements listed in its task.

---

## 8. Process and Documents

31. **Rule 31 – Documents first.** A requirement change goes into PRD.md first. A structure change goes into Architecture.md first. Any assumption made without customer confirmation goes into PRD.md Section 10.
32. **Rule 32 – Tick tasks only when done.** A checkbox in Tasks.md is ticked only when the Definition of Done in Roadmap.md Section 9 is met.
33. **Rule 33 – Record versions.** Every version change is recorded in `CHANGELOG.md`.
34. **Rule 34 – Small commits.** One task per commit. The commit message names the task ID, for example `T5.1: add entry validation`.
35. **Rule 35 – No new scope.** Features not in PRD.md go into PRD Section 9 (Future Scope), not into the code.
36. **Rule 36 – No file locations on screen.** No screen, message, popup, or tooltip shows a folder, AppData path, or file name (PRD NFR-9). Use the date, the name, or the action instead. Code may use the paths, and the planning documents may name them.
37. **Rule 37 – Colors come from the theme.** Screens use only the names in `theme.py`, which are the values in Design.md Section 1.1. A new colour needs a Design.md update first.
