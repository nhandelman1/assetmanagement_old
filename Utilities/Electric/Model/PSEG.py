import datetime
import pathlib
import tabula
import pandas as pd
from decimal import Decimal
from Database.MySQLAM import MySQLAM
from Database.POPO.RealEstate import RealEstate, Address
from Database.POPO.ElectricBillData import ElectricBillData
from Database.POPO.ElectricData import ElectricData
from Database.POPO.UtilityProvider import UtilityProvider
from Utilities.Model.UtilityModelBase import UtilityModelBase


class PSEG(UtilityModelBase):
    """ Perform data operations and calculations on PSEG data """
    def __init__(self):
        super().__init__()

    def process_monthly_bill(self, filename):
        """ Open, process and return pseg monthly bill

        self.amb_dict[(bill start date, bill end date)] is set with returned instance of ElectricBillData

        Args:
            filename (str): name of file in PSEGFiles directory

        Returns:
            ElectricBillData with all required fields populated and as many non required fields as available populated
        """
        df_list = tabula.read_pdf(pathlib.Path(__file__).parent.parent / ("PSEGFiles/" + filename), pages="all",
                                  password="11720", guess=False)
        bill_data = ElectricBillData(None, UtilityProvider.PSEG, None, None, None, 0, 0, None, None,
                                     None, None, None, True)

        # get start date and end date from 1st page
        srs = df_list[0]
        srs = srs[srs.columns[1]]
        service_to_found = False
        address = None
        for row in srs.values:
            if not isinstance(row, str):
                continue
            if "Service To" in row:
                # address is the next row
                service_to_found = True
            elif service_to_found:
                address = Address.to_address(row)
                service_to_found = False
            elif "Service From" in row:
                row = row.split(" ")
                bill_data.start_date = datetime.datetime.strptime("".join(row[-7:-4]), "%b%d,%Y").date()
                bill_data.start_date = bill_data.start_date + datetime.timedelta(days=1)
                bill_data.end_date = datetime.datetime.strptime("".join(row[-3:]), "%b%d,%Y").date()
                break

        # get total kwh from 2nd page third column if it is there. it might be in the first column
        srs = df_list[1]
        srs = srs[srs.columns[2]]
        for row in srs.values:
            if not isinstance(row, str):
                continue
            if "Billed KWH" in row:
                bill_data.total_kwh = int(row.split()[-1].strip())

        # get remaining data from 2nd page first column. get total kwh from here if it is here
        srs = df_list[1]
        srs = srs[srs.columns[0]]
        in_psc = False

        def fmt_int(rs, ind):
            return int(rs[ind].replace(",", "").strip())

        def fmt_dec(rs, ind):
            return Decimal(rs[ind].replace(",", "").strip())

        for row in srs.values:
            if not isinstance(row, str):
                continue

            row_split = row.split(" ")

            if "Electricity used in" in row:
                bill_data.total_kwh = fmt_int(row_split, -2)
            elif "Energy Credit Balance" in row:
                bill_data.bank_kwh = fmt_int(row_split, -1)
            elif "Delivery & System Charges" in row:
                bill_data.dsc_total_cost = fmt_dec(row_split, -1)
            elif "Basic Service" in row:
                bill_data.bs_rate = fmt_dec(row_split, -3)
                bill_data.bs_cost = fmt_dec(row_split, -1)
            elif "CBC" in row:
                bill_data.cbc_rate = fmt_dec(row_split, -3)
                bill_data.cbc_cost = fmt_dec(row_split, -1)
            elif "MFC" in row:
                bill_data.mfc_rate = fmt_dec(row_split, -3)
                bill_data.mfc_cost = fmt_dec(row_split, -1)
            elif all(x in row for x in ["First", "@"]):
                bill_data.first_kwh = fmt_int(row_split, 1)
                bill_data.first_rate = fmt_dec(row_split, 5)
                bill_data.first_cost = fmt_dec(row_split, -1)
            elif all(x in row for x in ["Next", "@"]):
                bill_data.next_kwh = fmt_int(row_split, 1)
                bill_data.next_rate = fmt_dec(row_split, 5)
                bill_data.next_cost = fmt_dec(row_split, -1)
            elif "Power Supply Charges" in row:
                bill_data.psc_total_cost = fmt_dec(row_split, -1)
                in_psc = True
            elif in_psc and all(x in row for x in ["KWH", "@", "="]):
                bill_data.psc_rate = fmt_dec(row_split, -3)
                bill_data.psc_cost = fmt_dec(row_split, -1)
                in_psc = False
            elif "Taxes & Other Charges" in row:
                bill_data.toc_total_cost = fmt_dec(row_split, -1)
            elif "DER Charge" in row:
                bill_data.der_rate = fmt_dec(row_split, -3)
                bill_data.der_cost = fmt_dec(row_split, -1)
            elif "Delivery Service Adjustment" in row:
                bill_data.dsa_cost = fmt_dec(row_split, -1)
            elif "Revenue Decoupling Adjustment" in row and len(row_split) == 4:
                bill_data.rda_cost = fmt_dec(row_split, -1)
            elif "NY State Assessment" in row:
                bill_data.nysa_cost = fmt_dec(row_split, -1)
            elif "Revenue-Based PILOTS" in row:
                bill_data.rbp_cost = fmt_dec(row_split, -1)
            elif "Suffolk Property Tax Adjustment" in row:
                bill_data.spta_cost = fmt_dec(row_split, -1)
            elif "Sales Tax" in row:
                bill_data.st_rate = fmt_dec(row_split, -3) / 100
                bill_data.st_cost = fmt_dec(row_split, -1)
            elif "Total Charges" in row:
                bill_data.total_cost = fmt_dec(row_split, -1)

        bill_data.real_estate = self.read_real_estate_by_address(address)

        self.amb_dict[(bill_data.start_date, bill_data.end_date)] = bill_data
        return bill_data

    def insert_monthly_bill_to_db(self, bill_data):
        """ Insert monthly electric bill to table

        Args:
            bill_data (ElectricBillData): electric bill data to insert

        Raises:
            MySQLException if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.electric_bill_data_insert([bill_data])

    def read_monthly_bill_from_db_by_start_date(self, start_date):
        """ read pseg monthly bill from electric_bill_data table by start date

        self.amb_dict[(bill start date, bill end date)] is set with returned instance of ElectricBillData if found

        Args:
            start_date (datetime.date): start date of bill

        Returns:
            ElectricBillData or None if no bill with start_date

        Raises:
            MySQLException if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.electric_bill_data_read(wheres=[["start_date", "=", start_date]])

        bill_data = None if len(bill_list) == 0 else bill_list[0]
        if bill_data is not None:
            self.amb_dict[(bill_data.start_date, bill_data.end_date)] = bill_data
        return bill_data

    def read_all_monthly_bills_from_db(self):
        with MySQLAM() as mam:
            bill_list = mam.electric_bill_data_read()

        df = pd.DataFrame()

        for bill in bill_list:
            df = pd.concat([df, bill.to_pd_df()], ignore_index=True)
            if bill.is_actual:
                self.amb_dict[(bill.start_date, bill.end_date)] = bill
            else:
                self.emb_dict[(bill.start_date, bill.end_date)] = bill

        return df.sort_values(by=["start_date", "is_actual"])

    def insert_monthly_data_to_db(self, electric_data):
        """ Insert monthly electric data to table

        Args:
            electric_data (ElectricData): electric data to insert

        Raises:
            MySQLException if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.electric_data_insert([electric_data])

    def read_monthly_data_from_db_by_month_year(self, month_year):
        """ read pseg data from electric_data table by month and year

        self.data_dict[month_year] is set with returned instance of ElectricData or None

        Args:
            month_year (str): month and year of data ("MMYYYY" format)

        Returns:
            ElectricData or None if no month_year found

        Raises:
            MySQLException if issue with database read
        """
        with MySQLAM() as mam:
            data_list = mam.electric_data_read(wheres=[["month_year", "=", month_year]])
        self.data_dict[month_year] = None if len(data_list) == 0 else data_list[0]

        return self.data_dict[month_year]

    def read_all_estimate_notes_by_reid_provider(self, real_estate, provider):
        """ read estimate notes from estimate_notes table by real estate and PSEG provider

        Args:
            real_estate (RealEstate): notes for this real estate
            provider (UtilityProvider): notes for this electric provider. UtilityProvider.PSEG used in this function

        Returns:
            list(dict) of notes with keys id, real_estate_id, provider, note_type, note

        Raises:
            MySQLException if issue with database read
        """
        return super().read_all_estimate_notes_by_reid_provider(real_estate, UtilityProvider.PSEG)

    def get_utility_data_instance(self, str_dict):
        """ Populate and return ElectricData instance with values in str_dict

        Args:
            str_dict (dict): dict of field keys and str values

        Returns:
            ElectricData instance
        """
        return ElectricData(None, None, None, None, None, None, None, str_dict=str_dict)

    def initialize_monthly_bill_estimate(self, start_date, end_date):
        """ Initialize monthly bill estimate using data from actual bill

        self.emb_dict[(start_date, end_date)] is set with returned instance of ElectricBillData

        Args:
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill

        Returns:
            ElectricBillData with real_estate, provider, start_date and end_date set with same values as in actual bill

        Raises:
            ValueError if self.amb_dict does not contain bill data for specified start_date and end_date
        """
        amb = self.amb_dict[(start_date, end_date)]
        if amb is None:
            raise ValueError("self.amb_dict does not contain electric bill data for start_date and end_date")

        bill_data = ElectricBillData(amb.real_estate, amb.provider, amb.start_date, amb.end_date, None, 0, 0, None,
                                     amb.bs_rate, amb.bs_cost, None, None, False)

        self.emb_dict[(start_date, end_date)] = bill_data
        return bill_data

    def _do_estimate_total_kwh(self, emb):
        """ Estimate what total kwh usage would have been without solar

        Remove the electric heater kwh usage from the total, since the electric heater would not have been used if no
        solar bank was available.

        Args:
            emb (ElectricBillData): estimate electric bill data

        Returns:
            emb with total_kwh set appropriately
        """
        emb.total_kwh -= emb.eh_kwh

        return emb

    def _do_estimate_dsc(self, emb, ed_start, ed_end):
        """ Estimate delivery and system charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month

        Returns:
            emb with delivery and system charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.first_kwh = min(emb.total_kwh, int(ed_start.first_kwh * s_rat + ed_end.first_kwh * e_rat))
        emb.first_rate = ed_start.first_rate * s_rat + ed_end.first_rate * e_rat
        emb.first_cost = emb.first_kwh * emb.first_rate
        emb.next_kwh = emb.total_kwh - emb.first_kwh
        emb.next_rate = ed_start.next_rate * s_rat + ed_end.next_rate * e_rat
        emb.next_cost = emb.next_kwh * emb.next_rate
        emb.mfc_rate = ed_start.mfc_rate * s_rat + ed_end.mfc_rate * e_rat
        emb.mfc_cost = emb.total_kwh * emb.mfc_rate
        emb.dsc_total_cost = emb.bs_cost + emb.first_cost + emb.next_cost + emb.mfc_cost

        return emb

    def _do_estimate_psc(self, emb, ed_start, ed_end):
        """ Estimate power supply charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month

        Returns:
            emb with power supply charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.psc_rate = ed_start.psc_rate * s_rat + ed_end.psc_rate * e_rat
        emb.psc_cost = emb.total_kwh * emb.psc_rate
        emb.psc_total_cost = emb.psc_cost

        return emb

    def _do_estimate_toc(self, emb, ed_start, ed_end, amb):
        """ Estimate taxes and other charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month
            amb (ElectricBillData): actual electric bill data

        Returns:
            emb with taxes and other charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        # cost dependent on total kwh
        emb.der_rate = ed_start.der_rate * s_rat + ed_end.der_rate * e_rat
        emb.der_cost = emb.total_kwh * emb.der_rate

        # cost dependent on delivery and system charges
        emb.dsa_rate = ed_start.dsa_rate * s_rat + ed_end.dsa_rate * e_rat
        emb.dsa_cost = emb.dsc_total_cost * emb.dsa_rate
        emb.rda_rate = ed_start.rda_rate * s_rat + ed_end.rda_rate * e_rat
        emb.rda_cost = emb.dsc_total_cost * emb.rda_rate
        emb.rbp_rate = ed_start.rbp_rate * s_rat + ed_end.rbp_rate * e_rat
        emb.rbp_cost = emb.dsc_total_cost * emb.rbp_rate

        # cost dependent on subtotal up to this point minus rbp_cost
        subtotal = (emb.dsc_total_cost + emb.psc_total_cost + emb.der_cost + emb.dsa_cost + emb.rda_cost)
        emb.nysa_rate = ed_start.nysa_rate * s_rat + ed_end.nysa_rate * e_rat
        emb.nysa_cost = subtotal * emb.nysa_rate

        # cost dependent on subtotal up to this point minus rbp_cost
        subtotal = (emb.dsc_total_cost + emb.psc_total_cost + emb.der_cost + emb.dsa_cost + emb.rda_cost
                    + emb.nysa_cost)
        emb.spta_rate = ed_start.spta_rate * s_rat + ed_end.spta_rate * e_rat
        emb.spta_cost = subtotal * emb.spta_rate

        # cost dependent on subtotal up to this point
        subtotal = (emb.dsc_total_cost + emb.psc_total_cost + emb.der_cost + emb.dsa_cost + emb.rda_cost + emb.nysa_cost
                    + emb.rbp_cost + emb.spta_cost)
        emb.st_rate = amb.st_rate
        emb.st_cost = emb.st_rate * subtotal

        emb.toc_total_cost = (emb.der_cost + emb.dsa_cost + emb.rda_cost + emb.nysa_cost + emb.rbp_cost + emb.spta_cost
                              + emb.st_cost)

        return emb

    def _do_estimate_total_cost(self, emb):
        """ Estimate bill total cost

        Args:
            emb (ElectricBillData): estimate electric bill data

        Returns:
            emb with total cost estimated
        """
        emb.total_cost = emb.dsc_total_cost + emb.psc_total_cost + emb.toc_total_cost

        return emb

    def do_estimate_monthly_bill(self, start_date, end_date):
        """ Run the process of estimating the monthly bill if solar were not used

        Args:
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill

        Returns:
            emb with all applicable estimate fields set
        """
        amb = self.amb_dict.get((start_date, end_date), None)
        ed_start = self.data_dict.get(start_date.strftime("%m%Y"), None)
        ed_end = self.data_dict.get(end_date.strftime("%m%Y"), None)
        emb = self.emb_dict.get((start_date, end_date), None)
        if any([x is None for x in [amb, ed_start, ed_end, emb]]):
            raise ValueError("actual monthly bill, start month electric data, end month electric data and estimate " +
                             "monthly bill for " + str(start_date) + " - " + str(end_date) + " must be set before " +
                             "calling this function")

        emb = self._do_estimate_total_kwh(emb)
        emb = self._do_estimate_dsc(emb, ed_start, ed_end)
        emb = self._do_estimate_psc(emb, ed_start, ed_end)
        emb = self._do_estimate_toc(emb, ed_start, ed_end, amb)
        emb = self._do_estimate_total_cost(emb)

        return emb