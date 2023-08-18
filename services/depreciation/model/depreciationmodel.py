import datetime
import os
import pandas as pd
import pathlib
from decimal import Decimal
from typing import Optional
from database.mysqlam import MySQLAM
from database.popo.depreciationbilldata import DepreciationBillData
from database.popo.realestate import Address, RealEstate
from database.popo.realpropertyvalues import RealPropertyValues
from database.popo.serviceprovider import ServiceProvider, ServiceProviderEnum
from services.depreciation.model.depreciationtaxation import DepreciationTaxation
from services.model.simpleservicemodelbase import SimpleServiceModelBase


class DepreciationModel(SimpleServiceModelBase):
    """ Depreciation implementation of SimpleServiceModelBase

    Attributes:
        see superclass docstring
    """
    def __init__(self):
        """ init function """
        super().__init__()

    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.DEP_DEP]
        """
        return [ServiceProviderEnum.DEP_DEP]

    def save_to_file(self, bill):
        """ Save depreciation bill to file with same format as DepreciationBillTemplate.csv

        File saved to .env FI_DEPRECIATION_DIR directory. Existing file will not be overwritten (see next note)
        Filename format: shortaddress_depreciationitem_purchasedate_startdate_enddate_*.csv
            * (int): if this file exists, replace star with next int in sequence until new file name is created

        Args:
            bill (DepreciationBillData): save this bill to file
        """
        def to_fn(ver):
            fn = bill.real_estate.address.short_name() + "_" + bill.real_property_values.item + "_" \
                 + str(bill.real_property_values.purchase_date) + "_" + str(bill.start_date) + "_" \
                 + str(bill.end_date) + "_" + str(ver) + ".csv"
            return fn, pathlib.Path(__file__).parent.parent.parent.parent / (os.getenv("FI_DEPRECIATION_DIR") + fn)

        filename, full_path = to_fn(1)
        while os.path.exists(full_path):
            filename, full_path = to_fn(int(filename.split("_")[-1][:-4]) + 1)

        df = bill.to_pd_df(rpv_prepend=True)
        df = df[["address", "provider", "item", "purchase_date", "start_date", "end_date", "period_usage_pct",
                 "total_cost", "tax_rel_cost", "paid_date", "notes"]]
        for col in ["address", "provider"]:
            df[col] = df[col].map(lambda x: str(x.value))

        df.to_csv(full_path, index=False)

        return filename

    def process_service_bill(self, filename):
        """ Open, process and return depreciation bill in same format as DepreciationBillTemplate.csv

        See directory specified by FI_DEPRECIATION_DIR in .env for DepreciationBillTemplate.csv
            address: valid values found in database.popo.realestate.Address values
            provider: see self.valid_providers() then database.popo.serviceprovider.ServiceProviderEnum for valid values
            item: an existing database.popo.realpropertyvalues.RealPropertyValues.item value
            dates: YYYY-MM-DD format
            period_usage_pct: 0.00 to 100.00 inclusive
            total cost: *.XX format
            tax related cost: *.XX format
        Returned instance of DepreciationBillData is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by FI_DEPRECIATION_DIR in .env

        Returns:
            DepreciationBillData: all attributes are set with bill values except id and paid_date. id is set to None
                and paid_date is set to the value provided in the bill or None if not provided

        Raises:
            ValueError: if address or service provider not found or value is not in correct format
        """
        df = pd.read_csv(pathlib.Path(__file__).parent.parent.parent.parent /
                         (os.getenv("FI_DEPRECIATION_DIR") + filename))

        address = df.loc[0, "address"]
        real_estate = self.read_real_estate_by_address(Address.to_address(address))
        if real_estate is None:
            raise ValueError(str(address) + " not set in Address class")
        provider = df.loc[0, "provider"]
        service_provider = self.read_service_provider_by_enum(ServiceProviderEnum(provider))
        if service_provider is None:
            raise ValueError(str(provider) + " not set in ServiceProviderEnum class")
        item = df.loc[0, "item"]
        purchase_date = datetime.datetime.strptime(df.loc[0, "purchase_date"], "%Y-%m-%d").date()
        # list will have 0 or 1 item
        real_property_values = self.read_real_property_value_by_reipd(real_estate, item, purchase_date)
        if len(real_property_values) == 0:
            raise ValueError("Depreciation item '" + str(item) + "' with purchase date " + str(purchase_date) +
                             " not found at real estate address: " + str(real_estate.address.value))
        real_property_values = real_property_values[0]
        start_date = datetime.datetime.strptime(df.loc[0, "start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(df.loc[0, "end_date"], "%Y-%m-%d").date()
        period_usage_pct = df.loc[0, "period_usage_pct"]
        total_cost = Decimal(df.loc[0, "total_cost"])
        tax_rel_cost = df.loc[0, "tax_rel_cost"]
        tax_rel_cost = total_cost if pd.isnull(tax_rel_cost) else Decimal(tax_rel_cost)
        paid_date = df.loc[0, "paid_date"]
        paid_date = None if pd.isnull(paid_date) \
            else datetime.datetime.strptime(df.loc[0, "paid_date"], "%Y-%m-%d").date()
        notes = None if pd.isnull(df.loc[0, "notes"]) else df.loc[0, "notes"]

        dbd = DepreciationBillData(real_estate, service_provider, real_property_values, start_date, end_date,
                                   period_usage_pct, total_cost, tax_rel_cost, paid_date=paid_date, notes=notes)
        self.asb_dict.insert_bills(dbd)

        return dbd

    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert depreciation bills to depreciation_bill_data table

        Args:
            bill_list (list[DepreciationBillData]): depreciation bill data to insert
            ignore (Optional[boolean]): see superclass docstring

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.depreciation_bill_data_insert(bill_list, ignore=ignore)

    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update service bills paid_date in depreciation_bill_data table by id

        Args:
            bill_list (list[DepreciationBillData]): depreciation bill data to update

        Raises:
            MySQLException: if database update issue occurs
        """
        with MySQLAM() as mam:
            mam.depreciation_bill_data_update(["paid_date"], wheres=[["id", "=", None]], bill_list=bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ read depreciation bill from depreciation_bill_data table by real estate, service provider, start date

        Returned instance(s) of DepreciationBillData, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[DepreciationBillData]: list of DepreciationBillData. empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.depreciation_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)
        return bill_list

    def read_all_service_bills_from_db_unpaid(self):
        with MySQLAM() as mam:
            bill_list = mam.depreciation_bill_data_read(wheres=[["paid_date", "is", None]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=False):
        wheres = self.resppdr_wheres_clause(real_estate_list=real_estate_list,
                service_provider_list=service_provider_list, paid_date_min=paid_date_min, paid_date_max=paid_date_max)

        with MySQLAM() as mam:
            bill_list = mam.depreciation_bill_data_read(wheres=wheres, order_bys=["paid_date"])

        return self.bills_post_read(bill_list, to_pd_df=to_pd_df, rpv_prepend=True)

    def read_one_bill(self):
        with MySQLAM() as mam:
            bill_list = mam.depreciation_bill_data_read(limit=1)

        if len(bill_list) == 0:
            raise ValueError("No depreciation bills found. Check that table has at least one record")

        return bill_list[0]

    def set_default_tax_related_cost(self, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            # depreciation is always a tax related cost so default tax related cost is always total cost. no need to
            # consider whether bills for the real estate in bill are typically tax related or not
            bill.tax_rel_cost = bill.total_cost if tax_related_cost.is_nan() else tax_related_cost
            bill_list.append(bill)
        return bill_list

    def read_real_property_value_by_reipd(self, real_estate, rpv_item, purchase_date):
        """ Read real property value from real_property_values table by real estate, item and purchase date

        Args:
            real_estate (RealEstate): real estate location of real property value
            rpv_item (str): real property value item
            purchase_date (datetime.date): purchase date of real property value item

        Returns:
            list[RealPropertyValues]: empty list if no real property values matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            rpv_list = mam.real_property_values_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["item", "=", rpv_item],
                        ["purchase_date", "=", purchase_date]])

        return rpv_list

    def read_real_property_values_by_repy(self, real_estate, purchase_year_lb=None, purchase_year_ub=None):
        """ Read real property values from real_property_values table by real estate and between purchase years

        Args:
            real_estate (RealEstate): real estate location of real property value
            purchase_year_lb (Optional[int]): real property values with purchase year greater than or equal to this.
                Default None for no lower bound on purchase year
            purchase_year_ub (Optional[int]): real property values with purchase year less than or equal to this.
                Default None for no upper bound on purchase year

        Returns:
            list[RealPropertyValues]: empty list if no real property values matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        wheres = [["real_estate_id", "=", real_estate.id]]
        if purchase_year_lb is not None:
            wheres.append(["purchase_date", ">=", datetime.date(purchase_year_lb, 1, 1)])
        if purchase_year_ub is not None:
            wheres.append(["purchase_date", "<=", datetime.date(purchase_year_ub, 12, 31)])
        with MySQLAM() as mam:
            rpv_list = mam.real_property_values_read(wheres=wheres)

        return rpv_list

    def create_bills(self, real_estate, service_provider, year):
        """ Create depreciation bills for the provided real_estate and year assuming full period business usage

        Find all real property values for real estate and year, and create depreciation bills where applicable assuming
        full period business usage. Not all real property values for real estate are depreciable for the given year.
        This function finds the depreciable items and creates depreciation bills for them. Non depreciable items are
        also returned (see Returns:). "full period" used here instead of "full year" to indicate that first and last
        years may be partial years. To apply period usage to each depreciation bill, see
        self.apply_period_usage_to_bills().

        Args:
            real_estate (RealEstate): real estate location of real property values
            service_provider (ServiceProvider): see self.valid_providers()
            year (int): year of purchase date

        Returns:
            (list[DepreciationBillData], list[RealPropertyValues]): (depreciable bill data, non depreciable items)
                1st element: depreciation bills assuming full period usage. empty list if no depreciable items found.
                2nd element: depreciation items that are never depreciable or have been fully depreciated. empty list
                    if no items found

        Raises:
            ValueError: if year is greater than or equal to the current year
        """
        if year >= datetime.date.today().year:
            raise ValueError(str(year) + " is not a previous year. Must be a previous year.")

        rpv_list = self.read_real_property_values_by_repy(real_estate, purchase_year_ub=year)
        bill_list = []
        nd_list = []
        dep_tax = DepreciationTaxation()
        for rpv in rpv_list:
            dep_for_year, remain_dep, max_dep_for_year = dep_tax.calculate_depreciation_for_year(rpv, year)

            if dep_for_year.is_zero():
                nd_list.append(rpv)
            else:
                notes = "Max depreciation possible for full period: " + str(max_dep_for_year) + "."
                if rpv.disposal_date is not None and rpv.disposal_date.year == year:
                    notes += " Partial year depreciation. Item disposed of " + str(rpv.disposal_date) + \
                             ". Full period less than a year."
                elif rpv.purchase_date.year == year:
                    notes += " Partial year depreciation. Item purchased " + str(rpv.purchase_date) + \
                             ". Full period less than a year."
                elif dep_for_year == remain_dep:
                    notes += " Partial year depreciation. Fully depreciated this year." \
                             " Full period probably less than a year."

                bill_list.append(DepreciationBillData(real_estate, service_provider, rpv, datetime.date(year, 1, 1),
                                                      datetime.date(year, 12, 31), Decimal(100), dep_for_year, None,
                                                      paid_date=datetime.date(year, 12, 31), notes=notes))

        bill_list = self.set_default_tax_related_cost([(bill, Decimal("NaN")) for bill in bill_list])

        return bill_list, nd_list

    def apply_period_usage_to_bills(self, bill_list):
        """ Apply period usage to bills in bill_list

        Call self.create_bills() to create bills before calling this function.
        bill.total_cost = bill.total_cost * bill.period_usage_pct / 100

        Args:
            bill_list (list[DepreciationBillData]):

        Returns:
            list[DepreciationBillData]: bill_list with period usage applied to total cost for each bill
        """
        for bill in bill_list:
            bill.total_cost *= (bill.period_usage_pct / 100)

        return bill_list