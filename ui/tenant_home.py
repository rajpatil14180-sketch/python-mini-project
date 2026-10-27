"""Tenant home screen."""
from tkinter import ttk
from core.pg_service import get_tenant_home_details
from core.finance import get_tenant_financials
from core.announcement_service import get_announcements_for_pg
from ui.tenant_tickets import TenantTickets


class TenantHome(ttk.Frame):
    """FEATURE: Tenant Home
    Display the tenant's room, finance, payment history, tickets, and notices."""

    def __init__(self, parent, app, user):
        """FEATURE: Tenant Home
        Build the tenant dashboard from the logged-in tenant record."""
        super().__init__(parent)
        self.app = app
        self.user = user
        self.tenant_id = user["tenant_id"]
        self.tenant = get_tenant_home_details(self.tenant_id)
        if self.tenant is None:
            ttk.Label(self, text="Tenant record could not be found.").pack()
            return
        ttk.Button(self, text="Log out", command=app.show_login).pack(anchor="e")
        ttk.Label(self, text="Tenant Dashboard", font=("TkDefaultFont", 20, "bold")).pack(
            anchor="w", pady=8
        )
        self._show_room_details()
        self._show_financials()
        self._show_tabs()

    def _show_room_details(self):
        """FEATURE: Tenant Home
        Show the tenant's PG, room, and bed assignment."""
        text = (
            f'{self.tenant["pg_name"]} · Room {self.tenant["room_no"]} '
            f'· Bed {self.tenant["label"]}'
        )
        ttk.Label(self, text=text).pack(anchor="w")

    def _show_financials(self):
        """FEATURE: Tenant Home
        Show yearly price, paid balance, overdue status, and payment history."""
        info = get_tenant_financials(self.tenant_id)
        if info is None:
            return
        cards = ttk.Frame(self)
        cards.pack(fill="x", pady=12)
        self._show_financial_cards(cards, info)
        status = "Overdue" if info["status"] == "overdue" else "Up to date"
        ttk.Label(self, text=f"Installment status: {status}").pack(anchor="w")
        due = info["next_due_date"] or "No remaining installments"
        ttk.Label(self, text=f"Next installment due: {due}").pack(anchor="w", pady=4)
        self._show_payment_history(info["payments"])

    def _show_financial_cards(self, parent, info):
        """FEATURE: Tenant Home
        Show the agreed price and payment totals as summary cards."""
        values = [
            ("Agreed yearly price", info["agreed_yearly_price"]),
            ("Total paid", info["total_paid"]),
            ("Due left", info["due_left"]),
            ("Overdue", info["overdue_amount"]),
        ]
        for label, value in values:
            card = ttk.LabelFrame(parent, text=label, padding=10)
            card.pack(side="left", fill="both", expand=True, padx=4)
            ttk.Label(card, text=f"₹{value:,}", font=("TkDefaultFont", 14, "bold")).pack()

    def _show_payment_history(self, payments):
        """FEATURE: Tenant Home
        List payment dates, amounts, and payment modes."""
        ttk.Label(self, text="Payment history", font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", pady=(10, 4)
        )
        table = ttk.Treeview(self, columns=("date", "amount", "mode"), show="headings", height=4)
        for column, heading in [("date", "Paid on"), ("amount", "Amount"), ("mode", "Mode")]:
            table.heading(column, text=heading)
            table.column(column, width=140)
        table.pack(fill="x")
        for payment in payments:
            table.insert("", "end", values=(
                payment["paid_on"], f'₹{payment["amount"]:,}', payment["mode"]
            ))

    def _show_tabs(self):
        """FEATURE: Tenant Home
        Add maintenance tickets and announcements tabs."""
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, pady=10)
        tickets_tab = ttk.Frame(tabs, padding=8)
        announcements_tab = ttk.Frame(tabs, padding=8)
        tabs.add(tickets_tab, text="Maintenance Tickets")
        tabs.add(announcements_tab, text="Announcements")
        TenantTickets(tickets_tab, self.tenant_id, self.tenant["pg_id"]).pack(
            fill="both", expand=True
        )
        self._show_announcements(announcements_tab)

    def _show_announcements(self, parent):
        """FEATURE: Tenant Home
        Show the PG's announcements newest first."""
        table = ttk.Treeview(parent, columns=("date", "message"), show="headings")
        table.heading("date", text="Date")
        table.heading("message", text="Announcement")
        table.column("date", width=180)
        table.column("message", width=650)
        table.pack(fill="both", expand=True)
        for item in get_announcements_for_pg(self.tenant["pg_id"]):
            table.insert("", "end", values=(item["created_at"], item["message"]))
