"""Screen for an owner to add a tenant to an available bed."""
from datetime import date
from tkinter import ttk, messagebox
from core.pricing import calculate_agreed_price
from core.tenant_service import add_tenant


class AddTenantWindow(ttk.Frame):
    """FEATURE: Add Tenant
    Collect tenant account details and the editable agreed yearly price."""

    def __init__(self, parent, bed, on_saved=None):
        """FEATURE: Add Tenant
        Build the screen and initialize its controls."""
        super().__init__(parent, padding=8)
        self.bed = bed
        self.on_saved = on_saved
        title = f'Room {bed["room_no"]} · Bed {bed["label"]}'
        ttk.Label(self, text=title, font=("TkDefaultFont", 15, "bold")).pack(anchor="w", padx=8, pady=8)
        self.fields = {}
        self._build_form()

    def _build_form(self):
        """FEATURE: Add Tenant
        Build the tenant details form and prefill the calculated price."""
        form = ttk.Frame(self, padding=8)
        form.pack(fill="both", expand=True)
        labels = [("Username", "username"), ("Temporary password", "password"), ("Full name", "name"), ("Phone", "phone"), ("Joining date (YYYY-MM-DD)", "join_date"), ("Deposit (₹)", "deposit"), ("Agreed yearly price (editable)", "agreed_price")]
        today = date.today()
        defaults = {"join_date": today.isoformat(), "deposit": "10000", "agreed_price": str(calculate_agreed_price(self.bed["base_yearly_price"], today))}
        for row, (label, key) in enumerate(labels):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(form, width=25, show="*" if key == "password" else "")
            entry.grid(row=row, column=1, padx=5, pady=5)
            entry.insert(0, defaults.get(key, ""))
            self.fields[key] = entry
        self.fields["join_date"].bind("<FocusOut>", self.update_price)
        self.fields["join_date"].bind("<Return>", self.update_price)
        ttk.Label(form, text=f'Base yearly price: ₹{self.bed["base_yearly_price"]:,}').grid(row=len(labels), column=0, columnspan=2, sticky="w", padx=5, pady=6)
        ttk.Button(self, text="Create tenant", command=self.save).pack(pady=8)

    def update_price(self, event=None):
        """FEATURE: Add Tenant
        Recalculate the suggested price when the joining date changes."""
        try:
            join_date = date.fromisoformat(self.fields["join_date"].get().strip())
        except ValueError:
            return
        price = calculate_agreed_price(self.bed["base_yearly_price"], join_date)
        self.fields["agreed_price"].delete(0, "end")
        self.fields["agreed_price"].insert(0, str(price))

    def save(self):
        """FEATURE: Add Tenant
        Validate the form and create the tenant using the agreed price."""
        try:
            deposit = int(self.fields["deposit"].get())
            agreed_price = int(self.fields["agreed_price"].get())
            if deposit < 0 or agreed_price < 0:
                raise ValueError("Deposit and agreed price cannot be negative.")
            join_date = date.fromisoformat(self.fields["join_date"].get().strip())
            add_tenant(self.bed["bed_id"], self.fields["name"].get(), self.fields["phone"].get(), join_date, deposit, agreed_price, self.fields["username"].get(), self.fields["password"].get())
        except ValueError as error:
            messagebox.showerror("Could not add tenant", str(error), parent=self.winfo_toplevel())
            return
        except Exception as error:
            messagebox.showerror("Could not add tenant", f"Please check the details.\n{error}", parent=self.winfo_toplevel())
            return
        messagebox.showinfo("Tenant added", "Tenant account created successfully.", parent=self.winfo_toplevel())
        self.winfo_toplevel().destroy()
        if self.on_saved:
            self.on_saved()
