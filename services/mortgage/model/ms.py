import datetime
import os
import pandas as pd
import pathlib
import tabula
from decimal import Decimal
from database.mysqlam import MySQLAM
from database.popo.mortgagebilldata import MortgageBillData
from database.popo.realestate import Address
from database.popo.serviceprovider import ServiceProvider, ServiceProviderEnum
from services.model.simpleservicemodelbase import SimpleServiceModelBase


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
        bill_data = MortgageBillData.default_constructor()

        def fmt_dec(str_val):
            return Decimal(str_val.replace("$", "").replace(" ", "").replace(",", ""))

        df_list = tabula.read_pdf(pathlib.Path(__file__).parent.parent.parent.parent /
                                  (os.getenv("FI_MORGANSTANLEY_DIR") + filename), pages="all", guess=False, silent=True)

        df = df_list[0]
        address = ""
        found_address = False
        for ind, row in df.iterrows():
            str0 = "" if pd.isna(row[0]) else row[0]
            str1 = "" if pd.isna(row[1]) else row[1]
            str2 = "" if pd.isna(row[2]) else row[2]

            # bill start date and end date from statement date
            if any(["Statement Date:" in x for x in [str0, str1]]):
                stmt_date = datetime.datetime.strptime(str2, "%m/%d/%y").date()

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

                bill_data.notes = ("" if bill_data.notes is None else bill_data.notes) + " statement date is " + \
                                  str(stmt_date)

            # address
            if "Property Address" in str0:
                # relevant address words are either completely numeric or upper case
                for s in str0.split(" "):
                    if s.isnumeric() or s.isupper():
                        address += (" " + s)
                found_address = True
            elif found_address:
                # 2nd part of address is in the next row
                # relevant address words are either all numeric or all upper case with punctuation
                for s in str0.split(" "):
                    if any([x.islower() for x in s]):
                        continue
                    address += (" " + s)
                found_address = False

            # "Principal" comes in other rows. don't want to overwrite prin_pmt
            if any(["Principal" in x for x in [str0, str1]]) and bill_data.prin_pmt is None:
                bill_data.prin_pmt = fmt_dec(str2)
            # "Interest" is found in later rows
            if any(["Interest" in x for x in [str0, str1]]) and bill_data.int_pmt is None:
                bill_data.int_pmt = fmt_dec(str2)
            # not sure if "Outstanding Principal" appears in later rows but assuming it does
            if "Outstanding Principal" in str0 and bill_data.outs_prin is None:
                bill_data.outs_prin = fmt_dec(str0.split(" ")[2])
            if "Escrow Balance" in str0:
                if bill_data.esc_bal is None:
                    bill_data.esc_bal = fmt_dec(str0.split(" ")[2])
            elif "Escrow" in str0 and bill_data.esc_pmt is None:
                bill_data.esc_pmt = fmt_dec(str2)
            if "Escrow" in str1 and bill_data.esc_pmt is None:
                bill_data.esc_pmt = fmt_dec(str0[:str0.find(".")+2])
            # Other pmt comes immediately after escrow payment
            if any(["Other" in x for x in [str0, str1]]) and bill_data.esc_pmt is not None and \
                    bill_data.other_pmt is None:
                bill_data.other_pmt = fmt_dec(str2)
            if "Current Payment Due" in str0:
                bill_data.total_cost = fmt_dec(str1)
            elif "Current Payment Due" in str1:
                bill_data.total_cost = fmt_dec(str0[:str0.find(".") + 2])

        bill_data.real_estate = self.read_real_estate_by_address(Address.to_address(address.strip()))
        bill_data.service_provider = self.read_service_provider_by_enum(ServiceProviderEnum.MS_MI)
        self.asb_dict.insert_bills(bill_data)

        return bill_data

    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert mortgage bills to mortgage_bill_data table

        Args:
            bill_list (list[MortgageBillData]): mortgage bill data to insert
            ignore (Optional[boolean]): see superclass docstring

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.mortgage_bill_data_insert(bill_list, ignore=ignore)

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

    def read_all_service_bills_from_db_unpaid(self):
        with MySQLAM() as mam:
            bill_list = mam.mortgage_bill_data_read(wheres=[["paid_date", "is", None]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=False):
        wheres = self.resppdr_wheres_clause(real_estate_list=real_estate_list,
                service_provider_list=service_provider_list, paid_date_min=paid_date_min, paid_date_max=paid_date_max)

        with MySQLAM() as mam:
            bill_list = mam.mortgage_bill_data_read(wheres=wheres, order_bys=["paid_date"])

        return self.bills_post_read(bill_list, to_pd_df=to_pd_df)

    def read_one_bill(self):
        with MySQLAM() as mam:
            bill_list = mam.mortgage_bill_data_read(limit=1)

        if len(bill_list) == 0:
            raise ValueError("No mortgage bills found. Check that table has at least one record")

        return bill_list[0]

    def set_default_tax_related_cost(self, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            if tax_related_cost.is_nan():
                bill.tax_rel_cost = bill.int_pmt if bill.real_estate.bill_tax_related else Decimal(0)
            else:
                bill.tax_rel_cost = tax_related_cost
            bill_list.append(bill)
        return bill_list