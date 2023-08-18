import pandas as pd
import numpy as np


# LN, SQRT: transform applied to each element. No change in number of observations
# Returns: transform applied to elements 1,2; 2,3; 3,4; etc. Number of observations decreased by 1. Most recent date is
#   removed. Intended for price data.
# LN Returns: Returns transform applied then LN applied to each element of the result. Number of observations decreased
#   by 1. Oldest date is removed. Intended for price data.
# Risk Adj.: Subtract risk adjust asset. No change in number of observations. Intended for return data.
# Risk Adj. Returns: Returns transform applied then risk adjust asset returns subtracted from result. Risk adjust asset
#   assumed to be in returns so must have one less element than original data series. Number of observations decreased
#   by 1. Oldest date is removed. Intended for price data.
# Risk Adj. LN Returns: Risk Adj. Returns transform applied then LN applied to each element of result. Risk adjust asset
#   assumed to be in returns so must have one less element than original data series. Number of observations decreased
#   by 1. Oldest data is removed. Intended for price data.
#
# Transform precedence (from greatest to least):
#   1. Returns
#   2. Risk Adj.
#   3. LN, SQRT
#
# data must be in pandas time series structure
#
# check_apply_transform split into 2 functions since risk adjust transform requires another data series.
#   1. call check_apply_return_transform and use the returned series to get the correct risk adjust data series
#   2. call check_apply_remaining_transforms to apply risk adjust and math transforms
class Transform:

    TRANSFORM_LIST = ["", "LN", "SQRT", "Returns", "LN Returns", "Risk Adj.", "Risk Adj. Returns",
                      "Risk Adj. LN Returns"]
    RAA_TRANSFORM_LIST = ["", "LN", "SQRT", "Returns", "LN Returns"]
    COST_DICT_ = {"": 0, "LN": 0, "SQRT": 0, "Returns": -1, "LN Returns": -1, "Risk Adj.": 0, "Risk Adj. Returns": -1,
                  "Risk Adj. LN Returns": -1}

    RETURN_TRANSFORMS = ["Returns", "LN Returns", "Risk Adj. Returns", "Risk Adj. LN Returns"]
    RISK_ADJUST_TRANSFORMS = ["Risk Adj.", "Risk Adj. Returns", "Risk Adj. LN Returns"]
    LN_TRANSFORMS = ['LN', 'LN Returns', 'Risk Adj. LN Returns']
    SQRT_TRANSFORMS = ['SQRT']

    RISK_ADJUST_DIRECT_TRANSFORMS = ["Risk Adj."]
    RISK_ADJUST_RETURN_TRANSFORMS = ["Risk Adj. Returns", "Risk Adj. LN Returns"]

    def __init__(self, transform, is_for_raa):
        self.is_for_raa = is_for_raa

        if is_for_raa and transform not in Transform.RAA_TRANSFORM_LIST:
            self.transform = ""
        elif not is_for_raa and transform not in Transform.TRANSFORM_LIST:
            self.transform = ""
        else:
            self.transform = transform

    # the change in number of observations caused by the transform
    def transform_cost(self):
        return Transform.COST_DICT_.get(self.transform, 0)

    def is_risk_adj_transform(self):
        return self.transform in Transform.RISK_ADJUST_TRANSFORMS

    def prepend_id_data(self, s):
        return "Transform " + self.transform + ": " + s

    # if error_msg_list is empty, the data series returned is return transformed if required
    def check_apply_return_transform(self, data_series):
        if self.transform not in Transform.RETURN_TRANSFORMS or data_series is None or len(data_series) == 0:
            return data_series, [], []

        error_msg_list = []
        sugg_msg_list = []

        if data_series is None or data_series.size == 0:
            error_msg_list.append(self.prepend_id_data("no data provided"))
        elif data_series.size < 2:
            error_msg_list.append(self.prepend_id_data("not enough data provided"))

        if len(error_msg_list) == 0:
            if data_series.eq(0).any():
                error_msg_list.append(self.prepend_id_data("0 found before return calculation"))
            if data_series.lt(0).any():
                sugg_msg_list.append(self.prepend_id_data(
                                     "negative number found before return calculation. Is this intended?"))
            if data_series.isnull().any():
                sugg_msg_list.append(self.prepend_id_data("missing value(s) found before return calculation."))

            if len(error_msg_list) == 0:
                data_series = self.apply_return(data_series)

        return data_series, error_msg_list, sugg_msg_list

    # assumes risk adjust asset is in units of return
    # does not assume both series have the same index (will do a check)
    # if error_msg_list is empty, the data series returned is completely transformed
    def check_apply_remaining_transforms(self, data_series, raa_series=None):
        if data_series is None or len(data_series) == 0:
            return data_series, [], []

        error_msg_list = []
        sugg_msg_list = []

        if self.transform in Transform.RISK_ADJUST_TRANSFORMS:
            if raa_series is None:
                error_msg_list.append(self.prepend_id_data("risk adjust asset data not provided"))
            elif data_series.size != raa_series.size:
                error_msg_list.append(self.prepend_id_data("number of observations must be equal for both series."))
            elif not data_series.index.equals(raa_series.index):
                error_msg_list.append(self.prepend_id_data("series indexes must be equal."))

        if len(error_msg_list) == 0 and self.transform in Transform.RISK_ADJUST_TRANSFORMS:
            data_series = self.apply_risk_adjust(data_series, raa_series)

        if len(error_msg_list) == 0 and self.transform in Transform.LN_TRANSFORMS:
            if data_series.le(0).any():
                error_msg_list.append(self.prepend_id_data("non-positive number found before LN calculation "
                                                           "(after previous transforms, if any)"))
            else:
                data_series = np.log(data_series)

        if len(error_msg_list) == 0 and self.transform in Transform.SQRT_TRANSFORMS:
            if data_series.lt(0).any():
                error_msg_list.append(self.prepend_id_data("negative number found before SQRT calculation "
                                                           "(after previous transforms, if any)"))
            else:
                data_series = np.sqrt(data_series)

        if data_series.isnull().any():
            sugg_msg_list.append(self.prepend_id_data("missing value(s) found after transform completed."))

        return data_series, error_msg_list, sugg_msg_list

    # calculate returns including for missing data
    # by default this sets the first (and should be the oldest) date's value to nan
    # shift returns back so most recent date's value is nan
    # drop the most recent date
    def apply_return(self, data_series):
        data_series = data_series.pct_change(fill_method=None).shift(-1)
        return data_series.drop(data_series.tail(1).index)

    # assumes risk adjust asset is in units of return and both series have the same index
    # data_series and raa_series assumed to have same number of observations
    def apply_risk_adjust(self, data_series, raa_series):
        return data_series - raa_series

    # this function does no checking. arguments assumed to be valid and data assumed to have the correct domain
    def apply_transform(self, data_series, raa_series):
        if self.transform in Transform.RETURN_TRANSFORMS:
            data_series = self.apply_return(data_series)

        if self.transform in Transform.RISK_ADJUST_TRANSFORMS:
            data_series = self.apply_risk_adjust(data_series, raa_series)

        if self.transform in Transform.LN_TRANSFORMS:
            data_series = np.log(data_series)
        elif self.transform in Transform.SQRT_TRANSFORMS:
            data_series = np.sqrt(data_series)

        return data_series