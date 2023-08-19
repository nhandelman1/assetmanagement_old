from enum import Enum

import pandas as pd
import statsmodels.api as sm


class RegrType(Enum):
    OLS = "Ordinary Least Squares",
    WLS = "Weighted Least Squares",
    GLS = "Generalized Least Squares",
    GLSAR = "Gneralized Least Squares AR Covariance",
    QUANT_REG = "Quantile Regression",
    RLM = "Robust Linear Models"

    def __init__(self, ls_type):
        self.ls_type = ls_type

    @staticmethod
    def to_lol():
        return [[x.ls_type, x] for x in RegrType]


########################################################################################################################
# class Regression
# statsmodels regression functions: OLS, WLS, GLS, GLSAR, RobustReg, Robust Linear Model (Robust Regression),
#
# Use pandas dataframe or numpy array for statsmodels data type 'array_like'. do not use python list
########################################################################################################################
class Regression:

    # endog, exog: either dict with key (variable name) and value (pandas series) or dataframe
    def __init__(self, regr_type, model_params=None, fit_params=None):
        self.reg_type = regr_type
        self.model_params = model_params
        self.fit_params = fit_params
        self.endog = None
        self.exog = None
        self.sm_model = None
        self.sm_results = None

    @property
    def endog(self):
        return self._endog

    @endog.setter
    def endog(self, endog):
        if isinstance(endog, dict):
            self._endog = pd.DataFrame(endog)
        else:
            self._endog = endog

    @property
    def exog(self):
        return self._exog

    @exog.setter
    def exog(self, exog):
        if isinstance(exog, dict):
            self._exog = pd.DataFrame(exog)
        else:
            self._exog = exog

    def add_constant(self):
        if self.endog is not None:
            self.endog = sm.add_constant(self.endog)

    # might need to be overridden. not sure
    def prepare_sm_model(self, endog, exog, add_const=False):
        self.endog = endog
        self.exog = exog

        if self.endog is None or self.exog is None:
            self.sm_model = None
            self.sm_results = None
            raise ValueError("endog and/or exog not set")
        elif add_const:
            self.exog = sm.add_constant(self.exog)

    # this needs to be overridden and probably called first by subclasses
    def fit_sm_model(self):
        if self.endog is None or self.exog is None:
            self.sm_model = None
            self.sm_results = None
            raise ValueError("endog and/or exog not set")

    # May consider overriding this function
    def sm_results_summary(self):
        try:
            return None if self.sm_results is None else self.sm_results.summary()
        except NotImplementedError:
            return type(self.sm_results).__name__ + " does not have a summary() function implemented"
