class BaseView:
    def __init__(self, ctx):
        self.ctx = ctx

    def render(self, stdscr):
        raise NotImplementedError()

    def handle_input(self, key):
        return None