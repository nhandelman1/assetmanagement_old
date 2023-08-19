from abc import ABC, abstractmethod
from decimal import Decimal

from assetmanagement.database.popo.simpleservicebilldatabase import SimpleServiceBillDataBase


class SimpleServiceViewBase(ABC):
    """ Abstract base view class for service data display and input """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def display_bill_preprocess_warning(self):
        """ Display this message before asking a user for input about a bill or processing the bill """
        raise NotImplementedError("display_bill_preprocess_warning() not implemented by subclass")

    @abstractmethod
    def input_choose_input_data_or_read_bill(self):
        """ ask to input bill data manually or read data from file

        Returns:
            str: "1" to input bill data manually or "2" to read data from file
        """
        raise NotImplementedError("input_choose_input_data_or_read_bill() not implemented by subclass")

    @abstractmethod
    def input_read_new_bill(self):
        """ ask for new file name

        Returns:
            str: name of file to read
        """
        raise NotImplementedError("input_read_new_bill() not implemented by subclass")

    @abstractmethod
    def input_select_real_estate(self, re_dict, pre_str=""):
        """ ask for user to select real estate from re_dict

        Args:
            re_dict (dict): dict of int real estate ids (keys) to RealEstate (values)
            pre_str(str): prepend this str to generic select real estate message determined by subclass. Default ""

        Returns:
            int: real estate id
        """
        raise NotImplementedError("input_select_real_estate() not implemented by subclass")

    @abstractmethod
    def input_select_service_provider(self, sp_dict, pre_str=""):
        """ ask for user to select provider from sp_dict

        Args:
            sp_dict (dict): dict of int service provider ids (keys) to ServiceProvider (values)
            pre_str(str): prepend this str to generic select service provider message determined by subclass. Default ""

        Returns:
            int: service provider id
        """
        raise NotImplementedError("input_select_service_provider() not implemented by subclass")

    @abstractmethod
    def input_bill_date(self, is_start=True):
        """ ask for user to input a bill date

        Args:
            is_start (boolean): True to ask for start date. False to ask for end date. Default True

        Returns:
            datetime.date:
        """
        raise NotImplementedError("input_bill_date() not implemented by subclass")

    @abstractmethod
    def input_paid_dates(self, unpaid_bill_list):
        """ ask for dates for unpaid bills with skip option

        bills in unpaid_bill_list are assumed to have no paid_date. paid_date will be overwritten in this function

        Args:
            unpaid_bill_list (list[SimpleServiceBillDataBase]): list of unpaid bills

        Returns:
            list[SimpleServiceBillDataBase]: list of bills from unpaid_bill_list where paid date is set (not skipped)
        """
        raise NotImplementedError("input_paid_dates() not implemented by subclass")

    @abstractmethod
    def input_paid_year(self, pre_str=""):
        """ ask for paid date year in format YYYY

        Args:
            pre_str(str): prepend this str to generic input paid year message determined by subclass. Default ""

        Returns:
            int: year
        """
        raise NotImplementedError("input_paid_year() not implemented by subclass")

    @abstractmethod
    def display_bill(self, bill):
        """ display the bill

        Display format determined by subclass but will always display at minimum some representation of all instance
        attributes of the bill.

        Args:
            bill (SimpleServiceBillDataBase):
        """
        raise NotImplementedError("display_bill() not implemented by subclass")

    @abstractmethod
    def display_bills(self, bill_list):
        """ display the bills

        Each bill will be displayed as determined by self.display_bill(). Any display before or after each bill is
        determined in this function by subclass.

        Args:
            bill_list (list[SimpleServiceBillDataBase]):
        """
        raise NotImplementedError("display_bills() not implemented by subclass")

    @abstractmethod
    def input_partial_bill_portion(self, bill_list):
        """ ask for portion (as a ratio) of existing bill(s) that the new bill(s) will be with cancel option

        Display all bills in bill_list.
        User asked to enter a ratio 0-1 (inclusive) that will apply to all bills, 'skip' to enter ratio per bill or
        'cancel' to not create any new bills.
        If 'skip', user asked to enter a ratio 0-1 (inclusive) per bill or 'cancel' to not create a new bill.
        No bill in bill_list will be altered

        Args:
            bill_list (list[SimpleServiceBillDataBase]): subclass instances. bills being asked about

        Returns:
            list[tuple[SimpleServiceBillDataBase, Decimal]]: sub tuples are 2-tuples where the first element is the
                bill and the second element is the ratio (0-1 inclusive) of the bill that the new bill will be or
                Decimal(NaN) to not create a copy
        """
        raise NotImplementedError("input_partial_bill_portion() not implemented by subclass")

    @abstractmethod
    def input_tax_related_cost(self, bill_list):
        """ Ask user to input tax related cost or use default value determined by subclass for each bill in bill_list

        If all bills in bill_list have the same real estate:
            Display all bills in bill_list.
            User asked to enter a tax related cost that will apply to all bills (either a specific value or blank to use
                default value as determined by subclass) or 'skip' to enter tax related cost per bill
            If 'skip', user asked to enter a tax related cost per bill, either a specific value or blank to use default
                value as determined by subclass
        If at least one bill has a different real estate:
            User asked to enter a tax related cost per bill, either a specific value or blank to use default value as
                determined by subclass

        Args:
            bill_list (list[SimpleServiceBillDataBase]): subclass instances. bills being asked about

        Returns:
            list[tuple[SimpleServiceBillDataBase, Decimal]]: sub tuples are 2-tuples where the first element is the
                bill and the second element is the tax related cost of the bill or Decimal(NaN) to use default tax
                related cost. bills are unaltered and in the same order as in bill_list
        """
        raise NotImplementedError("input_tax_related_cost() not implemented by subclass")