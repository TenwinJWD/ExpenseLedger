"""Fixed values for the app: name, version, limits, and the seed sub-head lists.

Every number used in the app is named here (Rules 6). Values come from
Roadmap/PRD.md and Roadmap/Architecture.md.
"""

APP_NAME = "Daily Fresh"
APP_VERSION = "1.0.1"
APP_AUTHOR = "Tenwin James"  # PRD FR-36: the only place this name is set.

# Update check. Leave UPDATE_URL empty to turn it off: the app then never connects to the internet.
# Set it to the https address of the version file described in app/services/update_service.py.
UPDATE_URL = ""
UPDATE_TIMEOUT_SECONDS = 5
UPDATE_MAX_BYTES = 64 * 1024

# Text size: the whole window is drawn at 110% (fonts and layout), which reads better than 100%.
UI_SCALE = 1.1

# Login (PRD FR-2, FR-4, NFR-5).
MAX_LOGIN_ATTEMPTS = 5
LOCK_MINUTES = 5
MIN_PASSWORD_LENGTH = 8
PBKDF2_ITERATIONS = 600_000

# Entry form and sub-heads (PRD FR-8, FR-13).
NAME_MAX_LENGTH = 100
PARTICULARS_MAX_LENGTH = 200
SUBHEAD_MAX_LENGTH = 40
MAIN_ENTRY_MAX_LENGTH = 30

# Expense Report pagination (PRD FR-18a).
PAGE_SIZE_CHOICES = (10, 25, 50)
DEFAULT_PAGE_SIZE = 10

# Seed sub-heads. These match Defaults/default.js (treesa <- Treesa.jpeg, daily <- Daily.jpeg).
# They are copied to AppData on first run and are the starting list for each Main Head.
SEED_SUBHEADS_TREESA = (
    "Treesa - SIB", "PD - IndusInd", "Salary", "Salary Advance", "Weekly Allowance", "Cash at Cochin",
    "Triprayar - CNG", "Triprayar - Petrol", "Triprayar - Diesel", "Triprayar - Driver",
    "Ponnani - CNG", "Ponnani - Petrol", "Ponnani - Diesel", "Ponnani - Driver",
    "Pattambi - CNG", "Pattambi - Petrol", "Pattambi - Diesel", "Pattambi - Driver",
    "EKM - CNG", "EKM - Petrol", "EKM - Diesel", "EKM - Driver",
    "KSFE Kuri", "Sadhu Kuri", "Stationary", "Cash or Chq John P.C", "Office Expense",
    "ICE - TCR", "ICE - Manjeri", "Fast Tag", "Repairs of Workshop", "Showroom Expenses",
    "CNG - Thrissur", "Vehicle Permit", "Plant", "Manjeri Diesel", "Manjeri CNG", "Plant Diesel",
    "Advertisement", "Tax", "Electrical Expense", "Rent", "Computer Maintenance",
    "Internet Charge", "Mobile Charge", "Parking Charge", "GST & Tax", "Vehicle EMIs",
)
SEED_SUBHEADS_DAILY = (
    "TPR Collection - Akhil Babu", "Ponnani Collection - Sanju", "Pattambi Collection - Devadas",
    "Lenin", "Mohandas", "Vivek", "Jeeva Farms", "Cochin Freshway", "RAK",
    "Daily Route Jilshad", "Daily Route Rajeev", "Daily Route Praveen", "Daily Route Mahesh",
    "Daily Route Mathew", "Daily Route Sumesh", "John P.C", "Cochin 11 - Shaji PBVR",
    "Cochin 11 - Shaji BVR", "Anil Chegannur", "Direct Route Emmanuvel, Cochin",
    "Shiji - Kodungallur", "Direct Route Salam, Cochin",
)
