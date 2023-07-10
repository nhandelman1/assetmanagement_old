import pandas as pd
from typing import Optional
from enum import Enum
from Database.POPO.DataFrameable import DataFrameable


class TaxCategory(Enum):
    DEP = "Depreciation"
    CM = "CleaningMaintenance"
    INC = "Income"
    INS = "Insurance"
    MI = "MortgageInterest"
    NONE = "None"
    REP = "Repairs"
    SUP = "Supplies"
    TAX = "Taxes"
    UTI = "Utilities"


class ServiceProviderEnum(Enum):
    """ Entries in service_provider table should be added here
    Appending tax category is not required and should not be assumed by any users of this class
    """
    BCPH_REP = "BigCityPlumbingHeating-REP"
    DEP_DEP = "Depreciation-DEP"
    HD_SUP = "HomeDepot-SUP"
    HOAT_REP = "HandymenOfAllTrades-REP"
    KPC_CM = "KnockoutPestControl-CM"
    MS_MI = "MorganStanley-MI"
    NB_INS = "NarragansettBay-INS"
    NG_UTI = "NationalGrid-UTI"
    NH = "NicholasHandelman"
    OH_INS = "OceanHarbor-INS"
    OC_UTI = "OptimumCable-UTI"
    OI_UTI = "OptimumInternet-UTI"
    PSEG_UTI = "PSEG-UTI"
    SCWA_UTI = "SCWA-UTI"
    SC_TAX = "SuffolkCounty-TAX"
    WMT_SUP = "Walmart-SUP"
    WL_10_APT_TEN_INC = "10WagonLnAptTenant-INC"
    WL_10_SP = "10WagonLnSunpower"
    WP_REP = "WolfPlumbing-REP"
    VI_UTI = "VerizonInternet-UTI"
    YTV_UTI = "YoutubeTV-UTI"


class ServiceProvider(DataFrameable):
    """ Service provider data

    Attributes:
        see init docstring (db_dict not kept as an attribute)
    """
    def __init__(self, provider, tax_category, db_dict=None):
        """ init function

        Args:
            provider (ServiceProviderEnum):
            tax_category (TaxCategory):
            db_dict (Optional[dict]): dictionary holding arguments. if an argument is in the dictionary, it will
                overwrite an argument provided explicitly through the argument variable
        """
        self.id = None
        self.provider = provider
        self.tax_category = tax_category

        if isinstance(db_dict, dict):
            self.__dict__.update(pair for pair in db_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.provider, str):
                self.provider = ServiceProviderEnum(self.provider)
            if isinstance(self.tax_category, str):
                self.tax_category = TaxCategory(self.tax_category)

    def to_pd_df(self, deprivative=True, **kwargs):
        """ see superclass docstring

        No changes made to any instance attributes
        """
        return pd.DataFrame(self.__dict__, index=[0])