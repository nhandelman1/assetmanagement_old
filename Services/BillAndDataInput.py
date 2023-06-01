import datetime
from Database.POPO.RealEstate import RealEstate
from Database.POPO.ServiceProvider import ServiceProvider
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData
from Database.POPO.ComplexServiceBillDataBase import ComplexServiceBillDataBase
from Database.POPO.ElectricBillData import ElectricBillData
from Database.POPO.NatGasBillData import NatGasBillData
from Database.POPO.UtilityDataBase import UtilityDataBase
from Services.Simple.Model.SimpleServiceModel import SimpleServiceModel
from Services.Model.ComplexServiceModelBase import ComplexServiceModelBase
from Services.Electric.Model.PSEG import PSEG
from Services.Electric.Model.Solar import Solar
from Services.NatGas.Model.NG import NG
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase
from Services.View.ComplexServiceViewBase import ComplexServiceViewBase
from Services.Electric.View.PSEGViewBase import PSEGViewBase
from Services.Electric.View.SolarViewBase import SolarViewBase
from Services.NatGas.View.NGViewBase import NGViewBase


class BillAndDataInput:
    """ Input bill data and other relevant data

    Attributes:
        see init function docstring
    """

    def __init__(self, simple_model, simple_view, pseg_model, pseg_view, solar_model, solar_view, ng_model, ng_view):
        """ init function

        Args:
            simple_model (SimpleServiceModel):
            simple_view (SimpleServiceViewBase):
            pseg_model (PSEG):
            pseg_view (PSEGViewBase): a subclass since base has no implemented functions
            solar_model (Solar):
            solar_view (SolarViewBase): a subclass since base has no implemented functions
            ng_model (NG):
            ng_view (NGViewBase): a subclass since base has no implemented functions
        """
        self.simple_model = simple_model
        self.simple_view = simple_view
        self.pseg_model = pseg_model
        self.pseg_view = pseg_view
        self.solar_model = solar_model
        self.solar_view = solar_view
        self.ng_model = ng_model
        self.ng_view = ng_view

    def do_simple_bill_process(self):
        """ Run process to input data for simple bills

        Returns:
            list[SimpleServiceBillData]: list with instance of bill data. there may be other bill data instances that
                have the same real estate, provider and start date
        """
        filename = self.simple_view.input_read_new_bill()
        bill_data = self.simple_model.process_service_bill(filename)
        self.simple_model.insert_service_bills_to_db([bill_data])
        bill_data = self.simple_model.read_service_bill_from_db_by_repsd(
            bill_data.real_estate, bill_data.provider, bill_data.start_date)

        return bill_data

    def process_or_load_actual_complex_bill(self, model, view):
        """ Read actual service bill from file and store to db or load from db

        Args:
            model (ComplexServiceModelBase): subclass
            view (ComplexServiceViewBase): subclass

        Returns:
            ComplexServiceBillDataBase: subclass instance of actual monthly bill
        """
        opt = view.input_read_new_or_use_existing_bill_option()
        if opt == "1":
            filename = view.input_read_new_bill()
            bill_data = model.process_service_bill(filename)
            model.insert_service_bills_to_db([bill_data])
            real_estate = bill_data.real_estate
            provider = bill_data.provider
            start_date = bill_data.start_date
        else:
            re_dict = model.read_all_real_estate()
            re_id = view.input_select_existing_bill_real_estate(re_dict)
            real_estate = re_dict[re_id]
            provider = view.input_select_existing_bill_provider(model.valid_providers())
            start_date = view.input_read_existing_bill_start_date()
            start_date = datetime.datetime.strptime(start_date, "%Y%m%d").date()

        bill_data = model.read_service_bill_from_db_by_repsd(real_estate, provider, start_date)
        # only one bill will match
        return bill_data[0]

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
            provider (ServiceProvider): utility provider
            date (datetime.date): run function for utility data for this month and year (day is ignored)
            model (ComplexServiceModelBase): subclass
            view (ComplexServiceViewBase): subclass

        Returns:
            UtilityDataBase: subclass instance of utility data
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

    def input_and_load_electric_estimation_data(self, address, start_date, end_date):
        """ Load electric estimation data already available and input any missing data

        Args:
            address (Address): bill for this real estate
            start_date (datetime.date): start date of an actual bill. will be the start date of the estimated bill
            end_date (datetime.date): end date of an actual bill. will be the end date of the estimated bill

        Returns:
            ElectricBillData: instance of estimated monthly bill with real_estate, provider, start_date, end_date,
            total_kwh, eh_kwh set
        """
        estimate_bill_data = self.pseg_model.initialize_complex_service_bill_estimate(address, start_date, end_date)
        kwh_dict = self.solar_model.calculate_total_kwh_between_dates(estimate_bill_data.start_date,
                                                                      estimate_bill_data.end_date)
        e_dict = self.pseg_view.input_estimation_data(
            estimate_bill_data.real_estate.address, estimate_bill_data.start_date, estimate_bill_data.end_date)
        estimate_bill_data.total_kwh = int(kwh_dict["home_kwh"])
        estimate_bill_data.eh_kwh = int(e_dict["eh_kwh"])

        return estimate_bill_data

    def do_electric_process(self):
        """ Run process to input data and calculate savings for electric utilities """
        amb = self.process_or_load_actual_complex_bill(self.pseg_model, self.pseg_view)

        self.process_sunpower_hourly_data_file(amb.start_date, amb.end_date)

        ed_sm = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.start_date, self.pseg_model,
                                                self.pseg_view)
        ed_em = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.end_date, self.pseg_model,
                                                self.pseg_view)

        # gather estimation data available elsewhere and enter estimation data otherwise not available
        emb = self.input_and_load_electric_estimation_data(amb.real_estate.address, amb.start_date, amb.end_date)

        # do bill estimate calculation
        emb = self.pseg_model.do_estimate_monthly_bill(amb.real_estate.address, amb.start_date, amb.end_date)
        self.pseg_model.insert_service_bills_to_db([emb])

    def input_and_load_natgas_estimation_data(self, address, start_date, end_date):
        """ Load natural gas estimation data already available and input any missing data

        Args:
            address (Address): bill for this real estate
            start_date (datetime.date): start date of an actual bill. will be the start date of the estimated bill
            end_date (datetime.date): end date of an actual bill. will be the end date of the estimated bill

        Returns:
            NatGasBillData: instance of estimated monthly bill with real_estate, provider, start_date, end_date,
            bsc_therms, bsc_cost, gs_rate
        """
        estimate_bill_data = self.ng_model.initialize_complex_service_bill_estimate(address, start_date, end_date)
        e_dict = self.ng_view.input_estimation_data(
            estimate_bill_data.real_estate.address, estimate_bill_data.start_date, estimate_bill_data.end_date)
        estimate_bill_data.saved_therms = int(e_dict["saved_therms"])

        return estimate_bill_data

    def do_natgas_process(self):
        """ Run process to input data and calculate savings for natural gas utilities """
        amb = self.process_or_load_actual_complex_bill(self.ng_model, self.ng_view)
        ngd_sm = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.start_date, self.ng_model,
                                                 self.ng_view)
        ngd_em = self.input_or_load_utility_data(amb.real_estate, amb.provider, amb.end_date, self.ng_model,
                                                 self.ng_view)

        # gather estimation data available elsewhere and enter estimation data otherwise not available
        emb = self.input_and_load_natgas_estimation_data(amb.real_estate.address, amb.start_date, amb.end_date)

        # do bill estimate calculation
        emb = self.ng_model.do_estimate_monthly_bill(amb.real_estate.address, amb.start_date, amb.end_date)
        self.ng_model.insert_service_bills_to_db([emb])

    def do_paid_date_process(self):
        """ Run process to input paid date for any bills missing a paid date """
        pass

    def do_main_menu_console_process(self):
        """ Run main menu process through console to select bill related process options """

        while True:
            try:
                print("######################################################################")
                print("Choose a bill or data option from the following:\n")
                print("1: Input Simple Bill")
                print("2: Input Electric Bill and Related Data")
                print("3: Input Natural Gas Bill and Related Data")
                print("4: Input Missing Paid Dates")
                print("0: Exit Program")
                opt = input("\nSelection: ")

                if opt == "1":
                    self.do_simple_bill_process()
                elif opt == "2":
                    self.do_electric_process()
                elif opt == "3":
                    self.do_natgas_process()
                elif opt == "4":
                    self.do_paid_date_process()
                elif opt == "0":
                    break
                else:
                    print(opt + " is not a valid option. Try again faggot.")
            except Exception as ex:
                print(str(ex))