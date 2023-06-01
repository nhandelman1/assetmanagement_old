import re
from abc import abstractmethod
from Database.POPO.ServiceProvider import ServiceProvider
from Database.POPO.RealEstate import RealEstate
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class ComplexServiceViewBase(SimpleServiceViewBase):
    """ Abstract base view class for complex service data display and input """
    @abstractmethod
    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def input_read_new_or_use_existing_bill_option():
        """ ask to read new file or use existing file option

        Returns:
            str: "1" if read new bill, anything else to use existing bill
        """
        raise NotImplementedError("input_read_new_or_use_existing_bill_option() not implemented by subclass")

    def input_select_existing_bill_real_estate(self, re_dict):
        """ ask for user to select real estate from re_dict

        Args:
            re_dict (dict): dict of int real estate ids (keys) to RealEstate (values)

        Returns:
            int: real estate id
        """
        re_print = "\n"
        re_ids = list(re_dict.keys())

        for re_id, real_estate in re_dict.items():
            re_print += str(re_id) + " : " + str(real_estate.address.value) + "\n"
        re_print += "Select a real estate location from the previous list: "

        while True:
            try:
                select_id = int(input(re_print))
            except ValueError:
                select_id = None

            if select_id not in re_ids:
                print("Invalid Selection. Try Again.")
            else:
                break

        return select_id

    def input_select_existing_bill_provider(self, provider_list):
        """ ask for user to select provider from provider_list

        Args:
            provider_list (list[ServiceProvider]): list of service providers

        Returns:
            ServiceProvider: selected service provider
        """
        sp_print = "\n"

        for sp in provider_list:
            sp_print += str(sp.value) + "\n"
        sp_print += "Select a provider from the previous list: "

        while True:
            try:
                select_prov = ServiceProvider(input(sp_print))
            except ValueError:
                select_prov = None

            if select_prov not in provider_list:
                print("Invalid Selection. Try Again.")
            else:
                break

        return select_prov


    @staticmethod
    def input_read_existing_bill_start_date():
        while True:
            start_date = input("\nEnter bill start date (YYYYMMDD, do not include quotes): ")
            if re.match(pattern="^\d{8}$", string=start_date):
                break
            else:
                print("Invalid date format. Try again.")

        return start_date

    @staticmethod
    @abstractmethod
    def display_utility_data_found_or_not(found, month_year):
        """ display message that a utility's data was found or not

        Args:
            found (boolean): True if data was found, False if not.
            month_year (str): "MMYYYY" date format
        """
        raise NotImplementedError("display_data_found_or_not() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_estimation_data(address, start_date, end_date):
        """ Input estimation data that isn't available elsewhere for bill estimation

        Args:
            address (Address): address of estimation data
            start_date (datetime.date): start date for estimation data
            end_date (datetime.date): end date for estimation data

        Returns:
            dict: (see subclass for more info)
        """
        raise NotImplementedError("input_estimation_data() not implemented by subclass")

    @staticmethod
    @abstractmethod
    def input_values_for_notes(notes_list):
        """ display note_types and notes and ask for input value for each note

        Args:
            notes_list (list[dict]): each dict must have keys "note_type" and "note"

        Returns:
            dict: with each note_type as keys and input value for that note_type as values
        """
        raise NotImplementedError("input_values_for_notes() not implemented by subclass")