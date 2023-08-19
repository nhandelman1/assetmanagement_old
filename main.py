import dotenv
import os
import sys

from PyQt5 import QtWidgets
import numpy as np
import pandas as pd
import scipy.stats as spstats
import statsmodels.api as sm

from assetmanagement.modelviews.mainwindow import MainWindow
from assetmanagement.services.billanddatainput import BillAndDataInput
from assetmanagement.services.billanddatadisplay import BillAndDataDisplay
from assetmanagement.services.simple.model.simpleservicemodel import SimpleServiceModel
from assetmanagement.services.simple.view.simpleserviceconsoleui import SimpleServiceConsoleUI
from assetmanagement.services.mortgage.model.ms import MS
from assetmanagement.services.mortgage.view.msconsoleui import MSConsoleUI
from assetmanagement.services.electric.model.pseg import PSEG
from assetmanagement.services.electric.view.psegconsoleui import PSEGConsoleUI
from assetmanagement.services.electric.model.solar import Solar
from assetmanagement.services.electric.view.solarconsoleui import SolarConsoleUI
from assetmanagement.services.natgas.model.ng import NG
from assetmanagement.services.natgas.view.ngconsoleui import NGConsoleUI
from assetmanagement.services.depreciation.model.depreciationmodel import DepreciationModel
from assetmanagement.services.depreciation.view.depreciationconsoleui import DepreciationConsoleUI
from assetmanagement.services.utilitysavings import UtilitySavings
from assetmanagement.services.billreport import BillReport
from assetmanagement.util.consoleutil import print, input


def run_old():
    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()
    sys.exit(app.exec())

    x = np.random.standard_normal((1000, 2))
    x.flat[np.random.sample(2000) < 0.1] = np.nan

    def model_args_fn(x):
        # Return endog, exog from x
        return x[:, 0], x[:, 1:]

    imp = sm.BayesGaussMI(x)
    # mi = sm.MI(imp, sm.OLS, model_args_fn)

    index_list = ["2019-12-30", "2019-12-31", "2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05",
                  "2020-01-06", "2020-01-07", "2020-01-08", "2020-01-09"]
    index = ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07"]
    index2 = ["2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05", "2020-01-06", "2020-01-07", "2020-01-08"]
    Y = pd.DataFrame({"y1": [1, 3, 4, 5, 2, 3, 4]})
    x1 = pd.Series([1, 1, 6, 7, 1, 2, 3], index=pd.to_datetime(index))
    x2 = pd.Series([1, 2, np.nan, 5, 1, 7, 3], index=pd.to_datetime(index2))

    X1 = pd.DataFrame({"dig": x1})
    X2 = pd.DataFrame({"dig": x2})

    sm.qqplot(x1, spstats.norm, distargs=(), loc=x1.mean(), scale=x1.std(), line='45')

    '''
    eq = Equation("test", False)
    print(eq.infix_str_to_postfix_list("r1/r2"))
    print(str(eq.postfix_list))
    errors = eq.evaluate_equation([x1,x2], True, True)
    print(errors)
    print(eq.evaluated_result)
    '''

    '''
    res = PCA(X, ncomp=1, missing='fill-em')
    print(res._adjusted_data)

    data = sm.datasets.engel.load_pandas().data

    reg = RLMRegression(RegrType.RLM)
    reg.model_params.set_value("m_estimator", "RamsayE")

    reg.fit_params.set_value("scale_est", "HuberScale")
    reg.fit_params.set_value("huberscale_d", 5.0)
    reg.fit_params.set_value("huberscale_tol", 0.001)

    reg.prepare_sm_model(data["foodexp"], data["income"], True)
    print(reg.fit_sm_model())
    print(reg.sm_results_summary())
    '''


def run_bill_data_console():
    """ Bill and Data Console Input and Display Main Menu """
    bill_and_data_input = BillAndDataInput(SimpleServiceModel(), SimpleServiceConsoleUI(), MS(), MSConsoleUI(), Solar(),
                                           SolarConsoleUI(), PSEG(), PSEGConsoleUI(), NG(), NGConsoleUI(),
                                           DepreciationModel(), DepreciationConsoleUI())
    bill_and_data_display = BillAndDataDisplay(SimpleServiceModel(), SimpleServiceConsoleUI(), MS(), MSConsoleUI(),
                                               Solar(), SolarConsoleUI(), PSEG(), PSEGConsoleUI(), NG(), NGConsoleUI(),
                                               DepreciationModel(), DepreciationConsoleUI())
    bill_report = BillReport(SimpleServiceModel(), SimpleServiceConsoleUI(), MS(), MSConsoleUI(), Solar(),
                             SolarConsoleUI(), PSEG(), PSEGConsoleUI(), NG(), NGConsoleUI(), DepreciationModel(),
                             DepreciationConsoleUI())

    menu_str = "\n######################################################################" + \
               "\nChoose a bill or data option from the following:" + \
               "\n1: Input or Create Bills" + \
               "\n2: Display Bill Data" + \
               "\n3: Utility Savings Report - Reload " + os.getenv("FO_DIR") + " directory from disk to see file" + \
               "\n4: Yearly Bill Report" + \
               "\n0: Exit Program"

    while True:
        try:
            print(menu_str)
            opt = input("\nSelection: ", fcolor="blue")

            if opt == "1":
                bill_and_data_input.do_input_or_create_bill_process()
            elif opt == "2":
                bill_and_data_display.do_display_process()
            elif opt == "3":
                us = UtilitySavings(PSEG(), PSEGConsoleUI(), NG())
                us.do_process()
            elif opt == "4":
                bill_report.do_process()
            elif opt == "0":
                break
            else:
                print(opt + " is not a valid option. Try again.", fcolor="red")
        except Exception as ex:
            print(str(ex), fcolor="red")


# TODO standard project structure
# Run the function if this is the main file executed
if __name__ == "__main__":
    dotenv.load_dotenv()

    run_bill_data_console()