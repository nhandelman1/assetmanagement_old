from .olsmodelparams import OLSModelParams


class GLSModelParams(OLSModelParams):

    _GLS_AVAILABLE_MODEL_PARAMS_DICT = {**OLSModelParams._OLS_AVAILABLE_MODEL_PARAMS_DICT,
                                        **{"sigma": ["", ("matrix", float)]}}

    def __init__(self):
        super().__init__(self._GLS_AVAILABLE_MODEL_PARAMS_DICT)

    # returns a scalar, np 1d array of length num_obs or an np 2d array of shape num_obs x num_obs
    def sigma(self, num_obs):
        sigma = self.param_dict.get("sigma", None)
        if sigma is None:
            return None

        sigma = self.matrix_to_np_array(sigma, self.available_param_dict["sigma"][1][1])

        if sigma.size == 1:
            return sigma[0][0]

        if sigma.shape[0] == 1:
            if sigma.shape[1] == num_obs:
                return sigma[0]
            else:
                raise ValueError("sigma array must have " + str(num_obs) + " values")

        if sigma.shape != (num_obs, num_obs):
            raise ValueError("sigma matrix must have dim " + str((num_obs, num_obs)))

        return sigma
