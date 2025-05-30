import curses, textwrap
from ui.views.base_view import BaseView
from ui.views.popup_confirm import PopupConfirmView
from utils.localization import t
from ui.common.footer import FooterController
from utils.layout import update_screen_size, compute_layout
from ui.common.render_box import render_boxed
from ui.modules.project_cards import *
from ui.views.window_size_error import draw_window_size_error
from ui.modules.project_header import draw_header
from utils.figlet import generate_figlet
from utils.hierarchy import flatten_project_hierarchy, get_children

from utils.logger import log





class ProjectView(BaseView):
    def __init__(self, ctx, project):
        super().__init__(ctx)
        self.ctx.layout.middle_split = [0.25, 0.75]
        self.project = project
        self.project_title_figlet = generate_figlet(self.project.title)
        self.selected_idx = 0
        self.scroll_offset = 0
        self.items = []
        self.ctx.control.focus = "explorer" 
        

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
        
        self.items = flatten_project_hierarchy(self.project)
        self.ctx.control.mode = "project_view"
        self.ctx.ui.footer = self.footer
        stdscr.refresh()

        
        render_boxed(self.layout["header"], draw_content_fn= lambda w: draw_header(w, self.project_title_figlet, self.project.title))


        render_boxed(
            self.layout["middle"][0],
            draw_content_fn=self.draw_explorer_panel,
            title="Projektstruktúra"
        )


        render_boxed(
            self.layout["middle"][1],
            draw_content_fn=self.draw_details_panel,
            title="Részletek"
        )


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
            if self.selected_idx > 0:
                self.selected_idx -= 1
                if self.selected_idx < self.scroll_offset:
                    self.scroll_offset = self.selected_idx

        elif key == curses.KEY_DOWN:
            if self.selected_idx < len(self.items) - 1:
                self.selected_idx += 1
                max_visible = self.layout["middle"][0].getmaxyx()[0] - 2  # header + bottom padding
                if self.selected_idx >= self.scroll_offset + max_visible:
                    self.scroll_offset = max(0, self.selected_idx - max_visible + 1)
        elif key in (10, 13, "\n"):
            pass
        elif key in (9, '\t'):
            self.ctx.control.focus = "footer"


    def draw_explorer_panel(self, win):
        max_rows, max_cols = win.getmaxyx()
        start_y = 1
        start_x = 2
        indent = 2

        curses.init_color(241, 765, 408, 51)
        curses.init_color(242, 351, 552, 600)
        curses.init_color(243, 663, 681, 438)
        curses.init_color(244, 753, 660, 678)

        curses.init_pair(1, 241, curses.COLOR_BLACK)
        curses.init_pair(2, 242, curses.COLOR_BLACK)
        curses.init_pair(3, 243, curses.COLOR_BLACK)
        curses.init_pair(4, 244, curses.COLOR_BLACK)

        def get_color_for_depth(depth):
            return {
                0: curses.color_pair(1),
                1: curses.color_pair(2),
                2: curses.color_pair(3)
            }.get(depth, curses.color_pair(4))


        visible_rows = max_rows - start_y - 1
        visible_items = self.items[self.scroll_offset:self.scroll_offset + visible_rows]

        for i, (obj, depth) in enumerate(visible_items):
            row = start_y + i
            if row >= max_rows - 1:
                break

            prefix = " " * (depth * indent)
            is_last = (self.scroll_offset + i == len(self.items) - 1)
            connector = "┗━" if is_last else "┣━"

            title = obj.title.upper() if hasattr(obj, "tasks") else obj.title
            line = f"{prefix}{connector} {title}"
            color = get_color_for_depth(depth)

            try:
                if self.scroll_offset + i == self.selected_idx:
                    win.addstr(row, start_x, line[:max_cols - start_x - 1], color | curses.A_REVERSE)
                else:
                    win.addstr(row, start_x, line[:max_cols - start_x - 1], color)
            except curses.error:
                pass

        win.refresh()


    def draw_details_panel(self, win):
        self.ctx.control.focus = "project_details"
        max_y, max_x = win.getmaxyx()
        pad_x = 2
        row = 1

        selected = self.items[self.selected_idx][0]  # kiválasztott objektum

        # Fejléc — név
        try:
            win.addstr(row, pad_x, f"Név: {selected.title}", curses.A_BOLD)
            row += 2
        except curses.error:
            pass

        # Leírás
        if getattr(selected, "full_desc", ""):
            desc = selected.full_desc.strip()
            wrapped = textwrap.wrap(desc, max_x - pad_x * 2)
            win.addstr(row, pad_x, "Leírás:")
            row += 1
            for line in wrapped:
                if row >= max_y - 2: break
                win.addstr(row, pad_x + 2, line)
                row += 1
            row += 1

        # Határidő
        if getattr(selected, "deadline", ""):
            win.addstr(row, pad_x, f"Határidő: {selected.deadline}")
            row += 3

        # Alárendelt elemek — ha vannak
        children = get_children(selected)
        if children:
            row += 1

            for child in children:
                if row >= max_y - 1: break
                status = ""
                if hasattr(child, "done"):
                    status = "  [x]  " if child.done else "  [ ]  "
                    tab_header = "| Státusz |        Név        |  Határidő  | Leírás                                   |"
                    win.addstr(row, pad_x, f"| {status} | {child.title.ljust(17)} | {child.deadline} | {child.full_desc[:40]} |")
                else:
                    tab_header = "|        Név        |  Határidő  | Leírás                                   |"
                    win.addstr(row, pad_x, f"| {child.title.ljust(17)} | {child.deadline} | {child.full_desc[:40]} |")

                try:
                    row += 1
                except curses.error:
                    pass
            
            win.addstr(row-(len(children)+2), pad_x, tab_header, curses.A_UNDERLINE)
            sep_line = "|"+"-"*(len(tab_header)-2)+"|"
            win.addstr(row-(len(children)+1), pad_x, sep_line)

        win.refresh()
