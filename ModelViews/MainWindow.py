from PyQt5 import QtWidgets
from ModelViews.MainGUI import Ui_MainWindow  # importing our generated file
from Database.MySQLOld import MySQLOld
from ModelViews.MenuBarMV import MenuBarMV
from ModelViews.DataInputTab.DataInputTabMV import DataInputTabMV
from ModelViews.StatisticsTab.StatisticsTabMV import StatisticsTabMV


class MainWindow(QtWidgets.QMainWindow):

    ########################################################################################################################
    # init
    ########################################################################################################################
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = MySQLOld()

        self.menu_bar_mv = MenuBarMV(self, self.ui, self.db)

        self.di_tab_mv = DataInputTabMV(self, self.ui, self.db)
        self.stats_tab_mv = StatisticsTabMV(self, self.ui, self.db)

    ########################################################################################################################
    # overrides
    ########################################################################################################################
    def closeEvent(self, event):
        super()
        self.db.db_close()
