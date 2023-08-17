from decimal import Decimal
from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase


class MortgageBillData(SimpleServiceBillDataBase):
    """ Mortgage implementation of SimpleServiceBillDataBase

    Attributes:
        see init docstring for attributes
    """
    def __init__(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, outs_prin,
                 esc_bal, prin_pmt, int_pmt, esc_pmt, other_pmt, paid_date=None, notes=None):
        """ init function

        Args:
            see superclass docstring
            outs_prin (Decimal): outstanding principal before principal payment is applied
            esc_bal (Decimal): escrow balance
            prin_pmt (Decimal): principal payment
            int_pmt (Decimal): interest payment
            esc_pmt (Decimal): escrow payment
            other_pmt (Decimal): other payment
        """
        super().__init__(real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost,
                         paid_date=paid_date, notes=notes)

        self.outs_prin = outs_prin
        self.esc_bal = esc_bal
        self.prin_pmt = prin_pmt
        self.int_pmt = int_pmt
        self.esc_pmt = esc_pmt
        self.other_pmt = other_pmt

    def __str__(self):
        """ __str__ override

        Format:
            super().__str__()


        Returns:
            str: as described by Format
        """
        return super().__str__() + "\nBalances (before payments applied): Principal: " + str(self.outs_prin) + \
            ", Escrow: " + str(self.esc_bal) + "\nPayments: Principal: " + str(self.prin_pmt) + ", Interest: " + \
            str(self.int_pmt) + ", Escrow: " + str(self.esc_pmt) + ", Other: " + str(self.other_pmt)

    @classmethod
    def default_constructor(cls):
        return MortgageBillData(None, None, None, None, None, None, None, None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        raise NotImplementedError("MortgageBillData does not implement str_dict_constructor()")

    def copy(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Ratio applied to all attributes.
        """
        bill_copy = super().copy(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

        if cost_ratio is not None:
            bill_copy.outs_prin *= cost_ratio
            bill_copy.esc_bal *= cost_ratio
            bill_copy.prin_pmt *= cost_ratio
            bill_copy.int_pmt *= cost_ratio
            bill_copy.esc_pmt *= cost_ratio
            bill_copy.other_pmt *= cost_ratio

            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to all attributes."

        return bill_copy