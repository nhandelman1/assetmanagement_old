from decimal import Decimal
from typing import Optional
from database.popo.complexservicebilldatabase import ComplexServiceBillDataBase


class ElectricBillData(ComplexServiceBillDataBase):
    """ Actual or estimated data provided on monthly electric bill or relevant to monthly bill

    Attributes:
        see super class docstring
        see init docstring for attributes
    """

    def __init__(self, real_estate, service_provider, start_date, end_date, total_kwh, eh_kwh, bank_kwh, total_cost,
                 tax_rel_cost, bs_rate, bs_cost, dsc_total_cost, toc_total_cost, is_actual, first_kwh=None,
                 first_rate=None, first_cost=None,  next_kwh=None, next_rate=None, next_cost=None, cbc_rate=None,
                 cbc_cost=None, mfc_rate=None, mfc_cost=None, psc_rate=None, psc_cost=None, psc_total_cost=None,
                 der_rate=None, der_cost=None, dsa_rate=None, dsa_cost=None, rda_rate=None, rda_cost=None,
                 nysa_rate=None, nysa_cost=None, rbp_rate=None, rbp_cost=None, spta_rate=None, spta_cost=None,
                 st_rate=None, st_cost=None, paid_date=None, notes=None):
        """ init function

        Args:
            see super class init docstring
            total_kwh (int): nonnegative total kwh used from provider
            eh_kwh (int): electric heater kwh usage
            bank_kwh (int): nonnegative banked kwh
            bs_rate (Decimal): basic service charge rate
            bs_cost (Decimal): basic service charge cost
            dsc_total_cost (Decimal): delivery and service charge total cost
            toc_total_cost (Decimal): taxes and other charges total cost
            first_kwh (Optional[int]): kwh used at first rate. will not be in bill if none used. Default None
            first_rate (Optional[Decimal]): first rate. will not be in bill if none used. Default None
            first_cost (Optional[Decimal]): first cost. will not be in bill if none used. Default None
            next_kwh (Optional[int]): kwh used at next rate. will not be in bill if none used. Default None
            next_rate (Optional[Decimal]): next rate. will not be in bill if none used. Default None
            next_cost (Optional[Decimal]): next cost. will not be in bill if none used. Default None
            cbc_rate (Optional[Decimal]): customer benefit contribution charge rate. Default None
            cbc_cost (Optional[Decimal]): customer benefit contribution charge cost. Default None
            mfc_rate (Optional[Decimal]): merchant function charge rate. Default None
            mfc_cost (Optional[Decimal]): merchant function charge cost. Default None
            psc_rate (Optional[Decimal]): power supply charge rate. Default None
            psc_cost (Optional[Decimal]): power supply charge cost. Default None
            psc_total_cost (Optional[Decimal]): power supply charge total cost. Default None
            der_rate (Optional[Decimal]): distributed energy resources charge rate. Default None
            der_cost (Optional[Decimal]): distributed energy resources charge cost. Default None
            dsa_rate (Optional[Decimal]): delivery service adjustment rate. Default None
            dsa_cost (Optional[Decimal]): delivery service adjustment cost. Default None
            rda_rate (Optional[Decimal]): revenue decoupling adjustment rate. Default None
            rda_cost (Optional[Decimal]): revenue decoupling adjustment cost. Default None
            nysa_rate (Optional[Decimal]): new york state assessment rate. Default None
            nysa_cost (Optional[Decimal]): new york state assessment cost. Default None
            rbp_rate (Optional[Decimal]): revenue based pilots rate. Default None
            rbp_cost (Optional[Decimal]): revenue based pilots cost. Default None
            spta_rate (Optional[Decimal]): suffolk property tax adjustment rate. Default None
            spta_cost (Optional[Decimal]): suffolk property tax adjustment cost. Default None
            st_rate (Optional[Decimal]): sales tax rate. Default None
            st_cost (Optional[Decimal]): sales tax cost. Default None
        """
        super().__init__(real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, is_actual,
                         paid_date=paid_date, notes=notes)

        self.total_kwh = total_kwh
        self.eh_kwh = eh_kwh
        self.bank_kwh = bank_kwh
        self.bs_rate = bs_rate
        self.bs_cost = bs_cost
        self.first_kwh = first_kwh
        self.first_rate = first_rate
        self.first_cost = first_cost
        self.next_kwh = next_kwh
        self.next_rate = next_rate
        self.next_cost = next_cost
        self.cbc_rate = cbc_rate
        self.cbc_cost = cbc_cost
        self.mfc_rate = mfc_rate
        self.mfc_cost = mfc_cost
        self.dsc_total_cost = dsc_total_cost
        self.psc_rate = psc_rate
        self.psc_cost = psc_cost
        self.psc_total_cost = psc_total_cost
        self.der_rate = der_rate
        self.der_cost = der_cost
        self.dsa_rate = dsa_rate
        self.dsa_cost = dsa_cost
        self.rda_rate = rda_rate
        self.rda_cost = rda_cost
        self.nysa_rate = nysa_rate
        self.nysa_cost = nysa_cost
        self.rbp_rate = rbp_rate
        self.rbp_cost = rbp_cost
        self.spta_rate = spta_rate
        self.spta_cost = spta_cost
        self.st_rate = st_rate
        self.st_cost = st_cost
        self.toc_total_cost = toc_total_cost

    def __str__(self):
        """ __str__ override

        Format:
            super().__str__()
            Total KWH: self.total_kwh, Electric Heater KWH: self.eh_kwh, Bank KWH: self.bank_kwh
            Delivery & System Charges: Total Cost: self.dsc_total_cost
              Basic: Rate: self.bs_rate/day, Cost: self.bs_cost
              First: KWH: self.first_kwh, Rate: self.first_rate/kwh, Cost: self.first_cost
              Next: KWH: self.next_kwh, Rate: self.next_rate/kwh, Cost: self.next_cost
              Customer Benefit Contribution: Rate: self.cbc_rate/day, Cost: self.cbc_cost
              Merchant Function Charge: Rate: self.mfc_rate/kwh, Cost: self.mfc_cost
            Power Supply Charges: Total Cost: self.psc_total_cost
              Power Supply: Rate: self.psc_rate/kwh, Cost: self.psc_cost
            Taxes & Other Charges: Total Cost: self.toc_total_cost
              Distributed Energy Resources: Rate: self.der_cost/kwh, Cost: self.der_cost
              Delivery Service Adjustment: Rate: self.dsa_rate, Cost: self.dsa_cost
              Revenue Decoupling Adjustment: Rate: self.rda_rate, Cost: self.rda_cost
              New York State Assessment: Rate: self.nysa_rate, Cost: self.nysa_cost
              Revenue Based Pilots: Rate: self.rbp_rate, Cost: self.rbp_cost
              Suffolk Property Tax Adjustment: Rate: self.spta_rate, Cost: self.spta_cost
              Sales Tax: Rate: self.st_rate, Cost: self.st_cost

        Returns:
            str: as described by Format
        """
        return super().__str__() + \
            "\nTotal KWH: " + str(self.total_kwh) + ", Electric Heater KWH: " + str(self.eh_kwh) + ", Bank KWH: " + \
            str(self.bank_kwh) + \
            "\nDelivery & System Charges: Total Cost: " + str(self.dsc_total_cost) + \
            "\n  Basic: Rate: " + str(self.bs_rate) + "/day, Cost: " + str(self.bs_cost) + \
            "\n  First: KWH: " + str(self.first_kwh) + ", Rate: " + str(self.first_rate) + "/kwh, Cost: " + \
                str(self.first_cost) + \
            "\n  Next: KWH: " + str(self.next_kwh) + ", Rate: " + str(self.next_rate) + "/kwh, Cost: " + \
                str(self.next_cost) + \
            "\n  Customer Benefit Contribution: Rate: " + str(self.cbc_rate) + "/day, Cost: " + str(self.cbc_cost) + \
            "\n  Merchant Function Charge: Rate: " + str(self.mfc_rate) + "/kwh, Cost: " + str(self.mfc_cost) + \
            "\nPower Supply Charges: Total Cost: " + str(self.psc_total_cost) + \
            "\n  Power Supply: Rate: " + str(self.psc_rate) + "/kwh, Cost: " + str(self.psc_cost) + \
            "\nTaxes & Other Charges: Total Cost: " + str(self.toc_total_cost) + \
            "\n  Distributed Energy Resources: Rate: " + str(self.der_rate) + "/kwh, Cost: " + str(self.der_cost) + \
            "\n  Delivery Service Adjustment: Rate: " + str(self.dsa_rate) + ", Cost: " + str(self.dsa_cost) + \
            "\n  Revenue Decoupling Adjustment: Rate: " + str(self.rda_rate) + ", Cost: " + str(self.rda_cost) + \
            "\n  New York State Assessment: Rate: " + str(self.nysa_rate) + ", Cost: " + str(self.nysa_cost) + \
            "\n  Revenue Based Pilots: Rate: " + str(self.rbp_rate) + ", Cost: " + str(self.rbp_cost) + \
            "\n  Suffolk Property Tax Adjustment: Rate: " + str(self.spta_rate) + ", Cost: " + str(self.spta_cost) + \
            "\n  Sales Tax: Rate: " + str(self.st_rate) + ", Cost: " + str(self.st_cost)

    @classmethod
    def default_constructor(cls):
        return ElectricBillData(None, None, None, None, None, None, None, None, None, None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        raise NotImplementedError("ElectricBillData does not implement str_dict_constructor()")

    def copy(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Ratio applied to KWH, cost and BS Rate attributes.
        """
        bill_copy = super().copy(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

        if cost_ratio is not None:
            def dec_mult_none(left):
                return None if left is None else left * cost_ratio

            def int_mult_none(left):
                return None if left is None else int(left * cost_ratio)

            bill_copy.total_kwh = int_mult_none(bill_copy.total_kwh)
            bill_copy.eh_kwh = int_mult_none(bill_copy.eh_kwh)
            bill_copy.bank_kwh = int_mult_none(bill_copy.bank_kwh)

            bill_copy.bs_rate *= cost_ratio
            bill_copy.bs_cost *= cost_ratio
            bill_copy.first_kwh = int_mult_none(bill_copy.first_kwh)
            bill_copy.first_cost = dec_mult_none(bill_copy.first_cost)
            bill_copy.next_kwh = int_mult_none(bill_copy.next_kwh)
            bill_copy.next_cost = dec_mult_none(bill_copy.next_cost)
            bill_copy.cbc_cost = dec_mult_none(bill_copy.cbc_cost)
            bill_copy.mfc_cost = dec_mult_none(bill_copy.mfc_cost)
            bill_copy.dsc_total_cost *= cost_ratio

            bill_copy.psc_cost = dec_mult_none(bill_copy.psc_cost)
            bill_copy.psc_total_cost = dec_mult_none(bill_copy.psc_total_cost)
            bill_copy.der_cost = dec_mult_none(bill_copy.der_cost)
            bill_copy.dsa_cost = dec_mult_none(bill_copy.dsa_cost)
            bill_copy.rda_cost = dec_mult_none(bill_copy.rda_cost)
            bill_copy.nysa_cost = dec_mult_none(bill_copy.nysa_cost)
            bill_copy.rbp_cost = dec_mult_none(bill_copy.rbp_cost)
            bill_copy.spta_cost = dec_mult_none(bill_copy.spta_cost)
            bill_copy.st_cost = dec_mult_none(bill_copy.st_cost)
            bill_copy.toc_total_cost *= cost_ratio

            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to KWH, cost and BS Rate attributes."

        return bill_copy