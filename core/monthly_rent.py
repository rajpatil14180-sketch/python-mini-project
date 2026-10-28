"""Helpers for owner-agreed monthly rent calculations."""
import calendar
from datetime import date


def get_monthly_due_date(join_date, year, month):
    """FEATURE: Monthly Rent
    Return the monthly due date using the tenant's joining day when possible."""
    last_day = calendar.monthrange(year, month)[1]
    due_day = min(join_date.day, last_day)
    return date(year, month, due_day)


def get_monthly_expected_rent(monthly_rent, join_date, today=None):
    """FEATURE: Monthly Rent
    Add one full agreed monthly rent for each due date reached since joining."""
    if today is None:
        today = date.today()
    if not isinstance(monthly_rent, int) or monthly_rent < 0:
        raise ValueError("Monthly rent must be a non-negative whole-rupee amount.")
    if today < join_date:
        return 0
    expected = 0
    year = join_date.year
    month = join_date.month
    while (year, month) <= (today.year, today.month):
        due_date = get_monthly_due_date(join_date, year, month)
        if join_date <= due_date <= today:
            expected += monthly_rent
        month += 1
        if month > 12:
            month = 1
            year += 1
    return expected


def get_monthly_balance(monthly_rent, paid_amount):
    """FEATURE: Monthly Rent
    Return the outstanding amount and status for one month's rent."""
    if not isinstance(monthly_rent, int) or monthly_rent < 0:
        raise ValueError("Monthly rent must be a non-negative whole-rupee amount.")
    if not isinstance(paid_amount, int) or paid_amount < 0:
        raise ValueError("Paid amount must be a non-negative whole-rupee amount.")
    if paid_amount > monthly_rent:
        raise ValueError("Paid amount cannot exceed this month's rent.")
    due_left = monthly_rent - paid_amount
    return {"monthly_rent": monthly_rent, "paid_amount": paid_amount,
            "due_left": due_left, "status": "paid" if due_left == 0 else "due"}
