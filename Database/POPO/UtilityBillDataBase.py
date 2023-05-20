import pandas as pd
from abc import ABC, abstractmethod
from Database.POPO.RealEstate import RealEstate
from Database.POPO.UtilityProvider import UtilityProvider


class UtilityBillDataBase(ABC):
    """ Base class for actual or estimated data provided on monthly utility bill or relevant to monthly bill

    Attributes:
        id (int): database primary key id
        see init docstring for attributes (db_dict is not kept as an attribute)
    """

    @abstractmethod
    def __init__(self, real_estate, provider, start_date, end_date, is_actual):
        """ init function

        Args:
            real_estate (RealEstate): real estate info
            provider (UtilityProvider): electricity provider
            start_date (datetime.date): bill start date
            end_date (datetime.date): bill end date
            is_actual (boolean): is this data from an actual bill (True) or estimated (False)
        """
        super().__init__()

        self.id = None
        self.real_estate = real_estate
        self.provider = provider
        self.start_date = start_date
        self.end_date = end_date
        self.is_actual = is_actual

    def db_dict_update(self, db_dict):
        """ Use db_dict to update instance variables

        Args:
            db_dict (dict, optional): dictionary with instance variables as keys. Default None to do no update
        """
        if isinstance(db_dict, dict):
            self.__dict__.update(pair for pair in db_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.provider, str):
                self.provider = UtilityProvider(self.provider)

    def to_insert_dict(self):
        """ Convert class to dict

        "id" and "real_estate" fields are not included in returned dict
        "real_estate_id" key is added with value = self.real_estate.id

        Returns:
            copy of self.__dict__ with changes described above
        """
        d = self.__dict__.copy()
        d.pop("id", None)
        d.pop("real_estate", None)
        d["real_estate_id"] = self.real_estate.id
        return d

    def to_pd_df(self):
        """ Convert instance attributes to pandas dataframe

        Returns:
            pandas dataframe
        """
        df = self.real_estate.to_pd_df().rename(columns={"id": "real_estate_id"})
        df = pd.concat([df, pd.DataFrame(self.__dict__, index=[0]).drop(columns=["real_estate"])], axis=1)
        return df

    @staticmethod
    def calc_bill_month_year(start_date, end_date, threshold=25):
        """ Calculate bill month depending on start_date and end_date

        Args:
            start_date (datetime.date): bill start date
            end_date (datetime.date): bill end date
            threshold (int, optional): 1-31. if start_date day is before or equal to this value, get month year from
                start_date. otherwise, get month year from end_date. Default 25

        Returns:
            str month year with format "YYYY-MM"
        """
        return start_date.strftime("%Y-%m") if start_date.day <= threshold else end_date.strftime("%Y-%m")

    def calc_this_bill_month_year(self, threshold=25):
        """ Call self.calc_bill_month_year(self.start_date, self.end_date)

        Args:
            threshold (int, optional): 1-31. Default 25

        Returns:
            str month year with format "YYYY-MM"
        """
        return self.calc_bill_month_year(self.start_date, self.end_date, threshold=threshold)