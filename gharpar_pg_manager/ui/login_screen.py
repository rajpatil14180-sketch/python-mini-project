"""Login screen."""
import tkinter as tk
from tkinter import ttk, messagebox
from core.auth import login


class LoginScreen(ttk.Frame):
    """FEATURE: Login Screen
    Collect credentials and route a successfully authenticated user."""

    def __init__(self, parent, app):
        """FEATURE: Login Screen
        Build the screen and initialize its controls."""
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="GharPar PG Manager", font=("TkDefaultFont", 22, "bold")).pack(pady=(70, 10))
        ttk.Label(self, text="Sign in with your account").pack(pady=(0, 20))
        form = ttk.Frame(self)
        form.pack()
        ttk.Label(form, text="Username").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.username = ttk.Entry(form, width=30)
        self.username.grid(row=0, column=1, padx=8, pady=8)
        ttk.Label(form, text="Password").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.password = ttk.Entry(form, width=30, show="*")
        self.password.grid(row=1, column=1, padx=8, pady=8)
        ttk.Button(self, text="Login", command=self.submit).pack(pady=12)
        self.password.bind("<Return>", lambda event: self.submit())

    def submit(self):
        """FEATURE: Login Screen
        Authenticate the entered username and password."""
        user = login(self.username.get().strip(), self.password.get())
        if user is None:
            messagebox.showerror("Login failed", "Incorrect username or password, or inactive account.")
            return
        self.app.login_success(user)
