import curses

def load_logo(path="visuals/logo_full.txt"):
    try:
        with open(path, encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f.readlines()]
    except Exception:
        return ["CMD.Flow"]
    
def draw_logo(win, ctx):
    logo_lines = ctx.ui.logos
    start_row = 1
    rows, cols = win.getmaxyx()
    for i, line in enumerate(logo_lines):
        if i + start_row >= rows - 1:
            break
        line = line[:cols - 2]
        col = max(1, (cols - len(line)) // 2)
        win.addstr(start_row + i, col, line)