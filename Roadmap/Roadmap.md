# Roadmap: Expense Ledger

Version: 1.2
Platform: Windows 10 (64-bit)
Language: Python 3.11+
UI: CustomTkinter
Storage (v1): Excel files (.xlsx) by date
Date format everywhere: DD-Mon-YYYY (example: 20-Oct-2026)

Revision 1.1: Updated to match the Customer Requirement Specification CX-REQ-2026-v1.0 and the customer corrections. Main Entry (main heads and sub-heads), Expense Report, and sub-head management replace the earlier Add Entry, Manage Lists, and Dashboard screens.

Revision 1.2: The design was approved after testing the mockup `Design/standalone-dairy-app.html` (24-Oct-2026). Design.md is now version 1.2 and matches the mockup's dark theme. Added: Change Password (PRD FR-37 to FR-41), table pagination (FR-18a), bundled fonts (NFR-8), the rule that no screen shows a file location (NFR-9), and inline edit with Main Head and Sub-Head dropdowns (FR-22, customer change request).

---

## 1. Project Overview

A Windows desktop app for recording daily collection and expense entries under two main heads (Treesa Agencies and Daily Collection). The Main Entry screen records each entry with a sub-head, date, name, particulars, debit, and credit. The Expense Report lists all entries with search, date range and column filters, inline editing, totals, and monthly and yearly summary cards. Each entry is saved to an Excel file for its date. Sub-heads are added and removed by the user without editing code, and every added sub-head is also written to `%APPDATA%\ExpenseLedger\Defaults\default.js`.

Version 1 runs locally on each device. Version 2 adds a FastAPI backend, PostgreSQL, a Next.js website, and multiple users.

---

## 2. Documents and How They Fit Together

Each document answers one question. Read them in this order.

| Order | Document | Question it answers | Status |
|-------|----------|---------------------|--------|
| 1 | PRD.md | What should the app do? | Revised (v1.2) |
| 2 | Architecture.md | How is the code organized? | Revised (v1.2) |
| 3 | Rules.md | How do we write and check code? | Revised (v1.2) |
| 4 | Design.md | What does each screen look like? | Approved (v1.2), matches the mockup |
| 5 | Tasks.md | What do we build next, step by step? | Revised (v1.2) |
| 6 | Roadmap.md | What is the big picture and timeline? | This document |

Open customer questions (assumptions A1 to A9, mandatory sub-heads, and currency wording) are listed in PRD.md Section 10. They must be answered before Phase 10.

Flow:
PRD → Architecture → Rules → Design → Tasks → Build → Test → Package → Release → v2

---

## 3. Phases at a Glance

| Phase | Name | Main output | Depends on |
|-------|------|-------------|------------|
| 0 | Setup | Working Python environment and date picker | Nothing |
| 1 | Foundation | Folders, paths, date and money helpers, theme file, bundled fonts, empty window | Phase 0 |
| 2 | Login | Account creation, login with lock, and Change Password | Phase 1 |
| 3 | Navigation | Sidebar (Main Entry, Expense Report, Logout) and page switching | Phase 2 |
| 4 | Sub-Heads | Add (+) and remove (−) sub-heads, saved to a file; added sub-heads are also written to `%APPDATA%\ExpenseLedger\Defaults\default.js` | Phase 3 |
| 5 | Main Entry | Main head, sub-head, and entry form with enable and submit rules | Phase 4 |
| 6 | Excel Storage | Daily Excel files saved, read, updated, and deleted | Phase 5 |
| 7 | Expense Report | Search, filters, totals, monthly and yearly summary cards, pagination, inline edit, delete | Phase 6 |
| 8 | Testing | Tests pass, speed checked, specification checked | Phase 7 |
| 9 | Packaging | EXE and MSI installer | Phase 8 |
| 10 | Release | Version 1.0 for your devices; customer questions closed | Phase 9 |
| 11 | Version 2 Planning | FastAPI, PostgreSQL, Next.js | Phase 10 |

Note: Phases 4 and 5 can be partly done in parallel once the UI shell is ready, but building in order is easier for a beginner.

---

## 4. Timeline (Estimated for a Beginner)

These are estimates for part-time work of about 1 to 2 hours per day. Adjust them to your pace.

| Weeks | Phases | Milestone |
|-------|--------|-----------|
| Week 1 | 0, 1 | Project runs with an empty window |
| Week 2 | 2, 3 | Login and Change Password work, and pages switch |
| Week 3 | 4, 5 | Sub-heads can be added and removed; entry form works and stays disabled until a sub-head is chosen |
| Week 4 | 6 | Entries saved to Excel by date |
| Week 5 | 7 | Expense Report shows filtered, paged rows and correct totals |
| Week 6 | 8, 9 | Tests pass; EXE and MSI built |
| Week 7 | 10 | Version 1.0 installed on your devices |

Total estimate: about 7 weeks for Version 1.

---

## 5. Milestones and Checkpoints

Each milestone is a point where the app can be run and checked by you.

- **M1 – Hello Window:** App opens with a blank window. (End of Phase 1)
- **M2 – Secure Entry:** You can create an account, log in, and change the password. (End of Phase 2)
- **M3 – Navigable App:** Sidebar switches between Main Entry, Expense Report, and Logout. (End of Phase 3)
- **M4 – Usable Form:** Sub-heads can be added and removed. Main Entry opens with Daily Collection selected, the fields stay disabled until a sub-head is chosen, and Submit is enabled only for a valid form. Typing `20/10/2026` shows `20-Oct-2026`. (End of Phase 5)
- **M5 – Data on Disk:** A saved entry appears in the correct Excel file. (End of Phase 6)
- **M6 – Full Report:** Expense Report search, filters, totals, monthly and yearly summary cards, pagination, and inline edit match the Excel data. (End of Phase 7)
- **M7 – Installable:** MSI installs and uninstalls on a clean Windows 10 PC. (End of Phase 9)
- **M8 – Release 1.0:** Installed and used on all your devices. (End of Phase 10)

---

## 6. Deliverables by Version

### Version 1.0 (Local Desktop App)
- Source code in the project folder
- `ExpenseLedger.exe` (standalone program)
- `ExpenseLedger-1.0.0.msi` (installer)
- User guide (README.md)
- Planning documents (PRD, Architecture, Rules, Design, Tasks, Roadmap)

### Version 2.0 (Web and Multi-User)
- FastAPI backend with REST endpoints
- PostgreSQL database
- Next.js website with the Dashboard (moved from v1, see PRD Section 9)
- Multiple user accounts with separate data
- Optional: migration tool to move Excel data into PostgreSQL

---

## 7. Version 2 Roadmap (Planned)

| Phase | Name | Main output |
|-------|------|-------------|
| V2.1 | API design | Endpoints for entries, sub-heads, report, and summary |
| V2.2 | FastAPI backend | Working API with tests |
| V2.3 | PostgreSQL | Database schema and migrations |
| V2.4 | Data migration | Import existing Excel data |
| V2.5 | Auth for web | Token-based login for multiple users |
| V2.6 | Next.js website | Main Entry, Expense Report, and Dashboard pages |
| V2.7 | Sync | Desktop app can use the API (optional) |
| V2.8 | Deployment | Hosted API and website |

Design note: the v1 storage layer is kept separate from the screens. This makes the switch to PostgreSQL a change in one layer, not a rewrite.

---

## 8. Risks and How to Handle Them

| Risk | Impact | Mitigation |
|------|--------|------------|
| Excel file is open while saving | Entry not saved | Show a clear message and keep the entry in the form (T6.4) |
| Beginner gets stuck on packaging | Delay at end | Build the EXE early in Phase 9; treat MSI as a separate step |
| Password lost | User locked out | Show a note in the User Guide; provide a reset method in v1.1 |
| Too many features at once | Project never finishes | Stick to the PRD; put new ideas in Future Scope |
| Sub-head changes break old entries | Wrong data shown | Deactivate instead of delete; old entries store the sub-head name (Rules 14) |
| Specification and customer corrections disagree | Wrong screen behavior | Customer corrections win; recorded in PRD Section 10 (A10) |
| Report reads every file; date range narrows only after reading | Report slow with many entries | Speed test in T8.3; add a cache only if needed (Architecture Section 7) |
| Unconfirmed assumptions (PRD Section 10) | Rework after testing | Get answers before Phase 10 (T10.1) |
| Mockup and app look differ | Screens do not match the approved design | Build colours and weights only from `theme.py`, using the values in Design.md Section 1 (Rule 37) |
| Bundled font licence or size | Legal issue or a large installer | Use a font under the SIL Open Font License; keep its licence file with it (NFR-8, T1.4a) |
| File location shown on a screen | Users see internal paths | Check every screen before release (NFR-9, Rule 36, T8.7) |
| Windows SmartScreen warning | Users distrust the exe | Document the warning; code signing is optional later |

---

## 9. Definition of Done

A task or phase is done only when:
1. The feature works on Windows 10.
2. It follows Rules.md.
3. Its screen matches Design.md.
4. Its checkbox is marked in Tasks.md.
5. Any new behavior is reflected in PRD.md.

---

## 10. Change Control

- Changes to requirements go into PRD.md first.
- Changes to structure go into Architecture.md first.
- Each version change is recorded in a CHANGELOG.md file.
- Roadmap.md is updated at the end of each phase with the actual date completed.

---

## 11. Progress Tracker

| Phase | Status | Actual finish date |
|-------|--------|--------------------|
| Design (mockup and Design.md) | Approved | 24-Oct-2026 |
| 0 Setup | Not started | |
| 1 Foundation | Not started | |
| 2 Login | Not started | |
| 3 Navigation | Not started | |
| 4 Sub-Heads | Not started | |
| 5 Main Entry | Not started | |
| 6 Excel Storage | Not started | |
| 7 Expense Report | Not started | |
| 8 Testing | Not started | |
| 9 Packaging | Not started | |
| 10 Release | Not started | |

---

## 12. Next Step

The design is approved, so the build can start. Start Phase 0, task T0.1 in Tasks.md.

Open items that do not block Phases 0 to 3:
- Get the customer's answers to PRD.md Section 10 before Phase 10.
