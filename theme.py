"""Shared black-gradient theme and bundled MoMo display font for ExamReadyTimer."""
import ctypes
import ctypes.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

BG, SURFACE, PANEL = "#080808", "#111111", "#191919"
HEADER, TEXT, MUTED = "#090909", "#FFFFFF", "#FFFFFF"
ACCENT, BORDER, BUTTON, BUTTON_HOVER = "#FFFFFF", "#303030", "#202020", "#343434"
FONT_FAMILY = "Momo Trust Display"
_FONT_READY = False


def _font_path():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    path = base / "assets" / "MomoTrustDisplay-Regular.ttf"
    if path.is_file():
        return path
    path = Path(sys.executable).resolve().parent / "MomoTrustDisplay-Regular.ttf"
    return path if path.is_file() else None


def _register_momo_font():
    global _FONT_READY
    if _FONT_READY:
        return
    path = _font_path()
    if path is None:
        return
    try:
        if sys.platform == "win32":
            ctypes.windll.gdi32.AddFontResourceExW(str(path), 0x10, None)
        elif sys.platform == "darwin":
            core_text_name = ctypes.util.find_library("CoreText")
            core_foundation_name = ctypes.util.find_library("CoreFoundation")
            if core_text_name and core_foundation_name:
                ct, cf = ctypes.CDLL(core_text_name), ctypes.CDLL(core_foundation_name)
                cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
                cf.CFURLCreateFromFileSystemRepresentation.argtypes = [
                    ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_ubyte
                ]
                encoded = os.fsencode(path)
                url = cf.CFURLCreateFromFileSystemRepresentation(None, encoded, len(encoded), 0)
                if url:
                    register = ct.CTFontManagerRegisterFontsForURL
                    register.restype = ctypes.c_ubyte
                    register.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
                    error = ctypes.c_void_p()
                    register(url, 1, ctypes.byref(error))
                    cf.CFRelease(url)
        elif sys.platform.startswith("linux"):
            font_dir = Path.home() / ".local" / "share" / "fonts" / "ExamReadyTimer"
            font_dir.mkdir(parents=True, exist_ok=True)
            target = font_dir / path.name
            if not target.exists() or target.stat().st_size != path.stat().st_size:
                shutil.copy2(path, target)
            cache = shutil.which("fc-cache")
            if cache:
                subprocess.run([cache, "-f", str(font_dir)], check=False,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _FONT_READY = True
    except (OSError, AttributeError, TypeError):
        pass


def _draw_gradient(canvas, width, height):
    canvas.delete("gradient")
    if width < 2 or height < 2:
        return
    top, bottom = (5, 5, 5), (25, 25, 25)
    bands = max(24, min(100, height // 8))
    for i in range(bands):
        ratio = i / max(1, bands - 1)
        rgb = tuple(round(top[j] + (bottom[j] - top[j]) * ratio) for j in range(3))
        colour = "#{:02x}{:02x}{:02x}".format(*rgb)
        y1, y2 = int(height * i / bands), int(height * (i + 1) / bands) + 1
        canvas.create_rectangle(0, y1, width, y2, fill=colour, outline=colour, tags="gradient")


def _apply_font_to_widget(widget, root):
    try:
        current = widget.cget("font")
        if not current:
            return
        font = tkfont.Font(root=root, font=current)
        actual = font.actual()
        if actual.get("family") == FONT_FAMILY:
            return
        replacement = tkfont.Font(root=root, family=FONT_FAMILY,
                                  size=actual.get("size", 10), weight="bold")
        widget.configure(font=replacement)
        root._examready_fonts.append(replacement)
    except (tk.TclError, TypeError, AttributeError):
        pass


def apply_dark_theme(root: tk.Misc) -> None:
    """Apply black gradient surfaces, white bold text and the bundled MoMo font."""
    _register_momo_font()
    root.configure(bg=BG)
    if not getattr(root, "_examready_gradient", None):
        canvas = tk.Canvas(root, highlightthickness=0, bd=0, bg=BG)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        canvas.tk.call('lower', canvas._w)
        def redraw(event):
            _draw_gradient(canvas, event.width, event.height)
            canvas.tk.call('lower', canvas._w)
        root.bind("<Configure>", redraw, add="+")
        root._examready_gradient = canvas
        root._examready_fonts = []
        root.bind_all("<Map>", lambda event: _apply_font_to_widget(event.widget, root), add="+")
    root.option_add("*Foreground", TEXT)
    root.option_add("*Background", BG)
    root.option_add("*Font", "{Momo Trust Display} 10 bold")
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
    style.configure(".", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10, "bold"))
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10, "bold"))
    style.configure("TLabelframe", background=BG, foreground=TEXT, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10, "bold"))
    style.configure("TButton", background=BUTTON, foreground=TEXT, padding=7,
                    bordercolor=BORDER, font=(FONT_FAMILY, 10, "bold"))
    style.map("TButton", background=[("active", BUTTON_HOVER), ("pressed", HEADER)],
              foreground=[("disabled", MUTED)])
    style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT,
                    bordercolor=BORDER, font=(FONT_FAMILY, 10, "bold"))
    style.configure("TCombobox", fieldbackground=PANEL, background=BUTTON,
                    foreground=TEXT, arrowcolor=TEXT, font=(FONT_FAMILY, 10, "bold"))
    style.map("TCombobox", fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", TEXT)], selectbackground=[("readonly", ACCENT)],
              selectforeground=[("readonly", BG)])
    style.configure("TNotebook", background=BG, bordercolor=BORDER, tabmargins=(2, 5, 2, 0))
    style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT, padding=(12, 7),
                    font=(FONT_FAMILY, 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", HEADER), ("active", BUTTON)],
              foreground=[("selected", TEXT), ("active", TEXT)])
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                    foreground=TEXT, bordercolor=BORDER, rowheight=28,
                    font=(FONT_FAMILY, 10, "bold"))
    style.map("Treeview", background=[("selected", "#343434")],
              foreground=[("selected", TEXT)])
    style.configure("Treeview.Heading", background=BUTTON, foreground=TEXT, relief="flat",
                    font=(FONT_FAMILY, 10, "bold"))
    style.map("Treeview.Heading", background=[("active", BUTTON_HOVER)])
    style.configure("TProgressbar", background=ACCENT, troughcolor=PANEL, bordercolor=BORDER)
    style.configure("TCheckbutton", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10, "bold"))
    style.configure("TRadiobutton", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10, "bold"))
    style.configure("TScrollbar", background=PANEL, troughcolor=BG, arrowcolor=TEXT)
