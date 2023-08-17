import os
from Database.POPO.ServiceProvider import ServiceProviderEnum
from Services.NatGas.View.NGViewBase import NGViewBase
from Services.View.ComplexConsoleUIBase import ComplexConsoleUIBase
from Util.ConsoleUtil import print, input


class NGConsoleUI(ComplexConsoleUIBase, NGViewBase):
    """ Implementation of NGViewBase for use with NationalGrid Console UI """

    def __init__(self):
        """ init function """
        super().__init__()

    def input_read_new_or_use_existing_bill_option(self):
        return input("\nEnter '1' to read new natural gas bill or anything else to use existing natural gas bill: ",
                     fcolor="blue")

    def input_read_new_bill(self):
        print("\nSave natural gas bill to " + str(os.getenv("FI_NATIONALGRID_DIR")) + " directory.")

        return input("Enter natural gas bill file name (include extension): ", fcolor="blue")

    def input_tax_related_cost(self, bill_list):
        return self.input_tax_related_cost_helper(bill_list, "Natural Gas", "total", "0")

    def display_bills(self, bill_list):
        print("\n********** Natural Gas Bills **********\n")
        for i, bill in enumerate(bill_list):
            print("__________ Natural Gas Bill #" + str(i+1) + " __________")
            self.display_bill(bill)
            print("\n")

    def display_utility_data_found_or_not(self, found, month_year):
        print("\n" + ("" if found else "No ") + "Natural gas data found for month-year: " + month_year + ".")

    def input_estimation_data(self, address, start_date, end_date):
        print("Input estimation data for " + str(ServiceProviderEnum.NG_UTI.value) + " natural gas bill at "
              + str(address.value) + " with start date - end date: " + str(start_date) + " - " + str(end_date))
        saved_therms = input("Natural gas saved therms: ", fcolor="blue")
        return {"saved_therms": int(saved_therms)}