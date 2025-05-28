import curses

def draw_main_menu(win, menu_items, selected_idx, padding=1):
    for i, item in enumerate(menu_items):
        prefix = "> " if i == selected_idx else "  "
        attr = curses.A_REVERSE if i == selected_idx else curses.A_NORMAL
        win.addstr(padding + i, padding + 1, prefix + item.upper()+" ", attr)