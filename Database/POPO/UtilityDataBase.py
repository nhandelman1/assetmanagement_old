from abc import ABC, abstractmethod
from typing import Union
from Database.MySQLBase import DictInsertable
from Database.POPO.RealEstate import RealEstate
from Database.POPO.ServiceProvider import ServiceProvider


class UtilityDataBase(DictInsertable, ABC):
    """ Base class for monthly data not necessarily provided on monthly utility bill and can be found elsewhere

    Attributes:
        id (int): database primary key id
        see init docstring for attributes (db_dict is not kept as an attribute)
    """

    @abstractmethod
    def __init__(self, real_estate, service_provider, month_date, month_year):
        """ init function

        Args:
            real_estate (RealEstate): real estate data
            service_provider (ServiceProvider):
            month_date (datetime.date): date representation for the month of this data
            month_year (str): "MMYYYY" representation for the month of this data
        """
        self.id = None
        self.real_estate = real_estate
        self.service_provider = service_provider
        self.month_date = month_date
        self.month_year = month_year

    def __str__(self):
        """ __str__ override

        Format:
            str(self.real_estate)
            str(self.service_provider)
            str(self.month_year)

        Returns:
            str: as described by Format
        """
        return str(self.real_estate) + "\n" + str(self.service_provider) + "\n" + str(self.month_year)

    @abstractmethod
    def str_dict_update(self, str_dict):
        """ Update instance variables using string (or subclass specific) values in str_dict

        Subclasses must implement this since the data type for each instance variable is dependent on the subclass

        Args:
            str_dict (Union[dict, None]): dictionary with instance variables (string keys) and string
                (or subclass specific) values. None is allowed for convenience
        """
        raise NotImplementedError("str_dict_update() not implemented by subclass")

    def db_dict_update(self, db_dict):
        """ Update instance variables using db_dict

        Args:
            db_dict (Union[dict, None]): dictionary with instance variables (string keys) and values (datatype values).
                None is allowed for convenience
        """
        # use db_dict to update instance variables
        if isinstance(db_dict, dict):
            # use this method of setting attributes instead of __dict__.update to property set private attributes
            for key, value in db_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)

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

