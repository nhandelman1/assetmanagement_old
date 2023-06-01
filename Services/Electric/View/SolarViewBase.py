from abc import ABC, abstractmethod


class SolarViewBase(ABC):
    """ Abstract base view class for Solar data display and input """

    @abstractmethod
    def __init__(self):
        """ init function """
        pass

    @staticmethod
    @abstractmethod
    def input_read_new_or_skip(start_date, end_date):
        """ ask to read new hourly data file or skip this step

        Args:
            start_date (datetime.date): read file with data starting on this date
            end_date (datetime.date): read file with data ending on this date

        Returns:
            str: "1" to read sunpower hourly file. anything else to skip reading file
        """
        raise NotImplementedError("input_read_new_or_skip() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_read_new_hourly_data_file(start_date, end_date):
        """ ask for new file name

        Args:
            start_date (datetime.date): read file with data starting on this date
            end_date (datetime.date): read file with data ending on this date

        Returns:
            str: name of file to read
        """
        raise NotImplementedError("input_read_new_hourly_data_file() not implemented by subclass")