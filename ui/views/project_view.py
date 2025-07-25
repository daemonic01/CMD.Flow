import curses, textwrap
from core.backend import Project, Phase, Task, Subtask
from core.backend import update_completion_status
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
from utils.hierarchy import flatten_project_hierarchy, get_children, get_parent
from ui.views.new_entry_form import NewEntryFormView

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
        self.footer_updated = False
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
        
        self.items = [(self.project, -1)] + flatten_project_hierarchy(self.project)
        self.ctx.control.mode = "project_view"
        self.ctx.ui.footer = self.footer
        self.selected_item = self.items[self.selected_idx][0]
        self.selected_children = get_children(self.selected_item)


        stdscr.refresh()

        
        render_boxed(self.layout["header"], draw_content_fn= lambda w: draw_header(w, self.project_title_figlet, self.project.title))

        


        render_boxed(
            self.layout["middle"][0],
            draw_content_fn=self.draw_explorer_panel,
            title="» Projektstruktúra" if self.ctx.control.focus == "explorer" else "Projektstruktúra",
            border_chars= self.ctx.layout.selected_panel_border if self.ctx.control.focus == "explorer" else None
        )


        render_boxed(
            self.layout["middle"][1],
            draw_content_fn=self.draw_details_panel,
            title="» Részletek" if self.ctx.control.focus == "project_details" else "Részletek",
            border_chars= self.ctx.layout.selected_panel_border if self.ctx.control.focus == "project_details" else None
        )

        if self.ctx.control.focus == "project_details":
            self.realign_table_scroll()

        


        if (self.ctx.control.focus == "project_details" and not self.footer_updated):
            selected = self.items[self.selected_idx][0]
            level, parent = self.get_add_target_info(selected)
            if level:
                self.footer.add_action_once("Új", "n", lambda: self.open_add_form(level, parent))
            self.footer.add_action_once("Szerkesztés", "e", self.open_edit_form)
            if not isinstance(selected, Project):
                self.footer.add_action_once("Törlés", "d", lambda: self.open_delete_confirm())

            self.footer_updated = True

        elif self.ctx.control.focus not in ("project_details", "footer") and self.footer_updated:
            self.footer.actions = [a for a in self.footer.actions if a["key"] not in ("d", "e", "n")]
            self.footer_updated = False




        render_boxed(self.layout["footer"], lambda w: self.footer.draw(w, self.ctx),
            border_chars= self.ctx.layout.selected_panel_border if self.ctx.control.focus == "footer" else None)

    def handle_input(self, key):
        """
        Handle user input based on the current focus mode.

        Routes key events to different input handlers depending on the UI focus:
        - 'footer': navigates and handles footer-specific commands
        """

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
                    max_visible = self.layout["middle"][1].getmaxyx()[0] - 12
                    if self.table_selected_row >= self.table_scroll_offset + max_visible:
                        self.table_scroll_offset = self.table_selected_row - max_visible + 1

            elif key == curses.KEY_UP:
                if self.table_selected_row > 0:
                    self.table_selected_row -= 1
                    if self.table_selected_row < self.table_scroll_offset:
                        self.table_scroll_offset = self.table_selected_row

            elif key in (curses.KEY_BACKSPACE, 127, 8, "\b"):
                log("BACKSPACE PRESSED!!")
                selected = self.items[self.selected_idx][0]
                parent = get_parent(selected, self.ctx.data["projects"])
                if parent:
                    log("PARENT TRUE!!")
                    for idx, (obj, _) in enumerate(self.items):
                        if obj == parent:
                            self.selected_idx = idx
                            max_visible = self.layout["middle"][0].getmaxyx()[0] - 2
                            if self.selected_idx >= self.scroll_offset + max_visible:
                                self.scroll_offset = self.selected_idx - max_visible + 1
                            elif self.selected_idx < self.scroll_offset:
                                self.scroll_offset = self.selected_idx
                            break


            elif key in (10, 13, "\n"):
                parent = self.items[self.selected_idx][0]
                children = get_children(parent)

                if isinstance(parent, Subtask):
                    self.toggle_and_save(parent)
                    return

                if not children or self.table_selected_row >= len(children):
                    return

                selected_child = children[self.table_selected_row]

                if isinstance(selected_child, Subtask):
                    self.toggle_and_save(selected_child)
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
                self.ctx.control.last_focus = self.ctx.control.focus
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
                self.ctx.control.last_focus = self.ctx.control.focus
                self.ctx.control.focus = "project_details"
                self.table_selected_row = 0
                self.table_scroll_offset = 0

            elif key in (9, '\t'):
                self.ctx.control.last_focus = self.ctx.control.focus
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
                -1: curses.color_pair(1),
                0: curses.color_pair(2),
                1: curses.color_pair(3),
                2: curses.color_pair(4),
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

        #selected = self.items[self.selected_idx][0]
        selected = self.selected_item
        children = self.selected_children

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
        #children = get_children(selected)
        if children:
            self.draw_details_table(win, children, start_row=row)


        # A fő információk és children rajzolása után
        elif hasattr(selected, "toggle"):  # csak részfeladatnál
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
            desc = getattr(child, "short_desc", "")[:40].ljust(40)

            line = f"|   {status}   | {title} | {deadline} | {desc} |"
            try:
                if self.table_scroll_offset + i == self.table_selected_row:
                    win.addstr(row, pad_x, line, curses.A_REVERSE)
                else:
                    win.addstr(row, pad_x, line)
            except curses.error:
                pass
        
    def realign_table_scroll(self):
        children = get_children(self.items[self.selected_idx][0])
        max_visible = self.layout["middle"][1].getmaxyx()[0] - 12  # vagy számítsd pontosan

        if self.table_selected_row >= self.table_scroll_offset + max_visible:
            self.table_scroll_offset = self.table_selected_row - max_visible + 1
        elif self.table_selected_row < self.table_scroll_offset:
            self.table_scroll_offset = self.table_selected_row
        elif len(children) - self.table_scroll_offset < max_visible:
            self.table_scroll_offset = max(0, len(children) - max_visible)


    def open_add_form(self, level=None, parent=None):
        selected = self.items[self.selected_idx][0]
        level, parent = self.get_add_target_info(selected)
        if level is None or parent is None:
            if not (0 <= self.selected_idx < len(self.items)):
                return "pop"
            if level is None:
                return "pop"

        return NewEntryFormView(
            ctx=self.ctx,
            level=level,
            parent=parent,
            initial_values=["", "", "", "", ""],
            edit_target=None
        )



    def open_edit_form(self):
        if not (0 <= self.selected_idx < len(self.items)):
            return "pop"

        from core.backend import Project, Phase, Task, Subtask

        obj = self.items[self.selected_idx][0]
        projects = self.ctx.data["projects"]

        # Meghatározzuk a szintet
        if isinstance(obj, Project):
            level = "project"
            parent = None
        elif isinstance(obj, Phase):
            level = "phase"
            parent = get_parent(obj, projects)
        elif isinstance(obj, Task):
            level = "task"
            parent = get_parent(obj, projects)
        elif isinstance(obj, Subtask):
            level = "subtask"
            parent = get_parent(obj, projects)
        else:
            return "pop"

        # Mezők előkészítése
        values = [
            obj.title or "",
            getattr(obj, "short_desc", "") or "",
            getattr(obj, "full_desc", "") or "",
            getattr(obj, "deadline", "") or "",
            str(getattr(obj, "priority", 1))
        ]

        return NewEntryFormView(
            ctx=self.ctx,
            level=level,
            initial_values=values,
            parent=parent,
            edit_target=obj
        )

    


    def open_delete_confirm(self):
        target = self.items[self.selected_idx][0]
        title = getattr(target, "title", "Ismeretlen elem")

        def on_accept():
            self.delete_selected_element()
            self.ctx.control.focus = "explorer"
            return "pop"

        return PopupConfirmView(
            ctx=self.ctx,
            message=f"Törlöd ezt az elemet?\n\n→ {title}",
            on_accept=on_accept,
            on_cancel=lambda: "pop"
        )




    def delete_selected_element(self):
        all_projects = self.ctx.data["projects"]
        target = self.items[self.selected_idx][0]

        from core.backend import Project, Phase, Task, Subtask

        # Projekt törlése
        if isinstance(target, Project):
            all_projects.remove(target)

        else:
            parent = get_parent(target, all_projects)

            if isinstance(target, Phase) and hasattr(parent, "phases"):
                parent.phases.remove(target)

            elif isinstance(target, Task) and hasattr(parent, "tasks"):
                parent.tasks.remove(target)

            elif isinstance(target, Subtask) and hasattr(parent, "subtasks"):
                parent.subtasks.remove(target)

        # Mentés fájlba
        from utils.data_io import save_projects_to_file
        save_projects_to_file(all_projects)

        # UI frissítés
        self.selected_idx = max(0, self.selected_idx - 1)
        self.scroll_offset = max(0, min(self.scroll_offset, self.selected_idx))


    def get_add_target_info(self, selected):
        from core.backend import Project, Phase, Task
        if isinstance(selected, Project):
            return "phase", selected
        elif isinstance(selected, Phase):
            return "task", selected
        elif isinstance(selected, Task):
            return "subtask", selected
        else:
            return None, None  # Subtask után már nincs újabb szint

    
    def toggle_and_save(self, obj):
        obj.toggle()
        from utils.data_io import save_projects_to_file
        update_completion_status(self.ctx.data["projects"])
        save_projects_to_file(self.ctx.data["projects"])
