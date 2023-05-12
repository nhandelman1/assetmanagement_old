from abc import ABC, abstractmethod


class UtilityViewBase(ABC):
    """ Abstract base view class for utility data display and input """
    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def input_read_new_or_use_existing_bill_option():
        """ ask to read new file or use existing file option

        Returns:
            "1" if read new bill, anything else to use existing bill
        """
        raise NotImplementedError("input_read_new_or_use_existing_bill_option() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_read_new_bill():
        """ ask for new file name

        Returns:
            str name of file to read
        """
        raise NotImplementedError("input_read_new_bill() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_read_existing_bill_start_date():
        """ ask for existing bill start date

        Returns:
            date str YYYY-MM-DD format
        """
        raise NotImplementedError("input_read_existing_bill_start_date() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def display_utility_data_found_or_not(found, month_year):
        """ display message that a utility's data was found or not

        Args:
            found (boolean): True if data was found, False if not.
            month_year (str): "MMYYYY" date format
        """
        raise NotImplementedError("display_data_found_or_not() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_estimation_data(start_date, end_date):
        """ Input estimation data that isn't available elsewhere for bill estimation

        Args:
            start_date (datetime.date): start date for estimation data
            end_date (datetime.date): end date for estimation data

        Returns:
            dict (see subclass for more info)
        """
        raise NotImplementedError("input_estimation_data() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_values_for_notes(notes_list):
        """ display note_types and notes and ask for input value for each note

        Args:
            notes_list (list(dict)): each dict must have keys "note_type" and "note"

        Returns:
            dict with each note_type as keys and input value for that note_type as values
        """
        raise NotImplementedError("input_values_for_notes() not implemented by subclass")