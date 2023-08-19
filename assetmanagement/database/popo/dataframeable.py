from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class DataFrameable(ABC):
    """ Classes that implement this class can create a 1-row pandas dataframe from the instance attributes
    Implementing classes can specify how attributes are handled
    """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def to_pd_df(self, deprivatize=True, **kwargs):
        """ Convert instance attributes to pandas dataframe

        Args:
            deprivatize (Optional[boolean]): True to have the leading underscore removed from "private" attributes.
                None or False to make no change. Default True
            **kwargs: keyword arguments specified by subclass (if any are used)

        Returns:
            pd.DataFrame: columns are instance attributes of self that may be modified as specified by subclass
        """
        raise NotImplementedError("to_pd_df() not implemented by subclass")

