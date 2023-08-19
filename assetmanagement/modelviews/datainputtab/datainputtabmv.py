from .generaltabmv import GeneralTabMV
from .businessmetatabmv import BusinessMetaTabMV
from .indexmetatabmv import IndexMetaTabMV
from .stockmetatabmv import StockMetaTabMV
from .etfmetatabmv import ETFMetaTabMV
from .seidatatabmv import SEIDataTabMV
from .iexcloudtabmv import IEXCloudTabMV


class DataInputTabMV:

    def __init__(self, main_window, ui, db):
        self.main_window = main_window
        self.ui = ui
        self.db = db

        self.init_class()

        self.gen_tab_mv = GeneralTabMV(ui, db)
        self.bus_meta_tab_mv = BusinessMetaTabMV(ui, db)
        self.index_meta_tab_mv = IndexMetaTabMV(ui, db)
        self.stock_meta_tab_mv = StockMetaTabMV(ui, db)
        self.etf_meta_tab_mv = ETFMetaTabMV(ui, db)
        self.sei_data_tab_mv = SEIDataTabMV(ui, db)
        self.iex_cloud_tab_mv = IEXCloudTabMV(ui, db)

    def init_class(self):
        self.ui.dataInputTabWidget.currentChanged.connect(self.di_tab_changed)

    def di_tab_changed(self, index):
        if index == 0:  # General Tab
            self.ui.genRCRCombo.setFocus()
        elif index == 1:  # Business Meta Tab
            self.ui.busMetaBHSCombo.setFocus()
        elif index == 2:  # Index Meta Tab
            self.ui.indexMetaTickerField.setFocus()
        elif index == 3:  # Stock Meta Tab
            self.ui.stockMetaTickerField.setFocus()
        elif index == 4:  # ETF Meta Tab
            self.ui.etfMetaTickerField.setFocus()
        elif index == 5:  # SEI P/W Tab
            self.ui.seiDataSTCombo.setFocus()