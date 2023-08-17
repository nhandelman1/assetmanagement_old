import datetime
import decimal
import os
import pandas as pd
import pathlib
from decimal import Decimal
from Database.MySQLAM import FetchCursor, MySQLAM
from Database.POPO.RealEstate import Address
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Database.POPO.SolarBillData import SolarBillData
from Services.Model.SimpleServiceModelBase import SimpleServiceModelBase


class Solar(SimpleServiceModelBase):
    """ Perform data operations and calculations on Solar data """
    def __init__(self):
        """ init function """
        super().__init__()

    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.WL_10_SP]
        """
        return [ServiceProviderEnum.WL_10_SP]

    def process_service_bill_dates(self, filename):
        """ Open, process and return solar service bill dates in same format as SolarBillTemplate.csv

        See directory specified by FI_SUNPOWER_DIR in .env for SolarBillTemplate.csv
            dates: YYYY-MM-DD format

        Args:
            filename (str): name of file in directory specified by FI_SUNPOWER_DIR in .env

        Returns:
            (datetime.date, datetime.date, pd.DataFrame): three tuple of start date, end date, bill dataframe

        Raises:
            ValueError: if required dates not found or have incorrect values or format
        """
        df = pd.read_csv(pathlib.Path(__file__).parent.parent.parent.parent /
                         (os.getenv("FI_SUNPOWER_DIR") + filename))
        start_date = datetime.datetime.strptime(df.loc[0, "start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(df.loc[0, "end_date"], "%Y-%m-%d").date()

        return start_date, end_date, df

    def process_service_bill(self, filename):
        """ Open, process and return solar service bill in same format as SolarBillTemplate.csv

        Solar hourly data must be available before calling this function. See self.process_sunpower_hourly_file() and
            self.insert_sunpower_hourly_data_to_db(). This function calls self.calculate_total_kwh_between_dates() to
            get solar and home kwh usage the billing period.
        This function will not work for the first bill since the beginning of the month opportunity cost basis isn't
            set. Should insert first bill directly in table.
        See directory specified by FI_SUNPOWER_DIR in .env for SolarBillTemplate.csv
            address: valid values found in Database.POPO.RealEstate.Address values
            provider: see self.valid_providers() then Database.POPO.ServiceProvider.ServiceProviderEnum for valid values
            dates: YYYY-MM-DD format. start_date and end_date should match the start_date and end_date of an electric
                bill or there will be issues later
            actual costs: *.XX dollar format
            oc_pnl_pct: *.XX percent format
        Returned instance of SolarBillData is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by FI_SUNPOWER_DIR in .env

        Returns:
            SolarBillData: all attributes are set with bill values except id and paid_date. id is set to None
                and paid_date is set to the value provided in the bill or None if not provided

        Raises:
            ValueError: if required data not found or has incorrect values or format, if solar hourly data not available
        """
        start_date, end_date, df = self.process_service_bill_dates(filename)

        address = df.loc[0, "address"]
        real_estate = self.read_real_estate_by_address(Address.to_address(address))
        if real_estate is None:
            raise ValueError(str(address) + " not set in Address class")
        provider = df.loc[0, "provider"]
        service_provider = self.read_service_provider_by_enum(ServiceProviderEnum(provider))
        if service_provider is None:
            raise ValueError(str(provider) + " not set in ServiceProviderEnum class")
        kwh_dict = self.calculate_total_kwh_between_dates(start_date, end_date)
        prev_bill_end_date = start_date - datetime.timedelta(days=1)
        prev_bill = self.read_service_bill_from_db_by_reped(real_estate, service_provider, prev_bill_end_date)
        if len(prev_bill) == 0:
            raise ValueError("No previous bill with the following parameters: " + str(real_estate.address.value) + ", "
                             + str(service_provider.provider.value) + ", end_date: " + str(prev_bill_end_date)
                             + ". First bill needs to be set directly in table")
        actual_costs = Decimal(df.loc[0, "actual_costs"])
        oc_pnl_pct = Decimal(df.loc[0, "oc_pnl_pct"])
        paid_date = df.loc[0, "paid_date"]
        paid_date = None if pd.isnull(paid_date) \
            else datetime.datetime.strptime(df.loc[0, "paid_date"], "%Y-%m-%d").date()
        notes = None if pd.isnull(df.loc[0, "notes"]) else df.loc[0, "notes"]

        sbd = SolarBillData(real_estate, service_provider, start_date, end_date, kwh_dict["solar_kwh"],
                            kwh_dict["home_kwh"], None, None, actual_costs, prev_bill[0].oc_eom_basis, oc_pnl_pct,
                            None, None, paid_date=paid_date, notes=notes)
        sbd.calc_variables()
        sbd = self.set_default_tax_related_cost([(sbd, Decimal("NaN"))])[0]

        self.asb_dict.insert_bills(sbd)

        return sbd

    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert solar service bills to solar_bill_data table

        Args:
            bill_list (list[SolarBillData]): solar bill data to insert
            ignore (Optional[boolean]): see superclass docstring

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.solar_bill_data_insert(bill_list, ignore=ignore)

    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update solar bills paid_date in solar_bill_data table by id

        Args:
            bill_list (list[SolarBillData]): solar bill data to update

        Raises:
            MySQLException: if database update issue occurs
        """
        with MySQLAM() as mam:
            mam.solar_bill_data_update(["paid_date"], wheres=[["id", "=", None]], bill_list=bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ Read service bills from table by real estate, service provider, start date

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[SolarBillData]: empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.solar_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)
        return bill_list

    def read_service_bill_from_db_by_reped(self, real_estate, service_provider, end_date):
        """ Read service bills from table by real estate, service provider, end date

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            end_date (datetime.date): end date of bill

        Returns:
            list[SolarBillData]: empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.solar_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["end_date", "=", end_date]])

        return bill_list

    def read_all_service_bills_from_db_unpaid(self):
        with MySQLAM() as mam:
            bill_list = mam.solar_bill_data_read(wheres=[["paid_date", "is", None]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=False):
        wheres = self.resppdr_wheres_clause(real_estate_list=real_estate_list,
                service_provider_list=service_provider_list, paid_date_min=paid_date_min, paid_date_max=paid_date_max)

        with MySQLAM() as mam:
            bill_list = mam.solar_bill_data_read(wheres=wheres, order_bys=["paid_date"])

        return self.bills_post_read(bill_list, to_pd_df=to_pd_df)

    def read_one_bill(self):
        with MySQLAM() as mam:
            bill_list = mam.solar_bill_data_read(limit=1)

        if len(bill_list) == 0:
            raise ValueError("No solar bills found. Check that table has at least one record")

        return bill_list[0]

    def set_default_tax_related_cost(self, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            # solar "bills" aren't real bills so default tax related cost is always 0. no need to consider whether bills
            # for the real estate in bill are typically tax related or not
            bill.tax_rel_cost = Decimal(0) if tax_related_cost.is_nan() else tax_related_cost
            bill_list.append(bill)
        return bill_list

    def process_sunpower_hourly_file(self, filename):
        """ Open, process and return mySunpower hourly file

        Args:
            filename (str): name of file in SunpowerFiles directory

        Returns:
            pd.DataFrame: with columns dt (datetime64), solar_kwh (float64) and home_kwh (float64)

        Raises:
            ValueError: if a date does not have 24 entries (1 per hour)
        """
        df = pd.read_excel(pathlib.Path(__file__).parent.parent.parent.parent /
                           (os.getenv("FI_SUNPOWER_DIR") + filename))
        df = df.rename(columns={"Period": "dt", "Solar Production (kWh)": "solar_kwh", "Home Usage (kWh)": "home_kwh"})
        df["dt"] = df["dt"].str.split(" ").map(lambda x: x[1] + " " + x[3])
        df["dt"] = pd.to_datetime(df["dt"], format="%m/%d/%Y %I:%M%p")
        df["date"] = df["dt"].dt.date

        v_df = df.groupby(by=["date"], as_index=False).agg({"dt": "count"})
        v_df = v_df[v_df["dt"] != 24]
        if len(v_df) > 0:
            msg = "mySunpower file has issues: "
            for ind, row in v_df.iterrows():
                msg += str(row["date"]) + " has " + str(row["dt"]) + " entries. "
            raise ValueError(msg)

        return df[["dt", "solar_kwh", "home_kwh"]]

    def insert_sunpower_hourly_data_to_db(self, data_df):
        """ write sunpower hourly data to table

        Should be called with pd.DataFrame return from process_sunpower_hourly_file()

        Args:
            data_df (pd.DataFrame): must have columns dt, solar_kwh, home_kwh

        Raises:
            MySQLException: if issue with database insert (probably primary key violation)
        """
        with MySQLAM() as mam:
            mam.mysunpower_hourly_data_insert(data_df.to_dict(orient="records"))

    def read_sunpower_hourly_data_from_db_between_dates(self, start_date, end_date, must_have_all_data=False):
        """ Read sunpower hourly data from mysunpower_hourly_data table

        This function checks that there is no missing data between the dates.

        Args:
            start_date (datetime.date): read data starting on this date (inclusive)
            end_date (datetime.date): read data ending on this date (inclusive)
            must_have_all_data (boolean): True for this function to check that there is no missing data between the
                dates. Default False for no checks

        Returns:
            pd.DataFrame: of hourly data with keys matching table columns

        Raises:
            ValueError: if any hourly data is missing and must_have_all_data is True
        """
        end_date = datetime.datetime.combine(end_date, datetime.time(23, 59, 59))
        with MySQLAM(FetchCursor.PD_DF) as mam:
            data_df = mam.mysunpower_hourly_data_read(wheres=[["dt", ">=", start_date], ["dt", "<=", end_date]])

        if must_have_all_data:
            end_date = end_date.date()
            days = (end_date - start_date).days + 1
            exp_records = days * 24
            act_records = len(data_df)

            if exp_records != act_records:
                raise ValueError("Missing hourly data: " + str(start_date) + " - " + str(end_date) + " has " + str(days)
                                 + " days and should have " + str(exp_records) + " hourly records but only has "
                                 + str(act_records) + " records.")

        return data_df

    def calculate_total_kwh_between_dates(self, start_date, end_date):
        """ Calculate total kwh generation and usage over period that must have all requested hourly data available

        Args:
            start_date (datetime.date): calculate total starting on this date (inclusive)
            end_date (datetime.date): calculate total  ending on this date (inclusive)

        Returns:
            dict: {solar_kwh: total solar kwh generated Decimal, home_kwh: total home kwh usage Decimal}

        Raises:
            ValueError: see self.read_sunpower_hourly_data_from_db_between_dates()
        """
        data_df = self.read_sunpower_hourly_data_from_db_between_dates(start_date, end_date, must_have_all_data=True)
        kwh_dict = {"solar_kwh": decimal.Decimal(data_df["solar_kwh"].sum()),
                    "home_kwh": decimal.Decimal(data_df["home_kwh"].sum())}

        return kwh_dict