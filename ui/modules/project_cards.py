import curses

def draw_project_card(ctx, win, project, selected=False):
    try:
        title = project.nev
        status = str(project.progress())+ "%"
        rows, cols = win.getmaxyx()

        attr = curses.color_pair(0)
        
        if selected and ctx.control.focus == "cards":
            attr |= curses.A_REVERSE
            for row in range(1, rows - 1):
                win.hline(row, 1, " ", cols - 2, attr)
            win.addstr(2, 2, title[:cols - 4], curses.color_pair(0) | curses.A_REVERSE)
            win.addstr(3, 2, f"Státusz: {status}"[:cols - 4], curses.color_pair(0) | curses.A_REVERSE)
            border_chars=["┃", "┃", " ", " ", "┏", "┓", "┗", "┛"]
            win.border(*[ord(c) for c in border_chars])
        
        else:
            border_chars=["│", "│", "⎽", "⎺", "┌", "┐", "└", "┘"]
            win.border(*[ord(c) for c in border_chars])
            win.addstr(2, 2, title[:cols - 4])
            win.addstr(3, 2, f"Státusz: {status}"[:cols - 4])
            win.bkgd(' ', curses.color_pair(0) | curses.A_REVERSE)
            
        #border_chars=["│", "│", "─", "─", "╭", "╮", "╰", "╯"]
        #border_chars=["█", "█", "▄", "▀", "▄", "▄", "▀", "▀"]
        #border_chars=[" ", " ", "▄", "▀", " ", " ", " ", " "]
        #border_chars=["┃", "┃", "━", "━", "┏", "┓", "┗", "┛"]

    except curses.error:
        pass



def draw_project_cards_panel(win, ctx, selected_idx, scroll_offset, padding=1):
    try:
        projektek = ctx.data.get("projektek", [])
        rows, cols = win.getmaxyx()
        card_height = ctx.layout.project_card_height
        spacing = ctx.layout.project_cards_spacing
        visible = max((rows - 2 * padding) // (card_height + spacing), 1)

        for i in range(visible):
            proj_idx = i + scroll_offset
            if proj_idx >= len(projektek):
                break

            y = i * (card_height + spacing) + padding
            card_win = win.derwin(card_height, cols - 2, y, 1)
            draw_project_card(ctx, card_win, projektek[proj_idx], selected=(proj_idx == selected_idx))
    except curses.error:
        pass
