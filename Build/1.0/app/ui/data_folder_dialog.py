"""First-run window: the user chooses the folder where their Excel ledger files are kept.

Each Windows user on a PC (and each PC) makes their own choice, so every person has a separate
ledger. This is the one place the app shows a folder path, because choosing it needs it.
"""

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from app.core import config, paths, theme
from app.ui import widgets

WIDTH = 620
HEIGHT = 360


def ask_data_folder(initial: Path, notice: str = "") -> Path | None:
    """Show the window and return the chosen folder, or None if the user closes it."""
    dialog = DataFolderDialog(initial, notice)
    dialog.mainloop()
    chosen = dialog.chosen
    dialog.destroy()
    return chosen


class DataFolderDialog(ctk.CTk):
    def __init__(self, initial: Path, notice: str) -> None:
        super().__init__()
        self.chosen: Path | None = None
        self.title(config.APP_NAME)
        widgets.set_window_icon(self)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_PAGE)
        self.folder_var = ctk.StringVar(value=str(initial))

        card = widgets.card(self)
        card.pack(fill="both", expand=True, padx=24, pady=24)
        widgets.label(card, "Where should your ledger be kept?", size=theme.FONT_SIZE_CARD_TITLE).pack(anchor="w", padx=20, pady=(20, 4))
        widgets.label(
            card,
            "Your Excel ledger files are saved in this folder. Each person who uses this PC chooses their own folder, with their own login.",
            size=theme.FONT_SIZE_LABEL,
            color=theme.TEXT_MUTED,
            wraplength=WIDTH - 90,
            justify="left",
        ).pack(anchor="w", padx=20)

        widgets.field_label(card, "Folder").pack(fill="x", padx=20, pady=(16, 6))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20)
        self.entry = widgets.entry(row, textvariable=self.folder_var)
        self.entry.pack(side="left", fill="x", expand=True)
        widgets.secondary_button(row, "Browse", self._browse, width=100).pack(side="left", padx=(8, 0))
        self.problem = widgets.error_label(card)
        self.problem.configure(text=notice)
        self.problem.pack(fill="x", padx=20, pady=(6, 0))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(side="bottom", anchor="e", padx=20, pady=20)
        widgets.secondary_button(buttons, "Cancel", self.quit).pack(side="left", padx=(0, 10))
        widgets.primary_button(buttons, "Continue", self._continue, width=160).pack(side="left")
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.bind("<Return>", lambda _event: self._continue())
        self.bind("<Escape>", lambda _event: self.quit())
        self.after(100, self.focus_force)

    def _browse(self) -> None:
        picked = filedialog.askdirectory(parent=self, initialdir=self._existing_parent(), title="Choose a folder")
        if picked:
            self.folder_var.set(str(Path(picked)))

    def _existing_parent(self) -> str:
        folder = Path(self.folder_var.get().strip() or ".")
        while not folder.exists() and folder != folder.parent:
            folder = folder.parent
        return str(folder)

    def _continue(self) -> None:
        text = self.folder_var.get().strip()
        if not text:
            self.problem.configure(text="Choose a folder.")
            return
        folder = Path(text).expanduser()
        problem = paths.folder_problem(folder)
        if problem:
            self.problem.configure(text=problem)
            return
        self.chosen = folder
        self.quit()
