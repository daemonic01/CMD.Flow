import curses
from utils.localization import t


def draw_window_size_error(stdscr):
    stdscr.clear()

    try:
        curses.update_lines_cols()
        rows, cols = stdscr.getmaxyx()
    except curses.error:
        rows, cols = 24, 80  # fallback

    msg_lines = [
        t("errors.window_size_error_message_1"),
        t("errors.window_size_error_message_2")
    ]

    start_row = max((rows - len(msg_lines)) // 2, 0)
    for i, line in enumerate(msg_lines):
        start_col = max((cols - len(line)) // 2, 0)
        try:
            stdscr.addstr(start_row + i, start_col, line, curses.A_BOLD)
        except curses.error:
            pass

    try:
        stdscr.refresh()
    except curses.error:
        pass

    stdscr.timeout(100000)  # várunk 300 ms-ot, majd visszatérünk (Igazából tök mindegy, ezt mire állítjuk. Minél több, annál ritkábban villog idegesítően a redraw.)
    try:
        
        stdscr.getch()
    except curses.error:
        pass




def wait_for_valid_window_size(stdscr, min_rows=30, min_cols=70):
    prev_size = (-1, -1)

    while True:
        rows, cols = stdscr.getmaxyx()
        curr_size = (rows, cols)

        if curr_size != prev_size:
            prev_size = curr_size

            if rows < min_rows or cols < min_cols:
                # csak akkor rajzolunk, ha túl kicsi
                stdscr.erase()  # nem clear, csak törli a tartalmat, nem flash-el
                msg_lines = [
                    "A program megjelenítése jelenleg nem támogatja ezt az ablakméretet.",
                    "A folytatáshoz növeld meg az ablak méretét."
                ]
                start_row = max((rows - len(msg_lines)) // 2, 0)
                for i, line in enumerate(msg_lines):
                    start_col = max((cols - len(line)) // 2, 0)
                    try:
                        stdscr.addstr(start_row + i, start_col, line, curses.A_BOLD)
                    except curses.error:
                        pass
                try:
                    stdscr.refresh()
                except curses.error:
                    pass

        if rows >= min_rows and cols >= min_cols:
            break

        stdscr.timeout(100000)
        try:
            stdscr.getch()
        except curses.error:
            pass
