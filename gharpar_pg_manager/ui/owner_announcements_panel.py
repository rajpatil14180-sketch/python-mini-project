"""Owner announcements panel."""
import tkinter as tk
from tkinter import ttk, messagebox
from core.announcement_service import add_announcement, get_announcements_for_pg, delete_announcement


class OwnerAnnouncementsPanel(ttk.Frame):
    """FEATURE: Owner Announcements
    List, add, and delete announcements for one PG."""

    def __init__(self, parent, pg):
        """FEATURE: Owner Announcements
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.pg = pg
        self.table = ttk.Treeview(self, columns=("date", "message"), show="headings")
        self.table.heading("date", text="Created")
        self.table.heading("message", text="Announcement")
        self.table.column("date", width=180)
        self.table.column("message", width=600)
        self.table.pack(fill="both", expand=True)
        buttons = ttk.Frame(self)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Add announcement", command=self.add).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Delete selected", command=self.delete).pack(side="left")
        self.refresh()

    def refresh(self):
        """FEATURE: Owner Announcements
        Reload the announcement table."""
        for item in self.table.get_children():
            self.table.delete(item)
        for item in get_announcements_for_pg(self.pg["id"]):
            self.table.insert("", "end", iid=str(item["id"]), values=(item["created_at"], item["message"]))

    def add(self, dialog=None):
        """FEATURE: Add Announcement
        Collect an announcement in a form and save it."""
        if dialog is None:
            dialog = tk.Toplevel(self.winfo_toplevel())
            dialog.title("New Announcement")
            dialog.transient(self.winfo_toplevel())
            self.announcement_message = ttk.Entry(dialog, width=60)
            ttk.Label(dialog, text="Announcement message").pack(anchor="w", padx=12, pady=(10, 0))
            self.announcement_message.pack(fill="x", padx=12, pady=8)
            ttk.Button(dialog, text="Post announcement", command=lambda: self.add(dialog)).pack(pady=10)
            dialog.grab_set()
            return
        try:
            add_announcement(self.pg["id"], self.announcement_message.get())
        except ValueError as error:
            messagebox.showerror("Invalid announcement", str(error), parent=dialog)
            return
        dialog.destroy()
        self.refresh()

    def delete(self):
        """FEATURE: Delete Announcement
        Delete the selected announcement after confirmation."""
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select announcement", "Choose an announcement first.", parent=self.winfo_toplevel())
            return
        if messagebox.askyesno("Confirm", "Delete this announcement?", parent=self.winfo_toplevel()):
            delete_announcement(int(selected[0]))
            self.refresh()
