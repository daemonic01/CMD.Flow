
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import curses
from utils.data_io import *
from visuals import *
from context import AppContext
from ui.views.base_view import BaseView
from ui.views.main_menu_view import MainMenuView, PopupConfirmView
from utils.layout import update_screen_size





def main(stdscr):
    stdscr.clear()
    stdscr.timeout(120)
    curses.curs_set(0)
    ctx = AppContext()
    view_stack = [MainMenuView(ctx)]

    while view_stack:

        if len(view_stack) >= 2 and isinstance(view_stack[-1], PopupConfirmView):
            update_screen_size(ctx)             # Refresh even if popup is active
            view_stack[-2].render(stdscr)       # Redraw view in the background

        current = view_stack[-1]
        current.render(stdscr)

        stdscr.refresh()
        key_code = stdscr.getch()
        try:
            key = chr(key_code) if 0 <= key_code <= 255 or key_code in (337, 369) else key_code
        except ValueError:
            key = key_code
        result = current.handle_input(key)

        if isinstance(result, BaseView):
            view_stack.append(result)
        elif result == "pop":
            stdscr.clear()
            view_stack.pop()
        elif result == "back":
            stdscr.clear()
            view_stack.pop()
            view_stack.pop()
            ctx.control.focus = "main"
        elif result == "exit":
            break


if __name__ == "__main__":
    curses.wrapper(main)



    