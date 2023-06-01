import datetime
from typing import Optional
from decimal import Decimal
from Database.POPO.UtilityDataBase import UtilityDataBase
from Database.POPO.ServiceProvider import ServiceProvider


class ElectricData(UtilityDataBase):
    """ Monthly data not necessarily provided on monthly electric bill and can be found elsewhere

    Attributes:
        see super class docstring
        see init docstring for attributes (db_dict is not kept as an attribute)
    """
    def __init__(self, real_estate, provider, month_date, month_year, first_kwh, first_rate, next_rate, mfc_rate=None,
                 psc_rate=None, der_rate=None, dsa_rate=None, rda_rate=None, nysa_rate=None, rbp_rate=None,
                 spta_rate=None, db_dict=None, str_dict=None):
        """ init function

        Args:
            see super class init docstring
            first_kwh (int): max kwh used at first rate. will not be in bill if none used
            first_rate (Decimal): first rate. will not be in bill if none used
            next_rate (Decimal): next rate. will not be in bill if none used
            mfc_rate (Optional[Decimal]): merchant function charge rate. Default None
            psc_rate (Optional[Decimal]): power supply charge rate. Default None
            der_rate (Optional[Decimal]): distributed energy resources charge rate. Default None
            dsa_rate (Optional[Decimal]): delivery service adjustment cost. Default None
            rda_rate (Optional[Decimal]): revenue decoupling adjustment rate. Default None
            nysa_rate (Optional[Decimal]): new york state assessment rate. Default None
            rbp_rate (Optional[Decimal]): revenue based pilots rate. Default None
            spta_rate (Optional[Decimal]): suffolk property tax adjustment rate. Default None
            db_dict (Optional[dict]): dictionary holding arguments loaded from database table. if an argument is in the
                dictionary, it will overwrite an argument provided explicitly through the argument variable
            str_dict (Optional[dict]): dictionary holding arguments as strings or type specified in this docstring.
                if an argument is in the dictionary, it will overwrite an argument provided explicitly through the
                argument variable or through db_dict. month_date str format must be YYYY-MM-DD
        """
        super().__init__(real_estate, provider, month_date, month_year)

        self.first_kwh = first_kwh
        self.first_rate = first_rate
        self.next_rate = next_rate
        self.mfc_rate = mfc_rate
        self.psc_rate = psc_rate
        self.der_rate = der_rate
        self.dsa_rate = dsa_rate
        self.rda_rate = rda_rate
        self.nysa_rate = nysa_rate
        self.rbp_rate = rbp_rate
        self.spta_rate = spta_rate

        self.db_dict_update(db_dict)
        self.str_dict_update(str_dict)

    def str_dict_update(self, str_dict):
        """ Update instance variables using string (or otherwise specified below) values in str_dict

        "real_estate" key must have value RealEstate instance
        "provider" key can have value string or ServiceProvider instance

        Args:
            see superclass docstring
        """
        if isinstance(str_dict, dict):
            def dec_none(val):
                return None if val is None else Decimal(val)

            self.__dict__.update(pair for pair in str_dict.items() if pair[0] in self.__dict__.keys())
            self.real_estate = self.real_estate
            self.provider = ServiceProvider(self.provider)
            if isinstance(self.month_date, str):
                self.month_date = datetime.datetime.strptime(self.month_date, "%Y-%m-%d").date()
            self.month_year = self.month_year
            self.first_kwh = int(self.first_kwh)
            self.first_rate = Decimal(self.first_rate)
            self.next_rate = Decimal(self.next_rate)
            self.mfc_rate = dec_none(self.mfc_rate)
            self.psc_rate = dec_none(self.psc_rate)
            self.der_rate = dec_none(self.der_rate)
            self.dsa_rate = dec_none(self.dsa_rate)
            self.rda_rate = dec_none(self.rda_rate)
            self.nysa_rate = dec_none(self.nysa_rate)
            self.rbp_rate = dec_none(self.rbp_rate)
            self.spta_rate = dec_none(self.spta_rate)