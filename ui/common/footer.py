import curses
from ui.common.info_panel import draw_info_panel

class FooterController:
    def __init__(self):
        self.actions = []
        self.selected_idx = 0

    def add_action(self, label: str, key, callback):
        self.actions.append({
            "label": label,
            "key": key,
            "callback": callback
        })

    def handle_navigation(self, key, win, ctx):
        if key == curses.KEY_LEFT:
            self.move_selection(-1)
            self.draw(win, ctx)
        elif key == curses.KEY_RIGHT:
            self.move_selection(1)
            self.draw(win, ctx)
        elif key in ('\n', 10, 13):
            return self.handle_key(key)
        elif key in (9, '\t'):
            ctx.control.focus = ctx.control.last_focus

    
    def handle_key(self, key):
        if key in ('\n', 10, 13):
            action = self.actions[self.selected_idx]
            return action["callback"]()
        else:
            for action in self.actions:
                if action["key"] == key:
                    return action["callback"]()

    def move_selection(self, direction: int):
        self.selected_idx = (self.selected_idx + direction) % len(self.actions)


    def draw(self, win, ctx):
        win.attron(curses.color_pair(11))
        win.addstr(1, 2, "↑ ↓ = Navigation | ENTER = Select | ESC = Back | TAB = Footer")
        win.attroff(curses.color_pair(11))
        draw_info_panel(win, ctx.ui.version, str(ctx.ui.build))
        col = 2
        for i, action in enumerate(self.actions):
            text = f"[ {action['label']} ]"
            attr = curses.A_REVERSE if i == self.selected_idx and ctx.control.focus == "footer" else curses.A_NORMAL
            if col + len(text) < win.getmaxyx()[1] - 2:
                win.addstr(2, col, text, attr)
            col += len(text) + 2

    def add_action_once(self, label: str, key, callback):
        if not any(a["key"] == key for a in self.actions):
            self.add_action(label, key, callback)