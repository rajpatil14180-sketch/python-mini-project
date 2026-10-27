"""Tenant maintenance ticket screen."""
from tkinter import ttk, messagebox, simpledialog
from core.ticket_service import create_ticket, get_tickets_for_tenant
import config


class TenantTickets(ttk.Frame):
    """FEATURE: Tenant Tickets
    Let a tenant create tickets and view their own ticket history."""

    def __init__(self, parent, tenant_id, pg_id):
        """FEATURE: Tenant Tickets
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.tenant_id = tenant_id
        self.pg_id = pg_id
        self.table = ttk.Treeview(self, columns=("date", "category", "urgency", "status", "description"), show="headings")
        for col, title in [("date", "Created"), ("category", "Category"), ("urgency", "Urgency"), ("status", "Status"), ("description", "Description")]:
            self.table.heading(col, text=title)
            self.table.column(col, width=130)
        self.table.pack(fill="both", expand=True)
        buttons = ttk.Frame(self)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Raise ticket", command=self.raise_ticket).pack(side="left")
        self.refresh()

    def refresh(self):
        """FEATURE: Tenant Tickets
        Reload this tenant's tickets."""
        for item in self.table.get_children():
            self.table.delete(item)
        for ticket in get_tickets_for_tenant(self.tenant_id):
            self.table.insert("", "end", iid=str(ticket["id"]), values=(
                ticket["created_at"], ticket["category"], ticket["urgency"],
                ticket["status"], ticket["description"]
            ))

    def raise_ticket(self):
        """FEATURE: Tenant Tickets
        Collect ticket fields and create a ticket."""
        category = simpledialog.askstring("Maintenance ticket", "Category: " + ", ".join(config.TICKET_CATEGORIES), parent=self)
        if not category:
            return
        category = next((item for item in config.TICKET_CATEGORIES if item.lower() == category.strip().lower()), "")
        if not category:
            messagebox.showerror("Invalid category", "Choose one of the listed categories.")
            return
        urgency = simpledialog.askstring("Maintenance ticket", "Urgency: Low, Medium, or High", parent=self)
        if not urgency:
            return
        urgency = next((item for item in config.TICKET_URGENCIES if item.lower() == urgency.strip().lower()), "")
        if not urgency:
            messagebox.showerror("Invalid urgency", "Choose Low, Medium, or High.")
            return
        description = simpledialog.askstring("Maintenance ticket", "Describe the issue:", parent=self)
        if not description:
            return
        try:
            create_ticket(self.tenant_id, category, description, urgency)
            self.refresh()
        except ValueError as error:
            messagebox.showerror("Could not create ticket", str(error))
