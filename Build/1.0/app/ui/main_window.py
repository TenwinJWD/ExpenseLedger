"""The app window: the start-up routing, and the main frame with the sidebar (Design.md Section 2).

App decides which screen to show: create account, login, or the main frame.
MainView is the frame after login. Its pages are placeholders until Phases 5 and 7.
"""

import threading
import tkinter as tk
import webbrowser
from typing import Callable

import customtkinter as ctk

from app.core import config, paths, theme
from app.services.auth_service import AuthService
from app.services.entry_service import EntryService
from app.services import update_service
from app.services.subhead_service import SubheadService
from app.storage.account_store import CorruptAccountFileError
from app.ui import widgets
from app.ui.expense_report_view import ExpenseReportView
from app.ui.gradient import GradientCanvas
from app.ui.main_entry_view import MainEntryView
from app.ui.change_password_popup import ChangePasswordPopup
from app.ui.create_account_view import CreateAccountView
from app.ui.login_view import LoginView


class App(ctk.CTk):
    """The window. It shows one screen at a time."""

    def __init__(self, auth: AuthService, subheads: SubheadService, entries: EntryService) -> None:
        super().__init__()
        self.auth = auth
        self.subheads = subheads
        self.entries = entries
        self.view: ctk.CTkFrame | None = None
        self.update_info: update_service.UpdateInfo | None = None
        self.title(config.APP_NAME)
        self.geometry(f"{theme.MIN_WINDOW_WIDTH}x{theme.MIN_WINDOW_HEIGHT}")
        self.minsize(theme.MIN_WINDOW_WIDTH, theme.MIN_WINDOW_HEIGHT)
        self.configure(fg_color=theme.BG_PAGE)
        self._set_app_icon()
        try:
            has_account = self.auth.has_account()
        except CorruptAccountFileError:
            has_account = True
        if has_account:
            self.show_login()
        else:
            self.show_create()
        self._start_update_check()

    def _start_update_check(self) -> None:
        """Look for a newer version in the background, once. Skipped when no update address is set."""
        if not config.UPDATE_URL:
            return
        result: list = []
        threading.Thread(target=lambda: result.append(update_service.check_for_update(config.UPDATE_URL)), daemon=True).start()
        self._poll_update_check(result)

    def _poll_update_check(self, result: list) -> None:
        if not result:
            self.after(500, lambda: self._poll_update_check(result))
            return
        self.update_info = result[0]
        if self.update_info is not None and isinstance(self.view, MainView):
            self.view.offer_update(self.update_info)

    def _set_app_icon(self) -> None:
        """The app icon in the title bar and the taskbar. Missing icon file: keep the default icon."""
        try:
            self._icon = tk.PhotoImage(file=str(paths.asset_file("app-icon.png")))
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass

    def _show(self, view: ctk.CTkFrame) -> None:
        if self.view is not None:
            self.view.destroy()
        self.view = view
        view.pack(fill="both", expand=True)

    def show_create(self) -> None:
        self._show(CreateAccountView(self, self.auth, on_done=lambda: self.show_login("Account created. Please log in.")))

    def show_login(self, notice: str = "") -> None:
        self._show(LoginView(self, self.auth, on_success=self.show_main, notice=notice))

    def show_main(self) -> None:
        view = MainView(self, self.auth, self.subheads, self.entries, on_logout=self.show_login)
        self._show(view)
        if self.update_info is not None:
            view.offer_update(self.update_info)


class SidebarCanvas(GradientCanvas):
    """The sidebar: a gradient canvas that places its items and keeps each background matched to the gradient."""

    def __init__(self, master) -> None:
        super().__init__(master, theme.SIDE_TOP, theme.SIDE_BOTTOM, width=theme.SIDEBAR_WIDTH, bg=theme.SIDE_BOTTOM)
        self._items: list[tuple] = []

    def add(self, widget, x: int, y_of: Callable[[int], int], height: int) -> None:
        """Place a widget at x and at a height that may depend on the window height (for bottom items)."""
        self._items.append((widget, x, y_of, height))
        widget.place(x=x, y=y_of(max(1, self.winfo_height())))

    def on_repaint(self) -> None:
        height = max(1, self.winfo_height())
        for widget, x, y_of, item_height in self._items:
            y = y_of(height)
            widget.place_configure(x=x, y=y)
            colour = self.colour_at(y + item_height / 2)
            if isinstance(widget, tk.Canvas):
                widget.configure(bg=colour)
            else:
                widget.configure(bg_color=colour)


class MainView(ctk.CTkFrame):
    """Sidebar on the left, page on the right."""

    PAGES = (
        ("entry", "Main Entry", "Main Entry", "Record a daily collection or a Treesa Agencies entry"),
        ("report", "Expense Report", "Expense Report", "All submitted entries, oldest first"),
    )

    def __init__(self, master, auth: AuthService, subheads: SubheadService, entries: EntryService, on_logout: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.BG_PAGE)
        self.auth = auth
        self.subheads = subheads
        self.entries = entries
        self.on_logout = on_logout
        self._toast_job = None
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._nav_bars: dict[str, ctk.CTkFrame] = {}
        self._pages: dict[str, ctk.CTkFrame] = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = SidebarCanvas(self)
        self.sidebar = sidebar
        self._update_button = None
        sidebar.grid(row=0, column=0, sticky="nsew")
        self._build_sidebar(sidebar)

        self.content = ctk.CTkFrame(self, fg_color=theme.BG_PAGE, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        for key, _nav_text, title, description in self.PAGES:
            if key == "entry":
                page = MainEntryView(self.content, self.subheads, self.entries)
            elif key == "report":
                page = ScrollablePage(self.content, lambda parent: ExpenseReportView(parent, self.subheads, self.entries))
            else:
                page = PlaceholderPage(self.content, title, description)
            self._pages[key] = page
        self.toast = ctk.CTkLabel(
            self.content,
            text="",
            fg_color=theme.SUCCESS_BG,
            text_color=theme.CREDIT,
            corner_radius=theme.BUTTON_RADIUS,
            font=widgets.text_font(theme.FONT_SIZE_BODY),
            padx=16,
            pady=10,
        )
        self.show_page("entry")

    def _build_sidebar(self, sidebar: "SidebarCanvas") -> None:
        """Brand and menu at the top, in one group; Change Password, Logout, and the footer at the bottom."""
        sidebar.add(ctk.CTkLabel(sidebar, text="Expense Ledger", font=widgets.text_font(16), text_color=theme.SIDEBAR_TEXT, anchor="w"), 20, lambda _h: 22, 26)
        sidebar.add(ctk.CTkLabel(sidebar, text=f"Version {config.APP_VERSION}", font=widgets.text_font(theme.FONT_SIZE_LABEL), text_color=theme.TEXT_MUTED, anchor="w"), 20, lambda _h: 50, 18)

        for index, (key, nav_text, _title, _description) in enumerate(self.PAGES):
            top = 96 + index * 46
            bar = ctk.CTkFrame(sidebar, width=4, height=40, corner_radius=2, fg_color="transparent")
            button = self._nav_button(sidebar, nav_text, lambda page=key: self.show_page(page))
            sidebar.add(bar, 12, lambda _h, y=top: y, 40)
            sidebar.add(button, 20, lambda _h, y=top: y, 40)
            self._nav_buttons[key] = button
            self._nav_bars[key] = bar

        logout = self._nav_button(sidebar, "Logout", self.on_logout)
        sidebar.add(logout, 12, lambda h: h - 96, 40)

        change_button = ctk.CTkButton(
            sidebar,
            text="Change Password",
            command=self.open_change_password,
            anchor="w",
            width=196,
            height=36,
            corner_radius=theme.BUTTON_RADIUS,
            fg_color="transparent",
            hover_color="#24242C",
            text_color=theme.SIDEBAR_TEXT,
            font=widgets.text_font(theme.FONT_SIZE_BODY),
        )
        sidebar.add(change_button, 20, lambda h: h - 154, 36)

        footer = ctk.CTkLabel(sidebar, text=f"Developed by {config.APP_AUTHOR}", font=ctk.CTkFont(family=theme.FONT_FAMILY_LIGHT, size=theme.FONT_SIZE_LABEL, weight="normal"), text_color=theme.SIDEBAR_TEXT, anchor="w")
        sidebar.add(footer, 20, lambda h: h - 36, 18)

    def _nav_button(self, parent, text: str, command) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            anchor="w",
            width=196,
            height=40,
            corner_radius=theme.BUTTON_RADIUS,
            fg_color="transparent",
            hover_color="#24242C",
            text_color=theme.SIDEBAR_TEXT,
            font=widgets.text_font(theme.FONT_SIZE_BODY),
        )

    def show_page(self, key: str) -> None:
        """Show one page and highlight its menu item (FR-7)."""
        for name, page in self._pages.items():
            page.grid_forget()
        page = self._pages[key]
        page.refresh()  # every page reloads its data when it opens (Design.md 5, PRD FR-11 and FR-18)
        page.grid(row=0, column=0, sticky="nsew")
        for name, button in self._nav_buttons.items():
            active = name == key
            button.configure(fg_color=theme.PRIMARY_LIGHT if active else "transparent")
            self._nav_bars[name].configure(fg_color=theme.BTN_TOP if active else "transparent")

    def offer_update(self, info: update_service.UpdateInfo) -> None:
        """Add an "Update available" button to the sidebar. It opens the download page in the browser."""
        if self._update_button is not None:
            return
        self._update_button = ctk.CTkButton(
            self.sidebar,
            text=f"Update to {info.version}",
            command=lambda: webbrowser.open(info.url),
            anchor="w",
            width=196,
            height=36,
            corner_radius=theme.BUTTON_RADIUS,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=widgets.text_font(theme.FONT_SIZE_BODY),
        )
        self.sidebar.add(self._update_button, 20, lambda h: h - 202, 36)
        self.show_toast(f"Version {info.version} is available.")

    def open_change_password(self) -> None:
        ChangePasswordPopup(self, self.auth, on_saved=lambda: self.show_toast("Password changed."))

    def show_toast(self, text: str) -> None:
        """Short success message in the bottom-right corner, gone after 3 seconds (Design.md 7)."""
        self.toast.configure(text=text)
        self.toast.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")
        if self._toast_job is not None:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(3000, self.toast.place_forget)


class ScrollablePage(ctk.CTkScrollableFrame):
    """Puts a long page in a frame that scrolls, and passes refresh() on to the page inside."""

    def __init__(self, master, build: Callable[[ctk.CTkFrame], ctk.CTkFrame]) -> None:
        super().__init__(master, fg_color=theme.BG_PAGE, corner_radius=0)
        self.inner = build(self)
        self.inner.pack(fill="both", expand=True)

    def refresh(self) -> None:
        self.inner.refresh()


class PlaceholderPage(ctk.CTkFrame):
    """Title and description only. The real forms and tables arrive in Phases 5 and 7.

    Real pages keep the same refresh() method. MainView calls it each time the page opens.
    """

    def __init__(self, master, title: str, description: str) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        widgets.label(self, title, size=theme.FONT_SIZE_PAGE_TITLE).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 0))
        widgets.label(self, description, color=theme.TEXT_MUTED).grid(row=1, column=0, sticky="w", padx=24, pady=(2, 18))

    def refresh(self) -> None:
        """Nothing to load yet."""
