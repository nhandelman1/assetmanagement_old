from PyQt5 import QtWidgets, QtCore
from database import dbdict
from database.mysqlold import MySQLOld
from database.dbdict import DBDict
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar2QT
import datetime
import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm

# textKey can be a list or a string
def combobox_dict_refresh(cb, dict_lists, text_key="name", tool_tip_key=None, include_blank=True):
    cb.clear()

    if include_blank:
        cb.addItem('', None)

    for d in dict_lists:
        if isinstance(text_key, list):
            text = ''
            for k in text_key:
                text = d[k] + ' - '
            cb.addItem(text[:-3], d)
        else:
            cb.addItem(d[text_key], d)

        if tool_tip_key is not None and d[tool_tip_key] is not None:
            cb.setItemData(cb.count() - 1, str(d[tool_tip_key]), QtCore.Qt.ToolTipRole)


# cb: QComboBox, data_lists: list of lists
def combobox_list_refresh(cb, data_lol, include_blank=True):
    cb.clear()
    if include_blank:
        cb.addItem('', ['', None])
    for row in data_lol:
        cb.addItem(row[0], row[1:])


# itemDataDict: dictionary in the cb's item data
# widgetkey_list: list of widget/key pair lists. keys are for itemDataDict
def combo_changed(item_data_dict, widget_key_list):
    for wk in widget_key_list:
        if item_data_dict is None:
            text = ''
        else:
            text = item_data_dict[wk[1]]

        if isinstance(wk[0], QtWidgets.QComboBox):
            wk[0].setCurrentIndex(wk[0].findText(text))
        elif isinstance(wk[0], (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
            wk[0].setText(text)


# assumes current data is a dictionary
def combo_data(combos, key_list=("id",)):
    if isinstance(combos, list):
        val_lol = []
        for c in combos:
            vals = []
            for k in key_list:
                if c.currentData() is None:
                    vals.append(None)
                else:
                    vals.append(c.currentData()[k])
            val_lol.append(vals)
        return val_lol
    else:
        vals = []
        for k in key_list:
            if combos.currentData() is None:
                vals.append(None)
            else:
                vals.append(combos.currentData()[k])
        return vals


def table_data(table_list, col=0):
    data_lol = []
    for table in table_list:
        data_list = []
        for r in range(table.rowCount()):
            data_list.append(table.item(r, col).data(QtCore.Qt.UserRole))
        data_lol.append(data_list)

    return data_lol


def add_up_button_clicked(widget, db_dict, insert_query=None, update_query=None, read_query=None, text_key="name"):
    for k in db_dict.keys:
        if db_dict.value_dict[k] in db_dict.reject_dict[k]:
            return

    res = "no action performed"
    if db_dict.value_dict["id"] is None:
        if insert_query is not None:
            res = insert_query(db_dict)
    elif update_query is not None:
        res = update_query(db_dict)

    complete = False
    if res is None:
        complete = True

        if read_query is not None:
            if isinstance(widget, QtWidgets.QComboBox):
                combobox_dict_refresh(widget, read_query(), text_key)
            elif isinstance(widget, QtWidgets.QTableWidget):
                populate_table(widget, read_query())
    elif res != "no action performed":
        show_error_msg("Insert/Update Error", res)

    return complete


def sec_sec_attach_detach_button_clicked(selected_comp_items, main_table, isAttach, db, comp_table):
    if len(selected_comp_items) == 0:
        return

    db_dict_list = []
    selected_main_dict = main_table.selectedItems()[0].data(QtCore.Qt.UserRole)

    for table_item in selected_comp_items:
        db_dict_list.append(MySQLOld.security_security_db_dict([None, selected_main_dict["securities_id"],
                                                               table_item.data(QtCore.Qt.UserRole)["securities_id"]]))

    if isAttach:
        res = db.attach_security_security(db_dict_list)
    else:
        res = db.detach_security_security(db_dict_list)
    if res is None:
        populate_table(comp_table, db.read_security_components(DBDict(val_dict=selected_main_dict)), ["ticker"])
    else:
        show_error_msg("Attach/Detach Error", res)


# column_headers can be False, True or list of headers. If False, the column headers are not changed. If True,
# column_headers are set to dict_keys (if dict_list is not None) or set to [1, 2, 3, ...] if data_lol is not None.
# If a list of headers is provided, the list must have the correct length, otherwise, column_headers assumed True.
def populate_table(table, dict_list=None, dict_keys=None, data_lol=None, column_headers=False):
    num_cols = 0
    col_headers = []

    if data_lol is None:
        which_list = dict_list
        num_rows = len(dict_list)

        if num_rows > 0:
            if dict_keys is None:
                dict_keys = list(dict_list[0])
            num_cols = len(dict_keys)
            col_headers = dict_keys
    else:
        which_list = data_lol
        num_rows = len(data_lol)

        if num_rows > 0:
            num_cols = len(data_lol[0])
            for c in range(1, num_cols+1):
                col_headers.append(str(c))

    table.clearSelection()

    if isinstance(column_headers, list) and len(column_headers) == num_cols:
        table.setColumnCount(num_cols)
        table.setHorizontalHeaderLabels(column_headers)
    elif column_headers is not False:
        table.setColumnCount(num_cols)
        table.setHorizontalHeaderLabels(col_headers)

    show_tooltip = num_cols > table.columnCount()

    table.setRowCount(num_rows)
    is_sort = table.isSortingEnabled()
    table.setSortingEnabled(False)
    for r in range(num_rows):
        for c in range(num_cols):
            if data_lol is None:
                ind = dict_keys[c]
            else:
                ind = c

            item = QtWidgets.QTableWidgetItem(str(which_list[r][ind]))
            if c == 0:
                item.setData(QtCore.Qt.UserRole, which_list[r])
            if show_tooltip and (c == 0 or c == 1):
                item.setData(QtCore.Qt.ToolTipRole, pop_tab_list_to_str(which_list[r], table.columnCount(), dict_keys))
            table.setItem(r, c, item)
    table.setSortingEnabled(is_sort)


def pop_tab_list_to_str(dict_or_list, count, keys):
    s = ""
    if keys is None:
        s = str(dict_or_list)
    else:
        for k in keys[count:]:
            s = s + k + ": " + str(dict_or_list[k]) + "\n"
        s = s[:-1]
    return s


def get_tab_names(tab_widget):
    data_list = []
    for i in range(tab_widget.count()):
        data_list.append((tab_widget.tabText(i),))
    return data_list


def clear(*widgets):
    for w in widgets:
        if isinstance(w, QtWidgets.QTableWidget):
            w.setRowCount(0)
        elif isinstance(w, QtWidgets.QCheckBox):
            w.setChecked(False)
        else:
            w.clear()


def set_disabled(disable, *widgets):
    for w in widgets:
        w.setDisabled(disable)


def layout_reset(*layout_list):
    if layout_list is not None:
        for layout in layout_list:
            for i in range(layout.count()):
                reset_widget(layout.itemAt(i).widget())


def reset_widget(w):
    if isinstance(w, QtWidgets.QComboBox):
        w.setCurrentIndex(0)
    elif isinstance(w, QtWidgets.QLineEdit):
        w.clear()
    elif isinstance(w, QtWidgets.QCheckBox):
        w.setChecked(False)
    elif isinstance(w, QtWidgets.QTableWidget):
        w.setRowCount(0)
    elif isinstance(w, QtWidgets.QGroupBox):
        for child_w in w.children():
            reset_widget(child_w)


def layout_clear(*layout_list):
    if layout_list is not None:
        for layout in layout_list:
            for i in reversed(range(layout.count())):
                w = layout.itemAt(i).widget()
                layout.removeWidget(w)
                w.setParent(None)
                w.deleteLater()


def set_current_index(widget, value):
    if isinstance(widget, QtWidgets.QComboBox):
        widget.setCurrentIndex(widget.findText(value))


def q_spin_box(value=0, minimum=0, maximum=99, change_func=None):
    spin = QtWidgets.QSpinBox()
    spin.setAlignment(QtCore.Qt.AlignRight)
    spin.wheelEvent = lambda *event: None
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    spin.setValue(value)  # set next to last. other setting need to be set first or value may be invalid
    if change_func is not None:
        spin.valueChanged.connect(change_func)  # set after setValue()
    return spin


def q_double_spin_box(value=0, decimal=2, minimum=0, maximum=99.99, change_func=None, step_val=None):
    spin = QtWidgets.QDoubleSpinBox()
    if step_val is None:
        spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
    else:
        spin.setSingleStep(step_val)

    spin.setAlignment(QtCore.Qt.AlignRight)
    spin.wheelEvent = lambda *event: None
    spin.setDecimals(decimal)
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    spin.setValue(value)  # set next to last. other setting need to be set first or value may be invalid
    if change_func is not None:
        spin.valueChanged.connect(change_func)  # set after setValue()
    return spin


def req_q_datetime(display_format):
    return " " in display_format


def q_date_edit(qdate=QtCore.QDate.currentDate(), change_func=None, min_qdate=None, max_qdate=None):
    de = QtWidgets.QDateEdit()

    if min_qdate is not None:
        de.setMinimumDate(min_qdate)
    if max_qdate is not None:
        de.setMaximumDate(max_qdate)

    de.setCalendarPopup(True)
    de.wheelEvent = lambda *event: None

    if de.minimumDate() < qdate < de.maximumDate():
        de.setDate(qdate)
    else:
        de.setDate(de.maximumDate())

    if change_func is not None:
        de.dateChanged.connect(change_func)  # set after setValue()
    return de


def q_date_time_edit(qdatetime=QtCore.QDateTime.currentDateTime(), change_func=None):
    dte = QtWidgets.QDateTimeEdit()
    dte.setCalendarPopup(True)
    dte.setDisplayFormat("yyyy-MM-dd hh:mm")
    dte.wheelEvent = lambda *event: None
    dte.setTime(QtCore.QTime())
    dte.setDateTime(qdatetime)
    if change_func is not None:
        dte.dateTimeChanged.connect(change_func)  # set after setValue()
    return dte


def q_combo_box_simple(value_list, sort=False):
    cb = QtWidgets.QComboBox()
    cb.addItems(value_list)
    if sort:
        cb.model().sort(0)
    return cb


def q_combo_box_complex(dict_list, text_key="name", tool_tip_key=None, sort=False):
    cb = QtWidgets.QComboBox()
    combobox_dict_refresh(cb, dict_list, text_key, tool_tip_key)
    if sort:
        cb.model().sort(0)
    return cb


def qdate_to_db_string(qdate):
    if isinstance(qdate, QtCore.QDate):
        return qdate.toString("yyyy-MM-dd")
    elif isinstance(qdate, QtCore.QDateTime):
        return qdate.toString("yyyy-MM-dd hh:mm:ss")
    else:
        return None


def db_string_to_qdatetime(date_str):
    format_str = "yyyy-MM-dd hh:mm:ss" if req_q_datetime(date_str) else "yyyy-MM-dd"
    return QtCore.QDateTime.fromString(date_str, format_str)


def db_string_to_pytdatetime(date_str):
    if " " in date_str:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")


def round_time_to_interval(datetime, freq):
    if freq == "5M":
        datetime = datetime.addSecs(-60 * (datetime.time().minute() % 5))

    return datetime


def plot_series_widget(canvas_layout, data_series, kind, option_dict=None, toolbar_layout=None):
    if option_dict is None:
        option_dict = {}

    figure = pyplot.figure(tight_layout=True)
    ax = figure.add_subplot()
    canvas = FigureCanvasQTAgg(figure)
    if toolbar_layout is not None:
        toolbar_layout.addWidget(NavigationToolbar2QT(canvas, None))
    canvas_layout.addWidget(canvas)

    data_series_list = []

    if "standardize" in option_dict:
        data_series = (data_series - data_series.mean()) / data_series.std()

    if "moving_average" in option_dict:
        window = option_dict["moving_average"]
        data_series_list.append(data_series.rolling(window).mean())

    if "ew_moving_average" in option_dict:
        alpha = option_dict["ew_moving_average"]
        data_series_list.append(data_series.ewm(alpha=alpha).mean())

    data_series_list.insert(0, data_series)

    for data_series in data_series_list:
        if kind in ["scatter"]:
            ax = data_series.to_frame("").reset_index().plot(kind=kind, x="index", y="", ax=ax)
        elif kind == "qqplot":
            dist = stats.norm
            dist_args = ()

            if "qqplot" in option_dict:
                qqplot_list = option_dict["qqplot"]

                if qqplot_list[0] == "norm":
                    dist = stats.norm
                elif qqplot_list[0] == "student-t":
                    dist = stats.t
                    dist_args = (qqplot_list[1],)

            sm.qqplot(data_series, dist, distargs=dist_args, loc=data_series.mean(), scale=data_series.std(),
                      line='45', ax=ax)
        else:
            ax = data_series.plot(kind=kind, ax=ax)

    if "density_compare" in option_dict:
        dist_list = option_dict["density_compare"]
        dist_series = None
        mean = data_series.mean()
        sd = data_series.std()

        if dist_list[0] == "norm":
            x_axis = np.linspace(mean - sd * 5, mean + sd * 5, 1000)
            dist_series = pd.Series(stats.norm.pdf(x_axis, mean, sd), index=x_axis)
        elif dist_list[0] == "student-t":
            x_axis = np.linspace(mean - sd * 5, mean + sd * 5, 1000)
            dist_series = pd.Series(stats.t.pdf(x_axis, dist_list[1], mean, sd), index=x_axis)

        if dist_series is not None:
            ax = dist_series.plot(kind="line", ax=ax)

    if "standardize" in option_dict:
        ax.axhline(3, color="red")
        ax.axhline(-3, color="red")

    canvas.draw()
    pyplot.close(figure)


def show_error_msg(title, msg):
    error_dialog = QtWidgets.QMessageBox()
    error_dialog.setWindowTitle(title)
    error_dialog.setText(msg)
    error_dialog.setDetailedText(msg)
    error_dialog.exec_()


def show_confirm_msg(title, msg):
    confirm_dialog = QtWidgets.QMessageBox()
    reply = confirm_dialog.question(None, title, msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                    QtWidgets.QMessageBox.No)

    return reply == QtWidgets.QMessageBox.Yes