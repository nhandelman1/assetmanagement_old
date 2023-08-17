import datetime
import os
import pathlib
import tabula
from decimal import Decimal
from typing import Optional, Union
from Database.MySQLAM import MySQLAM
from Database.POPO.ElectricBillData import ElectricBillData
from Database.POPO.ElectricData import ElectricData
from Database.POPO.RealEstate import RealEstate, Address
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Services.Model.ComplexServiceModelBase import ComplexServiceModelBase


class PSEG(ComplexServiceModelBase):
    """ Perform data operations and calculations on PSEG data """
    def __init__(self):
        """ init function """
        super().__init__()

    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.PSEG_UTI]
        """
        return [ServiceProviderEnum.PSEG_UTI]

    def process_service_bill(self, filename):
        """ Open, process and return pseg monthly bill

        Returned instance of ElectricBillData is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by FI_PSEG_DIR in .env

        Returns:
            ElectricBillData: with all required fields populated and as many non required fields as available populated
        """
        df_list = tabula.read_pdf(pathlib.Path(__file__).parent.parent.parent.parent /
                                  (os.getenv("FI_PSEG_DIR") + filename), pages="all", password="11720", guess=False)
        bill_data = ElectricBillData.default_constructor()
        bill_data.eh_kwh = 0
        bill_data.bank_kwh = 0
        bill_data.is_actual = True

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
        bill_data.service_provider = self.read_service_provider_by_enum(ServiceProviderEnum.PSEG_UTI)
        self.asb_dict.insert_bills(bill_data)

        return bill_data

    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert monthly electric bills to table

        Args:
            bill_list (list[ElectricBillData]): electric bill data to insert
            ignore (Optional[boolean]): see superclass docstring

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.electric_bill_data_insert(bill_list, ignore=ignore)

    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update electric bills paid_date in electric_bill_data table by id

        Args:
            bill_list (list[ElectricBillData]): electric bill data to update

        Raises:
            MySQLException: if database update issue occurs
        """
        with MySQLAM() as mam:
            mam.electric_bill_data_update(["paid_date"], wheres=[["id", "=", None]], bill_list=bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ read pseg monthly bill from electric_bill_data table by real estate, service provider, start date

        Returned instance(s) of ElectricBillData, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[ElectricBillData]: empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.electric_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_all_service_bills_from_db_unpaid(self):
        """ Read all electric bills that have a null paid date and are actual bills

        Electric bills are inserted in self.asb_dict

        Returns:
            list[ElectricBillData]: empty list if no bill with null paid date

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.electric_bill_data_read(wheres=[["paid_date", "is", None], ["is_actual", "=", True]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=False):
        wheres = self.resppdr_wheres_clause(real_estate_list=real_estate_list,
                service_provider_list=service_provider_list, paid_date_min=paid_date_min, paid_date_max=paid_date_max)

        with MySQLAM() as mam:
            bill_list = mam.electric_bill_data_read(wheres=wheres, order_bys=["paid_date"])

        return self.bills_post_read(bill_list, to_pd_df=to_pd_df)

    def read_one_bill(self):
        with MySQLAM() as mam:
            bill_list = mam.electric_bill_data_read(limit=1)

        if len(bill_list) == 0:
            raise ValueError("No electric bills found. Check that table has at least one record")

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

    def insert_monthly_data_to_db(self, electric_data):
        """ Insert monthly electric data to table

        Args:
            electric_data (ElectricData): electric data to insert

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.electric_data_insert([electric_data])

    def read_monthly_data_from_db_by_month_year(self, month_year):
        """ read pseg data from electric_data table by month and year

        self.data_dict[month_year] is set with returned instance of ElectricData or None

        Args:
            month_year (str): month and year of data ("MMYYYY" format)

        Returns:
            Optional[ElectricData]: ElectricData or None if no month_year found

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            data_list = mam.electric_data_read(wheres=[["month_year", "=", month_year]])
        self.data_dict[month_year] = None if len(data_list) == 0 else data_list[0]

        return self.data_dict[month_year]

    def read_all_estimate_notes_by_reid_provider(self, real_estate, provider):
        """ read estimate notes from estimate_notes table by real estate and PSEG provider

        Args:
            real_estate (RealEstate): notes for this real estate
            provider (Union[ServiceProvider, ServiceProviderEnum]): notes for this electric provider.
                Forced to use ServiceProvider with ServiceProviderEnum.PSEG_UTI in this function

        Returns:
            list[dict]: of notes with keys id, real_estate_id, service_provider_id, note_type, note, note_order

        Raises:
            MySQLException: if issue with database read
        """
        return super().read_all_estimate_notes_by_reid_provider(real_estate, ServiceProviderEnum.PSEG_UTI)

    def get_utility_data_instance(self, str_dict):
        """ Populate and return ElectricData instance with values in str_dict

        Args:
            str_dict (dict): dict of field keys and str values

        Returns:
            ElectricData: instance populated with values in str_dict
        """
        return ElectricData.str_dict_constructor(str_dict)

    def initialize_complex_service_bill_estimate(self, address, start_date, end_date, provider=None):
        """ Initialize monthly bill estimate using data from actual bill

        Returned instance of ElectricBillData is added to self.esb_dict

        Args:
            address (Address): address of actual bill
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill
            provider (Optional[ServiceProviderEnum]): Forced to ServiceProviderEnum.PSEG_UTI in this function

        Returns:
            ElectricBillData: with real_estate, provider, start_date and end_date set with same values as in actual bill

        Raises:
            ValueError: if self.asb_dict does not contain bill data for specified parameters
        """
        provider = ServiceProviderEnum.PSEG_UTI

        amb = self.asb_dict.get_bills(addresses=address, providers=provider, start_dates=start_date, end_dates=end_date)
        if len(amb) == 0:
            raise ValueError("self.asb_dict doesn't contain electric bill data for: " + str(address.value) + ", "
                             + str(provider.value) + ", " + str(start_date) + ", " + str(end_date))
        # there should be only one bill in the list
        amb = amb[0]

        bill_data = ElectricBillData(amb.real_estate, amb.service_provider, amb.start_date, amb.end_date, None, 0, 0,
                                     None, amb.bs_rate, amb.bs_cost, None, None, None, False)

        self.esb_dict.insert_bills(bill_data)

        return bill_data

    def _do_estimate_total_kwh(self, emb):
        """ Estimate what total kwh usage would have been without solar

        Remove the electric heater kwh usage from the total, since the electric heater would not have been used if no
        solar bank was available.

        Args:
            emb (ElectricBillData): estimate electric bill data

        Returns:
            ElectricBillData: emb with total_kwh set appropriately
        """
        emb.total_kwh -= emb.eh_kwh

        return emb

    # noinspection PyTypeChecker
    def _do_estimate_dsc(self, emb, ed_start, ed_end):
        """ Estimate delivery and system charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.


        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month

        Returns:
            ElectricBillData: emb with delivery and system charges estimated
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

    # noinspection PyTypeChecker
    def _do_estimate_psc(self, emb, ed_start, ed_end):
        """ Estimate power supply charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month

        Returns:
            ElectricBillData: emb with power supply charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.psc_rate = ed_start.psc_rate * s_rat + ed_end.psc_rate * e_rat
        emb.psc_cost = emb.total_kwh * emb.psc_rate
        emb.psc_total_cost = emb.psc_cost

        return emb

    # noinspection PyTypeChecker
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
            ElectricBillData: emb with taxes and other charges estimated
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

    # noinspection PyTypeChecker
    def _do_estimate_total_cost(self, emb):
        """ Estimate bill total cost

        Args:
            emb (ElectricBillData): estimate electric bill data

        Returns:
            ElectricBillData: emb with total cost estimated
        """
        emb.total_cost = emb.dsc_total_cost + emb.psc_total_cost + emb.toc_total_cost
        emb = self.set_default_tax_related_cost([(emb, Decimal("NaN"))])

        return emb

    def do_estimate_monthly_bill(self, address, start_date, end_date, provider=None):
        """ Run the process of estimating the monthly bill if solar were not used

        Args:
            address (Address): address of actual bill
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill
            provider (Optional[ServiceProviderEnum]): Forced to ServiceProviderEnum.PSEG_UTI in this function

        Returns:
            ElectricBillData: estimated monthly bill with all applicable estimate fields set

        Raises:
            ValueError: if self.asb_dict or self.esb_dict or self.data_dict do not contain bill data for specified
                parameters
        """
        provider = ServiceProviderEnum.PSEG_UTI

        amb = self.asb_dict.get_bills(addresses=address, providers=provider, start_dates=start_date, end_dates=end_date)
        ed_start = self.data_dict.get(start_date.strftime("%m%Y"), None)
        ed_end = self.data_dict.get(end_date.strftime("%m%Y"), None)
        emb = self.esb_dict.get_bills(addresses=address, providers=provider, start_dates=start_date, end_dates=end_date)
        if len(amb) == 0 or len(emb) == 0 or ed_start is None or ed_end is None:
            raise ValueError("actual monthly bill, start month electric data, end month electric data and estimate " +
                             "monthly bill for " + str(address.value) + ", " + str(provider.value) + ", "
                             + str(start_date) + " - " + str(end_date) + " must be set before calling this function")

        # there should be only one actual bill and one estimated bill in each of the bill dicts
        amb = amb[0]
        emb = emb[0]

        emb = self._do_estimate_total_kwh(emb)
        emb = self._do_estimate_dsc(emb, ed_start, ed_end)
        emb = self._do_estimate_psc(emb, ed_start, ed_end)
        emb = self._do_estimate_toc(emb, ed_start, ed_end, amb)
        emb = self._do_estimate_total_cost(emb)

        return emb