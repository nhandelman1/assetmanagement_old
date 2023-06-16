from abc import ABC, abstractmethod
from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase


class SimpleServiceViewBase(ABC):
    """ Abstract base view class for service data display and input """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def input_read_new_bill(self):
        """ ask for new file name

        Returns:
            str: name of file to read
        """
        raise NotImplementedError("input_read_new_bill() not implemented by subclass")

    @abstractmethod
    def input_select_real_estate(self, re_dict):
        """ ask for user to select real estate from re_dict

        Args:
            re_dict (dict): dict of int real estate ids (keys) to RealEstate (values)

        Returns:
            int: real estate id
        """
        raise NotImplementedError("input_select_real_estate() not implemented by subclass")

    @abstractmethod
    def input_select_service_provider(self, sp_dict):
        """ ask for user to select provider from sp_dict

        Args:
            sp_dict (dict): dict of int service provider ids (keys) to ServiceProvider (values)

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