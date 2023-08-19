import datetime
from decimal import Decimal
from typing import Optional

from .utilitydatabase import UtilityDataBase


class ElectricData(UtilityDataBase):
    """ Monthly data not necessarily provided on monthly electric bill and can be found elsewhere

    Attributes:
        see super class docstring
        see init docstring for attributes
    """
    def __init__(self, real_estate, service_provider, month_date, month_year, first_kwh, first_rate, next_rate,
                 mfc_rate=None, psc_rate=None, der_rate=None, dsa_rate=None, rda_rate=None, nysa_rate=None,
                 rbp_rate=None, spta_rate=None):
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
        """
        super().__init__(real_estate, service_provider, month_date, month_year)

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

    def __str__(self):
        """ __str__ override

        Format:
            super().__str__()
            Delivery & System Charges:
              First: KWH: self.first_kwh, Rate: self.first_rate/kwh
              Next: Rate: self.next_rate/kwh
              Merchant Function Charge: Rate: self.mfc_rate/kwh
            Power Supply Charges:
              Power Supply: Rate: self.psc_rate/kwh
            Taxes & Other Charges: Total Cost: self.toc_total_cost
              Distributed Energy Resources: Rate: self.der_cost/kwh
              Delivery Service Adjustment: Rate: self.dsa_rate
              Revenue Decoupling Adjustment: Rate: self.rda_rate
              New York State Assessment: Rate: self.nysa_rate
              Revenue Based Pilots: Rate: self.rbp_rate
              Suffolk Property Tax Adjustment: Rate: self.spta_rate

        Returns:
            str: as described by Format
        """
        return super().__str__() + \
            "\nDelivery & System Charges:" + \
            "\n  First: KWH: " + str(self.first_kwh) + ", Rate: " + str(self.first_rate) + "/kwh" + \
            "\n  Next: Rate: " + str(self.next_rate) + "/kwh" + \
            "\n  Merchant Function Charge: Rate: " + str(self.mfc_rate) + "/kwh" + \
            "\nPower Supply Charges: " + \
            "\n  Power Supply: Rate: " + str(self.psc_rate) + "/kwh" + \
            "\nTaxes & Other Charges:" + \
            "\n  Distributed Energy Resources: Rate: " + str(self.der_rate) + "/kwh" + \
            "\n  Delivery Service Adjustment: Rate: " + str(self.dsa_rate) + \
            "\n  Revenue Decoupling Adjustment: Rate: " + str(self.rda_rate) + \
            "\n  New York State Assessment: Rate: " + str(self.nysa_rate) + \
            "\n  Revenue Based Pilots: Rate: " + str(self.rbp_rate) + \
            "\n  Suffolk Property Tax Adjustment: Rate: " + str(self.spta_rate)

    @classmethod
    def default_constructor(cls):
        return ElectricData(None, None, None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        # month_date str format must be YYYY-MM-DD
        # "real_estate" key must have value RealEstate instance
        # "service_provider" key must have value ServiceProvider instance
        obj = super().str_dict_constructor(str_dict)

        if isinstance(obj.month_date, str):
            obj.month_date = datetime.datetime.strptime(obj.month_date, "%Y-%m-%d").date()
        obj.first_kwh = int(obj.first_kwh)
        obj.first_rate = Decimal(obj.first_rate)
        obj.next_rate = Decimal(obj.next_rate)
        obj.mfc_rate = cls.dec_none(obj.mfc_rate)
        obj.psc_rate = cls.dec_none(obj.psc_rate)
        obj.der_rate = cls.dec_none(obj.der_rate)
        obj.dsa_rate = cls.dec_none(obj.dsa_rate)
        obj.rda_rate = cls.dec_none(obj.rda_rate)
        obj.nysa_rate = cls.dec_none(obj.nysa_rate)
        obj.rbp_rate = cls.dec_none(obj.rbp_rate)
        obj.spta_rate = cls.dec_none(obj.spta_rate)

        return obj

    def str_dict_update(self, str_dict):
        """ Update instance variables using string (or otherwise specified below) values in str_dict

        "real_estate" key must have value RealEstate instance
        "service_provider" key must have value ServiceProvider instance

        Args:
            see superclass docstring
        """
        if isinstance(str_dict, dict):
            def dec_none(val):
                return None if val is None else Decimal(val)

            self.__dict__.update(pair for pair in str_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.month_date, str):
                self.month_date = datetime.datetime.strptime(self.month_date, "%Y-%m-%d").date()
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