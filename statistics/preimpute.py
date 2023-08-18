



'''
Simple imputations that can be applied to a 1d array of data, either time series or not.
Options: forward fill, backward fill, mean, median, specific value
No matter the selection, no missing values will remain in the data after imputation.
    Forward Fill will back fill after forward fill
    Backward Fill will forward fill after backward fill
'''


class PreImpute:

    IMPUTATION_LIST = ["", "Mean", "Median", "Value", "Forward Fill", "Backward Fill"]

    def __init__(self, pre_impute, special_value):
        self.pre_impute = "" if pre_impute not in PreImpute.IMPUTATION_LIST else pre_impute
        self.special_value = special_value

        if pre_impute not in PreImpute.IMPUTATION_LIST:
            self.pre_impute = ""
        else:
            self.pre_impute = pre_impute

    # can raise ValueError and TypeError
    def apply_pre_impute(self, data_series):
        if data_series.size == 0:
            return data_series

        dtype = data_series.dtype

        if self.pre_impute == "":
            return data_series
        if self.pre_impute == "Forward Fill":
            data_series = data_series.fillna(method="ffill")
            return data_series.fillna(method="bfill")
        if self.pre_impute == "Backward Fill":
            data_series = data_series.fillna(method="bfill")
            return data_series.fillna(method="ffill")
        if self.pre_impute == "Mean":
            if dtype in ["float64", "int64"]:
                return data_series.fillna(data_series.mean())
            raise TypeError("Mean can't be applied to dtype: " + dtype)
        if self.pre_impute == "Median":
            if dtype in ["float64", "int64"]:
                return data_series.fillna(data_series.median())
            raise TypeError("Median can't be applied to dtype: " + dtype)
        if self.pre_impute == "Value":
            if data_series.dtype == "float64":
                return data_series.fillna(float(self.special_value))
            elif data_series.dtype == "int64":
                return data_series.fillna(int(self.special_value))
            else:
                return data_series.fillna(self.special_value)
