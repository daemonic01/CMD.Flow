import json
import os
from typing import TYPE_CHECKING
import curses
from utils.date_utils import is_valid_date
from utils.localization import t


if TYPE_CHECKING:
    from core.backend import Project, Phase, Task, Subtask

def save_projects_to_file(projects: list["Project"], filename="data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in projects], f, indent=2, ensure_ascii=False)

def load_projects_from_file(filename="data.json") -> list["Project"]:
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        from core.backend import Project
        return [Project.from_dict(p) for p in data]





def save_entry_form(stdscr, values, row, projects, level, parent=None, wait_ms=2000, edit_target=None):
    curses.curs_set(0)

    title = values[0].strip()
    if not title:
        stdscr.addstr(row + 2, 4, t("errors.missing_name"), curses.A_BOLD)
        stdscr.refresh()
        curses.napms(wait_ms)
        return {"status": "error", "exit": False}

    deadline = values[3].strip()
    if deadline and not is_valid_date(deadline):
        stdscr.addstr(row + 2, 4, t("errors.invalid_date"), curses.A_BOLD)
        stdscr.refresh()
        curses.napms(wait_ms)
        return {"status": "error", "exit": False}

    entry_data = {
        "title": title,
        "short_desc": values[1].strip(),
        "full_desc": values[2].strip(),
        "deadline": deadline,
        "priority": values[4]
    }


    from core.backend import Project, Phase, Task, Subtask
    if edit_target:
        edit_target.title = entry_data["title"]
        edit_target.short_desc = entry_data["short_desc"]
        edit_target.full_desc = entry_data["full_desc"]
        edit_target.deadline = entry_data["deadline"]
        edit_target.priority = entry_data.get("priority", 1)

    else:
        if level == "project":
            projects.append(Project(**entry_data))
        elif level == "phase" and parent:
            parent.phases.append(Phase(**entry_data))
        elif level == "task" and parent:
            parent.tasks.append(Task(**entry_data))
        elif level == "subtask" and parent:
            parent.subtasks.append(Subtask(**entry_data))

    from core.backend import update_completion_status
    update_completion_status(projects)
    save_projects_to_file(projects)
    stdscr.addstr(row + 2, 4, "Saved successfully.", curses.A_BOLD)
    stdscr.refresh()
    curses.napms(wait_ms)

    return {"status": "success", "exit": True}
