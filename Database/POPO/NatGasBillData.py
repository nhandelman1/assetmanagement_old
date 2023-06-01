from typing import Optional
from decimal import Decimal
from Database.POPO.ComplexServiceBillDataBase import ComplexServiceBillDataBase


class NatGasBillData(ComplexServiceBillDataBase):
    """ Actual or estimated data provided on monthly natural gas bill or relevant to monthly bill

    Attributes:
        see super class docstring
        see init docstring for attributes (db_dict is not kept as an attribute)
    """
    def __init__(self, real_estate, provider, start_date, end_date, total_therms, saved_therms, total_cost, bsc_therms,
                 bsc_cost, next_therms, next_rate, next_cost, ds_total_cost, gs_rate, gs_cost, ss_total_cost,
                 oca_total_cost, is_actual, over_therms=None, over_rate=None, over_cost=None, dra_rate=None,
                 dra_cost=None, sbc_rate=None, sbc_cost=None, tac_rate=None, tac_cost=None, bc_cost=None,
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
        super().__init__(real_estate, provider, start_date, end_date, total_cost, is_actual, paid_date=paid_date,
                         notes=notes)

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
