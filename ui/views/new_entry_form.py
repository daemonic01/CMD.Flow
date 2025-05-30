# views/new_entry_form_view.py

import curses
import textwrap
from utils.data_io import save_entry_form
from ui.common.footer import FooterController
from ui.views.base_view import BaseView
from utils.layout import update_screen_size
from ui.common.render_box import render_boxed
from utils.logger import log


class NewEntryFormView(BaseView):
    def __init__(self, ctx, level, parent=None, initial_values=None, edit_target=None):
        super().__init__(ctx)
        self.level = level
        self.parent = parent
        self.fields = ["Név", "Leírás", "Határidő (YYYY-MM-DD)", "Prioritás"]
        self.values = initial_values or ["", "", "", ""]
        self.current_idx = 0
        self.should_exit = False
        self.wait_ms = 2000
        self.edit_target = edit_target
        self.ctx.control.focus = "entry_form"

        self.footer = FooterController()
        self.footer.add_action("Mentés", "s", self.save_and_exit)

    def save_and_exit(self):
        row = self.calculate_rendered_rows()
        result = save_entry_form(
            self.layout["middle"][0],
            self.values,
            row,
            self.ctx.data["projects"],
            self.level,
            parent=self.parent,
            wait_ms=self.wait_ms,
            edit_target=self.edit_target
        )
        if result["status"] == "success" and result["exit"]:
            self.ctx.control.focus = "cards"
            self.should_exit = True

    def render(self, stdscr):
        update_screen_size(self.ctx)
        self.ctx.ui.footer = self.footer
        self.layout = {
            "middle": [stdscr],
            "footer": curses.newwin(4, curses.COLS, curses.LINES - 4, 0)
        }

        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        field_padding = 27
        wrap_width = max_x - field_padding - 6

        stdscr.addstr(3, 2, f"Új {self.level} létrehozása", curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(5, 2, "↑/↓/ENTER: mezők között | F10: mentés | ESC: kilépés", curses.color_pair(11))

        

        row = self.render_form_fields(stdscr, wrap_width, field_padding)
        cursor_row, cursor_col = self.calculate_cursor_pos(wrap_width, field_padding)
        if cursor_row < max_y - 1:
            stdscr.move(cursor_row, min(cursor_col, max_x - 1))

        stdscr.refresh()
        curses.curs_set(1)
        render_boxed(self.layout["footer"], lambda w: self.footer.draw(w, self.ctx))



    def handle_input(self, key):
        if self.ctx.control.focus == "footer":
            return self.footer.handle_navigation(key, self.layout["footer"], self.ctx)
        
        if key in ('\n', '\r'):
            self.current_idx = (self.current_idx + 1) % len(self.fields)
        elif key == curses.KEY_UP:
            self.current_idx = (self.current_idx - 1) % len(self.fields)
        elif key == curses.KEY_DOWN:
            self.current_idx = (self.current_idx + 1) % len(self.fields)
        elif key in (curses.KEY_BACKSPACE, 127, 8) or key == '':
            self.values[self.current_idx] = self.values[self.current_idx][:-1]

        elif key in (9, '\t'):
            self.ctx.control.last_focus = self.ctx.control.focus
            self.ctx.control.focus = "footer"

        elif key == '' or key == 27:
            curses.curs_set(0)
            return "pop"
        elif key  in (274, curses.KEY_F10):
             row = self.calculate_rendered_rows()
             result = save_entry_form(
            self.layout["middle"][0],
            self.values,
            row,
            self.ctx.data["projects"],
            self.level,
            parent=self.parent,
            wait_ms=self.wait_ms
        )
             if result["status"] == "success" and result["exit"]:
                self.should_exit = True

        elif isinstance(key, str) and len(key) == 1:
            if len(self.values[self.current_idx]) < 500:
                self.values[self.current_idx] += key


        if self.should_exit:
            return "pop"




    def render_form_fields(self, stdscr, wrap_width, field_padding):
        row = 7
        max_y, max_x = curses.LINES, curses.COLS

        for i, field in enumerate(self.fields):
            label = f"[{field}]".ljust(25)

            is_selected = (i == self.current_idx)
            stdscr.addstr(row, 4, label, curses.A_REVERSE if is_selected else curses.A_NORMAL)

            if field == "Leírás" and self.values[i]:
                wrapped = textwrap.wrap(self.values[i], wrap_width)
                for j, line in enumerate(wrapped):
                    if row + j < max_y - 1:
                        stdscr.addstr(row + j, 4 + field_padding, line[:wrap_width])
                row += max(1, len(wrapped))
            else:
                display_val = self.values[i] if self.values[i] else "<nincs megadva>"
                stdscr.addstr(row, 4 + field_padding, display_val[:wrap_width])
                row += 1

            if row < max_y - 1:
                stdscr.hline(row, 2, '-', max_x - 20)
                row += 1

        return row

    def calculate_rendered_rows(self):
        wrap_width = curses.COLS - 27 - 6
        return self.render_form_fields(self.layout["middle"][0], wrap_width, 27)




    def calculate_cursor_pos(self, wrap_width, field_padding):
        cursor_row = 7
        for i in range(self.current_idx):
            if self.fields[i] == "Leírás" and self.values[i]:
                text = self.values[i]
                wrapped_lines = (len(text) // wrap_width) + (1 if text else 1)
                cursor_row += wrapped_lines + 1

            else:
                cursor_row += 2

        if self.values[self.current_idx]:
            if self.fields[self.current_idx] == "Leírás":
                text = self.values[self.current_idx]
                cursor_row += len(text) // wrap_width
                # simulate word-aware wrapping to match display
                last_line_len = 0
                line_len = 0
                for word in text.split(' '):
                    if line_len + len(word) + (1 if line_len > 0 else 0) > wrap_width:
                        line_len = len(word)
                    else:
                        line_len += len(word) + (1 if line_len > 0 else 0)
                    last_line_len = line_len
                cursor_col = 4 + field_padding + last_line_len
            else:
                last_line = self.values[self.current_idx]
                cursor_col = 4 + field_padding + len(last_line)
        else:
            cursor_col = 4 + field_padding
        
        return cursor_row, cursor_col