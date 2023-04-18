from Statistics.LeastSquaresReg.LSRegression import LSRegression
from Statistics.RobustReg.RLMRegression import RLMRegression
from Statistics.Regression import RegrType
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.multivariate.pca import PCA
from statsmodels.imputation import mice
from PyQt5 import QtWidgets
import sys
from ModelViews.MainWindow import MainWindow
import datetime
import ModelViews.GUIUtils as GUIUtils
from Statistics.Equation import Equation
import scipy.stats as spstats
import matplotlib.pyplot as plt
from scipy.stats import t
from Statistics.Regression import RegrType

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
#mi = sm.MI(imp, sm.OLS, model_args_fn)

index_list = ["2019-12-30", "2019-12-31","2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05",
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