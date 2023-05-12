import datetime
from Database.POPO.RealEstate import RealEstate
from Database.POPO.UtilityProvider import UtilityProvider
from Utilities.Model.UtilityModelBase import UtilityModelBase
from Utilities.Electric.Model.PSEG import PSEG
from Utilities.Electric.Model.Solar import Solar
from Utilities.NatGas.Model.NG import NG
from Utilities.Electric.View.PSEGViewBase import PSEGViewBase
from Utilities.Electric.View.PSEGConsoleUI import PSEGConsoleUI
from Utilities.Electric.View.SolarViewBase import SolarViewBase
from Utilities.Electric.View.SolarConsoleUI import SolarConsoleUI
from Utilities.NatGas.View.NGViewBase import NGViewBase
from Utilities.NatGas.View.NGConsoleUI import NGConsoleUI


class BillAndDataInput:
    """ Input bill data and other relevant data

    Attributes:
        see init function docstring
    """

    def __init__(self, pseg_model, pseg_view, solar_model, solar_view, ng_model, ng_view):
        """ init function

        Args:
            pseg_model (PSEG):
            pseg_view (PSEGViewBase): a subclass since base has no implemented functions
            solar_model (Solar):
            solar_view (SolarViewBase): a subclass since base has no implemented functions
            ng_model (NG):
            ng_view (NGViewBase): a subclass since base has no implemented functions
        """
        self.pseg_model = pseg_model
        self.pseg_view = pseg_view
        self.solar_model = solar_model
        self.solar_view = solar_view
        self.ng_model = ng_model
        self.ng_view = ng_view

    def process_or_load_actual_monthly_bill(self, model, view):
        """ Read actual monthly bill from file and store to db or load from db

        Args:
            model (UtilityModelBase): subclass of UtilityModelBase class
            view (UtilityViewBase): subclass of UtilityViewBase class

        Returns:
            subclass of UtilityBillDataBase instance of actual monthly bill
        """
        opt = view.input_read_new_or_use_existing_bill_option()
        if opt == "1":
            filename = view.input_read_new_bill()
            bill_data = model.process_monthly_bill(filename)
            model.insert_monthly_bill_to_db(bill_data)
            start_date = bill_data.start_date
        else:
            start_date = view.input_read_existing_bill_start_date()
            start_date = datetime.datetime.strptime(start_date, "%Y%m%d").date()

        bill_data = model.read_monthly_bill_from_db_by_start_date(start_date)

        return bill_data

    def process_sunpower_hourly_data_file(self, start_date, end_date):
        """ Read sunpower hourly data from file and store to db or skip if data already stored

        Args:
            start_date (datetime.date): file should have data starting on this date
            end_date (datetime.date): file should have data ending on this date
        """
        opt = self.solar_view.input_read_new_or_skip(start_date, end_date)
        if opt == "1":
            filename = self.solar_view.input_read_new_hourly_data_file(start_date, end_date)
            df = self.solar_model.process_sunpower_hourly_file(filename)
            self.solar_model.insert_sunpower_hourly_data_to_db(df)

    def input_or_load_utility_data(self, real_estate, provider, date, model, view):
        """ Input utility data and store to db or load from db

        Args:
            real_estate (RealEstate): bill for this real estate
            provider (UtilityProvider): utility provider
            date (datetime.date): run function for utility data for this month and year (day is ignored)
            model (UtilityModelBase): subclass of UtilityModelBase class
            view (UtilityViewBase): subclass of UtilityViewBase class

        Returns:
            UtilityDataBase subclass instance of utility data
        """
        month_year = date.strftime("%m%Y")
        utility_data = model.read_monthly_data_from_db_by_month_year(month_year)

        if utility_data is None:
            notes_list = model.read_all_estimate_notes_by_reid_provider(real_estate, provider)
            view.display_utility_data_found_or_not(False, month_year)
            el_dict = view.input_values_for_notes(notes_list)
            el_dict.update({"real_estate": real_estate, "provider": provider, "month_date": date,
                            "month_year": month_year})

            utility_data = model.get_utility_data_instance(el_dict)
            model.insert_monthly_data_to_db(utility_data)
            utility_data = model.read_monthly_data_from_db_by_month_year(utility_data.month_year)
        else:
            view.display_utility_data_found_or_not(True, month_year)

        return utility_data

    def input_and_load_electric_estimation_data(self, start_date, end_date):
        """ Load electric estimation data already available and input any missing data

        Args:
            start_date (datetime.date): start date of an actual bill. will be the start date of the estimated bill
            end_date (datetime.date): end date of an actual bill. will be the end date of the estimated bill

        Returns:
            ElectricBillData instance of estimated monthly bill with real_estate, provider, start_date, end_date,
            total_kwh, eh_kwh set
        """
        estimate_bill_data = self.pseg_model.initialize_monthly_bill_estimate(start_date, end_date)
        kwh_dict = self.solar_model.calculate_total_kwh_between_dates(estimate_bill_data.start_date,
                                                                      estimate_bill_data.end_date)
        e_dict = self.pseg_view.input_estimation_data(estimate_bill_data.start_date, estimate_bill_data.end_date)
        estimate_bill_data.total_kwh = int(kwh_dict["home_kwh"])
        estimate_bill_data.eh_kwh = int(e_dict["eh_kwh"])

        return estimate_bill_data

    def do_electric_process(self):
        """ Run process to input data and calculate savings for electric utilities """
        amb = self.process_or_load_actual_monthly_bill(self.pseg_model, self.pseg_view)

        self.process_sunpower_hourly_data_file(amb.start_date, amb.end_date)

        ed_sm = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.start_date, self.pseg_model,
                                                self.pseg_view)
        ed_em = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.end_date, self.pseg_model,
                                                self.pseg_view)

        # gather estimation data available elsewhere and enter estimation data otherwise not available
        emb = self.input_and_load_electric_estimation_data(amb.start_date, amb.end_date)

        # do bill estimate calculation
        emb = self.pseg_model.do_estimate_monthly_bill(amb.start_date, amb.end_date)
        self.pseg_model.insert_monthly_bill_to_db(emb)

    def input_and_load_natgas_estimation_data(self, start_date, end_date):
        """ Load natural gas estimation data already available and input any missing data

        Args:
            start_date (datetime.date): start date of an actual bill. will be the start date of the estimated bill
            end_date (datetime.date): end date of an actual bill. will be the end date of the estimated bill

        Returns:
            NatGasBillData instance of estimated monthly bill with real_estate, provider, start_date, end_date,
            bsc_therms, bsc_cost, gs_rate
        """
        estimate_bill_data = self.ng_model.initialize_monthly_bill_estimate(start_date, end_date)
        e_dict = self.ng_view.input_estimation_data(estimate_bill_data.start_date, estimate_bill_data.end_date)
        estimate_bill_data.saved_therms = int(e_dict["saved_therms"])

        return estimate_bill_data

    def do_natgas_process(self):
        """ Run process to input data and calculate savings for natural gas utilities """
        amb = self.process_or_load_actual_monthly_bill(self.ng_model, self.ng_view)
        ngd_sm = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.start_date, self.ng_model,
                                                 self.ng_view)
        ngd_em = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.end_date, self.ng_model,
                                                 self.ng_view)

        # gather estimation data available elsewhere and enter estimation data otherwise not available
        emb = self.input_and_load_natgas_estimation_data(amb.start_date, amb.end_date)

        # do bill estimate calculation
        emb = self.ng_model.do_estimate_monthly_bill(amb.start_date, amb.end_date)
        self.ng_model.insert_monthly_bill_to_db(emb)