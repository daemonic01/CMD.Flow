import curses
from utils.logger import log


def update_screen_size(ctx):
    curses.update_lines_cols()
    old_rows =  ctx.ui.screen["rows"] #ctx["ui"]["screen"]["rows"]
    old_cols = ctx.ui.screen["cols"] #ctx["ui"]["screen"]["cols"]

    rows, cols = curses.LINES, curses.COLS
    #rows, cols = ctx["ui"]["stdscr"].getmaxyx()
    ctx.ui.screen["rows"] = rows
    ctx.ui.screen["cols"] = cols
    ctx.control.screen_changed = (old_rows != rows or old_cols != cols)    # ctx["control"]["screen_changed"]

    # Frissítsük a compact módokat nézetenként
    """
    for view, limits in ctx.get("layout_profiles", {}).items():
        r = ctx["ui"]["screen"]["rows"]
        c = ctx["ui"]["screen"]["cols"]
        ctx["ui"]["compact"][view] = (r < limits["min_rows"] or c < limits["min_cols"])
    """
 
    ctx.control.layout_blocked = rows < 30 or cols < 105




def compute_layout(ctx):
    rows = ctx.ui.screen["rows"]
    cols = ctx.ui.screen["cols"]
    layout = ctx.layout

    has_header = layout.has_header
    has_footer = layout.has_footer
    header_height = layout.header_height
    footer_height = layout.footer_height
    middle_split = layout.middle_split

    # Remaining space for content
    middle_height = max(1, rows - header_height - footer_height)

    windows = {
        "header": None,
        "middle": [],
        "footer": None
    }

    if has_header:
        windows["header"] = curses.newwin(header_height, cols, 0, 0)
    
    x = 0
    total_width = 0
    for i, ratio in enumerate(middle_split):
        # fixing the width of the middle section with the remaining columns
        if i == len(middle_split) - 1:
            width = cols - total_width
        else:
            width = int(cols * ratio)
            total_width += width

        win = curses.newwin(middle_height, width, header_height, x)
        windows["middle"].append(win)
        x += width

    if has_footer:
        windows["footer"] = curses.newwin(footer_height, cols, header_height + middle_height, 0)

    return windows