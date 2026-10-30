"""The app window: the start-up routing, and the main frame with the top navbar (Design.md Section 2).

App decides which screen to show: create account, login, or the main frame.
MainView is the frame after login: a fixed top navbar (Dashboard, Main Entry, Transaction List, Modify Fields, the user
menu), a second bar with one chip per Main Entry on the Main Entry page, and the page itself.
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
from app.ui.gradient import GradientBar
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


class MainHeadBar(tk.Frame):
    """The second bar: one chip per Main Entry. It scrolls sideways (mouse wheel, or the arrows) with no scrollbar."""

    def __init__(self, master, on_pick: Callable[[str], None]) -> None:
        super().__init__(master, bg=theme.BG_CARD, highlightthickness=0, bd=0)
        self.on_pick = on_pick
        self._chips: dict[str, ctk.CTkButton] = {}
        scale = ctk.ScalingTracker.get_widget_scaling(self)
        self.grid_columnconfigure(1, weight=1)
        self.left = self._arrow("‹", -1)
        self.right = self._arrow("›", 1)
        self.canvas = tk.Canvas(self, height=round(theme.HEADS_BAR_HEIGHT * scale), bg=theme.BG_CARD, highlightthickness=0, bd=0, xscrollincrement=round(60 * scale))
        self.canvas.grid(row=0, column=1, sticky="ew")
        self.inner = tk.Frame(self.canvas, bg=theme.BG_CARD, highlightthickness=0, bd=0)
        self.canvas.create_window(0, round(theme.HEADS_BAR_HEIGHT * scale / 2), window=self.inner, anchor="w")
        self.inner.bind("<Configure>", lambda _event: self._update_arrows())
        self.canvas.bind("<Configure>", lambda _event: self._update_arrows())
        for widget in (self.canvas, self.inner):
            widget.bind("<MouseWheel>", self._wheel)

    def _arrow(self, text: str, direction: int) -> ctk.CTkButton:
        return ctk.CTkButton(
            self, text=text, width=34, height=34, corner_radius=17, fg_color=theme.SURFACE_SOFT, hover_color=theme.SIDE_HOVER,
            text_color=theme.TEXT, font=widgets.text_font(18), bg_color=theme.BG_CARD, command=lambda: self._scroll(direction),
        )

    def set_items(self, items: list[tuple[str, str]], active: str) -> None:
        """Draw one chip for each (id, name). The active one is filled."""
        for chip in self._chips.values():
            chip.destroy()
        self._chips = {}
        for item_id, name in items:
            chip = ctk.CTkButton(
                self.inner, text=name, height=34, corner_radius=17, border_width=1, bg_color=theme.BG_CARD,
                font=widgets.text_font(theme.FONT_SIZE_BODY), command=lambda main_head=item_id: self.on_pick(main_head),
            )
            chip.pack(side="left", padx=4)
            chip.bind("<MouseWheel>", self._wheel, add="+")
            self._chips[item_id] = chip
        self.update_idletasks()
        self._update_arrows()
        self.set_active(active)

    def set_active(self, active: str) -> None:
        for item_id, chip in self._chips.items():
            on = item_id == active
            chip.configure(
                fg_color=theme.HIGHLIGHT if on else theme.SURFACE_SOFT, hover_color=theme.HIGHLIGHT_HOVER if on else theme.SIDE_HOVER,
                text_color=theme.ON_HIGHLIGHT if on else theme.TEXT, border_color=theme.HIGHLIGHT if on else theme.INPUT_BORDER,
            )
        if active in self._chips:
            self.after_idle(lambda: self._reveal(self._chips.get(active)))

    def _needs_scroll(self) -> bool:
        return self.inner.winfo_reqwidth() > self.canvas.winfo_width() + 1

    def _update_arrows(self) -> None:
        self.canvas.configure(scrollregion=(0, 0, self.inner.winfo_reqwidth(), self.canvas.winfo_height()))
        if self._needs_scroll():
            self.left.grid(row=0, column=0, padx=(12, 4))
            self.right.grid(row=0, column=2, padx=(4, 12))
        else:
            self.left.grid_remove()
            self.right.grid_remove()
            self.canvas.xview_moveto(0)

    def _scroll(self, direction: int) -> None:
        self.canvas.xview_scroll(direction * 3, "units")

    def _wheel(self, event) -> None:
        if self._needs_scroll():
            self.canvas.xview_scroll(-3 if event.delta > 0 else 3, "units")

    def _reveal(self, chip: ctk.CTkButton | None) -> None:
        """Scroll so the chip is fully in view."""
        if chip is None or not self._needs_scroll() or not chip.winfo_exists():
            return
        total = max(1, self.inner.winfo_reqwidth())
        left, width = self.canvas.canvasx(0), self.canvas.winfo_width()
        start, end = chip.winfo_x(), chip.winfo_x() + chip.winfo_width()
        if start < left:
            self.canvas.xview_moveto(max(0, start - 8) / total)
        elif end > left + width:
            self.canvas.xview_moveto((end - width + 8) / total)


class MainView(ctk.CTkFrame):
    """A fixed top navbar, a second bar with the Main Entries (on the Main Entry page), and the page under them."""

    def __init__(self, master, auth: AuthService, main_entries: MainEntryService, subheads: SubheadService, entries: EntryService, on_logout: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.BG_PAGE)
        self.auth = auth
        self.main_entries = main_entries
        self.subheads = subheads
        self.entries = entries
        self.on_logout = on_logout
        self._toast_job = None
        self._tabs: dict[str, ctk.CTkButton] = {}
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._update_button = None
        self.current_page = "entry"
        self.current_main = models.DEFAULT_MAIN_HEAD

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_nav_bar()

        # Under the navbar: the Main Entries, for the Main Entry page only.
        self.heads_holder = tk.Frame(self, bg=theme.BG_CARD, highlightthickness=0, bd=0)
        self.heads_holder.grid(row=1, column=0, sticky="ew")
        self.heads_bar = MainHeadBar(self.heads_holder, on_pick=lambda main_head: self.show_entry(main_head))
        self.heads_bar.pack(fill="x")
        tk.Frame(self.heads_holder, bg=theme.BORDER_SOFT, height=1, highlightthickness=0, bd=0).pack(fill="x")

        self.page_area = ctk.CTkFrame(self, fg_color=theme.BG_PAGE, corner_radius=0)
        self.page_area.grid(row=2, column=0, sticky="nsew")
        self.page_area.grid_rowconfigure(0, weight=1)
        self.page_area.grid_columnconfigure(0, weight=1)
        self._pages = {
            "dashboard": ScrollablePage(self.page_area, lambda parent: DashboardView(parent, self.main_entries, self.entries)),
            "entry": ScrollablePage(self.page_area, lambda parent: MainEntryView(parent, self.main_entries, self.subheads, self.entries, notify=self.show_toast)),
            "modify": ScrollablePage(self.page_area, lambda parent: ModifyFieldsView(parent, self.main_entries, self.subheads, on_back=self._back_to_entry, on_entries_changed=self._entries_changed, notify=self.show_toast)),
            "report": ScrollablePage(self.page_area, lambda parent: ExpenseReportView(parent, self.main_entries, self.subheads, self.entries, notify=self.show_toast)),
        }
        self.toast = ctk.CTkLabel(
            self,
            text="",
            fg_color=theme.SUCCESS_BG,
            text_color=theme.CREDIT,
            corner_radius=theme.BUTTON_RADIUS,
            font=widgets.text_font(theme.FONT_SIZE_BODY),
            padx=16,
            pady=10,
        )
        self._build_heads()
        self.show_entry(self._first_active_id(models.DEFAULT_MAIN_HEAD))

    # ----- navbar -----

    def _build_nav_bar(self) -> None:
        """The fixed bar at the top: brand and the three pages on the left; Modify Fields and the user menu on the right."""
        self.nav_bar = GradientBar(self, (theme.NAV_START, theme.NAV_MIDDLE, theme.NAV_END), theme.NAV_HEIGHT)
        self.nav_bar.grid(row=0, column=0, sticky="ew")
        self.nav_bar.add(ctk.CTkLabel(self.nav_bar, text="DF", width=40, height=40, corner_radius=20, fg_color=theme.HIGHLIGHT, text_color=theme.ON_HIGHLIGHT, font=widgets.text_font(15)), before=24)
        self.nav_bar.add(ctk.CTkLabel(self.nav_bar, text=config.APP_NAME, text_color=theme.TEXT, font=widgets.text_font(18)), before=10, after=18)
        for key, text, command in (
            ("dashboard", "Dashboard", self.show_dashboard),
            ("entry", "Main Entry", lambda: self.show_entry(self.current_main)),
            ("report", "Transaction List", self.show_report),
        ):
            tab = ctk.CTkButton(self.nav_bar, text=text, command=command, height=38, corner_radius=19, fg_color="transparent", font=widgets.text_font(theme.FONT_SIZE_BODY))
            self._tabs[key] = tab
            self.nav_bar.add(tab, before=2, after=2)

        self.user_button = ctk.CTkButton(
            self.nav_bar, text=theme.ICON_USER, font=widgets.icon_font(15), width=40, height=40, corner_radius=20,
            fg_color=theme.HIGHLIGHT, hover_color=theme.HIGHLIGHT_HOVER, border_width=0,
            text_color=theme.ON_HIGHLIGHT, command=self._open_user_menu,
        )
        self.nav_bar.add(self.user_button, side="right", before=22)
        self.modify_button = widgets.secondary_button(self.nav_bar, "Modify Fields", lambda: self.show_modify(self.current_main), width=140)
        self.nav_bar.add(self.modify_button, side="right", before=12, after=0)

    def _build_heads(self) -> None:
        """One chip for each active Main Entry. Built again when the Main Entries change."""
        self.heads_bar.set_items([(item.id, item.name) for item in self.main_entries.active()], self.current_main)

    def _highlight(self) -> None:
        """Mark the open page in the navbar; Modify Fields counts as part of Main Entry."""
        open_tab = "entry" if self.current_page in ("entry", "modify") else self.current_page
        for key, tab in self._tabs.items():
            on = key == open_tab
            tab.configure(
                fg_color=theme.HIGHLIGHT if on else "transparent", hover_color=theme.HIGHLIGHT_HOVER if on else theme.SIDE_HOVER,
                text_color=theme.ON_HIGHLIGHT if on else theme.TEXT,
            )
        modifying = self.current_page == "modify"
        self.modify_button.configure(
            fg_color=theme.HIGHLIGHT if modifying else "transparent", hover_color=theme.HIGHLIGHT_HOVER if modifying else theme.PRIMARY_LIGHT,
            text_color=theme.ON_HIGHLIGHT if modifying else theme.INK,
        )
        if self.current_page == "entry":
            self.heads_holder.grid()
            self.heads_bar.set_active(self.current_main)
        else:
            self.heads_holder.grid_remove()

    def _open_user_menu(self) -> None:
        menu = tk.Menu(
            self, tearoff=0, font=(theme.FONT_FAMILY, 11), bg=theme.BG_CARD, fg=theme.TEXT, activebackground=theme.SIDE_ACTIVE,
            activeforeground=theme.TEXT, disabledforeground=theme.TEXT_MUTED, bd=0,
        )
        menu.add_command(label="Change Password", command=self.open_change_password)
        menu.add_command(label="Logout", command=self.on_logout)
        menu.add_separator()
        menu.add_command(label=f"Version {config.APP_VERSION}", state="disabled")
        menu.add_command(label=f"Developed by {config.APP_AUTHOR}", state="disabled")
        try:
            menu.tk_popup(self.user_button.winfo_rootx() - 150, self.user_button.winfo_rooty() + self.user_button.winfo_height() + 4)
        finally:
            menu.grab_release()

    # ----- pages -----

    def _first_active_id(self, preferred: str) -> str:
        active = [item.id for item in self.main_entries.active()]
        return preferred if preferred in active else (active[0] if active else preferred)

    def _open(self, key: str) -> None:
        """Show one page and highlight its menu item (FR-7)."""
        self.current_page = key
        for page in self._pages.values():
            page.grid_forget()
        page = self._pages[key]
        page.refresh()  # every page reloads its data when it opens (Design.md 5, PRD FR-11 and FR-18)
        page.grid(row=0, column=0, sticky="nsew")
        self._highlight()

    def show_dashboard(self) -> None:
        self._open("dashboard")

    def show_entry(self, main_head: str) -> None:
        self.current_main = self._first_active_id(main_head)
        self._pages["entry"].inner.show(self.current_main)
        self._open("entry")

    def show_modify(self, main_head: str) -> None:
        self.current_main = self._first_active_id(main_head)
        self._pages["modify"].inner.show(self.current_main)
        self._open("modify")

    def show_report(self) -> None:
        self._open("report")

    def _back_to_entry(self) -> None:
        self.show_entry(self._pages["modify"].inner.main_head)

    def _entries_changed(self) -> None:
        """The Main Entries changed on the Modify Fields page: draw the Main Entry bar again."""
        self.current_main = self._first_active_id(self.current_main)
        self._build_heads()

    # ----- update, password, toast -----

    def offer_update(self, info: update_service.UpdateInfo) -> None:
        """Add an "Update available" button to the navbar. It opens the download page in the browser."""
        if self._update_button is not None:
            return
        self._update_button = ctk.CTkButton(
            self.nav_bar,
            text=f"Update to {info.version}",
            command=lambda: webbrowser.open(info.url),
            height=36,
            corner_radius=theme.BUTTON_RADIUS,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color=theme.ON_PRIMARY,
            font=widgets.text_font(theme.FONT_SIZE_BODY),
        )
        self.nav_bar.add(self._update_button, side="right", before=12)
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
        super().__init__(master, fg_color=theme.BG_PAGE, corner_radius=0, scrollbar_button_color=theme.INPUT_BORDER, scrollbar_button_hover_color=theme.DROPDOWN_BORDER)
        self.inner = build(self)
        self.inner.pack(fill="both", expand=True)

    def refresh(self) -> None:
        self.inner.refresh()
