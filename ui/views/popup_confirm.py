from ui.views.base_view import BaseView
import curses
from utils.logger import log

class PopupConfirmView(BaseView):
    def __init__(self, ctx, message, on_accept=None, on_cancel=None):
        super().__init__(ctx)
        self.message = message
        self.on_accept = on_accept
        self.on_cancel = on_cancel
        self.options = ["Igen", "Mégse"]
        self.selected_idx = 1

    def render(self, stdscr):
        stdscr.refresh()
        rows, cols = stdscr.getmaxyx()
        width = 50
        height = 8
        start_y = (rows - height) // 2
        start_x = (cols - width) // 2


        win = curses.newwin(height, width, start_y, start_x)
        win.box()
        
        try:
            win.addstr(1, 2, self.message[:width - 4], curses.A_BOLD)

            option_str = ""
            for i, opt in enumerate(self.options):
                if i == self.selected_idx:
                    option_str += f"[ {opt} ] "
                else:
                    option_str += f"  {opt}   "
            # center
            option_start_x = max(2, (width - len(option_str)) // 2)
            win.addstr(3, option_start_x, option_str)
        except curses.error:
            pass

        
        win.refresh()


    def handle_input(self, key):
        if key in (curses.KEY_LEFT, curses.KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.options)
        elif key in (curses.KEY_RIGHT, curses.KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.options)
        elif key in [10, 13, "\n"]:  # ENTER
            selected = self.options[self.selected_idx]
            if selected == "Igen" and self.on_accept:
                return self.on_accept()
            elif selected == "Mégse" and self.on_cancel:
                return self.on_cancel()
            return "pop"
        elif key == '' or key == 27:  # ESC
            if self.on_cancel:
                return self.on_cancel()
            return "pop"
