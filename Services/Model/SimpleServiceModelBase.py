import datetime
import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Union
from Database.MySQLAM import MySQLAM
from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase
from Database.POPO.RealEstate import Address, RealEstate
from Database.POPO.ServiceProvider import ServiceProvider


class BillDict(dict):
    """ Nested dict for holding Database.POPO.SimpleServiceBillDataBase.SimpleServiceBillDataBase instances

    Structure is: self[Database.POPO.RealEstate.Address][Database.POPO.ServiceProvider.ServiceProvider]
        [Start Date (datetime.date)][End Date (datetime.date)] = list[SimpleServiceBillDataBase]
    """
    def __init__(self):
        super().__init__()

    def insert_bills(self, bills):
        """ Insert SimpleServiceBillDataBase instance(s) to self nested dict

        Args:
            bills (Union[SimpleServiceBillDataBase, list[SimpleServiceBillDataBase], None]): subclass instance(s).
                bills are added to self nested dict by bill.real_estate.address, bill.provider, bill.start_date,
                bill.end_date. This function will not insert bills if it is None
        """
        bills = [] if bills is None else [bills] if isinstance(bills, SimpleServiceBillDataBase) else bills

        for bill in bills:
            self.setdefault(bill.real_estate.address, {}).setdefault(bill.provider, {})\
                .setdefault(bill.start_date, {}).setdefault(bill.end_date, []).append(bill)

    def get_bills(self, addresses=None, providers=None, start_dates=None, end_dates=None):
        """ Get SimpleServiceBillDataBase instances from self nested dict depending on parameters

        Args:
            addresses (Union[Address, list[Address], None]): address(es) of bill(s). Default None for all addresses
            providers (Union[ServiceProvider, list[ServiceProvider], None]): service provider(s) of bill(s).
                Default None for all service providers
            start_dates (Union[datetime.date, list[datetime.date], None]): start date(s) of bill(s).
                Default None for all start dates
            end_dates (Union[datetime.date, list[datetime.date], None]): end date(s) of bill(s).
                Default None for all end dates

        Returns:
            list[SimpleServiceBillDataBase]: list of subclass instances matching criteria. empty list if no matches
        """
        def keys_func(d_, params):
            return [] if d_ is None else list(d_.keys()) if params is None else params if isinstance(params, list) \
                else [params]

        ret_list = []
        for addr in keys_func(self, addresses):
            addr_dict = self.get(addr, None)
            for prov in keys_func(addr_dict, providers):
                prov_dict = addr_dict.get(prov, None)
                for sd in keys_func(prov_dict, start_dates):
                    sd_dict = prov_dict.get(sd, None)
                    for ed in keys_func(sd_dict, end_dates):
                        ret_list += sd_dict.get(ed, [])
        return ret_list


class SimpleServiceModelBase(ABC):
    """ Base model for simple service model classes

    Simple service models are associated with subclasses of SimpleServiceBillDataBase. Simple services are those where
    minimal data is required to be stored. Subclasses can override process_simple_service_bill(filename) function , or
    use the function as implemented in this class.

    Attributes:
        asb_dict (BillDict): actual service bills
    """
    @abstractmethod
    def __init__(self):
        """ init function """
        self.asb_dict = BillDict()

    @abstractmethod
    def process_service_bill(self, filename):
        """ Open, process and return service bill

        Returned instance of SimpleServiceBillDataBase subclass is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by subclass

        Returns:
            SimpleServiceBillDataBase: subclass with all required fields populated and as many non required fields as
            available populated

        Raises:
            FileNotFoundError: if file not found
        """
        raise NotImplementedError("process_service_bill() not implemented by subclass")

    @abstractmethod
    def insert_service_bills_to_db(self, bill_list):
        """ Insert service bills to table

        Args:
            bill_list (list[SimpleServiceBillDataBase]): list of subclass instances to insert

        Raises:
            MySQLException: if database insert issue occurs
        """
        raise NotImplementedError("insert_service_bill_to_db() not implemented by subclass")

    @abstractmethod
    def read_service_bill_from_db_by_repsd(self, real_estate, provider, start_date):
        """ Read service bills from table by real estate, provider, start date

        Returned instance(s) of SimpleServiceBillDataBase subclass, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[SimpleServiceBillDataBase]: list of subclass instances. empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_service_bill_from_db_by_start_date() not implemented by subclass")

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

    def read_real_estate_by_address(self, address):
        """ Read real estate from real_estate table by address

        Args:
            address (Address): address of the real estate to read data for

        Returns:
            Optional[RealEstate]: if a real estate record matches address, else None

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            re_list = mam.real_estate_read(wheres=[["address", "=", address]])

        return None if len(re_list) == 0 else re_list[0]

    def read_all_real_estate(self):
        """ Read all real estate records from real_estate table

        Returns:
            dict: int real estate id keys to real estate values. empty dict if table has no real estate records

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            re_list = mam.real_estate_read()

        return {re.id: re for re in re_list}