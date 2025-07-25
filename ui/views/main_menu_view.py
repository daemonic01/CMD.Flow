import curses, json
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
from ui.views.project_view import ProjectView




class MainMenuView(BaseView):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.last_focus = ctx.control.last_focus
        self.ctx.control.focus = "menu"
        self.selected_idx = 0
        self.card_idx = 0
        self.scroll_offset = 0
        self.changelog_scroll = 0
        self.changelog_lines = self.build_changelog_lines()
        self.menu_items = [
            t("menu.options.projects"),
            t("menu.options.new_project"),
            t("menu.options.demodata"),
            t("menu.options.changelog"),
            t("menu.options.exit")
        ]
        # FooterController handles footer actions and input hints shown at the bottom of the UI
        self.footer_updated = False
        self.footer = FooterController()
        self.footer.add_action(t("footer.actions.exit"), "q", lambda: PopupConfirmView(
                    self.ctx,
                    message=t("footer.messages.exit_confirm"),
                    on_accept=lambda: "exit",
                    on_cancel=lambda: "pop"
                ))
        


    def render(self, stdscr):
        update_screen_size(self.ctx)
        if self.ctx.control.layout_blocked:
            draw_window_size_error(stdscr)
            return


        self.ctx.control.mode = "menu"
        self.ctx.ui.footer = self.footer
        stdscr.refresh()

        # Middle area layout: [main menu width, project cards width, calendar panel width]
        self.ctx.layout.middle_split = [0.3, 0.4, 0.3]
        self.layout = compute_layout(self.ctx)

        render_boxed(self.layout["header"], draw_content_fn=lambda w: draw_logo(w, self.ctx))
        render_boxed(self.layout["middle"][0], draw_content_fn=lambda w: draw_main_menu(w, self.menu_items, self.selected_idx), title=t("menu.title"),
                     border_chars= self.ctx.layout.selected_panel_border if self.ctx.control.focus == "menu" else None)
        
        if self.ctx.control.focus == "cards":
            render_boxed(
                self.layout["middle"][1],
                draw_content_fn=lambda w: draw_project_cards_panel(w, self.ctx, self.card_idx, self.scroll_offset),
                title=t("menu.cards_title"),
                border_chars=["|", "|", "-", "-", "+", "+", "+", "+"]
            )


        if (self.ctx.control.focus == "cards" and not self.footer_updated):

            self.footer.add_action_once("Törlés", "d", lambda: PopupConfirmView(
            self.ctx,
            message="Törlöd a kiválasztott projektet?",
            on_accept=lambda: self.delete_selected_project(),
            on_cancel=lambda: "pop"
        ))
            self.footer.add_action_once("Szerkesztés", "e", self.open_edit_form)

            self.footer_updated = True

        elif self.ctx.control.focus not in ("cards", "footer") and self.footer_updated:
            self.footer.actions = [a for a in self.footer.actions if a["key"] not in ("d", "e")]
            self.footer_updated = False



        elif self.ctx.control.focus == "changelog":
            render_boxed(
                self.layout["middle"][1],
                draw_content_fn=lambda w: draw_changelog_panel(w, self.ctx, self.changelog_lines, self.changelog_scroll),
                title=t("menu.changelog_title"),
                border_chars=["|", "|", "-", "-", "+", "+", "+", "+"]
            )

        elif self.ctx.control.focus == "main":
            render_boxed(
                self.layout["middle"][1], border= False
            )

        render_boxed(self.layout["middle"][2], draw_content_fn=lambda w: draw_menu_info_box(w, self.ctx), title=t("menu.main_menu_info_box_title"))
        render_boxed(self.layout["footer"], lambda w: self.footer.draw(w, self.ctx),
            border_chars= self.ctx.layout.selected_panel_border if self.ctx.control.focus == "footer" else None)


    def handle_input(self, key):
        """
        Handle user input based on the current focus mode.

        Routes key events to different input handlers depending on the UI focus:
        - 'footer': navigates and handles footer-specific commands
        - 'cards': handles scrollable card list interaction
        - main: controls the main menu navigation
        """
        if self.ctx.control.focus == "footer":
            return self.footer.handle_navigation(key, self.layout["footer"], self.ctx)
        elif self.ctx.control.focus == "cards":
            return self.handle_card_input(key)
        elif self.ctx.control.focus == "changelog":
            return self.handle_changelog_input(key)

        if key == curses.KEY_UP:
            self.selected_idx = (self.selected_idx - 1) % len(self.menu_items)
        elif key == curses.KEY_DOWN:
            self.selected_idx = (self.selected_idx + 1) % len(self.menu_items)


        elif key in (10, 13, "\n"):
            if self.selected_idx == 0:
                self.ctx.control.focus = "cards"
            elif self.selected_idx == 1:
                return NewEntryFormView(self.ctx, level="project")
            elif self.selected_idx == 2:
                create_demo_data(self.ctx)
            elif self.selected_idx == 3:
                self.ctx.control.focus = "changelog"
            elif self.selected_idx == 4:
                return PopupConfirmView(
                    self.ctx,
                    message=t("footer.messages.exit_confirm"),
                    on_accept=lambda: exit(),
                    on_cancel=lambda: "pop"
                )
        if key in (9, '\t'):
            self.ctx.control.last_focus = self.ctx.control.focus
            self.ctx.control.focus = "footer"


    def handle_card_input(self, key):
        """
        Handles navigation and selection logic for the scrollable project card list.

        The function ensures that scrolling stays in sync with the selected index.
        - 'card_idx' represents the currently selected project's global index.
        - 'scroll_offset' is adjusted when selection moves beyond the visible range.
        - Only the visible slice of projects is rendered based on 'scroll_offset'.
        """
        projects = self.ctx.data.get("projects", [])
        total = len(projects)

        rows, cols = self.layout["middle"][1].getmaxyx()
        card_height = self.ctx.layout.project_card_height
        spacing = self.ctx.layout.project_cards_spacing
        visible = max(rows // (card_height + spacing), 1)

        if key == curses.KEY_UP:
            if self.card_idx > 0:
                self.card_idx -= 1
                if self.card_idx < self.scroll_offset:
                    self.scroll_offset = self.card_idx

        elif key == curses.KEY_DOWN:
            if self.card_idx < total - 1:
                self.card_idx += 1
                if self.card_idx >= self.scroll_offset + visible:
                    self.scroll_offset = max(0, self.card_idx - visible + 1)

        elif key in (10, 13, "\n"):
            return ProjectView(ctx = self.ctx, project=projects[self.card_idx])
        
        elif key in (46, curses.KEY_DC):
            projects = self.ctx.data["projects"]
            if 0 <= self.card_idx < len(projects):
                title = projects[self.card_idx].title
                return PopupConfirmView(
                    self.ctx,
                    message=f"Törlöd a(z) „{title}” projektet?",
                    on_accept=lambda: self.delete_selected_project(),
                    on_cancel=lambda: "pop"
                )
        elif key in (9, '\t'):
            self.ctx.control.last_focus = self.ctx.control.focus
            self.ctx.control.focus = "footer"
        elif key == '' or key == 27:
            self.layout["middle"][1].erase()
            self.ctx.control.focus = "main"


    

    def build_changelog_lines(self):
        try:
            with open("changelog.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"Hiba": {"changes": ["A changelog.json fájl nem található."]}}

        versions = list(data.keys())
        lines = []
        for v in versions:
            ver_data = data[v]
            date = ver_data.get("date", "ismeretlen dátum")
            lines.append(("header", f"{v} – {date}"))
            for change in ver_data.get("changes", []):
                lines.append(("item", f"  • {change}"))
            lines.append(("", ""))
        return lines
        


    def handle_changelog_input(self, key):
        total_lines = len(self.changelog_lines)
        max_visible = self.layout["middle"][1].getmaxyx()[0] - 4

        if key == curses.KEY_UP and self.changelog_scroll > 0:
            self.changelog_scroll -= 1
        elif key == curses.KEY_DOWN and self.changelog_scroll + max_visible < total_lines:
            self.changelog_scroll += 1
        elif key in (27, ''):
            self.ctx.control.focus = "main"


    def delete_selected_project(self):
        projects = self.ctx.data["projects"]
        if 0 <= self.card_idx < len(projects):
            projects.pop(self.card_idx)
            from utils.data_io import save_projects_to_file
            save_projects_to_file(projects)
            self.card_idx = max(0, self.card_idx - 1)

        visible = max(1, self.layout["middle"][1].getmaxyx()[0] // (self.ctx.layout.project_card_height + self.ctx.layout.project_cards_spacing))
        self.scroll_offset = max(0, self.card_idx - visible + 1)
        self.ctx.control.focus = "cards"
        return "pop"


    def open_edit_form(self):
        projects = self.ctx.data["projects"]
        if not (0 <= self.card_idx < len(projects)):
            return "pop"

        project = projects[self.card_idx]
        values = [
            project.title,
            project.full_desc or "",
            project.deadline or "",
            project.priority or ""
        ]


        return NewEntryFormView(
            ctx=self.ctx,
            level="project",
            initial_values=values,
            edit_target=project
        )


def create_demo_data(ctx):
    from utils.demodata import generate_demo_data
    from utils.data_io import save_projects_to_file

    ctx.data["projects"] = generate_demo_data()
    save_projects_to_file(ctx.data["projects"])

