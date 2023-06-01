import datetime
from abc import abstractmethod
from typing import Optional
from Database.MySQLAM import MySQLAM
from Database.POPO.RealEstate import RealEstate, Address
from Database.POPO.UtilityDataBase import UtilityDataBase
from Database.POPO.ServiceProvider import ServiceProvider
from Database.POPO.ComplexServiceBillDataBase import ComplexServiceBillDataBase
from Services.Model.SimpleServiceModelBase import SimpleServiceModelBase, BillDict


class ComplexServiceModelBase(SimpleServiceModelBase):
    """ Base model for complex service model classes

    Complex service has all data and functionality of a simple service, but also includes more data used for estimating
    what the service would have cost under different circumstances. Complex services provide bills with detailed data
    and subclasses

    Attributes:
        data_dict (dict): dict of date: subclass of UtilityDataBase. utility data for the month given by date
        esb_dict (BillDict): estimated service bills
    """
    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()
        self.data_dict = {}
        self.esb_dict = BillDict()

    @abstractmethod
    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProvider]: list of ServiceProvider
        """
        raise NotImplementedError("valid_providers() not implemented by subclass")

    @abstractmethod
    def process_service_bill(self, filename):
        """ Open, process and return service bill

        Returned instance of ComplexServiceBillDataBase subclass is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by subclass

        Returns:
            ComplexServiceBillDataBase: subclass with all required fields populated and as many non required fields as
            available populated

        Raises:
            FileNotFoundError: if file not found
        """
        raise NotImplementedError("process_service_bill() not implemented by subclass")

    @abstractmethod
    def read_all_service_bills_from_db(self):
        """ Read all service bills

        Service bills are inserted in self.asb_dict

        Returns:
            pd.DataFrame: with all service bill data ordered by most recent to oldest start date

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_all_service_bills_from_db() not implemented by subclass")

    @abstractmethod
    def get_utility_data_instance(self, str_dict):
        """ Populate and return subclass of UtilityDataBase instance with values in str_dict

        Args:
            str_dict (dict): dict of field keys and str values

        Returns:
            UtilityDataBase: subclass associated with a subclass of this class
        """
        raise NotImplementedError("get_utility_data_instance() not implemented by subclass")

    @abstractmethod
    def insert_monthly_data_to_db(self, utility_data):
        """ Insert monthly utility data to table

        Args:
            utility_data (UtilityDataBase): subclass instance to insert

        Raises:
            MySQLException: if database insert issue occurs
        """
        raise NotImplementedError("insert_monthly_data_to_db() not implemented by subclass")

    @abstractmethod
    def read_monthly_data_from_db_by_month_year(self, month_year):
        """ read utility data from data table by month and year

        self.data_dict[month_year] is set with returned instance of UtilityDataBase subclass or None

        Args:
            month_year (str): month and year of data ("MMYYYY" format)

        Returns:
            Optional[UtilityDataBase]: subclass or None if no month_year found

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_monthly_data_from_db_by_month_year() not implemented by subclass")

    @abstractmethod
    def initialize_complex_service_bill_estimate(self, address, start_date, end_date, provider=None):
        """ Initialize complex service bill estimate using data from actual bill

        Returned instance of ComplexServiceBillDataBase subclass is added to self.esb_dict

        Args:
            address (Address): address of actual bill
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill
            provider (Optional[ServiceProvider]): service provider of actual bill. Default None needs to be set to a
                certain provider by each subclass

        Returns:
            ComplexServiceBillDataBase: subclass with real_estate, provider, start_date and end_date set with same
                values as in actual bill. other values may also be set

        Raises:
            ValueError: if self.asb_dict does not contain bill data for specified parameters
        """
        raise NotImplementedError("initialize_monthly_bill_estimate() not implemented by subclass")

    @abstractmethod
    def do_estimate_monthly_bill(self, address, start_date, end_date, provider=None):
        """ Run the process of estimating the complex service bill under other circumstances

        Other circumstances initially relate to solar usage but could be extended to other sources.

        Args:
            address (Address): address of actual bill
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill
            provider (Optional[ServiceProvider]): service provider of actual bill. Default None needs to be set to a
                certain provider by each subclass

        Returns:
            ComplexServiceBillDataBase: estimated bill with all applicable estimate fields set
        """
        raise NotImplementedError("do_estimate_monthly_bill() not implemented by subclass")

    def read_all_estimate_notes_by_reid_provider(self, real_estate, provider):
        """ read estimate notes from estimate_notes table by real estate and provider and order by note_order

        Args:
            real_estate (RealEstate): get notes for this real estate
            provider (ServiceProvider): get notes for this service provider

        Returns:
            list[dict]: of notes with keys id, real_estate_id, provider, note_type, note

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            notes_list = mam.estimate_notes_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["provider", "=", provider]], order_bys=["note_order"])

        return notes_list