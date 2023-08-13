import decimal
import colorama
import datetime
import textwrap
from abc import abstractmethod
from decimal import Decimal, InvalidOperation
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase
from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase


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
                ratio1 = input(textwrap.fill(print_str, width=100))

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

    def input_blank_skip_or_dollar_decimal(self, ask_str, allow_blank, allow_skip):
        """ Ask to input a decimal value (*.XX format) or blank if allowed

        Args:
            ask_str (str): indication of what the value being entered relates to."\n" is prepended and
                "\nEnter [blank], ['skip'], [or] decimal value (*.XX format): " is appended in this function
            allow_blank (boolean): True to allow blank as valid input. False to require a dollar value input.
            allow_skip (boolean): True to allow 'skip' as valid input. False to not allow 'skip' as valid input.

        Returns:
            str: "" if allow_blank is True and blank is entered. 'skip' if allow_skip is True and 'skip' is
                entered. str format *.XX otherwise
        """
        print_str = ""
        if allow_blank:
            print_str += " blank, "
        if allow_skip:
            print_str += " 'skip', "
        print_str += ("" if print_str == "" else " or ") + " decimal value: (*.XX format): "
        print_str = "\nEnter" + print_str

        print_str = "\n" + textwrap.fill(ask_str, width=100) + print_str

        while True:
            dol_val = input(print_str)

            if allow_blank and dol_val == "":
                break

            if allow_skip and dol_val == "skip":
                break

            try:
                Decimal(dol_val)
            except InvalidOperation:
                print(colorama.Fore.RED, "Invalid format. Try again.")
                print(colorama.Style.RESET_ALL)
                continue

            tc_split = dol_val.split(".")
            if len(tc_split) != 2 or len(tc_split[1]) != 2:
                print(colorama.Fore.RED, "Must have 2 decimal places. Try again.")
                print(colorama.Style.RESET_ALL)
                continue

            break

        return dol_val

    def input_tax_related_cost_helper(self, bill_list, bill_type, default_tax_rel_field, default_not_tax_rel_val):
        """ Ask user to input tax related cost or use default value for each bill in bill_list

        See SimpleServiceViewBase.input_tax_related_cost(). Several subclasses of SimpleServiceViewBase override
        input_tax_related_cost() using a substantially similar algorithm. This function centralizes that algorithm.

        Args:
            bill_list (list[SimpleServiceBillDataBase]): subclass instances. bills being asked about
            bill_type (str): what type of bill is this, e.g. "Mortgage", "Natural Gas"
            default_tax_rel_field (str): an indicator of which field in bill to use as the default tax related cost
                field for bills with real_estate.bill_tax_related == True
            default_not_tax_rel_val (str): the default tax related cost value for bills with
                real_estate.bill_tax_related == False

        Returns:
            list[tuple[SimpleServiceBillDataBase, Decimal]]: see SimpleServiceViewBase.input_tax_related_cost()
        """
        if len(bill_list) == 0:
            return bill_list

        ret_list = []

        if len(set([bill.real_estate for bill in bill_list])) == 1:
            # real estate in all bills is the same
            self.display_bills(bill_list)
            if bill_list[0].real_estate.bill_tax_related:
                print_str = bill_type + " bills associated with this real estate are typically tax related. " \
                            "Leave blank to use " + default_tax_rel_field + " cost of each bill as the tax related " \
                            "cost for that bill or enter a tax related cost to apply to all bills. Enter 'skip' to " \
                            "enter a tax related cost per bill."
            else:
                print_str = bill_type + " bills associated with this real estate are typically NOT tax " \
                            "related. Leave blank to use " + default_not_tax_rel_val + " as the tax related cost for " \
                            "each bill or enter a tax related cost to apply to all bills. Enter 'skip' to enter a " \
                            "tax related cost per bill."
            tax_rel_cost = self.input_blank_skip_or_dollar_decimal(print_str, True, True)

            if tax_rel_cost != "skip":
                tax_rel_cost = Decimal("NaN" if tax_rel_cost == "" else tax_rel_cost)
                ret_list = [(bill, tax_rel_cost) for bill in bill_list]

        if len(ret_list) == 0:
            # at least one real estate in bills is different or user chose to enter tax related cost per bill
            for bill in bill_list:
                self.display_bill(bill)
                if bill.real_estate.bill_tax_related:
                    print_str = bill_type + " bills associated with this real estate are typically tax " \
                                "related. Leave blank to use " + default_tax_rel_field + " cost as the tax related " \
                                "cost or enter a tax related cost."
                else:
                    print_str = bill_type + " bills associated with this real estate are typically NOT tax " \
                                "related. Leave blank to use " + default_not_tax_rel_val + " as the tax related cost " \
                                "or enter a tax related cost."
                tax_rel_cost = self.input_blank_skip_or_dollar_decimal(print_str, True, False)
                tax_rel_cost = Decimal("NaN" if tax_rel_cost == "" else tax_rel_cost)
                ret_list.append((bill, tax_rel_cost))

        return ret_list