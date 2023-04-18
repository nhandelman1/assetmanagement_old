from ModelViews import GUIUtils
from Database.DBDict import DBDict


class GeneralTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.init_class()

    def init_class(self):
        self.gen_set_tab_order()
        self.ui.genRefreshButton.clicked.connect(self.gen_refresh_button_clicked)
        self.ui.genDSCombo.currentIndexChanged.connect(self.gen_ds_combo_changed)
        self.ui.genDSAddUpButton.clicked.connect(self.gen_ds_add_up_button_clicked)
        self.ui.genRCRCombo.currentIndexChanged.connect(self.gen_rcr_combo_changed)
        self.ui.genRCRAddUpButton.clicked.connect(self.gen_rcr_add_up_button_clicked)
        self.ui.genRCCCombo.currentIndexChanged.connect(self.gen_rcc_combo_changed)
        self.ui.genRCCAddUpButton.clicked.connect(self.gen_rcc_add_up_button_clicked)
        self.ui.genRCAttButton.clicked.connect(lambda: self.gen_rc_link_changed(self.db.attach_region_country))
        self.ui.genRCDetButton.clicked.connect(lambda: self.gen_rc_link_changed(self.db.detach_region_country))
        self.ui.genECCombo.currentIndexChanged.connect(self.gen_ec_combo_changed)
        self.ui.genECAddUpButton.clicked.connect(self.gen_ec_add_up_button_clicked)

    def gen_set_tab_order(self):
        self.ui.genRCRCombo.setTabOrder(self.ui.genRCRCombo, self.ui.genRCRField)
        self.ui.genRCRField.setTabOrder(self.ui.genRCRField, self.ui.genRCRNotesArea)
        self.ui.genRCRNotesArea.setTabOrder(self.ui.genRCRNotesArea, self.ui.genRCCCombo)
        self.ui.genRCCCombo.setTabOrder(self.ui.genRCCCombo, self.ui.genRCCField)
        self.ui.genRCCField.setTabOrder(self.ui.genRCCField, self.ui.genRCCNotesArea)
        self.ui.genRCCNotesArea.setTabOrder(self.ui.genRCCNotesArea, self.ui.genDSCombo)
        self.ui.genDSCombo.setTabOrder(self.ui.genDSCombo, self.ui.genDSNameField)
        self.ui.genDSNameField.setTabOrder(self.ui.genDSNameField, self.ui.genDSNotesArea)
        self.ui.genDSNotesArea.setTabOrder(self.ui.genDSNotesArea, self.ui.genECCombo)
        self.ui.genECCombo.setTabOrder(self.ui.genECCombo, self.ui.genECNameField)
        self.ui.genECNameField.setTabOrder(self.ui.genECNameField, self.ui.genECNotesArea)
        self.ui.genECNotesArea.setTabOrder(self.ui.genECNotesArea, self.ui.genRCRCombo)

    def gen_refresh_button_clicked(self):
        GUIUtils.combobox_dict_refresh(self.ui.genDSCombo, self.db.read_data_source())
        GUIUtils.combobox_dict_refresh(self.ui.genRCRCombo, self.db.read_region())
        GUIUtils.combobox_dict_refresh(self.ui.genRCCCombo, self.db.read_country())
        GUIUtils.combobox_dict_refresh(self.ui.genECCombo, self.db.read_etf_categories())

    def gen_ds_combo_changed(self, index):
        GUIUtils.combo_changed(self.ui.genDSCombo.itemData(index),
                               [[self.ui.genDSNameField, "name"], [self.ui.genDSNotesArea, "notes"]])

    def gen_ds_add_up_button_clicked(self):
        db_dict = self.db.data_source_db_dict([GUIUtils.combo_data(self.ui.genDSCombo)[0],
                                               self.ui.genDSNameField.text(), self.ui.genDSNotesArea.text()],
                                              [[], [''], []])
        GUIUtils.add_up_button_clicked(self.ui.genDSCombo, db_dict, self.db.insert_data_source,
                                       self.db.update_data_source, self.db.read_data_source)

    def gen_rcr_combo_changed(self, index):
        GUIUtils.combo_changed(self.ui.genRCRCombo.itemData(index),
                               [[self.ui.genRCRField, "name"], [self.ui.genRCRNotesArea, "notes"]])
        self.gen_rc_table_populate(self.ui.genRCRCombo.currentData(), "name", self.db.read_country)

    def gen_rcr_add_up_button_clicked(self):
        db_dict = self.db.region_db_dict(
            [GUIUtils.combo_data(self.ui.genRCRCombo)[0], self.ui.genRCRField.text(), self.ui.genRCRNotesArea.text()],
            [[], [''], []])
        GUIUtils.add_up_button_clicked(self.ui.genRCRCombo, db_dict, self.db.insert_region, self.db.update_region,
                                       self.db.read_region)

    def gen_rcc_combo_changed(self, index):
        GUIUtils.combo_changed(self.ui.genRCCCombo.itemData(index),
                               [[self.ui.genRCCField, "name"], [self.ui.genRCCNotesArea, "notes"]])
        self.gen_rc_table_populate(self.ui.genRCCCombo.currentData(), "name", self.db.read_region)

    def gen_rcc_add_up_button_clicked(self):
        db_dict = self.db.country_db_dict(
            [GUIUtils.combo_data(self.ui.genRCCCombo)[0], self.ui.genRCCField.text(), self.ui.genRCCNotesArea.text()],
            [[], [''], []])
        GUIUtils.add_up_button_clicked(self.ui.genRCCCombo, db_dict, self.db.insert_country, self.db.update_country,
                                       self.db.read_country)

    def gen_rc_table_populate(self, item_data_dict, header_key, read_query):
        if item_data_dict is None:
            header = ''
        else:
            header = item_data_dict[header_key]

        self.ui.genRCTable.setHorizontalHeaderLabels([header])

        if header == '':
            self.ui.genRCTable.setRowCount(0)
        else:
            GUIUtils.populate_table(self.ui.genRCTable, dict_list=read_query(DBDict(val_dict=item_data_dict)))

    def gen_rc_link_changed(self, query):
        if self.ui.genRCRCombo.currentText() == '' or self.ui.genRCCCombo.currentText() == '':
            return

        res = query(self.db.region_country_db_dict([None, self.ui.genRCRCombo.currentData()["id"],
                                                    self.ui.genRCCCombo.currentData()["id"]]))

        if res is None:
            self.gen_rcr_combo_changed(self.ui.genRCRCombo.currentIndex())
        else:
            GUIUtils.show_error_msg("Insert/Update Error", res)

    def gen_ec_combo_changed(self, index):
        GUIUtils.combo_changed(self.ui.genECCombo.itemData(index),
                               [[self.ui.genECNameField, "name"], [self.ui.genECNotesArea, "notes"]])

    def gen_ec_add_up_button_clicked(self):
        db_dict = self.db.etf_category_db_dict([GUIUtils.combo_data(self.ui.genECCombo)[0],
                                                self.ui.genECNameField.text(), self.ui.genECNotesArea.text()],
                                               [[], [''], []])
        GUIUtils.add_up_button_clicked(self.ui.genECCombo, db_dict, self.db.insert_etf_category,
                                       self.db.update_etf_category, self.db.read_etf_categories)