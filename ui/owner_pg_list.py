"""Owner PG selection screen."""
import tkinter as tk
from tkinter import ttk, messagebox
from core.pg_service import get_pgs_for_owner


class OwnerPGList(ttk.Frame):
    """FEATURE: Owner PG List
    Show the owner's PGs and occupancy."""

    def __init__(self, parent, app, user):
        """FEATURE: Owner PG List
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.app = app
        self.user = user
        ttk.Label(self, text="Your PG Properties", font=("TkDefaultFont", 20, "bold")).pack(anchor="w", pady=(0, 12))
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))
        ttk.Button(top, text="Log out", command=app.show_login).pack(side="right")
        self.table = ttk.Treeview(self, columns=("name", "address", "occupancy", "overdue"), show="headings", height=8)
        for col, title in [("name", "PG Name"), ("address", "Address"), ("occupancy", "Occupancy"), ("overdue", "Overdue tenants")]:
            self.table.heading(col, text=title)
            self.table.column(col, width=180)
        self.table.pack(fill="x", pady=8)
        self.pgs = get_pgs_for_owner(user["user_id"])
        for pg in self.pgs:
            self.table.insert("", "end", iid=str(pg["id"]), values=(
                pg["name"], pg["address"], f'{pg["occupied_beds"]}/{pg["total_beds"]} beds',
                pg["overdue_tenants"]
            ))
        ttk.Button(self, text="Open selected PG", command=self.open_selected).pack(anchor="w", pady=8)
        self.table.bind("<Double-1>", lambda event: self.open_selected())

    def open_selected(self):
        """FEATURE: Owner PG List
        Open the selected PG dashboard."""
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a PG", "Choose a PG first.")
            return
        from ui.owner_pg_view import OwnerPGView
        for widget in self.app.container.winfo_children():
            widget.destroy()
        pg = next(item for item in self.pgs if item["id"] == int(selected[0]))
        OwnerPGView(self.app.container, self.app, self.user, pg).pack(fill="both", expand=True)
