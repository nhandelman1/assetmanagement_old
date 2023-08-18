from statistics.LeastSquaresReg.OLSModelParams import OLSModelParams


class WLSModelParams(OLSModelParams):

    _WLS_AVAILABLE_MODEL_PARAMS_DICT = {**OLSModelParams._OLS_AVAILABLE_MODEL_PARAMS_DICT,
                                        **{"weights": ["", ("array", float)]}}

    def __init__(self):
        super().__init__(self._WLS_AVAILABLE_MODEL_PARAMS_DICT)

    def weights(self, num_obs):
        weights = self.array_to_np_array(self.param_dict.get("weights", "1.0"),
                                         self.available_param_dict["weights"][1][1])
        if weights.size == 1:
            return weights[0]

        if weights.size != num_obs:
            raise ValueError("weights array must have " + str(num_obs) + " values")

        return weights
