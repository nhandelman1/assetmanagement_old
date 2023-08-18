
class MenuBarMV:

    def __init__(self, main_window, ui, db):
        self.main_window = main_window
        self.ui = ui
        self.db = db

        self.init_class()

    def init_class(self):
        self.ui.actionExit.triggered.connect(lambda: self.main_window.close())