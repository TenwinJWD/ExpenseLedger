# Design: Expense Ledger (Version 1.2)

Version: 1.2
Status: Draft (matches the mockup `Design/standalone-dairy-app.html`, palette v1.7)
Read after: PRD.md, Architecture.md, Rules.md

This document describes what each screen looks like and how it behaves. The layout, labels, and behavior come from the Customer Requirement Specification CX-REQ-2026-v1.0 (Sections 1 to 4), with the customer corrections applied. The look (colors, weights, spacing, popups, pagination) follows the finished mockup, `Design/standalone-dairy-app.html`. Where the mockup and this document differ, the mockup is the reference for how a screen looks, and this document is the reference for the rules.

The app never shows a file location (folder, AppData path, or file name) as text on any screen (PRD NFR-9).

---

## 1. Look and Feel

### 1.1 Theme

The app uses a dark theme only in v1. The palette has layered blacks, soft white text, blue primary actions, and red for debit and errors. Use these names in code (`theme.py`). Each name maps to the CSS variable in the mockup shown in the last column.

| Role | Name in code | Hex | Mockup variable | Used for |
|------|--------------|-----|-----------------|----------|
| Page top | `PAGE_TOP` | `#141419` | `--page-top` | Top of the page gradient |
| Page bottom | `PAGE_BOTTOM` | `#0B0B0E` | `--page-bottom` | Bottom of the page gradient |
| Page background | `BG_PAGE` | `#0C0C0F` | `--bg-page` | Solid fallback under the gradient |
| Card top | `CARD_TOP` | `#1B1B22` | card gradient | Top of each card |
| Card bottom | `CARD_BOTTOM` | `#131317` | card gradient | Bottom of each card |
| Card | `BG_CARD` | `#151519` | `--bg-card` | Popups, solid card fallback |
| Input | `BG_INPUT` | `#1C1C22` | `--bg-input` | Text boxes, dropdowns, table inputs |
| Border | `BORDER_SOFT` | `#26262E` | `--border-soft` | Card and sidebar edges |
| Input border | `INPUT_BORDER` | `#34343E` | `--input-border` | Text boxes and dropdowns |
| Sidebar top | `SIDE_TOP` | `#1A1A21` | `--side-top` | Top of the sidebar gradient |
| Sidebar bottom | `SIDE_BOTTOM` | `#0A0A0D` | `--side-bottom` | Bottom of the sidebar gradient |
| Sidebar text | `SIDEBAR_TEXT` | `#E4E4E7` | `--sidebar-text` | Sidebar items and footer |
| Primary top | `BTN_TOP` | `#4F8CFF` | `--btn-top` | Top of the primary button gradient, active bar |
| Primary bottom | `BTN_BOTTOM` | `#2563EB` | `--btn-bottom` | Bottom of the primary button gradient |
| Primary | `PRIMARY` | `#2563EB` | `--primary` | Primary buttons, focus |
| Primary hover | `PRIMARY_HOVER` | `#1D4ED8` | `--primary-hover` | Hover on primary buttons |
| Primary light | `PRIMARY_LIGHT` | `#18203A` | `--primary-light` | Summary cards, highlights |
| Text | `TEXT` | `#F4F4F5` | `--text` | Headings, labels, body text (soft white) |
| Text muted | `TEXT_MUTED` | `#8B8B98` | `--muted` | Hints, secondary text, card labels |
| Table header | `SURFACE_TINT` | `#1C1C22` | `--surface-tint` | Table headers, totals, pager bar |
| Table row line | `ROW_BORDER` | `#22222A` | `--row-border` | Lines between table rows |
| Disabled | `DISABLED_BG` | `#17171B` | `--disabled-bg` | Disabled fields and buttons |
| Disabled text | `DISABLED_TEXT` | `#4A4A55` | `--disabled-text` | Disabled labels and text |
| Debit | `DEBIT` | `#FB7185` | `--debit` | Debit amounts |
| Credit | `CREDIT` | `#34D399` | `--credit` | Credit amounts, success text |
| Error light | `ERROR_BG` | `#2A1218` | `--error-bg` | Error message background |
| Error text | `ERROR` | `#FB7185` | `--error` | Field error messages |
| Success light | `SUCCESS_BG` | `#0E2620` | `--success-bg` | Success message and toast background |
| Warning light | `WARNING_BG` | `#2A2310` | `--warning-bg` | Warning message background |
| Warning text | `WARNING` | `#FBBF24` | `--warning` | Warning message text |
| Scrim | `SCRIM` | `rgba(0, 0, 0, 0.6)` | backdrop | Dims the page behind popups |
| Focus ring | `FOCUS_RING` | `rgba(79, 140, 255, 0.25)` | focus shadow | 3 px ring on focused fields |

### 1.2 Typography

- Font: Segoe UI, the Windows system font (PRD NFR-8). Nothing is bundled or installed. The mockup uses the same font.
- Weights (the mockup's levels, shown in the font's heaviest available weight):
  - Page titles, popup titles, the sidebar app name, card titles: Black (900).
  - Field labels, table headers, card labels, summary card values, totals: Black (900).
  - Primary buttons and secondary buttons: Black (900).
  - Navigation items: ExtraBold (800); the active item: Black (900).
  - Body text, hints, and page descriptions: SemiBold (600).
  - Debit and credit amounts, summary sub-values, and message bars: ExtraBold (800).
- Sizes: page title 22; popup and card titles 15 to 16; body 13; field labels and table headers 11 uppercase with letter spacing 0.04 em; hints 11.
- Page titles use a slightly tighter letter spacing (-0.02 em).
- Amounts use a monospace font (Consolas on Windows), right-aligned, two decimals with thousands separators.

### 1.3 Shape, Depth, and Spacing

- **Layers:** the page is the deepest layer, cards sit one layer above it, and input boxes and popups sit above the cards. Each layer is a shade lighter than the one below.
- **Cards:** radius 16, 1 px `BORDER_SOFT` outline, 20 px padding, a vertical gradient from `CARD_TOP` to `CARD_BOTTOM`, a 1 px lit top edge, and a deep shadow (about 18 px down, 40 px blur, black at 90%). Gap between cards: 16 px.
- **Page background:** a vertical gradient from `PAGE_TOP` to `PAGE_BOTTOM`, with two faint blue glows: one in the top-right corner and one in the bottom-left corner. The page does not scroll the sidebar (see Section 2).
- **Buttons:** radius 10, height 36, horizontal padding 16. Primary buttons have a blue vertical gradient (`BTN_TOP` to `BTN_BOTTOM`), uppercase white text, and a soft blue glow beneath (about 8 px down, 20 px blur, blue at 70%). Secondary buttons are `BG_CARD` with an `INPUT_BORDER` outline.
- **Inputs and dropdowns:** radius 8, height 36, 1 px `INPUT_BORDER`, background `BG_INPUT`. The focus state uses a `PRIMARY` border and a 3 px `FOCUS_RING`.
- **Table cells:** inputs in edit mode are radius 6, height 32, background `BG_INPUT`.
- **Minimum window size:** 1000 × 640 px. The page content scrolls if the window is smaller.

### 1.4 Disabled State

A disabled field or button uses `DISABLED_BG` with `DISABLED_TEXT` and ignores clicks (Rule 24). The label "Select a Sub-Head to enable entry." under the Sub-Head dropdown explains why the fields are disabled.

---

### 1.5 Windows Build Notes (how the screens are built)

These rules keep the Windows app close to the mockup. They were set after the first build was compared with the mockup on 25-Oct-2026.

- **Cards:** login, create-account, and popup cards keep their size (420 px wide). Layout containers use plain frames (no default height), so content does not stretch.
- **Dropdowns:** every dropdown is the styled dropdown box (`SelectBox`). It opens a list with hover highlights and a selected row in `PRIMARY_LIGHT`. Lists with more than 8 items show a search box at the top. The system menu is not used.
- **Icons:** pencil, delete, tick, and calendar use the Windows icon font (Segoe MDL2 Assets). Emoji are not used, because they show as empty boxes in Segoe UI. The Change Password key is drawn as a white line icon.
- **Sidebar:** the app name and version, then Main Entry and Expense Report together, directly under the header. Change Password, Logout, and the developer footer sit at the bottom.
- **Font weights:** Tkinter has only normal and bold. The mockup's Black and ExtraBold weights therefore show as bold in the app.
- **Gradients:** Tkinter cannot draw CSS gradients. The app uses solid colours from `theme.py`, with the nearest mid-tone for each gradient.

---

## 2. Main Layout

After login, every page uses the same frame.

```
+------------------+-----------------------------------------------+
|  Expense Ledger  |  Page title                                   |
|  Version 1.0.0   |  Short description line                       |
|                  |                                               |
|  ✎ Main Entry    |  [ Page content in cards ]                    |
|  ▤ Expense Report|                                               |
|                  |                                               |
|                  |                                               |
|  🔑 Change Pass- |                                               |
|     word         |                                               |
|  ⏻ Logout        |                                               |
|                  |                                               |
|  Developed by    |                                               |
|  Tenwin James    |                                               |
+------------------+-----------------------------------------------+
```

- **Sidebar**: width 220 px, full window height, fixed while the content scrolls. It never scrolls itself; its contents fit the window height.
  - Background: a vertical gradient from `SIDE_TOP` to `SIDE_BOTTOM`, with a 1 px `BORDER_SOFT` right edge, an inner highlight, and a soft shadow on the right side so the sidebar looks raised above the content.
  - App name at the top: "Expense Ledger" in Black weight, with "Version 1.0.0" below in muted text. A `BORDER_SOFT` line separates the header from the menu.
  - Menu items, in this order: Main Entry (✎), Expense Report (▤), then **Change Password** (text only, see Section 2.1), then Logout (⏻). The icons for Main Entry, Expense Report, and Logout are text symbols, and the key icon is an SVG so it can take the sidebar text colour (PRD FR-6, FR-37, FR-5).
  - Hover: a light tint (white at 14%). Active item: a stronger tint (white at 22%) and a 4 px `BTN_TOP` bar on its left edge.
  - Footer at the bottom of the sidebar: "Developed by Tenwin James" in small type (PRD FR-34).
- **Content area**: background is the page gradient, padding 24 px.
- Main Entry is the default page after login (PRD FR-7).
- On narrow windows (under 760 px) the sidebar becomes a top bar that wraps. It is no longer fixed.

### 2.1 Change Password Button and Popup

- The button sits directly above Logout, on every page (PRD FR-37). It is not a page.
- The popup is 420 px wide, centered, over a dimmed page (`SCRIM`, blurred 4 px).

```
+----------------------------------------------+
|  Change Password                         ✕   |
|                                              |
|  CURRENT PASSWORD *                          |
|  [ ________________________________ ]        |
|  Wrong current password. 4 tries left.       |
|                                              |
|  NEW PASSWORD *                              |
|  [ ________________________________ ]        |
|  At least 8 characters, different from the   |
|  current password.                           |
|                                              |
|  CONFIRM NEW PASSWORD *                      |
|  [ ________________________________ ]        |
|                                              |
|            [ CANCEL ]   [ SAVE ]             |
+----------------------------------------------+
```

- **SAVE** is disabled until all three fields have a value (PRD FR-38).
- A wrong current password counts toward the 5-attempt lock, and the error shows the tries left (PRD FR-39).
- Errors appear under the field they belong to (Rule 25). Enter in the last field saves when SAVE is enabled.
- On success, the popup closes and a toast appears in the bottom-right corner: "Password changed." It stays for about 3 seconds (PRD FR-41).

---

## 3. Screen: Create Account (first run only)

Shown only when no account exists (PRD FR-2). Not in the specification; the design follows the login screen.

```
+-----------------------------------------------------+
|                 Expense Ledger                      |
|       Create your account to get started            |
|                                                     |
|   +---------------------------------------------+   |
|   | USERNAME *                                  |   |
|   | [ ___________________________________ ]     |   |
|   |                                             |   |
|   | PASSWORD *                                  |   |
|   | [ ___________________________________ ]     |   |
|   | Use at least 8 characters.                  |   |
|   |                                             |   |
|   | CONFIRM PASSWORD *                          |   |
|   | [ ___________________________________ ]     |   |
|   |                                             |   |
|   | [        CREATE ACCOUNT        ]            |   |
|   +---------------------------------------------+   |
+-----------------------------------------------------+
```

- The card is centered, 420 px wide, with the page gradient behind it. The title is Black weight.
- Required fields are marked with `*` in the error colour.
- Errors appear under the field (Rule 25): username empty, password under 8 characters, passwords do not match.
- Enter in the last field submits.
- On success, the login screen shows "Account created. Please log in." in `SUCCESS_BG`.

---

## 4. Screen: Login

Shown on every start after the account exists (PRD FR-1).

```
+-----------------------------------------------------+
|                 Expense Ledger                      |
|                 Please log in                       |
|                                                     |
|   +---------------------------------------------+   |
|   | USERNAME                                    |   |
|   | [ ___________________________________ ]     |   |
|   |                                             |   |
|   | PASSWORD                                    |   |
|   | [ ___________________________________ ]     |   |
|   |                                             |   |
|   | [ LOGIN ]                                   |   |
|   |                                             |   |
|   | Wrong username or password. 4 tries left.   |   |
|   +---------------------------------------------+   |
+-----------------------------------------------------+
```

- The error message does not say which field was wrong.
- After 5 failures, the login button is disabled and this message shows: "Too many attempts. Try again in 4 min 12 sec." The countdown updates every second (PRD FR-4).
- Enter submits.

---

## 5. Screen: Main Entry

The default page (PRD FR-7). Layout follows the specification's "Main Entry Form View" (Section 1).

```
+-------------------------------------------------------------------+
|  Main Entry                                                       |
|  Record a daily collection or a Treesa Agencies entry             |
|                                                                   |
|  +-------------------------------------------------------------+  |
|  | MAIN HEAD                                                   |  |
|  | ( ) Treesa Agencies        (•) Daily Collection             |  |
|  |                                                             |  |
|  | SUB-HEAD                                                    |  |
|  | [ -Select-                                 ▼ ]  [ + ] [ − ] |  |
|  | Select a Sub-Head to enable entry.                          |  |
|  |                                                             |  |
|  | DATE *                 NAME *                               |  |
|  | [ DD-Mon-YYYY  📅 ]    [ ______________________________ ]    |  |
|  |                                                             |  |
|  | PARTICULARS *                                               |  |
|  | [ ____________________________________________________ ]    |  |
|  |                                                             |  |
|  | DEBIT *                    CREDIT *                         |  |
|  | [ 0.00            ]        [ 0.00                     ]     |  |
|  |                                                             |  |
|  |                       [ CLEAR ]   [   SUBMIT   ]            |  |
|  +-------------------------------------------------------------+  |
|                                                                   |
|  ( message bar: "Entry saved to 20-Oct-2026." in SUCCESS_BG )     |
+-------------------------------------------------------------------+
```

### 5.1 Main Head
- Two options shown as radio buttons: **Treesa Agencies** (MH 1) and **Daily Collection** (MH 2).
- **Daily Collection is selected by default** when the page opens (customer correction; PRD FR-10).
- Changing the Main Head resets the Sub-Head to "-Select-", because the two sub-head lists are different.

### 5.2 Sub-Head
- Dropdown with "-Select-" as the first item, followed by the active sub-heads of the selected Main Head.
- **"-Select-" is the default value** when the page opens, and it stays that way until the user picks a sub-head (customer correction; PRD FR-11). This is the same for all select fields on the entry form.
- Buttons beside it:
  - **+** opens the add popup (Section 5.4).
  - **−** removes the selected sub-head after confirmation (Section 5.5). It is disabled when "-Select-" is chosen.
- Helper text below the dropdown: "Select a Sub-Head to enable entry." It hides once a sub-head is chosen.

### 5.3 Transaction Fields
- Date, Name, Particulars, Debit, and Credit are **disabled** while the Sub-Head is "-Select-". They become enabled when a sub-head is chosen (customer correction; PRD FR-12).
- **Submit is disabled** until the form is valid (PRD FR-14). It is also disabled while the Sub-Head is "-Select-", even if the other fields are filled.
- **Date**:
  - Shows `DD-Mon-YYYY` (example: `20-Oct-2026`).
  - A calendar button (📅) opens a date picker. Picking a date fills the field.
  - The user can type a date. `20/10/2026` is accepted and changed to `20-Oct-2026` when the field loses focus.
  - Any other text shows the error "Enter a date as 20-Oct-2026 or 20/10/2026."
  - The field is empty until a date is entered; it is not filled with today's date.
- **Name**: up to 100 characters.
- **Particulars**: up to 200 characters.
- **Debit** and **Credit**: start empty and show a grey 0.00 placeholder. A blank amount counts as 0.00. Accept digits and one decimal point, two decimals at most, 0.00 or more. Errors show under the field (Rule 25).
- If both Debit and Credit are 0.00, Submit stays disabled and the hint "Enter a Debit or Credit amount greater than 0.00." shows under the two amount fields.
- Labels with `*` are mandatory.

### 5.4 Add Sub-Head Popup (+)

```
+----------------------------------------------+
|  Add Sub-Head                            ✕   |
|                                              |
|  SUB-HEAD NAME *                             |
|  [ ________________________________ ]        |
|  Up to 40 characters.                        |
|  Adds to the Treesa Agencies list.           |
|  Stored value: sample_name                    |
|                                              |
|            [ CANCEL ]   [ ADD ]              |
+----------------------------------------------+
```

- The popup shows which Main Head list the name is added to, and the stored value (a lower-case form of the name with spaces and symbols replaced by underscores). It never shows a file location.
- ADD is disabled until a name is entered.
- A duplicate name (case-insensitive) shows "This Sub-Head already exists." under the field (PRD FR-8).
- On success, the popup closes, the new sub-head appears in the dropdown, and it is selected. The name is also saved for the selected Main Head, so it appears the next time the app starts (PRD FR-8). If saving fails, the sub-head is still added and the message bar shows a warning that does not mention any file location.

### 5.5 Remove Sub-Head Popup (−)

```
+----------------------------------------------+
|  Remove Sub-Head                         ✕   |
|                                              |
|  Remove "Auxiliary Sub Head" from the list?  |
|  Old entries keep this sub-head name.        |
|                                              |
|            [ CANCEL ]   [ REMOVE ]           |
+----------------------------------------------+
```

- After removal, the sub-head leaves the dropdown and the dropdown returns to "-Select-" (PRD FR-9). Old entries keep the name.

### 5.6 Submit and Clear
- **SUBMIT** saves the entry (PRD FR-15). On success:
  - the message bar shows "Entry saved to 20-Oct-2026." in `SUCCESS_BG`;
  - Date, Name, Particulars, Debit, and Credit are cleared (Debit and Credit reset to 0.00);
  - Main Head and Sub-Head are unchanged.
- If the Excel file for the date is open in Excel, the message bar uses `WARNING_BG` and reads: "The Excel file for 20-Oct-2026 is open. Close it in Excel and click Submit again. Your entry has not been lost." This message names the date, not a file path. All values stay in the form (Rule 15).
- **CLEAR** resets the transaction fields only (PRD FR-17).
- Enter in a text field submits when Submit is enabled (PRD NFR-6).

---

## 6. Screen: Expense Report

Layout follows the specification's "Expense Report Table & Filter Bar" (Section 3). The order on the page is: Monthly Summary, Yearly Summary, the filter card, then the table.

```
+--------------------------------------------------------------------------+
|  Expense Report                                                          |
|  All submitted entries, oldest first                                     |
|                                                                          |
|  MONTHLY SUMMARY                                           [ Oct 2026 ▼ ]|
|  Values are based on the selected month. Independent of the filters.     |
|  +----------------+  +----------------+  +----------------+              |
|  | 1. DEBIT TOTAL |  | 2. MOST DEBIT  |  | 3. LEAST DEBIT |              |
|  | 2,500.00       |  | Vendor Route   |  | Office Expense |              |
|  |                |  | 2,500.00       |  | 0.00           |              |
|  +----------------+  +----------------+  +----------------+              |
|  | 4. CREDIT TOTAL|  | 5. MOST CREDIT |  | 6. LEAST CREDIT|              |
|  | 14,200.00      |  | ...            |  | ...            |              |
|  +----------------+  +----------------+  +----------------+              |
|                                                                          |
|  YEARLY SUMMARY                                            [ 2026 ▼ ]    |
|  (same six cards)                                                        |
|                                                                          |
|  +--------------------------------------------------------------------+  |
|  | SEARCH                                                             |  |
|  | [ Search by name, particulars, or amount ____________________ ]    |  |
|  | DATE RANGE         FROM          TO                                |  |
|  | [ All Dates ▼ ]    [ DD-Mon-YYYY ]  [ DD-Mon-YYYY ]  (custom only)  |  |
|  | MAIN HEAD          SUB-HEAD                                        |  |
|  | [ All Main Heads ▼] [ All Sub-Heads ▼ ]                            |  |
|  | NAME               PARTICULARS                                     |  |
|  | [ contains...    ] [ contains...     ]                             |  |
|  | DEBIT FROM  DEBIT TO   CREDIT FROM  CREDIT TO                      |  |
|  | [ 0.00 ]    [ 0.00 ]   [ 0.00 ]     [ 0.00 ]                       |  |
|  |                              [ CLEAR FILTERS ]  [ FILTER REPORT ]  |  |
|  +--------------------------------------------------------------------+  |
|                                                                          |
|  +--------------------------------------------------------------------+  |
|  | DATE | MAIN HEAD | SUB-HEAD | NAME | PARTICULARS | DEBIT | CREDIT | ACTIONS |
|  | 24-Oct-2026 | Treesa Agencies | Office Expense | Vendor Account | ...   |
|  | 24-Oct-2026 | Daily Collection | Lenin | Daily Counter | ...           |
|  |------------------------------------------------------------------------|  |
|  | TOTAL (all 2 matching rows)                       2,500.00 14,200.00   |  |
|  |------------------------------------------------------------------------|  |
|  | Showing 1 to 2 of 2 entries   Rows per page [10 ▼]  ‹ Prev  1  Next ›  |  |
|  +--------------------------------------------------------------------+  |
+--------------------------------------------------------------------------+
```

### 6.1 Summary Cards (Monthly and Yearly)

- Each summary is a card with a title, a line saying the values follow the selected month or year, and a period selector on the right. The default period is the latest one with entries (PRD FR-21a, FR-21b).
- Six cards in two rows of three:
  1. **Debit (Total Amount)**: total Debit for the period.
  2. **Most Debited Sub-Head**: the sub-head name, with its Debit total below.
  3. **Least Debited Sub-Head**: the sub-head name, with its Debit total below.
  4. **Credit (Total Amount)**: total Credit for the period.
  5. **Most Credited Sub-Head**: the sub-head name, with its Credit total below.
  6. **Least Credited Sub-Head**: the sub-head name, with its Credit total below.
- Card style: `PRIMARY_LIGHT` background, 1 px `BORDER_SOFT` outline, radius 12, label in uppercase `TEXT_MUTED`. The total value is Black weight at 20. Debit values use `DEBIT`, Credit values use `CREDIT`.
- Only sub-heads with at least one entry in the period are ranked. Ties are broken by name (PRD FR-21c).
- The cards ignore the report filters. A card shows "—" and 0.00 when the period has no entries.
- Cards stack to one column on a narrow window.

### 6.2 Filters

- **Search** (PRD FR-19a): one box that matches the Name or Particulars text, or an amount. `2500`, `2500.00`, and `2,500` all find 2,500.00. Enter in the box applies the filters.
- **Filters** (PRD FR-19): every column can be filtered, and the filters combine.
  - Date Range: All Dates (default), This Month, Last Month, This Year, Custom Range. Custom Range shows From and To fields that accept DD-Mon-YYYY or DD/MM/YYYY.
  - Main Head: All Main Heads (default), **Treesa Agencies**, **Daily Collection**.
  - Sub-Head: All Sub-Heads (default), then the sub-heads of the selected Main Head. Removed sub-heads still appear, so old entries can be filtered.
  - Name and Particulars: contains the typed text.
  - Debit From / To and Credit From / To: amount range, inclusive.
  - **FILTER REPORT** applies the filters. **CLEAR FILTERS** resets them. Filtering does not change the data, and the table returns to page 1.
  - An invalid value (for example a date that does not exist) shows a red message above the buttons and is not applied.

### 6.3 Table

- **Columns** (PRD FR-18): Date, Main Head, Sub-Head, Name, Particulars, Debit, Credit, Actions. Main Head shows the name (Treesa Agencies or Daily Collection), not the code.
- Rows are oldest first. Dates use DD-Mon-YYYY. Amounts are right-aligned with two decimals. Debit is shown in `DEBIT` and Credit in `CREDIT`.
- Table headers are Black weight, uppercase, on `SURFACE_TINT`. Rows are separated by `ROW_BORDER`.
- Actions: **✎** (edit) and **🗑** (delete) icon buttons.
- Empty state: "No entries match these filters."
- **Totals row** (PRD FR-20): labelled "TOTAL (all N matching rows)". It shows the total Debit and Credit of every matching row, not only the rows on the current page.

### 6.4 Pagination

- The table shows **10 rows per page** by default. The user can choose 10, 25, or 50 rows per page (PRD FR-18a).
- The pager bar sits under the table on `SURFACE_TINT`:
  - a line such as "Showing 1 to 10 of 24 entries" on the left;
  - on the right, a "Rows per page" selector, a **‹ Prev** button, page number buttons, and a **Next ›** button.
- Page number buttons are 32 px tall. The current page is blue (`PRIMARY`) with white text. The first page, the last page, and the two pages either side of the current one are always shown; gaps show "…".
- Prev is disabled on the first page, and Next is disabled on the last page.
- Applying or clearing filters, or changing the rows per page, returns the table to page 1.
- When the table has no rows, the pager bar is hidden.

### 6.5 Inline Edit

- **Pencil (✎)**: the row's Main Head, Sub-Head, Date, Name, Particulars, Debit, and Credit become input fields with the same rules as Main Entry (Section 5.3). The pencil becomes a **checkmark (✓)**.
  - **Main Head** is a dropdown with Treesa Agencies and Daily Collection (PRD FR-22).
  - **Sub-Head** is a dropdown that follows the chosen Main Head. The entry's current Sub-Head stays in the list even if it was removed later. If the Main Head changes and the current Sub-Head is not in the new list, the dropdown shows "-Select-" and a Sub-Head must be picked before saving. The error "Select a Sub-Head." appears under the dropdown.
  - **✓** saves the change (PRD FR-22). If the row is invalid, the error shows under the field and the row stays in edit mode.
  - **Esc** cancels the edit and restores the row. A hint "Esc cancels" shows next to the checkmark.
- **Delete (🗑)**: opens the confirmation popup (Section 6.6).

### 6.6 Delete Confirmation Popup

```
+----------------------------------------------+
|  Delete Row                              ✕   |
|                                              |
|  Are you sure you want to delete this row?   |
|                                              |
|            [ CANCEL ]   [ DELETE ]           |
+----------------------------------------------+
```

- The row is deleted only after **DELETE** is clicked (PRD FR-23, Rule 17).
- Cancel or Esc closes the popup and leaves the row unchanged.

---

## 7. Shared Elements

| Element | Behavior |
|---------|----------|
| Message bar | Full width under the page title or form. Four styles: success (`SUCCESS_BG`, text `CREDIT`), warning (`WARNING_BG`, text `WARNING`), error (`ERROR_BG`, text `ERROR`), info (`PRIMARY_LIGHT`). Success and info disappear after 6 seconds. Warnings and errors stay until the next action. Messages never show a file path. |
| Toast | Bottom-right corner, `SUCCESS_BG` with a 1 px `BORDER_SOFT` outline, radius 12, ExtraBold text, deep shadow. Disappears after 3 seconds. Used for "Password changed.". |
| Primary button | Blue gradient (`BTN_TOP` to `BTN_BOTTOM`), white uppercase Black text, soft blue glow. Hover `PRIMARY_HOVER`. Disabled style from Section 1.4. |
| Secondary button | `BG_CARD` background, `INPUT_BORDER` outline, `TEXT` text. Hover `SURFACE_TINT`. |
| Danger button | `PRIMARY` background (same red family as the debit amounts), used for DELETE and REMOVE. |
| Popup | 420 px wide, radius 16, `BG_CARD`, centered over a `SCRIM` backdrop blurred 4 px. Closes with ✕, Cancel, or Esc. |
| Icon buttons | Transparent, 15 px icons, a `PRIMARY_LIGHT` background on hover. |
| Dates on screen | DD-Mon-YYYY everywhere (Rule 10). |
| Amounts on screen | Two decimals, thousands separator, monospace. |
| File locations | Never shown on any screen (PRD NFR-9, Rule 36). |

---

## 8. Screen Checklist (used in Phase 8)

- [ ] Theme matches Section 1: dark layered blacks, soft white text, blue primary buttons, red debit, green credit.
- [ ] Sidebar: fixed height, no scrolling, items in order Main Entry, Expense Report, Change Password (text only), Logout, and the developer footer.
- [ ] Change Password popup matches Section 2.1; the success toast appears after saving.
- [ ] Login and create account match sections 3 and 4.
- [ ] Main Entry opens with Daily Collection selected and Sub-Head at "-Select-".
- [ ] Date, Name, Particulars, Debit, Credit, and Submit are disabled until a sub-head is chosen.
- [ ] Submit is disabled until the form is valid (including Debit or Credit above 0.00).
- [ ] Typing `20/10/2026` shows `20-Oct-2026`; the date picker also fills the field.
- [ ] Add (+) rejects duplicates and shows no file location; Remove (−) asks for confirmation in its popup.
- [ ] Expense Report order: Monthly Summary, Yearly Summary, filter card, table with pagination.
- [ ] Search, date range, column filters, Main Head names, totals, and both summary sections match Section 6.
- [ ] Table shows Main Head and Sub-Head columns; inline edit has Main Head and Sub-Head dropdowns.
- [ ] Pagination: 10 rows by default, choices 10/25/50, Prev/Next, page numbers, and the "Showing x to y of z" line.
- [ ] Delete asks for confirmation before removing a row.
- [ ] No screen shows a folder, AppData path, or file name (other than the date-based Excel name shown in the warning, which is shown as a date only).
- [ ] All dates are DD-Mon-YYYY.
- [ ] All screens work with keyboard only.

### 1.6 App Icon

- The app icon is the file `Design/IconKitchen-Output/web/icon-512.png` (a blue rounded square with a white box). It is the program's icon in the title bar and taskbar, on the EXE file, and on the installed program's Start Menu shortcut and Add/Remove Programs entry.
- The Change Password button has no icon; it is text only.
