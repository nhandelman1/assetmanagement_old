from modelviews import guiutils
from PyQt5 import QtWidgets, QtCore
from statistics import Transform, StatsData, Equation, PreImpute
import datetime
import csv
import pandas as pd


class DataSelectionTabMV:

    def __init__(self, ui, db):
        self.ui = ui
        self.db = db

        self.init_class()

    def init_class(self):
        self.set_tab_order()

        self.ui.statsDataSelDepDataTable.setColumnWidth(2, 60)
        self.ui.statsDataSelDepDataTable.setColumnWidth(4, 60)
        self.ui.statsDataSelIndepDataTable.setColumnWidth(2, 60)
        self.ui.statsDataSelIndepDataTable.setColumnWidth(4, 60)
        self.ui.statsDataSelRAADataTable.setColumnWidth(2, 60)
        self.ui.statsDataSelRAADataTable.setColumnWidth(4, 60)
        self.ui.statsDataSelOtherDataTable.setColumnWidth(2, 60)
        self.ui.statsDataSelOtherDataTable.setColumnWidth(4, 60)

        self.ui.statsDataSelRefreshButton.clicked.connect(self.refresh_button_clicked)
        self.ui.statsDataSelDSAddButton.clicked.connect(self.ds_add_button_clicked)
        self.ui.statsDataSelLoadFileButton.clicked.connect(self.load_file_button_clicked)
        self.ui.statsDataSelIntAddButton.clicked.connect(self.int_add_button_clicked)

        self.ui.statsDataSelDepRemoveDataButton.clicked.connect(
            lambda: self.remove_button_clicked(self.ui.statsDataSelDepDataTable))
        self.ui.statsDataSelDepRemoveIntButton.clicked.connect(
            lambda: self.remove_button_clicked(self.ui.statsDataSelDepIntTable, False))
        self.ui.statsDataSelIndepRemoveDataButton.clicked.connect(
            lambda: self.remove_button_clicked(self.ui.statsDataSelIndepDataTable))
        self.ui.statsDataSelIndepRemoveIntButton.clicked.connect(
            lambda: self.remove_button_clicked(self.ui.statsDataSelIndepIntTable, False))
        self.ui.statsDataSelRAARemoveDataButton.clicked.connect(
            lambda: self.remove_button_clicked(self.ui.statsDataSelRAADataTable))
        self.ui.statsDataSelOtherRemoveDataButton.clicked.connect(
            lambda: self.remove_button_clicked(self.ui.statsDataSelOtherDataTable))

        self.ui.statsDataSelCheckButton.clicked.connect(self.check_data_button_clicked)
        self.ui.statsDataSelApplyIntButton.clicked.connect(self.apply_interactions_button_clicked)
        self.ui.statsDataSelCheckCheckbox.clicked.connect(
            lambda: self.verify_checkbox_clicked(self.ui.statsDataSelCheckCheckbox))
        self.ui.statsDataSelApplyIntCheckbox.clicked.connect(
            lambda: self.verify_checkbox_clicked(self.ui.statsDataSelApplyIntCheckbox))

        self.ui.statsDataSelTypeCombo.currentIndexChanged.connect(self.type_combo_changed)
        self.ui.statsDataSelSubtypeCombo.currentIndexChanged.connect(self.subtype_combo_changed)
        self.ui.statsDataSelFreqCombo.currentIndexChanged.connect(self.freq_combo_changed)
        self.ui.statsDataSelNameCombo.currentIndexChanged.connect(self.name_column_combo_changed)
        self.ui.statsDataSelColumnCombo.currentIndexChanged.connect(self.name_column_combo_changed)
        self.ui.statsDataSelVarCombo.currentIndexChanged.connect(self.var_combo_changed)

    def set_tab_order(self):
        pass

    def refresh_button_clicked(self):
        guiutils.layout_reset(self.ui.statsDataSelDSGrid, self.ui.statsDataSelDS2Grid, self.ui.statsDataSelIntGrid,
                              self.ui.statsDataSelDepGrid, self.ui.statsDataSelIndepGrid, self.ui.statsDataSelRAAGrid,
                              self.ui.statsDataSelOtherGrid, self.ui.statsDataSelVerifyGrid)
        guiutils.set_disabled(False, self.ui.statsDataSelDSAddButton, self.ui.statsDataSelLoadFileButton,
                              self.ui.statsDataSelIntAddButton, self.ui.statsDataSelCheckButton,
                              self.ui.statsDataSelApplyIntButton)

        guiutils.combobox_dict_refresh(self.ui.statsDataSelTypeCombo, self.db.read_data_types())
        self.ui.statsDataSelBeginField.setDate(QtCore.QDate.currentDate())
        self.ui.statsDataSelEndField.setDate(QtCore.QDate.currentDate())
        guiutils.combobox_list_refresh(self.ui.statsDataSelVarCombo,
                                       [[x] for x in StatsData.StatsData.VAR_TYPE_LIST], False)
        guiutils.combobox_list_refresh(self.ui.statsDataSelPreImputeCombo,
                                       [[x] for x in PreImpute.PreImpute.IMPUTATION_LIST], False)
        self.update_pos_combo()

    def var_combo_changed(self):
        if self.ui.statsDataSelVarCombo.currentText() == "Other":
            trans_list = []
        elif self.ui.statsDataSelVarCombo.currentText() == "RAA":
            trans_list = Transform.Transform.RAA_TRANSFORM_LIST
        else:
            trans_list = Transform.Transform.TRANSFORM_LIST

        guiutils.combobox_list_refresh(self.ui.statsDataSelTransformCombo, [[s] for s in trans_list], False)

        self.update_pos_combo()

    def type_combo_changed(self):
        type_data_dict = self.ui.statsDataSelTypeCombo.currentData()

        if type_data_dict is None:
            self.ui.statsDataSelSubtypeCombo.clear()
        else:
            db_dict = self.db.data_subtypes_db_dict([None, None, type_data_dict["id"]])
            guiutils.combobox_dict_refresh(self.ui.statsDataSelSubtypeCombo, self.db.read_data_subtypes(db_dict))

    def subtype_combo_changed(self):
        subtype_data_dict = self.ui.statsDataSelSubtypeCombo.currentData()

        if subtype_data_dict is None:
            self.ui.statsDataSelFreqCombo.clear()
            self.ui.statsDataSelNameCombo.clear()
        else:
            db_dict = self.db.data_subtype_freq_db_dict([None, subtype_data_dict["id"]])
            guiutils.combobox_dict_refresh(self.ui.statsDataSelFreqCombo, self.db.read_data_subtype_freq(db_dict),
                                           "freq", include_blank=False)
            db_dict = self.db.data_meta_table_db_dict([subtype_data_dict["db_table_meta"]])
            dict_list = self.db.read_data_subtype_meta_table(db_dict)
            guiutils.combobox_dict_refresh(self.ui.statsDataSelNameCombo, dict_list, "ticker")

    def freq_combo_changed(self):
        freq = self.ui.statsDataSelFreqCombo.currentText()
        if freq == '':
            return

        db_dict = self.db.data_data_table_db_dict(
            [self.ui.statsDataSelSubtypeCombo.currentData()["db_data_table_prefix"],
             self.ui.statsDataSelTypeCombo.currentData()["db_data_table_midfix"], freq, None, None, True])
        guiutils.combobox_dict_refresh(self.ui.statsDataSelColumnCombo,
                                       self.db.read_data_or_meta_table_columns(data_data_table_db_dict=db_dict),
                                       text_key="Field", tool_tip_key="Type")

        display_format = self.ui.statsDataSelFreqCombo.currentData()["format_str"]
        self.ui.statsDataSelBeginField.setDisplayFormat(display_format)
        self.ui.statsDataSelEndField.setDisplayFormat(display_format)

    # column and name both change both date field ranges
    def name_column_combo_changed(self):
        column = self.ui.statsDataSelColumnCombo.currentText()

        if '' in [self.ui.statsDataSelNameCombo.currentText(), column]:
            min_date = QtCore.QDateTime.currentDateTime()
            max_date = QtCore.QDateTime.currentDateTime()
        else:
            data_type_data = self.ui.statsDataSelTypeCombo.currentData()

            db_dict = self.db.data_data_table_db_dict(
                [self.ui.statsDataSelSubtypeCombo.currentData()["db_data_table_prefix"],
                 data_type_data["db_data_table_midfix"], self.ui.statsDataSelFreqCombo.currentText(), column,
                 self.ui.statsDataSelNameCombo.currentData(), None, data_type_data["db_table_meta"]])
            min_max_list = self.db.read_data_data_table_min_max_date(db_dict)

            if min_max_list[0] is None:
                min_date = QtCore.QDateTime.currentDateTime()
                max_date = QtCore.QDateTime.currentDateTime()
            else:
                min_date = min_max_list[0]
                max_date = min_max_list[1]

                if not isinstance(min_date, datetime.datetime):
                    min_date = datetime.datetime(min_date.year, min_date.month, min_date.day)
                    max_date = datetime.datetime(max_date.year, max_date.month, max_date.day)

        self.ui.statsDataSelBeginField.setMinimumDateTime(min_date)
        self.ui.statsDataSelBeginField.setMaximumDateTime(max_date)
        self.ui.statsDataSelBeginField.setDateTime(min_date)

        self.ui.statsDataSelEndField.setMinimumDateTime(min_date)
        self.ui.statsDataSelEndField.setMaximumDateTime(max_date)
        self.ui.statsDataSelEndField.setDateTime(max_date)

    def update_pos_combo(self):
        if self.ui.statsDataSelVarCombo.currentText() == "Dep":
            num_rows = self.ui.statsDataSelDepDataTable.rowCount()
        elif self.ui.statsDataSelVarCombo.currentText() == "Indep":
            num_rows = self.ui.statsDataSelIndepDataTable.rowCount()
        elif self.ui.statsDataSelVarCombo.currentText() == "Other":
            num_rows = self.ui.statsDataSelOtherDataTable.rowCount()
        else:
            num_rows = self.ui.statsDataSelRAADataTable.rowCount()

        num_lol = [[str(x + 1)] for x in range(num_rows + 1)]
        guiutils.combobox_list_refresh(self.ui.statsDataSelPosCombo, num_lol[::-1], False)

    # checkbox will change value but not by user action
    # the value of the checkbox is changed before this function is called. this function undoes the change
    def verify_checkbox_clicked(self, cb):
        cb.setChecked(not cb.isChecked())

    def update_verify(self, data_check=None, inter_check=None):
        if data_check is not None:
            self.ui.statsDataSelCheckCheckbox.setChecked(data_check)
            self.ui.statsDataSelApplyIntCheckbox.setChecked(False)

        if inter_check is not None:
            self.ui.statsDataSelApplyIntCheckbox.setChecked(inter_check)

    def ds_add_button_clicked(self):
        name = self.ui.statsDataSelNameCombo.currentText()
        column = self.ui.statsDataSelColumnCombo.currentText()
        if '' in [name, column]:
            return

        freq = self.ui.statsDataSelFreqCombo.currentText()
        begin_date = guiutils.qdate_to_db_string(self.ui.statsDataSelBeginField.dateTime())
        end_date = guiutils.qdate_to_db_string(self.ui.statsDataSelEndField.dateTime())

        data_type_data = self.ui.statsDataSelTypeCombo.currentData()
        data_subtype_data = self.ui.statsDataSelSubtypeCombo.currentData()

        stats_data = StatsData.StatsData(
            name, column, self.ui.statsDataSelTransformCombo.currentText(),
            [self.ui.statsDataSelPreImputeCombo.currentText(), self.ui.statsDataSelPreImputeField.text()],
            self.ui.statsDataSelVarCombo.currentText(), self.ui.statsDataSelTypeCombo.currentText(),
            data_type_data["db_table_meta"], data_type_data["db_data_table_midfix"],
            self.ui.statsDataSelSubtypeCombo.currentText(), data_subtype_data["db_table_meta"],
            data_subtype_data["db_data_table_prefix"], self.ui.statsDataSelNameCombo.currentData(), None, freq,
            begin_date, end_date)

        if not self.raa_valid(stats_data):
            return

        db_dict = self.db.data_data_table_db_dict(
            [stats_data.db_data_table_prefix, stats_data.db_data_table_midfix, stats_data.freq,
             stats_data.column, stats_data.name_data_dict, None, stats_data.type_db_table_meta,
             stats_data.db_begin_date, stats_data.db_end_date])
        try:
            stats_data.set_data_series(self.db.read_data_data_table(db_dict),
                                       db_type=self.ui.statsDataSelColumnCombo.currentData().get("Type", None))
        except Exception as e:
            guiutils.show_error_msg("Add Data Error", str(e))
            return

        self.add_row_to_table(stats_data)

    # csv file
    # first line is name (required),column (required), freq, data type
    #   freq in [, 1D, 5M, etc.] (same format as database frequency), required if data is time series
    #   data type in ["", "float", "str", "int"], blank is identity
    # all other lines are data
    # first column is date_time (YYYY-MM-DD hh:mm:ss) or data
    # second column is data if first column is date_time
    def load_file_button_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory("modelviews/loadfile")
        filename = dialog.getOpenFileName()[0]

        if filename == '':
            return

        data_lol = []
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data_lol.append(row)
        except Exception as e:
            guiutils.show_error_msg("Load File Error", str(e))
            return

        name = data_lol[0][0]
        column = data_lol[0][1]
        freq = data_lol[0][2]
        dt_func = data_lol[0][3]
        data_lol.pop(0)

        freq_list = self.db.read_data_freq()
        freq_list = [d["freq"] for d in freq_list]
        if freq not in freq_list + ['']:
            guiutils.show_error_msg("Load File Error", "Frequency must be in " + str(freq_list + ['']))
            return

        if freq == '':
            freq = None

        stats_data = StatsData.StatsData(
            name, column, self.ui.statsDataSelTransformCombo.currentText(),
            [self.ui.statsDataSelPreImputeCombo.currentText(), self.ui.statsDataSelPreImputeField.text()],
            self.ui.statsDataSelVarCombo.currentText(), file_name=filename, freq=freq)

        if not self.raa_valid(stats_data):
            return

        try:
            stats_data.set_data_series(data_lol, dt_func)
        except Exception as e:
            guiutils.show_error_msg("Add Data Error", str(e))
            return

        self.add_row_to_table(stats_data)

    def raa_valid(self, new_stats_data):
        if not new_stats_data.is_raa():
            return True

        for r in range(self.ui.statsDataSelRAADataTable.rowCount()):
            stats_data = self.ui.statsDataSelRAADataTable.item(r, 0).data(QtCore.Qt.UserRole)

            if new_stats_data.name != stats_data.name or new_stats_data.column != stats_data.column or\
                    new_stats_data.freq == stats_data.freq:
                guiutils.show_error_msg("RAA Error", "RAA must have same name and column but different frequency than "
                                                     "all existing RAA")
                return False

        return True

    def add_row_to_table(self, stats_data):
        if stats_data.var == "RAA":
            if not stats_data.data_series_is_time_series():
                guiutils.show_error_msg("RAA Error", "RAA data must be a time series")
                return

            table = self.ui.statsDataSelRAADataTable
        elif stats_data.var == "Other":
            table = self.ui.statsDataSelOtherDataTable
        else:
            if not stats_data.data_series_is_time_series() and stats_data.transform.is_risk_adj_transform():
                guiutils.show_error_msg("Risk Adjust Error",
                                        "Data series must be a time series for risk adjust transform")
                return
            if stats_data.var == "Dep":
                table = self.ui.statsDataSelDepDataTable
            else:  # stats_data.var == "Indep":
                table = self.ui.statsDataSelIndepDataTable

        row_pos = int(self.ui.statsDataSelPosCombo.currentText()) - 1
        table.insertRow(row_pos)

        item = QtWidgets.QTableWidgetItem(str(stats_data.name))
        item.setData(QtCore.Qt.ToolTipRole, str(stats_data.type) + "\n" + str(stats_data.subtype))
        item.setData(QtCore.Qt.UserRole, stats_data)
        table.setItem(row_pos, 0, item)

        table.setItem(row_pos, 1, QtWidgets.QTableWidgetItem(str(stats_data.column)))

        item = QtWidgets.QTableWidgetItem(str(stats_data.num_obs_after_transform))
        item.setData(QtCore.Qt.ToolTipRole, str(stats_data.pre_imputed_begin_date) + "\n" +
                     str(stats_data.pre_imputed_end_date) + "\n" + str(stats_data.freq) + "\n# Obs before transform: "
                     + str(stats_data.num_obs_original))
        table.setItem(row_pos, 2, item)

        item = QtWidgets.QTableWidgetItem(stats_data.transform.transform)
        item.setData(QtCore.Qt.ToolTipRole, "# Obs Change: " + str(stats_data.transform.transform_cost()))
        table.setItem(row_pos, 3, item)

        table.setItem(row_pos, 4, QtWidgets.QTableWidgetItem(str(stats_data.num_missing_original)))

        item = QtWidgets.QTableWidgetItem(str(stats_data.pre_impute.pre_impute))
        item.setData(QtCore.Qt.ToolTipRole, "Special Value: " + str(stats_data.pre_impute.special_value))
        table.setItem(row_pos, 5, item)

        self.update_pos_combo()
        self.update_verify(data_check=False)

    def int_add_button_clicked(self):
        name = self.ui.statsDataSelIntNameField.text()
        int_eq = self.ui.statsDataSelIntIntField.text()
        is_dep = self.ui.statsDataSelIntCheckbox.isChecked()

        if '' in [name, int_eq]:
            return

        if is_dep:
            if self.ui.statsDataSelDepIntTable.rowCount() > 0:
                return

            table = self.ui.statsDataSelDepIntTable
            data_table = self.ui.statsDataSelDepDataTable
        else:
            table = self.ui.statsDataSelIndepIntTable
            data_table = self.ui.statsDataSelIndepDataTable

            for r in range(table.rowCount()):
                if name == table.item(r, 0).text():
                    return

        equation = Equation.Equation(name, False)
        error_msg = equation.infix_str_to_postfix_list(int_eq)
        if error_msg is None:
            error_msg = equation.check_variable_count(data_table.rowCount())
            if error_msg is not None:
                error_msg += " Need more data rows"

        if error_msg is not None:
            guiutils.show_error_msg("Interaction Equation Error", error_msg)
            return

        row_pos = table.rowCount()
        table.insertRow(table.rowCount())

        item = QtWidgets.QTableWidgetItem(equation.equation_name)
        item.setData(QtCore.Qt.UserRole, equation)
        table.setItem(row_pos, 0, item)
        table.setItem(row_pos, 1, QtWidgets.QTableWidgetItem(equation.infix_str))

        self.update_verify(inter_check=False)

    def remove_button_clicked(self, table, is_data_table=True):
        rows = []
        for sel_row in table.selectionModel().selectedRows():
            rows.append(sel_row.row())

        if len(rows) == 0:
            return

        rows.sort(reverse=True)
        # need selection in order of greatest to least in order to properly remove rows
        for r in rows:
            table.removeRow(r)

        table.clearSelection()

        self.update_pos_combo()

        if is_data_table:
            self.update_verify(data_check=False)
        else:
            self.update_verify(inter_check=False)

    def check_data_button_clicked(self):
        error_msg_list = []
        sugg_msg_list = []

        dep_stats_data_list = []
        indep_stats_data_list = []
        other_stats_data_list = []
        raa_stats_data_list = []

        for lt in [[dep_stats_data_list, self.ui.statsDataSelDepDataTable],
                   [indep_stats_data_list, self.ui.statsDataSelIndepDataTable],
                   [raa_stats_data_list, self.ui.statsDataSelRAADataTable],
                   [other_stats_data_list, self.ui.statsDataSelOtherDataTable]]:
            for r in range(lt[1].rowCount()):
                lt[0].append(lt[1].item(r, 0).data(QtCore.Qt.UserRole))

        if 0 in [len(dep_stats_data_list), len(indep_stats_data_list)]:
            error_msg_list.append('Dependent and Independent data tables must each have at least 1 row.')

        # check #obs is the same for dependent and independent data
        obs_set = set()
        freq_set = set()
        req_raa = False
        for stats_data in dep_stats_data_list + indep_stats_data_list:
            obs_set.add(stats_data.num_obs_after_transform)
            freq_set.add(stats_data.freq)
            if stats_data.transform.is_risk_adj_transform():
                req_raa = True

        if len(freq_set) > 1:
            sugg_msg_list.append('Different frequencies among dependent and independent variables')

        if len(obs_set) > 1:
            error_msg_list.append('# obs must be equal across dependent and independent variables')
        elif req_raa and self.ui.statsDataSelRAADataTable.rowCount() == 0:
            error_msg_list.append('Risk adjust transform requires risk adjust asset to be selected')
        else:
            err_list = []

            if req_raa:
                for stats_data in raa_stats_data_list:
                    e_list, sugg_list = stats_data.check_apply_transform()
                    err_list += e_list
                    sugg_msg_list += sugg_list
            error_msg_list += err_list

            # do transforms after raa is correctly transformed
            if len(err_list) == 0:
                force_match = self.ui.statsDataSelForceMatchCheckbox.isChecked()
                for stats_data in dep_stats_data_list + indep_stats_data_list:
                    err_list, sugg_list = stats_data.check_apply_transform(raa_stats_data_list, force_match)
                    error_msg_list += err_list
                    sugg_msg_list += sugg_list

            # detailed check dates after all transforms correctly applied
            if len(error_msg_list) == 0:
                err_list, sugg_list = self.check_dep_indep_dates_match(
                    dep_stats_data_list + indep_stats_data_list)
                error_msg_list += err_list
                sugg_msg_list += sugg_list

        msg = "Errors:"
        for s in error_msg_list:
            msg = msg + "\n  " + s
        msg += "\n\nSuggestions:"
        for s in sugg_msg_list:
            msg = msg + "\n  " + s

        guiutils.show_error_msg("Check Selection Report", msg)

        self.update_verify(data_check=len(error_msg_list) == 0)

    # Data Suggestions:
    #   TODO check for gaps within data rows - these are probably not intended but statistics can still be run if # obs
    #       is same across all data rows
    #   check for gaps at begin/end of data rows - these are probably intended as lags
    def check_dep_indep_dates_match(self, stats_data_list):
        error_msg_list = []
        sugg_msg_list = []

        begin_date_set = set()
        end_date_set = set()
        for stats_data in stats_data_list:
            begin_date_set.add(stats_data.transformed_begin_date)
            end_date_set.add(stats_data.transformed_end_date)

        for ss in [[begin_date_set, "Begin"], [end_date_set, "End"]]:
            if len(ss[0]) > 1:
                sugg_msg_list.append(ss[1] + " dates do not match for all rows. Are lags intended?")

        return error_msg_list, sugg_msg_list

    def apply_interactions_button_clicked(self):
        error_msg_list = []
        sugg_msg_list = []
        dep_int_list = []
        indep_int_list = []

        for lt in [[dep_int_list, self.ui.statsDataSelDepIntTable],
                   [indep_int_list, self.ui.statsDataSelIndepIntTable]]:
            for r in range(lt[1].rowCount()):
                lt[0].append(lt[1].item(r, 0).data(QtCore.Qt.UserRole))

        if 0 in [len(dep_int_list), len(indep_int_list)]:
            error_msg_list.append('Dependent and Independent interaction tables must each have at least 1 row.')

        if self.ui.statsDataSelCheckCheckbox.isChecked():
            dep_series_data_list = []
            indep_series_data_list = []

            for lt in [[dep_series_data_list, self.ui.statsDataSelDepDataTable],
                       [indep_series_data_list, self.ui.statsDataSelIndepDataTable]]:
                for r in range(lt[1].rowCount()):
                    lt[0].append(lt[1].item(r, 0).data(QtCore.Qt.UserRole).transformed_data_series)

            for iv in [[dep_int_list, dep_series_data_list], [indep_int_list, indep_series_data_list]]:
                for equation in iv[0]:
                    err_list = equation.evaluate_equation(iv[1], False, True)
                    error_msg_list += err_list
        else:
            error_msg_list.append("Data must be checked before interactions can be applied.")

        msg = "Errors:"
        for s in error_msg_list:
            msg = msg + "\n  " + s
        msg += "\n\nSuggestions:"
        for s in sugg_msg_list:
            msg = msg + "\n  " + s

        guiutils.show_error_msg("Apply Interactions Report", msg)

        self.update_verify(inter_check=len(error_msg_list) == 0)

    def get_data_from_tables_external(self, ignore_verify=False, dep=True, indep=True, raa=True, other=True):
        if not ignore_verify and not self.ui.statsDataSelApplyIntCheckbox.isChecked():
            return None

        data_lol = guiutils.table_data([self.ui.statsDataSelDepDataTable, self.ui.statsDataSelIndepDataTable,
                                        self.ui.statsDataSelRAADataTable, self.ui.statsDataSelOtherDataTable,
                                        self.ui.statsDataSelDepIntTable, self.ui.statsDataSelIndepIntTable])

        data_dict = {}
        if dep:
            data_dict["dep_data"] = data_lol[0]
            data_dict["dep_int"] = data_lol[4]
        if indep:
            data_dict["indep_data"] = data_lol[1]
            data_dict["indep_int"] = data_lol[5]
        if raa:
            data_dict["raa_data"] = data_lol[2]
        if other:
            data_dict["other_data"] = data_lol[3]

        return data_dict