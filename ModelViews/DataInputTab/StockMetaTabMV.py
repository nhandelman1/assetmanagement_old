from ModelViews import GUIUtils


class StockMetaTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.init_class()

    def init_class(self):
        self.stock_meta_set_tab_order()

        self.ui.stockMetaTable.horizontalHeader().setSectionResizeMode(0, 2)
        self.ui.stockMetaTable.setColumnWidth(0, 0)
        self.ui.stockMetaTable.setColumnWidth(2, 300)

        self.ui.stockMetaRefreshButton.clicked.connect(self.stock_meta_refresh_button_clicked)
        self.ui.stockMetaInsertButton.clicked.connect(self.stock_meta_insert_update_button_clicked)
        self.ui.stockMetaUpdateButton.clicked.connect(self.stock_meta_insert_update_button_clicked)
        self.ui.stockMetaTable.itemSelectionChanged.connect(self.stock_meta_table_item_changed)
        self.stock_meta_tab_clear()

    def stock_meta_set_tab_order(self):
        pass

    def stock_meta_tab_clear(self):
        GUIUtils.clear(self.ui.stockMetaTickerField, self.ui.stockMetaCompanyField, self.ui.stockMetaCompanyCombo,
                       self.ui.stockMetaTable)
        GUIUtils.set_disabled(True, self.ui.stockMetaInsertButton, self.ui.stockMetaUpdateButton,
                              self.ui.stockMetaTable)

    def stock_meta_refresh_button_clicked(self):
        self.stock_meta_tab_clear()

        GUIUtils.combobox_dict_refresh(self.ui.stockMetaCompanyCombo, self.db.read_company())
        GUIUtils.set_disabled(False, self.ui.stockMetaInsertButton, self.ui.stockMetaTable)
        GUIUtils.populate_table(self.ui.stockMetaTable, self.db.read_stocks())

    def stock_meta_insert_update_button_clicked(self):
        if len(self.ui.stockMetaTable.selectedItems()) == 0:
            id = None
        else:
            id = self.ui.stockMetaTable.selectedItems()[0].text()

        db_dict = self.db.stock_db_dict([id, self.ui.stockMetaTickerField.text(),
                                         GUIUtils.combo_data(self.ui.stockMetaCompanyCombo)[0]], [[], [''], []])

        GUIUtils.add_up_button_clicked(self.ui.stockMetaTable, db_dict, self.db.insert_stock, self.db.update_stock,
                                       self.db.read_stocks)

    def stock_meta_table_item_changed(self):
        selected_items = self.ui.stockMetaTable.selectedItems()
        if len(selected_items) == 0:
            GUIUtils.clear(self.ui.stockMetaTickerField, self.ui.stockMetaCompanyField)
            self.ui.stockMetaInsertButton.setEnabled(True)
            self.ui.stockMetaUpdateButton.setEnabled(False)
        else:
            self.ui.stockMetaInsertButton.setEnabled(False)
            self.ui.stockMetaUpdateButton.setEnabled(True)
            self.ui.stockMetaTickerField.setText(selected_items[1].text())
            self.ui.stockMetaCompanyField.setText(selected_items[2].text())
            GUIUtils.set_current_index(self.ui.stockMetaCompanyCombo, selected_items[2].text())