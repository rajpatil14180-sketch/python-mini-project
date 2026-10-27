"""Tests for the core service contracts."""
import secrets
import unittest
from datetime import date
import config
from database import create_tables, get_connection
from core.tenant_service import add_tenant, add_payment, vacate_tenant
from core.pg_service import get_pg_layout, get_bed_details, get_pg_summary
from core.ticket_service import create_ticket, get_tickets_for_pg, update_ticket_status
from core.announcement_service import add_announcement, get_announcements_for_pg, delete_announcement
from core.auth import login


class ServiceTests(unittest.TestCase):
    """FEATURE: Service Tests
    Check the main service contracts using a temporary database."""

    def setUp(self):
        """FEATURE: Service Tests
        Create a small isolated database for each service test."""
        self.original_db_name = config.DB_NAME
        self.temp_db = f"file:pg_manager_test_{secrets.token_hex(8)}?mode=memory&cache=shared"
        config.DB_NAME = self.temp_db
        self.keeper = get_connection()
        create_tables()
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
            ("owner", "x", "y", "owner"),
        )
        conn.execute("INSERT INTO pgs (owner_id, name, address) VALUES (1, 'Test PG', 'Nashik')")
        conn.execute("INSERT INTO rooms (pg_id, room_no, has_attached_bath) VALUES (1, 1, 1)")
        conn.execute("INSERT INTO beds (room_id, label, base_yearly_price) VALUES (1, 'A', 120000)")
        conn.execute("INSERT INTO beds (room_id, label, base_yearly_price) VALUES (1, 'B', 110000)")
        conn.commit()
        conn.close()
        self.tenant_id = add_tenant(
            1, "Test Tenant", "9999999999", date.today(), 10000,
            120000, "testtenant", "tenant123",
        )

    def tearDown(self):
        """FEATURE: Service Tests
        Restore the original database setting and remove the test database."""
        self.keeper.close()
        config.DB_NAME = self.original_db_name

    def test_tenant_creation_and_duplicate_bed(self):
        """FEATURE: Service Tests
        Check tenant login creation and reject a second active tenant in one bed."""
        user = login("testtenant", "tenant123")
        self.assertEqual(user["tenant_id"], self.tenant_id)
        with self.assertRaises(ValueError):
            add_tenant(
                1, "Second Tenant", "9888888888", date.today(), 10000,
                100000, "secondtenant", "tenant123",
            )

    def test_payment_validation_and_vacating(self):
        """FEATURE: Service Tests
        Check payment limits and ensure vacating preserves the tenant record."""
        payment_id = add_payment(self.tenant_id, 50000, date.today(), "upi")
        self.assertGreater(payment_id, 0)
        with self.assertRaises(ValueError):
            add_payment(self.tenant_id, 70001, date.today(), "cash")
        vacate_tenant(self.tenant_id)
        self.assertIsNone(login("testtenant", "tenant123"))

    def test_pg_service_contracts(self):
        """FEATURE: Service Tests
        Check nested layout, bed details, and PG summary keys."""
        layout = get_pg_layout(1)
        self.assertEqual(len(layout), 1)
        self.assertEqual(len(layout[0]["beds"]), 2)
        self.assertEqual(layout[0]["beds"][0]["status"], "overdue")
        details = get_bed_details(layout[0]["beds"][0]["bed_id"])
        self.assertEqual(set(details), {"bed", "room_no", "pg_name", "tenant", "financials"})
        self.assertEqual(
            set(get_pg_summary(1)),
            {"total_beds", "occupied_beds", "total_expected", "total_collected", "total_overdue"},
        )

    def test_ticket_and_announcement_contracts(self):
        """FEATURE: Service Tests
        Check ticket ordering, resolved filtering, and announcement deletion."""
        ticket_id = create_ticket(self.tenant_id, "Plumbing", "Tap is leaking", "High")
        tickets = get_tickets_for_pg(1)
        self.assertEqual(tickets[0]["id"], ticket_id)
        self.assertIn("age_in_days", tickets[0])
        self.assertIsNone(update_ticket_status(ticket_id, "Resolved"))
        self.assertEqual(get_tickets_for_pg(1), [])
        self.assertEqual(len(get_tickets_for_pg(1, include_resolved=True)), 1)
        announcement_id = add_announcement(1, "Water supply notice")
        self.assertEqual(get_announcements_for_pg(1)[0]["id"], announcement_id)
        self.assertIsNone(delete_announcement(announcement_id))
        self.assertEqual(get_announcements_for_pg(1), [])

    def test_invalid_payment_and_ticket_inputs(self):
        """FEATURE: Service Tests
        Reject invalid payment amounts, modes, dates, and ticket fields."""
        with self.assertRaises(ValueError):
            add_payment(self.tenant_id, 0, date.today(), "cash")
        with self.assertRaises(ValueError):
            add_payment(self.tenant_id, 100, date.today(), "card")
        with self.assertRaises(ValueError):
            add_payment(self.tenant_id, 100, "not-a-date", "cash")
        with self.assertRaises(ValueError):
            create_ticket(self.tenant_id, "Invalid", "Issue", "High")
        with self.assertRaises(ValueError):
            create_ticket(self.tenant_id, "Plumbing", "", "High")

    def test_ticket_resolution_timestamp_and_empty_announcement(self):
        """FEATURE: Service Tests
        Check resolved timestamps and reject empty announcements."""
        ticket_id = create_ticket(self.tenant_id, "Plumbing", "Tap is leaking", "High")
        update_ticket_status(ticket_id, "Resolved")
        conn = get_connection()
        row = conn.execute("SELECT status, resolved_at FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        conn.close()
        self.assertEqual(row["status"], "Resolved")
        self.assertIsNotNone(row["resolved_at"])
        with self.assertRaises(ValueError):
            add_announcement(1, "   ")


if __name__ == "__main__":
    unittest.main()
