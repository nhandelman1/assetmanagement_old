import datetime
import os
import pathlib
import pandas as pd
import tabula
from typing import Optional
from decimal import Decimal
from Database.MySQLAM import MySQLAM
from Database.POPO.RealEstate import RealEstate, Address
from Database.POPO.NatGasBillData import NatGasBillData
from Database.POPO.NatGasData import NatGasData
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Services.Model.ComplexServiceModelBase import ComplexServiceModelBase


class NG(ComplexServiceModelBase):
    """ Perform data operations and calculations on NationalGrid data """
    def __init__(self):
        """ init function """
        super().__init__()

    def valid_providers(self):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.NG_UTI]
        """
        return [ServiceProviderEnum.NG_UTI]

    def process_service_bill(self, filename):
        """ Open, process and return national grid monthly bill

        Returned instance of NatGasBillData is added to self.asb_dict

        Args:
            filename (str): name of file in directory specified by FI_NATIONALGRID_DIR in .env

        Returns:
            NatGasBillData: with all required fields populated and as many non required fields as available populated

        Raises:
            ValueError: unable to read relevant data in bill
        """
        df_list = tabula.read_pdf(pathlib.Path(__file__).parent.parent.parent.parent /
                            (os.getenv("FI_NATIONALGRID_DIR") + filename), pages="all", password="11720", guess=False)
        bill_data = NatGasBillData(None, None, None, None, None, 0, None, None, None, None, None, None, None, None,
                                   None, None, None, None, True)

        df = None
        for df_1 in df_list:
            if "page2of3" in [x.replace(" ", "").lower() for x in df_1.columns]:
                df = df_1
                break
        if df is None:
            raise ValueError("Unable to read relevant data in bill with filename: " + filename)
        keep_cols = [c for c in df.columns if any([x in c.lower() for x in ["service", "page"]])]
        df = df[keep_cols]
        df.columns = [1, 2]

        def fmt_dec(str_val):
            return Decimal(str_val.replace("$", "").replace(" ", ""))

        date_found = False
        total_found = False
        total_therms_found = False
        next_found = False
        in_delivery_services = True
        for ind, row in df.iterrows():
            str1 = row[1]
            str2 = row[2]
            if isinstance(str1, str):
                row_split = str1.split(" ")

                if " to " in str1 and not date_found:
                    bill_data.start_date = datetime.datetime.strptime(" ".join(row_split[0:3]), "%b %d, %Y").date()
                    bill_data.start_date = bill_data.start_date + datetime.timedelta(days=1)
                    bill_data.end_date = datetime.datetime.strptime(" ".join(row_split[-3:]), "%b %d, %Y").date()
                    date_found = True
                elif "Basic Service Charge" in str1:
                    bill_data.bsc_therms = Decimal(row_split[-2])
                    bill_data.bsc_cost = Decimal(str2)
                elif "Next" in str1:
                    bill_data.next_therms = Decimal(row_split[1])
                    bill_data.next_rate = Decimal(row_split[3])
                    bill_data.next_cost = Decimal(str2)
                    next_found = True
                elif "Over/Last" in str1:
                    if next_found:
                        bill_data.over_therms = Decimal(row_split[1])
                        bill_data.over_rate = Decimal(row_split[3])
                        bill_data.over_cost = round(bill_data.over_therms * bill_data.over_rate, 2)
                    else:
                        bill_data.next_therms = Decimal(row_split[1])
                        bill_data.next_rate = Decimal(row_split[3])
                        bill_data.next_cost = round(bill_data.next_therms * bill_data.next_rate, 2)
                elif "Delivery Rate Adj" in str1:
                    bill_data.dra_rate = Decimal(row_split[3])
                    # stupid formatting in pdf might push the cost from the expected column to another column
                    bill_data.dra_cost = round(bill_data.total_therms * bill_data.dra_rate, 2) if pd.isna(str2) \
                        else Decimal(str2)
                elif "System Benefits Charge" in str1:
                    bill_data.sbc_rate = Decimal(row_split[3])
                    bill_data.sbc_cost = Decimal(str2)
                elif "Transp Adj Chg" in str1:
                    bill_data.tac_rate = Decimal(row_split[3])
                    bill_data.tac_cost = Decimal(str2)
                elif "Billing Charge" in str1:
                    bill_data.bc_cost = Decimal(str2)
                elif "NY State and Local Surcharges" in str1 and in_delivery_services:
                    bill_data.ds_nysls_cost = Decimal(str2)
                elif "NY State Sales Tax" in str1 and in_delivery_services:
                    bill_data.ds_nysst_rate = Decimal(row_split[4]) / 100
                    bill_data.ds_nysst_cost = Decimal(str2)
                elif "Total Delivery Services" in str1:
                    bill_data.ds_total_cost = fmt_dec(str2)
                    in_delivery_services = False
                elif "Gas Supply" in str1:
                    bill_data.gs_rate = Decimal(row_split[2])
                    bill_data.gs_cost = Decimal(str2)
                elif "NY State and Local Surcharges" in str1 and not in_delivery_services:
                    bill_data.ss_nysls_cost = Decimal(str2)
                elif "Sales Tax" in str1 and not in_delivery_services:
                    if "NY State Sales Tax" in str1:
                        bill_data.ss_nysst_rate = Decimal(row_split[4]) / 100
                    else:
                        bill_data.ss_nysst_rate = Decimal("0.025")
                        bill_data.notes = "No supply services sales tax provided. Assumed to be 0.025."
                    bill_data.ss_nysst_cost = Decimal(str2)
                elif "Total Supply Services" in str1:
                    bill_data.ss_total_cost = fmt_dec(str2)
                elif "Paperless Billing Credit" in str1:
                    bill_data.pbc_cost = Decimal(str2)
                elif "Total Other Charges/Adjustments" in str1:
                    bill_data.oca_total_cost = fmt_dec(str2)

            if isinstance(str2, str):
                if not total_found:
                    # total should be the first string in column 2
                    bill_data.total_cost = fmt_dec(str2)
                    total_found = True
                elif "=  Used" in str2 and not total_therms_found:
                    total_therms_found = True
                elif total_therms_found:
                    bill_data.total_therms = int(str2)
                    total_therms_found = False

        bill_data.real_estate = self.read_real_estate_by_address(Address.to_address(df.at[2, 1] + df.at[3, 1]))
        bill_data.service_provider = self.read_service_provider_by_enum(ServiceProviderEnum.NG_UTI)
        self.asb_dict.insert_bills(bill_data)

        return bill_data

    def insert_service_bills_to_db(self, bill_list, ignore=None):
        """ Insert monthly natural gas bills to table

        Args:
            bill_list (list[NatGasBillData]): natural gas bill data to insert
            ignore (Optional[boolean]): see superclass docstring

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.natgas_bill_data_insert(bill_list, ignore=ignore)

    def update_service_bills_in_db_paid_date_by_id(self, bill_list):
        """ Update natural gas bills paid_date in natgas_bill_data table by id

        Args:
            bill_list (list[NatGasBillData]): natural gas bill data to update

        Raises:
            MySQLException: if database update issue occurs
        """
        with MySQLAM() as mam:
            mam.natgas_bill_data_update(["paid_date"], wheres=[["id", "=", None]], bill_list=bill_list)

    def read_service_bill_from_db_by_repsd(self, real_estate, service_provider, start_date):
        """ read national grid monthly bill from natgas_bill_data table by real estate, service provider, start date

        Returned instance(s) of NatGasBillData, if found, are added to self.asb_dict

        Args:
            real_estate (RealEstate): real estate location of bill
            service_provider (ServiceProvider): service provider of bill
            start_date (datetime.date): start date of bill

        Returns:
            list[NatGasBillData]: empty list if no bill matching parameters

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.natgas_bill_data_read(
                wheres=[["real_estate_id", "=", real_estate.id], ["service_provider_id", "=", service_provider.id],
                        ["start_date", "=", start_date]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_all_service_bills_from_db_unpaid(self):
        """ Read all natural gas bills that have a null paid date and are actual bills

        Natural gas bills are inserted in self.asb_dict

        Returns:
            list[NatGasBillData]: empty list if no bill with null paid date

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            bill_list = mam.natgas_bill_data_read(wheres=[["paid_date", "is", None], ["is_actual", "=", True]])

        self.asb_dict.insert_bills(bill_list)

        return bill_list

    def read_service_bills_from_db_by_resppdr(self, real_estate_list=(), service_provider_list=(), paid_date_min=None,
                                              paid_date_max=None, to_pd_df=False):
        wheres = self.resppdr_wheres_clause(real_estate_list=real_estate_list,
                service_provider_list=service_provider_list, paid_date_min=paid_date_min, paid_date_max=paid_date_max)

        with MySQLAM() as mam:
            bill_list = mam.natgas_bill_data_read(wheres=wheres, order_bys=["paid_date"])

        return self.bills_post_read(bill_list, to_pd_df=to_pd_df)

    def read_one_bill(self):
        with MySQLAM() as mam:
            bill_list = mam.natgas_bill_data_read(limit=1)

        if len(bill_list) == 0:
            raise ValueError("No natural gas bills found. Check that table has at least one record")

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

    def insert_monthly_data_to_db(self, natgas_data):
        """ Insert monthly natural gas data to table

        Args:
            natgas_data (NatGasData): natural gas data to insert

        Raises:
            MySQLException: if database insert issue occurs
        """
        with MySQLAM() as mam:
            mam.natgas_data_insert([natgas_data])

    def read_monthly_data_from_db_by_month_year(self, month_year):
        """ read national grid data from natgas_data table by month and year

        self.data_dict[month_year] is set with returned instance of NatGasData or None

        Args:
            month_year (str): month and year of data ("MMYYYY" format)

        Returns:
            Optional[NatGasData]: NatGasData or None if no month_year found

        Raises:
            MySQLException: if issue with database read
        """
        with MySQLAM() as mam:
            data_list = mam.natgas_data_read(wheres=[["month_year", "=", month_year]])
        self.data_dict[month_year] = None if len(data_list) == 0 else data_list[0]

        return self.data_dict[month_year]

    def read_all_estimate_notes_by_reid_provider(self, real_estate, provider):
        """ read estimate notes from estimate_notes table by real estate and NationalGrid provider

        Args:
            real_estate (RealEstate): notes for this real estate
            provider (Union[ServiceProvider, ServiceProviderEnum]): notes for this natural gas provider.
                Forced to use ServiceProvider with ServiceProviderEnum.NG_UTI in this function

        Returns:
            list[dict]: of notes with keys id, real_estate_id, service_provider_id, note_type, note, note_order

        Raises:
            MySQLException: if issue with database read
        """
        return super().read_all_estimate_notes_by_reid_provider(real_estate, ServiceProviderEnum.NG_UTI)

    def get_utility_data_instance(self, str_dict):
        """ Populate and return NatGasData instance with values in str_dict

        Args:
            str_dict (dict): dict of field keys and str values

        Returns:
            NatGasData: instance populated with values in str_dict
        """
        return NatGasData(None, None, None, None, None, None, None, None, None, None, str_dict=str_dict)

    def initialize_complex_service_bill_estimate(self, address, start_date, end_date, provider=None):
        """ Initialize monthly bill estimate using data from actual bill

        Returned instance of NatGasBillData is added to self.esb_dict

        Args:
            address (Address): address of actual bill
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill
            provider (Optional[ServiceProviderEnum]): Forced to ServiceProviderEnum.NG_UTI in this function

        Returns:
            NatGasBillData: with real_estate, service_provider, start_date, end_date, total_therms, bsc_therms,
            bsc_cost, gs_rate, dra_rate, sbc_rate, tac_rate, bc_cost, ds_nysst_rate, ss_nysst_rate, pbc_cost set with
            same values as in actual bill

        Raises:
            ValueError: if self.asb_dict does not contain bill data for specified parameters
        """
        provider = ServiceProviderEnum.NG_UTI

        amb = self.asb_dict.get_bills(addresses=address, providers=provider, start_dates=start_date, end_dates=end_date)
        if len(amb) == 0:
            raise ValueError("self.asb_dict doesn't contain natural gas bill data for: " + str(address.value) + ", "
                             + str(provider.value) + ", " + str(start_date) + ", " + str(end_date))
        # there should be only one bill in the list
        amb = amb[0]

        bill_data = NatGasBillData(amb.real_estate, amb.service_provider, amb.start_date, amb.end_date,
                                   amb.total_therms, None, None, None, amb.bsc_therms, amb.bsc_cost, None, amb.next_rate,
                                   None, None, amb.gs_rate, None, None, None, False, dra_rate=amb.dra_rate,
                                   sbc_rate=amb.sbc_rate, tac_rate=amb.tac_rate, bc_cost=amb.bc_cost,
                                   ds_nysst_rate=amb.ds_nysst_rate, ss_nysst_rate=amb.ss_nysst_rate,
                                   pbc_cost=amb.pbc_cost)

        self.esb_dict.insert_bills(bill_data)

        return bill_data

    def _do_estimate_total_therms(self, emb):
        """ Estimate what total natural gas therms would have been without solar

        Add the saved therms to the total, since the furnace would have been used if no solar bank was available.

        Args:
            emb (NatGasBillData): estimate natural gas bill data

        Returns:
            NatGasBillData: emb with total_therms set appropriately
        """
        emb.total_therms += emb.saved_therms

        return emb

    def _do_estimate_ds(self, emb, ngd_start, ngd_end, amb):
        """ Estimate delivery services charges

        Args:
            emb (NatGasBillData): estimate natural gas bill data
            ngd_start (NatGasData): for the earlier month
            ngd_end (NatGasData): for the later month
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: emb with delivery services charges estimated
        """
        def sum_none(*nums):
            return sum(filter(None, nums))

        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.next_therms = min(emb.total_therms - emb.bsc_therms,
                              ngd_start.next_therms * s_rat + ngd_end.next_therms * e_rat)
        emb.next_cost = emb.next_therms * emb.next_rate
        emb.over_therms = emb.total_therms - emb.bsc_therms - emb.next_therms
        # over rate may not be in the bill
        emb.over_rate = ngd_start.over_rate * s_rat + ngd_end.over_rate * e_rat if amb.over_rate is None \
            else amb.over_rate
        emb.over_cost = emb.over_therms * emb.over_rate
        emb.dra_cost = sum_none(emb.dra_rate) * emb.total_therms
        emb.sbc_rate = sum_none(emb.sbc_rate)
        emb.sbc_cost = emb.sbc_rate * emb.total_therms
        emb.tac_rate = sum_none(emb.tac_rate)
        emb.tac_cost = emb.tac_rate * emb.total_therms
        emb.ds_nysls_rate = sum_none(amb.ds_nysls_cost) / sum_none(amb.bsc_cost, amb.next_cost, amb.over_cost,
                                                                   amb.dra_cost, amb.sbc_cost, amb.bc_cost)
        subtotal = sum_none(emb.bsc_cost, emb.next_cost, emb.over_cost, emb.dra_cost, emb.sbc_cost, emb.tac_cost,
                            emb.bc_cost)
        emb.ds_nysls_cost = emb.ds_nysls_rate * subtotal
        emb.ds_nysst_rate = amb.ds_nysst_rate
        emb.ds_nysst_cost = emb.ds_nysst_rate * (subtotal + emb.ds_nysls_cost)
        emb.ds_total_cost = subtotal + emb.ds_nysls_cost + emb.ds_nysst_cost
        return emb

    # noinspection PyTypeChecker
    def _do_estimate_ss(self, emb, ed_start, ed_end, amb):
        """ Estimate supply services charges

        The bill can span over two months, but I can't determine how the ratio is determined (it's not as simple as a
        ratio of days in each month). For gas supply rate (gs_rate), use the value in the actual bill. For ny state and
        local surcharges rate (ss_nysls_rate) use the ratio of the supply service nysls cost in the actual bill to the
        subtotal of all previous supply service charges (e.g. dont include supply service sales tax in the subtotal)

        Args:
            emb (NatGasBillData): estimate natural gas bill data
            ed_start (NatGasData): for the earlier month
            ed_end (NatGasData): for the later month
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: emb with supply services charges estimated
        """
        def sum_none(*nums):
            return sum(filter(None, nums))

        emb.gs_cost = emb.gs_rate * emb.total_therms
        emb.ss_nysls_rate = sum_none(amb.ss_nysls_cost) / amb.gs_cost
        emb.ss_nysls_cost = emb.ss_nysls_rate * emb.gs_cost
        emb.ss_nysst_rate = amb.ss_nysst_rate
        emb.ss_nysst_cost = amb.ss_nysst_rate * emb.gs_cost
        emb.ss_total_cost = emb.gs_cost + emb.ss_nysls_cost + emb.ss_nysst_cost

        return emb

    def _do_estimate_oca(self, emb, ed_start, ed_end, amb):
        """ Estimate other charges/adjustments

        paperless billing credit is the only other charges/adjustments item

        Args:
            emb (NatGasBillData): estimate natural gas bill data
            ed_start (NatGasData): for the earlier month
            ed_end (NatGasData): for the later month
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: emb with other charges/adjustments estimated
        """
        emb.oca_total_cost = emb.pbc_cost

        return emb

    def _do_estimate_total_cost(self, emb):
        """ Estimate bill total cost

        Args:
            emb (NatGasBillData): estimate natural gas bill data

        Returns:
            NatGasBillData: emb with total cost estimated
        """
        emb.total_cost = emb.ds_total_cost + emb.ss_total_cost + emb.oca_total_cost
        emb = self.set_default_tax_related_cost([(emb, Decimal("NaN"))])[0]

        return emb

    def do_estimate_monthly_bill(self, address, start_date, end_date, provider=None):
        """ Run the process of estimating the monthly bill if solar were not used

        Nat gas bill is lowered due to using kwh bank for electric heating instead of nat gas heating

        Args:
            address (Address): address of actual bill
            start_date (datetime.date): start date of actual bill
            end_date (datetime.date): end date of actual bill
            provider (Optional[ServiceProviderEnum]): Forced to ServiceProviderEnum.NG_UTI in this function

        Returns:
            NatGasBillData: emb with all applicable estimate fields set

        Raises:
            ValueError: if self.asb_dict or self.esb_dict or self.data_dict do not contain bill data for specified
                parameters
        """
        provider = ServiceProviderEnum.NG_UTI

        amb = self.asb_dict.get_bills(addresses=address, providers=provider, start_dates=start_date, end_dates=end_date)
        ngd_start = self.data_dict.get(start_date.strftime("%m%Y"), None)
        ngd_end = self.data_dict.get(end_date.strftime("%m%Y"), None)
        emb = self.esb_dict.get_bills(addresses=address, providers=provider, start_dates=start_date, end_dates=end_date)

        if len(amb) == 0 or len(emb) == 0 or ngd_start is None or ngd_end is None:
            raise ValueError("actual monthly bill, start month natural gas data, end month natural gas data and " +
                             "estimate monthly bill for " + str(address.value) + ", " + str(provider.value) + ", "
                             + str(start_date) + " - " + str(end_date) + " must be set before calling this function")

        # there should be only one actual bill and one estimated bill in each of the bill dicts
        amb = amb[0]
        emb = emb[0]

        emb = self._do_estimate_total_therms(emb)
        emb = self._do_estimate_ds(emb, ngd_start, ngd_end, amb)
        emb = self._do_estimate_ss(emb, ngd_start, ngd_end, amb)
        emb = self._do_estimate_oca(emb, ngd_start, ngd_end, amb)
        emb = self._do_estimate_total_cost(emb)

        return emb