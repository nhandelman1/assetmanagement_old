from enum import Enum
from typing import Optional

import pandas as pd

from .classconstructors import ClassConstructors
from .dataframeable import DataFrameable


class Address(Enum):
    WAGON_LN_10 = "10 Wagon Ln Centereach NY 11720"
    WAGON_LN_10_APT_1 = "10 Wagon Ln Apt 1 Centereach NY 11720"

    @staticmethod
    def to_address(str_addr):
        """ Try to match str_val to an Address using street number, street name, apt, city, state and zip code

        Args:
            str_addr (str): string address

        Returns:
            Address: that matches str_addr

        Raises:
            ValueError: if no Address matches str_addr
        """
        str_addr = str_addr.lower()
        if all([x in str_addr for x in ["10", "wagon", "centereach", "ny", "11720"]] +
               [any([x in str_addr for x in ["ln", "la"]])]):
            return Address.WAGON_LN_10_APT_1 if "apt 1" in str_addr else Address.WAGON_LN_10
        raise ValueError("No Address matches string address: " + str_addr)

    def short_name(self):
        """ Short name for each address

        Done here to maintain some control over uniqueness of naming

        Returns:
            str: short name for self Address
        Raises
        """
        if self == Address.WAGON_LN_10:
            return "WL10"
        elif self == Address.WAGON_LN_10_APT_1:
            return "WL10A1"
        else:
            raise ValueError("No short name set for Address: " + str(self))


class RealEstate(DataFrameable, ClassConstructors):
    """ Real estate data

    Attributes:
        see init docstring

    """
    def __init__(self, address, street_num, street_name, city, state, zip_code, bill_tax_related, apt=None):
        """ init function

        Args:
            address (Address): real estate address
            street_num (str): street number or id
            street_name (str): street name
            city (str): city
            state (str): 2 letter state code
            zip_code (str): 5 letter zip code
            bill_tax_related (boolean): True if bills associated with this real estate typically (but not necessarily)
                affect taxes in some way. False if they typically (but not necessarily) do not.
            apt (Optional[str]): apt name or number
        """
        self.id = None
        self.address = address
        self.street_num = street_num
        self.street_name = street_name
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.apt = apt
        self.bill_tax_related = bill_tax_related

    def __str__(self):
        """ __str__ override

        Returns:
            str: self.address.value
        """
        return str(self.address.value) + ", Bill Tax Related: " + str(self.bill_tax_related)

    @classmethod
    def default_constructor(cls):
        return RealEstate(None, None, None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        raise NotImplementedError("RealEstate does not implement str_dict_constructor()")

    def db_dict_update(self, db_dict):
        super().db_dict_update(db_dict)
        if isinstance(self.address, str):
            self.address = Address(self.address)
        self.bill_tax_related = bool(self.bill_tax_related)

    def to_pd_df(self, deprivatize=True, **kwargs):
        """ see superclass docstring

        No changes made to any instance attributes
        """
        return pd.DataFrame(self.__dict__, index=[0])