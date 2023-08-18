from PyQt5 import QtWidgets
from modelviews.maingui import Ui_MainWindow  # importing our generated file
from database.mysqlold import MySQLOld
from modelviews.menubarmv import MenuBarMV
from modelviews.datainputtab.datainputtabmv import DataInputTabMV
from modelviews.statisticstab.statisticstabmv import StatisticsTabMV


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
