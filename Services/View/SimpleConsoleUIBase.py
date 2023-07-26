import decimal

import colorama
import datetime
from abc import abstractmethod
from decimal import Decimal
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class SimpleConsoleUIBase(SimpleServiceViewBase):
    """ Abstract base view class for service data display and input through the console

    This is an intermediary base class that implements functions in SimpleServiceViewBase that are common to any
    subclasses of this class.
    """

    @abstractmethod
    def __init__(self):
        pass

    def input_select_real_estate(self, re_dict, pre_str=""):
        re_print = "\n"
        re_ids = list(re_dict.keys())

        for re_id, real_estate in re_dict.items():
            re_print += str(re_id) + " : " + str(real_estate.address.value) + "\n"
        re_print += (pre_str + "Select a real estate location from the previous list: ")

        while True:
            try:
                select_id = int(input(re_print))
            except ValueError:
                select_id = None

            if select_id not in re_ids:
                print("Invalid Selection. Try Again.")
            else:
                break

        return select_id

    def input_select_service_provider(self, sp_dict, pre_str=""):
        sp_print = "\n"
        sp_ids = list(sp_dict.keys())

        for sp_id, service_provider in sp_dict.items():
            sp_print += str(sp_id) + " : " + str(service_provider.provider.value) + "\n"
        sp_print += (pre_str + "Select a service provider from the previous list: ")

        while True:
            try:
                select_id = int(input(sp_print))
            except ValueError:
                select_id = None

            if select_id not in sp_ids:
                print("Invalid Selection. Try Again.")
            else:
                break

        return select_id

    def input_bill_date(self, is_start=True):
        start_or_end = "start" if is_start else "end"
        while True:
            date = input("\nEnter bill " + start_or_end + " date (YYYYMMDD, do not include quotes): ")
            try:
                date = datetime.datetime.strptime(date, "%Y%m%d").date()
                break
            except ValueError:
                print(colorama.Fore.RED, "Invalid date format. Try again.")
                print(colorama.Style.RESET_ALL)

        return date

    def input_paid_dates(self, unpaid_bill_list):
        paid_bill_list = []
        for bill in unpaid_bill_list:
            while True:
                print("\nUnpaid Bill Data: " + str(bill.real_estate.address.value) + ", "
                      + str(bill.service_provider.provider.value) + ", " + str(bill.start_date) + " - "
                      + str(bill.end_date) + ", " + str(bill.total_cost) + ", Notes: " + str(bill.notes))
                start_date = input("Enter bill paid date (YYYYMMDD, do not include quotes) or 'skip' to not enter a "
                                   "paid date: ")
                try:
                    if start_date != "skip":
                        bill.paid_date = datetime.datetime.strptime(start_date, "%Y%m%d").date()
                        paid_bill_list.append(bill)
                    break
                except ValueError:
                    print(colorama.Fore.RED, "Invalid date value or format. Try again.")
                    print(colorama.Style.RESET_ALL)

        return paid_bill_list

    def input_paid_year(self, pre_str=""):
        while True:
            year = input(pre_str + "Enter paid year (YYYY, do not include quotes): ")
            try:
                year = int(year)
                break
            except ValueError:
                print(colorama.Fore.RED, "Invalid year format. Try again.")
                print(colorama.Style.RESET_ALL)

        return year

    def display_bill(self, bill):
        """ Print bill using bill's __str__ function

        Args:
            bill (SimpleServiceBillDataBase):
        """
        print(str(bill))

    def input_partial_bill_portion(self, bill_list):
        """ ask for portion (as a ratio) of existing bill(s) that the new bill(s) will be with cancel option

        Display all bills in bill_list.
        User asked to enter a ratio 0-1 (inclusive) that will apply to all bills, 'skip' to enter ratio per bill or
        'cancel' to not create any new bills.
        If 'skip', user asked to enter a ratio 0-1 (inclusive) per bill or 'cancel' to not create a new bill.
        No bill in bill_list will be altered

        Args:
            bill_list (list[SimpleServiceBillDataBase]): bills being asked about

        Returns:
            list[tuple[SimpleServiceBillDataBase, Decimal]]: sub tuples are 2-tuples where the first element is the
                bill and the second element is the ratio (0-1 inclusive) of the bill that the new bill will be or
                Decimal(NaN) to not create a copy
        """
        if len(bill_list) == 0:
            return []

        def input_func(is_all):
            if is_all:
                print_str = "See all bills listed. Enter 'skip' to enter ratio per bill. Enter 'cancel' to create no " \
                            "new bills. Enter ratio 0-1 (inclusive) of the existing bill(s) that the new bill(s) " \
                            "will be: "
            else:
                print_str = "Enter 'cancel' or 'skip' to not create a new partial bill for this existing bill. " \
                            "Enter ratio 0 - 1 (inclusive) of the existing bill that the new bill will be: "
            while True:
                ratio1 = input(print_str)

                if ratio1 == "skip":
                    if is_all:
                        break
                    else:
                        ratio1 = "NaN"

                if ratio1 == "cancel":
                    ratio1 = "NaN"

                try:
                    ratio1 = Decimal(ratio1)
                    if not ratio1.is_nan() and (ratio1 < Decimal(0) or ratio1 > Decimal(1)):
                        raise ValueError
                    break
                except (ValueError, decimal.InvalidOperation):
                    print(colorama.Fore.RED, "Invalid value. Try again.")
                    print(colorama.Style.RESET_ALL)

            return ratio1

        ret_list = []

        self.display_bills(bill_list)
        ratio = input_func(True)
        if isinstance(ratio, Decimal):
            # Decimal between 0 and 1 inclusive or Decimal(NaN)
            ret_list = [(bill, ratio) for bill in bill_list]
        else:  # skip - enter ratio per bill
            for bill in bill_list:
                print("\n")
                self.display_bill(bill)
                ratio = input_func(False)
                ret_list.append((bill, ratio))

        return ret_list