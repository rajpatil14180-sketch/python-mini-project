"""Tests for tenant finance calculations and password verification."""
import secrets
import unittest
from datetime import date
import config
from database import create_tables, get_connection
from core.finance import get_tenant_financials
from core.auth import hash_password, verify_password


class FinanceTests(unittest.TestCase):
    """FEATURE: Finance Tests
    Verify financial totals using an isolated temporary database."""

    def setUp(self):
        """FEATURE: Finance Tests
        Prepare an isolated test database."""
        self.original_db_name = config.DB_NAME
        self.temp_db = f"file:pg_manager_test_{secrets.token_hex(8)}?mode=memory&cache=shared"
        config.DB_NAME = self.temp_db
        self.keeper = get_connection()
        create_tables()
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
            ("testtenant", "x", "y", "tenant"),
        )
        conn.execute(
            "INSERT INTO pgs (owner_id, name, address) VALUES (1, 'Test PG', 'Test address')"
        )
        conn.execute("INSERT INTO rooms (pg_id, room_no, has_attached_bath) VALUES (1, 1, 1)")
        conn.execute("INSERT INTO beds (room_id, label, base_yearly_price) VALUES (1, 'A', 120000)")
        conn.execute(
            "INSERT INTO tenants (user_id, bed_id, name, phone, join_date, deposit, agreed_yearly_price, is_active) "
            "VALUES (1, 1, 'Test Tenant', '9999999999', '2026-06-01', 10000, 120000, 1)"
        )
        self.tenant_id = 1
        conn.execute(
            "INSERT INTO payments (tenant_id, amount, paid_on, mode) VALUES (1, 20000, '2026-07-01', 'upi')"
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        """FEATURE: Finance Tests
        Close the isolated in-memory database and restore the setting."""
        self.keeper.close()
        config.DB_NAME = self.original_db_name

    def test_overdue_calculation(self):
        """FEATURE: Finance Tests
        Check the overdue payment totals."""
        info = get_tenant_financials(self.tenant_id, date(2026, 8, 5))
        self.assertEqual(info["total_paid"], 20000)
        self.assertEqual(info["expected_till_today"], 30000)
        self.assertEqual(info["overdue_amount"], 10000)
        self.assertEqual(info["due_left"], 100000)
        self.assertEqual(info["next_due_date"], "2026-08-01")
        self.assertEqual(info["status"], "overdue")

    def test_up_to_date_calculation(self):
        """FEATURE: Finance Tests
        Check financial totals after an additional payment."""
        conn = get_connection()
        conn.execute(
            "INSERT INTO payments (tenant_id, amount, paid_on, mode) VALUES (?, ?, ?, ?)",
            (self.tenant_id, 10000, "2026-08-01", "cash"),
        )
        conn.commit()
        conn.close()
        info = get_tenant_financials(self.tenant_id, date(2026, 8, 5))
        self.assertEqual(info["overdue_amount"], 0)
        self.assertEqual(info["status"], "ok")
        self.assertEqual(info["next_due_date"], "2026-09-01")

    def test_all_installments_paid_has_no_next_due_date(self):
        """FEATURE: Finance Tests
        Check that a fully paid tenant has no remaining installment date."""
        conn = get_connection()
        conn.execute("DELETE FROM payments WHERE tenant_id = ?", (self.tenant_id,))
        for index in range(12):
            due_month = index + 1
            due_year = 2026 + (due_month - 1) // 12
            due_month = (due_month - 1) % 12 + 1
            due_date = date(due_year, due_month, 1).isoformat()
            amount = 10000
            conn.execute(
                "INSERT INTO payments (tenant_id, amount, paid_on, mode) VALUES (?, ?, ?, ?)",
                (self.tenant_id, amount, due_date, "cash"),
            )
        conn.commit()
        conn.close()
        info = get_tenant_financials(self.tenant_id, date(2027, 6, 1))
        self.assertEqual(info["total_paid"], 120000)
        self.assertEqual(info["due_left"], 0)
        self.assertIsNone(info["next_due_date"])
        self.assertEqual(info["status"], "ok")

    def test_password_verification(self):
        """FEATURE: Finance Tests
        Check correct and incorrect password verification."""
        hash_hex, salt_hex = hash_password("hello")
        self.assertTrue(verify_password("hello", hash_hex, salt_hex))
        self.assertFalse(verify_password("wrong", hash_hex, salt_hex))


if __name__ == "__main__":
    unittest.main()
