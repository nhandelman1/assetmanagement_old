from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase


class SimpleServiceBillData(SimpleServiceBillDataBase):
    """ Simple implementation of SimpleServiceBillDataBase

    Attributes:
        see init docstring for attributes (db_dict is not kept as an attribute)
    """
    def __init__(self, real_estate, service_provider, start_date, end_date, total_cost, paid_date=None, notes=None,
                 db_dict=None):
        """ init function

        Args:
            see superclass docstring
        """
        super().__init__(real_estate, service_provider, start_date, end_date, total_cost, paid_date=paid_date,
                         notes=notes)

        self.db_dict_update(db_dict)

    def copy(self, cost_ratio=None, real_estate=None, **kwargs):
        return super().copy(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)
