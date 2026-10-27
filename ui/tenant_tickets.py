"""Tenant maintenance ticket screen."""
import tkinter as tk
from tkinter import ttk, messagebox
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
        ttk.Button(self, text="Raise ticket", command=self.raise_ticket).pack(anchor="w", pady=8)
        self.refresh()

    def refresh(self):
        """FEATURE: Tenant Tickets
        Reload this tenant's tickets."""
        for item in self.table.get_children():
            self.table.delete(item)
        for ticket in get_tickets_for_tenant(self.tenant_id):
            values = (ticket["created_at"], ticket["category"], ticket["urgency"], ticket["status"], ticket["description"])
            self.table.insert("", "end", iid=str(ticket["id"]), values=values)

    def raise_ticket(self, dialog=None):
        """FEATURE: Tenant Tickets
        Collect ticket fields in a form and create a ticket."""
        if dialog is None:
            dialog = tk.Toplevel(self.winfo_toplevel())
            dialog.title("Raise Maintenance Ticket")
            dialog.transient(self.winfo_toplevel())
            self.ticket_category = ttk.Combobox(dialog, values=config.TICKET_CATEGORIES, state="readonly")
            self.ticket_urgency = ttk.Combobox(dialog, values=config.TICKET_URGENCIES, state="readonly")
            self.ticket_description = ttk.Entry(dialog, width=45)
            self.ticket_category.set(config.TICKET_CATEGORIES[0])
            self.ticket_urgency.set(config.TICKET_URGENCIES[1])
            for label, widget in [("Category", self.ticket_category), ("Urgency", self.ticket_urgency), ("Description", self.ticket_description)]:
                ttk.Label(dialog, text=label).pack(anchor="w", padx=12, pady=(8, 0))
                widget.pack(fill="x", padx=12)
            ttk.Button(dialog, text="Submit ticket", command=lambda: self.raise_ticket(dialog)).pack(pady=12)
            dialog.grab_set()
            return
        try:
            create_ticket(self.tenant_id, self.ticket_category.get(), self.ticket_description.get(), self.ticket_urgency.get())
        except ValueError as error:
            messagebox.showerror("Could not create ticket", str(error), parent=dialog)
            return
        dialog.destroy()
        self.refresh()
