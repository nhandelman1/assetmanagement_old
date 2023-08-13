from abc import abstractmethod
from decimal import Decimal
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase
from Database.POPO.DepreciationBillData import DepreciationBillData


class DepreciationViewBase(SimpleServiceViewBase):

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()

    def input_read_new_bill(self):
        """ ask for new file name

        Returns:
            str: name of file to read
        """
        raise NotImplementedError("DepreciationViewBase does not implement input_read_new_bill()")

    def input_tax_related_cost(self, bill_list):
        """ see superclass method docstring

        Depreciation bill tax related cost is always default value

        Args:
            see overriden method docstring

        Returns:
            see overriden method docstring
        """
        return [(bill, Decimal("NaN")) for bill in bill_list]

    def input_depreciation_year(self):
        """ ask for year in which to calculate all depreciation bills

        This function validates that the input year is a previous year.

        Returns:
            int: year
        """
        raise NotImplementedError("input_depreciation_year() not implemented by subclass")

    def input_period_usages(self, bill_list):
        """ ask for percent of period the depreciation item is used for each bill

        period is a full year except for purchase year, disposal year or last year of recovery period. For example,
        for a property purchased in July 2021, 100% usage indicates that the property was used for 100% of the period
        between July and December 31, 2021.

        Args:
            bill_list (list[DepreciationBillData]):

        Returns:
            list[DepreciationBillData]: bill_list with period_usage_pct set for each bill in list
        """
        raise NotImplementedError("input_period_usages() not implemented by subclass")
