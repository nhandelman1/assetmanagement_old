import numpy as np

# Format param_dict
#   key: suggested using associated statsmodel value but not required. it is possible to have keys are not associated
#       with a statsmodel param but may be associated with a statsmodel function (e.g. fit vs fit_regularized)
#   value: a list of two elements
#       first element is a string note about the item
#       second element are the possible value(s) that the statsmodel parameter can take
#       there are several possible values
#           list: a list of elements from which one must be picked. the first element in the list is the default
#           str type: for params that depend on the data or other params. read the string note for what is expected.
#               may also need to read the string note for other parameters. can also look at statsmodels documentation.
#               these will be checked before being passed to statsmodels
#           numeric range: a tuple with the following format:
#               (type, begin, bool_inclusive_begin, end, bool_inclusive_end, default, decimals). read string note for
#               acceptable numbers in the range. user expected to pick one number in the range. this will be checked
#               before being passed to statsmodels.
#               e.g. (float, 0, True, 1, True, 1, 2), (int, 0, False, 50, True, 0, 0).
#           array: a tuple with the following format: ("array", "type"), "type" is int, float or str
#           matrix: a tuple with the following format: ("matrix", "type"), "type" is int, float or str
#
# list, str type and numeric range values must be passed as a string. array and matrix values can be passed as a numpy
# array or string.
#   string formats can be the following:
#       a single value: e.g. "HCO" will be formatted to "HCO", "0.0" will be formatted to 0.0
#       a list of csv for array: e.g. "1.0, 0.0" will be formatted to [1.0, 0.0]
#       a list sccsv for matrix: e.g. "1.0, 2.0; 3.0, 4.0" will be formatted to [[1.0, 2.0], [3.0], [4.0]]
#
# not all parameters will necessarily be used. certain ones depend on the value of others. if a parameter is given a
# value but the parameter is not used, it will simply be ignored.
#
# Use pandas dataframe or numpy array for statsmodels data type 'array_like'. do not use python list

class Params:

    def __init__(self, available_param_dict):
        self.available_param_dict = available_param_dict
        self.param_dict = {}

    def set_value(self, key, value):
        self.param_dict[key] = value

    def value(self, key):
        return self.param_dict[key]

    # array is a either a string or np array
    # data_type_func is str, int or float
    # can raise ValueError
    @staticmethod
    def array_to_np_array(array, data_type_func):
        if isinstance(array, str):
            if data_type_func in [int, float]:
                array = array.replace(" ", "")

            array = array.split(",")

            new_array = []
            for s in array:
                new_array.append(data_type_func(s))

            return np.array(new_array)
        else:
            return array

    # array is a either a string or np 1d array or np 2d array
    # data_type_func is str, int or float
    # returns an np 2d array
    # can raise ValueError
    @staticmethod
    def matrix_to_np_array(matrix, data_type_func):
        if isinstance(matrix, str):
            matrix = matrix.split(";")
            try:
                matrix.remove("")
            except ValueError:
                pass

            new_matrix = []
            for s in matrix:
                new_matrix.append(Params.array_to_np_array(s, data_type_func))

            return np.array(new_matrix)
        else:
            if len(matrix.shape) == 1:
                return matrix.reshape(1, -1)

            return matrix

    # get the value from param_dict for keys with list values in available_param_dict
    # the first value in the list of values in available_param_dict is the default
    # raise ValueError if key is not in available_param_dict or value not in value list.
    # returns default if key is not in param_dict.
    def check_list(self, key):
        val_list = self.available_param_dict.get(key, None)
        if val_list is None:
            raise ValueError("key: " + str(key) + " not in available parameters dict")
        else:
            val_list = val_list[1]

        val = self.param_dict.get(key, val_list[0])
        if val in val_list:
            return val
        else:
            raise ValueError("Value: " + str(val) + " not in " + str(val_list))

    # can raise ValueError
    def check_bool_list(self, key):
        return self.check_list(key) == "True"

    # can raise ValueError
    def check_bool_none_list(self, key):
        val = self.check_list(key)
        return None if val == "None" else val == "True"

    # (float, 0, True, 1, True, 1)
    # can raise ValueError
    def check_numeric_range(self, key):
        range_tuple = self.available_param_dict.get(key, None)

        if range_tuple is None:
            raise KeyError("Key: " + str(key) + " not in available params dict")

        range_tuple = range_tuple[1]

        val = self.param_dict.get(key, None)
        # return default value
        if val is None:
            return range_tuple[5]

        if not isinstance(val, range_tuple[0]):
            raise ValueError("Key: " + str(key) + ", Value: " + str(val) + " must have " + str(range_tuple[0]) + " type")

        if val < range_tuple[1] or (not range_tuple[2] and val <= range_tuple[1]):
            raise ValueError(str(val) + " violates lower bound " + str(range_tuple[1]))
        if val > range_tuple[3] or (not range_tuple[4] and val >= range_tuple[3]):
            return ValueError(str(val) + " violates upper bound " + str(range_tuple[3]))

        return val