from statisticsam.params import Params


class QRModelParams(Params):

    _QR_AVAILABLE_MODEL_PARAMS_DICT = {}

    def __init__(self, available_model_params_dict=None):
        if available_model_params_dict is None:
            available_model_params_dict = self._QR_AVAILABLE_MODEL_PARAMS_DICT

        super().__init__(available_model_params_dict)