from ModelViews import GUIUtils
from DataProvider import IEXCloud
from PyQt5 import QtWidgets, QtCore
import json
import datetime


class IEXCloudTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.iex_cloud_base_major_endpoint = None
        self.init_class()

    def init_class(self):
        self.iex_cloud_set_tab_order()

        self.ui.iexCloudResultTable.horizontalHeader().setSectionsMovable(True)
        self.ui.iexCloudResultTable.horizontalHeader().setDragEnabled(True)
        self.ui.iexCloudResultTable.horizontalHeader().setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.iexCloudResultTable.verticalHeader().setSectionsMovable(True)
        self.ui.iexCloudResultTable.verticalHeader().setDragEnabled(True)
        self.ui.iexCloudResultTable.verticalHeader().setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.iexCloudRefreshButton.clicked.connect(self.iex_cloud_refresh_button_clicked)
        self.ui.iexCloudInitButton.clicked.connect(self.iex_cloud_init_button_clicked)
        self.ui.iexCloudChangeCheckbox.toggled.connect(self.iex_cloud_change_checked)
        self.ui.iexCloudKeyUpdateButton.clicked.connect(self.iex_cloud_key_update_button_clicked)
        self.ui.iexCloudMajorEndpointCombo.currentIndexChanged.connect(self.iex_cloud_major_endpoint_combo_changed)
        self.ui.iexCloudEndpointCombo.currentIndexChanged.connect(self.iex_cloud_endpoint_combo_changed)
        self.ui.iexCloudAPICallButton.clicked.connect(self.iex_cloud_api_call_button_clicked)
        self.ui.iexCloudSaveToFileButton.clicked.connect(self.iex_cloud_save_file_button_clicked)
        self.ui.iexCloudLoadFileButton.clicked.connect(self.iex_cloud_load_file_button_clicked)
        self.ui.iexCloudSaveToDBButton.clicked.connect(self.iex_cloud_save_db_button_clicked)

        self.iex_cloud_tab_clear()

    def iex_cloud_set_tab_order(self):
        pass

    def iex_cloud_tab_clear(self):
        GUIUtils.clear(self.ui.iexCloudEnvCombo, self.ui.iexCloudVersionCombo, self.ui.iexCloudMajorEndpointCombo)
        self.ui.iexCloudInitButton.setEnabled(False)
        self.iex_cloud_init_clear()

    def iex_cloud_init_clear(self):
        GUIUtils.clear(self.ui.iexCloudEnvLabel, self.ui.iexCloudStatusLabel, self.ui.iexCloudVersionLabel,
                       self.ui.iexCloudTimeLabel, self.ui.iexCloudSKField, self.ui.iexCloudPKField,
                       self.ui.iexCloudPaygLabel, self.ui.iexCloudEffDateLabel, self.ui.iexCloudSubTypeLabel,
                       self.ui.iexCloudTierLabel, self.ui.iexCloudMsgLimitLabel, self.ui.iexCloudMsgUsedLabel,
                       self.ui.iexCloudCircBreakLabel, self.ui.iexCloudMonthUsageLabel, self.ui.iexCloudMonthPaygLabel,
                       self.ui.iexCloudChangeCheckbox, self.ui.iexCloudMajorEndpointCombo, self.ui.iexCloudResultTable,
                       self.ui.iexCloudSelMajorEndpointLabel, self.ui.iexCloudSelEndpointLabel,
                       self.ui.iexCloudSelParamsCombo)
        self.ui.iexCloudResultTable.setColumnCount(0)
        GUIUtils.set_disabled(True, self.ui.iexCloudChangeCheckbox, self.ui.iexCloudAPICallButton,
                              self.ui.iexCloudSaveToDBButton, self.ui.iexCloudSaveToFileButton,
                              self.ui.iexCloudLoadFileButton)
        self.ui.iexCloudStatusLabel.setStyleSheet("")
        # do this last. clear sends signals to slots that require this variable to be set to IEXCloud.Base or subclasses
        self.iex_cloud_base_major_endpoint = None

    def iex_cloud_refresh_button_clicked(self):
        self.iex_cloud_tab_clear()

        self.ui.iexCloudEnvCombo.addItems(IEXCloud.Base.ENV_URL_DICT.keys())
        self.ui.iexCloudVersionCombo.addItems(IEXCloud.Base.VERSION_DICT.keys())
        self.ui.iexCloudInitButton.setEnabled(True)

    def iex_cloud_init_button_clicked(self):
        self.ui.iexCloudInitButton.setText("Loading")
        self.ui.iexCloudInitButton.setEnabled(False)
        QtWidgets.qApp.processEvents()

        self.iex_cloud_init_clear()

        base = self.ui.iexCloudEnvCombo.currentText()
        version = self.ui.iexCloudVersionCombo.currentText()

        cont = self.iex_cloud_check_status(base, version)
        if cont:
            cont = self.iex_cloud_load_tokens(base, version)
        if cont:
            cont = self.iex_cloud_load_account_data()

        self.ui.iexCloudInitButton.setEnabled(True)
        self.ui.iexCloudInitButton.setText("Init")

        if cont:
            self.ui.iexCloudMajorEndpointCombo.addItems(IEXCloud.Base.MAJOR_ENDPOINTS)
            self.ui.iexCloudLoadFileButton.setEnabled(True)

    def iex_cloud_check_status(self, base, version):
        GUIUtils.clear(self.ui.iexCloudEnvLabel, self.ui.iexCloudStatusLabel, self.ui.iexCloudVersionLabel,
                       self.ui.iexCloudTimeLabel)
        self.ui.iexCloudStatusLabel.setStyleSheet("")
        if base == "Production":
            metadata = IEXCloud.APISystemMetadata(base, version, None, None)
            res = metadata.API_metadata()
            if isinstance(res, dict):
                self.ui.iexCloudEnvLabel.setText(base)
                self.ui.iexCloudStatusLabel.setText(res["status"])
                self.ui.iexCloudStatusLabel.setStyleSheet("background-color:lightgreen;")
                self.ui.iexCloudVersionLabel.setText(res["version"])
                self.ui.iexCloudTimeLabel.setText(str(res["time"]))
                return True
            else:
                GUIUtils.show_error_msg("IEX Cloud Status", res)
                return False
        elif base == "Sandbox":
            self.ui.iexCloudEnvLabel.setText(base)
            return True

    def iex_cloud_load_tokens(self, base, version):
        secret_key = None
        publishable_key = None
        key_dict_list = self.db.read_iex_api_tokens()

        for key_dict in key_dict_list:
            if key_dict["env"] == base:
                if key_dict["type"] == "Secret":
                    secret_key = key_dict["token"]
                elif key_dict["type"] == "Publishable":
                    publishable_key = key_dict["token"]

        if secret_key is not None and publishable_key is not None:
            self.iex_cloud_base_major_endpoint = IEXCloud.Base(base, version,
                                                               secret_key, publishable_key)
            self.ui.iexCloudChangeCheckbox.setEnabled(True)
            self.ui.iexCloudSKField.setText(secret_key)
            self.ui.iexCloudPKField.setText(publishable_key)
            return True
        else:
            GUIUtils.show_error_msg("Key Error", "Secret Key and Publishable Key must not be None")
            return False

    def iex_cloud_load_account_data(self):
        self.iex_cloud_base_major_endpoint.set_account_endpoint()
        res = self.iex_cloud_base_major_endpoint.account_metadata()
        if isinstance(res, str):
            GUIUtils.show_error_msg("Account Error", res)
            cont = False
        else:
            self.ui.iexCloudPaygLabel.setText(str(res["payAsYouGoEnabled"]))
            self.ui.iexCloudEffDateLabel.setText(str(res["effectiveDate"]))
            self.ui.iexCloudSubTypeLabel.setText(res["subscriptionTermType"])
            self.ui.iexCloudTierLabel.setText(res["tierName"])
            self.ui.iexCloudMsgLimitLabel.setNum(res["messageLimit"])
            self.ui.iexCloudMsgUsedLabel.setNum(res["messagesUsed"])
            self.ui.iexCloudCircBreakLabel.setNum(res["circuitBreaker"])
            cont = True

        if cont:
            res = self.iex_cloud_base_major_endpoint.monthly_message_usage()
            if isinstance(res, str):
                GUIUtils.show_error_msg("Account Error", res)
                cont = False
            else:
                self.ui.iexCloudMonthUsageLabel.setNum(res["monthlyUsage"])
                self.ui.iexCloudMonthPaygLabel.setNum(res["monthlyPayAsYouGo"])
                cont = True

        return cont

    def iex_cloud_change_checked(self):
        enable = self.ui.iexCloudChangeCheckbox.isChecked()
        self.ui.iexCloudSKField.setReadOnly(not enable)
        self.ui.iexCloudPKField.setReadOnly(not enable)
        self.ui.iexCloudKeyUpdateButton.setEnabled(enable)

    def iex_cloud_key_update_button_clicked(self):
        env = self.ui.iexCloudEnvLabel.text()
        sk_db_dict = self.db.iex_cloud_token_db_dict([self.ui.iexCloudSKField.text(), "Secret", env])
        pk_db_dict = self.db.iex_cloud_token_db_dict([self.ui.iexCloudPKField.text(), "Publishable", env])

        res = self.db.update_iex_api_tokens([sk_db_dict, pk_db_dict])
        if res is None:
            self.ui.iexCloudEnvCombo.setCurrentText(env)
            self.iex_cloud_init_button_clicked()
        else:
            GUIUtils.show_error_msg("Key Update Error", res)

    def iex_cloud_major_endpoint_combo_changed(self):
        self.iex_cloud_base_major_endpoint.set_major_endpoint(self.ui.iexCloudMajorEndpointCombo.currentText())
        GUIUtils.combobox_dict_refresh(self.ui.iexCloudEndpointCombo, self.iex_cloud_base_major_endpoint.endpoints())
        self.ui.iexCloudEndpointCombo.model().sort(0)

    def iex_cloud_endpoint_combo_changed(self):
        data = self.ui.iexCloudEndpointCombo.currentData()
        if data is None:
            self.ui.iexCloudNoteArea.setText("")
            self.ui.iexCloudCostField.setText("")
            self.ui.iexCloudAPICallButton.setEnabled(False)
            self.ui.iexCloudParamTable.setRowCount(0)
        else:
            info_dict, param_dict = data["param_func"]()
            self.ui.iexCloudNoteArea.setText(info_dict["note"])
            self.ui.iexCloudCostField.setText(info_dict["cost"])
            self.ui.iexCloudAPICallButton.setEnabled(True)
            self.iex_cloud_set_param_table(param_dict)

    def iex_cloud_set_param_table(self, param_dict):
        self.ui.iexCloudParamTable.setRowCount(0)
        num_rows = len(param_dict)
        self.ui.iexCloudParamTable.setRowCount(num_rows)

        for r, (k, v) in enumerate(param_dict.items()):
            self.ui.iexCloudParamTable.setItem(r, 0, QtWidgets.QTableWidgetItem(k))
            if k[0:7] == "ticker-":
                ticker_dict_list = []
                if "ETFs" in v:
                    ticker_dict_list = ticker_dict_list + self.db.read_etfs()
                if "Stocks" in v:
                    ticker_dict_list = ticker_dict_list + self.db.read_stocks()

                widget = GUIUtils.q_combo_box_complex(ticker_dict_list, "ticker", "name")
            elif k[0:5] == "date-":
                min_date = None if v[0] is None else GUIUtils.db_string_to_qdatetime(v[0]).date()
                max_date = None if v[1] is None else GUIUtils.db_string_to_qdatetime(v[1]).date()
                widget = GUIUtils.q_date_edit(min_qdate=min_date, max_qdate=max_date)
            else:
                widget = GUIUtils.q_combo_box_simple(v)
            self.ui.iexCloudParamTable.setCellWidget(r, 1, widget)

    def iex_cloud_api_call_button_clicked(self):
        param_dict = {}
        for r in range(self.ui.iexCloudParamTable.rowCount()):
            key = self.ui.iexCloudParamTable.item(r, 0).text()
            widget = self.ui.iexCloudParamTable.cellWidget(r, 1)
            if isinstance(widget, QtWidgets.QDateEdit):
                value = widget.date().toString("yyyyMMdd")
            elif isinstance(widget, QtWidgets.QComboBox):
                value = widget.currentText()
            else:
                value = None

            if value is None:
                GUIUtils.show_error_msg("API Call Error", "Type not set for cell widget")
                return
            else:
                param_dict[key] = value

        data = self.ui.iexCloudEndpointCombo.currentData()
        res = data["api_func"](param_dict)
        if isinstance(res, str):
            GUIUtils.show_error_msg("API Call Error", res)
        else:
            self.iex_cloud_populate_results(self.ui.iexCloudMajorEndpointCombo.currentText(),
                                            self.ui.iexCloudEndpointCombo.currentText(), param_dict, res)

    def iex_cloud_populate_results(self, major_endpoint, endpoint, param_dict, res_list):
        self.ui.iexCloudSelMajorEndpointLabel.setText(major_endpoint)
        self.ui.iexCloudSelEndpointLabel.setText(endpoint)
        GUIUtils.combobox_list_refresh(self.ui.iexCloudSelParamsCombo, [[v, k] for k, v in param_dict.items()], False)
        GUIUtils.set_disabled(False, self.ui.iexCloudSaveToDBButton, self.ui.iexCloudSaveToFileButton)

        if len(res_list) == 0 or isinstance(res_list[0], dict):  # list of dict
            GUIUtils.populate_table(self.ui.iexCloudResultTable, dict_list=res_list, column_headers=True)
        else:  # list of lists of strings or list of strings or list of numbers
            if isinstance(res_list[0], list):
                data_lol = res_list
            else:
                data_lol = []
                for s in res_list:
                    data_lol.append([s])

            GUIUtils.populate_table(self.ui.iexCloudResultTable, data_lol=data_lol, column_headers=True)

    def iex_cloud_save_file_button_clicked(self):
        param_str = ""
        param_dict = {}
        major_endpoint = self.ui.iexCloudSelMajorEndpointLabel.text()
        endpoint = self.ui.iexCloudSelEndpointLabel.text()
        param_dict["major_endpoint"] = major_endpoint
        param_dict["endpoint"] = endpoint

        for i in range(self.ui.iexCloudSelParamsCombo.count()):
            item_text = self.ui.iexCloudSelParamsCombo.itemText(i)
            param_dict[self.ui.iexCloudSelParamsCombo.itemData(i, QtCore.Qt.UserRole)[0]] = item_text
            param_str = param_str + item_text + "_"

        file_name = "ModelViews/LoadFile/" + major_endpoint + "_" + endpoint + "_" + param_str
        file_name = file_name + str(datetime.datetime.now())
        file_name = file_name.replace(" ", "-").replace(".", "-").replace(":", "-")
        file_name += ".json"

        result_list = []
        for i in range(self.ui.iexCloudResultTable.rowCount()):
            result_list.append(self.ui.iexCloudResultTable.item(i, 0).data(QtCore.Qt.UserRole))

        def json_default_converter(obj):
            if isinstance(obj, datetime.datetime):
                return obj.__str__()

        try:
            with open(file_name, 'w') as fp:
                json.dump([param_dict, result_list], fp, default=json_default_converter)
        except Exception as e:
            GUIUtils.show_error_msg("Save File Error", str(e))

    def iex_cloud_load_file_button_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory("ModelViews/LoadFile")
        filename = dialog.getOpenFileName()[0]

        param_dict = None
        result_list = None
        if filename != '':
            try:
                with open(filename, 'r') as infile:
                    lista = json.loads(infile.read())
                    param_dict = lista[0]
                    result_list = lista[1]
            except Exception as e:
                GUIUtils.show_error_msg("Load File Error", str(e))

        if None not in (param_dict, result_list):
            major_endpoint = param_dict.pop("major_endpoint")
            endpoint = param_dict.pop("endpoint")
            self.iex_cloud_populate_results(major_endpoint, endpoint, param_dict, result_list)

    def iex_cloud_save_db_button_clicked(self):
        data_list = []
        for r in range(self.ui.iexCloudResultTable.rowCount()):
            data_list.append(self.ui.iexCloudResultTable.item(r, 0).data(QtCore.Qt.UserRole))

        if len(data_list) > 0:
            res = self.db.save_iex_data_to_db(self.ui.iexCloudSelMajorEndpointLabel.text(),
                                              self.ui.iexCloudSelEndpointLabel.text(), data_list)
            if isinstance(res, str):
                GUIUtils.show_error_msg("Save to DB Error", res)
