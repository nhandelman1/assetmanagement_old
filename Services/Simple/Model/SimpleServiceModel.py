import pathlib
import datetime
import pandas as pd
from typing import Union
from decimal import Decimal
from Database.MySQLAM import MySQLAM
from Database.POPO.ServiceProvider import ServiceProvider
from Database.POPO.RealEstate import Address
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData
from Services.Model.SimpleServiceModelBase import SimpleServiceModelBase


class SimpleServiceModel(SimpleServiceModelBase):
    """ Simplest implementation of SimpleServiceModelBase

    Designed to work with SimpleServiceBillData class

    Attributes:
        see superclass docstring
    """
    def __init__(self):
        """ init function """
        super().__init__()

    def process_service_bill(self, filename):
        """ Open, process and return simple service bill in same format as SimpleServiceBillTemplate.csv

        See directory Services/Simple/SimpleFiles for SimpleServiceBillTemplate.csv
            provider: valid values found in Database.POPO.ServiceProvider values
            address: valid values found in Database.POPO.RealEstate.Address values
            dates: YYYY-MM-DD format
            total cost: *.XX format
        Returned instance of SimpleServiceBillDataBase subclass is added to self.asb_dict

        Args:
            filename (str): name of file in Services/SimpleFiles directory

        Returns:
            SimpleServiceBillData: all attributes are set with bill values except id and paid_date. id is set to None
                and paid_date is set to the value provided in the bill or None if not provided

        Raises:
            ValueError: if address or service provider not found or value is not in correct format
        """
        df = pd.read_csv(pathlib.Path(__file__).parent.parent / ("SimpleFiles/" + filename))

        address = df.loc[0, "address"]
        real_estate = self.read_real_estate_by_address(Address.to_address(address))
        if real_estate is None:
            raise ValueError(str(address) + " not set in Address class")
        provider = ServiceProvider(df.loc[0, "provider"])
        start_date = datetime.datetime.strptime(df.loc[0, "start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(df.loc[0, "end_date"], "%Y-%m-%d").date()
        total_cost = Decimal(df.loc[0, "total_cost"])
        paid_date = df.loc[0, "paid_date"]
        paid_date = None if pd.isnull(paid_date) \
            else datetime.datetime.strptime(df.loc[0, "paid_date"], "%Y-%m-%d").date()
        notes = None if pd.isnull(df.loc[0, "notes"]) else df.loc[0, "notes"]
        ssbd = SimpleServiceBillData(real_estate, provider, start_date, end_date, total_cost, paid_date=paid_date,
                                     notes=notes)
        self.asb_dict.insert_bills(ssbd)

        return ssbd

    def insert_service_bills_to_db(self, bill_list):
        """ Insert simple service bills to simple_bill_data table

        Args:
            bill_list (list[SimpleServiceBillData]): simple bill data to insert

        Raises:
            ValueError: if the provider for any bill in bill_list does not have a simple bill
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.simple_bill_data_insert(bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, provider, start_date):
        """ read simple service bill from simple_bill_data table by real estate, provider, start date

        Returned instance(s) of SimpleServiceBillData, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[SimpleServiceBillData]: list of SimpleServiceBillData. empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.simple_bill_data_read(wheres=[["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)
        return bill_list

    def read_all_service_bills_from_db(self):
        with MySQLAM() as mam:
            bill_list = mam.simple_bill_data_read()

        df = pd.DataFrame()

        for bill in bill_list:
            df = pd.concat([df, bill.to_pd_df()], ignore_index=True)

        self.asb_dict.insert_bills(bill_list)

        return df.sort_values(by=["start_date"])