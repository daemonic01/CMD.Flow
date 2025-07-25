from datetime import datetime

def is_valid_date(text: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        date = datetime.strptime(text, fmt).date()
        return date > datetime.today().date()
    except ValueError:
        return False
    

def get_nearest_deadline(projects):
    upcoming = []

    def collect_deadlines(obj):
        if hasattr(obj, "deadline") and obj.deadline and not getattr(obj, "is_done", False):
            try:
                dt = datetime.strptime(obj.deadline, "%Y-%m-%d")
                if dt >= datetime.today():
                    upcoming.append(dt)
            except ValueError:
                pass

    def walk(obj):
        collect_deadlines(obj)
        for child in getattr(obj, "phases", []):
            walk(child)
        for child in getattr(obj, "tasks", []):
            walk(child)
        for child in getattr(obj, "subtasks", []):
            collect_deadlines(child)

    for project in projects:
        walk(project)

    return min(upcoming).strftime("%Y-%m-%d") if upcoming else "—"