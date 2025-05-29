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
        full_desc: str = ""
    ):
        self.id = id or Subtask._id_counter
        Subtask._id_counter = max(Subtask._id_counter, self.id + 1)
        self.title = title
        self.done = done

        # New metadata fields
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.full_desc = full_desc

    def toggle(self):
        self.done = not self.done

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "creation_date": self.creation_date,
            "deadline": self.deadline,
            "full_desc": self.full_desc
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            done=data.get("done", False),
            id=data.get("id"),
            creation_date=data.get("creation_date", date.today().isoformat()),
            deadline=data.get("deadline", ""),
            full_desc=data.get("full_desc", "")
        )


class Task:
    _id_counter = 1

    def __init__(self, title: str, id: int = None, creation_date: str = None, deadline: str = "", full_desc: str = ""):
        self.id = id or Task._id_counter
        Task._id_counter = max(Task._id_counter, self.id + 1)
        self.title = title
        self.subtasks: list[Subtask] = []

        # New metadata fields
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.full_desc = full_desc

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
            "full_desc": self.full_desc,
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
            full_desc=data.get("full_desc", "")
        )
        f.subtasks = [Subtask.from_dict(r) for r in data.get("subtasks", [])]
        return f




    @classmethod
    def from_dict(cls, data):
        f = cls(data["title"], data["id"])
        f.subtasks = [Subtask.from_dict(r) for r in data["subtasks"]]
        return f


class Phase:
    _id_counter = 1

    def __init__(self, title: str, id: int = None, creation_date: str = None, deadline: str = "", full_desc: str = ""):
        self.id = id or Phase._id_counter
        Phase._id_counter = max(Phase._id_counter, self.id + 1)
        self.title = title
        self.tasks: list[Task] = []

        # New metadata fields
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline
        self.full_desc = full_desc

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
            "full_desc": self.full_desc,
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
            full_desc=data.get("full_desc", "")
        )
        phase.tasks = [Task.from_dict(f) for f in data.get("tasks", [])]
        return phase


class Project:
    _id_counter = 1

    def __init__(self, title: str, id: int = None, creation_date: str = None, deadline: str = "", full_desc: str = "", priority: int = 1, status: bool = False):
        self.id = id or Project._id_counter
        Project._id_counter = max(Project._id_counter, self.id + 1)
        self.title = title
        self.phases: list[Phase] = []
        self.creation_date = creation_date or date.today().isoformat()
        self.deadline = deadline  # Optional deadline (YYYY-MM-DD or empty)
        self.full_desc = full_desc      # Optional description
        self.priority = priority
        self.status = status

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
            "full_desc": self.full_desc,
            "priority": self.priority,
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
            full_desc=data.get("full_desc", ""),
            priority=data.get("priority", ""),
            status=data.get("status", "")
        )
        project.phases = [Phase.from_dict(f) for f in data.get("phases", [])]
        return project







# --- Segédfüggvények ---
def print_structure(projects: list[Project]):
    for p in projects:
        print(f"Project: {p.title} (#{p.id}) - {p.progress()}%")
        for phase in p.phases:
            print(f"  Phase: {phase.title} (#{phase.id}) - {phase.progress()}%")
            for task in phase.tasks:
                print(f"    Task: {task.title} (#{task.id}) - {task.progress()}%")
                for resz in task.subtasks:
                    status = "[x]" if resz.done else "[ ]"
                    print(f"      {status} {resz.title} (#{resz.id})")

def remove_project_by_id(projects: list[Project], id: int) -> list[Project]:
    [p for p in projects if p.id != id]




# --- Interaktív parancskezelés ---
def toggle_subtask_interaktiv(projects):
    try:
        pid = int(input("Project ID: "))
        project = next((p for p in projects if p.id == pid), None)
        if not project:
            print("Nincs ilyen project.")
            return

        fazid = int(input("  Fázis ID: "))
        phase = project.get_phase_by_id(fazid)
        if not phase:
            print("  Nincs ilyen fázis.")
            return

        fid = int(input("    Task ID: "))
        task = phase.get_task_by_id(fid)
        if not task:
            print("    Nincs ilyen task.")
            return

        rid = int(input("      Résztask ID: "))
        resz = task.get_subtask_by_id(rid)
        if not resz:
            print("      Nincs ilyen résztask.")
            return

        resz.toggle()
        print("      Résztask állapota megváltozott.")
    except ValueError:
        print("Hibás bemenet.")


# --- Main függvény ---

def main():
    projects = load_projects_from_file()

    while True:
        print("\n--- CMD.Flow ---")
        print("Parancsok: add | list | delete | toggle | save | exit")
        parancs = input(">>> ").strip().lower()

        # --- Listázás ---
        if parancs == "list":
            print_structure(projects)

        # --- Résztask kapcsolás ---
        elif parancs == "toggle":
            toggle_subtask_interaktiv(projects)

        # --- Adatok mentése ---
        elif parancs == "save":
            save_projects_to_file(projects)
            print("Mentve.")
        
        # --- Kilépés ---
        elif parancs == "exit":
            print("Kilépés...")
            break

        # --- Új egység hozzáadása ---
        elif parancs.startswith("add"):
            alparancs = parancs.split()
            if len(alparancs) < 2:
                print("Pontosan add mit?")
                continue

            tipus = alparancs[1]

            if tipus == "project":
                title = input("Project titlee: ")
                projects.append(Project(title))

            elif tipus == "phase":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    title = input("Fázis titlee: ")
                    project.add_phase(title)


            elif tipus == "task":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    fid = int(input("Fázis ID: "))
                    phase = project.get_phase_by_id(fid)
                    if phase:
                        title = input("Task titlee: ")
                        phase.add_task(title)
                    else:
                        print("Nincs ilyen fázis.")
                else:
                    print("Nincs ilyen project.")

            elif tipus == "subtask":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    fid = int(input("Fázis ID: "))
                    phase = project.get_phase_by_id(fid)
                    if phase:
                        felid = int(input("Task ID: "))
                        task = phase.get_task_by_id(felid)
                        if task:
                            title = input("Résztask titlee: ")
                            task.add_subtask(title)
                        else:
                            print("Nincs ilyen task.")
                    else:
                        print("Nincs ilyen fázis.")
                else:
                    print("Nincs ilyen project.")

            else:
                print("Ismeretlen add-típus.")

        # --- Egység törlése ---
        elif parancs.startswith("delete"):
            alparancs = parancs.split()
            if len(alparancs) < 2:
                print("Pontosan delete mit?")
                continue

            tipus = alparancs[1]

            if tipus == "project":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    if project.phases:
                        valasz = input(f"A(z) '{project.title}' project nem üres. Törlöd? (i/n): ").lower()
                        if valasz != "i":
                            print("Törlés megszakítva.")
                            continue
                    projects = [p for p in projects if p.id != pid]
                    print("Project törölve.")
                else:
                    print("Nincs ilyen project.")

            elif tipus == "phase":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    fid = int(input("Fázis ID: "))
                    project.remove_phase_by_id(fid)

            elif tipus == "task":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    fazid = int(input("Fázis ID: "))
                    phase = project.get_phase_by_id(fazid)
                    if phase:
                        felid = int(input("Task ID: "))
                        phase.remove_task_by_id(felid)

            elif tipus == "subtask":
                pid = int(input("Project ID: "))
                project = next((p for p in projects if p.id == pid), None)
                if project:
                    fazid = int(input("Fázis ID: "))
                    phase = project.get_phase_by_id(fazid)
                    if phase:
                        felid = int(input("Task ID: "))
                        task = phase.get_task_by_id(felid)
                        if task:
                            rid = int(input("Résztask ID: "))
                            task.remove_subtask_by_id(rid)

            else:
                print("Ismeretlen delete-típus.")

        else:
            print("Ismeretlen parancs.")


if __name__ == "__main__":
    main()
