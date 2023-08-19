from ..params import Params


'''
Same Params for OLS, WLS, GLS, GLSAR
'''


class LSFitParams(Params):

    _OLS_AVAILABLE_FIT_PARAMS_DICT = {
        "fit": ["Only GLSAR uses iterative", ["Fit", "Regularized", "Iterative"]],
        "fit_method": ["MP Pseudo-Inverse, QR Decomposition", ["pinv", "qr"]],
        "cov_type": ["See statsmodels documentation", ["nonrobust", "fixed scale", "HCO", "HC1", "HC2", "HC3", "HAC",
                                                       "cluster"]],
        "fixed_scale_scale": ["", (float, -100.00, True, 100.00, True, 1.00, 2)],
        "hac_maxlag": ["", (int, 0, True, 100, True, 0, 0)],
        "hac_kernel": ["", ["bartlett", "uniform"]],
        "hac_cluster_use_correction": ["HAC and cluster", ["False", "True"]],
        "cluster_groups": ["", ("array", int)],
        "cluster_df_correction": ["", ["True", "False"]],
        "use_t": ["", ["None", "True", "False"]],
        "regularized_method": ["", ["elastic_net", "sqrt_lasso"]],
        "alpha": ["Penalty weight(s) for each exog variable in fit_regularized. One weight applied to all variables or "
                  "a weight given for each variable.", ("array", float)],
        "l1_wt": ["Inclusive [0,1]", (float, 0.000, True, 1.000, True, 1.000, 3)],
        "start_params": ["Starting value for each exog variable (incl. constant) in fit_regularized", ("array", float)],
        "profile_scale": ["", ["False", "True"]],
        "refit": ["", ["False", "True"]],
        "regularized_maxiter": ["", (int, 1, True, 100000, True, 50, 0)],
        "cnvrg_tol": ["", (float, 0.000000000000, False, 1.000000000000, True, 0.000000000100, 12)],
        "zero_tol": ["", (float, 0.0000000000, False, 1.0000000000, True, 0.0000000100, 10)],
        "iterative_maxiter": ["", (int, 1, True, 100000, True, 3, 0)],
        "r_tol": ["", (float, 0.0000000000, False, 1.0000000000, True, 0.0001000000, 10)]
    }

    def __init__(self):
        super().__init__(self._OLS_AVAILABLE_FIT_PARAMS_DICT)

    def fit_method(self):
        return self.check_list("fit_method")

    def cov_type(self):
        return self.check_list("cov_type")

    def use_t(self):
        return self.check_bool_none_list("use_t")

    def fit(self):
        return self.check_list("fit")

    def regularized_method(self):
        return self.check_list("regularized_method")

    # num_vars must include the constant
    def alpha(self, num_vars):
        alpha_array = self.array_to_np_array(self.param_dict.get("alpha", "0"),
                                             self.available_param_dict["alpha"][1][1])
        if alpha_array.size == 1:
            return alpha_array[0]

        if alpha_array.size != num_vars:
            raise ValueError("alpha array must have " + str(num_vars) + " values")

        return alpha_array

    def l1_wt(self):
        return self.check_numeric_range("l1_wt")

    # num_vars must include the constant
    def start_params(self, num_vars):
        if self.param_dict.get("start_params", None) is None:
            return None

        start_array = self.array_to_np_array(self.param_dict["start_params"],
                                             self.available_param_dict["start_params"][1][1])

        if start_array.size != num_vars:
            raise ValueError("start params array must have " + str(num_vars) + " values")

        return start_array

    def profile_scale(self):
        return self.check_bool_list("profile_scale")

    def refit(self):
        return self.check_bool_list("refit")

    def regularized_max_iter(self):
        return self.check_numeric_range("regularized_maxiter")

    def cnvrg_tol(self):
        return self.check_numeric_range("cnvrg_tol")

    def zero_tol(self):
        return self.check_numeric_range("zero_tol")

    def fixed_scale_scale(self):
        return self.check_numeric_range("fixed_scale_scale")

    def hac_maxlag(self):
        return self.check_numeric_range("hac_maxlag")

    def hac_kernel(self):
        return self.check_list("hac_kernel")

    def hac_cluster_use_correction(self):
        return self.check_bool_list("hac_cluster_use_correction")

    # num_groups must include the constant
    def cluster_groups(self, num_groups):
        cluster_array = self.array_to_np_array(self.param_dict("cluster_groups"),
                                               self.available_param_dict["cluster_groups"][1][1])

        if cluster_array.size != num_groups:
            raise ValueError("cluster groups array must have " + str(num_groups) + " values")

        return cluster_array

    def cluster_df_correction(self):
        return self.check_bool_list("cluster_df_correction")

    def cov_kwds_check(self, num_groups=None):
        cov_type = self.cov_type()
        kwds_dict = {}

        if cov_type == "fixed scale":
            kwds_dict["scale"] = self.fixed_scale_scale()
        elif cov_type == "HAC":
            kwds_dict["kernel"] = self.hac_kernel()
            kwds_dict["maxlags"] = self.hac_maxlag()
            kwds_dict["use_correction"] = self.hac_cluster_use_correction()
        elif cov_type == "cluster":
            kwds_dict["groups"] = self.cluster_groups(num_groups)
            kwds_dict["use_correction"] = self.hac_cluster_use_correction()
            kwds_dict["df_correction"] = self.cluster_df_correction()

        return None if len(kwds_dict) == 0 else kwds_dict

    def iterative_max_iter(self):
        return self.check_numeric_range("iterative_maxiter")

    def r_tol(self):
        return self.check_numeric_range("r_tol")