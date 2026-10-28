"""
App-wide constants used by all modules.
All values come from SPEC section 4.
"""
from datetime import date

# Database file name
DB_NAME = "pg.db"

# The academic year starts on this date
COLLEGE_START_DATE = date(2026, 8, 1)

# Late-join discount tiers: (max_days_late, discount_percent)
# The first row where days_late <= limit is used.
LATE_JOIN_DISCOUNTS = [(0, 0), (30, 5), (60, 10), (90, 15), (999999, 20)]

# Border colours for beds on the blueprint (hex strings)
BED_BORDER_COLOURS = {
    "empty": "#2e9e5b",
    "occupied": "#2b6cb0",
    "overdue": "#c53030",
}

# Allowed values for ticket fields
TICKET_CATEGORIES = ["Plumbing", "Electrical", "Wi-Fi", "Cleaning", "Furniture", "Other"]
TICKET_URGENCIES = ["Low", "Medium", "High"]
TICKET_STATUSES = ["Open", "In Progress", "Resolved"]

# Allowed payment modes
PAYMENT_MODES = ["cash", "upi"]
