# PRD: Expense Ledger (Windows Desktop App)

Version: 1.0
Status: Draft
Owner: [Your Name]

---

## 1. Purpose

A simple Windows desktop ledger that lets a user record income and expenses, see totals on a dashboard, and keep every entry in Excel files organized by date.

The app is installed separately on each device. Each installation has its own local data and its own login.

---

## 2. Target User

- Primary: a single person (or small household or shop owner) who tracks money on a Windows 10 PC.
- Skill level of the builder: beginner. The code must stay simple, readable, and well-commented.

---

## 3. Goals

1. Record income and expense entries quickly using dropdown lists.
2. Show total income, total expenses, and balance on a dashboard.
3. Store every entry in a readable Excel file, organized by year and month.
4. Let the user manage dropdown lists (categories, payment modes, etc.) without editing code.
5. Protect the app with a login.
6. Ship as a standalone `.exe` and as an `.msi` installer.

---

## 4. Non-Goals (Version 1)

- No cloud sync or website (planned for a later version).
- No multi-user access on one device (planned for a later version).
- No bank integration.
- No budgets, reminders, or recurring entries.
- No mobile app.

---

## 5. Functional Requirements

### 5.1 Login
- FR-1: The app opens on a login screen before any data is shown.
- FR-2: On first run, the user creates one account (username and password).
- FR-3: Passwords are never stored as plain text.
- FR-4: After 5 failed attempts, the login is locked for 5 minutes.
- FR-5: A "Logout" option is available on every page.

### 5.2 Navigation
- FR-6: After login, the main window shows a sidebar with: Dashboard, Add Entry, Manage Lists, Logout.
- FR-7: The Dashboard is the default page.

### 5.3 Dashboard
- FR-8: Shows Total Income, Total Expenses, and Balance (Income minus Expenses).
- FR-9: The user can choose a period: This Month (default), This Year, All Time, or a custom month.
- FR-10: Shows the 10 most recent transactions in a table.
- FR-11: Totals update automatically when the user returns to the dashboard.

### 5.4 Add Entry
- FR-12: Form fields:
  - Entry Type: dropdown (Income, Expense)
  - Category: dropdown (managed list)
  - Payment Mode: dropdown (managed list)
  - Amount: number, must be greater than 0, up to 2 decimal places
  - Date: defaults to today, format DD-Mon-YYYY (example: 12-Oct-2026)
  - Note: optional text, up to 200 characters
- FR-13: Required fields are marked, and errors are shown next to the field.
- FR-14: "Save" writes the entry to the correct Excel file (see 5.6).
- FR-15: "Clear" resets the form.
- FR-16: After a successful save, a confirmation message is shown.

### 5.5 Manage Lists (Dropdown Options)
- FR-17: The user can view, add, edit, and deactivate items in each dropdown list.
- FR-18: Lists managed: Entry Type (fixed: Income, Expense), Category, Payment Mode.
- FR-19: Adding a new item to a list makes it appear in the Add Entry dropdown immediately.
- FR-20: Duplicate items (case-insensitive) are not allowed.
- FR-21: Deleting a list item is replaced by "Deactivate." Old entries that used it still display correctly.

### 5.6 Data Storage in Excel
- FR-22: Each day with entries has its own Excel file.
- FR-23: File location pattern:
  ```
  <DataFolder>\<YYYY>\<MM-Mon>\<DD-Mon-YYYY>.xlsx
  Example: Documents\ExpenseLedger\2026\10-Oct\12-Oct-2026.xlsx
  ```
- FR-24: Each file has one sheet named "Entries" with these columns:
  ID | Date | Type | Category | Payment Mode | Amount | Note | Created At
- FR-25: The file is created automatically the first time an entry is saved for that day.
- FR-26: Dates inside the file also use DD-Mon-YYYY.
- FR-27: If an Excel file is open in Excel when saving, the app shows a clear message and does not lose the entry.

### 5.7 Date Format (Global Rule)
- FR-28: DD-Mon-YYYY is used everywhere: screens, Excel files, folder names, and logs.
- FR-29: Examples: 12-Oct-2026, 01-Jan-2027.

---

## 6. Non-Functional Requirements

- NFR-1 Platform: Windows 10 (64-bit) and later.
- NFR-2 Python version: 3.11 or newer for development.
- NFR-3 Performance: Saving an entry and loading the dashboard should each take less than 1 second for up to 10,000 entries.
- NFR-4 Reliability: No entry is lost if the app closes unexpectedly while saving.
- NFR-5 Security: Passwords are hashed with PBKDF2 (standard library). Login data is stored in the user's AppData folder, not in the project or the Excel data folder.
- NFR-6 Usability: Every page must be usable with mouse and keyboard (Tab key moves between fields, Enter saves).
- NFR-7 Maintainability: Code is split into layers (see Architecture.md) so the storage layer can be replaced later.

---

## 7. Deliverables

| # | Deliverable | Format |
|---|-------------|--------|
| 1 | Expense Ledger application | Source code (Python) |
| 2 | Standalone program | `ExpenseLedger.exe` (PyInstaller) |
| 3 | Installer | `ExpenseLedger-1.0.0.msi` |
| 4 | Documentation | PRD.md, Architecture.md, Rules.md, Design.md, Tasks.md |

---

## 8. Future Scope (Version 2+)

- FastAPI backend with PostgreSQL database.
- Next.js website as a second frontend.
- Multiple users with separate accounts and data.
- Sync between desktop app and website.
- Reports export (PDF).

Version 1 must be built so that the storage layer can be swapped for PostgreSQL without rewriting the screens.

---

## 9. Success Criteria

- The user can add an income and an expense entry in under 30 seconds.
- The dashboard totals match the sum of the Excel files.
- A new dropdown item added in Manage Lists appears in Add Entry right away.
- The MSI installs and uninstalls cleanly on a Windows 10 machine without Python.
