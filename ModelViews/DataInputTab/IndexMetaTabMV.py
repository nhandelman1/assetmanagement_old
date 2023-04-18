from ModelViews import GUIUtils
from Database.DBDict import DBDict
from PyQt5 import QtCore


class IndexMetaTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.init_class()

    def init_class(self):
        self.index_meta_set_tab_order()

        self.ui.indexMetaIndexTable.horizontalHeader().setSectionResizeMode(0, 2)
        self.ui.indexMetaIndexTable.setColumnWidth(0, 0)
        self.ui.indexMetaIndexTable.setColumnWidth(2, 300)
        self.ui.indexMetaIndexTable.setColumnWidth(3, 300)

        self.ui.indexMetaRefreshButton.clicked.connect(self.index_meta_refresh_button_clicked)
        self.ui.indexMetaSTCombo.currentIndexChanged.connect(self.index_meta_st_combo_changed)

        self.ui.indexMetaAttachButton.clicked.connect(lambda: GUIUtils.sec_sec_attach_detach_button_clicked(
            self.ui.indexMetaSecurityTable.selectedItems(), self.ui.indexMetaIndexTable, True, self.db,
            self.ui.indexMetaIndexCompTable))

        self.ui.indexMetaDetachButton.clicked.connect(lambda: GUIUtils.sec_sec_attach_detach_button_clicked(
            self.ui.indexMetaIndexCompTable.selectedItems(), self.ui.indexMetaIndexTable, False, self.db,
            self.ui.indexMetaIndexCompTable))

        self.ui.indexMetaIndexInsertButton.clicked.connect(self.index_meta_index_insert_update_button_clicked)
        self.ui.indexMetaUpdateButton.clicked.connect(self.index_meta_index_insert_update_button_clicked)
        self.ui.indexMetaIndexTable.itemSelectionChanged.connect(self.index_meta_index_table_item_changed)
        self.ui.indexMetaIndexCompTable.itemSelectionChanged.connect(self.index_meta_index_comp_table_item_changed)

        self.index_meta_tab_clear()

    def index_meta_set_tab_order(self):
        pass

    def index_meta_tab_clear(self):
        GUIUtils.clear(self.ui.indexMetaTickerField, self.ui.indexMetaNameField, self.ui.indexMetaCompanyCombo,
                       self.ui.indexMetaSTCombo, self.ui.indexMetaSecurityTable, self.ui.indexMetaIndexCompTable,
                       self.ui.indexMetaIndexTable)
        GUIUtils.set_disabled(True, self.ui.indexMetaAttachButton, self.ui.indexMetaDetachButton,
                              self.ui.indexMetaIndexCompTable, self.ui.indexMetaIndexInsertButton,
                              self.ui.indexMetaUpdateButton, self.ui.indexMetaIndexTable)

    def index_meta_refresh_button_clicked(self):
        self.index_meta_tab_clear()

        GUIUtils.combobox_dict_refresh(self.ui.indexMetaCompanyCombo, self.db.read_company())
        GUIUtils.combobox_dict_refresh(self.ui.indexMetaSTCombo, self.db.read_security_subtypes())
        GUIUtils.set_disabled(False, self.ui.indexMetaIndexInsertButton, self.ui.indexMetaIndexTable)
        GUIUtils.populate_table(self.ui.indexMetaIndexTable, self.db.read_indices())

    def index_meta_st_combo_changed(self, index):
        self.ui.indexMetaSecurityTable.setRowCount(0)

        item_data = self.ui.indexMetaSTCombo.currentData()
        if item_data is not None:
            db_dict = self.db.data_meta_table_db_dict([item_data["db_table_meta"]])
            GUIUtils.populate_table(self.ui.indexMetaSecurityTable,
                                    self.db.read_data_subtype_meta_table(db_dict), ["ticker"])

    def index_meta_index_insert_update_button_clicked(self):
        if len(self.ui.indexMetaIndexTable.selectedItems()) == 0:
            index_id = None
        else:
            index_id = self.ui.indexMetaIndexTable.selectedItems()[0].text()

        db_dict = self.db.index_db_dict(
            [index_id, self.ui.indexMetaTickerField.text(), self.ui.indexMetaNameField.text(),
             GUIUtils.combo_data(self.ui.indexMetaCompanyCombo)[0]], [[], [''], [], []])

        GUIUtils.add_up_button_clicked(self.ui.indexMetaIndexTable, db_dict, self.db.insert_index, self.db.update_index,
                                       self.db.read_indices)

    def index_meta_index_table_item_changed(self):
        selected_items = self.ui.indexMetaIndexTable.selectedItems()
        if len(selected_items) == 0:
            self.ui.indexMetaIndexInsertButton.setEnabled(True)
            GUIUtils.set_disabled(True, self.ui.indexMetaAttachButton, self.ui.indexMetaUpdateButton,
                                  self.ui.indexMetaIndexCompTable)
            GUIUtils.clear(self.ui.indexMetaIndexCompTable, self.ui.indexMetaTickerField, self.ui.indexMetaNameField)
        else:
            GUIUtils.set_disabled(False, self.ui.indexMetaAttachButton, self.ui.indexMetaUpdateButton,
                                  self.ui.indexMetaIndexCompTable)
            self.ui.indexMetaIndexInsertButton.setEnabled(False)
            self.ui.indexMetaTickerField.setText(selected_items[1].text())
            self.ui.indexMetaNameField.setText(selected_items[2].text())
            GUIUtils.set_current_index(self.ui.indexMetaCompanyCombo, selected_items[3].text())
            GUIUtils.populate_table(self.ui.indexMetaIndexCompTable,
                                    self.db.read_security_components(
                                        DBDict(val_dict=selected_items[0].data(QtCore.Qt.UserRole))),
                                    ["ticker"])

    def index_meta_index_comp_table_item_changed(self):
        selected_items = self.ui.indexMetaIndexCompTable.selectedItems()
        self.ui.indexMetaDetachButton.setEnabled(len(selected_items) > 0)