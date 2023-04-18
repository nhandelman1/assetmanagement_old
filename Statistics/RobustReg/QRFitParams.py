from Statistics.Params import Params


class QRFitParams(Params):

    _QR_AVAILABLE_FIT_PARAMS_DICT = {
        "fit": ["", ["Fit"]],
        "quantile": ["", (float, 0.000, False, 1.000, False, 0.500, 3)],
        "vcov": ["", ["robust", "iid"]],
        "kernel": ["", ["epa", "cos", "gau", "par"]],
        "bandwidth": ["", ["hsheather", "bofinger", "chamberlain"]],
        "max_iter": ["", (int, 1, True, 100000, True, 1000, 0)],
        "p_tol": ["", (float, 0.0000000000, False, 1.0000000000, True, 0.0000010000, 10)]
    }

    def __init__(self):
        super().__init__(self._QR_AVAILABLE_FIT_PARAMS_DICT)

    def fit(self):
        return self.check_list("fit")

    def quantile(self):
        return self.check_numeric_range("quantile")

    def vcov(self):
        return self.check_list("vcov")

    def kernel(self):
        return self.check_list("kernel")

    def bandwidth(self):
        return self.check_list("bandwidth")

    def max_iter(self):
        return self.check_numeric_range("max_iter")

    def p_tol(self):
        return self.check_numeric_range("p_tol")