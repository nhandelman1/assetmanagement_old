from enum import Enum
from typing import Optional
from decimal import Decimal
from Database.POPO.RealEstate import RealEstate


class DepClass(Enum):
    """ Depreciation Class

    https://www.irs.gov/publications/p946 -> Which Recovery Period Applies?
    """
    NONE = "None"
    GDS_RRP = "GDS-RRP"

    def get_recovery_period(self):
        """ Get recovery period for this depreciation class

        Returns:
            Decimal: recovery period in years
        """
        if self == DepClass.NONE:
            return Decimal(0)
        if self == DepClass.GDS_RRP:
            return Decimal(27.5)


class RealPropertyValues:
    """ Real property values data

    Initially used for home improvement related data but could be others. Might need to generalize this concept.

    Attributes:
        see init docstring (db_dict not kept as an attribute)
    """
    def __init__(self, real_estate, item, purchase_date, cost_basis, dep_class, notes=None, db_dict=None):
        """ init function

        Args:
            real_estate (RealEstate): real estate data
            item (str): real property item (e.g. House, Roof, etc.)
            purchase_date (datetime.date): date of item purchase
            cost_basis (Decimal): cost basis of item
            dep_class (DepClass): depreciation class
            notes (Optional[str]): any notes associated with this item. Default None for no notes
            db_dict (Optional[dict]): dictionary holding arguments. if an argument is in the dictionary, it will
                overwrite an argument provided explicitly through the argument variable. Default None
        """
        self.id = None
        self.real_estate = real_estate
        self.item = item
        self.purchase_date = purchase_date
        self.cost_basis = cost_basis
        self.dep_class = dep_class
        self.notes = notes

        if isinstance(db_dict, dict):
            self.__dict__.update(pair for pair in db_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.dep_class, str):
                self.dep_class = DepClass(self.dep_class)