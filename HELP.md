# Daily Fresh – Help

Daily Fresh is a Windows desktop app for recording daily money in (credit) and money out (debit). Every entry is saved in an ordinary Excel file, so your records stay readable even without the app.

Contents: [1. Installing](#1-installing) · [2. First run](#2-first-run) · [3. Using the app](#3-using-the-app) · [4. Sharing work between users](#4-sharing-work-between-users) · [5. Where your data is](#5-where-your-data-is) · [6. Upgrading and uninstalling](#6-upgrading-and-uninstalling) · [7. Troubleshooting](#7-troubleshooting)

---

## 1. Installing

You need a Windows 10 or 11 PC (64-bit). Python is not needed.

### 1.1 Get the setup file
You will receive `ExpenseLedger-Setup-<version>.exe` (for example `ExpenseLedger-Setup-1.0.3.exe`). Only use a setup you received from the developer.

### 1.2 If Windows blocks it ("Windows protected your PC")
SmartScreen blocks setup files from unknown publishers. Choose one:

- **Click through:** click **More info**, then **Run anyway**.
- **Unblock it first (recommended):** put `Unblock-Setup.bat` and `Unblock-Setup.ps1` in the same folder as the setup and double-click the `.bat`. It removes the "downloaded from the internet" mark from that one file. It needs no administrator rights and changes no Windows setting.
- Files copied to a USB stick formatted FAT32 or exFAT usually lose that mark, so they often run without a warning.

### 1.3 Run the setup wizard
Double-click the setup file and follow the pages:

| Page | What to choose |
|---|---|
| **Install for all users or just me** | *Just me* needs no administrator approval. *All users* installs for every Windows user on the PC and asks for approval. |
| **Welcome / License** | Read and accept to continue. |
| **Install folder** | Keep the default unless you have a reason to change it. |
| **Shortcuts** | Tick *Desktop shortcut* and/or *Start Menu shortcut*. |
| **Publisher (all-users installs only)** | Optional, off by default: *Trust the Tenwin James publisher certificate on this PC*. Tick it only on a PC you manage and only if the thumbprint shown matches the one the developer gave you. It makes Windows show "Tenwin James" as the publisher on later setups. |
| **Finish** | Leave *Launch Daily Fresh* ticked to start the app. |

Daily Fresh then appears in **Settings > Apps > Installed apps**.

### 1.4 Moving the setup on a USB stick
Copy only the setup file (plus the two Unblock files if you want them). Copying `ExpenseLedger.exe` alone will not work, because the app needs the folder beside it; always run the setup on each PC. Your entries and login do not travel with the setup: each PC keeps its own (see [section 5](#5-where-your-data-is) and [section 4](#4-sharing-work-between-users)).

### 1.5 An older version installed with `.msi`
If a version up to 1.0.2 was installed with the old `.msi` installer, the new setup asks to remove it first. Your entries and settings are kept.

---

## 2. First run

1. **Choose a folder for your Excel files.** The app asks once. Pick a folder you can save in (for example on the Desktop or a synced folder). If you used version 1.0 before, it keeps `Desktop\ExpenseLedger` without asking.
2. **Create your account.** Enter a username and a password of at least 8 characters, and repeat the password.
3. **Log in.** The **username matters**: it becomes part of your file names (see section 5), so pick something short and recognisable, such as your first name.

---

## 3. Using the app

The sidebar has **Dashboard**, **Main Entry** (one item for each ledger), **Transaction List** and **Modify Fields**. The round user button at the top right opens **Change Password** and **Logout**.

### 3.1 Main Entry – recording a transaction
1. Click a ledger under *Main Entry* in the sidebar (by default **Treesa Agencies** or **Daily Collection**).
2. Choose the **Transaction** (sub-head) from the list.
3. Enter the **date** (type `20/10/2026` or `20-Oct-2026`, or pick it from the calendar), the **name** and the **particulars**.
4. Enter the **debit** (money out) or **credit** (money in). Amounts use up to two decimals; commas are fine. A blank amount counts as 0.00, but both cannot be zero.
5. Click **Submit**. The button stays disabled until everything is valid, and each problem is shown under its own field.

If the day's Excel file is open in Excel, Windows will not let the app save. The app tells you, keeps your entry in the form and loses nothing: close the file in Excel and click Submit again.

### 3.2 Transaction List – find, check, edit, delete
- Shows every entry **newest first**, with the total debit and credit of the matching rows. Choose 10, 25 or 50 rows per page.
- **Search** matches the name, the particulars or an amount.
- **Filters:** date range (All, This Month, Last Month, This Year, Custom with From/To), Main Entry, Sub-Head, name, particulars, and debit/credit from–to. Click **Filter Report** to apply and **Clear Filters** to reset.
- **Edit** changes a row in place (Esc cancels); **Delete** asks for confirmation first. Changing the date moves the entry to that day's file.
- Rows with a name in the **User** column that is not yours were imported from another person. They are read-only.

### 3.3 Dashboard
Monthly and yearly summaries show total debit and credit and the Transactions with the most and least debit and credit. A bar chart shows each month of the year and each day of the chosen month. The dashboard counts every entry in your data folder, including imported ones.

### 3.4 Modify Fields
Add, rename and remove ledgers (Main Entries) and their Transactions (sub-heads). Removing hides an item but never deletes it, and renaming keeps old rows linked, so history stays correct. At least one ledger must stay.

### 3.5 Passwords and locking
Five wrong password tries lock the login for 5 minutes. The lock survives closing the app. **Change Password** is in the user menu.

---

## 4. Sharing work between users

Each person has their own Excel files. To let others see your work, export it; they import it.

**Export** (Transaction List, buttons above the table)
- **Export CSV:** a spreadsheet-friendly file that can be imported by others.
- **Export PDF:** a printable landscape report with totals.
- Both export the rows your **current filters show** (everything if no filter is set). Set the filters first if you only want a month or a Main Entry.

**Import CSV**
1. Receive the CSV from the other person (USB, shared folder, email).
2. Click **Import CSV** and choose the file.
3. The app checks every row. If any row is invalid, **nothing** is imported and the message names the line.
4. Good rows are saved into files named with the other person's username, shown in the **User** column, and counted on the Dashboard. They cannot be edited or deleted here.
5. Importing the same file again adds nothing, so it is safe to import a person's newer export on top of an older one.

Only import CSV files exported by Daily Fresh from people you trust.

---

## 5. Where your data is

| What | Where |
|---|---|
| **Daily Excel files** | The folder you chose on first run, in `<year>\<MM-Mon>\`, one file per day per user, named like `20-Oct-2026_tenwin.xlsx` |
| **Login, Main Entries, Transactions list, settings** | `%APPDATA%\ExpenseLedger` (open it by typing that into the Explorer address bar) |
| **Speed-up index** | `%APPDATA%\ExpenseLedger\entries-index.db` – only a cache; safe to delete, it is rebuilt from the Excel files |
| **Automatic backups** | `%APPDATA%\ExpenseLedger\Backups` – made before the app changes saved files to a newer format; the newest five are kept |
| **Log** | `%APPDATA%\ExpenseLedger\app.log` |

Your Excel files are the real records – back up the data folder the way you back up any important folder. You can open the files in Excel to read or sum them; avoid editing them by hand, and close them before you save new entries in the app.

---

## 6. Upgrading and uninstalling

**Upgrade:** run the newer setup over the old install. It closes the running app, replaces the program and keeps all your data. On first start the app may rename old Excel files to include your username and copies the originals to `Backups` first.

**Uninstall:** use **Settings > Apps > Installed apps > Daily Fresh**.
- Your **entries and Transactions lists are kept**.
- Your **login is removed**, so after a reinstall the app asks you to create a new username and password.
- If you ticked the publisher-certificate option during setup, that certificate is removed too.

---

## 7. Troubleshooting

| Problem | What to do |
|---|---|
| Windows says "Windows protected your PC" | See [1.2](#12-if-windows-blocks-it-windows-protected-your-pc). |
| "The Excel file for 20-Oct-2026 is open…" | Close that day's file in Excel, then click Submit again. Your entry is still in the form. |
| "Too many attempts. Try again in …" | Wait for the time shown. The lock is 5 minutes. |
| Forgot the password | There is no reset. Uninstall and reinstall the app: that removes the login only. Create a new account when asked; your entries are kept. Use the same username so your file names stay the same. |
| Import says "not an export from this app" | The file was not made by Export CSV, or its column headings were changed. Ask for a fresh export. |
| Import says "Line N: …" | Row N has an invalid date, amount, ID or a blank required field. Fix or re-export; nothing was imported. |
| The Transaction List looks out of date | Open another page and come back, or restart the app. If it still looks wrong, delete `entries-index.db` (section 5) and start the app; it rebuilds itself. |
| "This folder cannot be used" on first run | Choose a folder you can create files in (not a protected system folder). |
| Wrong data folder chosen | Your Excel files stay where they were. Copy them into the new folder (keeping the year\month folders), or restore the old folder. |

**Still stuck?** Note the exact message on screen and the contents of `%APPDATA%\ExpenseLedger\app.log`, and send both to the developer, Tenwin James.
