# Roadmap: Expense Ledger

Version: 1.0
Platform: Windows 10 (64-bit)
Language: Python 3.11+
UI: CustomTkinter
Storage (v1): Excel files (.xlsx) by date
Date format everywhere: DD-Mon-YYYY (example: 12-Oct-2026)

---

## 1. Project Overview

A Windows desktop ledger for recording income and expenses. It has a login, a dashboard with totals, an Add Entry form using dropdowns, and a Manage Lists page to control those dropdowns. Each entry is saved to an Excel file for its date.

Version 1 runs locally on each device. Version 2 adds a FastAPI backend, PostgreSQL, a Next.js website, and multiple users.

---

## 2. Documents and How They Fit Together

Each document answers one question. Read them in this order.

| Order | Document | Question it answers | Status |
|-------|----------|---------------------|--------|
| 1 | PRD.md | What should the app do? | Done |
| 2 | Architecture.md | How is the code organized? | Ready to write |
| 3 | Rules.md | How do we write and check code? | Ready to write |
| 4 | Design.md | What does each screen look like? | Ready to write |
| 5 | Tasks.md | What do we build next, step by step? | Ready to write |
| 6 | Roadmap.md | What is the big picture and timeline? | This document |

Flow:
PRD → Architecture → Rules → Design → Tasks → Build → Test → Package → Release → v2

---

## 3. Phases at a Glance

| Phase | Name | Main output | Depends on |
|-------|------|-------------|------------|
| 0 | Setup | Working Python environment | Nothing |
| 1 | Foundation | Folders, paths, date helpers, empty window | Phase 0 |
| 2 | Login | Account creation and login with lock | Phase 1 |
| 3 | Navigation | Sidebar and page switching | Phase 2 |
| 4 | Manage Lists | Editable dropdown lists | Phase 3 |
| 5 | Add Entry | Validated form that uses dropdowns | Phase 4 |
| 6 | Excel Storage | Daily Excel files saved and read | Phase 5 |
| 7 | Dashboard | Income, expense, and balance totals | Phase 6 |
| 8 | Testing | Tests pass, speed checked | Phase 7 |
| 9 | Packaging | EXE and MSI installer | Phase 8 |
| 10 | Release | Version 1.0 for your devices | Phase 9 |
| 11 | Version 2 Planning | FastAPI, PostgreSQL, Next.js | Phase 10 |

Note: Phases 4 and 5 can be partly done in parallel once the UI shell is ready, but building in order is easier for a beginner.

---

## 4. Timeline (Estimated for a Beginner)

These are estimates for part-time work of about 1 to 2 hours per day. Adjust them to your pace.

| Weeks | Phases | Milestone |
|-------|--------|-----------|
| Week 1 | 0, 1 | Project runs with an empty window |
| Week 2 | 2, 3 | Login works and pages switch |
| Week 3 | 4, 5 | Lists and Add Entry form save to memory |
| Week 4 | 6 | Entries saved to Excel by date |
| Week 5 | 7 | Dashboard shows correct totals |
| Week 6 | 8, 9 | Tests pass; EXE and MSI built |
| Week 7 | 10 | Version 1.0 installed on your devices |

Total estimate: about 7 weeks for Version 1.

---

## 5. Milestones and Checkpoints

Each milestone is a point where the app can be run and checked by you.

- **M1 – Hello Window:** App opens with a blank window. (End of Phase 1)
- **M2 – Secure Entry:** You can create an account and log in. (End of Phase 2)
- **M3 – Navigable App:** Sidebar switches between all pages. (End of Phase 3)
- **M4 – Usable Form:** Add Entry works with dropdowns and validation. (End of Phase 5)
- **M5 – Data on Disk:** A saved entry appears in the correct Excel file. (End of Phase 6)
- **M6 – Full Ledger:** Dashboard totals match the Excel data. (End of Phase 7)
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
- Next.js website
- Multiple user accounts with separate data
- Optional: migration tool to move Excel data into PostgreSQL

---

## 7. Version 2 Roadmap (Planned)

| Phase | Name | Main output |
|-------|------|-------------|
| V2.1 | API design | Endpoints for entries, lists, and summary |
| V2.2 | FastAPI backend | Working API with tests |
| V2.3 | PostgreSQL | Database schema and migrations |
| V2.4 | Data migration | Import existing Excel data |
| V2.5 | Auth for web | Token-based login for multiple users |
| V2.6 | Next.js website | Dashboard and Add Entry pages |
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
| Dropdown changes break old entries | Wrong data shown | Deactivate instead of delete (Rules 14) |
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
| 0 Setup | Not started | |
| 1 Foundation | Not started | |
| 2 Login | Not started | |
| 3 Navigation | Not started | |
| 4 Manage Lists | Not started | |
| 5 Add Entry | Not started | |
| 6 Excel Storage | Not started | |
| 7 Dashboard | Not started | |
| 8 Testing | Not started | |
| 9 Packaging | Not started | |
| 10 Release | Not started | |

---

## 12. Next Step

Create the remaining documents (Architecture.md, Rules.md, Design.md, Tasks.md) and then start Phase 0, task T0.1.
