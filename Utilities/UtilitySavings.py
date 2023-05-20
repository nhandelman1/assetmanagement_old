import datetime
import pathlib
import Util.ExcelUtil as ExcelUtil
import pandas as pd
from Database.POPO.ElectricBillData import ElectricBillData
from Database.POPO.NatGasBillData import NatGasBillData
from Utilities.Electric.Model.PSEG import PSEG
from Utilities.NatGas.Model.NG import NG


class UtilitySavings:
    """ Calculate utility savings

    This applies to savings due to using solar but if other savings arise they will be added.

    Attributes:
        see init function docstring
    """
    def __init__(self, pseg_model, ng_model):
        """ init function

        Args:
            pseg_model (PSEG):
            ng_model (NG):
        """
        self.pseg_model = pseg_model
        self.ng_model = ng_model

        self.final_df = pd.DataFrame()

    def calc_savings(self):
        """ Run process to calculate savings across all utilities

        Initially, this is just for PSEG, NG and Solar but could be expanded to more utilities in the future
        self.final_df holds the final output dataframe with savings by month_year, total and ROI (return on investment)

        """
        pseg_df = self.pseg_model.read_all_monthly_bills_from_db()
        pseg_df = pseg_df[["start_date", "end_date", "is_actual", "total_kwh", "eh_kwh", "total_cost"]]
        pseg_df = pseg_df[pseg_df["is_actual"] == True].merge(pseg_df[pseg_df["is_actual"] == False],
                                      on=["start_date", "end_date"], how="left", suffixes=["_act", "_est"])
        pseg_df = pseg_df[~pseg_df["is_actual_est"].isnull()]
        pseg_df = pseg_df.drop(columns=["is_actual_act", "eh_kwh_act", "is_actual_est"])
        pseg_df["savings"] = pseg_df["total_cost_est"] - pseg_df["total_cost_act"]
        # there may be "savings" due to estimated total cost calculation inaccuracies, but true savings only
        # occur if total_kwh is different for act and est
        pseg_df = pseg_df[pseg_df["total_kwh_act"] != pseg_df["total_kwh_est"]]
        pseg_df.columns = pd.MultiIndex.from_product([["PSEG"], pseg_df.columns])
        pseg_df["month_year"] = pseg_df.apply(
            lambda row: ElectricBillData.calc_bill_month_year(row[("PSEG", "start_date")], row[("PSEG", "end_date")]),
            axis=1)

        ng_df = self.ng_model.read_all_monthly_bills_from_db()
        ng_df = ng_df[["start_date", "end_date", "is_actual", "total_therms", "saved_therms", "total_cost"]]
        ng_df = ng_df[ng_df["is_actual"] == True].merge(ng_df[ng_df["is_actual"] == False],
                                      on=["start_date", "end_date"], how="left", suffixes=["_act", "_est"])
        ng_df = ng_df[~ng_df["is_actual_est"].isnull()]
        ng_df = ng_df.drop(columns=["is_actual_act", "saved_therms_act", "is_actual_est"])
        ng_df["savings"] = ng_df["total_cost_est"] - ng_df["total_cost_act"]
        # there may be "savings" due to estimated total cost calculation inaccuracies, but true savings only
        # occur if total_kwh is different for act and est
        ng_df = ng_df[ng_df["total_therms_act"] != ng_df["total_therms_est"]]
        ng_df.columns = pd.MultiIndex.from_product([["NG"], ng_df.columns])
        ng_df["month_year"] = ng_df.apply(
            lambda row: NatGasBillData.calc_bill_month_year(row[("NG", "start_date")], row[("NG", "end_date")]), axis=1)

        f_df = pseg_df.merge(ng_df, on=["month_year"], how="outer")
        f_df[("Total", "savings")] = f_df[("PSEG", "savings")].fillna(0) + f_df[("NG", "savings")].fillna(0)
        f_df.insert(0, "month_year", f_df.pop("month_year"))
        flds = [("PSEG", "savings"), ("NG", "savings"), ("Total", "savings")]
        f_df.loc["Total", flds] = f_df[flds].sum()
        f_df.loc["ROI", ("month_year", "")] = 17402
        f_df.loc["ROI", flds] = (f_df.loc["Total", flds] / 17402 * 100).astype("float64").round(2)

        self.final_df = f_df

    def to_excel(self):
        """ Write self.final_df to excel file saved in Utilities -> Output directory

        Output file name has format: "Utility Savings as of (datetime this function is called).xlsx"
        """
        output_file = pathlib.Path(__file__).parent / ("Output/" +
                           ExcelUtil.clean_file_name("Utility Savings as of " + str(datetime.datetime.now()) + ".xlsx"))
        writer = pd.ExcelWriter(output_file, engine="openpyxl")
        self.final_df.to_excel(writer)
        ws = writer.book["Sheet1"]
        ExcelUtil.sheet_adj_col_width(ws)
        writer.close()