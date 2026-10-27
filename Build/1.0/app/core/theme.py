"""Colours and text styles, copied from Roadmap/Design.md Section 1 (palette v1.7).

Screens use only these names (Rule 37). Do not write a colour value anywhere else.
The font family is a placeholder until the font is chosen (task T1.4a); Segoe UI is
installed on every Windows 10 PC and is used until then.
"""

# Page and layers (Design.md 1.1).
PAGE_TOP = "#141419"
PAGE_BOTTOM = "#0B0B0E"
BG_PAGE = "#0C0C0F"
CARD_TOP = "#1B1B22"
CARD_BOTTOM = "#131317"
BG_CARD = "#151519"
BG_INPUT = "#1C1C22"
BORDER_SOFT = "#26262E"
INPUT_BORDER = "#34343E"
DROPDOWN_BORDER = "#6B7AA1"

# Sidebar.
SIDE_TOP = "#1A1A21"
SIDE_BOTTOM = "#0A0A0D"
SIDEBAR_TEXT = "#E4E4E7"

# Primary actions.
BTN_TOP = "#4F8CFF"
BTN_BOTTOM = "#2563EB"
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_LIGHT = "#18203A"

# Text.
TEXT = "#F4F4F5"
TEXT_MUTED = "#8B8B98"

# Tables and states.
SURFACE_TINT = "#1C1C22"
ROW_BORDER = "#22222A"
DISABLED_BG = "#17171B"
DISABLED_TEXT = "#4A4A55"

# Amounts and messages.
DEBIT = "#FB7185"
CREDIT = "#34D399"
ERROR_BG = "#2A1218"
ERROR = "#FB7185"
SUCCESS_BG = "#0E2620"
WARNING_BG = "#2A2310"
WARNING = "#FBBF24"

# Radii and sizes (Design.md 1.3). CustomTkinter takes these as numbers.
CARD_RADIUS = 16
BUTTON_RADIUS = 10
INPUT_RADIUS = 8
BUTTON_HEIGHT = 40
INPUT_HEIGHT = 40
SIDEBAR_WIDTH = 250
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 640

# Font (Design.md 1.2). Segoe UI is the Windows system font (PRD NFR-8).
FONT_FAMILY = "Segoe UI"
FONT_FAMILY_LIGHT = "Segoe UI Light"  # the light weight, installed with Windows 10 and 11
# Windows icon font, installed with Windows 10 and 11. Used for the pencil, delete, tick, and calendar icons.
ICON_FONT = "Segoe MDL2 Assets"
ICON_EDIT = ""
ICON_DELETE = ""
ICON_CONFIRM = ""
ICON_INFO = "\ue946"
ICON_CALENDAR = ""
FONT_SIZE_BODY = 15
FONT_SIZE_LABEL = 13
FONT_SIZE_PAGE_TITLE = 28
FONT_SIZE_CARD_TITLE = 20
FONT_SIZE_VALUE = 24
