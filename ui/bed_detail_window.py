"""Bed details and owner actions screen."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from core.pg_service import get_bed_details
from core.tenant_service import add_payment, vacate_tenant
from config import PAYMENT_MODES


class BedDetailWindow(ttk.Frame):
    """FEATURE: Bed Details
    Show bed information and allow owner payment and vacancy actions."""

    def __init__(self, parent, app, bed_id, pg, on_close=None):
        """FEATURE: Bed Details
        Build the screen and initialize its controls."""
        super().__init__(parent, padding=8)
        self.app = app
        self.pg = pg
        self.bed_id = bed_id
        self.on_close = on_close
        self.details = get_bed_details(bed_id)
        self._show_header()
        if self.details["tenant"] is None:
            self._show_empty_bed()
        else:
            self._show_tenant()
        ttk.Button(self, text="Close", command=self.close).pack(pady=8)

    def _show_header(self):
        """FEATURE: Bed Details
        Show the selected room, bed, PG, and base price."""
        bed = self.details["bed"]
        title = f'Room {self.details["room_no"]} · Bed {bed["label"]}'
        ttk.Label(self, text=title, font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        ttk.Label(self, text=self.details["pg_name"]).pack(anchor="w")
        ttk.Label(self, text=f'Base yearly price: ₹{bed["base_yearly_price"]:,}').pack(anchor="w")

    def _show_empty_bed(self):
        """FEATURE: Bed Details
        Show availability and the action to add a tenant."""
        ttk.Label(self, text="Status: Available").pack(anchor="w", pady=8)
        ttk.Label(self, text="No tenant is currently assigned to this bed.").pack(anchor="w")
        ttk.Button(self, text="Add Tenant", command=self.add_tenant).pack(anchor="w", pady=8)

    def _show_tenant(self):
        """FEATURE: Bed Details
        Show tenant profile, financial summary, and payment history."""
        tenant = self.details["tenant"]
        info = self.details["financials"]
        ttk.Label(self, text=f'Tenant: {tenant["name"]}').pack(anchor="w", pady=2)
        ttk.Label(self, text=f'Phone: {tenant["phone"]}').pack(anchor="w")
        ttk.Label(self, text=f'Joined: {tenant["join_date"]}').pack(anchor="w")
        self._show_financial_labels(info)
        self._show_payments(info["payments"])
        self._show_tenant_actions(tenant["tenant_id"])

    def _show_financial_labels(self, info):
        """FEATURE: Bed Details
        Display agreed price, payments, remaining balance, and due dates."""
        labels = [
            f'Agreed yearly price: ₹{info["agreed_yearly_price"]:,}',
            f'Total paid: ₹{info["total_paid"]:,}',
            f'Due left: ₹{info["due_left"]:,}',
            f'Next due date: {info["next_due_date"] or "None"}',
            f'Overdue amount: ₹{info["overdue_amount"]:,}',
        ]
        for label in labels:
            ttk.Label(self, text=label).pack(anchor="w", pady=1)

    def _show_payments(self, payments):
        """FEATURE: Bed Details
        Show payment dates, amounts, and payment modes."""
        ttk.Label(self, text="Payment history", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        table = ttk.Treeview(self, columns=("date", "amount", "mode"), show="headings", height=4)
        for column, heading in [("date", "Paid on"), ("amount", "Amount"), ("mode", "Mode")]:
            table.heading(column, text=heading)
            table.column(column, width=140)
        table.pack(fill="x")
        for payment in payments:
            values = (payment["paid_on"], f'₹{payment["amount"]:,}', payment["mode"])
            table.insert("", "end", values=values)

    def _show_tenant_actions(self, tenant_id):
        """FEATURE: Record Payment
        Show actions to record a payment or vacate the tenant."""
        buttons = ttk.Frame(self)
        buttons.pack(anchor="w", pady=8)
        ttk.Button(buttons, text="Record Payment", command=lambda: self.record_payment(tenant_id)).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Vacate", command=lambda: self.vacate(tenant_id)).pack(side="left")

    def record_payment(self, tenant_id, dialog=None):
        """FEATURE: Record Payment
        Collect and save a payment using a form with validated fields."""
        if dialog is None:
            dialog = tk.Toplevel(self.winfo_toplevel())
            dialog.title("Record Payment")
            dialog.transient(self.winfo_toplevel())
            self.payment_amount = ttk.Entry(dialog)
            self.payment_date = ttk.Entry(dialog)
            self.payment_mode = ttk.Combobox(dialog, values=PAYMENT_MODES, state="readonly")
            self.payment_date.insert(0, date.today().isoformat())
            self.payment_mode.set(PAYMENT_MODES[0])
            for label, widget in [("Amount in rupees", self.payment_amount), ("Date (YYYY-MM-DD)", self.payment_date), ("Payment mode", self.payment_mode)]:
                ttk.Label(dialog, text=label).pack(anchor="w", padx=12, pady=(8, 0))
                widget.pack(fill="x", padx=12)
            ttk.Button(dialog, text="Save payment", command=lambda: self.record_payment(tenant_id, dialog)).pack(pady=12)
            return
        try:
            amount = int(self.payment_amount.get())
            paid_on = date.fromisoformat(self.payment_date.get().strip())
            add_payment(tenant_id, amount, paid_on, self.payment_mode.get())
        except (ValueError, TypeError) as error:
            messagebox.showerror("Payment not recorded", str(error), parent=dialog)
            return
        messagebox.showinfo("Payment recorded", "The payment was saved.", parent=dialog)
        dialog.destroy()
        self.close()

    def vacate(self, tenant_id):
        """FEATURE: Vacate Tenant
        Confirm vacancy and preserve the tenant's historical records."""
        confirm = messagebox.askyesno("Vacate tenant", "Vacate this tenant and release the bed?", parent=self.winfo_toplevel())
        if confirm:
            vacate_tenant(tenant_id)
            self.close()

    def add_tenant(self):
        """FEATURE: Add Tenant
        Open the tenant form for this available bed."""
        from ui.add_tenant_window import AddTenantWindow
        bed = dict(self.details["bed"])
        bed["room_no"] = self.details["room_no"]
        dialog = tk.Toplevel(self.winfo_toplevel())
        dialog.title("Add Tenant")
        dialog.geometry("470x540")
        dialog.transient(self.winfo_toplevel())
        AddTenantWindow(dialog, bed, self.refresh_parent).pack(fill="both", expand=True)
        dialog.grab_set()

    def refresh_parent(self):
        """FEATURE: Bed Details
        Refresh the blueprint after a tenant record changes."""
        self.close()

    def close(self):
        """FEATURE: Bed Details
        Close the popup and refresh the parent blueprint."""
        self.winfo_toplevel().destroy()
        if self.on_close:
            self.on_close()
