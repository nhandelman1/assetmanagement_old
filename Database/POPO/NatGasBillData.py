from typing import Optional
from decimal import Decimal
from Database.POPO.ComplexServiceBillDataBase import ComplexServiceBillDataBase


class NatGasBillData(ComplexServiceBillDataBase):
    """ Actual or estimated data provided on monthly natural gas bill or relevant to monthly bill

    Attributes:
        see super class docstring
        see init docstring for attributes (db_dict is not kept as an attribute)
    """
    def __init__(self, real_estate, service_provider, start_date, end_date, total_therms, saved_therms, total_cost,
                 tax_rel_cost, bsc_therms, bsc_cost, next_therms, next_rate, next_cost, ds_total_cost, gs_rate, gs_cost,
                 ss_total_cost, oca_total_cost, is_actual, over_therms=None, over_rate=None, over_cost=None,
                 dra_rate=None, dra_cost=None, sbc_rate=None, sbc_cost=None, tac_rate=None, tac_cost=None, bc_cost=None,
                 ds_nysls_rate=None, ds_nysls_cost=None, ds_nysst_rate=None, ds_nysst_cost=None, ss_nysls_rate=None,
                 ss_nysls_cost=None, ss_nysst_rate=None, ss_nysst_cost=None, pbc_cost=None, paid_date=None, notes=None,
                 db_dict=None):
        """ init function

        Args:
            see super class init docstring
            total_therms (int): nonnegative total therms used from provider
            saved_therms (int): nonnegative therms saved by using non nat gas sources (probably electric)
            bsc_therms (Decimal): therms used at basic service charge cost
            bsc_cost (Decimal): basic service charge cost
            next_therms (Decimal): therms used at next rate
                In the bill, either by "Next Therms" or "Over/Last Therms" (if "Next Therms" is not in the bill)
            next_rate (Decimal): next rate
                In the bill, either by "Next Therms" or "Over/Last Therms" (if "Next Therms" is not in the bill)
            next_cost (Decimal): next cost
                In the bill, either by "Next Therms" or "Over/Last Therms" (if "Next Therms" is not in the bill)
            ds_total_cost (Decimal): delivery service total cost
            gs_rate (Decimal): gas supply rate
            gs_cost (Decimal): gas supply cost
            ss_total_cost (Decimal): supply service total cost
            oca_total_cost (Decimal): other charges/adjustments total cost
            over_therms (Optional[Decimal]): therms used at over/last rate.
                If "Next Therms" is in the bill, by "Over/Last Therms", otherwise not used. Default None
            over_rate (Optional[Decimal]): over/last rate.
                If "Next Therms" is in the bill, by "Over/Last Therms", otherwise not used. Default None
            over_cost (Optional[Decimal]): over/last cost.
                If "Next Therms" is in the bill, by "Over/Last Therms", otherwise not used. Default None
            dra_rate (Optional[Decimal]): delivery rate adjustment rate. Default None
            dra_cost (Optional[Decimal]): delivery rate adjustment cost. Default None
            sbc_rate (Optional[Decimal]): system benefits charge rate. Default None
            sbc_cost (Optional[Decimal]): system benefits charge cost. Default None
            tac_rate (Optional[Decimal]): transportation adjustment charge rate. Default None
            tac_cost (Optional[Decimal]): transportation adjustment charge cost. Default None
            bc_cost (Optional[Decimal]): billing charge cost. Default None
            ds_nysls_rate (Optional[Decimal]): delivery services ny state and local surcharges rate. Default None
            ds_nysls_cost (Optional[Decimal]): delivery services ny state and local surcharges cost. Default None
            ds_nysst_rate (Optional[Decimal]): delivery services ny state sales tax rate. Default None
            ds_nysst_cost (Optional[Decimal]): delivery services ny state sales tax cost. Default None
            ss_nysls_rate (Optional[Decimal]): supply services ny state and local surcharges rate. Default None
            ss_nysls_cost (Optional[Decimal]): supply services ny state and local surcharges cost. Default None
            ss_nysst_rate (Optional[Decimal]): supply services ny state sales tax rate. Default None
            ss_nysst_cost (Optional[Decimal]): supply services ny state sales tax cost. Default None
            pbc_cost (Optional[Decimal]): paperless billing credit cost. Default None
            db_dict (Optional[dict]): dictionary holding arguments. if an argument is in the dictionary, it will
                overwrite an argument provided explicitly through the argument variable
        """
        super().__init__(real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, is_actual,
                         paid_date=paid_date, notes=notes)

        self.total_therms = total_therms
        self.saved_therms = saved_therms
        self.bsc_therms = bsc_therms
        self.bsc_cost = bsc_cost
        self.next_therms = next_therms
        self.next_rate = next_rate
        self.next_cost = next_cost
        self.over_therms = over_therms
        self.over_rate = over_rate
        self.over_cost = over_cost
        self.dra_rate = dra_rate
        self.dra_cost = dra_cost
        self.sbc_rate = sbc_rate
        self.sbc_cost = sbc_cost
        self.tac_rate = tac_rate
        self.tac_cost = tac_cost
        self.bc_cost = bc_cost
        self.ds_nysls_rate = ds_nysls_rate
        self.ds_nysls_cost = ds_nysls_cost
        self.ds_nysst_rate = ds_nysst_rate
        self.ds_nysst_cost = ds_nysst_cost
        self.ds_total_cost = ds_total_cost
        self.gs_rate = gs_rate
        self.gs_cost = gs_cost
        self.ss_nysls_rate = ss_nysls_rate
        self.ss_nysls_cost = ss_nysls_cost
        self.ss_nysst_rate = ss_nysst_rate
        self.ss_nysst_cost = ss_nysst_cost
        self.ss_total_cost = ss_total_cost
        self.pbc_cost = pbc_cost
        self.oca_total_cost = oca_total_cost

        self.db_dict_update(db_dict)

    def __str__(self):
        """ __str__ override

        Format:
            super().__str__()
            Total Therms: self.total_therms, Saved Therms: self.saved_therms, Bank KWH: self.bank_kwh
            Delivery Services: Total Cost: self.ds_total_cost
              Basic: Therms: self.bsc_therms, Cost: self.bsc_cost
              Next: Therms: self.next_therms, Rate: self.next_rate/therm, Cost: self.next_cost
              Over: Therms: self.over_therms, Rate: self.over_rate/therm, Cost: self.over_cost
              Delivery Rate Adjustment: Rate: self.dra_rate/therm, Cost: self.dra_cost
              System Benefits Charge: Rate: self.sbc_rate/therm, Cost: self.sbc_cost
              Transportation Adjustment Charge: Rate: self.tac_rate/therm, Cost: self.tac_cost
              Billing Charge: Cost: self.bc_cost
              NY State and Local Surcharges: Rate: self.ds_nysls_rate, Cost: self.ds_nysls_cost
              NY State Sales Tax: Rate: self.ds_nysst_rate, Cost: self.ds_nysst_cost
            Supply Services: Total Cost: self.ss_total_cost
              Gas Supply: Rate: self.gs_rate/therm, Cost: self.gs_cost
              NY State and Local Surcharges: Rate: self.ss_nysls_rate, Cost: self.ss_nysls_cost
              NY State Sales Tax: Rate: self.ss_nysst_rate, Cost: self.ss_nysst_cost
            Other Charges/Adjustments: Total Cost: self.oca_total_cost
                Paperless Billing Credit: Cost: self.pbc_cost

        Returns:
            str: as described by Format
        """
        return super().__str__() + \
            "\nTotal Therms: " + str(self.total_therms) + ", Saved Therms: " + str(self.saved_therms) + \
            "\nDelivery Services: Total Cost: " + str(self.ds_total_cost) + \
            "\n  Basic: Therms: " + str(self.bsc_therms) + ", Cost: " + str(self.bsc_cost) + \
            "\n  Next: Therms: " + str(self.next_therms) + ", Rate: " + str(self.next_rate) + "/therm, Cost: " + \
                str(self.next_cost) + \
            "\n  Over: Therms: " + str(self.over_therms) + ", Rate: " + str(self.over_rate) + "/therm, Cost: " + \
                str(self.over_cost) + \
            "\n  Delivery Rate Adjustment: Rate: " + str(self.dra_rate) + "/therm, Cost: " + str(self.dra_cost) + \
            "\n  System Benefits Charge: Rate: " + str(self.sbc_rate) + "/kwh, Cost: " + str(self.sbc_cost) + \
            "\n  Transportation Adjustment Charge: Rate: " + str(self.tac_rate) + "/therm, Cost: "+str(self.tac_cost)+\
            "\n  Billing Charge: Cost: " + str(self.bc_cost) + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ds_nysls_rate) + ", Cost: "+str(self.ds_nysls_cost)+\
            "\n  NY State Sales Tax: Rate: " + str(self.ds_nysst_rate) + ", Cost: " + str(self.ds_nysst_cost) + \
            "\nSupply Services: Total Cost: " + str(self.ss_total_cost) + \
            "\n  Gas Supply: Rate: " + str(self.gs_rate) + "/therm, Cost: " + str(self.gs_cost) + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ss_nysls_rate) + ", Cost: "+str(self.ss_nysls_cost)+\
            "\n  NY State Sales Tax: Rate: " + str(self.ss_nysst_rate) + ", Cost: " + str(self.ss_nysst_cost) + \
            "\nOther Charges/Adjustments: Total Cost: " + str(self.oca_total_cost) + \
            "\n  Paperless Billing Credit: Cost: " + str(self.pbc_cost)

    def copy(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Ratio applied to therms and cost attributes.
        """
        bill_copy = super().copy(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

        if cost_ratio is not None:
            def dec_mult_none(left):
                return None if left is None else left * cost_ratio

            def int_mult_none(left):
                return None if left is None else int(left * cost_ratio)

            bill_copy.total_therms = int_mult_none(bill_copy.total_therms)
            bill_copy.saved_therms = int_mult_none(bill_copy.saved_therms)
            bill_copy.bsc_therms *= cost_ratio
            bill_copy.bsc_cost *= cost_ratio
            bill_copy.next_therms *= cost_ratio
            bill_copy.next_cost *= cost_ratio
            bill_copy.over_therms = dec_mult_none(bill_copy.over_therms)
            bill_copy.over_cost = dec_mult_none(bill_copy.over_cost)
            bill_copy.dra_cost = dec_mult_none(bill_copy.dra_cost)
            bill_copy.sbc_cost = dec_mult_none(bill_copy.sbc_cost)
            bill_copy.tac_cost = dec_mult_none(bill_copy.tac_cost)
            bill_copy.bc_cost = dec_mult_none(bill_copy.bc_cost)
            bill_copy.ds_nysls_cost = dec_mult_none(bill_copy.ds_nysls_cost)
            bill_copy.ds_nysst_cost = dec_mult_none(bill_copy.ds_nysst_cost)
            bill_copy.ds_total_cost *= cost_ratio
            bill_copy.gs_cost *= cost_ratio
            bill_copy.ss_nysls_cost = dec_mult_none(bill_copy.ss_nysls_cost)
            bill_copy.ss_nysst_cost = dec_mult_none(bill_copy.ss_nysst_cost)
            bill_copy.ss_total_cost *= cost_ratio
            bill_copy.pbc_cost = dec_mult_none(bill_copy.pbc_cost)
            bill_copy.oca_total_cost *= cost_ratio

            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to therms and cost attributes."

        return bill_copy