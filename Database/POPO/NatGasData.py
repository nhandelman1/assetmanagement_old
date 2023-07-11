import datetime
from typing import Optional
from decimal import Decimal
from Database.POPO.UtilityDataBase import UtilityDataBase


class NatGasData(UtilityDataBase):
    """ Monthly data not necessarily provided on monthly natural gas bill and can be found elsewhere

    Attributes:
        see super class docstring
        see init docstring for attributes (db_dict is not kept as an attribute)
    """
    def __init__(self, real_estate, service_provider, month_date, month_year, bsc_therms, bsc_rate, next_therms,
                 next_rate, over_rate, gs_rate, dra_rate=None, wna_low_rate=None, wna_high_rate=None, sbc_rate=None,
                 tac_rate=None, bc_rate=None, ds_nysls_rate=None, ds_nysst_rate=None, ss_nysls_rate=None,
                 ss_nysst_rate=None, pbc_rate=None, db_dict=None, str_dict=None):
        """ init function

        Args:
            see super class init docstring
            bsc_therms (Decimal): max therms used at basic rate
            bsc_rate (Decimal): basic service charge rate
            next_therms (Decimal): max therms used at next rate
            next_rate (Decimal): next rate.
            over_rate (Decimal): over/last rate.
            gs_rate (Decimal): gas supply rate
            dra_rate (Optional[Decimal]): delivery rate adjustment rate. Default None
            wna_low_rate (Optional[Decimal]): weather normalization adjustment rate for lower therms. Default None
            wna_high_rate (Optional[Decimal]): weather normalization adjustment rate for higher therms. Default None
            sbc_rate (Optional[Decimal]): system benefits charge. Default None
            tac_rate (Optional[Decimal]): transportation adjustment charge rate. Default None
            bc_rate (Optional[Decimal]): billing charge rate
            ds_nysls_rate (Optional[Decimal]): delivery services ny state and local surcharges rate. Default None.
            ds_nysst_rate (Optional[Decimal]): delivery services ny state sales tax. Default None
            ss_nysls_rate (Optional[Decimal]): supply services ny state and local surcharges rate. Default None.
            ss_nysst_rate (Optional[Decimal]): supply services ny state sales tax. Default None
            pbc_rate (Optional[Decimal]): paperless billing credit rate. Default None
            db_dict (Optional[dict]): dictionary holding arguments. if an argument is in the dictionary, it will
                overwrite an argument provided explicitly through the argument variable
            str_dict (Optional[dict]): dictionary holding arguments as strings or type specified in this docstring.
                if an argument is in the dictionary, it will overwrite an argument provided explicitly through the
                argument variable or through db_dict. month_date str format must be YYYY-MM-DD
        """
        super().__init__(real_estate, service_provider, month_date, month_year)

        self.bsc_therms = bsc_therms
        self.bsc_rate = bsc_rate
        self.next_therms = next_therms
        self.next_rate = next_rate
        self.over_rate = over_rate
        self.gs_rate = gs_rate
        self.dra_rate = dra_rate
        self.wna_low_rate = wna_low_rate
        self.wna_high_rate = wna_high_rate
        self.sbc_rate = sbc_rate
        self.tac_rate = tac_rate
        self.bc_rate = bc_rate
        self.ds_nysls_rate = ds_nysls_rate
        self.ds_nysst_rate = ds_nysst_rate
        self.ss_nysls_rate = ss_nysls_rate
        self.ss_nysst_rate = ss_nysst_rate
        self.pbc_rate = pbc_rate

        self.db_dict_update(db_dict)
        self.str_dict_update(str_dict)

    def __str__(self):
        """ __str__ override

        Format:
            super().__str__()
            Delivery Services:
              Basic: Therms: self.bsc_therms, Rate: self.bsc_rate
              Next: Therms: self.next_therms, Rate: self.next_rate/therm
              Over: Rate: self.over_rate/therm
              Delivery Rate Adjustment: Rate: self.dra_rate/therm
              Weather Normalization Adjustment: Low Rate: self.wna_low_rate/therm, High Rate: self.wna_high_rate/therm
              System Benefits Charge: Rate: self.sbc_rate/therm
              Transportation Adjustment Charge: Rate: self.tac_rate/therm
              Billing Charge: Rate: self.bc_rate/bill
              NY State and Local Surcharges: Rate: self.ds_nysls_rate
              NY State Sales Tax: Rate: self.ds_nysst_rate
            Supply Services:
              Gas Supply: Rate: self.gs_rate/therm
              NY State and Local Surcharges: Rate: self.ss_nysls_rate
              NY State Sales Tax: Rate: self.ss_nysst_rate
            Other Charges/Adjustments:
              Paperless Billing Credit: Cost: self.pbc_rate/bill

        Returns:
            str: as described by Format
        """
        return super().__str__() + \
            "\nDelivery Services:" + \
            "\n  Basic: Therms: " + str(self.bsc_therms) + ", Rate: " + str(self.bsc_rate) + \
            "\n  Next: Therms: " + str(self.next_therms) + ", Rate: " + str(self.next_rate) + "/therm" \
            "\n  Over: Rate: " + str(self.over_rate) + "/therm" + \
            "\n  Delivery Rate Adjustment: Rate: " + str(self.dra_rate) + "/therm" + \
            "\n  Weather Normalization Adjustment: Low Rate: " + str(self.wna_low_rate) + "/therm, High Rate: " + \
                str(self.wna_high_rate) + "/therm" + \
            "\n  System Benefits Charge: Rate: " + str(self.sbc_rate) + "/therm" + \
            "\n  Transportation Adjustment Charge: Rate: " + str(self.tac_rate) + "/therm" + \
            "\n  Billing Charge: Rate: " + str(self.bc_rate) + "/bill" + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ds_nysls_rate) + \
            "\n  NY State Sales Tax: Rate: " + str(self.ds_nysst_rate) + \
            "\nSupply Services: " + \
            "\n  Gas Supply: Rate: " + str(self.gs_rate) + "/therm" + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ss_nysls_rate) + \
            "\n  NY State Sales Tax: Rate: " + str(self.ss_nysst_rate) + \
            "\nOther Charges/Adjustments:" + \
            "\n  Paperless Billing Credit: Rate: " + str(self.pbc_rate) + "/bill"

    def str_dict_update(self, str_dict):
        """ Update instance variables using string (or otherwise specified below) values in str_dict

        "real_estate" key must have value RealEstate instance
        "provider" key must have value ServiceProvider instance

        Args:
            see superclass docstring
        """
        if isinstance(str_dict, dict):
            def dec_none(val):
                return None if val is None else Decimal(val)

            self.__dict__.update(pair for pair in str_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.month_date, str):
                self.month_date = datetime.datetime.strptime(self.month_date, "%Y-%m-%d").date()
            self.bsc_therms = Decimal(self.bsc_therms)
            self.bsc_rate = Decimal(self.bsc_rate)
            self.next_therms = Decimal(self.next_therms)
            self.next_rate = Decimal(self.next_rate)
            self.over_rate = Decimal(self.over_rate)
            self.gs_rate = Decimal(self.gs_rate)
            self.dra_rate = dec_none(self.dra_rate)
            self.wna_low_rate = dec_none(self.wna_low_rate)
            self.wna_high_rate = dec_none(self.wna_high_rate)
            self.sbc_rate = dec_none(self.sbc_rate)
            self.tac_rate = dec_none(self.tac_rate)
            self.bc_rate = dec_none(self.bc_rate)
            self.ds_nysls_rate = dec_none(self.ds_nysls_rate)
            self.ds_nysst_rate = dec_none(self.ds_nysst_rate)
            self.ss_nysls_rate = dec_none(self.ss_nysls_rate)
            self.ss_nysst_rate = dec_none(self.ss_nysst_rate)
            self.pbc_rate = dec_none(self.pbc_rate)
