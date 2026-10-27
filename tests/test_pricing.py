"""Tests for late-join pricing and installment scheduling."""
import unittest
from datetime import date
from core.pricing import add_months, get_late_join_discount_percent, calculate_agreed_price, get_installment_schedule


class PricingTests(unittest.TestCase):
    """FEATURE: Pricing Tests
    Verify date clamping, discount tiers, and installment totals."""

    def test_add_months_clamps_end_of_month(self):
        """FEATURE: Pricing Tests
        Check month addition at the end of a month."""
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))

    def test_no_discount_on_college_start(self):
        """FEATURE: Pricing Tests
        Check that the start date has no discount."""
        self.assertEqual(get_late_join_discount_percent(date(2026, 8, 1)), 0)

    def test_five_percent_discount(self):
        """FEATURE: Pricing Tests
        Check the five percent late-join tier."""
        self.assertEqual(get_late_join_discount_percent(date(2026, 8, 15)), 5)

    def test_ten_percent_discount(self):
        """FEATURE: Pricing Tests
        Check the ten percent late-join tier."""
        self.assertEqual(get_late_join_discount_percent(date(2026, 9, 15)), 10)

    def test_price_rounds_down_to_hundred(self):
        """FEATURE: Pricing Tests
        Check the agreed price rounding rule."""
        self.assertEqual(calculate_agreed_price(230000, date(2026, 9, 15)), 207000)

    def test_schedule_has_twelve_entries_and_exact_total(self):
        """FEATURE: Pricing Tests
        Check the installment count and total."""
        schedule = get_installment_schedule(120000, date(2026, 8, 31))
        self.assertEqual(len(schedule), 12)
        self.assertEqual(sum(amount for _, amount in schedule), 120000)
        self.assertEqual(schedule[1][0], date(2026, 9, 30))

    def test_discount_tier_boundaries(self):
        """FEATURE: Pricing Tests
        Check dates at each discount tier boundary."""
        cases = [
            (date(2026, 8, 1), 0),
            (date(2026, 8, 2), 5),
            (date(2026, 8, 31), 5),
            (date(2026, 9, 1), 10),
            (date(2026, 9, 30), 10),
            (date(2026, 10, 1), 15),
            (date(2026, 10, 30), 15),
            (date(2026, 10, 31), 20),
        ]
        for join_date, expected in cases:
            with self.subTest(join_date=join_date):
                self.assertEqual(get_late_join_discount_percent(join_date), expected)

    def test_schedule_last_installment_gets_remainder(self):
        """FEATURE: Pricing Tests
        Check that the final installment receives any division remainder."""
        schedule = get_installment_schedule(100000, date(2026, 1, 31))
        self.assertEqual(schedule[0][1], 8333)
        self.assertEqual(schedule[-1][1], 8337)
        self.assertEqual(schedule[-1][0], date(2026, 12, 31))

    def test_leap_year_month_end(self):
        """FEATURE: Pricing Tests
        Check month-end scheduling through a leap-year February."""
        self.assertEqual(add_months(date(2028, 1, 31), 1), date(2028, 2, 29))


if __name__ == "__main__":
    unittest.main()
