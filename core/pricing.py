"""
Late-join pricing and installment schedule calculations.
All money values are whole rupees (int). No floats.
"""
import calendar
from datetime import date

from config import COLLEGE_START_DATE, LATE_JOIN_DISCOUNTS


def add_months(d, n):
    """FEATURE: Installment Schedule
    Return a new date that is n months after d, clamping the day to the
    last day of the target month when necessary."""
    # Shift the month forward by n
    month = d.month + n
    year = d.year
    # Handle overflow past December
    while month > 12:
        month -= 12
        year += 1
    # Clamp the day if the target month is shorter
    last_day = calendar.monthrange(year, month)[1]
    day = min(d.day, last_day)
    return date(year, month, day)


def get_late_join_discount_percent(join_date):
    """FEATURE: Late-Join Pricing
    Return the discount percentage for a tenant based on how many days
    after COLLEGE_START_DATE they joined."""
    days_late = (join_date - COLLEGE_START_DATE).days
    # Walk the tiers; first match wins
    for limit, percent in LATE_JOIN_DISCOUNTS:
        if days_late <= limit:
            return percent
    # Fallback (should never happen because the last limit is 999999)
    return 0


def calculate_agreed_price(base_price, join_date):
    """FEATURE: Late-Join Pricing
    Apply the late-join discount to the base price and round DOWN to the
    nearest 100."""
    pct = get_late_join_discount_percent(join_date)
    # Integer arithmetic: base * (100 - pct) // 100
    price = base_price * (100 - pct) // 100
    # Round down to nearest 100
    price = price // 100 * 100
    return price


def get_installment_schedule(agreed_price, join_date):
    """FEATURE: Installment Schedule
    Return a list of 12 (due_date, amount) tuples.  The first 11
    installments are agreed_price // 12; the 12th gets the remainder
    so the total equals agreed_price exactly."""
    monthly = agreed_price // 12
    schedule = []
    for k in range(12):
        due_date = add_months(join_date, k)
        if k < 11:
            amount = monthly
        else:
            # Last installment picks up the remainder
            amount = agreed_price - monthly * 11
        schedule.append((due_date, amount))
    return schedule
