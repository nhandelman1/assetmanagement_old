import datetime
from decimal import Decimal
from typing import Optional
from Database.POPO.UtilityDataBase import UtilityDataBase


class NatGasData(UtilityDataBase):
    """ Monthly data not necessarily provided on monthly natural gas bill and can be found elsewhere

    Attributes:
        see super class docstring
        see init docstring for attributes
    """
    def __init__(self, real_estate, service_provider, month_date, month_year, bsc_therms, bsc_rate, next_therms,
                 next_rate, over_rate, gs_rate, dra_rate=None, wna_low_rate=None, wna_high_rate=None, sbc_rate=None,
                 tac_rate=None, bc_rate=None, ds_nysls_rate=None, ds_nysst_rate=None, ss_nysls_rate=None,
                 ss_nysst_rate=None, pbc_rate=None):
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

    @classmethod
    def default_constructor(cls):
        return NatGasData(None, None, None, None, None, None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        # month_date str format must be YYYY-MM-DD
        obj = super().str_dict_constructor(str_dict)

        if isinstance(obj.month_date, str):
            obj.month_date = datetime.datetime.strptime(obj.month_date, "%Y-%m-%d").date()
        obj.bsc_therms = Decimal(obj.bsc_therms)
        obj.bsc_rate = Decimal(obj.bsc_rate)
        obj.next_therms = Decimal(obj.next_therms)
        obj.next_rate = Decimal(obj.next_rate)
        obj.over_rate = Decimal(obj.over_rate)
        obj.gs_rate = Decimal(obj.gs_rate)
        obj.dra_rate = cls.dec_none(obj.dra_rate)
        obj.wna_low_rate = cls.dec_none(obj.wna_low_rate)
        obj.wna_high_rate = cls.dec_none(obj.wna_high_rate)
        obj.sbc_rate = cls.dec_none(obj.sbc_rate)
        obj.tac_rate = cls.dec_none(obj.tac_rate)
        obj.bc_rate = cls.dec_none(obj.bc_rate)
        obj.ds_nysls_rate = cls.dec_none(obj.ds_nysls_rate)
        obj.ds_nysst_rate = cls.dec_none(obj.ds_nysst_rate)
        obj.ss_nysls_rate = cls.dec_none(obj.ss_nysls_rate)
        obj.ss_nysst_rate = cls.dec_none(obj.ss_nysst_rate)
        obj.pbc_rate = cls.dec_none(obj.pbc_rate)

        return obj