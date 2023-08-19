from abc import abstractmethod
from typing import Optional, Union
import datetime

import pandas as pd

from .simpleservicemodelbase import SimpleServiceModelBase, BillDict
from assetmanagement.database.mysqlam import MySQLAM
from assetmanagement.database.popo.realestate import RealEstate, Address
from assetmanagement.database.popo.serviceprovider import ServiceProviderEnum


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

    def clear_model(self):
        """ Call clear() on attribute dict(s) """
        super().clear_model()
        self.data_dict.clear()
        self.esb_dict.clear()

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
    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=None):
        """ Read service bills from table by real estate(s), service provider(s), paid date range inclusive

        Service bills are inserted in self.asb_dict or self.esb_dict
        See SimpleServiceModelBase.resppdr_wheres_clause() when overriding this function.
        See self.bills_post_read() when overriding this function.

        Args:
            real_estate_list (list[RealEstate]): real estate location(s) of bills. Default () for all locations
            service_provider_list (list[ServiceProvider]): service provider(s) of bills. Default () for all providers
            paid_date_min (Optional[datetime.date]): bills with paid date greater than or equal to this date. Default
                None for no minimum
            paid_date_max (Optional[datetime.date]): bills with paid date less than or equal to this date. Default None
                for no maximum
            to_pd_df (boolean): True to return data as a dataframe. Default False to return bill list

        Returns:
            Union[list[ComplexServiceBillDataBase], pd.DataFrame]:
                list: subclass instances. empty if no bills matching parameters. ordered by paid date increasing
                dataframe: with all bill data ordered by start date decreasing then actual before estimated bills

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_service_bills_from_db_by_resppdr() not implemented by subclass")

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
            provider (Optional[ServiceProviderEnum]): service provider of actual bill. Default None needs to be set to a
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
            provider (Optional[ServiceProviderEnum]): service provider of actual bill. Default None needs to be set to a
                certain provider by each subclass

        Returns:
            ComplexServiceBillDataBase: estimated bill with all applicable estimate fields set
        """
        raise NotImplementedError("do_estimate_monthly_bill() not implemented by subclass")

    def read_all_service_bills_from_db_unpaid(self):
        """ Read all complex bills that have a null paid date and are actual bills

        Superclass only requires bills to have a null paid date. This class also requires bills to be actual
        Complex service bills are inserted in self.asb_dict

        Returns:
            list[ComplexServiceBillDataBase]: empty list if no bill with null paid date

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_all_service_bills_from_db_unpaid() not implemented by subclass")

    def bills_post_read(self, bill_list, to_pd_df=False, **kwargs):
        """ Convenience function to save bill_list to model and convert bill_list to dataframe if specified

        Args:
            bill_list (list[ComplexServiceBillDataBase]): subclass instances
            to_pd_df (boolean): True to return data as a dataframe. Default False to return bill_list unaltered

        Returns:
            Union[list[ComplexServiceBillDataBase], pd.DataFrame]:
                list: bill_list unaltered
                dataframe: with all bill data ordered by start date decreasing then actual before estimated bills
        """
        if to_pd_df:
            if len(bill_list) == 0:
                df = self.read_one_bill().to_pd_df(**kwargs).head(0)
            else:
                df = pd.DataFrame()

                for bill in bill_list:
                    df = pd.concat([df, bill.to_pd_df()], ignore_index=True)
                    if bill.is_actual:
                        self.asb_dict.insert_bills(bill)
                    else:
                        self.esb_dict.insert_bills(bill)

            return df.sort_values(by=["start_date", "is_actual"])
        else:
            for bill in bill_list:
                if bill.is_actual:
                    self.asb_dict.insert_bills(bill)
                else:
                    self.esb_dict.insert_bills(bill)
            return bill_list

    def read_all_estimate_notes_by_reid_provider(self, real_estate, provider):
        """ read estimate notes from estimate_notes table by real estate and provider and order by note_order

        Args:
            real_estate (RealEstate): get notes for this real estate
            provider (Union[ServiceProvider, ServiceProviderEnum]): get notes for this service provider

        Returns:
            list[dict]: of notes with keys id, real_estate_id, service_provider_id, note_type, note, note_order

        Raises:
            ValueError: if provider is ServiceProviderEnum but no ServiceProvider is found
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            if isinstance(provider, ServiceProviderEnum):
                service_provider = mam.service_provider_read(wheres=[["provider", "=", provider]])
                if len(service_provider) == 0:
                    raise ValueError("No Service Provider found for Service Provider Enum: " + str(provider.value))
                provider = service_provider[0]
            notes_list = mam.estimate_notes_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", provider.id]],
                order_bys=["note_order"])

        return notes_list