from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase


class SimpleServiceBillData(SimpleServiceBillDataBase):
    """ Simple implementation of SimpleServiceBillDataBase

    Attributes:
        see init docstring for attributes
    """
    def __init__(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, paid_date=None,
                 notes=None):
        """ init function

        Args:
            see superclass docstring
        """
        super().__init__(real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost,
                         paid_date=paid_date, notes=notes)

    @classmethod
    def default_constructor(cls):
        return SimpleServiceBillData(None, None, None, None, None, None)

    @classmethod
    def str_dict_constructor(cls, str_dict):
        raise NotImplementedError("SimpleServiceBillData does not implement str_dict_constructor()")

    def copy(self, cost_ratio=None, real_estate=None, **kwargs):
        return super().copy(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)
