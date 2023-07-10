import colorama
import datetime
from abc import abstractmethod
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class SimpleConsoleUIBase(SimpleServiceViewBase):
    """ Abstract base view class for service data display and input through the console

    This is an intermediary base class that implements functions in SimpleServiceViewBase that are common to any
    subclasses of this class.
    """

    @abstractmethod
    def __init__(self):
        pass

    def input_select_real_estate(self, re_dict):
        re_print = "\n"
        re_ids = list(re_dict.keys())

        for re_id, real_estate in re_dict.items():
            re_print += str(re_id) + " : " + str(real_estate.address.value) + "\n"
        re_print += "Select a real estate location from the previous list: "

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

    def input_select_service_provider(self, sp_dict):
        sp_print = "\n"
        sp_ids = list(sp_dict.keys())

        for sp_id, service_provider in sp_dict.items():
            sp_print += str(sp_id) + " : " + str(service_provider.provider.value) + "\n"
        sp_print += "Select a service provider from the previous list: "

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