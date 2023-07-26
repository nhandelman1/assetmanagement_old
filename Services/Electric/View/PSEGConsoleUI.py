import os
from Services.View.ComplexConsoleUIBase import ComplexConsoleUIBase
from Services.Electric.View.PSEGViewBase import PSEGViewBase
from Database.POPO.ServiceProvider import ServiceProviderEnum


class PSEGConsoleUI(ComplexConsoleUIBase, PSEGViewBase):
    """ Implementation of PSEGViewBase for use with PSEG Console UI """

    def __init__(self):
        """ init function """
        super().__init__()

    def input_read_new_or_use_existing_bill_option(self):
        opt = input("\nEnter '1' to read new electric bill or anything else to use existing electric bill: ")

        return opt

    def input_read_new_bill(self):
        print("\nSave electric bill to " + str(os.getenv("FI_PSEG_DIR")) + " directory.")
        filename = input("Enter electric bill file name (include extension): ")

        return filename

    def display_bills(self, bill_list):
        print("\n********** Electric Bills **********\n")
        for i, bill in enumerate(bill_list):
            print("__________ Electric Bill #" + str(i+1) + " __________")
            self.display_bill(bill)
            print("\n")

    def display_utility_data_found_or_not(self, found, month_year):
        print("\n" + ("" if found else "No ") + "Electric data found for month-year: " + month_year + ".")

    def input_estimation_data(self, address, start_date, end_date):
        print("Input estimation data for " + str(ServiceProviderEnum.PSEG_UTI.value) + " electric bill at "
              + str(address.value) + " with start date - end date: " + str(start_date) + " - " + str(end_date))
        eh_kwh = input("Electric heater kwh usage: ")
        return {"eh_kwh": int(eh_kwh)}