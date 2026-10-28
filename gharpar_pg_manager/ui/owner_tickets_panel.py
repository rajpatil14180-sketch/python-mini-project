"""Owner maintenance ticket panel."""
from tkinter import ttk, messagebox
from core.ticket_service import get_tickets_for_pg, update_ticket_status
import config


class OwnerTicketsPanel(ttk.Frame):
    """FEATURE: Owner Tickets
    List tickets and allow their status to be updated."""

    def __init__(self, parent, pg):
        """FEATURE: Owner Tickets
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.pg = pg
        self.table = ttk.Treeview(self, columns=("tenant", "room", "category", "urgency", "status", "age", "description"), show="headings")
        for col, title in [("tenant", "Tenant"), ("room", "Room/Bed"), ("category", "Category"), ("urgency", "Urgency"), ("status", "Status"), ("age", "Age (days)"), ("description", "Description")]:
            self.table.heading(col, text=title)
            self.table.column(col, width=120)
        self.table.pack(fill="both", expand=True)
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=8)
        self.status = ttk.Combobox(controls, values=config.TICKET_STATUSES, state="readonly", width=18)
        self.status.set("In Progress")
        self.status.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Update selected ticket", command=self.update_selected).pack(side="left")
        self.refresh()

    def refresh(self):
        """FEATURE: Owner Tickets
        Reload the ticket table."""
        for item in self.table.get_children():
            self.table.delete(item)
        for ticket in get_tickets_for_pg(self.pg["id"]):
            room = f'R{ticket["room_no"]}{ticket["bed_label"]}' if ticket["room_no"] else "—"
            self.table.insert("", "end", iid=str(ticket["id"]), values=(
                ticket["tenant_name"], room, ticket["category"], ticket["urgency"],
                ticket["status"], ticket["age_in_days"], ticket["description"]
            ))

    def update_selected(self):
        """FEATURE: Update Ticket
        Change status for the selected ticket."""
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select ticket", "Choose a ticket first.")
            return
        update_ticket_status(int(selected[0]), self.status.get())
        self.refresh()
