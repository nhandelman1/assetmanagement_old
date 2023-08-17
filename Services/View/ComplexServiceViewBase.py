import datetime
from abc import abstractmethod
from Database.POPO.RealEstate import Address
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class ComplexServiceViewBase(SimpleServiceViewBase):
    """ Abstract base view class for complex service data display and input """
    @abstractmethod
    def __init__(self):
        super().__init__()

    def input_choose_input_data_or_read_bill(self):
        return "2"

    @abstractmethod
    def input_read_new_or_use_existing_bill_option(self):
        """ ask to read new file or use existing file option

        Returns:
            str: "1" if read new bill, anything else to use existing bill
        """
        raise NotImplementedError("input_read_new_or_use_existing_bill_option() not implemented by subclass")

    @abstractmethod
    def display_utility_data_found_or_not(self, found, month_year):
        """ display message that a utility's data was found or not

        Args:
            found (boolean): True if data was found, False if not.
            month_year (str): "MMYYYY" date format
        """
        raise NotImplementedError("display_data_found_or_not() not implemented by subclass")

    @abstractmethod
    def input_estimation_data(self, address, start_date, end_date):
        """ Input estimation data that isn't available elsewhere for bill estimation

        Args:
            address (Address): address of estimation data
            start_date (datetime.date): start date for estimation data
            end_date (datetime.date): end date for estimation data

        Returns:
            dict: (see subclass for more info)
        """
        raise NotImplementedError("input_estimation_data() not implemented by subclass")

    @abstractmethod
    def input_values_for_notes(self, notes_list):
        """ display note_types and notes and ask for input value for each note

        Args:
            notes_list (list[dict]): each dict must have keys "note_type" and "note"

        Returns:
            dict: with each note_type as keys and input value for that note_type as values
        """
        raise NotImplementedError("input_values_for_notes() not implemented by subclass")