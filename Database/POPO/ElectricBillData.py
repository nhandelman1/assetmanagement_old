from decimal import Decimal
from Database.POPO.UtilityBillDataBase import UtilityBillDataBase


class ElectricBillData(UtilityBillDataBase):
    """ Actual or estimated data provided on monthly electric bill or relevant to monthly bill

    Attributes:
        see super class docstring
        see init docstring for attributes (db_dict is not kept as an attribute)
    """

    def __init__(self, real_estate, provider, start_date, end_date, total_kwh, eh_kwh, bank_kwh, total_cost, bs_rate,
                 bs_cost, dsc_total_cost, toc_total_cost, is_actual, first_kwh=None, first_rate=None, first_cost=None,
                 next_kwh=None, next_rate=None, next_cost=None, cbc_rate=None, cbc_cost=None, mfc_rate=None,
                 mfc_cost=None, psc_rate=None, psc_cost=None, psc_total_cost=None, der_rate=None, der_cost=None,
                 dsa_rate=None, dsa_cost=None, rda_rate=None, rda_cost=None, nysa_rate=None, nysa_cost=None,
                 rbp_rate=None, rbp_cost=None, spta_rate=None, spta_cost=None, st_rate=None, st_cost=None,
                 db_dict=None):
        """ init function

        Args:
            see super class init docstring
            total_kwh (int): nonnegative total kwh used from provider
            eh_kwh (int): electric heater kwh usage
            bank_kwh (int): nonnegative banked kwh
            total_cost (Decimal): total bill cost
            bs_rate (Decimal): basic service charge rate
            bs_cost (Decimal): basic service charge cost
            dsc_total_cost (Decimal): delivery and service charge total cost
            toc_total_cost (Decimal): taxes and other charges total cost
            first_kwh (int, optional): kwh used at first rate. will not be in bill if none used. Default None
            first_rate (Decimal, optional): first rate. will not be in bill if none used. Default None
            first_cost (Decimal, optional): first cost. will not be in bill if none used. Default None
            next_kwh (int, optional): kwh used at next rate. will not be in bill if none used. Default None
            next_rate (Decimal, optional): next rate. will not be in bill if none used. Default None
            next_cost (Decimal, optional): next cost. will not be in bill if none used. Default None
            cbc_rate (Decimal, optional): customer benefit contribution charge rate. Default None
            cbc_cost (Decimal, optional): customer benefit contribution charge cost. Default None
            mfc_rate (Decimal, optional): merchant function charge rate. Default None
            mfc_cost (Decimal, optional): merchant function charge cost. Default None
            psc_rate (Decimal, optional): power supply charge rate. Default None
            psc_cost (Decimal, optional): power supply charge cost. Default None
            psc_total_cost (Decimal, optional): power supply charge total cost. Default None
            der_rate (Decimal, optional): distributed energy resources charge rate. Default None
            der_cost (Decimal, optional): distributed energy resources charge cost. Default None
            dsa_rate (Decimal, optional): delivery service adjustment rate. Default None
            dsa_cost (Decimal, optional): delivery service adjustment cost. Default None
            rda_rate (Decimal, optional): revenue decoupling adjustment rate. Default None
            rda_cost (Decimal, optional): revenue decoupling adjustment cost. Default None
            nysa_rate (Decimal, optional): new york state assessment rate. Default None
            nysa_cost (Decimal, optional): new york state assessment cost. Default None
            rbp_rate (Decimal, optional): revenue based pilots rate. Default None
            rbp_cost (Decimal, optional): revenue based pilots cost. Default None
            spta_rate (Decimal, optional): revenue decoupling adjustment rate. Default None
            spta_cost (Decimal, optional): suffolk property tax adjustment cost. Default None
            st_rate (Decimal, optional): sales tax rate. Default None
            st_cost (Decimal, optional): sales tax cost. Default None
            db_dict (dict, optional): dictionary holding arguments. if an argument is in the dictionary, it will
                overwrite an argument provided explicitly through the argument variable
        """
        super().__init__(real_estate, provider, start_date, end_date, is_actual)

        self.total_kwh = total_kwh
        self.eh_kwh = eh_kwh
        self.bank_kwh = bank_kwh
        self.total_cost = total_cost
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

        self.db_dict_update(db_dict)