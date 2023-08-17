import datetime
import textwrap
from enum import Enum
from typing import Union
from Database.POPO.RealEstate import RealEstate
from Database.POPO.ServiceProvider import ServiceProvider, ServiceProviderEnum
from Services.Depreciation.Model.DepreciationModel import DepreciationModel
from Services.Depreciation.View.DepreciationViewBase import DepreciationViewBase
from Services.Electric.Model.PSEG import PSEG
from Services.Electric.Model.Solar import Solar
from Services.Electric.View.PSEGViewBase import PSEGViewBase
from Services.Electric.View.SolarViewBase import SolarViewBase
from Services.Model.SimpleServiceModelBase import SimpleServiceModelBase
from Services.Mortgage.Model.MS import MS
from Services.Mortgage.View.MortgageViewBase import MortgageViewBase
from Services.NatGas.Model.NG import NG
from Services.NatGas.View.NGViewBase import NGViewBase
from Services.Simple.Model.SimpleServiceModel import SimpleServiceModel
from Services.Simple.View.SimpleViewBase import SimpleViewBase
from Util.ConsoleUtil import print, input


class BillType(Enum):
    """ Do not use 0 for any enum value """
    DEPRECIATION = "DEPRECIATION"
    ELECTRIC_SOLAR = "ELECTRIC_SOLAR"
    ELECTRIC_UTILITY = "ELECTRIC_UTILITY"
    MORTGAGE = "MORTGAGE"
    NATURAL_GAS = "NATURAL_GAS"
    SIMPLE = "SIMPLE"


class BillAndDataDisplay:
    """ Display bill data and other relevant data by selected parameters

    Attributes:
        real_estate_set (set[RealEstate]): display bills with these real estate(s)
        bt_sp_set_dict (dict[DisplayParams.BillType, set[ServiceProvider]]): display bills for these service
            provider(s). map service provider to the bill type (i.e. model)
        minimum_paid_date (Union[datetime.date, None]): display bills with paid date greater than or equal to this date.
            None for no minimum paid date.
        maximum_paid_date (Union[datetime.date, None]): display bills with paid date less than or equal to this date.
            None for no maximum paid date.
        bt_model_dict (dict[DisplayParams.BillType, SimpleServiceModelBase]): map bill type to the model it represents
        sp_enum_bt_dict (dict[ServiceProviderEnum, DisplayParams.BillType]): map service provider to the bill type with
            which it is associated
        re_dict (dict[int, RealEstate]): map of real estate id to a RealEstate instance with that id
        bt_sp_dict_dict (dict[DisplayParams.BillType, dict[int, ServiceProvider]]): map of bill type to dict of service
            provider id to service provider. each dict holds service providers associated with bill type. this dict
            holds all bill types and all of their associated service providers
        sp_all_dict (dict[int, ServiceProvider]): map of service provider id to service provider. this dict holds all
            service providers
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

        Raises:
            AssertionError: if an enum in BillType is not matched with a model passed as an arg
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

        self.real_estate_set = None
        self.bt_sp_set_dict = None
        self.minimum_paid_date = None
        self.maximum_paid_date = None

        BT = BillType
        self.bt_model_dict = {BT.DEPRECIATION: dep_model, BT.ELECTRIC_SOLAR: solar_model,
                              BT.ELECTRIC_UTILITY: pseg_model, BT.MORTGAGE: mortgage_model, BT.NATURAL_GAS: ng_model,
                              BT.SIMPLE: simple_model}
        self.bt_view_dict = {BT.DEPRECIATION: dep_view, BT.ELECTRIC_SOLAR: solar_view, BT.ELECTRIC_UTILITY: pseg_view,
                             BT.MORTGAGE: mortgage_view, BT.NATURAL_GAS: ng_view, BT.SIMPLE: simple_view}
        assert (len(self.bt_model_dict) == len(BillType))
        self.sp_enum_bt_dict = {sp: bt for bt, model in self.bt_model_dict.items() for sp in model.valid_providers()}

        self.re_dict = simple_model.read_all_real_estate()

        self.bt_sp_dict_dict = {}
        self.sp_all_dict = {}
        for bt, model in self.bt_model_dict.items():
            self.bt_sp_dict_dict[bt] = model.read_valid_service_providers()
            self.sp_all_dict.update(self.bt_sp_dict_dict[bt])

        self.reset_params()

    def __str__(self):
        """ __str__ override

        Format:
        Real Estates:
          str(RealEstate) from self.real_estate_set with 1 RealEstate per line
        Service Providers:
          str(BillType) from self.bt_sp_set_dict keys() each with 2 space indent
            str(ServiceProvider) from self.bt_sp_set_dict values() with 4 space indent, with 1 ServiceProvider per line
        Minimum Paid Date: str(self.minimum_paid_date)
        Maximum Paid Date: str(self.maximum_paid_date)

        Returns:
            str: as described in Format
        """
        s = "Real Estates:\n"
        for re in self.real_estate_set:
            s += ("  " + str(re) + "\n")
        s += "Service Providers:\n"
        for bt, sp_set in self.bt_sp_set_dict.items():
            s += ("  " + str(bt.value) + ":\n")
            for sp in sp_set:
                s += ("    " + str(sp) + "\n")
        s += ("Minimum Paid Date: " + str(self.minimum_paid_date) + "\n")
        s += ("Maximum Paid Date: " + str(self.maximum_paid_date))

        return s

    def reset_params(self):
        """ Reset display parameters to initial state """
        self.real_estate_set = set()
        self.bt_sp_set_dict = {bill_type: set() for bill_type in BillType}
        self.minimum_paid_date = None
        self.maximum_paid_date = None

    def add_real_estate(self, re_id):
        """ Add real estate to self.real_estate_set

        Args:
            re_id (int): id associated with a RealEstate instance

        Raises:
             KeyError: if re_id does not match a RealEstate instance
        """
        self.real_estate_set.add(self.re_dict[re_id])

    def update_selected_service_providers(self, selection):
        """ Update self.bt_sp_set_dict with service providers indicated by selection

        Args:
            selection (str): possible value that indicates service provider(s) to add to display parameters. Valid
                values are BillType enum values or numbers that are the id of a ServiceProvider instance

        Returns:
            boolean: False for invalid selection, True for valid selection
        """
        valid = False
        try:
            bill_type = BillType(selection.upper())
            selected_service_providers = list(self.bt_sp_dict_dict[bill_type].values())
            self.bt_sp_set_dict[bill_type].update(selected_service_providers)
            valid = True
        except ValueError:
            # selection does not match a BillType enum value
            pass

        if valid is False:
            try:
                service_provider = self.sp_all_dict[int(selection)]
                bill_type = self.sp_enum_bt_dict[service_provider.provider]
                self.bt_sp_set_dict[bill_type].add(service_provider)
                valid = True
            except (ValueError, KeyError):
                # selection is not an int or selection is an id not associated with a service provider
                pass

        return valid

    def input_service_providers(self):
        """ Select service providers

        Add selected service providers to self.bt_sp_set_dict in this function
        """
        print_str = textwrap.fill("Service providers are ordered by provider type. Enter one of the following: a "
                                  "number to select a specific service provider, provider type to select all service "
                                  "providers for that type or 0 to return to parameter select menu.\n", width=150)
        for bt, sp_dict in self.bt_sp_dict_dict.items():
            print_str += ("\n" + bt.value + "\n")
            for sp_id, service_provider in sp_dict.items():
                print_str += ("  " + str(sp_id) + ": " + str(service_provider.provider.value) + "\n")
        print_str = "\n" + print_str + "\n0: Return to Parameter Select Menu"

        while True:
            print(print_str)
            selection = input("Selection: ", fcolor="blue")

            if selection == "0":
                break

            valid_selection = self.update_selected_service_providers(selection)

            if not valid_selection:
                print("Invalid selection. Press any key to try again.", fcolor="red")
                input()

    def input_bill_range_paid_date(self, is_min=True):
        """ ask for user to input minimum or maximum range paid date

        Set self.minimum_paid_date (is_min) or self.maximum_paid_date (not is_min) in this function

        Args:
            is_min (boolean): True to ask for minimum paid date. False to ask for maximum paid date. Default True
        """
        start_or_end = "minimum" if is_min else "maximum"
        while True:
            date = input("\nEnter " + start_or_end + " range paid date (YYYYMMDD, do not include quotes): ",
                         fcolor="blue")

            try:
                date = datetime.datetime.strptime(date, "%Y%m%d").date()
                break
            except ValueError:
                print("Invalid date format. Try again.", fcolor="red")

        if is_min:
            self.minimum_paid_date = date
        else:
            self.maximum_paid_date = date

    def display_bills_matching_parameters(self):
        """ Display bills matching parameters

        Bills will be displayed only for bill types that have at least one service provider selected
        """
        re_list = list(self.real_estate_set)
        for bt, sp_set in self.bt_sp_set_dict.items():
            if len(sp_set) > 0:
                model, view = self.bt_model_dict[bt], self.bt_view_dict[bt]
                bill_list = model.read_service_bills_from_db_by_resppdr(re_list, list(sp_set), self.minimum_paid_date,
                                                                        self.maximum_paid_date)
                view.display_bills(bill_list)

    def do_display_process(self):
        """ Select bill parameters and display matching bills """

        print_str = "\n###################################################################### " \
                    "\nBills will be displayed only for bill types that have at least one service provider selected. " \
                    "\nEnter parameters then select '9' to display matching bills:\n" \
                    "\n1: Select Real Estate(s)" \
                    "\n2: Select Service Provider(s)" \
                    "\n3: Enter Minimum Paid Date" \
                    "\n4: Enter Maximum Paid Date" \
                    "\n9: Display Bills Matching Parameters" \
                    "\n10: Clear Parameters" \
                    "\n11: Show Parameters" \
                    "\n0: Return to Previous Menu"

        while True:
            try:
                print(print_str)
                opt = input("\nSelection: ", fcolor="blue")

                if opt == "1":
                    while True:
                        re_id = self.simple_view.input_select_real_estate(self.re_dict)
                        self.add_real_estate(re_id)
                        cont = input("Enter any value to add another real estate. No value to return to parameter "
                                     "select menu: ", fcolor="blue")
                        if cont == "":
                            break
                elif opt == "2":
                    self.input_service_providers()
                elif opt == "3":
                    self.input_bill_range_paid_date(is_min=True)
                elif opt == "4":
                    self.input_bill_range_paid_date(is_min=False)
                elif opt == "9":
                    self.display_bills_matching_parameters()
                elif opt == "10":
                    self.reset_params()
                elif opt == "11":
                    print(str(self))
                elif opt == "0":
                    break
                else:
                    print(opt + " is not a valid option. Try again.", fcolor="red")
            except Exception as ex:
                print(str(ex), fcolor="red")