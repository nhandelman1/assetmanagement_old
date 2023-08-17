import pandas as pd
from decimal import Decimal
from enum import Enum
from typing import Optional
from Database.POPO.DataFrameable import DataFrameable
from Database.POPO.ClassConstructors import ClassConstructors
from Database.POPO.RealEstate import RealEstate


class DepClass(Enum):
    """ Depreciation Class

    Enum value naming convention (**REQUIRED**, convention assumed by users of this class):
        system-propertyclass-method-convention
    """
    NONE = "None-None-None-None"
    GDS_RRP_SL_MM = "GDS-RRP-SL-MM"
    GDS_YEAR5_SL_MM = "GDS-YEAR5-SL-MM"


class RealPropertyValues(DataFrameable, ClassConstructors):
    """ Real property values data

    Initially used for home improvement related data but could be others. Might need to generalize this concept.

    Attributes:
        see init docstring
    """
    def __init__(self, real_estate, item, purchase_date, cost_basis, dep_class, disposal_date=None, notes=None):
        """ init function

        Args:
            real_estate (RealEstate): real estate data
            item (str): real property item (e.g. House, Roof, etc.)
            purchase_date (datetime.date): date of item purchase
            cost_basis (Decimal): cost basis of item
            dep_class (DepClass): depreciation class
            disposal_date (Optional[datetime.date]): date of disposal of item. Default None for not disposed
            notes (Optional[str]): any notes associated with this item. Default None for no notes
        """
        self.id = None
        self.real_estate = real_estate
        self.item = item
        self.purchase_date = purchase_date
        self.disposal_date = disposal_date
        self.cost_basis = cost_basis
        self.dep_class = dep_class
        self.notes = notes

    def __str__(self):
        return self.real_estate.address.value + "\n" + self.item + ", Depreciation Class: " + self.dep_class.value \
            + "\nPurchase Date: " + str(self.purchase_date) + ", Disposal Date: " + str(self.disposal_date) \
            + "\nCost Basis: " + str(self.cost_basis) + "\nNotes: " + str(self.notes)

    @classmethod
    def default_constructor(cls):
        return RealPropertyValues(None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        raise NotImplementedError("RealPropertyValues does not implement str_dict_constructor()")

    def db_dict_update(self, db_dict):
        super().db_dict_update(db_dict)
        if isinstance(self.dep_class, str):
            self.dep_class = DepClass(self.dep_class)

    def to_pd_df(self, deprivatize=True, **kwargs):
        """ see superclass docstring

        Returns:
            pd.DataFrame: with the following changes:
                self.real_estate.to_pd_df() with 'id' renamed to 'real_estate_id' and real_estate column dropped
        """
        re_df = self.real_estate.to_pd_df().rename(columns={"id": "real_estate_id"})
        other_df = pd.DataFrame(self.__dict__, index=[0]).drop(columns=["real_estate"])
        df = pd.concat([re_df, other_df], axis=1)
        return df