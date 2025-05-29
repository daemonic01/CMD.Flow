import curses
from ui.views.base_view import BaseView
from ui.views.popup_confirm import PopupConfirmView
from utils.localization import t
from ui.common.footer import FooterController
from utils.layout import update_screen_size, compute_layout
from ui.common.main_menu import draw_main_menu
from ui.common.main_logo_utils import draw_logo
from ui.common.render_box import render_boxed
from ui.modules.main_menu_info_box import draw_menu_info_box
from ui.modules.project_cards import *
from ui.views.window_size_error import draw_window_size_error
from ui.views.new_entry_form import NewEntryFormView
from ui.modules.changelog_panel import draw_changelog_panel
import json
from ui.modules.header import draw_header
from utils.figlet import generate_figlet
from utils.hierarchy import draw_hierarchy_panel




class ProjectView(BaseView):
    def __init__(self, ctx, project):
        super().__init__(ctx)
        self.ctx.layout.middle_split = [0.5, 0.5]
        self.project = project
        self.project_title_figlet = generate_figlet(self.project.title)
        

        self.footer = FooterController()
        self.footer.add_action(t("footer.actions.exit"), "q", lambda: PopupConfirmView(
                    self.ctx, message=t("footer.messages.exit_confirm"),
                    on_accept=lambda: "exit", on_cancel=lambda: "pop"
                ))
        self.footer.add_action(t("footer.actions.back"), "q", lambda: PopupConfirmView(
                    self.ctx,
                    message=t("footer.messages.back"),
                    on_accept= lambda: "back",
                    on_cancel=lambda: "pop"
                ))



    def render(self, stdscr):
        update_screen_size(self.ctx)
        self.layout = compute_layout(self.ctx)
        if self.ctx.control.layout_blocked:
            draw_window_size_error(stdscr)
            return
        

        self.ctx.control.mode = "project_view"
        self.ctx.ui.footer = self.footer
        stdscr.refresh()

        

        render_boxed(self.layout["header"], draw_content_fn= lambda w: draw_header(w, self.project_title_figlet, self.project.title))
        render_boxed(
            self.layout["middle"][0],
            draw_content_fn=lambda w: draw_hierarchy_panel(w, self.project),
            title="Projektstruktúra"
        )
        render_boxed(self.layout["middle"][1])
        render_boxed(self.layout["footer"], lambda w: self.footer.draw(w, self.ctx))







    def handle_input(self, key):
        """
        Handle user input based on the current focus mode.

        Routes key events to different input handlers depending on the UI focus:
        - 'footer': navigates and handles footer-specific commands
        """
        if self.ctx.control.focus == "footer":
            return self.footer.handle_navigation(key, self.layout["footer"], self.ctx)

        if key == curses.KEY_UP:
            self.selected_idx = (self.selected_idx - 1) % len(self.menu_items)
        elif key == curses.KEY_DOWN:
            self.selected_idx = (self.selected_idx + 1) % len(self.menu_items)
        elif key in (10, 13, "\n"):  # ENTER
            pass
        elif key in (9, '\t'):
            self.ctx.control.focus = "footer"