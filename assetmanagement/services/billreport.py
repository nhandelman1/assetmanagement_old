import calendar
import datetime
import os
import pathlib

import numpy as np
import pandas as pd

from .depreciation.model.depreciationmodel import DepreciationModel
from .depreciation.view.depreciationviewbase import DepreciationViewBase
from .electric.model.pseg import PSEG
from .electric.model.solar import Solar
from .electric.view.psegviewbase import PSEGViewBase
from .electric.view.solarviewbase import SolarViewBase
from .mortgage.model.ms import MS
from .mortgage.view.mortgageviewbase import MortgageViewBase
from .natgas.model.ng import NG
from .natgas.view.ngviewbase import NGViewBase
from .simple.model.simpleservicemodel import SimpleServiceModel
from .simple.view.simpleviewbase import SimpleViewBase
from assetmanagement.database.popo.realestate import RealEstate
import assetmanagement.util.excelutil as excelutil


class BillReport:
    """ Create Excel report of yearly bills

    The report has 4 sheets: Totals (total_sheet()), By Tax Category (tax_category_sheet()), By Paid Month
    (paid_date_month_sheet()) and By Provider (provider_sheet()). See to_excel() docstring for output file name format

    Attributes:
        see __init__ docstring
    """
    def __init__(self, simple_model, simple_view, mortgage_model, mortgage_view, solar_model, solar_view, pseg_model,
                 pseg_view, ng_model, ng_view, dep_model, dep_view):
        """ init function

        Args:
            simple_model (SimpleServiceModel):
            simple_view (SimpleViewBase):
            mortgage_model (MS):
            mortgage_view (MortgageViewBase):
            solar_model (Solar):
            solar_view (SolarViewBase): a subclass since base has no implemented functions
            pseg_model (PSEG):
            pseg_view (PSEGViewBase): a subclass since base has no implemented functions
            ng_model (NG):
            ng_view (NGViewBase): a subclass since base has no implemented functions
            dep_model (DepreciationModel):
            dep_view (DepreciationViewBase): a subclass since base has no implemented functions
        """
        self.simple_model = simple_model
        self.simple_view = simple_view
        self.mortgage_model = mortgage_model
        self.mortgage_view = mortgage_view
        self.solar_model = solar_model
        self.solar_view = solar_view
        self.pseg_model = pseg_model
        self.pseg_view = pseg_view
        self.ng_model = ng_model
        self.ng_view = ng_view
        self.dep_model = dep_model
        self.dep_view = dep_view

    def total_sheet(self, df):
        """ Create three dataframes of totals by tax category, month and provider

        Args:
            df (pd.DataFrame): must have columns "Paid Date", "Total Cost", "Tax Rel Cost", "Tax Category", "Provider"

        Returns:
            list[pd.DataFrame]: three dataframes. first column is "Tax Category Totals", "Month Totals",
                "Provider Totals", respectively. Columns 2-7 are "Total Income", "Total Expense", "Total Cost",
                "Tax Rel Income", "Tax Rel Expense", "Tax Rel Cost". Last row is "Total" with sum of each column
        """
        df = df.copy()
        df.insert(0, "Month", pd.to_datetime(df["Paid Date"]).dt.month)
        df["Total Income"] = df["Total Cost"].mask(df["Total Cost"].gt(0), np.nan).abs()
        df["Total Expense"] = df["Total Cost"].mask(df["Total Cost"].lt(0), np.nan)
        df["Tax Rel Income"] = df["Tax Rel Cost"].mask(df["Tax Rel Cost"].gt(0), np.nan).abs()
        df["Tax Rel Expense"] = df["Tax Rel Cost"].mask(df["Tax Rel Cost"].lt(0), np.nan)

        df_list = []
        for col in ["Tax Category", "Month", "Provider"]:
            df1 = df.groupby(by=col, as_index=False).agg(
                {"Total Income": "sum", "Total Expense": "sum", "Total Cost": "sum",
                 "Tax Rel Income": "sum", "Tax Rel Expense": "sum", "Tax Rel Cost": "sum"})
            df1.loc["Total"] = df1.sum()
            df1.loc["Total", col] = "Total"
            df_list.append(df1.rename(columns={col: col + " Totals"}))

        df_list[1]["Month Totals"] = df_list[1]["Month Totals"].map(
            lambda x: x if x == "Total" else calendar.month_name[int(x)])

        return df_list

    def tax_category_sheet(self, df):
        """ Create dataframe of bills ordered by Tax Category, Provider and Paid Date

        Args:
            df (pd.DataFrame): must have columns "Tax Category", "Provider", "Paid Date". other columns are optional

        Returns:
            pd.DataFrame: columns are in the same order as in df. Repeated values in sequential rows in the Tax Category
                and Provider columns are replaced with ""
        """
        df = df.copy()
        df = df.sort_values(by=["Tax Category", "Provider", "Paid Date"])

        df.loc[df["Tax Category"] == df["Tax Category"].shift(1), "Tax Category"] = ""
        df.loc[df["Provider"] == df["Provider"].shift(1), "Provider"] = ""

        return df

    def paid_date_month_sheet(self, df):
        """ Create dataframe of bills ordered by Month, Tax Category, Provider and Paid Date

        Args:
            df (pd.DataFrame): must have columns "Paid Date", "Tax Category", "Provider". "Month" column created in this
                function

        Returns:
            pd.DataFrame: columns are in the same order as in df with "Month" at column 0. Repeated values in sequential
                rows in the Month and Tax Category columns are replaced with ""
        """
        df = df.copy()
        df.insert(0, "Month", pd.to_datetime(df["Paid Date"]).dt.month)

        df = df.sort_values(by=["Month", "Tax Category", "Provider", "Paid Date"])
        df.loc[df["Month"] == df["Month"].shift(1), "Month"] = ""
        df["Month"] = df["Month"].map(lambda x: x if x == "" else calendar.month_name[int(x)])
        df.loc[df["Tax Category"] == df["Tax Category"].shift(1), "Tax Category"] = ""

        return df

    def provider_sheet(self, df):
        """ Create dataframe of bills ordered by Provider and Paid Date

        Args:
            df (pd.DataFrame): must have columns "Paid Date", "Tax Category", "Provider"

        Returns:
            pd.DataFrame: columns are in the same order as in df with "Provider" moved to column 0. Repeated values in
                sequential rows in the Provider and Tax Category columns are replaced with ""
        """
        df = df.copy().sort_values(by=["Provider", "Paid Date"])
        df.insert(0, "Provider", df.pop("Provider"))
        df.loc[df["Provider"] == df["Provider"].shift(1), ["Provider", "Tax Category"]] = ["", ""]

        return df

    def to_excel(self, real_estate, year, df_dict, index=False, delete_file=False):
        """ Write data to Excel file in specified sheets

        Output file name format: Yearly Bill Report for [real_estate.address.short_name()] - [year].xlsx

        Args:
            real_estate (RealEstate):
            year (int):
            df_dict (dict[str, list[pd.DataFrame]]): sheet name is key. list of dataframe of data is value. dataframes
                are written to sheet with an empty line between each dataframe
            index (boolean): True to write dataframe index to sheet. Default False to not.
            delete_file (boolean): True to delete output file if it exists. Default False to not.
        """
        output_file = "Yearly Bill Report for " + str(real_estate.address.short_name()) + " - " + str(year) + ".xlsx"
        output_file = pathlib.Path(__file__).parent.parent.parent / \
                      (os.getenv("DO_DIR") + excelutil.clean_file_name(output_file))

        if os.path.exists(output_file) and delete_file:
            os.remove(output_file)

        with pd.ExcelWriter(output_file) as writer:
            for sheet, df_list in df_dict.items():
                row = 0
                for df in df_list:
                    df.to_excel(writer, sheet_name=sheet, startrow=row, index=index)
                    row += (len(df) + 2)
                excelutil.sheet_adj_col_width(writer.book[sheet], right_count=4, comma_fmt=True, neg_fmt="-")

    def do_process(self):
        """ Run process to gather data and write to Excel file """
        re_dict = self.simple_model.read_all_real_estate()
        re_id = self.simple_view.input_select_real_estate(re_dict, pre_str="Create report for this real estate. ")
        real_estate = re_dict[re_id]
        year = self.simple_view.input_paid_year(pre_str="Create report for this year. ")

        flds = ["tax_category", "provider", "paid_date", "start_date", "end_date", "total_cost", "tax_rel_cost",
                "notes"]
        bill_df = pd.DataFrame()
        for model in [self.simple_model, self.mortgage_model, self.solar_model, self.pseg_model, self.ng_model,
                      self.dep_model]:
            df = model.read_service_bills_from_db_by_resppdr(
                real_estate_list=[real_estate], paid_date_min=datetime.date(year, 1, 1),
                paid_date_max=datetime.date(year, 12, 31), to_pd_df=True)
            bill_df = pd.concat([bill_df, df[flds]], ignore_index=True)

        bill_df = bill_df.rename(columns={col: col.replace("_", " ").title() for col in df.columns})
        bill_df = bill_df.astype({"Total Cost": "float64", "Tax Rel Cost": "float64"})
        for col in ["Tax Category", "Provider"]:
            bill_df[col] = bill_df[col].map(lambda x: x.value)

        tct_df, mt_df, pt_df = self.total_sheet(bill_df)
        tc_df = self.tax_category_sheet(bill_df)
        m_df = self.paid_date_month_sheet(bill_df)
        p_df = self.provider_sheet(bill_df)

        df_dict = {"Totals": [tct_df, mt_df, pt_df], "By Tax Category": [tc_df], "By Paid Month": [m_df],
                   "By Provider": [p_df]}
        self.to_excel(real_estate, year, df_dict, delete_file=True)