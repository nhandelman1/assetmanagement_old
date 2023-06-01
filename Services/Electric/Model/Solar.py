import datetime
import decimal
import pathlib
import pandas as pd
from decimal import Decimal
from Database.MySQLAM import MySQLAM, FetchCursor


class Solar:
    """ Model class for Solar related data

    Attributes:
        kwh_dict (dict): {"solar_kwh": Decimal, "home_kwh": Decimal}
    """
    def __init__(self):
        """ init function """
        self.kwh_dict = {}

    def process_sunpower_hourly_file(self, filename):
        """ Open, process and return mySunpower hourly file

        Args:
            filename (str): name of file in MySunpowerFiles directory

        Returns:
            pd.DataFrame: with columns dt (datetime64), solar_kwh (float64) and home_kwh (float64)

        Raises:
            ValueError: if a date does not have 24 entries (1 per hour)
        """
        df = pd.read_excel(pathlib.Path(__file__).parent.parent / ("MySunpowerFiles/" + filename))
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

    def read_sunpower_hourly_data_from_db_between_dates(self, start_date, end_date):
        """ Read sunpower hourly data from mysunpower_hourly_data table

        Args:
            start_date (datetime.date): read data starting on this date (inclusive)
            end_date (datetime.date): read data ending on this date (inclusive)

        Returns:
            pd.DataFrame: of hourly data with keys matching table columns
        """
        end_date = datetime.datetime.combine(end_date, datetime.time(23, 59, 59))
        with MySQLAM(FetchCursor.PD_DF) as mam:
            data_df = mam.mysunpower_hourly_data_read(wheres=[["dt", ">=", start_date], ["dt", "<=", end_date]])

        return data_df

    def calculate_total_kwh_between_dates(self, start_date, end_date):
        """ Calculate total kwh generation and usage over period

        self.kwh_dict set and returned

        Args:
            start_date (datetime.date): calculate total starting on this date (inclusive)
            end_date (datetime.date): calculate total  ending on this date (inclusive)

        Returns:
            dict: {solar_kwh: total solar kwh generated Decimal, home_kwh: total home kwh usage Decimal}
        """
        data_df = self.read_sunpower_hourly_data_from_db_between_dates(start_date, end_date)
        self.kwh_dict = {"solar_kwh": decimal.Decimal(data_df["solar_kwh"].sum()),
                         "home_kwh": decimal.Decimal(data_df["home_kwh"].sum())}

        return self.kwh_dict
