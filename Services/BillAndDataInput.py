import datetime
import colorama
from Database.POPO.RealEstate import RealEstate
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData
from Database.POPO.ComplexServiceBillDataBase import ComplexServiceBillDataBase
from Database.POPO.SolarBillData import SolarBillData
from Database.POPO.ElectricBillData import ElectricBillData
from Database.POPO.NatGasBillData import NatGasBillData
from Database.POPO.UtilityDataBase import UtilityDataBase
from Database.POPO.MortgageBillData import MortgageBillData
from Database.POPO.DepreciationBillData import DepreciationBillData
from Services.Simple.Model.SimpleServiceModel import SimpleServiceModel
from Services.Simple.View.SimpleViewBase import SimpleViewBase
from Services.Model.ComplexServiceModelBase import ComplexServiceModelBase
from Services.Electric.Model.PSEG import PSEG
from Services.Electric.Model.Solar import Solar
from Services.NatGas.Model.NG import NG
from Services.View.ComplexServiceViewBase import ComplexServiceViewBase
from Services.Mortgage.Model.MS import MS
from Services.Mortgage.View.MortgageViewBase import MortgageViewBase
from Services.Electric.View.PSEGViewBase import PSEGViewBase
from Services.Electric.View.SolarViewBase import SolarViewBase
from Services.NatGas.View.NGViewBase import NGViewBase
from Services.Depreciation.Model.DepreciationModel import DepreciationModel
from Services.Depreciation.View.DepreciationViewBase import DepreciationViewBase


class BillAndDataInput:
    """ Input and Display bill data and other relevant data

    Attributes:
        see init function docstring
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

    def do_simple_bill_process(self):
        """ Run process to input or read simple bill data and store data to table

        Returns:
            list[SimpleServiceBillData]: there may be other bill data instances that have the same real estate, provider
                and start date so a list is used
        """
        opt = self.simple_view.input_choose_input_data_or_read_bill()
        if opt == "1":
            re_dict = self.simple_model.read_all_real_estate()
            sp_dict = self.simple_model.read_valid_service_providers()
            bill_data = self.simple_view.input_bill_data(re_dict, sp_dict,
                                                         self.simple_model.set_default_tax_related_cost)
            filename = self.simple_model.save_to_file(bill_data)
        else:  # opt == "2"
            filename = self.simple_view.input_read_new_bill()

        bill_data = self.simple_model.process_service_bill(filename)
        self.simple_model.insert_service_bills_to_db([bill_data])
        bill_list = self.simple_model.read_service_bill_from_db_by_repsd(
            bill_data.real_estate, bill_data.service_provider, bill_data.start_date)

        self.simple_model.clear_model()

        return bill_list

    def do_solar_bill_process(self):
        """ Run process to input data for solar bills and solar kwh usage

        Returns:
            list[SolarBillData]: list with instance of bill data. there may be other bill data instances that
                have the same real estate, service provider and start date
        """
        self.solar_view.display_bill_preprocess_warning()
        bill_filename = self.solar_view.input_read_new_bill()
        start_date, end_date, df = self.solar_model.process_service_bill_dates(bill_filename)
        opt = self.solar_view.input_read_new_hourly_data_file_or_skip(start_date, end_date)
        if opt == "1":
            hourly_filename = self.solar_view.input_read_new_hourly_data_file(start_date, end_date)
            df = self.solar_model.process_sunpower_hourly_file(hourly_filename)
            self.solar_model.insert_sunpower_hourly_data_to_db(df)
        bill_data = self.solar_model.process_service_bill(bill_filename)
        bill_trc_list = self.solar_view.input_tax_related_cost([bill_data])
        bill_data = self.solar_model.set_default_tax_related_cost(bill_trc_list)[0]
        self.solar_model.insert_service_bills_to_db([bill_data])

        bill_list = self.solar_model.read_service_bill_from_db_by_repsd(
            bill_data.real_estate, bill_data.service_provider, bill_data.start_date)

        self.solar_model.clear_model()

        return bill_list

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
            bill_trc_list = view.input_tax_related_cost([bill_data])
            bill_data = model.set_default_tax_related_cost(bill_trc_list)[0]
            model.insert_service_bills_to_db([bill_data])
            real_estate = bill_data.real_estate
            service_provider = bill_data.service_provider
            start_date = bill_data.start_date
        else:
            re_dict = model.read_all_real_estate()
            re_id = view.input_select_real_estate(re_dict)
            real_estate = re_dict[re_id]
            sp_dict = model.read_valid_service_providers()
            sp_id = view.input_select_service_provider(sp_dict)
            service_provider = sp_dict[sp_id]
            start_date = view.input_bill_date()

        bill_data = model.read_service_bill_from_db_by_repsd(real_estate, service_provider, start_date)
        # only one bill will match
        return bill_data[0]

    def input_or_load_utility_data(self, real_estate, service_provider, date, model, view):
        """ Input utility data and store to db or load from db

        Args:
            real_estate (RealEstate): bill for this real estate
            service_provider (ServiceProvider): utility provider
            date (datetime.date): run function for utility data for this month and year (day is ignored)
            model (ComplexServiceModelBase): subclass
            view (ComplexServiceViewBase): subclass

        Returns:
            UtilityDataBase: subclass instance of utility data
        """
        month_year = date.strftime("%m%Y")
        utility_data = model.read_monthly_data_from_db_by_month_year(month_year)

        if utility_data is None:
            notes_list = model.read_all_estimate_notes_by_reid_provider(real_estate, service_provider)
            view.display_utility_data_found_or_not(False, month_year)
            el_dict = view.input_values_for_notes(notes_list)
            el_dict.update({"real_estate": real_estate, "service_provider": service_provider, "month_date": date,
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
            ElectricBillData: instance of estimated monthly bill with real_estate, service provider, start_date,
            end_date, total_kwh, eh_kwh set
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

        ed_sm = self.input_or_load_utility_data(amb.real_estate, amb.service_provider, amb.start_date, self.pseg_model,
                                                self.pseg_view)
        ed_em = self.input_or_load_utility_data(amb.real_estate, amb.service_provider, amb.end_date, self.pseg_model,
                                                self.pseg_view)

        # gather estimation data available elsewhere and enter estimation data otherwise not available
        emb = self.input_and_load_electric_estimation_data(amb.real_estate.address, amb.start_date, amb.end_date)

        # do bill estimate calculation
        emb = self.pseg_model.do_estimate_monthly_bill(amb.real_estate.address, amb.start_date, amb.end_date)
        self.pseg_model.insert_service_bills_to_db([emb])

        self.pseg_model.clear_model()

    def input_and_load_natgas_estimation_data(self, address, start_date, end_date):
        """ Load natural gas estimation data already available and input any missing data

        Args:
            address (Address): bill for this real estate
            start_date (datetime.date): start date of an actual bill. will be the start date of the estimated bill
            end_date (datetime.date): end date of an actual bill. will be the end date of the estimated bill

        Returns:
            NatGasBillData: instance of estimated monthly bill with real_estate, service_provider, start_date, end_date,
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
        ngd_sm = self.input_or_load_utility_data(amb.real_estate, amb.service_provider, amb.start_date, self.ng_model,
                                                 self.ng_view)
        ngd_em = self.input_or_load_utility_data(amb.real_estate, amb.service_provider, amb.end_date, self.ng_model,
                                                 self.ng_view)

        # gather estimation data available elsewhere and enter estimation data otherwise not available
        emb = self.input_and_load_natgas_estimation_data(amb.real_estate.address, amb.start_date, amb.end_date)

        # do bill estimate calculation
        emb = self.ng_model.do_estimate_monthly_bill(amb.real_estate.address, amb.start_date, amb.end_date)
        self.ng_model.insert_service_bills_to_db([emb])

        self.ng_model.clear_model()

    def do_mortgage_bill_process(self):
        """ Run process to read mortgage bills and store data to table

        Returns:
            list[MortgageBillData]: there may be other bill data instances that have the same real estate, provider and
                start date so a list is used
        """
        filename = self.mortgage_view.input_read_new_bill()
        bill_data = self.mortgage_model.process_service_bill(filename)
        bill_trc_list = self.mortgage_view.input_tax_related_cost([bill_data])
        bill_data = self.mortgage_model.set_default_tax_related_cost(bill_trc_list)[0]
        self.mortgage_model.insert_service_bills_to_db([bill_data])
        bill_list = self.mortgage_model.read_service_bill_from_db_by_repsd(
            bill_data.real_estate, bill_data.service_provider, bill_data.start_date)

        self.mortgage_model.clear_model()

        return bill_list

    def do_paid_date_process(self):
        """ Run process to input paid date for any bills missing a paid date """

        while True:
            try:
                print("######################################################################")
                print("Choose a bill option from the following:\n")
                print("1: Simple Bill Paid Dates")
                print("2: Solar Bill Paid Dates")
                print("3: Electric Bill Paid Dates")
                print("4: Natural Gas Bill Paid Dates")
                print("5: Mortgage Bill Paid Dates")
                print("6: Depreciation Bill Paid Dates")
                print("0: Return to Previous Menu")
                opt = input("\nSelection: ")

                if opt in ["1", "2", "3", "4", "5", "6"]:
                    if opt == "1":
                        (model, view) = (self.simple_model, self.simple_view)
                    elif opt == "2":
                        (model, view) = (self.solar_model, self.solar_view)
                    elif opt == "3":
                        (model, view) = (self.pseg_model, self.pseg_view)
                    elif opt == "4":
                        (model, view) = (self.ng_model, self.ng_view)
                    elif opt == "5":
                        (model, view) = (self.mortgage_model, self.mortgage_view)
                    else:  # opt == "6":
                        (model, view) = (self.dep_model, self.dep_view)

                    unpaid_bill_list = model.read_all_service_bills_from_db_unpaid()
                    if len(unpaid_bill_list) > 0:
                        unpaid_bill_list = view.input_paid_dates(unpaid_bill_list)
                        model.update_service_bills_in_db_paid_date_by_id(unpaid_bill_list)
                    else:
                        print("No unpaid bills")
                    model.clear_model()
                elif opt == "0":
                    break
                else:
                    print(opt + " is not a valid option. Try again.")
            except Exception as ex:
                print(colorama.Fore.RED, str(ex))
                print(colorama.Style.RESET_ALL)

    def do_depreciation_bill_process(self):
        """ Run process to create depreciation bills and store data to table

        Returns:
            list[DepreciationBillData]: all bills created by this process
        """
        # get real estate
        re_dict = self.dep_model.read_all_real_estate()
        re_id = self.dep_view.input_select_real_estate(re_dict)
        real_estate = re_dict[re_id]

        # get service provider
        sp_dict = self.dep_model.read_valid_service_providers()
        sp_id = self.dep_view.input_select_service_provider(sp_dict)
        service_provider = sp_dict[sp_id]

        # get year
        year = self.dep_view.input_depreciation_year()

        # create bills for depreciable items and make a list of non depreciable items. period usage considered later
        bill_list, rpv_list = self.dep_model.create_bills(real_estate, service_provider, year)

        bill_trc_list = self.dep_view.input_tax_related_cost(bill_list)
        bill_list = self.dep_model.set_default_tax_related_cost(bill_trc_list)

        # enter period usage for each depreciable item
        bill_list = self.dep_view.input_period_usages(bill_list)

        # apply period usage to bills
        self.dep_model.apply_period_usage_to_bills(bill_list)

        # store to table
        self.dep_model.insert_service_bills_to_db(bill_list)

        print("\n**** Depreciation Bill Report ****")
        print("\n**** Depreciable Bills Created and Stored ****")
        self.dep_view.display_bills(bill_list)
        print("\n**** Non-Depreciable Items ****")
        for rpv in rpv_list:
            print("\n\n" + str(rpv))

        self.dep_model.clear_model()

        return bill_list

    def do_partial_bill_process(self):
        """ Run process to create new bill(s) as a portion of existing bill(s) """

        while True:
            try:
                print("######################################################################")
                print("Choose a bill option from the following:\n")
                print("1: Simple Bill Partials")
                print("2: Solar Bill Partials")
                print("3: Electric Bill Partials")
                print("4: Natural Gas Bill Partials")
                print("5: Mortgage Bill Partials")
                print("6: Depreciation Bill Partials")
                print("0: Return to Previous Menu")
                opt = input("\nSelection: ")

                if opt in ["1", "2", "3", "4", "5", "6"]:
                    if opt == "1":
                        (model, view) = (self.simple_model, self.simple_view)
                    elif opt == "2":
                        (model, view) = (self.solar_model, self.solar_view)
                    elif opt == "3":
                        (model, view) = (self.pseg_model, self.pseg_view)
                    elif opt == "4":
                        (model, view) = (self.ng_model, self.ng_view)
                    elif opt == "5":
                        (model, view) = (self.mortgage_model, self.mortgage_view)
                    else:  # opt == "6":
                        (model, view) = (self.dep_model, self.dep_view)

                    re_dict = model.read_all_real_estate()
                    sp_dict = model.read_valid_service_providers()

                    re_id = view.input_select_real_estate(re_dict, pre_str="Load bills for this real estate. ")
                    primary_real_estate = re_dict[re_id]

                    re_id = view.input_select_real_estate(re_dict,
                                                          pre_str="Create partial bills for this real estate. ")
                    secondary_real_estate = re_dict[re_id]

                    sp_id = view.input_select_service_provider(sp_dict,
                                                       pre_str="Load/Create partial bills for this service provider. ")
                    service_provider = sp_dict[sp_id]

                    year = view.input_paid_year(pre_str="\nLoad/Create partial bills for this year. ")

                    orig_bill_list = model.read_service_bills_from_db_by_resppdr(
                        real_estate_list=[primary_real_estate], service_provider_list=[service_provider],
                        paid_date_min=datetime.date(year, 1, 1), paid_date_max=datetime.date(year, 12, 31))
                    bill_ratio_list = view.input_partial_bill_portion(orig_bill_list)
                    new_bill_list = [bill.copy(cost_ratio=ratio, real_estate=secondary_real_estate)
                                     for bill, ratio in bill_ratio_list if not ratio.is_nan()]

                    bill_tax_related_cost_list = view.input_tax_related_cost(new_bill_list)
                    new_bill_list = model.set_default_tax_related_cost(bill_tax_related_cost_list)

                    model.insert_service_bills_to_db(new_bill_list, ignore=True)

                    model.clear_model()
                elif opt == "0":
                    break
                else:
                    print(opt + " is not a valid option. Try again.")
            except Exception as ex:
                print(colorama.Fore.RED, str(ex))
                print(colorama.Style.RESET_ALL)

    def do_input_or_create_bill_process(self):
        """ Select and run bill or data input or create process through console """

        while True:
            try:
                print("\n######################################################################")
                print("Choose a bill or data input or create option from the following:\n")
                print("1: Input Simple Bill")
                print("2: Input Solar Bill")
                print("3: Input Electric Bill and Related Data")
                print("4: Input Natural Gas Bill and Related Data")
                print("5: Input Mortgage Bill")
                print("6: Input Missing Paid Dates")
                print("7: Create Depreciation Bill(s)")
                print("8: Create Partial Bill(s)")
                print("0: Return to Previous Menu")
                opt = input("\nSelection: ")

                if opt == "1":
                    self.do_simple_bill_process()
                elif opt == "2":
                    self.do_solar_bill_process()
                elif opt == "3":
                    self.do_electric_process()
                elif opt == "4":
                    self.do_natgas_process()
                elif opt == "5":
                    self.do_mortgage_bill_process()
                elif opt == "6":
                    self.do_paid_date_process()
                elif opt == "7":
                    self.do_depreciation_bill_process()
                elif opt == "8":
                    self.do_partial_bill_process()
                elif opt == "0":
                    break
                else:
                    print(opt + " is not a valid option. Try again.")
            except Exception as ex:
                print(colorama.Fore.RED, str(ex))
                print(colorama.Style.RESET_ALL)