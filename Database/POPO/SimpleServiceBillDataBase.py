import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional
from decimal import Decimal
from Database.MySQLBase import DictInsertable
from Database.POPO.RealEstate import RealEstate
from Database.POPO.ServiceProvider import ServiceProvider


class SimpleServiceBillDataBase(DictInsertable, ABC):
    """ Base class for simple data provided on service bill or relevant to service bill

    Simple data is for services actually provided and includes location (real estate), provider, start date, end date,
    total cost, paid date and notes. These are service attributes that are common to all forms of service. This class is
    intended to be subclassed by specific forms of service (e.g. electric service) that may or may not be more complex.
    Note that a "service" is loosely defined and may include actual services, goods purchased or any other item that
    can loosely be considered a "service".

    Attributes:
        id (int): database primary key id
        see init docstring for attributes
    """

    @abstractmethod
    def __init__(self, real_estate, service_provider, start_date, end_date, total_cost, paid_date=None, notes=None):
        """ init function

        Args:
            real_estate (RealEstate): real estate info
            service_provider (ServiceProvider): service provider
            start_date (datetime.date): bill start date
            end_date (datetime.date): bill end date
            total_cost (Decimal): total bill cost
            paid_date (Optional[datetime.date]): date on which bill was paid (for tax purposes). Optional since bill
                data might be saved before bill is paid
            notes (Optional[str]): notes about this bill
        """
        self.id = None
        self.real_estate = real_estate
        self.service_provider = service_provider
        self.start_date = start_date
        self.end_date = end_date
        self.total_cost = total_cost
        self.paid_date = paid_date
        self.notes = notes

    def db_dict_update(self, db_dict):
        """ Use db_dict to update instance variables

        Args:
            db_dict (Optional[dict]): dictionary with instance variables as keys. Default None to do no update
        """
        if isinstance(db_dict, dict):
            self.__dict__.update(pair for pair in db_dict.items() if pair[0] in self.__dict__.keys())

    def to_insert_dict(self):
        """ Convert class to dict

        "id" and "real_estate" fields are not included in returned dict
        "real_estate_id" key is added with value = self.real_estate.id
        "service_provider_id" key is added with value = self.service_provider.id

        Returns:
            dict: copy of self.__dict__ with changes described above
        """
        d = self.__dict__.copy()
        d.pop("id", None)
        d.pop("real_estate", None)
        d.pop("service_provider", None)
        d["real_estate_id"] = self.real_estate.id
        d["service_provider_id"] = self.service_provider.id
        return d

    def to_pd_df(self):
        """ Convert instance attributes to pandas dataframe

        Returns:
            pd.DataFrame: columns are attributes of this with self.real_estate and self.service_provider attributes
        """
        re_df = self.real_estate.to_pd_df().rename(columns={"id": "real_estate_id"})
        sp_df = self.service_provider.to_pd_df().rename(columns={"id": "service_provider_id"})
        df = pd.concat([re_df, sp_df,
                    pd.DataFrame(self.__dict__, index=[0]).drop(columns=["real_estate", "service_provider"])], axis=1)
        return df

    @staticmethod
    def calc_bill_month_year(start_date, end_date, threshold: int = 25):
        """ Calculate bill month depending on start_date and end_date

        Args:
            start_date (datetime.date): bill start date
            end_date (datetime.date): bill end date
            threshold (int): 1-31. if start_date day is before or equal to this value, get month year from
                start_date. otherwise, get month year from end_date. Default 25

        Returns:
            str: month year with format "YYYY-MM"
        """
        return start_date.strftime("%Y-%m") if start_date.day <= threshold else end_date.strftime("%Y-%m")

    def calc_this_bill_month_year(self, threshold: int = 25):
        """ Call self.calc_bill_month_year(self.start_date, self.end_date)

        Args:
            threshold (int): 1-31. Default 25

        Returns:
            str: month year with format "YYYY-MM"
        """
        return self.calc_bill_month_year(self.start_date, self.end_date, threshold=threshold)