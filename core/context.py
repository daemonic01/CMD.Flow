from ui.common.main_logo_utils import load_logo
from utils.data_io import load_projects_from_file

class UIState:
    def __init__(self):
        self.footer = None
        self.messages = []
        self.screen = {"rows": 0, "cols": 0}
        self.version = "v0.4.0-pre9"
        self.build = "N/A"
        self.logos = load_logo()
        self.compact = {
            "menu": False,
            "main": False,
            "form": False,
            "changelog": False
        }


class ControlState:
    def __init__(self):
        self.mode = "menu"
        self.focus = "main"
        self.prev_mode = None
        self.last_focus = None
        self.screen_changed = False
        self.layout_blocked = False


class SelectionState:
    def __init__(self):
        self.level = "project"
        self.idx = 0
        self.selected_project = None
        self.selected_phase = None
        self.selected_task = None


class LayoutConfig:
    def __init__(self):
        self.has_header = True
        self.has_footer = True
        self.header_height = 12
        self.footer_height = 4
        self.middle_split = [0.5, 0.5]
        self.project_card_height = 8
        self.project_cards_spacing = 1
        self.selected_panel_border = ["|", "|", "-", "-", "+", "+", "+", "+"]

        self.field_max_lengths = {
            "title": 50,
            "short_desc": 80,
            "full_desc": 400,
            "deadline": 10,
            "priority": 1
        }

        self.layout_profiles = {
            "menu": {"min_rows": 30, "min_cols": 90},
            "main": {"min_rows": 25, "min_cols": 80},
            "form": {"min_rows": 22, "min_cols": 60}
        }


class AppConfig:
    def __init__(self):
        self.theme = "default"
        self.lang = "en"
        self.log_max_lines = 10


class AppContext:
    def __init__(self):
        self.data = {
            "projects": load_projects_from_file()
        }
        self.selection = SelectionState()
        self.control = ControlState()
        self.ui = UIState()
        self.layout = LayoutConfig()
        self.config = AppConfig()
