from core.backend import Project, Phase, Task, Subtask

def get_children(obj):
    if isinstance(obj, Project):
        return obj.phases or []
    elif isinstance(obj, Phase):
        return obj.tasks or []
    elif isinstance(obj, Task):
        return obj.subtasks or []
    return []


def get_parent(obj, projects):
    from core.backend import Project, Phase, Task, Subtask

    for project in projects:
        if obj == project:
            return None

        for phase in getattr(project, "phases", []):
            if obj == phase:
                return project

            for task in getattr(phase, "tasks", []):
                if obj == task:
                    return phase

                for subtask in getattr(task, "subtasks", []):
                    if obj == subtask:
                        return task
    return None



def flatten_project_hierarchy(project):
    items = []

    for fazis in project.phases:
        items.append((fazis, 0))
        for feladat in fazis.tasks:
            items.append((feladat, 1))
            for resz in feladat.subtasks:
                items.append((resz, 2))

    return items


