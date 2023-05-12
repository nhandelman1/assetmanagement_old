import datetime
from abc import ABC, abstractmethod
from Database.MySQLAM import MySQLAM
from Database.POPO.RealEstate import RealEstate, Address
from Database.POPO.UtilityBillDataBase import UtilityBillDataBase
from Database.POPO.UtilityDataBase import UtilityDataBase
from Database.POPO.UtilityProvider import UtilityProvider


class UtilityModelBase(ABC):
    """ Base model for utility model classes

    Attributes:
        amb_dict (dict): dict of (start_date, end_date): subclass of UtilityBillDataBase. actual monthly bills
        data_dict (dict): dict of date: subclass of UtilityDataBase. utility data for the month given by date
        emb_dict (dict): dict of (start_date, end_date): subclass of UtilityBillDataBase. estimated monthly bills
    """
    @abstractmethod
    def __init__(self):
        """ init function """
        self.amb_dict = {}
        self.data_dict = {}
        self.emb_dict = {}

    @abstractmethod
    def process_monthly_bill(self, filename):
        """ Open, process and return utility monthly bill

        self.amb_dict[(bill start date, bill end date)] is set with returned instance of UtilityBillDataBase subclass

        Args:
            filename (str): name of file in directory specified by subclass

        Returns:
            UtilityBillDataBase subclass with all required fields populated and as many non required fields as
            available populated
        """
        raise NotImplementedError("process_monthly_bill() not implemented by subclass")

    @abstractmethod
    def insert_monthly_bill_to_db(self, bill_data):
        """ Insert monthly utility bill to table

        Args:
            bill_data (UtilityBillDataBase): subclass instance to insert

        Raises:
            MySQLException if database insert issue occurs
        """
        raise NotImplementedError("insert_monthly_bill_to_db() not implemented by subclass")

    @abstractmethod
    def read_monthly_bill_from_db_by_start_date(self, start_date):
        """ read monthly utility bill from table by start date

        self.amb_dict[(bill start date, bill end date)] is set with returned instance of UtilityBillDataBase subclass
        if found

        Args:
            start_date (datetime.date): start date of bill

        Returns:
            UtilityBillDataBase subclass instance or None if no bill with start_date

        Raises:
            MySQLException if issue with database read
        """
        raise NotImplementedError("read_monthly_bill_from_db_by_start_date() not implemented by subclass")

    @abstractmethod
    def get_utility_data_instance(self, str_dict):
        """ Populate and return subclass of UtilityDataBase instance with values in str_dict

        Args:
            str_dict (dict): dict of field keys and str values

        Returns:
            UtilityDataBase subclass associated with a subclass of this class
        """
        raise NotImplementedError("get_utility_data_instance() not implemented by subclass")


    @abstractmethod
    def insert_monthly_data_to_db(self, utility_data):
        """ Insert monthly utility data to table

        Args:
            utility_data (UtilityDataBase): subclass instance to insert

        Raises:
            MySQLException if database insert issue occurs
        """
        raise NotImplementedError("insert_monthly_data_to_db() not implemented by subclass")

    @abstractmethod
    def read_monthly_data_from_db_by_month_year(self, month_year):
        """ read utility data from data table by month and year

        self.data_dict[month_year] is set with returned instance of UtilityDataBase subclass or None

        Args:
            month_year (str): month and year of data ("MMYYYY" format)

        Returns:
            UtilityDataBase subclass or None if no month_year found

        Raises:
            MySQLException if issue with database read
        """
        raise NotImplementedError("read_monthly_data_from_db_by_month_year() not implemented by subclass")

    @abstractmethod
    def initialize_monthly_bill_estimate(self, start_date, end_date):
        """ Initialize monthly bill estimate using data from actual bill

        self.emb_dict[(start_date, end_date)] is set with returned instance of UtilityBillDataBase subclass

        Args:
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill

        Returns:
            UtilityBillDataBase subclass with real_estate, provider, start_date and end_date set with same values as in
            actual bill

        Raises:
            ValueError if self.amb_dict does not contain bill data for specified start_date and end_date
        """
        raise NotImplementedError("initialize_monthly_bill_estimate() not implemented by subclass")

    @abstractmethod
    def do_estimate_monthly_bill(self, start_date, end_date):
        """ Run the process of estimating the monthly bill if solar (or other source) was or was not used

        Args:
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill

        Returns:
            emb with all applicable estimate fields set
        """
        raise NotImplementedError("do_estimate_monthly_bill() not implemented by subclass")

    def read_all_estimate_notes_by_reid_provider(self, real_estate, provider):
        """ read estimate notes from estimate_notes table by real estate and provider and order by note_order

        Args:
            real_estate (RealEstate): get notes for this real estate
            provider (UtilityProvider): get notes for this utility provider

        Returns:
            list(dict) of notes with keys id, real_estate_id, provider, note_type, note

        Raises:
            MySQLException if issue with database read
        """
        with MySQLAM() as mam:
            notes_list = mam.estimate_notes_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["provider", "=", provider]], order_bys=["note_order"])

        return notes_list

    def read_real_estate_by_address(self, address):
        """ read real estate from real_estate table by address

        Args:
            address (Address): notes for this real estate

        Returns:
            RealEstate if a real estate record matches address, else None

        Raises:
            MySQLException if issue with database read
        """
        with MySQLAM() as mam:
            re_list = mam.real_estate_read(wheres=[["address", "=", address]])

        return None if len(re_list) == 0 else re_list[0]