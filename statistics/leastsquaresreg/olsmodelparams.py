from statistics.Params import Params


class OLSModelParams(Params):

    _OLS_AVAILABLE_MODEL_PARAMS_DICT = {
        "missing": ["", ["none", "drop", "raise"]],
        "hasconst": ["", ["None", "True", "False"]]
    }

    def __init__(self, available_model_params_dict=None):
        if available_model_params_dict is None:
            available_model_params_dict = self._OLS_AVAILABLE_MODEL_PARAMS_DICT

        super().__init__(available_model_params_dict)

    def missing(self):
        return self.check_list("missing")

    def hasconst(self):
        return self.check_bool_none_list("hasconst")