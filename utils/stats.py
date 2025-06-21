def count_done_projects(projects):
    done = sum(1 for p in projects if getattr(p, "is_done", False))
    not_done = len(projects) - done
    return done, not_done