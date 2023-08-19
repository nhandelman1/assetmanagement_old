import pandas as pd

from .preimpute import PreImpute
from .transform import Transform


class StatsData:

    VAR_TYPE_LIST = ["Dep", "Indep", "RAA", "Other"]

    '''
    Data can come from database or file and can be time series or non time series
    All types must have name, column, transform, var specified in init arguments
    database types must also have data_type, type_db_table_meta, db_data_table_midfix, subtype, subtype_db_table_meta,
        db_data_table_prefix, name_data_dict specified in init arguments
    File types must also have file_name specified in init arguments
    Time series types should set freq, begin_date, end_date in init arguments if possible 
    '''
    # transform: string name of transform. this class will create the transform object
    def __init__(self, name, column, transform, pre_impute_list, var, data_type=None, type_db_table_meta=None,
                 db_data_table_midfix=None, subtype=None, subtype_db_table_meta=None, db_data_table_prefix=None,
                 name_data_dict=None, file_name=None, freq=None, db_begin_date=None, db_end_date=None,
                 data_coll=None):
        if var not in self.VAR_TYPE_LIST:
            raise ValueError(str(var) + " not in " + str(self.VAR_TYPE_LIST))

        self.name = name
        self.column = column
        self.var = var
        self.transform = Transform(transform, var == "RAA")
        self.pre_impute = PreImpute(pre_impute_list[0], pre_impute_list[1])

        if file_name is None:
            self.type = data_type
            self.type_db_table_meta = type_db_table_meta
            self.db_data_table_midfix = db_data_table_midfix
            self.subtype = subtype
            self.subtype_db_table_meta = subtype_db_table_meta
            self.db_data_table_prefix = db_data_table_prefix
            self.name_data_dict = name_data_dict
        else:
            self.type = None
            self.type_db_table_meta = None
            self.db_data_table_midfix = None
            self.subtype = None
            self.subtype_db_table_meta = None
            self.db_data_table_prefix = None
            self.name_data_dict = None

        self.file_name = file_name

        self.freq = freq
        self.db_begin_date = db_begin_date
        self.db_end_date = db_end_date
        self.pre_imputed_begin_date = None
        self.pre_imputed_end_date = None
        self.transformed_begin_date = None
        self.transformed_end_date = None

        self.num_obs_original = -1
        self.num_obs_after_transform = -1
        self.num_missing_original = -1

        self.original_data_series = None
        self.pre_imputed_data_series = None
        if data_coll is not None:
            self.set_data_series(data_coll)

        self.transformed_data_series = None
        self.transformed_raa_series = None
        self.transformed_raa_series_freq = None

    # should be able to use any of the data series objects. no changes should change the time series status
    def data_series_is_time_series(self, data_series=None):
        if data_series is None:
            data_series = self.pre_imputed_data_series

        return False if data_series is None else isinstance(data_series.index, pd.DatetimeIndex)

    def is_raa(self):
        return self.transform.is_for_raa

    # data_coll can be a pandas series, list of dicts or list of lists
    # pandas series index can be pandas datetimeindex or default index. if it is datetimeindex: freq, begin_date
    #   end_date, variables should have been set in init (indicating a time series)
    # each dict must have column key. if it has a 'date_time' key, freq, begin_date and end_date variables should have
    #   been set in init (indicating a time series)
    # each list must either be 1 or 2 elements. the first element is the date_time, second element is data
    # list of dicts and lists of lists will be converted to a pandas series
    # python type in ["", "float", "int", "str"], blank is identity. for converting list data to a certain type
    # bad data in list is set in the series as None (NaN)
    # self.original_data_series will hold the unaltered data series at the end of this function
    # self.pre_imputed_data_series will hold the pre-imputed data series at the end of this function
    # transformed variables will be set to None at the end of this function
    # can throw ValueError, TypeError, IndexError
    def set_data_series(self, data_coll, python_type='', db_type=None):
        if isinstance(data_coll, pd.Series):
            self.original_data_series = data_coll
        elif len(data_coll) == 0:
            self.original_data_series = pd.Series([])
        else:
            if db_type is not None:
                if "decimal" in db_type or "float" in db_type or "double" in db_type:
                    python_type = "float"
                elif "int" in db_type:
                    python_type = "int"
                elif "char" in db_type:
                    python_type = "str"
                else:
                    python_type = db_type

            if python_type not in ['', 'float', 'int', 'str']:
                raise ValueError(str(python_type) + " not in " + str(['', 'float', 'int', 'str']))

            datetime_list = []
            data_list = []

            if python_type == "float":
                func = float
            elif python_type == "int":
                func = int
            elif python_type == "str":
                func = str
            else:
                func = lambda x: x

            def data_val(x):
                try:
                    return func(x)
                except (ValueError, TypeError):
                    return None

            if isinstance(data_coll[0], dict):
                has_datetime = 'date_time' in data_coll[0]

                for d in data_coll:
                    datetime_list.append(d.get('date_time', None))
                    data_list.append(data_val(d[self.column]))
            else:
                has_datetime = len(data_coll[0]) == 2

                if has_datetime:
                    datetime_list = [lst[0] for lst in data_coll]
                    data_list = [data_val(lst[1]) for lst in data_coll]
                else:
                    data_list = [data_val(lst[0]) for lst in data_coll]

            if has_datetime:
                self.original_data_series = pd.Series(data_list, index=pd.to_datetime(datetime_list))
            else:
                self.original_data_series = pd.Series(data_list)

        self.num_obs_original = self.original_data_series.size
        self.num_obs_after_transform = self.num_obs_original + self.transform.transform_cost()
        self.num_missing_original = self.original_data_series.isnull().sum().sum()
        self.pre_imputed_data_series = self.pre_impute.apply_pre_impute(self.original_data_series)

        self.set_pre_impute_dates()
        self.reset_transform_vars()

    def set_pre_impute_dates(self):
        if self.data_series_is_time_series() and len(self.pre_imputed_data_series) > 0:
            self.pre_imputed_begin_date = self.pre_imputed_data_series.index[0]
            self.pre_imputed_end_date = self.pre_imputed_data_series.index[-1]
        else:
            self.pre_imputed_begin_date = None
            self.pre_imputed_end_date = None

    def set_transformed_dates(self):
        if self.data_series_is_time_series(self.transformed_data_series) and len(self.transformed_data_series) > 0:
            self.transformed_begin_date = self.transformed_data_series.index[0]
            self.transformed_end_date = self.transformed_data_series.index[-1]
        else:
            self.transformed_begin_date = None
            self.transformed_end_date = None

    def prepend_id_data(self, msg_list):
        new_list = []
        for msg in msg_list:
            new_list.append(self.var + " : " + self.name + " : " + self.column + " : " + msg)
        return new_list

    def reset_transform_vars(self):
        self.transformed_data_series = None
        self.transformed_begin_date = None
        self.transformed_end_date = None
        self.transformed_raa_series = None
        self.transformed_raa_series_freq = None

    # also checks for missing values
    def check_apply_transform(self, raa_stats_data_list=(), force_match=False):
        self.reset_transform_vars()

        transformed_raa_series = None
        transformed_raa_series_freq = None
        error_msg_list = []
        sugg_msg_list = []

        transformed_data_series, err_list, sugg_list = \
            self.transform.check_apply_return_transform(self.pre_imputed_data_series)
        error_msg_list += err_list
        sugg_msg_list += sugg_list

        if len(error_msg_list) == 0 and self.transform.is_risk_adj_transform():
            transformed_raa_series, transformed_raa_series_freq, err_list, sugg_list = \
                self.match_data_series_raa_series_indexes(transformed_data_series, raa_stats_data_list, force_match)
            error_msg_list += err_list
            sugg_msg_list += sugg_list

        if len(error_msg_list) == 0:
            transformed_data_series, err_list, sugg_list = \
                self.transform.check_apply_remaining_transforms(transformed_data_series, transformed_raa_series)
            error_msg_list += err_list
            sugg_msg_list += sugg_list

        if len(error_msg_list) == 0:
            self.transformed_data_series = transformed_data_series
            self.transformed_raa_series = transformed_raa_series
            self.transformed_raa_series_freq = transformed_raa_series_freq
            self.set_transformed_dates()

        return self.prepend_id_data(error_msg_list), self.prepend_id_data(sugg_msg_list)

    # Force match False:
    #   raa_stats_data_list must have a stats_data with same frequency as data_series (which is this class instance)
    #   For all data series values that are missing, their indexes are not required to be in the raa series index
    #   For all data series values that are non-missing, their indexes must be in the raa series but can have a missing
    #       value
    # Force match True:
    #   raa_stats_data_list not required to have a stats_data with same frequency as data_series (which is this class
    #       instance)
    #   If there is a frequency match, try to use that data. Otherwise try to force a match with a different frequency.
    #   For different frequencies, it should be possible to force a match.
    #       5M data series and 1D raa series: ignore the hh:mm:ss part of the 5M data series
    #       1D data series and 5M raa series: find all matching YYYY-MM-DD in 5M raa series. use compound return since
    #           raa series is in units of return. Really should just have the 5M raa series data saved in the database
    #           or file as 1D data and not rely on this feature.

    # Return: transformed_raa_series, transformed_raa_series_freq, error_msg_list, sugg_msg_list
    #   If transformed_raa_series is None: error_msg_list will contain one error message
    #   If transformed_raa_series is not None: error_msg_list will be an empty list
    #   sugg_msg_list will provide info on the force match (if used) and any other suggestions that may come up
    # TODO implement force match
    def match_data_series_raa_series_indexes(self, data_series, raa_stats_data_list, force_match=False):
        force_match = False
        sugg_msg_list = []

        if force_match:
            return None, None, ["Force match not implemented"], []
        else:
            transformed_raa_series = None
            for stats_data in raa_stats_data_list:
                if self.freq == stats_data.freq:
                    transformed_raa_series = stats_data.transformed_data_series
                    break

            if transformed_raa_series is None:
                err = ["No RAA with matching frequency found. Include an RAA with matching frequency or use force "
                       "match."]
                return None, None, err, sugg_msg_list

            if all(data_series.dropna().index.isin(transformed_raa_series.index)):
                return transformed_raa_series.reindex(data_series.index), self.freq, [], sugg_msg_list
            else:
                err = ["Data series non-missing values have index value(s) that are not found in the RAA's index. "
                       "Include an RAA with required index values or use force match."]
                return None, None, err, sugg_msg_list

    def check_missing_values(self, for_transformed_data=True):
        data_series = self.transformed_data_series if for_transformed_data else self.pre_imputed_data_series
        data_name = "transformed" if for_transformed_data else "pre-imputed"

        if data_series.isnull().any():
            return "missing value(s) found for " + data_name + " data series"
        else:
            return ""