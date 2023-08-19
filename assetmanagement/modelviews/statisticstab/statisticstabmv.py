from .dataexploretabmv import DataExploreTabMV
from .dataselectiontabmv import DataSelectionTabMV
from .regressionmv import RegressionMV


class StatisticsTabMV:

    def __init__(self, main_window, ui, db):
        self.main_window = main_window
        self.ui = ui
        self.db = db

        self.init_class()

        self.data_selection_tab_mv = DataSelectionTabMV(ui, db)
        self.data_explore_tab_mv = DataExploreTabMV(ui, db, self)
        self.data_regression_tab_mv = RegressionMV(ui, db, self)

    def init_class(self):
        self.ui.statsTabWidget.currentChanged.connect(self.stats_tab_changed)

    def stats_tab_changed(self, index):
        if index == 0:  # Data Selection Tab
            pass

    def get_data_selection_tab_tables_data(self, ignore_verify=False, dep=True, indep=True, raa=True, other=True):
        return self.data_selection_tab_mv.get_data_from_tables_external(ignore_verify, dep, indep, raa, other)