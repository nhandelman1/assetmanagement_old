from assetmanagement.database.dbdict import DBDict
from assetmanagement.modelviews import guiutils


class BusinessMetaTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.init_class()

    ####################################################################################################################
    # Business Meta
    ####################################################################################################################
    def init_class(self):
        self.bus_meta_set_tab_order()
        self.ui.busMetaRefreshButton.clicked.connect(self.bus_meta_refresh_button_clicked)
        self.ui.busMetaBHSICheckbox.toggled.connect(lambda: self.bus_meta_bh_link_group_checked(True))
        self.ui.busMetaBHICCheckbox.toggled.connect(lambda: self.bus_meta_bh_link_group_checked(False))
        self.ui.busMetaBHSCombo.currentIndexChanged.connect(self.bus_meta_bhs_combo_changed)
        self.ui.busMetaBHSButton.clicked.connect(self.bus_meta_bhs_add_up_button_clicked)
        self.ui.busMetaBHICombo.currentIndexChanged.connect(self.bus_meta_bhi_combo_changed)
        self.ui.busMetaBHIButton.clicked.connect(self.bus_meta_bhi_add_up_button_clicked)
        self.ui.busMetaBHCCombo.currentIndexChanged.connect(self.bus_meta_bhc_combo_changed)
        self.ui.busMetaBHCButton.clicked.connect(self.bus_meta_bhc_add_up_button_clicked)
        self.ui.busMetaBHAttButton.clicked.connect(lambda: self.bus_meta_bh_link_changed(True))
        self.ui.busMetaBHDetButton.clicked.connect(lambda: self.bus_meta_bh_link_changed(False))

    def bus_meta_set_tab_order(self):
        pass

    def bus_meta_refresh_button_clicked(self):
        guiutils.combobox_dict_refresh(self.ui.busMetaBHSCombo, self.db.read_sector())
        guiutils.combobox_dict_refresh(self.ui.busMetaBHICombo, self.db.read_industry())
        guiutils.combobox_dict_refresh(self.ui.busMetaBHCCombo, self.db.read_company())

    def bus_meta_bhs_combo_changed(self, index):
        guiutils.combo_changed(self.ui.busMetaBHSCombo.itemData(index),
                               [[self.ui.busMetaBHSField, "name"], [self.ui.busMetaBHNotesArea, "notes"]])
        self.bus_meta_bh_table_populate(self.ui.busMetaBHSCombo, self.db.read_sector_hier)

    def bus_meta_bhs_add_up_button_clicked(self):
        db_dict = self.db.sector_db_dict(
            [guiutils.combo_data(self.ui.busMetaBHSCombo)[0], self.ui.busMetaBHSField.text(),
             self.ui.busMetaBHNotesArea.toPlainText()], [[], [''], []])
        guiutils.add_up_button_clicked(self.ui.busMetaBHSCombo, db_dict, self.db.insert_sector, self.db.update_sector,
                                       self.db.read_sector)

    def bus_meta_bhi_combo_changed(self, index):
        guiutils.combo_changed(self.ui.busMetaBHICombo.itemData(index),
                               [[self.ui.busMetaBHIField, "name"], [self.ui.busMetaBHNotesArea, "notes"]])
        self.bus_meta_bh_table_populate(self.ui.busMetaBHICombo, self.db.read_industry_hier)

    def bus_meta_bhi_add_up_button_clicked(self):
        vals = guiutils.combo_data(self.ui.busMetaBHICombo, ["id", "sector_id"])
        db_dict = self.db.industry_db_dict(
            [vals[0], self.ui.busMetaBHIField.text(), vals[1], self.ui.busMetaBHNotesArea.toPlainText()],
            [[], [''], [], []])
        guiutils.add_up_button_clicked(self.ui.busMetaBHICombo, db_dict, self.db.insert_industry,
                                       self.db.update_industry,
                                       self.db.read_industry)

    def bus_meta_bhc_combo_changed(self, index):
        guiutils.combo_changed(self.ui.busMetaBHCCombo.itemData(index),
                               [[self.ui.busMetaBHCField, "name"], [self.ui.busMetaBHNotesArea, "notes"]])
        self.bus_meta_bh_table_populate(self.ui.busMetaBHCCombo, self.db.read_company_hier)

    def bus_meta_bhc_add_up_button_clicked(self):
        db_dict = self.db.company_db_dict(
            [guiutils.combo_data(self.ui.busMetaBHCCombo)[0], self.ui.busMetaBHCField.text(),
             self.ui.busMetaBHNotesArea.toPlainText()], [[], [''], []])
        guiutils.add_up_button_clicked(self.ui.busMetaBHCCombo, db_dict, self.db.insert_company, self.db.update_company,
                                       self.db.read_company)

    def bus_meta_bh_table_populate(self, combo, query):
        if combo.currentText() == '':
            self.ui.busMetaBHSICTable.setRowCount(0)
        else:
            guiutils.populate_table(self.ui.busMetaBHSICTable, dict_list=query(DBDict(val_dict=combo.currentData())))

    def bus_meta_bh_link_group_checked(self, is_sector_industry):
        if is_sector_industry and self.ui.busMetaBHSICheckbox.isChecked():
            self.ui.busMetaBHICCheckbox.setChecked(False)
            guiutils.set_disabled(False, self.ui.busMetaBHAttButton, self.ui.busMetaBHDetButton)
        elif not is_sector_industry and self.ui.busMetaBHICCheckbox.isChecked():
            self.ui.busMetaBHSICheckbox.setChecked(False)
            guiutils.set_disabled(False, self.ui.busMetaBHAttButton, self.ui.busMetaBHDetButton)
        else:
            guiutils.set_disabled(True, self.ui.busMetaBHAttButton, self.ui.busMetaBHDetButton)

    def bus_meta_bh_link_changed(self, is_attach):
        if self.ui.busMetaBHICombo.currentText() == '':
            self.ui.busMetaBHSICheckbox.setChecked(False)
            self.ui.busMetaBHICCheckbox.setChecked(False)
            return

        if self.ui.busMetaBHSICheckbox.isChecked() and self.ui.busMetaBHSCombo.currentText() != '':
            if is_attach:
                self.bus_meta_bhsi_link_changed(guiutils.combo_data(self.ui.busMetaBHSCombo)[0])
            else:
                self.bus_meta_bhsi_link_changed(None)
        elif self.ui.busMetaBHICCheckbox.isChecked() and self.ui.busMetaBHCCombo.currentText() != '':
            if is_attach:
                self.bus_meta_bhic_link_changed(self.db.attach_industry_company)
            else:
                self.bus_meta_bhic_link_changed(self.db.detach_industry_company)

        self.ui.busMetaBHSICheckbox.setChecked(False)
        self.ui.busMetaBHICCheckbox.setChecked(False)

    def bus_meta_bhsi_link_changed(self, new_sector_id):
        db_dict = self.db.industry_db_dict([guiutils.combo_data(self.ui.busMetaBHICombo)[0], None, new_sector_id, None])
        res = self.db.update_industry(db_dict)

        if res is None:
            self.ui.busMetaBHICombo.setCurrentIndex(0)
            self.bus_meta_bhs_combo_changed(self.ui.busMetaBHSCombo.currentIndex())
        else:
            guiutils.show_error_msg("Insert/Update Error", res)

    def bus_meta_bhic_link_changed(self, query):
        db_dict = self.db.company_industry_db_dict([None, guiutils.combo_data(self.ui.busMetaBHCCombo)[0],
                                                    guiutils.combo_data(self.ui.busMetaBHICombo)[0]])
        res = query(db_dict)

        if res is None:
            self.ui.busMetaBHCCombo.setCurrentIndex(0)
            self.bus_meta_bhi_combo_changed(self.ui.busMetaBHICombo.currentIndex())
        else:
            guiutils.show_error_msg("Insert/Update Error", res)