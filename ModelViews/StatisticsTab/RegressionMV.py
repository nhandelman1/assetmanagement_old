from Statistics.Regression import RegrType
from Statistics.LeastSquaresReg.LSRegression import LSRegression
from Statistics.RobustReg.QuantRegression import QuantRegression
from Statistics.RobustReg.RLMRegression import RLMRegression
from ModelViews import GUIUtils
from PyQt5 import QtWidgets, QtCore

'''

all regressions:
    prediction and prediction interval

    save results

multiple linear regression:
    r^2 and r
    individual tests on coefficients
    F-test on all coefficients

    check linearity with respect to each predictor variable
        residuals vs each predictor variable

    check constant variance of residuals across fitted values
        residuals vs fitted values
        constant variance f-test
        modified levene test / brown forsythe test
        white test
        breusch-pagan test / cook-weisberg score test
        bartlett's test

    check normality
        qq plot of residuals or density estimates
        d'agostino k-squared test
        jarque-bera test
        anderson-darling test
        cramer von mises criterion
        kolmogorov-smirnov test / lillifors test
        shapiro-wil test

    check for autocorrelation or time trends
        time series plot of residuals
        autocorrelations with respect to sample size
        durbin-watson test
        ljung-box test
        breusch-godfrey test

    omitted variables:
        residuals vs omitted predictor variables - a pattern indicates omitted variables should be included in the model

    influential observations
        standardized scatter plot
        cook distance

    multicollinearity - predictor variables are linearly dependent, can cause numerical issues (during inversion),
        can cause statistical issues (coefficients not robust to small changes in data, coefficients insignificant due
        to large standard errors even if F-test is significant)
        correlation matrix between predictor variables (for bivariate linear dependence)
        variance inflation factors - for each predictor variable, diagonal elements of inverse correlation matrix,
            r^2 for a single predictor variable regressed on the remaining predictor variables, high r^2 indicates
            linear dependence, r^2 > 0.9 implies vif > 10

    comparison across models:
        adjusted r^2
        AIC and BIC
        Mallows Cp
        Hannan-Quinn information criterion






'''
class RegressionMV:

    def __init__(self, ui, db, parent):
        self.ui = ui
        self.db = db
        self.parent = parent

        self.regression_obj = None

        self.init_class()

    def init_class(self):
        self.set_tab_order()

        self.ui.statsRegRefreshButton.clicked.connect(self.refresh_button_clicked)
        self.ui.statsRegFitButton.clicked.connect(self.fit_button_clicked)

        self.ui.statsRegRegCombo.currentIndexChanged.connect(self.reg_combo_changed)

    def set_tab_order(self):
        pass

    def refresh_button_clicked(self):
        self.regression_obj = None

        GUIUtils.combobox_list_refresh(self.ui.statsRegRegCombo, RegrType.to_lol())

    def reg_combo_changed(self):
        regr_type = self.ui.statsRegRegCombo.currentData()

        if regr_type is None or regr_type[0] == "":
            self.regression_obj = None
        else:
            regr_type = regr_type[0]

            if regr_type in [RegrType.OLS, RegrType.WLS, RegrType.GLS, RegrType.GLSAR]:
                self.regression_obj = LSRegression(regr_type)
            elif regr_type == RegrType.QUANT_REG:
                self.regression_obj = QuantRegression(regr_type)
            elif regr_type == RegrType.RLM:
                self.regression_obj = RLMRegression(regr_type)
            else:
                GUIUtils.show_error_msg("Regression Type Error", self.ui.statsRegRegCombo.currentText() + " invalid")

        self.set_param_table(self.ui.statsRegModelParamTable, True)
        self.set_param_table(self.ui.statsRegFitParamTable, False)

    def set_param_table(self, table, is_model=True):
        if self.regression_obj is None:
            table.setRowCount(0)
            return

        if is_model:
            param_dict = self.regression_obj.model_params.available_param_dict
        else:
            param_dict = self.regression_obj.fit_params.available_param_dict

        table.setRowCount(0)
        num_rows = len(param_dict)
        table.setRowCount(num_rows)

        for r, (k, v) in enumerate(param_dict.items()):
            item = QtWidgets.QTableWidgetItem(k)
            item.setData(QtCore.Qt.ToolTipRole, v[0])
            table.setItem(r, 0, item)

            widget = None

            if isinstance(v[1], list):
                widget = GUIUtils.q_combo_box_simple(v[1])
            elif isinstance(v[1], tuple):
                if v[1][0] in ["array", "matrix"]:
                    widget = QtWidgets.QLineEdit()
                    widget.setToolTip("Leave blank or enter 'other data row #' to load "
                                      + v[1][1].__name__ + " " + v[1][0])
                else:
                    # v = (type, begin, bool_inclusive_begin, end, bool_inclusive_end, default, decimals)
                    decimals = v[1][6]

                    step_val = 1 if decimals == 0 else float("0." + "0" * (decimals - 1) + "1")
                    minimum = v[1][1] if v[1][2] else v[1][1] + step_val
                    maximum = v[1][3] if v[1][4] else v[1][3] - step_val

                    widget = GUIUtils.q_double_spin_box(v[1][5], decimals, minimum, maximum, step_val=step_val)
            elif v[1] == str:
                widget = QtWidgets.QLineEdit()

            if widget is not None:
                table.setCellWidget(r, 1, widget)

    def fit_button_clicked(self):
        for td in [[self.ui.statsRegModelParamTable, self.regression_obj.model_params],
                   [self.ui.statsRegFitParamTable, self.regression_obj.fit_params]]:
            for r in range(td[0].rowCount()):
                key = td[0].item(r, 0).text()
                widget = td[0].cellWidget(r, 1)

                if isinstance(widget, QtWidgets.QLineEdit):
                    value = widget.text()




                elif isinstance(widget, QtWidgets.QComboBox):
                    value = widget.currentText()
                elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                    value = widget.value()
                else:
                    value = None

                td[1].set_value(key, value)

        print(self.regression_obj.fit_params.param_dict)