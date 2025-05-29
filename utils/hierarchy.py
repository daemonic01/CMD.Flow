import curses

def get_children(obj):
    if hasattr(obj, "phases"):
        return obj.phases
    elif hasattr(obj, "tasks"):
        return obj.tasks
    elif hasattr(obj, "subtasks"):
        return obj.subtasks
    else:
        return []




def draw_hierarchy_panel(win, root_obj, start_y=1, start_x=2, indent=2, max_depth=10):
    def draw_node(obj, depth, row):
        if row >= win.getmaxyx()[0] - 1 or depth > max_depth:
            return row  # kilépünk, ha nincs több hely

        prefix = " " * (depth * indent)
        try:
            win.addstr(row, start_x, f"{prefix}- {obj.title} {obj.deadline}")
        except curses.error:
            pass  # túl hosszú sor vagy ablakból kifut

        row += 1
        for child in get_children(obj):
            row = draw_node(child, depth + 1, row)

        return row


    draw_node(root_obj, depth=0, row=start_y)
    win.refresh()
