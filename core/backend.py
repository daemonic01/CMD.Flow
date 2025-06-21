from utils.data_io import load_projects_from_file, save_projects_to_file
from datetime import date

# --- Osztályok ---

class Subtask:
    _id_counter = 1

    def __init__(
        self,
        title: str,
        done: bool = False,
        id: int = None,
        creation_date: str = None,
        deadline: str = "",
        short_desc: str = "",
        full_desc: str = "",
        priority: int = 1
        
    ):
        self.id = id or Subtask._id_counter
        Subtask._id_counter = max(Subtask._id_counter, self.id + 1)
        self.title = title
        self.done = done

        # New metadata fields
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.short_desc = short_desc
        self.full_desc = full_desc
        self.priority = priority

    def toggle(self):
        self.done = not self.done

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "creation_date": self.creation_date,
            "deadline": self.deadline,
            "short_desc": self.short_desc,
            "full_desc": self.full_desc,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            done=data.get("done", False),
            id=data.get("id"),
            creation_date=data.get("creation_date", date.today().isoformat()),
            deadline=data.get("deadline", ""),
            short_desc=data.get("short_desc", ""),
            full_desc=data.get("full_desc", ""),
            priority=data.get("priority", "")
        )


class Task:
    _id_counter = 1

    def __init__(self, title: str, id: int = None, creation_date: str = None, deadline: str = "", short_desc: str = "", full_desc: str = "", priority: int = 1, is_done: bool = False):
        self.id = id or Task._id_counter
        Task._id_counter = max(Task._id_counter, self.id + 1)
        self.title = title
        self.subtasks: list[Subtask] = []

        # New metadata fields
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.short_desc = short_desc
        self.full_desc = full_desc
        self.priority = priority
        self.is_done = is_done

    def add_subtask(self, title: str):
        self.subtasks.append(Subtask(title))

    def progress(self) -> int:
        if not self.subtasks:
            return 0
        doneek = sum(1 for r in self.subtasks if r.done)
        return int((doneek / len(self.subtasks)) * 100)

    def get_subtask_by_id(self, id: int):
        return next((r for r in self.subtasks if r.id == id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "creation_date": self.creation_date,
            "deadline": self.deadline,
            "short_desc": self.short_desc,
            "full_desc": self.full_desc,
            "priority": self.priority,
            "is_done": self.is_done,
            "subtasks": [r.to_dict() for r in self.subtasks]
        }

    def remove_subtask(self, subtask):
        if subtask in self.subtasks:
            self.subtasks.remove(subtask)

    @classmethod
    def from_dict(cls, data):
        f = cls(
            title=data["title"],
            id=data.get("id"),
            creation_date=data.get("creation_date", date.today().isoformat()),
            deadline=data.get("deadline", ""),
            short_desc=data.get("short_desc", ""),
            full_desc=data.get("full_desc", ""),
            priority=data.get("priority", ""),
            is_done = data.get("is_done", False)
        )
        f.subtasks = [Subtask.from_dict(r) for r in data.get("subtasks", [])]
        return f


class Phase:
    _id_counter = 1

    def __init__(self, title: str, id: int = None, creation_date: str = None, deadline: str = "", short_desc: str = "", full_desc: str = "", priority: int = 1, is_done: bool = False):
        self.id = id or Phase._id_counter
        Phase._id_counter = max(Phase._id_counter, self.id + 1)
        self.title = title
        self.tasks: list[Task] = []

        # New metadata fields
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.short_desc = short_desc
        self.full_desc = full_desc
        self.priority = priority
        self.is_done = is_done

    def add_task(self, title: str):
        self.tasks.append(Task(title))

    def progress(self) -> int:
        if not self.tasks:
            return 0
        return int(sum(f.progress() for f in self.tasks) / len(self.tasks))

    def get_task_by_id(self, id: int):
        return next((f for f in self.tasks if f.id == id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "creation_date": self.creation_date,
            "deadline": self.deadline,
            "short_desc": self.short_desc,
            "full_desc": self.full_desc,
            "priority": self.priority,
            "is_done": self.is_done,
            "tasks": [f.to_dict() for f in self.tasks]
        }

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)

    @classmethod
    def from_dict(cls, data):
        phase = cls(
            title=data["title"],
            id=data.get("id"),
            creation_date=data.get("creation_date", date.today().isoformat()),
            deadline=data.get("deadline", ""),
            short_desc=data.get("short_desc", ""),
            full_desc=data.get("full_desc", ""),
            priority=data.get("priority", ""),
            is_done = data.get("is_done", False)
        )
        phase.tasks = [Task.from_dict(f) for f in data.get("tasks", [])]
        return phase


class Project:
    _id_counter = 1

    def __init__(self, title: str, id: int = None, creation_date: str = None, deadline: str = "", short_desc: str = "", full_desc: str = "", priority: int = 1, status: bool = False, is_done: bool = False):
        self.id = id or Project._id_counter
        Project._id_counter = max(Project._id_counter, self.id + 1)
        self.title = title
        self.phases: list[Phase] = []
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.short_desc = short_desc
        self.full_desc = full_desc
        self.priority = priority
        self.status = status
        self.is_done = is_done

    def add_phase(self, title: str):
        self.phases.append(Phase(title))

    def progress(self) -> int:
        if not self.phases:
            return 0
        return int(sum(f.progress() for f in self.phases) / len(self.phases))

    def get_phase_by_id(self, id: int):
        return next((f for f in self.phases if f.id == id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "creation_date": self.creation_date,
            "deadline": self.deadline,
            "short_desc": self.short_desc,
            "full_desc": self.full_desc,
            "priority": self.priority,
            "is_done": self.is_done,
            "phases": [f.to_dict() for f in self.phases],
            "status": self.status
        }

    def is_empty(self):
        return len(self.phases) == 0

    def remove_phase(self, phase):
        if phase not in self.phases:
            print("Phase not found.")
            return

        if phase.tasks:
            print(f"The phase '{phase.title}' isn't empty.")
            return

        self.phases.remove(phase)

    @classmethod
    def from_dict(cls, data):
        project = cls(
            title=data["title"],
            id=data.get("id"),
            creation_date=data.get("creation_date", date.today().isoformat()),
            deadline=data.get("deadline", ""),
            short_desc=data.get("short_desc", ""),
            full_desc=data.get("full_desc", ""),
            priority=data.get("priority", ""),
            status=data.get("status", ""),
            is_done = data.get("is_done", False)
        )
        project.phases = [Phase.from_dict(f) for f in data.get("phases", [])]
        return project
    



def update_completion_status(projects):
    for project in projects:
        for phase in project.phases:
            for task in phase.tasks:
                task.is_done = all(subtask.done for subtask in task.subtasks)
            phase.is_done = all(task.is_done for task in phase.tasks)
        project.is_done = all(phase.is_done for phase in project.phases)



