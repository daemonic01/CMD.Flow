

def draw_header(win, lines, title):
    try: 
        rows, cols = win.getmaxyx()
        height, length = len(lines), len(lines[0])
        draw_row = (rows - height) // 2
        
        for i, line in enumerate(lines):
            if i + draw_row >= rows - 1:
                break
            line = line[:cols - 2]
            col = max(1, (cols - len(line)) // 2)
            win.addstr(draw_row + i, col, line)
    except:
        win.addstr(draw_row, (cols-length) // 2, title)