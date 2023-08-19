import datetime

from PyQt5 import QtWidgets, QtCore
import pandas as pd

from assetmanagement.modelviews import guiutils


class SEIDataTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db
        self.sei_data_selected_meta = None
        self.sei_data_tab_price_table_changed_ids_set = set()
        self.sei_data_tab_data_table_changed_ids_set = set()
        self.sei_data_tab_weight_table_changed_ids_set = set()

        self.init_class()

    ####################################################################################################################
    # SEI Data
    ####################################################################################################################
    def init_class(self):
        self.sei_data_selected_meta = {}
        self.sei_data_tab_price_table_changed_ids_set = set()
        self.sei_data_tab_data_table_changed_ids_set = set()
        self.sei_data_tab_weight_table_changed_ids_set = set()

        self.sei_data_set_tab_order()

        self.ui.seiDataPriceTable.setColumnWidth(0, 120)
        self.ui.seiDataDataTable.setColumnWidth(1, 50)
        self.ui.seiDataDataTable.setColumnWidth(2, 50)
        self.ui.seiDataWeightTable.setColumnWidth(1, 50)

        self.ui.seiDataRefreshButton.clicked.connect(self.sei_data_refresh_button_clicked)
        self.ui.seiDataSTCombo.currentIndexChanged.connect(self.sei_data_st_combo_changed)
        self.ui.seiDataTickerCombo.currentIndexChanged.connect(self.sei_data_ticker_combo_changed)
        self.ui.seiDataFreqCombo.currentIndexChanged.connect(self.sei_data_freq_combo_changed)

        self.ui.seiDataShowButton.clicked.connect(self.sei_data_show_button_clicked)
        self.ui.seiDataPriceAddUpButton.clicked.connect(self.sei_data_price_add_up_button_clicked)
        self.ui.seiDataPriceLoadFileButton.clicked.connect(self.sei_data_price_load_file_button_clicked)
        self.ui.seiDataDataAddUpButton.clicked.connect(self.sei_data_data_add_up_button_clicked)
        self.ui.seiDataWeightUpdateButton.clicked.connect(self.sei_data_weight_update_button_clicked)

        self.sei_data_tab_clear()

    def sei_data_set_tab_order(self):
        pass

    def sei_data_tab_clear(self):
        guiutils.clear(self.ui.seiDataNameField, self.ui.seiDataDateEndField, self.ui.seiDataSTLabel,
                       self.ui.seiDataTickerLabel, self.ui.seiDataFreqLabel, self.ui.seiDataPriceTable,
                       self.ui.seiDataDataTable, self.ui.seiDataWeightTable)
        self.ui.seiDataDateBeginField.setDate(QtCore.QDate(1900, 1, 1))
        self.ui.seiDataDateEndField.setDate(QtCore.QDate(1900, 1, 1))
        guiutils.set_disabled(True, self.ui.seiDataShowButton, self.ui.seiDataPriceAddUpButton,
                              self.ui.seiDataPriceLoadFileButton, self.ui.seiDataDataAddUpButton,
                              self.ui.seiDataWeightUpdateButton)

    def sei_data_refresh_button_clicked(self):
        guiutils.combobox_dict_refresh(self.ui.seiDataSTCombo, self.db.read_security_subtypes())

        self.sei_data_tab_clear()

    def sei_data_st_combo_changed(self, index):
        self.ui.seiDataTickerCombo.clear()

        item_data = self.ui.seiDataSTCombo.currentData()
        if item_data is not None:
            db_dict = self.db.data_meta_table_db_dict([item_data["db_table_meta"]])
            guiutils.combobox_dict_refresh(self.ui.seiDataTickerCombo,
                                           self.db.read_data_subtype_meta_table(db_dict), "ticker")
            db_dict = self.db.data_subtype_freq_db_dict([None, item_data["id"], None])
            guiutils.combobox_dict_refresh(self.ui.seiDataFreqCombo, self.db.read_data_subtype_freq(db_dict), "freq",
                                           include_blank=False)

    def sei_data_ticker_combo_changed(self, index):
        item_data = self.ui.seiDataTickerCombo.currentData()

        if item_data is None:
            self.ui.seiDataShowButton.setEnabled(False)
        else:
            self.ui.seiDataShowButton.setEnabled(True)
            self.ui.seiDataNameField.setText(item_data["name"])

    def sei_data_freq_combo_changed(self, index):
        display_format = guiutils.combo_data(self.ui.seiDataFreqCombo, ["format_str"])[0]
        self.ui.seiDataDateBeginField.setDisplayFormat(display_format)
        self.ui.seiDataDateEndField.setDisplayFormat(display_format)

    def sei_data_show_button_clicked(self):
        self.sei_data_selected_meta = {}
        self.sei_data_tab_price_table_changed_ids_set = set()
        self.sei_data_tab_data_table_changed_ids_set = set()
        self.sei_data_tab_weight_table_changed_ids_set = set()

        freq = self.ui.seiDataFreqCombo.currentText()
        begin_datetime = guiutils.round_time_to_interval(self.ui.seiDataDateBeginField.dateTime(), freq)
        end_datetime = guiutils.round_time_to_interval(self.ui.seiDataDateEndField.dateTime(), freq)

        if begin_datetime.date() == QtCore.QDate(1900, 1, 1):
            begin_datetime = None
        if end_datetime.date() == QtCore.QDate(1900, 1, 1):
            end_datetime = None

        security_type = self.ui.seiDataSTCombo.currentText()
        ticker = self.ui.seiDataTickerCombo.currentText()
        st_data = self.ui.seiDataSTCombo.currentData()
        freq_data = self.ui.seiDataFreqCombo.currentData()
        securities_id = self.ui.seiDataTickerCombo.currentData()["securities_id"]

        self.sei_data_selected_meta = {"security_type": security_type, "securities_id": securities_id,
                                       "db_data_table_prefix": st_data["db_data_table_prefix"], "freq": freq,
                                       "display_format": freq_data["format_str"], "ticker": ticker,
                                       "begin_datetime": begin_datetime, "end_datetime": end_datetime}

        self.sei_data_set_price_table(security_type, securities_id, freq, freq_data["format_str"], begin_datetime,
                                      end_datetime)
        self.sei_data_set_data_table(security_type, securities_id, begin_datetime, end_datetime)
        self.sei_data_set_weight_table(security_type, securities_id)

        self.ui.seiDataSTLabel.setText(security_type)
        self.ui.seiDataTickerLabel.setText(ticker)
        self.ui.seiDataFreqLabel.setText(freq)

    def sei_data_set_price_table(self, security_type, securities_id, freq, display_format, begin_datetime,
                                 end_datetime):
        req_q_datetime = guiutils.req_q_datetime(display_format)
        db_dict = self.db.sei_data_price_data_read_db_dict(
            [security_type, freq, securities_id, guiutils.qdate_to_db_string(begin_datetime),
             guiutils.qdate_to_db_string(end_datetime)])

        dict_list = self.db.read_sei_price(db_dict)
        data_keys = dict_list.pop(0)

        empty_dict = {}
        for k in data_keys:
            empty_dict[k] = 0
        empty_dict["id"] = None
        empty_dict["date_time"] = datetime.datetime.now()
        dict_list.insert(0, empty_dict)
        num_rows = len(dict_list)
        num_cols = len(data_keys)

        self.ui.seiDataPriceTable.clearSelection()
        self.ui.seiDataPriceTable.setRowCount(num_rows)
        is_sort = self.ui.seiDataPriceTable.isSortingEnabled()
        self.ui.seiDataPriceTable.setSortingEnabled(False)

        for r in range(num_rows):
            data = [dict_list[r].get(key) for key in data_keys]
            data = [0 if x is None else x for x in data]

            q_date_time = QtCore.QDateTime(data[0])

            item = QtWidgets.QTableWidgetItem(str(data[0]))
            item.setData(QtCore.Qt.UserRole, dict_list[r])
            if req_q_datetime:
                dte = guiutils.q_date_time_edit(q_date_time, self.sei_data_price_cell_changed)
            else:
                dte = guiutils.q_date_edit(q_date_time.date(), self.sei_data_price_cell_changed)

            self.ui.seiDataPriceTable.setItem(r, 0, item)
            self.ui.seiDataPriceTable.setCellWidget(r, 0, dte)
            for c in range(num_cols - 1):
                self.ui.seiDataPriceTable.setItem(r, c + 1, QtWidgets.QTableWidgetItem(str(data[c + 1])))
                self.ui.seiDataPriceTable.setCellWidget(
                    r, c + 1, guiutils.q_double_spin_box(data[c + 1], 2, -999999999.99, 999999999.99,
                                                         self.sei_data_price_cell_changed))
            if security_type == "Indices":
                # need this to set the style sheet
                self.ui.seiDataPriceTable.setCellWidget(r, 6, QtWidgets.QWidget())
            else:
                self.ui.seiDataPriceTable.setItem(r, 6, QtWidgets.QTableWidgetItem(str(data[6])))
                self.ui.seiDataPriceTable.setCellWidget(
                    r, 6, guiutils.q_double_spin_box(data[6], 0, 0, 999999999999, self.sei_data_price_cell_changed))

        for c in range(self.ui.seiDataPriceTable.columnCount()):
            self.ui.seiDataPriceTable.cellWidget(0, c).setStyleSheet("background-color:lightgreen;")

        self.ui.seiDataPriceTable.setSortingEnabled(is_sort)
        guiutils.set_disabled(False, self.ui.seiDataPriceAddUpButton, self.ui.seiDataPriceLoadFileButton)

    def sei_data_set_data_table(self, security_type, securities_id, begin_datetime, end_datetime):
        guiutils.set_disabled(False, self.ui.seiDataDataTable, self.ui.seiDataDataAddUpButton)

        db_dict = self.db.sei_data_price_data_read_db_dict(
            [security_type, None, securities_id, guiutils.qdate_to_db_string(begin_datetime),
             guiutils.qdate_to_db_string(end_datetime)])

        res = self.db.read_sei_data(db_dict)

        if res is False:
            guiutils.set_disabled(True, self.ui.seiDataDataTable, self.ui.seiDataDataAddUpButton)
            self.ui.seiDataDataTable.setRowCount(0)
        else:
            dict_list = res
            data_keys = dict_list.pop(0)

            if security_type == "Stocks":
                item = QtWidgets.QTableWidgetItem("Outstanding")
                item.setData(QtCore.Qt.ToolTipRole, "Outstanding Shares")
            else:  # security_type == "ETFs":
                item = QtWidgets.QTableWidgetItem("AUM")
            self.ui.seiDataDataTable.setHorizontalHeaderItem(self.ui.seiDataDataTable.columnCount() - 1, item)

            empty_dict = {}
            for k in data_keys:
                empty_dict[k] = 0
            empty_dict["id"] = None
            empty_dict["date_time"] = QtCore.QDateTime().currentDateTime()
            dict_list.insert(0, empty_dict)
            num_rows = len(dict_list)

            self.ui.seiDataDataTable.clearSelection()
            self.ui.seiDataDataTable.setRowCount(num_rows)
            is_sort = self.ui.seiDataDataTable.isSortingEnabled()
            self.ui.seiDataDataTable.setSortingEnabled(False)

            ps = [[2, 0, 999.99], [3, 0, 999.999], [0, 0, 99999999999], [0, 0, 99999999999], [0, 0, 9999999999999]]
            for r in range(num_rows):
                data = [dict_list[r].get(key) for key in data_keys]
                data = [0 if x is None else x for x in data]

                q_date_time = QtCore.QDateTime(data[0])

                item = QtWidgets.QTableWidgetItem(str(data[0]))
                item.setData(QtCore.Qt.UserRole, dict_list[r])

                self.ui.seiDataDataTable.setItem(r, 0, item)
                self.ui.seiDataDataTable.setCellWidget(r, 0, guiutils.q_date_edit(q_date_time.date(),
                                                                                  self.sei_data_data_cell_changed))

                for c in range(self.ui.seiDataDataTable.columnCount() - 1):
                    self.ui.seiDataDataTable.setItem(r, c + 1, QtWidgets.QTableWidgetItem(str(data[c + 1])))
                    self.ui.seiDataDataTable.setCellWidget(
                        r, c + 1, guiutils.q_double_spin_box(data[c + 1], ps[c][0], ps[c][1], ps[c][2],
                                                             self.sei_data_data_cell_changed))

            for c in range(self.ui.seiDataDataTable.columnCount()):
                self.ui.seiDataDataTable.cellWidget(0, c).setStyleSheet("background-color:lightgreen;")

            self.ui.seiDataDataTable.setSortingEnabled(is_sort)

    def sei_data_set_weight_table(self, security_type, securities_id):
        guiutils.set_disabled(False, self.ui.seiDataWeightTable, self.ui.seiDataWeightUpdateButton)

        res = self.db.read_securities_under(self.db.securities_under_db_dict([security_type, securities_id]))

        if res is False:
            guiutils.set_disabled(True, self.ui.seiDataWeightTable, self.ui.seiDataWeightUpdateButton)
            self.ui.seiDataWeightTable.setRowCount(0)
        else:
            dict_list = res
            data_keys = dict_list.pop(0)
            num_rows = len(dict_list)

            self.ui.seiDataWeightTable.clearSelection()
            self.ui.seiDataWeightTable.setRowCount(num_rows)
            is_sort = self.ui.seiDataWeightTable.isSortingEnabled()
            self.ui.seiDataWeightTable.setSortingEnabled(False)

            for r in range(num_rows):
                data = [dict_list[r].get(key) for key in data_keys]
                data = [0 if x is None else x for x in data]

                item = QtWidgets.QTableWidgetItem(data[0])
                item.setData(QtCore.Qt.UserRole, dict_list[r])

                self.ui.seiDataWeightTable.setItem(r, 0, item)
                self.ui.seiDataWeightTable.setItem(r, 1, QtWidgets.QTableWidgetItem(str(data[1])))
                self.ui.seiDataWeightTable.setCellWidget(
                    r, 1, guiutils.q_double_spin_box(data[1], 2, 0, 100.00, self.sei_data_weight_cell_changed))

            self.ui.seiDataWeightTable.setSortingEnabled(is_sort)

        self.sei_data_sum_weights()

    def sei_data_price_load_file_button_clicked(self):
        confirm = guiutils.show_confirm_msg(
            "Load Data", "See sei_load_price_template.csv for required file format. Existing data will be overwritten "
                         "for matching dates. Confirm?")
        if not confirm:
            return

        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory("modelviews/loadfile")
        filename = dialog.getOpenFileName()[0]

        if filename != '':
            try:
                # TODO finish this. make sure fields have appropriate values for database insert/update
                df = pd.read_csv(filename)
                df = df.where(pd.notnull(df), None)
                print(df.to_dict(orient="records")[0:100])
                '''
                res = self.db.insert_or_update_sei_price(
                    df.to_dict(orient="records"), self.sei_data_selected_meta["freq"],
                    self.sei_data_selected_meta["security_type"], self.sei_data_selected_meta["securities_id"])

                if res is None:
                    self.sei_data_tab_price_table_changed_ids_set = set()  # do last
                else:
                    raise Exception(res)
                '''
            except Exception as e:
                guiutils.show_error_msg("Load File Error", str(e))

    def sei_data_price_add_up_button_clicked(self):
        db_dict_list = []

        for r in range(self.ui.seiDataPriceTable.rowCount()):
            rid = self.ui.seiDataPriceTable.item(r, 0).data(QtCore.Qt.UserRole)["id"]

            if rid in self.sei_data_tab_price_table_changed_ids_set \
                    and self.ui.seiDataPriceTable.cellWidget(r, 0).date() != QtCore.QDate(1900, 1, 1):

                vals = [rid, self.sei_data_selected_meta["security_type"],
                        str(self.sei_data_selected_meta["securities_id"]), self.sei_data_selected_meta["freq"]]
                vals.append(self.ui.seiDataPriceTable.item(r, 0).text())

                for c in range(self.ui.seiDataPriceTable.columnCount() - 1):
                    vals.append(self.ui.seiDataPriceTable.cellWidget(r, c + 1).value())
                vals = [None if x == 0 else x for x in vals]

                db_dict = self.db.sei_data_price_db_dict(vals)

                if rid is None:
                    if guiutils.add_up_button_clicked(None, db_dict, self.db.insert_sei_price):
                        self.sei_data_tab_price_table_changed_ids_set.remove(rid)
                else:
                    db_dict_list.append(db_dict)

        if len(db_dict_list) > 0:
            res = self.db.update_sei_price(db_dict_list)
            if res is None:
                self.sei_data_tab_price_table_changed_ids_set = set()  # do last
            else:
                guiutils.show_error_msg("Update Error", res)

    def sei_data_data_add_up_button_clicked(self):
        db_dict_list = []
        is_etf = self.sei_data_selected_meta["security_type"] == "ETFs"

        for r in range(self.ui.seiDataDataTable.rowCount()):
            rid = self.ui.seiDataDataTable.item(r, 0).data(QtCore.Qt.UserRole)["id"]

            if rid in self.sei_data_tab_data_table_changed_ids_set \
                    and self.ui.seiDataDataTable.cellWidget(r, 0).date() != QtCore.QDate(1900, 1, 1):
                vals = [rid, str(self.sei_data_selected_meta["securities_id"])]
                vals.append(self.ui.seiDataDataTable.item(r, 0).text())

                for c in range(self.ui.seiDataDataTable.columnCount() - 1):
                    vals.append(self.ui.seiDataDataTable.cellWidget(r, c + 1).value())
                vals = [None if x == 0 else x for x in vals]

                if is_etf:
                    vals.insert(len(vals) - 1, None)

                db_dict = self.db.sei_data_data_db_dict(vals)

                if rid is None:
                    if guiutils.add_up_button_clicked(None, db_dict, self.db.insert_sei_data):
                        self.sei_data_tab_data_table_changed_ids_set.remove(rid)
                else:
                    db_dict_list.append(db_dict)

        if len(db_dict_list) > 0:
            res = self.db.update_sei_data(db_dict_list)
            if res is None:
                self.sei_data_tab_data_table_changed_ids_set = set()  # do last
            else:
                guiutils.show_error_msg("Update Error", res)

    def sei_data_weight_update_button_clicked(self):
        db_dict_list = []

        for r in range(self.ui.seiDataWeightTable.rowCount()):
            rid = self.ui.seiDataWeightTable.item(r, 0).data(QtCore.Qt.UserRole)["id"]

            if rid in self.sei_data_tab_weight_table_changed_ids_set:
                vals = [rid, None, None, self.ui.seiDataWeightTable.cellWidget(r, 1).value()]
                vals = [None if x == 0 else x for x in vals]
                db_dict_list.append(self.db.security_security_db_dict(vals))

        if len(db_dict_list) > 0:
            res = self.db.update_security_security_weight(db_dict_list)
            if res is None:
                self.sei_data_tab_weight_table_changed_ids_set = set()  # do last
            else:
                guiutils.show_error_msg("Update Error", res)

    def sei_data_price_cell_changed(self, value):
        self.sei_data_tab_price_table_changed_ids_set.add(
            self.ui.seiDataPriceTable.item(self.ui.seiDataPriceTable.currentRow(), 0).data(QtCore.Qt.UserRole)["id"])
        if isinstance(value, (QtCore.QDate, QtCore.QDateTime)):
            value = guiutils.qdate_to_db_string(value)
        self.ui.seiDataPriceTable.currentItem().setText(str(value))

    def sei_data_data_cell_changed(self, value):
        self.sei_data_tab_data_table_changed_ids_set.add(
            self.ui.seiDataDataTable.item(self.ui.seiDataDataTable.currentRow(), 0).data(QtCore.Qt.UserRole)["id"])
        if isinstance(value, (QtCore.QDate, QtCore.QDateTime)):
            value = guiutils.qdate_to_db_string(value)
        self.ui.seiDataDataTable.currentItem().setText(str(value))

    def sei_data_weight_cell_changed(self, value):
        self.sei_data_tab_weight_table_changed_ids_set.add(
            self.ui.seiDataWeightTable.item(self.ui.seiDataWeightTable.currentRow(), 0).data(QtCore.Qt.UserRole)["id"])
        self.ui.seiDataWeightTable.currentItem().setText(str(value))
        self.sei_data_sum_weights()

    def sei_data_sum_weights(self):
        wsum = 0.00
        for r in range(self.ui.seiDataWeightTable.rowCount()):
            wsum += self.ui.seiDataWeightTable.cellWidget(r, 1).value()
        self.ui.seiDataWeightSumField.setText(str(wsum))