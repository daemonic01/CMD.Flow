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



def flatten_project_hierarchy(project):
    items = []

    for fazis in project.phases:
        items.append((fazis, 0))
        for feladat in fazis.tasks:
            items.append((feladat, 1))
            for resz in feladat.subtasks:
                items.append((resz, 2))

    return items


