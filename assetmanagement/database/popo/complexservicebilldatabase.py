from .simpleservicebilldatabase import SimpleServiceBillDataBase
from abc import abstractmethod


class ComplexServiceBillDataBase(SimpleServiceBillDataBase):
    """ Base class for complex data provided on service bill or relevant to service bill

    Complex data includes simple service data and an indicator of whether the service is actual or estimated. Complex
    data can also include more specific data used in calculating the total cost of the bill. This class is intended to
    be subclassed by specific forms of service (e.g. electric service) that include an estimation component and may or
    may not have subclass specific data fields.

    Attributes:
        see init docstring for attributes
    """
    @abstractmethod
    def __init__(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, is_actual,
                 paid_date=None, notes=None):
        """ init function

        Args:
            see super class init docstring
            is_actual (boolean): is this data from an actual bill (True) or estimated (False)
        """
        super().__init__(real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost,
                         paid_date=paid_date, notes=notes)

        self.is_actual = is_actual

    def __str__(self):
        """ __str__ override

        Format:
            Actual Bill: str(self.is_actual), super().__str__()

        Returns:
            str: as described by Format
        """
        return "Actual Bill: " + str(self.is_actual) + ", " + super().__str__()

    def db_dict_update(self, db_dict):
        super().db_dict_update(db_dict)
        self.is_actual = bool(self.is_actual)