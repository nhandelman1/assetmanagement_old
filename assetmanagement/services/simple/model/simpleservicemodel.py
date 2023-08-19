from decimal import Decimal
import datetime
import os
import pathlib

import pandas as pd

from ...model.simpleservicemodelbase import SimpleServiceModelBase
from assetmanagement.database.mysqlam import MySQLAM
from assetmanagement.database.popo.realestate import Address
from assetmanagement.database.popo.serviceprovider import ServiceProviderEnum
from assetmanagement.database.popo.simpleservicebilldata import SimpleServiceBillData


class SimpleServiceModel(SimpleServiceModelBase):
    """ Simplest implementation of SimpleServiceModelBase

    Designed to work with SimpleServiceBillData class

    Attributes:
        see superclass docstring
    """
    def __init__(self):
        """ init function """
        super().__init__()

    def valid_providers(self):
        """ Which service providers are valid for this model

        SPE = ServiceProviderEnum
        Returns:
            list[ServiceProviderEnum]: [SPE.BCPH_REP, SPE.HD_SUP, SPE.HOAT_REP, SPE.KPC_CM, SPE.MS_MI, SPE.NB_INS,
                SPE.OH_INS, SPE.OC_UTI, SPE.OI_UTI, SPE.SCWA_UTI, SPE.SC_TAX, SPE.WMT_SUP, SPE.WL_10_APT_TEN_INC,
                SPE.WP_REP,  SPE.VI_UTI, SPE.YTV_UTI]
        """
        SPE = ServiceProviderEnum
        return [SPE.BCPH_REP, SPE.HD_SUP, SPE.HOAT_REP, SPE.KPC_CM, SPE.NB_INS, SPE.OH_INS, SPE.OC_UTI, SPE.OI_UTI,
                SPE.SCWA_UTI, SPE.SC_TAX, SPE.WMT_SUP, SPE.WL_10_APT_TEN_INC, SPE.WP_REP, SPE.VI_UTI, SPE.YTV_UTI]

    def save_to_file(self, bill):
        """ Save simple bill to file with same format as SimpleServiceBillTemplate.csv

        File saved to .env FI_SIMPLE_DIR directory. Existing file will not be overwritten (see next note)
        Filename format: shortaddress_providername_startdate_enddate_*.csv
            * (int): if this file exists, replace star with next int in sequence until new file name is created

        Args:
            bill (SimpleServiceBillData): save this bill to file
        """
        def to_fn(ver):
            fn = bill.real_estate.address.short_name() + "_" + str(bill.service_provider.provider.value) + "_" \
                   + str(bill.start_date) + "_" + str(bill.end_date) + "_" + str(ver) + ".csv"
            return fn, pathlib.Path(__file__).parent.parent.parent.parent.parent / (os.getenv("FI_SIMPLE_DIR") + fn)

        filename, full_path = to_fn(1)
        while os.path.exists(full_path):
            filename, full_path = to_fn(int(filename.split("_")[-1][:-4]) + 1)

        df = bill.to_pd_df()
        df = df[["address", "provider", "start_date", "end_date", "total_cost", "tax_rel_cost", "paid_date", "notes"]]
        for col in ["address", "provider"]:
            df[col] = df[col].map(lambda x: str(x.value))
        if df.loc[0, "tax_rel_cost"] == 0:
            # conform to required format *.XX
            df.loc[0, "tax_rel_cost"] = "0.00"

        df.to_csv(full_path, index=False)

        return filename

    def process_service_bill(self, filename):
        """ Open, process and return simple service bill in same format as SimpleServiceBillTemplate.csv

        See directory specified by FI_SIMPLE_DIR in .env for SimpleServiceBillTemplate.csv
            address: valid values found in database.popo.realestate.Address values
            provider: see self.valid_providers() then database.popo.serviceprovider.ServiceProviderEnum for valid values
            dates: YYYY-MM-DD format
            total cost: *.XX format
            tax related cost: *.XX format
        Returned instance of SimpleServiceBillData is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by FI_SIMPLE_DIR in .env

        Returns:
            SimpleServiceBillData: all attributes are set with bill values except id and paid_date. id is set to None
                and paid_date is set to the value provided in the bill or None if not provided

        Raises:
            ValueError: if address or service provider not found or value is not in correct format
        """
        df = pd.read_csv(pathlib.Path(__file__).parent.parent.parent.parent.parent /
                         (os.getenv("FI_SIMPLE_DIR") + filename))

        address = df.loc[0, "address"]
        real_estate = self.read_real_estate_by_address(Address.to_address(address))
        if real_estate is None:
            raise ValueError(str(address) + " not set in Address class")
        provider = df.loc[0, "provider"]
        service_provider = self.read_service_provider_by_enum(ServiceProviderEnum(provider))
        if service_provider is None:
            raise ValueError(str(provider) + " not set in ServiceProviderEnum class")
        start_date = datetime.datetime.strptime(df.loc[0, "start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(df.loc[0, "end_date"], "%Y-%m-%d").date()
        total_cost = Decimal(df.loc[0, "total_cost"])
        try:
            tax_rel_cost = df.loc[0, "tax_rel_cost"]
            tax_rel_cost = total_cost if pd.isnull(tax_rel_cost) else Decimal(tax_rel_cost)
        except KeyError:
            tax_rel_cost = total_cost
        paid_date = df.loc[0, "paid_date"]
        paid_date = None if pd.isnull(paid_date) \
            else datetime.datetime.strptime(df.loc[0, "paid_date"], "%Y-%m-%d").date()
        notes = None if pd.isnull(df.loc[0, "notes"]) else df.loc[0, "notes"]
        ssbd = SimpleServiceBillData(real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost,
                                     paid_date=paid_date, notes=notes)
        self.asb_dict.insert_bills(ssbd)

        return ssbd

    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert simple service bills to simple_bill_data table

        Args:
            bill_list (list[SimpleServiceBillData]): simple bill data to insert
            ignore (Optional[boolean]): see superclass docstring

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.simple_bill_data_insert(bill_list, ignore=ignore)

    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update service bills paid_date in simple_bill_data table by id

        Args:
            bill_list (list[SimpleServiceBillData]): simple bill data to update

        Raises:
            MySQLException: if database update issue occurs
        """
        with MySQLAM() as mam:
            mam.simple_bill_data_update(["paid_date"], wheres=[["id", "=", None]], bill_list=bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ read simple service bill from simple_bill_data table by real estate, service provider, start date

        Returned instance(s) of SimpleServiceBillData, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[SimpleServiceBillData]: list of SimpleServiceBillData. empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.simple_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)
        return bill_list

    def read_all_service_bills_from_db_unpaid(self):
        with MySQLAM() as mam:
            bill_list = mam.simple_bill_data_read(wheres=[["paid_date", "is", None]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=False):
        wheres = self.resppdr_wheres_clause(real_estate_list=real_estate_list,
                service_provider_list=service_provider_list, paid_date_min=paid_date_min, paid_date_max=paid_date_max)

        with MySQLAM() as mam:
            bill_list = mam.simple_bill_data_read(wheres=wheres, order_bys=["paid_date"])

        return self.bills_post_read(bill_list, to_pd_df=to_pd_df)

    def read_one_bill(self):
        with MySQLAM() as mam:
            bill_list = mam.simple_bill_data_read(limit=1)

        if len(bill_list) == 0:
            raise ValueError("No simple bills found. Check that table has at least one record")

        return bill_list[0]

    def set_default_tax_related_cost(self, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            if tax_related_cost.is_nan():
                bill.tax_rel_cost = bill.total_cost if bill.real_estate.bill_tax_related else Decimal(0)
            else:
                bill.tax_rel_cost = tax_related_cost
            bill_list.append(bill)
        return bill_list