"""The app window: the start-up routing, and the main frame with the sidebar (Design.md Section 2).

App decides which screen to show: create account, login, or the main frame.
MainView is the frame after login: a sidebar (Dashboard, Main Entry with one item per Main Entry,
Transaction List), a top bar with the page title and the user menu, and the page itself.
"""

import threading
import tkinter as tk
import webbrowser
from typing import Callable

import customtkinter as ctk

from app.core import config, models, paths, theme
from app.services.auth_service import AuthService
from app.services.entry_service import EntryService
from app.services.main_entry_service import MainEntryService
from app.services import update_service
from app.services.subhead_service import SubheadService
from app.storage.account_store import CorruptAccountFileError
from app.ui import widgets
from app.ui.expense_report_view import ExpenseReportView
from app.ui.dashboard_view import DashboardView
from app.ui.gradient import gradient_color
from app.ui.main_entry_view import MainEntryView
from app.ui.modify_fields_view import ModifyFieldsView
from app.ui.change_password_popup import ChangePasswordPopup
from app.ui.create_account_view import CreateAccountView
from app.ui.login_view import LoginView


class App(ctk.CTk):
    """The window. It shows one screen at a time."""

    def __init__(self, auth: AuthService, main_entries: MainEntryService, subheads: SubheadService, entries: EntryService) -> None:
        super().__init__()
        self.auth = auth
        self.main_entries = main_entries
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
        widgets.set_window_icon(self)
        try:
            self._icon = tk.PhotoImage(file=str(paths.asset_file("app-icon.png")))
            self.iconphoto(True, self._icon)  # the larger picture, for the taskbar and Alt+Tab
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
        view = MainView(self, self.auth, self.main_entries, self.subheads, self.entries, on_logout=self.show_login)
        self._show(view)
        if self.update_info is not None:
            view.offer_update(self.update_info)


class ShadowEdge(tk.Canvas):
    """A soft shadow down the right edge of the sidebar, so it stands out from the page."""

    WIDTH = 10

    def __init__(self, master) -> None:
        super().__init__(master, width=self.WIDTH, highlightthickness=0, bd=0, bg=theme.BG_PAGE)
        for x in range(self.WIDTH):
            self.create_line(x, 0, x, 5000, fill=gradient_color(theme.SIDE_SHADOW, theme.BG_PAGE, (x / (self.WIDTH - 1)) ** 0.6))


class MainView(ctk.CTkFrame):
    """Sidebar on the left; the top bar and the page on the right."""

    def __init__(self, master, auth: AuthService, main_entries: MainEntryService, subheads: SubheadService, entries: EntryService, on_logout: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.BG_PAGE)
        self.auth = auth
        self.main_entries = main_entries
        self.subheads = subheads
        self.entries = entries
        self.on_logout = on_logout
        self._toast_job = None
        self._nav_buttons: dict = {}
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._update_button = None
        self.current_page = "entry"
        self.current_main = models.DEFAULT_MAIN_HEAD

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, fg_color=theme.SIDE_TOP, corner_radius=0, width=theme.SIDEBAR_WIDTH)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        ShadowEdge(self).grid(row=0, column=1, sticky="ns")
        self._build_sidebar()

        self.content = ctk.CTkFrame(self, fg_color=theme.BG_PAGE, corner_radius=0)
        self.content.grid(row=0, column=2, sticky="nsew")
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self._build_top_bar()

        self.page_area = ctk.CTkFrame(self.content, fg_color=theme.BG_PAGE, corner_radius=0)
        self.page_area.grid(row=1, column=0, sticky="nsew")
        self.page_area.grid_rowconfigure(0, weight=1)
        self.page_area.grid_columnconfigure(0, weight=1)
        self._pages = {
            "dashboard": ScrollablePage(self.page_area, lambda parent: DashboardView(parent, self.main_entries, self.entries)),
            "entry": ScrollablePage(self.page_area, lambda parent: MainEntryView(parent, self.main_entries, self.subheads, self.entries, )),
            "modify": ScrollablePage(self.page_area, lambda parent: ModifyFieldsView(parent, self.main_entries, self.subheads, on_back=self._back_to_entry, on_entries_changed=self._entries_changed, notify=self.show_toast)),
            "report": ScrollablePage(self.page_area, lambda parent: ExpenseReportView(parent, self.main_entries, self.subheads, self.entries)),
        }
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
        self.show_entry(self._first_active_id(models.DEFAULT_MAIN_HEAD))

    # ----- sidebar -----

    def _build_sidebar(self) -> None:
        """Brand on top, the menu under it, and the version and author at the bottom."""
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=18, pady=(22, 18))
        ctk.CTkLabel(brand, text="DF", width=40, height=40, corner_radius=10, fg_color=theme.PRIMARY, text_color="#FFFFFF", font=widgets.text_font(16)).pack(side="left")
        ctk.CTkLabel(brand, text=config.APP_NAME, text_color=theme.TEXT, font=widgets.text_font(18)).pack(side="left", padx=(10, 0))

        self.bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.bottom.pack(side="bottom", fill="x", padx=18, pady=(0, 18))
        self.modify_button = self._nav_button(self.bottom, "Modify Fields", lambda: self.show_modify(self.current_main))
        self.modify_button.pack(fill="x", pady=(0, 12))
        self.version_label = ctk.CTkLabel(self.bottom, text=f"Version {config.APP_VERSION}", font=widgets.text_font(theme.FONT_SIZE_BODY, bold=False), text_color=theme.TEXT_MUTED, anchor="w")
        self.version_label.pack(fill="x")
        ctk.CTkLabel(self.bottom, text=f"Developed by {config.APP_AUTHOR}", font=widgets.text_font(theme.FONT_SIZE_LABEL, bold=False), text_color=theme.TEXT_MUTED, anchor="w").pack(fill="x")

        self.nav = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav.pack(fill="x", padx=12)
        self._build_nav()

    def _build_nav(self) -> None:
        """Dashboard, Main Entry with one item per active Main Entry, and Transaction List. Rebuilt when the Main Entries change."""
        for child in self.nav.winfo_children():
            child.destroy()
        self._nav_buttons = {}
        self._nav_buttons["dashboard"] = self._nav_button(self.nav, "Dashboard", self.show_dashboard)
        self._nav_buttons["dashboard"].pack(fill="x", pady=2)
        self._nav_buttons["entry"] = self._nav_button(self.nav, "Main Entry", lambda: self.show_entry(self.current_main))
        self._nav_buttons["entry"].pack(fill="x", pady=2)

        # CustomTkinter frames default to 200 px tall, so these are made 1 px tall and grow to fit their buttons.
        children = ctk.CTkFrame(self.nav, fg_color="transparent", height=1)
        children.pack(fill="x", padx=(14, 0), pady=(0, 2))
        ctk.CTkFrame(children, fg_color=theme.BORDER_SOFT, corner_radius=0, width=2, height=1).pack(side="left", fill="y")
        column = ctk.CTkFrame(children, fg_color="transparent", height=1)
        column.pack(side="left", fill="x", expand=True, padx=(10, 0))
        for item in self.main_entries.active():
            button = self._nav_button(column, item.name, lambda main_head=item.id: self.show_entry(main_head))
            button.pack(fill="x", pady=2)
            self._nav_buttons[("entry", item.id)] = button

        self._nav_buttons["report"] = self._nav_button(self.nav, "Transaction List", self.show_report)
        self._nav_buttons["report"].pack(fill="x", pady=(10, 2))
        self._highlight()

    def _nav_button(self, parent, text: str, command) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            anchor="w",
            height=40,
            corner_radius=theme.BUTTON_RADIUS,
            fg_color="transparent",
            hover_color=theme.SIDE_HOVER,
            text_color=theme.SIDEBAR_TEXT,
            font=widgets.text_font(theme.FONT_SIZE_BODY),
        )

    def _highlight(self) -> None:
        """Mark the open page: a pale pill for Dashboard, Main Entry, and Transaction List; a solid pill for the open Main Entry."""
        in_entry = self.current_page in ("entry", "modify")
        modifying = self.current_page == "modify"
        self.modify_button.configure(fg_color=theme.PRIMARY_LIGHT if modifying else "transparent", text_color=theme.PRIMARY if modifying else theme.SIDEBAR_TEXT)
        for key, button in self._nav_buttons.items():
            if isinstance(key, tuple):
                solid = in_entry and key[1] == self.current_main
                button.configure(fg_color=theme.PRIMARY if solid else "transparent", hover_color=theme.PRIMARY_HOVER if solid else theme.SIDE_HOVER, text_color="#FFFFFF" if solid else theme.SIDEBAR_TEXT)
            else:
                active = (key == "entry" and in_entry) or key == self.current_page
                button.configure(fg_color=theme.PRIMARY_LIGHT if active else "transparent", text_color=theme.PRIMARY if active else theme.SIDEBAR_TEXT)

    # ----- top bar -----

    def _build_top_bar(self) -> None:
        bar = ctk.CTkFrame(self.content, fg_color="transparent", height=64)
        bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(8, 0))
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(bar, text="", font=widgets.text_font(theme.FONT_SIZE_CARD_TITLE), text_color=theme.TEXT, anchor="w")
        self.title_label.grid(row=0, column=0, sticky="w")
        bar.grid_rowconfigure(0, weight=1)
        self.user_button = ctk.CTkButton(
            bar, text=theme.ICON_USER, font=widgets.icon_font(15), width=40, height=40, corner_radius=20,
            fg_color=theme.BG_CARD, hover_color=theme.PRIMARY_LIGHT, border_color=theme.BORDER_SOFT, border_width=1,
            text_color=theme.PRIMARY, command=self._open_user_menu,
        )
        self.user_button.grid(row=0, column=1, sticky="e")

    def _open_user_menu(self) -> None:
        menu = tk.Menu(self, tearoff=0, font=(theme.FONT_FAMILY, 11))
        menu.add_command(label="Change Password", command=self.open_change_password)
        menu.add_separator()
        menu.add_command(label="Logout", command=self.on_logout)
        try:
            menu.tk_popup(self.user_button.winfo_rootx() - 90, self.user_button.winfo_rooty() + self.user_button.winfo_height() + 4)
        finally:
            menu.grab_release()

    # ----- pages -----

    def _first_active_id(self, preferred: str) -> str:
        active = [item.id for item in self.main_entries.active()]
        return preferred if preferred in active else (active[0] if active else preferred)

    def _open(self, key: str, title: str) -> None:
        """Show one page and highlight its menu item (FR-7)."""
        self.current_page = key
        for page in self._pages.values():
            page.grid_forget()
        page = self._pages[key]
        page.refresh()  # every page reloads its data when it opens (Design.md 5, PRD FR-11 and FR-18)
        page.grid(row=0, column=0, sticky="nsew")
        self.title_label.configure(text=title)
        self._highlight()

    def show_dashboard(self) -> None:
        self._open("dashboard", "Dashboard")

    def show_entry(self, main_head: str) -> None:
        self.current_main = self._first_active_id(main_head)
        self._pages["entry"].inner.show(self.current_main)
        self._open("entry", f"Main Entry · {self.main_entries.label(self.current_main)}")

    def show_modify(self, main_head: str) -> None:
        self.current_main = self._first_active_id(main_head)
        self._pages["modify"].inner.show(self.current_main)
        self._open("modify", f"Modify Fields · {self.main_entries.label(self.current_main)}")

    def show_report(self) -> None:
        self._open("report", "Transaction List")

    def _back_to_entry(self) -> None:
        self.show_entry(self._pages["modify"].inner.main_head)

    def _entries_changed(self) -> None:
        """The Main Entries changed on the Modify Fields page: redraw the sidebar."""
        self.current_main = self._first_active_id(self.current_main)
        self._build_nav()

    # ----- update, password, toast -----

    def offer_update(self, info: update_service.UpdateInfo) -> None:
        """Add an "Update available" button to the sidebar. It opens the download page in the browser."""
        if self._update_button is not None:
            return
        self._update_button = ctk.CTkButton(
            self.bottom,
            text=f"Update to {info.version}",
            command=lambda: webbrowser.open(info.url),
            height=36,
            corner_radius=theme.BUTTON_RADIUS,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=widgets.text_font(theme.FONT_SIZE_BODY),
        )
        self._update_button.pack(fill="x", pady=(0, 12), before=self.modify_button)
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
    """Puts a page in a frame that scrolls, and passes refresh() on to the page inside (self.inner)."""

    def __init__(self, master, build: Callable[[ctk.CTkFrame], ctk.CTkFrame]) -> None:
        super().__init__(master, fg_color=theme.BG_PAGE, corner_radius=0)
        self.inner = build(self)
        self.inner.pack(fill="both", expand=True)

    def refresh(self) -> None:
        self.inner.refresh()
