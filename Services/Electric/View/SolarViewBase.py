from abc import abstractmethod
from decimal import Decimal
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class SolarViewBase(SimpleServiceViewBase):
    """ Abstract base view class for Solar data display and input """

    @abstractmethod
    def __init__(self):
        """ init function """
        pass

    def display_bill_preprocess_warning(self):
        """ Display message that solar bill dates should match the electric bill dates with the associated property
        Dates are start date and end date
        """
        raise NotImplementedError("display_preprocess_warning() not implemented by subclass")

    def input_choose_input_data_or_read_bill(self):
        return "2"

    def input_tax_related_cost(self, bill_list):
        """ see superclass method docstring

        Solar bill tax related cost is always default value

        Args:
            see overriden method docstring

        Returns:
            see overriden method docstring
        """
        return [(bill, Decimal("NaN")) for bill in bill_list]

    @abstractmethod
    def input_read_new_hourly_data_file_or_skip(self, start_date, end_date):
        """ ask to read new hourly data file or skip this step

        Args:
            start_date (datetime.date): read file with data starting on this date
            end_date (datetime.date): read file with data ending on this date

        Returns:
            str: "1" to read sunpower hourly file. anything else to skip reading file
        """
        raise NotImplementedError("input_read_new_or_skip() not implemented by subclass")

    @abstractmethod
    def input_read_new_hourly_data_file(self, start_date, end_date):
        """ ask for new file name

        Args:
            start_date (datetime.date): read file with data starting on this date
            end_date (datetime.date): read file with data ending on this date

        Returns:
            str: name of file to read
        """
        raise NotImplementedError("input_read_new_hourly_data_file() not implemented by subclass")