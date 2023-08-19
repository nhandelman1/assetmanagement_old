import numpy as np
import pandas as pd
import scipy.stats as sp_stats

from assetmanagement.modelviews import guiutils
from assetmanagement.statisticsam.equation import Equation
from assetmanagement.statisticsam.statsdata import StatsData


'''
general: date range, num obs, num missing, freq, data type
location: mean, median, mode?
dispersion: std dev, med dev, range, percentiles, quartiles
other: skewness, kurtosis, correlation to certain benchmarks?, 
outliers: beyond 3 std devs 
time series components: stable, trend, seasonal (short term), random, cyclic (long term)
time series: autocorrelation coefficients

visuals: box and whisker, histogram
plots: scatter, standardized scatter, empirical (kernel) distribution, qq plot (and for other distributions), 
    time series plot, moving average vs raw plot, 
    

tests: data come from certain distributions?, independence,

tooltips: indicate too little data for accurate measures (e.g. kurtosis requires 50 for reliability)

ideas: any application of clustering?, 
'''


class DataExploreTabMV:

    def __init__(self, ui, db, parent):
        self.ui = ui
        self.db = db
        self.parent = parent

        self.current_data_series = None

        self.init_class()

    def init_class(self):
        self.set_tab_order()

        self.ui.statsExplRefreshButton.clicked.connect(self.refresh_button_clicked)
        self.ui.statsExplDisplayButton.clicked.connect(self.display_button_clicked)
        self.ui.statsExplTSMADisplayButton.clicked.connect(self.ts_ma_display_button_clicked)
        self.ui.statsExplTSEWMADisplayButton.clicked.connect(self.ts_ewma_display_button_clicked)
        self.ui.statsExplKDTDisplayButton.clicked.connect(self.kd_t_display_button_clicked)
        self.ui.statsExplQQTDisplayButton.clicked.connect(self.qq_t_display_button_clicked)

        self.ui.statsExplVarCombo.currentIndexChanged.connect(self.var_combo_changed)
        self.ui.statsExplRowCombo.currentIndexChanged.connect(self.row_combo_changed)

    def set_tab_order(self):
        pass

    def refresh_button_clicked(self):
        guiutils.layout_reset(self.ui.statsExplDSGrid)
        self.clear_data_and_plots()
        self.current_data_series = None

        data_dict = self.parent.get_data_selection_tab_tables_data(ignore_verify=True)

        data_list = []
        for key, value in data_dict.items():
            data_list.append([key, value])

        guiutils.combobox_list_refresh(self.ui.statsExplVarCombo, data_list)

    def clear_data_and_plots(self):
        guiutils.layout_reset(self.ui.statsExplSelGrid, self.ui.statsExplLocDispGrid, self.ui.statsExplPercentileGrid)
        guiutils.layout_clear(
            self.ui.statsExplBoxBWVert, self.ui.statsExplScatterScatterVert, self.ui.statsExplScatterStdVert,
            self.ui.statsExplTSMAVert, self.ui.statsExplTSEWMAVert, self.ui.statsExplKDNormVert,
            self.ui.statsExplKDTVert, self.ui.statsExplQQNormVert, self.ui.statsExplQQTVert)
        guiutils.layout_clear(
            self.ui.statsExplBoxBWToolVert, self.ui.statsExplScatterScatterToolVert,
            self.ui.statsExplScatterStdToolVert, self.ui.statsExplTSMAToolVert, self.ui.statsExplTSEWMAToolVert,
            self.ui.statsExplKDNormToolVert, self.ui.statsExplKDTToolVert, self.ui.statsExplQQNormToolVert,
            self.ui.statsExplQQTToolVert)

    def var_combo_changed(self):
        var_data_lol = self.ui.statsExplVarCombo.currentData()
        if var_data_lol is None:
            self.ui.statsExplRowCombo.clear()
        else:
            rows = [[str(x+1), var_data_lol[0][x]] for x in range(len(var_data_lol[0]))]
            guiutils.combobox_list_refresh(self.ui.statsExplRowCombo, rows, False)

    def row_combo_changed(self):
        stats_or_eq_data = self.ui.statsExplRowCombo.currentData()
        stage_lol = []

        if stats_or_eq_data is not None:
            stats_or_eq_data = stats_or_eq_data[0]

            if isinstance(stats_or_eq_data, StatsData):
                if stats_or_eq_data.original_data_series is not None:
                    stage_lol.append(["Original"])

                if stats_or_eq_data.pre_imputed_data_series is not None:
                    stage_lol.append(["Pre-Imputed"])

                if stats_or_eq_data.transformed_data_series is not None:
                    stage_lol.append(["Transformed"])
            elif isinstance(stats_or_eq_data, Equation):
                if stats_or_eq_data.evaluated_result is not None:
                    stage_lol.append(["Evaluation"])
            else:
                raise TypeError("Row Combo data must be StatsData or Equation")

        guiutils.combobox_list_refresh(self.ui.statsExplStageCombo, stage_lol, False)

    def display_button_clicked(self):
        stage = self.ui.statsExplStageCombo.currentText()
        if stage == "":
            return

        self.clear_data_and_plots()

        stats_or_eq_data = self.ui.statsExplRowCombo.currentData()[0]
        if stage == "Original":
            data_series = stats_or_eq_data.original_data_series
        elif stage == "Pre-Imputed":
            data_series = stats_or_eq_data.pre_imputed_data_series
        elif stage == "Transformed":
            data_series = stats_or_eq_data.transformed_data_series
        else:
            data_series = stats_or_eq_data.evaluated_result

        if isinstance(data_series, pd.Series):
            self.current_data_series = data_series
            self.set_general_fields(stats_or_eq_data, data_series)
            self.set_loc_disp_fields(data_series)
            self.set_percentile_fields(data_series)
            index = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07"]
            data_series = pd.Series([-50, 10, np.nan, -5, 15, 25, 50], index=pd.to_datetime(index))
            guiutils.plot_series_widget(self.ui.statsExplBoxBWVert, data_series, "box",
                                        toolbar_layout=self.ui.statsExplBoxBWToolVert)
            guiutils.plot_series_widget(self.ui.statsExplScatterScatterVert, data_series, "scatter",
                                        toolbar_layout=self.ui.statsExplScatterScatterToolVert)
            guiutils.plot_series_widget(self.ui.statsExplScatterStdVert, data_series, "scatter",
                                        option_dict={"standardize": None},
                                        toolbar_layout=self.ui.statsExplScatterStdToolVert)
            self.ts_ma_display_button_clicked()
            self.ts_ewma_display_button_clicked()
            guiutils.plot_series_widget(self.ui.statsExplKDNormVert, data_series, "density",
                                        {"density_compare": ["norm"]}, toolbar_layout=self.ui.statsExplKDNormToolVert)
            self.kd_t_display_button_clicked()
            guiutils.plot_series_widget(self.ui.statsExplQQNormVert, data_series, "qqplot",
                                        option_dict={"qqplot": ["norm"]},
                                        toolbar_layout=self.ui.statsExplQQNormToolVert)
            self.qq_t_display_button_clicked()
        else:
            guiutils.show_error_msg("Display Error", "Selected data must be a pandas Series")

    def set_general_fields(self, stats_or_eq_data, data_series):
        if isinstance(stats_or_eq_data, StatsData):
            label1 = stats_or_eq_data.name
            label2 = stats_or_eq_data.column
            freq = stats_or_eq_data.freq
        else:
            label1 = stats_or_eq_data.equation_name
            label2 = stats_or_eq_data.infix_str
            freq = ""

        self.ui.statsExplTableField.setText(self.ui.statsExplVarCombo.currentText())
        self.ui.statsExplRowField.setText(self.ui.statsExplRowCombo.currentText())
        self.ui.statsExplStageField.setText(self.ui.statsExplStageCombo.currentText())
        self.ui.statsExplNameField.setText(label1)
        self.ui.statsExplColIntField.setText(label2)
        self.ui.statsExplBeginField.setText(str(data_series.index.min()))
        self.ui.statsExplEndField.setText(str(data_series.index.max()))
        self.ui.statsExplFreqField.setText(freq)
        self.ui.statsExplDataTypeField.setText(str(data_series.dtype))
        self.ui.statsExplObsField.setText(str(data_series.size))
        self.ui.statsExplMissingField.setText(str(data_series.isnull().sum().sum()))

    def set_loc_disp_fields(self, data_series):
        rnd = self.ui.statsExplRoundSpin.value()

        self.ui.statsExplMeanField.setText(str(np.round(data_series.mean(), rnd)))
        self.ui.statsExplMedianField.setText(str(np.round(data_series.median(), rnd)))
        self.ui.statsExplSDField.setText(str(np.round(data_series.std(), rnd)))
        self.ui.statsExplMADField.setText(str(np.round(sp_stats.median_absolute_deviation(data_series, scale=1), rnd)))
        self.ui.statsExplSkewField.setText(str(np.round(data_series.skew(), rnd)))
        self.ui.statsExplKurtField.setText(str(np.round(data_series.kurt()+3, rnd)))

    def set_percentile_fields(self, data_series):
        rnd = self.ui.statsExplRoundSpin.value()

        self.ui.statsExplMaxField.setText(str(np.round(data_series.max(), rnd)))
        self.ui.statsExpl999PField.setText(str(np.round(data_series.quantile(0.999), rnd)))
        self.ui.statsExpl99PField.setText(str(np.round(data_series.quantile(0.99), rnd)))
        self.ui.statsExpl95PField.setText(str(np.round(data_series.quantile(0.95), rnd)))
        self.ui.statsExpl90PField.setText(str(np.round(data_series.quantile(0.9), rnd)))
        self.ui.statsExpl75PField.setText(str(np.round(data_series.quantile(0.75), rnd)))
        self.ui.statsExpl50PField.setText(str(np.round(data_series.quantile(0.5), rnd)))
        self.ui.statsExpl25PField.setText(str(np.round(data_series.quantile(0.25), rnd)))
        self.ui.statsExpl10PField.setText(str(np.round(data_series.quantile(0.10), rnd)))
        self.ui.statsExpl5PField.setText(str(np.round(data_series.quantile(0.05), rnd)))
        self.ui.statsExpl1PField.setText(str(np.round(data_series.quantile(0.01), rnd)))
        self.ui.statsExpl01PField.setText(str(np.round(data_series.quantile(0.001), rnd)))
        self.ui.statsExplMinField.setText(str(np.round(data_series.min(), rnd)))

    def ts_ma_display_button_clicked(self):
        if self.current_data_series is None:
            return
        guiutils.layout_clear(self.ui.statsExplTSMAVert, self.ui.statsExplTSMAToolVert)

        window = self.ui.statsExplTSMAWindowSpin.value()
        #data_series = self.current_data_series.rolling(window).mean()
        index = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07"]
        data_series = pd.Series([-50, 10, 0, -5, 15, 25, 50], index=pd.to_datetime(index))

        guiutils.plot_series_widget(self.ui.statsExplTSMAVert, data_series, "line",
                                    option_dict={"moving_average": window},
                                    toolbar_layout=self.ui.statsExplTSMAToolVert)

    def ts_ewma_display_button_clicked(self):
        if self.current_data_series is None:
            return
        guiutils.layout_clear(self.ui.statsExplTSEWMAVert, self.ui.statsExplTSEWMAToolVert)

        alpha = self.ui.statsExplTSEWMAAlphaSpin.value()
        #data_series = self.current_data_series.rolling(window).mean()
        index = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07"]
        data_series = pd.Series([-50, 10, 0, -5, 15, 25, 50], index=pd.to_datetime(index))

        guiutils.plot_series_widget(self.ui.statsExplTSEWMAVert, data_series, "line",
                                    option_dict={"ew_moving_average": alpha},
                                    toolbar_layout=self.ui.statsExplTSEWMAToolVert)

    def kd_t_display_button_clicked(self):
        if self.current_data_series is None:
            return
        guiutils.layout_clear(self.ui.statsExplKDTVert, self.ui.statsExplKDTToolVert)
        index = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07"]
        data_series = pd.Series([-50, 10, 0, -5, 15, 25, 50], index=pd.to_datetime(index))
        dof = self.ui.statsExplKDTDoFSpin.value()
        guiutils.plot_series_widget(self.ui.statsExplKDTVert, data_series, "density",
                                    option_dict={"density_compare": ["student-t", dof]},
                                    toolbar_layout=self.ui.statsExplKDTToolVert)

    def qq_t_display_button_clicked(self):
        if self.current_data_series is None:
            return
        guiutils.layout_clear(self.ui.statsExplQQTVert, self.ui.statsExplQQTToolVert)
        index = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07"]
        data_series = pd.Series([-50, 10, 0, -5, 15, 25, 50], index=pd.to_datetime(index))
        dof = self.ui.statsExplQQTDoFSpin.value()
        guiutils.plot_series_widget(self.ui.statsExplQQTVert, data_series, "qqplot",
                                    option_dict={"qqplot": ["student-t", dof]},
                                    toolbar_layout=self.ui.statsExplQQTToolVert)




























