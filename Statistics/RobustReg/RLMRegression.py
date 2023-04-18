from Statistics.Regression import Regression, RegrType
from Statistics.RobustReg.RLMModelParams import RLMModelParams
from Statistics.RobustReg.RLMFitParams import RLMFitParams
import statsmodels.api as sm


class RLMRegression(Regression):

    def __init__(self, regr_type):
        self.fit = None

        if regr_type != RegrType.RLM:
            raise ValueError(str(regr_type) + " not valid")

        super().__init__(regr_type, RLMModelParams(), RLMFitParams())

    def prepare_sm_model(self, endog, exog, add_const=False):
        super().prepare_sm_model(endog, exog, add_const)

        mp = self.model_params
        self.sm_model = sm.RLM(self.endog, self.exog, mp.m_estimator(), mp.missing())

    def fit_sm_model(self):
        super().fit_sm_model()

        num_vars = self.exog.shape[1]
        fp = self.fit_params
        self.fit = fp.fit()

        self.sm_results = self.sm_model.fit(fp.max_iter(), fp.tol(), fp.scale_est(), fp.init(), fp.cov(),
                                            fp.update_scale(), fp.conv(), fp.start_params(num_vars))

    def sm_results_summary(self):
        return super().sm_results_summary()