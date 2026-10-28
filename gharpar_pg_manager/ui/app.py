"""Main Tkinter application and navigation."""
import tkinter as tk
from tkinter import ttk
from ui.login_screen import LoginScreen


class GharParApp(tk.Tk):
    """FEATURE: Application Window
    Own the main window and display the login screen."""

    def __init__(self):
        """FEATURE: Application Window
        Build the screen and initialize its controls."""
        super().__init__()
        self.title("GharPar PG Manager")
        self.geometry("1000x680")
        self.minsize(800, 550)
        self.current_user = None
        self.container = ttk.Frame(self, padding=16)
        self.container.pack(fill="both", expand=True)
        self.show_login()

    def show_login(self):
        """FEATURE: Login Navigation
        Clear the active account and display the login screen."""
        self.current_user = None
        for widget in self.container.winfo_children():
            widget.destroy()
        LoginScreen(self.container, self).pack(fill="both", expand=True)

    def show_owner_list(self):
        """FEATURE: Owner PG List
        Return to the owner property list."""
        if self.current_user is None:
            self.show_login()
            return
        for widget in self.container.winfo_children():
            widget.destroy()
        from ui.owner_pg_list import OwnerPGList
        OwnerPGList(self.container, self, self.current_user).pack(fill="both", expand=True)

    def login_success(self, user):
        """FEATURE: Login Navigation
        Store the logged-in user and show the correct home screen."""
        self.current_user = user
        for widget in self.container.winfo_children():
            widget.destroy()
        if user["role"] == "owner":
            from ui.owner_pg_list import OwnerPGList
            OwnerPGList(self.container, self, user).pack(fill="both", expand=True)
        else:
            from ui.tenant_home import TenantHome
            TenantHome(self.container, self, user).pack(fill="both", expand=True)
