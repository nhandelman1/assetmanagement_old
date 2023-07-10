import decimal
import os
import pathlib
import datetime
import tabula
import pandas as pd
from decimal import Decimal
from Database.MySQLAM import MySQLAM
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Database.POPO.RealEstate import Address
from Database.POPO.MortgageBillData import MortgageBillData
from Services.Model.SimpleServiceModelBase import SimpleServiceModelBase


class MS(SimpleServiceModelBase):
    """ Morgan Stanley mortgage implementation of SimpleServiceModelBase

    Attributes:
        see superclass docstring
    """
    def __init__(self):
        """ init function """
        super().__init__()

    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.MS_MI]
        """
        return [ServiceProviderEnum.MS_MI]

    def process_service_bill(self, filename):
        """ Open, process and return Morgan Stanley mortgage bill

        Returned instance of MortgageBillData is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by FI_MORGANSTANLEY_DIR in .env

        Returns:
            MortgageBillData: with all required fields populated and as many non required fields as available populated
        """
        bill_data = MortgageBillData(None, None, None, None, None, None, None, None, None, None, None)

        df_list = tabula.read_pdf(pathlib.Path(__file__).parent.parent.parent.parent /
                                  (os.getenv("FI_MORGANSTANLEY_DIR") + filename), pages="all")

        df = df_list[0]
        df.loc[len(df)] = df.columns
        is_ver1 = len(df.columns) == 2
        for ind, row in df.iterrows():
            str1 = row[1]

            if isinstance(str1, str):
                str1_split = str1.split(" ")

                if "Statement Date:" in str1:
                    stmt_date = datetime.datetime.strptime(
                        str1_split[2] if is_ver1 else row[2], "%m/%d/%y").date()

                    # mortgage is a monthly payment so start date is the first day of the month (even if the statement
                    # date isn't the first day of the month)
                    bill_data.start_date = stmt_date
                    # sometimes the statement date is at the end of the previous month. make it a day in the next month
                    if bill_data.start_date.day >= 25:
                        bill_data.start_date += datetime.timedelta(days=7)
                    bill_data.start_date = bill_data.start_date.replace(day=1)

                    # default end date to last day of month of start date
                    bill_data.end_date = bill_data.start_date + datetime.timedelta(days=31)
                    bill_data.end_date = bill_data.end_date.replace(day=1) - datetime.timedelta(days=1)

                    bill_data.notes = ("" if bill_data.notes is None else bill_data.notes) + " statement date is " \
                                      + str(stmt_date)

        df = df_list[1]
        if len(df.columns) == 4:
            df[df.columns[1]] = df[df.columns[1]].fillna(df[df.columns[2]])
            df = df.drop(columns=[df.columns[2]])

        def fmt_dec(str_val):
            return Decimal(str_val.replace("$", "").replace(" ", "").replace(",", ""))

        address = ""
        found_address = False
        for ind, row in df.iterrows():
            str0 = row[0]
            str1 = row[1]
            str2 = row[2]

            if isinstance(str0, str):
                str0_split = str0.split(" ")

                if "Property Address" in str0:
                    address = " ".join(str0_split[2:])
                    found_address = True
                elif found_address:
                    # 2nd part of address is in the next row
                    address += (" " + str0)
                    found_address = False
                elif "Outstanding Principal" in str0:
                    bill_data.outs_prin = fmt_dec(str1)
                elif "Escrow Balance" in str0:
                    bill_data.esc_bal = fmt_dec(str1)
                    # stupid formatting so escrow payment is in str0
                    e_pos = str0.find("E")
                    if e_pos > 1:
                        bill_data.esc_pmt = fmt_dec(str0[:str0.find("E")])

            if isinstance(str2, str):
                str2_split = str2.split(" ")

                if "Principal" in str2:
                    bill_data.prin_pmt = fmt_dec(str2_split[1])
                elif "Interest" in str2:
                    bill_data.int_pmt = fmt_dec(str2_split[1])
                elif "Escrow" in str2:
                    try:
                        bill_data.esc_pmt = fmt_dec(str2_split[-1])
                    except decimal.InvalidOperation:
                        pass
                elif "Other" in str2 and len(str2_split) == 2:
                    bill_data.other_pmt = fmt_dec(str2_split[1])
                elif "Total Amount Due" in str2:
                    bill_data.total_cost = fmt_dec(str2_split[3])

        bill_data.real_estate = self.read_real_estate_by_address(Address.to_address(address))
        bill_data.service_provider = self.read_service_provider_by_enum(ServiceProviderEnum.MS_MI)
        self.asb_dict.insert_bills(bill_data)

        return bill_data

    def insert_service_bills_to_db(self, bill_list):
        """ Insert mortgage bills to mortgage_bill_data table

        Args:
            bill_list (list[MortgageBillData]): mortgage bill data to insert

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.mortgage_bill_data_insert(bill_list)

    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update service bills paid_date in mortgage_bill_data table by id

        Args:
            bill_list (list[MortgageBillData]): mortgage bill data to update

        Raises:
            MySQLException: if database update issue occurs
        """
        with MySQLAM() as mam:
            mam.mortgage_bill_data_update(["paid_date"], wheres=[["id", "=", None]], bill_list=bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ read mortgage bill from mortgage_bill_data table by real estate, service provider, start date

        Returned instance(s) of MortgageBillData, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[MortgageBillData]: list of MortgageBillData. empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.mortgage_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)
        return bill_list

    def read_all_service_bills_from_db(self):
        with MySQLAM() as mam:
            bill_list = mam.mortgage_bill_data_read()

        df = pd.DataFrame()

        for bill in bill_list:
            df = pd.concat([df, bill.to_pd_df()], ignore_index=True)

        self.asb_dict.insert_bills(bill_list)

        return df.sort_values(by=["start_date"])

    def read_all_service_bills_from_db_unpaid(self):
        with MySQLAM() as mam:
            bill_list = mam.mortgage_bill_data_read(wheres=[["paid_date", "is", None]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list