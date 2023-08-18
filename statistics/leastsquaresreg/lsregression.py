from statistics.Regression import Regression, RegrType
from statistics.LeastSquaresReg.OLSModelParams import OLSModelParams
from statistics.LeastSquaresReg.WLSModelParams import WLSModelParams
from statistics.LeastSquaresReg.GLSModelParams import GLSModelParams
from statistics.LeastSquaresReg.GLSARModelParams import GLSARModelParams
from statistics.LeastSquaresReg.LSFitParams import LSFitParams

import statsmodels.api as sm


class LSRegression(Regression):

    def __init__(self, regr_type):
        self.fit = None

        if regr_type == RegrType.OLS:
            model_params = OLSModelParams()
        elif regr_type == RegrType.WLS:
            model_params = WLSModelParams()
        elif regr_type == RegrType.GLS:
            model_params = GLSModelParams()
        elif regr_type == RegrType.GLSAR:
            model_params = GLSARModelParams()
        else:
            raise ValueError(str(regr_type) + " not valid")

        super().__init__(regr_type, model_params, LSFitParams())

    def prepare_sm_model(self, endog, exog, add_const=False):
        super().prepare_sm_model(endog, exog, add_const)

        mp = self.model_params
        num_obs = self.exog.shape[0]
        if self.reg_type == RegrType.OLS:
            self.sm_model = sm.OLS(self.endog, self.exog, mp.missing(), mp.hasconst())
        elif self.reg_type == RegrType.WLS:
            self.sm_model = sm.WLS(self.endog, self.exog, mp.weights(num_obs), mp.missing(), mp.hasconst())
        elif self.reg_type == RegrType.GLS:
            self.sm_model = sm.GLS(self.endog, self.exog, mp.sigma(num_obs), mp.missing(), mp.hasconst())
        elif self.reg_type == RegrType.GLSAR:
            self.sm_model = sm.GLSAR(self.endog, self.exog, mp.rho(), mp.missing(), mp.hasconst())

    def fit_sm_model(self):
        super().fit_sm_model()

        fp = self.fit_params
        self.fit = fp.fit()
        if self.fit == "Regularized":
            num_vars = self.exog.shape[1]

            self.sm_results = self.sm_model.fit_regularized(
                fp.regularized_method(), fp.alpha(num_vars), fp.l1_wt(), fp.start_params(num_vars), fp.profile_scale(),
                fp.refit(), maxiter=fp.regularized_max_iter(), cnvrg_tol=fp.cnvrg_tol(), zero_tol=fp.zero_tol())
        elif self.fit == "Iterative":
            if self.reg_type != RegrType.GLSAR:
                raise ValueError("Iterative fit only allowed for GLSAR")

            self.sm_results = self.sm_model.iterative_fit(fp.iterative_max_iter(), fp.r_tol(), use_t=fp.use_t(),
                                                          cov_type=fp.cov_type(), cov_kwds=fp.cov_kwds_check(None))
        else:
            #TODO num_groups = ?
            num_groups = None
            self.sm_results = self.sm_model.fit(fp.fit_method(), fp.cov_type(), fp.cov_kwds_check(num_groups), fp.use_t())

    def sm_results_summary(self):
        return super().sm_results_summary()