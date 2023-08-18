from modelviews import guiutils
from dataprovider import iexcloud
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

        self.ui.iexcloudResultTable.horizontalHeader().setSectionsMovable(True)
        self.ui.iexcloudResultTable.horizontalHeader().setDragEnabled(True)
        self.ui.iexcloudResultTable.horizontalHeader().setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.iexcloudResultTable.verticalHeader().setSectionsMovable(True)
        self.ui.iexcloudResultTable.verticalHeader().setDragEnabled(True)
        self.ui.iexcloudResultTable.verticalHeader().setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.ui.iexcloudRefreshButton.clicked.connect(self.iex_cloud_refresh_button_clicked)
        self.ui.iexcloudInitButton.clicked.connect(self.iex_cloud_init_button_clicked)
        self.ui.iexcloudChangeCheckbox.toggled.connect(self.iex_cloud_change_checked)
        self.ui.iexcloudKeyUpdateButton.clicked.connect(self.iex_cloud_key_update_button_clicked)
        self.ui.iexcloudMajorEndpointCombo.currentIndexChanged.connect(self.iex_cloud_major_endpoint_combo_changed)
        self.ui.iexcloudEndpointCombo.currentIndexChanged.connect(self.iex_cloud_endpoint_combo_changed)
        self.ui.iexcloudAPICallButton.clicked.connect(self.iex_cloud_api_call_button_clicked)
        self.ui.iexcloudSaveToFileButton.clicked.connect(self.iex_cloud_save_file_button_clicked)
        self.ui.iexcloudLoadFileButton.clicked.connect(self.iex_cloud_load_file_button_clicked)
        self.ui.iexcloudSaveToDBButton.clicked.connect(self.iex_cloud_save_db_button_clicked)

        self.iex_cloud_tab_clear()

    def iex_cloud_set_tab_order(self):
        pass

    def iex_cloud_tab_clear(self):
        guiutils.clear(self.ui.iexcloudEnvCombo, self.ui.iexcloudVersionCombo, self.ui.iexcloudMajorEndpointCombo)
        self.ui.iexcloudInitButton.setEnabled(False)
        self.iex_cloud_init_clear()

    def iex_cloud_init_clear(self):
        guiutils.clear(self.ui.iexcloudEnvLabel, self.ui.iexcloudStatusLabel, self.ui.iexcloudVersionLabel,
                       self.ui.iexcloudTimeLabel, self.ui.iexcloudSKField, self.ui.iexcloudPKField,
                       self.ui.iexcloudPaygLabel, self.ui.iexcloudEffDateLabel, self.ui.iexcloudSubTypeLabel,
                       self.ui.iexcloudTierLabel, self.ui.iexcloudMsgLimitLabel, self.ui.iexcloudMsgUsedLabel,
                       self.ui.iexcloudCircBreakLabel, self.ui.iexcloudMonthUsageLabel, self.ui.iexcloudMonthPaygLabel,
                       self.ui.iexcloudChangeCheckbox, self.ui.iexcloudMajorEndpointCombo, self.ui.iexcloudResultTable,
                       self.ui.iexcloudSelMajorEndpointLabel, self.ui.iexcloudSelEndpointLabel,
                       self.ui.iexcloudSelParamsCombo)
        self.ui.iexcloudResultTable.setColumnCount(0)
        guiutils.set_disabled(True, self.ui.iexcloudChangeCheckbox, self.ui.iexcloudAPICallButton,
                              self.ui.iexcloudSaveToDBButton, self.ui.iexcloudSaveToFileButton,
                              self.ui.iexcloudLoadFileButton)
        self.ui.iexcloudStatusLabel.setStyleSheet("")
        # do this last. clear sends signals to slots that require this variable to be set to iexcloud.Base or subclasses
        self.iex_cloud_base_major_endpoint = None

    def iex_cloud_refresh_button_clicked(self):
        self.iex_cloud_tab_clear()

        self.ui.iexcloudEnvCombo.addItems(iexcloud.Base.ENV_URL_DICT.keys())
        self.ui.iexcloudVersionCombo.addItems(iexcloud.Base.VERSION_DICT.keys())
        self.ui.iexcloudInitButton.setEnabled(True)

    def iex_cloud_init_button_clicked(self):
        self.ui.iexcloudInitButton.setText("Loading")
        self.ui.iexcloudInitButton.setEnabled(False)
        QtWidgets.qApp.processEvents()

        self.iex_cloud_init_clear()

        base = self.ui.iexcloudEnvCombo.currentText()
        version = self.ui.iexcloudVersionCombo.currentText()

        cont = self.iex_cloud_check_status(base, version)
        if cont:
            cont = self.iex_cloud_load_tokens(base, version)
        if cont:
            cont = self.iex_cloud_load_account_data()

        self.ui.iexcloudInitButton.setEnabled(True)
        self.ui.iexcloudInitButton.setText("Init")

        if cont:
            self.ui.iexcloudMajorEndpointCombo.addItems(iexcloud.Base.MAJOR_ENDPOINTS)
            self.ui.iexcloudLoadFileButton.setEnabled(True)

    def iex_cloud_check_status(self, base, version):
        guiutils.clear(self.ui.iexcloudEnvLabel, self.ui.iexcloudStatusLabel, self.ui.iexcloudVersionLabel,
                       self.ui.iexcloudTimeLabel)
        self.ui.iexcloudStatusLabel.setStyleSheet("")
        if base == "Production":
            metadata = iexcloud.APISystemMetadata(base, version, None, None)
            res = metadata.API_metadata()
            if isinstance(res, dict):
                self.ui.iexcloudEnvLabel.setText(base)
                self.ui.iexcloudStatusLabel.setText(res["status"])
                self.ui.iexcloudStatusLabel.setStyleSheet("background-color:lightgreen;")
                self.ui.iexcloudVersionLabel.setText(res["version"])
                self.ui.iexcloudTimeLabel.setText(str(res["time"]))
                return True
            else:
                guiutils.show_error_msg("IEX Cloud Status", res)
                return False
        elif base == "Sandbox":
            self.ui.iexcloudEnvLabel.setText(base)
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
            self.iex_cloud_base_major_endpoint = iexcloud.Base(base, version,
                                                               secret_key, publishable_key)
            self.ui.iexcloudChangeCheckbox.setEnabled(True)
            self.ui.iexcloudSKField.setText(secret_key)
            self.ui.iexcloudPKField.setText(publishable_key)
            return True
        else:
            guiutils.show_error_msg("Key Error", "Secret Key and Publishable Key must not be None")
            return False

    def iex_cloud_load_account_data(self):
        self.iex_cloud_base_major_endpoint.set_account_endpoint()
        res = self.iex_cloud_base_major_endpoint.account_metadata()
        if isinstance(res, str):
            guiutils.show_error_msg("Account Error", res)
            cont = False
        else:
            self.ui.iexcloudPaygLabel.setText(str(res["payAsYouGoEnabled"]))
            self.ui.iexcloudEffDateLabel.setText(str(res["effectiveDate"]))
            self.ui.iexcloudSubTypeLabel.setText(res["subscriptionTermType"])
            self.ui.iexcloudTierLabel.setText(res["tierName"])
            self.ui.iexcloudMsgLimitLabel.setNum(res["messageLimit"])
            self.ui.iexcloudMsgUsedLabel.setNum(res["messagesUsed"])
            self.ui.iexcloudCircBreakLabel.setNum(res["circuitBreaker"])
            cont = True

        if cont:
            res = self.iex_cloud_base_major_endpoint.monthly_message_usage()
            if isinstance(res, str):
                guiutils.show_error_msg("Account Error", res)
                cont = False
            else:
                self.ui.iexcloudMonthUsageLabel.setNum(res["monthlyUsage"])
                self.ui.iexcloudMonthPaygLabel.setNum(res["monthlyPayAsYouGo"])
                cont = True

        return cont

    def iex_cloud_change_checked(self):
        enable = self.ui.iexcloudChangeCheckbox.isChecked()
        self.ui.iexcloudSKField.setReadOnly(not enable)
        self.ui.iexcloudPKField.setReadOnly(not enable)
        self.ui.iexcloudKeyUpdateButton.setEnabled(enable)

    def iex_cloud_key_update_button_clicked(self):
        env = self.ui.iexcloudEnvLabel.text()
        sk_db_dict = self.db.iex_cloud_token_db_dict([self.ui.iexcloudSKField.text(), "Secret", env])
        pk_db_dict = self.db.iex_cloud_token_db_dict([self.ui.iexcloudPKField.text(), "Publishable", env])

        res = self.db.update_iex_api_tokens([sk_db_dict, pk_db_dict])
        if res is None:
            self.ui.iexcloudEnvCombo.setCurrentText(env)
            self.iex_cloud_init_button_clicked()
        else:
            guiutils.show_error_msg("Key Update Error", res)

    def iex_cloud_major_endpoint_combo_changed(self):
        self.iex_cloud_base_major_endpoint.set_major_endpoint(self.ui.iexcloudMajorEndpointCombo.currentText())
        guiutils.combobox_dict_refresh(self.ui.iexcloudEndpointCombo, self.iex_cloud_base_major_endpoint.endpoints())
        self.ui.iexcloudEndpointCombo.model().sort(0)

    def iex_cloud_endpoint_combo_changed(self):
        data = self.ui.iexcloudEndpointCombo.currentData()
        if data is None:
            self.ui.iexcloudNoteArea.setText("")
            self.ui.iexcloudCostField.setText("")
            self.ui.iexcloudAPICallButton.setEnabled(False)
            self.ui.iexcloudParamTable.setRowCount(0)
        else:
            info_dict, param_dict = data["param_func"]()
            self.ui.iexcloudNoteArea.setText(info_dict["note"])
            self.ui.iexcloudCostField.setText(info_dict["cost"])
            self.ui.iexcloudAPICallButton.setEnabled(True)
            self.iex_cloud_set_param_table(param_dict)

    def iex_cloud_set_param_table(self, param_dict):
        self.ui.iexcloudParamTable.setRowCount(0)
        num_rows = len(param_dict)
        self.ui.iexcloudParamTable.setRowCount(num_rows)

        for r, (k, v) in enumerate(param_dict.items()):
            self.ui.iexcloudParamTable.setItem(r, 0, QtWidgets.QTableWidgetItem(k))
            if k[0:7] == "ticker-":
                ticker_dict_list = []
                if "ETFs" in v:
                    ticker_dict_list = ticker_dict_list + self.db.read_etfs()
                if "Stocks" in v:
                    ticker_dict_list = ticker_dict_list + self.db.read_stocks()

                widget = guiutils.q_combo_box_complex(ticker_dict_list, "ticker", "name")
            elif k[0:5] == "date-":
                min_date = None if v[0] is None else guiutils.db_string_to_qdatetime(v[0]).date()
                max_date = None if v[1] is None else guiutils.db_string_to_qdatetime(v[1]).date()
                widget = guiutils.q_date_edit(min_qdate=min_date, max_qdate=max_date)
            else:
                widget = guiutils.q_combo_box_simple(v)
            self.ui.iexcloudParamTable.setCellWidget(r, 1, widget)

    def iex_cloud_api_call_button_clicked(self):
        param_dict = {}
        for r in range(self.ui.iexcloudParamTable.rowCount()):
            key = self.ui.iexcloudParamTable.item(r, 0).text()
            widget = self.ui.iexcloudParamTable.cellWidget(r, 1)
            if isinstance(widget, QtWidgets.QDateEdit):
                value = widget.date().toString("yyyyMMdd")
            elif isinstance(widget, QtWidgets.QComboBox):
                value = widget.currentText()
            else:
                value = None

            if value is None:
                guiutils.show_error_msg("API Call Error", "Type not set for cell widget")
                return
            else:
                param_dict[key] = value

        data = self.ui.iexcloudEndpointCombo.currentData()
        res = data["api_func"](param_dict)
        if isinstance(res, str):
            guiutils.show_error_msg("API Call Error", res)
        else:
            self.iex_cloud_populate_results(self.ui.iexcloudMajorEndpointCombo.currentText(),
                                            self.ui.iexcloudEndpointCombo.currentText(), param_dict, res)

    def iex_cloud_populate_results(self, major_endpoint, endpoint, param_dict, res_list):
        self.ui.iexcloudSelMajorEndpointLabel.setText(major_endpoint)
        self.ui.iexcloudSelEndpointLabel.setText(endpoint)
        guiutils.combobox_list_refresh(self.ui.iexcloudSelParamsCombo, [[v, k] for k, v in param_dict.items()], False)
        guiutils.set_disabled(False, self.ui.iexcloudSaveToDBButton, self.ui.iexcloudSaveToFileButton)

        if len(res_list) == 0 or isinstance(res_list[0], dict):  # list of dict
            guiutils.populate_table(self.ui.iexcloudResultTable, dict_list=res_list, column_headers=True)
        else:  # list of lists of strings or list of strings or list of numbers
            if isinstance(res_list[0], list):
                data_lol = res_list
            else:
                data_lol = []
                for s in res_list:
                    data_lol.append([s])

            guiutils.populate_table(self.ui.iexcloudResultTable, data_lol=data_lol, column_headers=True)

    def iex_cloud_save_file_button_clicked(self):
        param_str = ""
        param_dict = {}
        major_endpoint = self.ui.iexcloudSelMajorEndpointLabel.text()
        endpoint = self.ui.iexcloudSelEndpointLabel.text()
        param_dict["major_endpoint"] = major_endpoint
        param_dict["endpoint"] = endpoint

        for i in range(self.ui.iexcloudSelParamsCombo.count()):
            item_text = self.ui.iexcloudSelParamsCombo.itemText(i)
            param_dict[self.ui.iexcloudSelParamsCombo.itemData(i, QtCore.Qt.UserRole)[0]] = item_text
            param_str = param_str + item_text + "_"

        file_name = "modelviews/loadfile/" + major_endpoint + "_" + endpoint + "_" + param_str
        file_name = file_name + str(datetime.datetime.now())
        file_name = file_name.replace(" ", "-").replace(".", "-").replace(":", "-")
        file_name += ".json"

        result_list = []
        for i in range(self.ui.iexcloudResultTable.rowCount()):
            result_list.append(self.ui.iexcloudResultTable.item(i, 0).data(QtCore.Qt.UserRole))

        def json_default_converter(obj):
            if isinstance(obj, datetime.datetime):
                return obj.__str__()

        try:
            with open(file_name, 'w') as fp:
                json.dump([param_dict, result_list], fp, default=json_default_converter)
        except Exception as e:
            guiutils.show_error_msg("Save File Error", str(e))

    def iex_cloud_load_file_button_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory("modelviews/loadfile")
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
                guiutils.show_error_msg("Load File Error", str(e))

        if None not in (param_dict, result_list):
            major_endpoint = param_dict.pop("major_endpoint")
            endpoint = param_dict.pop("endpoint")
            self.iex_cloud_populate_results(major_endpoint, endpoint, param_dict, result_list)

    def iex_cloud_save_db_button_clicked(self):
        data_list = []
        for r in range(self.ui.iexcloudResultTable.rowCount()):
            data_list.append(self.ui.iexcloudResultTable.item(r, 0).data(QtCore.Qt.UserRole))

        if len(data_list) > 0:
            res = self.db.save_iex_data_to_db(self.ui.iexcloudSelMajorEndpointLabel.text(),
                                              self.ui.iexcloudSelEndpointLabel.text(), data_list)
            if isinstance(res, str):
                guiutils.show_error_msg("Save to DB Error", res)
