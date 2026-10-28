"""Small reusable Tkinter widgets."""
import tkinter as tk
from tkinter import ttk


def clear_frame(frame):
    """FEATURE: UI Helpers
    Remove all widgets from a frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def make_treeview(parent, columns, headings):
    """FEATURE: UI Helpers
    Create a scrollable table with the supplied columns and headings."""
    wrapper = ttk.Frame(parent)
    wrapper.pack(fill="both", expand=True)
    tree = ttk.Treeview(wrapper, columns=columns, show="headings")
    for column, heading in zip(columns, headings):
        tree.heading(column, text=heading)
        tree.column(column, width=130, anchor="w")
    scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return tree
