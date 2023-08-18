from statisticsam.params import Params
import statsmodels.robust.norms as smrn


class RLMModelParams(Params):

    _RLM_AVAILABLE_MODEL_PARAMS_DICT = {
        "m_estimator": ["", ["HuberT", "LeastSquares", "RamsayE", "AndrewWave", "TrimmedMean", "Hampel",
                             "TukeyBiweight"]],
        "tune1": ["Defaults are as follows. Huber: 1.345, LeastSquares:None, RamsayE: 0.3, AndrewWave:1.339, "
                  "TrimmedMean: 2.0, Hampel: 2.0, TukeyBiweight: 4.685. Any value less than 0 for default",
                  (float, -1.00, True, 100.00, True, -1.00, 2)],
        "tune2": ["Hampel only. Greater than tune1", (float, 0.00, True, 100.00, True, 4.00, 2)],
        "tune3": ["Hampel only. Greater than tune2", (float, 0.00, True, 100.00, True, 8.00, 2)],
        "missing": ["", ["none", "drop", "raise"]]
    }

    def __init__(self, available_model_params_dict=None):
        if available_model_params_dict is None:
            available_model_params_dict = self._RLM_AVAILABLE_MODEL_PARAMS_DICT

        super().__init__(available_model_params_dict)

    def m_estimator(self):
        m_est = self.check_list("m_estimator")
        tune1 = self.check_numeric_range("tune1")
        tune2 = self.check_numeric_range("tune2")
        tune3 = self.check_numeric_range("tune3")

        if m_est == "LeastSquares":
            return smrn.LeastSquares()
        elif m_est == "RamsayE":
            return smrn.RamsayE(tune1 if tune1 >= 0 else .3)
        elif m_est == "AndrewWave":
            return smrn.AndrewWave(tune1 if tune1 >= 0 else 1.339)
        elif m_est == "TrimmedMean":
            return smrn.TrimmedMean(tune1 if tune1 >= 0 else 2.)
        elif m_est == "Hampel":
            if tune1 <= 0.0:
                tune1 = 2.0
            if tune1 > tune2 or tune2 > tune3:
                raise ValueError("Hampel tuning parameters must be increasing non-negative")
            return smrn.Hampel(tune1, tune2, tune3)
        elif m_est == "TukeyBiweight":
            return smrn.TukeyBiweight(tune1 if tune1 >= 0 else 4.685)
        else:
            return smrn.HuberT(tune1 if tune1 >= 0 else 1.345)

    def missing(self):
        return self.check_list("missing")