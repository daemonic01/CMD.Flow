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
        self.table_selected_row = 0
        self.table_scroll_offset = 0
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
    def handle_input(self, key):

        # ───────────── FOOTER ─────────────
        if self.ctx.control.focus == "footer":
            if key == 27:  # ESC
                self.ctx.control.focus = self.ctx.control.last_focus or "explorer"
            return self.footer.handle_navigation(key, self.layout["footer"], self.ctx)

        # ───────────── PROJECT DETAILS ─────────────
        if self.ctx.control.focus == "project_details":
            children = get_children(self.items[self.selected_idx][0])
            if key == curses.KEY_DOWN:
                if self.table_selected_row < len(children) - 1:
                    self.table_selected_row += 1
                    max_visible = self.layout["middle"][1].getmaxyx()[0] - 8
                    if self.table_selected_row >= self.table_scroll_offset + max_visible:
                        self.table_scroll_offset = self.table_selected_row - max_visible + 1

            elif key == curses.KEY_UP:
                if self.table_selected_row > 0:
                    self.table_selected_row -= 1
                    if self.table_selected_row < self.table_scroll_offset:
                        self.table_scroll_offset = self.table_selected_row

            elif key in (10, 13, "\n"):
                parent = self.items[self.selected_idx][0]
                children = get_children(parent)

                if not children and hasattr(parent, "toggle"):
                    parent.toggle()
                    from utils.data_io import save_projects_to_file
                    save_projects_to_file(self.ctx.data["projects"])
                    return


                if not children or self.table_selected_row >= len(children):
                    return

                selected_child = children[self.table_selected_row]


                if not get_children(selected_child):
                    selected_child.toggle()
                    from utils.data_io import save_projects_to_file
                    save_projects_to_file(self.ctx.data["projects"])
                else:

                    for idx, (obj, _) in enumerate(self.items):
                        if obj == selected_child:
                            self.selected_idx = idx
                            max_visible = self.layout["middle"][0].getmaxyx()[0] - 2
                            if self.selected_idx >= self.scroll_offset + max_visible:
                                self.scroll_offset = self.selected_idx - max_visible + 1
                            elif self.selected_idx < self.scroll_offset:
                                self.scroll_offset = self.selected_idx
                            break


            elif key == '' or key == 27:
                self.ctx.control.focus = "explorer"

            elif key in (9, '\t'):
                self.ctx.control.last_focus = "project_details"
                self.ctx.control.focus = "footer"

            return

        # ───────────── EXPLORER ─────────────
        if self.ctx.control.focus == "explorer":
            if key == curses.KEY_DOWN:
                if self.selected_idx < len(self.items) - 1:
                    self.selected_idx += 1
                    max_visible = self.layout["middle"][0].getmaxyx()[0] - 2
                    if self.selected_idx >= self.scroll_offset + max_visible:
                        self.scroll_offset = self.selected_idx - max_visible + 1

            elif key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
                    if self.selected_idx < self.scroll_offset:
                        self.scroll_offset = self.selected_idx

            elif key in (10, 13, "\n"):
                self.ctx.control.focus = "project_details"
                self.table_selected_row = 0
                self.table_scroll_offset = 0

            elif key in (9, '\t'):
                self.ctx.control.last_focus = "explorer"
                self.ctx.control.focus = "footer"

            return




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
        max_y, max_x = win.getmaxyx()
        pad_x = 2
        row = 1

        #self.ctx.control.focus = "project_details"

        selected = self.items[self.selected_idx][0]

        try:
            win.addstr(row, pad_x, f"Név: {selected.title}", curses.A_BOLD)
            row += 2
        except curses.error:
            pass

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

        if getattr(selected, "deadline", ""):
            win.addstr(row, pad_x, f"Határidő: {selected.deadline}")
            row += 2

        # Táblázat
        children = get_children(selected)
        if children:
            self.draw_details_table(win, children, start_row=row)


        # A fő információk és children rajzolása után
        if not children and hasattr(selected, "toggle"):  # csak részfeladatnál
            box_height = 3
            box_width = 30
            max_y, max_x = win.getmaxyx()
            box_y = max_y - box_height - 1
            box_x = max_x - box_width - 2

            try:
                box_win = win.derwin(box_height, box_width, box_y, box_x)
                box_win.box()
                cols = box_win.getmaxyx()[1]

                status = "[ KÉSZ ]" if selected.done else "[ NINCS KÉSZ ]"
                box_win.addstr(1, ((cols - len(status)-8)//2), f"Állapot: {status}")
                box_win.refresh()
            except curses.error:
                pass


        win.refresh()






    def draw_details_table(self, win, children, start_row):
        max_y, max_x = win.getmaxyx()
        pad_x = 2
        visible_rows = max_y - start_row - 2
        table_rows = children[self.table_scroll_offset:self.table_scroll_offset + visible_rows]

        # Fejléc
        header = "| Státusz |        Név        |  Határidő  | Leírás                                   |"
        sep_line = "|" + "-" * (len(header) - 2) + "|"

        try:
            win.addstr(start_row, pad_x, header, curses.A_UNDERLINE)
            win.addstr(start_row + 1, pad_x, sep_line)
        except curses.error:
            pass

        for i, child in enumerate(table_rows):
            row = start_row + 2 + i
            if row >= max_y - 1:
                break

            status = "[x]" if getattr(child, "done", False) else "[ ]"
            title = child.title[:17].ljust(17)
            deadline = getattr(child, "deadline", "—")[:10].ljust(10)
            desc = getattr(child, "full_desc", "")[:40].ljust(40)

            line = f"|   {status}   | {title} | {deadline} | {desc} |"
            try:
                if self.table_scroll_offset + i == self.table_selected_row:
                    win.addstr(row, pad_x, line, curses.A_REVERSE)
                else:
                    win.addstr(row, pad_x, line)
            except curses.error:
                pass

