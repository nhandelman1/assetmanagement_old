from abc import ABC, abstractmethod
from Database.POPO.RealEstate import RealEstate
from Database.POPO.ServiceProvider import ServiceProvider


class UtilityDataBase(ABC):
    """ Base class for monthly data not necessarily provided on monthly utility bill and can be found elsewhere

    Attributes:
        id (int): database primary key id
        see init docstring for attributes (db_dict is not kept as an attribute)
    """

    @abstractmethod
    def __init__(self, real_estate, provider, month_date, month_year):
        """ init function

        Args:
            real_estate (RealEstate): real estate data
            provider (ServiceProvider): electricity provider
            month_date (datetime.date): date representation for the month of this data
            month_year (str): "MMYYYY" representation for the month of this data
        """
        self.id = None
        self.real_estate = real_estate
        self.provider = provider
        self.month_date = month_date
        self.month_year = month_year

    @abstractmethod
    def str_dict_update(self, str_dict):
        """ Update instance variables using string (or subclass specific) values in str_dict

        Subclasses must implement this since the data type for each instance variable is dependent on the subclass

        Args:
            str_dict (dict): dictionary with instance variables (string keys) and string (or subclass specific) values
        """
        raise NotImplementedError("str_dict_update() not implemented by subclass")

    def db_dict_update(self, db_dict):
        """ Update instance variables using db_dict

        provider value can be strings in db_dict

        Args:
            db_dict (dict): dictionary with instance variables (string keys) and values (datatype values)
        """
        # use db_dict to update instance variables
        if isinstance(db_dict, dict):
            self.__dict__.update(pair for pair in db_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.provider, str):
                self.provider = ServiceProvider(self.provider)

    def to_insert_dict(self):
        """ Convert class to dict

        "id" and "real_estate" fields are not included in returned dict
        "real_estate_id" key is added with value = self.real_estate.id

        Returns:
            dict: copy of self.__dict__ with changes described above
        """
        d = self.__dict__.copy()
        d.pop("id", None)
        d.pop("real_estate", None)
        d["real_estate_id"] = self.real_estate.id
        return d

