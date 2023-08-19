import statsmodels.api as sm

from ..params import Params


class RLMFitParams(Params):

    _RLM_AVAILABLE_FIT_PARAMS_DICT = {
        "fit": ["", ["Fit"]],
        "conv": ["", ["dev", "coefs", "weights", "sresid"]],
        "cov": ["", ["H1", "H2", "H3"]],
        "maxiter": ["", (int, 1, True, 100000, True, 50, 0)],
        "tol": ["", (float, 0.0000000000, False, 1.0000000000, True, 0.0000000100, 10)],
        "update_scale": ["", ["True", "False"]],
        "start_params": ["", ("array", float)],
        "scale_est": ["", ["mad", "HuberScale"]],
        "huberscale_d": ["", (float, 0.00, False, 100.00, True, 2.50, 2)],
        "huberscale_tol": ["", (float, 0.0000000000, False, 1.0000000000, True, 0.0000000100, 10)],
        "huberscale_maxiter": ["", (int, 1, True, 100000, True, 30, 0)]
    }

    def __init__(self):
        super().__init__(self._RLM_AVAILABLE_FIT_PARAMS_DICT)

    def fit(self):
        return self.check_list("fit")

    def conv(self):
        return self.check_list("conv")

    def cov(self):
        return self.check_list("cov")

    def init(self):
        return None

    def max_iter(self):
        return self.check_numeric_range("maxiter")

    def tol(self):
        return self.check_numeric_range("tol")

    def update_scale(self):
        return self.check_bool_list("update_scale")

    def start_params(self, num_vars):
        if self.param_dict.get("start_params", None) is None:
            return None

        start_array = self.array_to_np_array(self.param_dict["start_params"],
                                             self.available_param_dict["start_params"][1][1])

        if start_array.size != num_vars:
            raise ValueError("start params array must have " + str(num_vars) + " values")

        return start_array

    def scale_est(self):
        scale = self.check_list("scale_est")
        if scale == "HuberScale":
            d = self.check_numeric_range("huberscale_d")
            tol = self.check_numeric_range("huberscale_tol")
            max_iter = self.check_numeric_range("huberscale_maxiter")
            scale = sm.robust.HuberScale(d, tol, max_iter)

        return scale