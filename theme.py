"""Shared dark colour palette for ExamReadyTimer desktop windows."""
import tkinter as tk
from tkinter import ttk

BG = "#0B1020"
SURFACE = "#111B30"
PANEL = "#18243D"
HEADER = "#172544"
TEXT = "#FFFFFF"
MUTED = TEXT
ACCENT = TEXT
BORDER = "#34415D"
BUTTON = "#263657"
BUTTON_HOVER = "#34496F"


def apply_dark_theme(root: tk.Misc) -> None:
    """Apply readable white text and consistent dark styling to every Tk window."""
    root.configure(bg=BG)
    # Classic Tk widgets and ttk widgets use separate style systems.
    root.option_add("*Foreground", TEXT)
    root.option_add("*Background", BG)
    for widget in ("Label", "LabelFrame", "Entry", "Text", "Listbox", "Button",
                   "Checkbutton", "Radiobutton", "Menubutton", "Menu", "Spinbox", "Scale"):
        root.option_add(f"*{widget}.foreground", TEXT)
    root.option_add("*Entry.background", PANEL)
    root.option_add("*Text.background", PANEL)
    root.option_add("*Listbox.background", SURFACE)
    root.option_add("*Button.background", BUTTON)
    root.option_add("*Checkbutton.background", BG)
    root.option_add("*Radiobutton.background", BG)
    root.option_add("*Menu.background", PANEL)
    root.option_add("*Menu.activeBackground", BUTTON_HOVER)
    root.option_add("*Menu.activeForeground", TEXT)
    root.option_add("*Entry.insertBackground", TEXT)
    root.option_add("*Text.insertBackground", TEXT)
    root.option_add("*Entry.selectForeground", TEXT)
    root.option_add("*Text.selectForeground", TEXT)
    root.option_add("*Listbox.selectForeground", TEXT)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.background", PANEL)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=BG, foreground=TEXT)
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("TLabelframe", background=BG, foreground=ACCENT, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT)
    style.configure("TButton", background=BUTTON, foreground=TEXT, padding=7, bordercolor=BORDER)
    style.map("TButton", background=[("active", BUTTON_HOVER), ("pressed", HEADER)],
              foreground=[("disabled", MUTED)])
    style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT,
                    bordercolor=BORDER)
    style.configure("TCombobox", fieldbackground=PANEL, background=BUTTON,
                    foreground=TEXT, arrowcolor=TEXT)
    style.map("TCombobox", fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", TEXT)], selectbackground=[("readonly", ACCENT)],
              selectforeground=[("readonly", BG)])
    style.configure("TNotebook", background=BG, bordercolor=BORDER, tabmargins=(2, 5, 2, 0))
    style.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(12, 7))
    style.map("TNotebook.Tab", background=[("selected", HEADER), ("active", BUTTON)],
              foreground=[("selected", TEXT), ("active", TEXT)])
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                    foreground=TEXT, bordercolor=BORDER, rowheight=26)
    style.map("Treeview", background=[("selected", "#34496F")],
              foreground=[("selected", TEXT)])
    style.configure("Treeview.Heading", background=BUTTON, foreground=TEXT, relief="flat")
    style.map("Treeview.Heading", background=[("active", BUTTON_HOVER)])
    style.configure("TProgressbar", background=ACCENT, troughcolor=PANEL, bordercolor=BORDER)
    style.configure("TCheckbutton", background=BG, foreground=TEXT)
    style.configure("TRadiobutton", background=BG, foreground=TEXT)
    style.configure("TScrollbar", background=PANEL, troughcolor=BG, arrowcolor=TEXT)
