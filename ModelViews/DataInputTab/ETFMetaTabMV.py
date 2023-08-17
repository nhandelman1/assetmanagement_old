from ModelViews import GUIUtils
from PyQt5 import QtCore
from Database.DBDict import DBDict
from Database.MySQLOld import ETFDataTypes
import datetime


class ETFMetaTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.init_class()

    def init_class(self):
        self.etf_meta_set_tab_order()

        self.ui.etfMetaTable.horizontalHeader().setSectionResizeMode(0, 2)
        self.ui.etfMetaTable.setColumnWidth(0, 0)
        self.ui.etfMetaTable.setColumnWidth(2, 200)
        self.ui.etfMetaTable.setColumnWidth(3, 150)
        self.ui.etfMetaTable.setColumnWidth(4, 200)
        self.ui.etfMetaTable.setColumnWidth(6, 50)
        self.ui.etfMetaTable.setColumnWidth(7, 50)

        self.ui.etfMetaRefreshButton.clicked.connect(self.etf_meta_refresh_button_clicked)
        self.ui.etfMetaAssetClassCombo.currentIndexChanged.connect(self.etf_meta_asset_class_combo_changed)
        self.ui.etfMetaRegionCombo.currentIndexChanged.connect(self.etf_meta_region_combo_changed)
        self.ui.etfMetaSectorCombo.currentIndexChanged.connect(self.etf_meta_sector_combo_changed)
        self.ui.etfMetaSTCombo.currentIndexChanged.connect(self.etf_meta_st_combo_changed)

        self.ui.etfMetaAttachButton.clicked.connect(lambda: GUIUtils.sec_sec_attach_detach_button_clicked(
            self.ui.etfMetaSecurityTable.selectedItems(), self.ui.etfMetaTable, True, self.db,
            self.ui.etfMetaEtfCompTable))

        self.ui.etfMetaDetachButton.clicked.connect(lambda: GUIUtils.sec_sec_attach_detach_button_clicked(
            self.ui.etfMetaEtfCompTable.selectedItems(), self.ui.etfMetaTable, False, self.db,
            self.ui.etfMetaEtfCompTable))

        self.ui.etfMetaInsertButton.clicked.connect(self.etf_meta_etf_insert_update_button_clicked)
        self.ui.etfMetaUpdateButton.clicked.connect(self.etf_meta_etf_insert_update_button_clicked)
        self.ui.etfMetaTable.itemSelectionChanged.connect(self.etf_meta_etf_table_item_changed)
        self.ui.etfMetaEtfCompTable.itemSelectionChanged.connect(self.etf_meta_etf_comp_table_item_changed)
        self.ui.etfMetaClearButton.clicked.connect(lambda: GUIUtils.layout_reset(self.ui.etfMetaSearchGrid))
        self.ui.etfMetaSearchButton.clicked.connect(self.etf_meta_search_button_clicked)

        self.etf_meta_tab_clear()

    def etf_meta_set_tab_order(self):
        self.ui.etfMetaTickerField.setTabOrder(self.ui.etfMetaTickerField, self.ui.etfMetaNameField)
        self.ui.etfMetaNameField.setTabOrder(self.ui.etfMetaNameField, self.ui.etfMetaAssetClassCombo)
        self.ui.etfMetaAssetClassCombo.setTabOrder(self.ui.etfMetaAssetClassCombo, self.ui.etfMetaCompanyCombo)
        self.ui.etfMetaCompanyCombo.setTabOrder(self.ui.etfMetaCompanyCombo, self.ui.etfMetaIndexCombo)
        self.ui.etfMetaIndexCombo.setTabOrder(self.ui.etfMetaIndexCombo, self.ui.etfMetaLevSpin)
        self.ui.etfMetaLevSpin.setTabOrder(self.ui.etfMetaLevSpin, self.ui.etfMetaFeeSpin)
        self.ui.etfMetaFeeSpin.setTabOrder(self.ui.etfMetaFeeSpin, self.ui.etfMetaIncepField)
        self.ui.etfMetaIncepField.setTabOrder(self.ui.etfMetaIncepField, self.ui.etfMetaCategoryCombo)
        self.ui.etfMetaCategoryCombo.setTabOrder(self.ui.etfMetaCategoryCombo, self.ui.etfMetaRegionCombo)
        self.ui.etfMetaRegionCombo.setTabOrder(self.ui.etfMetaRegionCombo, self.ui.etfMetaCountryCombo)
        self.ui.etfMetaCountryCombo.setTabOrder(self.ui.etfMetaCountryCombo, self.ui.etfMetaSectorCombo)
        self.ui.etfMetaSectorCombo.setTabOrder(self.ui.etfMetaSectorCombo, self.ui.etfMetaIndustryCombo)
        self.ui.etfMetaIndustryCombo.setTabOrder(self.ui.etfMetaIndustryCombo, self.ui.etfMetaAssetSizeCombo)
        self.ui.etfMetaAssetSizeCombo.setTabOrder(self.ui.etfMetaAssetSizeCombo, self.ui.etfMetaAssetStyleCombo)
        self.ui.etfMetaAssetStyleCombo.setTabOrder(self.ui.etfMetaAssetStyleCombo, self.ui.etfMetaBondTypeCombo)
        self.ui.etfMetaBondTypeCombo.setTabOrder(self.ui.etfMetaBondTypeCombo, self.ui.etfMetaBondDurCombo)
        self.ui.etfMetaBondDurCombo.setTabOrder(self.ui.etfMetaBondDurCombo, self.ui.etfMetaCommTypeCombo)
        self.ui.etfMetaCommTypeCombo.setTabOrder(self.ui.etfMetaCommTypeCombo, self.ui.etfMetaCommCombo)
        self.ui.etfMetaCommCombo.setTabOrder(self.ui.etfMetaCommCombo, self.ui.etfMetaCommExpoCombo)
        self.ui.etfMetaCommExpoCombo.setTabOrder(self.ui.etfMetaCommExpoCombo, self.ui.etfMetaCurrCombo)
        self.ui.etfMetaCurrCombo.setTabOrder(self.ui.etfMetaCurrCombo, self.ui.etfMetaSTCombo)
        self.ui.etfMetaSTCombo.setTabOrder(self.ui.etfMetaSTCombo, self.ui.etfMetaTickerField)

    def etf_meta_tab_clear(self):
        GUIUtils.clear(self.ui.etfMetaTickerField, self.ui.etfMetaNameField, self.ui.etfMetaAssetClassCombo,
                       self.ui.etfMetaCompanyCombo, self.ui.etfMetaIndexCombo, self.ui.etfMetaCategoryCombo,
                       self.ui.etfMetaSecurityTable, self.ui.etfMetaEtfCompTable, self.ui.etfMetaTable)
        self.ui.etfMetaLevSpin.setValue(0)
        self.ui.etfMetaFeeSpin.setValue(0)
        self.ui.etfMetaIncepField.setDate(QtCore.QDate(1900, 1, 1))
        GUIUtils.set_disabled(True, self.ui.etfMetaAttachButton, self.ui.etfMetaDetachButton,
                              self.ui.etfMetaEtfCompTable, self.ui.etfMetaInsertButton, self.ui.etfMetaUpdateButton,
                              self.ui.etfMetaTable, self.ui.etfMetaSearchButton)
        GUIUtils.layout_reset(self.ui.etfMetaSearchGrid)

    def etf_meta_refresh_button_clicked(self):
        self.etf_meta_tab_clear()

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaAssetClassCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.ASSET_CLASS))

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaCompanyCombo, self.db.read_company())
        GUIUtils.combobox_dict_refresh(self.ui.etfMetaIndexCombo, self.db.read_indices(), "ticker")
        GUIUtils.combobox_dict_refresh(self.ui.etfMetaCategoryCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.CATEGORIES), tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaRegionCombo, self.db.read_region())
        GUIUtils.combobox_dict_refresh(self.ui.etfMetaAssetSizeCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.ASSET_CLASS_SIZE),
                                       tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaAssetStyleCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.ASSET_CLASS_STYLE),
                                       tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaSectorCombo, self.db.read_sector())
        GUIUtils.combobox_dict_refresh(self.ui.etfMetaBondTypeCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.BOND_TYPE),
                                       tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaBondDurCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.BOND_DURATION), tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaCommTypeCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.COMMODITY_TYPE),
                                       tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaCommCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.COMMODITY), tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaCommExpoCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.COMMODITY_EXPOSURE),
                                       tool_tip_key="notes")

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaCurrCombo,
                                       self.db.read_etf_data_type(ETFDataTypes.CURRENCY_TYPE), tool_tip_key="notes")
        GUIUtils.combobox_dict_refresh(self.ui.etfMetaSTCombo, self.db.read_security_subtypes())

        GUIUtils.set_disabled(False, self.ui.etfMetaInsertButton, self.ui.etfMetaTable, self.ui.etfMetaSearchButton)

        GUIUtils.populate_table(self.ui.etfMetaTable, self.db.read_etfs())

    def etf_meta_asset_class_combo_changed(self):
        GUIUtils.set_disabled(True, self.ui.etfMetaSecIndFrame, self.ui.etfMetaAssetFrame, self.ui.etfMetaBondFrame,
                              self.ui.etfMetaCommFrame, self.ui.etfMetaCurrFrame)

        asset_class = GUIUtils.combo_data(self.ui.etfMetaAssetClassCombo, ("name",))[0]

        if asset_class != "Bonds":
            GUIUtils.layout_reset(self.ui.etfMetaBondGrid)
        if asset_class != "Commodity":
            GUIUtils.layout_reset(self.ui.etfMetaCommGrid)
        if asset_class != "Currency":
            GUIUtils.layout_reset(self.ui.etfMetaCurrGrid)

        if asset_class is None:
            GUIUtils.set_disabled(False, self.ui.etfMetaSecIndFrame, self.ui.etfMetaAssetFrame,
                                  self.ui.etfMetaBondFrame, self.ui.etfMetaCommFrame, self.ui.etfMetaCurrFrame)
        elif asset_class in ["Alternatives", "Equities", "Preferred Stocks", "Real Estate"]:
            GUIUtils.set_disabled(False, self.ui.etfMetaSecIndFrame, self.ui.etfMetaAssetFrame)
        elif asset_class == "Bonds":
            GUIUtils.set_disabled(False, self.ui.etfMetaSecIndFrame, self.ui.etfMetaAssetFrame,
                                  self.ui.etfMetaBondFrame)
        elif asset_class == "Commodity":
            self.ui.etfMetaCommFrame.setEnabled(True)
            GUIUtils.layout_reset(self.ui.etfMetaSecIndGrid, self.ui.etfMetaAssetGrid)
        elif asset_class == "Currency":
            self.ui.etfMetaCurrFrame.setEnabled(True)
            GUIUtils.layout_reset(self.ui.etfMetaSecIndGrid, self.ui.etfMetaAssetGrid)
        elif asset_class == "Multi-Assets":
            GUIUtils.set_disabled(False, self.ui.etfMetaAssetFrame)
            GUIUtils.layout_reset(self.ui.etfMetaSecIndGrid)
        elif asset_class == "Volatilities":
            GUIUtils.layout_reset(self.ui.etfMetaSecIndGrid, self.ui.etfMetaAssetGrid)

    def etf_meta_region_combo_changed(self):
        self.ui.etfMetaCountryCombo.clear()

        item_data = self.ui.etfMetaRegionCombo.currentData()
        if item_data is not None:
            GUIUtils.combobox_dict_refresh(self.ui.etfMetaCountryCombo,
                                           self.db.read_country(DBDict(val_dict=item_data)))

    def etf_meta_sector_combo_changed(self):
        self.ui.etfMetaIndustryCombo.clear()

        item_data = self.ui.etfMetaSectorCombo.currentData()

        if item_data is None:
            db_dict = self.db.sector_db_dict([None, None, None, None])
        else:
            db_dict = DBDict(val_dict=item_data)

        GUIUtils.combobox_dict_refresh(self.ui.etfMetaIndustryCombo, self.db.read_industry(db_dict))

    def etf_meta_st_combo_changed(self, index):
        self.ui.etfMetaSecurityTable.setRowCount(0)

        item_data = self.ui.etfMetaSTCombo.currentData()
        if item_data is not None:
            db_dict = self.db.data_meta_table_db_dict([item_data["db_table_meta"]])
            GUIUtils.populate_table(self.ui.etfMetaSecurityTable,
                                    self.db.read_data_subtype_meta_table(db_dict), ["ticker"])

    def etf_meta_etf_insert_update_button_clicked(self):
        if len(self.ui.etfMetaTable.selectedItems()) == 0:
            index_id = None
        else:
            index_id = self.ui.etfMetaTable.selectedItems()[0].text()

        lev, fee, incep, data_lol = self.etf_meta_get_data()

        db_dict = self.db.etf_db_dict([
            index_id, None, self.ui.etfMetaTickerField.text(),
            self.ui.etfMetaNameField.text(), data_lol[0][0], data_lol[1][0], data_lol[2][0], lev, fee, incep,
            data_lol[3][0], data_lol[4][0], data_lol[5][0], data_lol[6][0], data_lol[7][0], data_lol[8][0],
            data_lol[9][0], data_lol[10][0], data_lol[11][0], data_lol[12][0], data_lol[13][0]],
            [[], [], [''], [], [None]])

        GUIUtils.add_up_button_clicked(self.ui.etfMetaTable, db_dict, self.db.insert_etf, self.db.update_etf,
                                       self.db.read_etfs)

    def etf_meta_etf_table_item_changed(self):
        selected_items = self.ui.etfMetaTable.selectedItems()
        if len(selected_items) == 0:
            self.ui.etfMetaInsertButton.setEnabled(True)
            GUIUtils.set_disabled(True, self.ui.etfMetaAttachButton, self.ui.etfMetaUpdateButton,
                                  self.ui.etfMetaEtfCompTable)
            GUIUtils.clear(self.ui.etfMetaTickerField, self.ui.etfMetaNameField, self.ui.indexMetaIndexCompTable)
            self.ui.etfMetaAssetClassCombo.setCurrentIndex(0)
        else:
            GUIUtils.set_disabled(False, self.ui.etfMetaAttachButton, self.ui.etfMetaUpdateButton,
                                  self.ui.etfMetaEtfCompTable)
            self.ui.etfMetaInsertButton.setEnabled(False)

            data = selected_items[0].data(QtCore.Qt.UserRole)

            if data["lev"] is None:
                data["lev"] = 0
            if data["fee"] is None:
                data["fee"] = 0
            if data["inception"] is None:
                data["inception"] = datetime.datetime(1900, 1, 1, 0, 0)

            self.ui.etfMetaTickerField.setText(data["ticker"])
            self.ui.etfMetaNameField.setText(data["name"])
            self.ui.etfMetaLevSpin.setValue(data["lev"])
            self.ui.etfMetaFeeSpin.setValue(data["fee"])
            self.ui.etfMetaIncepField.setDate(data["inception"])

            cd_list = [
                [self.ui.etfMetaAssetClassCombo, data["asset_class"]],
                [self.ui.etfMetaCompanyCombo, data["company_name"]],
                [self.ui.etfMetaIndexCombo, data["index_ticker"]],
                [self.ui.etfMetaCategoryCombo, data["category"]],
                [self.ui.etfMetaRegionCombo, data["region"]],
                [self.ui.etfMetaCountryCombo, data["country"]],
                [self.ui.etfMetaSectorCombo, data["sector"]],
                [self.ui.etfMetaIndustryCombo, data["industry"]],
                [self.ui.etfMetaAssetSizeCombo, data["asset_class_size"]],
                [self.ui.etfMetaAssetStyleCombo, data["asset_class_style"]],
                [self.ui.etfMetaBondTypeCombo, data["bond_type"]],
                [self.ui.etfMetaBondDurCombo, data["bond_duration_type"]],
                [self.ui.etfMetaCommTypeCombo, data["commodity_type"]],
                [self.ui.etfMetaCommCombo, data["commodity"]],
                [self.ui.etfMetaCommExpoCombo, data["commodity_exposure_type"]],
                [self.ui.etfMetaCurrCombo, data["currency_type"]]]

            for cd in cd_list:
                GUIUtils.set_current_index(cd[0], cd[1])

            GUIUtils.populate_table(self.ui.etfMetaEtfCompTable,
                                    self.db.read_security_components(DBDict(val_dict=data)), ["ticker"])

    def etf_meta_etf_comp_table_item_changed(self):
        selected_items = self.ui.etfMetaEtfCompTable.selectedItems()
        self.ui.etfMetaDetachButton.setEnabled(len(selected_items) > 0)

    def etf_meta_search_button_clicked(self):
        search_db_dict = self.db.etf_search_db_dict()

        lev, fee, incep, data_lol = self.etf_meta_get_data()

        ckd_list = [[self.ui.etfMetaAssetClassCheckbox, "asset_class_id", data_lol[0][0]],
                    [self.ui.etfMetaCompanyCheckbox, "issue_company_id", data_lol[1][0]],
                    [self.ui.etfMetaIndexCheckbox, "index_id", data_lol[2][0]],
                    [self.ui.etfMetaLevLessCheckbox, "lev_less", lev],
                    [self.ui.etfMetaLevGreaterCheckbox, "lev_greater", lev],
                    [self.ui.etfMetaFeeLessCheckbox, "fee_less", fee],
                    [self.ui.etfMetaFeeGreaterCheckbox, "fee_greater", fee],
                    [self.ui.etfMetaIncepLessCheckbox, "inception_less", incep],
                    [self.ui.etfMetaInceptGreaterCheckbox, "inception_greater", incep],
                    [self.ui.etfMetaCategoryCheckbox, "category_id", data_lol[3][0]],
                    [self.ui.etfMetaRCCheckbox, "region_country_id", data_lol[4][0]],
                    [self.ui.etfMetaSICheckbox, "industry_id", data_lol[5][0]],
                    [self.ui.etfMetaAssetSizeCheckbox, "asset_class_size_id", data_lol[6][0]],
                    [self.ui.etfMetaAssetStyleCheckbox, "asset_class_style_id", data_lol[7][0]],
                    [self.ui.etfMetaBondTypeCheckbox, "bond_type_id", data_lol[8][0]],
                    [self.ui.etfMetaBondDurCheckbox, "bond_duration_type_id", data_lol[9][0]],
                    [self.ui.etfMetaCommTypeCheckbox, "commodity_type_id", data_lol[10][0]],
                    [self.ui.etfMetaCommCheckbox, "commodity_id", data_lol[11][0]],
                    [self.ui.etfMetaCommExpoCheckbox, "commodity_exposure_type_id", data_lol[12][0]],
                    [self.ui.etfMetaCurrCheckbox, "currency_type_id", data_lol[13][0]]]

        for ckd in ckd_list:
            if ckd[0].isChecked():
                search_db_dict.value_dict[ckd[1]] = ckd[2]
            else:
                search_db_dict.remove_keys(ckd[1])

        GUIUtils.populate_table(self.ui.etfMetaTable, self.db.read_etfs(search_db_dict))

    def etf_meta_get_data(self):
        lev = self.ui.etfMetaLevSpin.value()
        if lev == 0:
            lev = None

        fee = self.ui.etfMetaFeeSpin.value()
        if fee == 0.00:
            fee = None

        incep = self.ui.etfMetaIncepField.date()
        if incep == QtCore.QDate(1900, 1, 1):
            incep = None
        else:
            incep = GUIUtils.qdate_to_db_string(incep)

        return lev, fee, incep, GUIUtils.combo_data([
            self.ui.etfMetaAssetClassCombo, self.ui.etfMetaCompanyCombo, self.ui.etfMetaIndexCombo,
            self.ui.etfMetaCategoryCombo, self.ui.etfMetaCountryCombo, self.ui.etfMetaIndustryCombo,
            self.ui.etfMetaAssetSizeCombo, self.ui.etfMetaAssetStyleCombo, self.ui.etfMetaBondTypeCombo,
            self.ui.etfMetaBondDurCombo, self.ui.etfMetaCommTypeCombo, self.ui.etfMetaCommCombo,
            self.ui.etfMetaCommExpoCombo, self.ui.etfMetaCurrCombo])