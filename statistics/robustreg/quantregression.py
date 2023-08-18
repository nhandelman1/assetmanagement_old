from statistics.Regression import Regression, RegrType
from statistics.RobustReg.QRModelParams import QRModelParams
from statistics.RobustReg.QRFitParams import QRFitParams
import statsmodels.api as sm


class QuantRegression(Regression):

    def __init__(self, regr_type):
        self.fit = None

        if regr_type != RegrType.QUANT_REG:
            raise ValueError(str(regr_type) + " not valid")

        super().__init__(regr_type, QRModelParams(), QRFitParams())

    def prepare_sm_model(self, endog, exog, add_const=False):
        super().prepare_sm_model(endog, exog, add_const)

        self.sm_model = sm.QuantReg(self.endog, self.exog)

    def fit_sm_model(self):
        super().fit_sm_model()

        fp = self.fit_params
        self.fit = fp.fit()

        self.sm_results = self.sm_model.fit(fp.quantile(), fp.vcov(), fp.kernel(), fp.bandwidth(), fp.max_iter(),
                                            fp.p_tol())

    def sm_results_summary(self):
        return super().sm_results_summary()