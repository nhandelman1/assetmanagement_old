import datetime
import decimal
import colorama
import textwrap
from Services.View.SimpleConsoleUIBase import SimpleConsoleUIBase
from Services.Depreciation.View.DepreciationViewBase import DepreciationViewBase


class DepreciationConsoleUI(SimpleConsoleUIBase, DepreciationViewBase):
    """ Implementation of SimpleServiceViewBase for use with depreciation console UI """

    def __init__(self):
        super().__init__()

    def input_read_new_bill(self):
        raise NotImplementedError("DepreciationConsoleUI does not implement input_read_new_bill()")

    def input_depreciation_year(self):
        current_year = datetime.date.today().year
        year_print = "\nEnter depreciation year with format YYYY (must be previous year (before " \
                     + str(current_year) + ")): "

        while True:
            try:
                year = int(input(year_print))
                if year >= current_year:
                    raise ValueError
                break
            except ValueError:
                print(colorama.Fore.RED, "Invalid year or year is not a previous year. Try Again.")
                print(colorama.Style.RESET_ALL)

        return year

    def input_period_usages(self, bill_list):
        if len(bill_list) == 0:
            return bill_list

        print("\nInput period usages for depreciation items. Note that for a partial year, 100% usage means the "
              "property was used for the entirety of the partial year it was in service.")
        for bill in bill_list:
            rpv_str = "\n**** Real Property Value Data ****\n" + textwrap.fill(str(bill.real_property_value), width=150)
            bill_str = "\n**** Bill Data ****\n" + \
                       textwrap.fill("start date: " + str(bill.start_date) + ", end date: " + str(bill.end_date) +
                                     ", total cost: " + str(bill.total_cost) + ", paid date: " + str(bill.paid_date) +
                                     ", notes: " + str(bill.notes), width=150)

            while True:
                try:
                    print(rpv_str, bill_str, "\n**** Input Period Usage ****")
                    yup = decimal.Decimal(input("Enter period usage as a percent (0 - 100 inclusive) for this "
                                                "depreciation item: "))
                    if yup < decimal.Decimal(0) or yup > decimal.Decimal(100):
                        raise ValueError
                    bill.period_usage_pct = yup
                    break
                except (decimal.InvalidOperation, ValueError):
                    print(colorama.Fore.RED, "Period usage percent must be between 0 and 100. Try Again.")
                    print(colorama.Style.RESET_ALL)

        return bill_list
