"""Owner dashboard for one PG."""
from tkinter import ttk
from core.pg_service import get_pg_summary
from ui.blueprint_panel import BlueprintPanel
from ui.owner_tickets_panel import OwnerTicketsPanel
from ui.owner_announcements_panel import OwnerAnnouncementsPanel


class OwnerPGView(ttk.Frame):
    """FEATURE: Owner PG View
    Show the blueprint on the left and task panels on the right."""

    def __init__(self, parent, app, user, pg):
        """FEATURE: Owner PG View
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.app = app
        self.user = user
        self.pg = pg
        self._show_heading()
        self.content = ttk.Frame(self)
        self.content.pack(fill="both", expand=True)
        self.blueprint = BlueprintPanel(self.content, self.app, self.pg)
        self.blueprint.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.right = ttk.Frame(self.content, width=360)
        self.right.pack(side="right", fill="both", expand=False)
        self.right.pack_propagate(False)
        self._show_taskbar()
        self.show_blueprint_summary()

    def _show_heading(self):
        """FEATURE: Owner PG View
        Show the PG title and return navigation."""
        ttk.Button(self, text="← All PGs", command=self.app.show_owner_list).pack(anchor="w")
        ttk.Label(self, text=self.pg["name"], font=("TkDefaultFont", 20, "bold")).pack(
            anchor="w", pady=8
        )

    def _show_taskbar(self):
        """FEATURE: Owner PG View
        Show the three task buttons on the right side."""
        bar = ttk.Frame(self.right)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="Blueprint", command=self.show_blueprint_summary).pack(
            side="left", expand=True, fill="x"
        )
        ttk.Button(bar, text="Tickets", command=self.show_tickets).pack(
            side="left", expand=True, fill="x"
        )
        ttk.Button(bar, text="Announcements", command=self.show_announcements).pack(
            side="left", expand=True, fill="x"
        )
        self.panel = ttk.Frame(self.right)
        self.panel.pack(fill="both", expand=True)

    def _clear_panel(self):
        """FEATURE: Owner PG View
        Clear the right panel before showing another task."""
        for widget in self.panel.winfo_children():
            widget.destroy()

    def show_blueprint_summary(self):
        """FEATURE: Owner PG View
        Show the occupancy and finance summary beside the blueprint."""
        self._clear_panel()
        summary = get_pg_summary(self.pg["id"])
        for key, label in [
            ("total_beds", "Total beds"),
            ("occupied_beds", "Occupied beds"),
            ("total_expected", "Expected to date"),
            ("total_collected", "Total collected"),
            ("total_overdue", "Total overdue"),
        ]:
            value = summary[key]
            if key.startswith("total_") and key != "total_beds":
                value = f"₹{value:,}"
            ttk.Label(self.panel, text=f"{label}: {value}").pack(anchor="w", pady=8)

    def show_tickets(self):
        """FEATURE: Owner Tickets
        Display unresolved maintenance tickets for this PG."""
        self._clear_panel()
        OwnerTicketsPanel(self.panel, self.pg).pack(fill="both", expand=True)

    def show_announcements(self):
        """FEATURE: Owner Announcements
        Display announcement management for this PG."""
        self._clear_panel()
        OwnerAnnouncementsPanel(self.panel, self.pg).pack(fill="both", expand=True)
