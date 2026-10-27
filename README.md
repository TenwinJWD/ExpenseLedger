# Expense Ledger

A Windows desktop app for recording daily collection and expense entries under two main heads, keeping every entry in Excel files by date, and reviewing them in an Expense Report.

Developed by **Tenwin James**.

> Status: planning and design are complete (version 1.1). The app itself is not built yet. This README will be replaced by the full user guide in task T10.2.

---

## What the app does

- **Login:** the first run creates one account (username and password). Five wrong passwords lock the login for 5 minutes.
- **Main Entry:** choose a main head, then a sub-head, then enter the date, name, particulars, debit, and credit.
  - Main heads: **Treesa Agencies** and **Daily Collection** (Daily Collection is selected when the page opens).
  - Sub-heads come from the lists in `Defaults/default.js` (48 for Treesa Agencies and 22 for Daily Collection). You can add sub-heads with **+** and remove them with **−**.
  - The fields stay disabled until a sub-head is chosen. Submit stays disabled until the entry is valid.
  - Dates can be typed as `20-Oct-2026` or `20/10/2026`, or picked from the calendar. They always display as `20-Oct-2026`.
- **Expense Report:** all entries, oldest first.
  - Search by name, particulars, or amount.
  - Filter by date range (This Month, Last Month, This Year, or a custom range), main head, sub-head, name, particulars, and debit or credit amounts.
  - Edit a row with the pencil icon, and delete a row after confirming.
  - Totals for the rows shown.
  - Monthly and yearly summary cards: the total debit and credit, plus the most and least debited and credited sub-heads, with their amounts.

---

## Where data is stored

| What | Where |
|---|---|
| Daily entries (Excel) | `Documents\ExpenseLedger\<YYYY>\<MM-Mon>\<DD-Mon-YYYY>.xlsx` |
| Login account | `%APPDATA%\ExpenseLedger\account.json` (the password is stored as a hash, never as plain text) |
| Sub-heads | `%APPDATA%\ExpenseLedger\subheads.json` |
| Added sub-heads (list copy) | `%APPDATA%\ExpenseLedger\Defaults\default.js` |
| Log | `%APPDATA%\ExpenseLedger\app.log` |

Uninstalling removes the program and your login. Your entries and sub-heads are kept. After a reinstall, the app asks you to create a new user and password.

---

## Requirements

- Windows 10 (64-bit) or later
- Python 3.11 or newer (only for development; the installed program does not need Python)
- Approximate space: about 40 to 60 MB for the program, plus a few MB per year of entries
- Approximate memory: about 50 to 150 MB while running

---

## Development setup

The project uses a virtual environment in `.venv`.

```
python -m venv .venv
.venv\Scripts\activate
```

Packages are listed in `requirements.txt` (the app) and `requirements-dev.txt` (tests and packaging). These files are added in tasks T0.3 and T0.4.

The packaged program is built from this environment, so the build includes the libraries from `.venv`. The `.venv` folder itself is not part of the program and is excluded from Git.

---

## Packaging and uninstall

- `ExpenseLedger.exe` is built with PyInstaller.
- `ExpenseLedger-Setup-1.0.0.exe` is a single setup program. It shows the license, then installs for the current user (no administrator rights) with a desktop shortcut and a Start Menu entry. It installs the `ExpenseLedger-1.0.0-CurrentUser.msi` inside it.
- `ExpenseLedger-1.0.0.msi` is the installer, built with WiX Toolset v4. The install dialog asks **Just me** (the default: installs for the current user, no administrator rights) or **Anyone who uses this computer** (installs for all users, needs administrator rights). A desktop shortcut and a Start Menu entry are added for the chosen user.
- To uninstall, use **Settings > Apps > Installed apps > Expense Ledger**, or run `installer\uninstall.bat`. Both keep your data.
- **Windows SmartScreen warning:** an unsigned build triggers "Windows protected your PC" and may be quarantined by Windows Defender. Release builds should be digitally signed with `installer\sign.ps1` (see **Release checklist** below). For an unsigned build, click **More info**, then **Run anyway**. Only do this for the installer you received from the developer.

### Release checklist (avoid Defender and SmartScreen blocks)

1. Build with PyInstaller using the latest release. `upx=False` is set in `ExpenseLedger.spec` (UPX-packed files are flagged more often). Keep one-folder mode.
2. `.\installer\sign.ps1 -Stage Exe <certificate options>`, then rebuild the MSI files.
3. `.\installer\sign.ps1 -Stage Msi ...`, then rebuild the Burn setup.
4. `.\installer\sign.ps1 -Stage Setup ...` (detaches, signs and reattaches the Burn engine, then signs the setup).
5. `.\installer\sign.ps1 -Stage Verify` and keep the SHA-256 hashes it prints. Publish them with the download.
6. Scan the files at virustotal.com.
7. Submit each release to Microsoft as a software developer at https://www.microsoft.com/wdsi/filesubmission.
8. Publish over HTTPS from a stable URL, with the same certificate and publisher name (Tenwin James) every release.

---

## Releasing a new version (upgrades)

1. Set `APP_VERSION` in `Build/1.0/app/core/config.py`. This is the only place the version is typed. `build.ps1` copies it into the exe properties, the MSI and the setup EXE.
2. Add a `## <version>` entry to `CHANGELOG.md`. A test fails if it is missing.
3. Never change the two `UpgradeCode` values in `installer/Product.wxs` and `installer/Bundle.wxs`, or the component GUIDs in `installer/component_guids.json`. A test guards the codes.
4. If the saved file format changes: raise `DATA_VERSION` in `app/storage/migrations.py` and add a migration function for the old version. Start-up backs up the files, runs the migration, and stops without changing anything if it fails.
5. Run `.\build.ps1`. Installing the new setup over an old install replaces the program and keeps all data.
6. To announce the release in the app, upload a `version.json` such as `{"version": "1.1.0", "url": "https://.../ExpenseLedger-Setup-1.1.0.exe", "notes": "What is new"}` to a web address, and set `UPDATE_URL` in `config.py` to it (https only). Users then see an "Update to 1.1.0" button in the sidebar that opens the download.

## Project documents

All planning documents are in the `Roadmap` folder:

| Document | Purpose |
|---|---|
| `Roadmap/PRD.md` | What the app should do (requirements and open questions) |
| `Roadmap/Architecture.md` | How the code is organized and where data is stored |
| `Roadmap/Rules.md` | How code is written and checked |
| `Roadmap/Design.md` | What each screen looks like |
| `Roadmap/Tasks.md` | The step-by-step build list (tasks T0.1 to T10.6) |
| `Roadmap/Roadmap.md` | The big picture, timeline, and milestones |

A clickable design mockup is in `Design/standalone-dairy-app.html`. Open it in a browser. Its data is stored in that browser only.

---

## Open questions for the customer

These are listed in `Roadmap/PRD.md` Section 10. The main one that changes the app's behavior:

- Which sub-heads are mandatory (they cannot be removed).

---

## Credits

Developed by **Tenwin James**.
