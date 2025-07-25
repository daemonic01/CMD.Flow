def generate_demo_data():
    from core.backend import Project, Phase, Task, Subtask

    demo_project = Project(
        title="Demo Project",
        short_desc="Short description of test project.",
        full_desc="This is an example project for representation of the systems functions.",
        deadline="2099-08-15",
        priority=1,
    )

    phase1 = Phase(
        title="Phase I.",
        short_desc="Preparing phase of the project.",
        full_desc="The first steps needed to start the project.",
        deadline="2099-07-30",
        priority=2,
    )

    task1 = Task(
        title="Task A",
        short_desc="Main task of the phase.",
        full_desc="Detailed description of Task A.",
        deadline="2099-07-27",
        priority=2,
    )

    subtask1 = Subtask(
        title="Subtask A1",
        short_desc="A subtask of the main task.",
        full_desc="Detailed descrition of Subtask A1.",
        deadline="2099-07-25",
        priority=3,
        done=False,
    )

    task1.subtasks.append(subtask1)
    phase1.tasks.append(task1)
    demo_project.phases.append(phase1)

    return [demo_project]
