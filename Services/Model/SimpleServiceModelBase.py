import datetime
import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Union
from Database.MySQLAM import MySQLAM
from Database.POPO.RealEstate import Address, RealEstate
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Database.POPO.SimpleServiceBillDataBase import SimpleServiceBillDataBase


class BillDict(dict):
    """ Nested dict for holding Database.POPO.SimpleServiceBillDataBase.SimpleServiceBillDataBase instances

    Structure is: self[Database.POPO.RealEstate.Address][Database.POPO.ServiceProvider.ServiceProviderEnum]
        [Start Date (datetime.date)][End Date (datetime.date)] = list[SimpleServiceBillDataBase]
    """
    def __init__(self):
        super().__init__()

    def insert_bills(self, bills):
        """ Insert SimpleServiceBillDataBase instance(s) to self nested dict

        Args:
            bills (Union[SimpleServiceBillDataBase, list[SimpleServiceBillDataBase], None]): subclass instance(s).
                bills are added to self nested dict by bill.real_estate.address, bill.service_provider.provider,
                bill.start_date, bill.end_date. This function will not insert bills if it is None
        """
        bills = [] if bills is None else [bills] if isinstance(bills, SimpleServiceBillDataBase) else bills

        for bill in bills:
            self.setdefault(bill.real_estate.address, {}).setdefault(bill.service_provider.provider, {})\
                .setdefault(bill.start_date, {}).setdefault(bill.end_date, []).append(bill)

    def get_bills(self, addresses=None, providers=None, start_dates=None, end_dates=None):
        """ Get SimpleServiceBillDataBase instances from self nested dict depending on parameters

        Args:
            addresses (Union[Address, list[Address], None]): address(es) of bill(s). Default None for all addresses
            providers (Union[ServiceProviderEnum, list[ServiceProviderEnum], None]):
                service provider(s) of bill(s). Default None for all service providers
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
    minimal data is required to be stored. Subclasses can override process_simple_service_bill(filename) function, or
    use the function as implemented in this class.

    Attributes:
        asb_dict (BillDict): actual service bills
    """
    @abstractmethod
    def __init__(self):
        """ init function """
        self.asb_dict = BillDict()

    @abstractmethod
    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: list of ServiceProviderEnum
        """
        raise NotImplementedError("valid_providers() not implemented by subclass")

    def clear_model(self):
        """ Call clear() on attribute dict(s) """
        self.asb_dict.clear()

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
    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert service bills to table

        Args:
            bill_list (list[SimpleServiceBillDataBase]): list of subclass instances to insert
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if database insert issue occurs
        """
        raise NotImplementedError("insert_service_bill_to_db() not implemented by subclass")

    @abstractmethod
    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update service bills paid_date in table by id

        Args:
            bill_list (list[SimpleServiceBillDataBase]): list of subclass instances to update

        Raises:
            MySQLException: if database update issue occurs
        """
        raise NotImplementedError("update_service_bills_in_db_paid_date_by_id() not implemented by subclass")

    @abstractmethod
    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ Read service bills from table by real estate, service provider, start date

        Returned instance(s) of SimpleServiceBillDataBase subclass, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[SimpleServiceBillDataBase]: list of subclass instances. empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_service_bill_from_db_by_start_date() not implemented by subclass")

    @abstractmethod
    def read_all_service_bills_from_db_unpaid(self):
        """ Read all service bills that have a null paid date

        Service bills are inserted in self.asb_dict

        Returns:
            list[SimpleServiceBillDataBase]: list of subclass instances. empty list if no bill with null paid date

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_all_unpaid_service_bills_from_db() not implemented by subclass")

    @abstractmethod
    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=None):
        """ Read service bills from table by real estate(s), service provider(s), paid date range inclusive

        Service bills are inserted in self.asb_dict
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
            Union[list[SimpleServiceBillDataBase], pd.DataFrame]:
                list: subclass instances. empty if no bills matching parameters. ordered by paid date increasing
                dataframe: with all bill data ordered by start date decreasing. empty dataframe will have column headers

        Raises:
            MySQLException: if issue with database read
        """
        raise NotImplementedError("read_service_bills_from_db_by_resppdr() not implemented by subclass")

    @abstractmethod
    def read_one_bill(self):
        """ Read one bill from database table specified by subclass

        Returns:
            SimpleServiceBillDataBase: subclass instance. the one bill read from table

        Raises:
            ValueError: if table is empty
        """
        raise NotImplementedError("read_one_bill() not implemented by subclass")

    @abstractmethod
    def set_default_tax_related_cost(self, bill_tax_related_cost_list):
        """ Set tax_rel_cost in each bill with the provided tax related cost or use default value

        Overriding functions should do the following:
            If a number Decimal is provided, set the bill's tax_rel_cost to that value.
            If Decimal(NaN) is provided, set the bill's tax_rel_cost depending on the bill's
                real_estate.bill_tax_related value

        Args:
            bill_tax_related_cost_list (list[tuple[SimpleServiceBillDataBase, Decimal]]): sub tuples are 2-tuples where
                the first element is the bill and the second element is the tax related cost of the bill or Decimal(NaN)
                to use default tax related cost.

        Returns:
            list[SimpleServiceBillDataBase]: subclass instances. tax_rel_cost in each bill is set as described. bills
                are returned in same order as in bill_tax_related_cost_list
        """
        raise NotImplementedError("set_default_tax_related_cost() not implemented by subclass")

    @staticmethod
    def resppdr_wheres_clause(real_estate_list=(), service_provider_list=(), paid_date_min=None,
                              paid_date_max=None):
        """ Create where clause for self.read_service_bills_from_db_by_resppdr() function

        See SimpleServiceModelBase.read_service_bills_from_db_by_resppdr(). The Args are common to all
        SimpleServiceBillDataBase subclasses so no need to reimplement in each subclass of this class.

        Args:
            real_estate_list (list[RealEstate]): real estate location(s) of bills. Default () for all locations
            service_provider_list (list[ServiceProvider]): service provider(s) of bills. Default () for all providers
            paid_date_min (Optional[datetime.date]): bills with paid date greater than or equal to this date. Default
                None for no minimum
            paid_date_max (Optional[datetime.date]): bills with paid date less than or equal to this date. Default None
                for no maximum

        Returns:
            list[list]: where clause with up to 4 sub lists with 3 elements each
        """
        wheres = []
        if len(real_estate_list) > 0:
            wheres.append(["real_estate_id", "in", [x.id for x in real_estate_list]])
        if len(service_provider_list) > 0:
            wheres.append(["service_provider_id", "in", [x.id for x in service_provider_list]])
        if paid_date_min is not None:
            wheres.append(["paid_date", ">=", paid_date_min])
        if paid_date_max is not None:
            wheres.append(["paid_date", "<=", paid_date_max])

        return wheres

    def bills_post_read(self, bill_list, to_pd_df=False, **kwargs):
        """ Convenience function to save bill_list to model and convert bill_list to dataframe if specified

        Args:
            bill_list (list[SimpleServiceBillDataBase]): subclass instances
            to_pd_df (boolean): True to return data as a dataframe with column headers (even if bill_list is empty).
                Default False to return bill_list unaltered
            kwargs: see SimpleServiceBillDataBase.to_pd_df(kwargs) (and subclasses)

        Returns:
            Union[list[SimpleServiceBillDataBase], pd.DataFrame]:
                list: bill_list unaltered
                dataframe: with all bill data ordered by start date decreasing
        """
        self.asb_dict.insert_bills(bill_list)

        if to_pd_df:
            if len(bill_list) == 0:
                df = self.read_one_bill().to_pd_df(**kwargs).head(0)
            else:
                df = pd.DataFrame()
                for bill in bill_list:
                    df = pd.concat([df, bill.to_pd_df(**kwargs)], ignore_index=True)

                df = df.sort_values(by=["start_date"])

            return df
        else:
            return bill_list

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

    def read_valid_service_providers(self):
        """ Read all valid service providers for this model from service_providers table

        Returns:
            dict: int service provider id keys to service provider values. empty dict if table has no records

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            sp_list = mam.service_provider_read(wheres=[["provider", "in", self.valid_providers()]])

        return {sp.id: sp for sp in sp_list}

    def read_service_provider_by_enum(self, provider):
        """ Read service provider from service_provider table by provider

        Args:
            provider (ServiceProviderEnum): provider name of service provider

        Returns:
            Optional[ServiceProvider]: if a service provider record matches provider, else None

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            re_list = mam.service_provider_read(wheres=[["provider", "=", provider]])

        return None if len(re_list) == 0 else re_list[0]