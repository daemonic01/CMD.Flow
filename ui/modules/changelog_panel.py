import curses
import textwrap


def draw_changelog_panel(win, ctx, lines, scroll=0, padding=1):
    rows, cols = win.getmaxyx()
    usable_width = cols - 6
    wrap_indent = 4
    base_x = 4
    start_row = 2
    max_rows = rows - start_row - 1

    try:
        wrapped_lines = []
        for kind, line in lines:
            wrapped = textwrap.wrap(line, width=usable_width) or [""]
            for j, subline in enumerate(wrapped):
                wrapped_lines.append((kind, subline, j > 0))  # j > 0 jelzi, hogy ez nem első sor

        visible_lines = wrapped_lines[scroll : scroll + max_rows]

        for i, (kind, subline, is_wrapped) in enumerate(visible_lines):
            attr = curses.A_BOLD | curses.A_UNDERLINE if kind == "header" else curses.A_NORMAL
            x = base_x + (wrap_indent if is_wrapped else 0)
            win.addstr(start_row + i, x, subline, attr)

    except curses.error:
        pass
