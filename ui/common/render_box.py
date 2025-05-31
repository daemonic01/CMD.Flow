import curses

def render_boxed(
    win,
    draw_content_fn=None,
    border=True,
    title=None,
    color_pair=0,
    border_chars=None,
    **kwargs
):
    try:


        if border:
            if border_chars and len(border_chars) == 8:
                try:
                    win.border(
                        *[ord(c) for c in border_chars]
                    )
                except curses.error:
                    pass
            else:
                win.box()

            if title:
                max_width = win.getmaxyx()[1] - 4
                title = f" {title[:max_width]} "
                try:
                    win.addstr(0, 2, title, curses.color_pair(color_pair))
                except curses.error:
                    pass

        if draw_content_fn:
            draw_content_fn(win, **kwargs)

        win.refresh()
    except curses.error:
        pass

