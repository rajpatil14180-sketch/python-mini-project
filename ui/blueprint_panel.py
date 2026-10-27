"""Room and bed blueprint panel."""
import tkinter as tk
from tkinter import ttk
from core.pg_service import get_pg_layout
from ui.bed_detail_window import BedDetailWindow
from config import BED_BORDER_COLOURS


class BlueprintPanel(ttk.Frame):
    """FEATURE: PG Blueprint
    Display rooms and beds with borders showing their current status."""

    def __init__(self, parent, app, pg):
        """FEATURE: PG Blueprint
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.app = app
        self.pg = pg
        self.refresh()

    def refresh(self):
        """FEATURE: PG Blueprint
        Rebuild the blueprint using current room and bed data."""
        for widget in self.winfo_children():
            widget.destroy()
        for room in get_pg_layout(self.pg["id"]):
            self._show_room(room)
        washroom = ttk.LabelFrame(self, text="Common washroom")
        washroom.pack(fill="x", pady=6)
        ttk.Label(washroom, text="Shared by Rooms 3 and 4").pack(anchor="w", padx=10, pady=6)

    def _show_room(self, room):
        """FEATURE: PG Blueprint
        Display one room, its beds, and its washroom information."""
        bath = "Attached bathroom" if room["has_attached_bath"] else "Common washroom"
        frame = ttk.LabelFrame(self, text=f'Room {room["room_no"]} · {bath}')
        frame.pack(fill="x", pady=6)
        for bed in room["beds"]:
            self._show_bed(frame, room, bed)

    def _show_bed(self, parent, room, bed):
        """FEATURE: PG Blueprint
        Display one bed with a status-coloured border and tenant label."""
        status = bed["status"]
        tenant = bed["tenant_name"] or "Available"
        label = f'Bed {bed["label"]}\n{tenant}\n₹{bed["base_yearly_price"]:,}/year'
        colour = BED_BORDER_COLOURS[status]
        border = tk.Frame(parent, highlightbackground=colour, highlightthickness=3, bd=0)
        border.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        button = ttk.Button(
            border, text=label,
            command=lambda item=bed: self.open_bed(item),
        )
        button.pack(fill="both", expand=True, padx=2, pady=2)

    def open_bed(self, bed):
        """FEATURE: Bed Details
        Open the details popup for the selected bed."""
        window = tk.Toplevel(self.winfo_toplevel())
        window.title("Bed Details")
        window.geometry("650x560")
        window.transient(self.winfo_toplevel())
        BedDetailWindow(window, self.app, bed["bed_id"], self.pg, self.refresh).pack(fill="both", expand=True)
