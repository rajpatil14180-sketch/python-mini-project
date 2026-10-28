"""Tests for owner-agreed monthly rent calculations."""
import unittest
from datetime import date
from core.monthly_rent import get_monthly_due_date, get_monthly_expected_rent, get_monthly_balance


class MonthlyRentTests(unittest.TestCase):
    """Check due dates, expected monthly rent, and balances."""

    def test_due_date_clamps_short_month(self):
        """FEATURE: Monthly Rent
        Clamp a joining day that does not exist in the target month."""
        self.assertEqual(get_monthly_due_date(date(2026, 1, 31), 2026, 2), date(2026, 2, 28))

    def test_expected_rent_counts_due_dates_reached(self):
        """FEATURE: Monthly Rent
        Count full monthly rent only after each due date has arrived."""
        join_date = date(2026, 8, 15)
        self.assertEqual(get_monthly_expected_rent(12000, join_date, date(2026, 9, 14)), 12000)
        self.assertEqual(get_monthly_expected_rent(12000, join_date, date(2026, 9, 15)), 24000)

    def test_future_join_date_has_no_expected_rent(self):
        """FEATURE: Monthly Rent
        Do not expect rent before a tenant's joining date."""
        self.assertEqual(get_monthly_expected_rent(12000, date(2026, 12, 1), date(2026, 11, 30)), 0)

    def test_monthly_balance(self):
        """FEATURE: Monthly Rent
        Return the remaining rent and paid status for one month."""
        self.assertEqual(get_monthly_balance(15000, 5000), {
            "monthly_rent": 15000, "paid_amount": 5000, "due_left": 10000, "status": "due"
        })
        self.assertEqual(get_monthly_balance(15000, 15000)["status"], "paid")

    def test_invalid_amounts_are_rejected(self):
        """FEATURE: Monthly Rent
        Reject negative values and payments larger than one month's rent."""
        with self.assertRaises(ValueError):
            get_monthly_balance(15000, 16000)
        with self.assertRaises(ValueError):
            get_monthly_balance(-1, 0)


if __name__ == "__main__":
    unittest.main()
