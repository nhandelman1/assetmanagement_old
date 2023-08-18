from statisticsam.leastsquaresreg.olsmodelparams import OLSModelParams


class GLSARModelParams(OLSModelParams):

    _GLSAR_AVAILABLE_MODEL_PARAMS_DICT = {**OLSModelParams._OLS_AVAILABLE_MODEL_PARAMS_DICT,
                                          **{"rho": ["", (int, 1, True, 100, True, 1, 0)]}}

    def __init__(self):
        super().__init__(self._GLSAR_AVAILABLE_MODEL_PARAMS_DICT)

    def rho(self):
        return self.check_numeric_range("rho")