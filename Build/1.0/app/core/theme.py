"""Colours and text styles: the cream theme from the Design/design mockups (cream page, tan sidebar, olive buttons, black text) (earlier dark palette: Roadmap/Design.md Section 1).

Screens use only these names (Rule 37). Do not write a colour value anywhere else.
The font is Nunito, shipped in assets/fonts and loaded at start-up (app/core/fonts.py). If it
cannot be loaded, main.py switches FONT_FAMILY to Segoe UI, which every Windows 10 PC has.
"""

# Page and layers (light theme, from the Design/design mockups).
PAGE_TOP = "#E7E3D8"
PAGE_BOTTOM = "#E7E3D8"
BG_PAGE = "#E7E3D8"
CARD_TOP = "#F2EFE7"
CARD_BOTTOM = "#F2EFE7"
BG_CARD = "#F2EFE7"
BG_INPUT = "#F9F7F2"
BORDER_SOFT = "#8A826D"
INPUT_BORDER = "#6B644F"
DROPDOWN_BORDER = "#6B644F"

# Sidebar.
SIDE_TOP = "#C1B4A1"
SIDE_BOTTOM = "#C1B4A1"
SIDEBAR_TEXT = "#000000"
SIDE_SHADOW = "#8F836F"  # the shadow along the sidebar edge
SIDE_HOVER = "#B0A28D"

# Primary actions.
BTN_TOP = "#6B7B2C"
BTN_BOTTOM = "#6B7B2C"
PRIMARY = "#6B7B2C"
PRIMARY_HOVER = "#566423"
PRIMARY_LIGHT = "#D9DFB8"

# Text.
TEXT = "#000000"
TEXT_MUTED = "#4A463B"

# Tables and states.
SURFACE_TINT = "#DDE2C2"
SURFACE_SOFT = "#E9E6DB"
ROW_BORDER = "#BDB6A2"
DISABLED_BG = "#D8D3C5"
DISABLED_TEXT = "#8A8574"

# Amounts and messages.
DEBIT = "#A82214"
CREDIT = "#1B7A43"
ERROR_BG = "#F6DCD6"
ERROR = "#A82214"
SUCCESS_BG = "#DCE8CF"
WARNING_BG = "#F3E6BC"
WARNING = "#7A5200"

# Radii and sizes (Design.md 1.3). CustomTkinter takes these as numbers.
CARD_RADIUS = 16
BUTTON_RADIUS = 10
INPUT_RADIUS = 8
BUTTON_HEIGHT = 40
INPUT_HEIGHT = 40
SIDEBAR_WIDTH = 250
MIN_WINDOW_WIDTH = 1120
MIN_WINDOW_HEIGHT = 640

# Font (Design.md 1.2). Nunito matches the mockups; Segoe UI is the fallback (PRD NFR-8).
FONT_FAMILY = "Nunito"
FALLBACK_FONT_FAMILY = "Segoe UI"
# Windows icon font, installed with Windows 10 and 11. Used for the pencil, delete, tick, and calendar icons.
ICON_FONT = "Segoe MDL2 Assets"
ICON_EDIT = ""
ICON_DELETE = ""
ICON_CONFIRM = ""
ICON_INFO = "\ue946"
ICON_USER = ""
ICON_CALENDAR = ""
FONT_SIZE_BODY = 15
FONT_SIZE_LABEL = 13
FONT_SIZE_PAGE_TITLE = 28
FONT_SIZE_CARD_TITLE = 20
FONT_SIZE_VALUE = 22
