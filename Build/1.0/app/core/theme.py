"""Colours and text styles: the retro theme from Design/design/retro.png (light grey page, white cards, blue save buttons, red cancel buttons, slate highlights).

Screens use only these names (Rule 37). Do not write a colour value anywhere else.
The font is Nunito, shipped in assets/fonts and loaded at start-up (app/core/fonts.py). If it
cannot be loaded, main.py switches FONT_FAMILY to Segoe UI, which every Windows 10 PC has.
"""

# Page and layers.
PAGE_TOP = "#ECF0F1"  # the login page fades from light grey at the top to pale blue-grey
PAGE_BOTTOM = "#CFDCE6"
BG_PAGE = "#ECF0F1"
CARD_TOP = "#FFFFFF"
CARD_BOTTOM = "#FFFFFF"
BG_CARD = "#FFFFFF"
BG_INPUT = "#ECF0F1"
BORDER_SOFT = "#DCE3E8"
INPUT_BORDER = "#C5D0D8"
DROPDOWN_BORDER = "#A9B8C3"

# Menu colours.
SIDE_TOP = "#FFFFFF"
SIDE_BOTTOM = "#FFFFFF"
SIDEBAR_TEXT = "#34495E"
SIDE_SHADOW = "#D3DEE8"
SIDE_HOVER = "#E3EAEF"
SIDE_ACTIVE = "#DDE4EA"

# The top navbar: a gradient from white on the left to pale blue on the right.
NAV_START = "#FFFFFF"
NAV_MIDDLE = "#F1F6FA"
NAV_END = "#DCEAF5"
NAV_HEIGHT = 64
HEADS_BAR_HEIGHT = 56  # the second bar, with the Main Entries

# Primary actions (Save, Submit, Login): blue with white text. PRIMARY_LIGHT is the pale blue for hovers and selected items.
BTN_TOP = "#2E86C1"
BTN_BOTTOM = "#2E86C1"
PRIMARY = "#2E86C1"
PRIMARY_HOVER = "#2573A7"
PRIMARY_LIGHT = "#D6E8F5"
ON_PRIMARY = "#FFFFFF"  # text on a PRIMARY fill
# Highlights (the open tab, the open Main Entry, the open page number): dark slate.
HIGHLIGHT = "#34495E"
HIGHLIGHT_HOVER = "#2B3C4D"
ON_HIGHLIGHT = "#FFFFFF"
# Cancel-type buttons (Cancel, Clear Filters): red.
CANCEL = "#E74C3C"
CANCEL_HOVER = "#CF3F30"
ON_CANCEL = "#FFFFFF"
INK = "#34495E"  # dark fill for the delete button and outlines of buttons
INK_HOVER = "#2B3C4D"
BADGE_TEXT = "#34495E"  # text on the pale pills

# Text.
TEXT = "#2C3E50"
TEXT_MUTED = "#5D6D7E"

# Tables and states.
SURFACE_TINT = "#E8F1F8"
SURFACE_SOFT = "#ECF0F1"
ROW_BORDER = "#E1E7EB"
DISABLED_BG = "#E3E8EB"
DISABLED_TEXT = "#9AA7B1"

# Amounts and messages.
DEBIT = "#C0392B"
CREDIT = "#1E8449"
ERROR_BG = "#FADBD8"
ERROR = "#C0392B"
SUCCESS_BG = "#D5F5E3"
WARNING_BG = "#FCF3CF"
WARNING = "#7D6608"

# Radii and sizes. CustomTkinter takes these as numbers.
CARD_RADIUS = 20
BUTTON_RADIUS = 20  # half the button height: a pill
INPUT_RADIUS = 12
BUTTON_HEIGHT = 40
INPUT_HEIGHT = 40
SIDEBAR_WIDTH = 250
PAGE_MARGIN = 16  # the gap around the floating sidebar and panels
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 640

# Font. Nunito is the main font; Segoe UI is the fallback (PRD NFR-8).
FONT_FAMILY = "Nunito"
FALLBACK_FONT_FAMILY = "Segoe UI"
# Windows icon font, installed with Windows 10 and 11. Used for the pencil, delete, tick, and calendar icons.
ICON_FONT = "Segoe MDL2 Assets"
ICON_EDIT = "\ue70f"
ICON_DELETE = "\ue74d"
ICON_CONFIRM = "\ue8fb"
ICON_INFO = "\ue946"
ICON_USER = "\ue77b"
ICON_CALENDAR = "\ue787"
FONT_SIZE_BODY = 15
FONT_SIZE_LABEL = 13
FONT_SIZE_PAGE_TITLE = 28
FONT_SIZE_CARD_TITLE = 20
FONT_SIZE_VALUE = 22
