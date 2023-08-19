import os

from ...view.simpleconsoleuibase import SimpleConsoleUIBase
from .solarviewbase import SolarViewBase
from assetmanagement.util.consoleutil import print, input


class SolarConsoleUI(SimpleConsoleUIBase, SolarViewBase):
    """ Implementation of SolarBase for use with Console UI """

    def __init__(self):
        """ init function """
        super().__init__()

    def display_bill_preprocess_warning(self):
        print("\nConsider if solar bill start and end dates should match with electric bill start and end dates for "
              "the associated property. Since there isn't really a 'bill' for solar, solar usage is typically compared "
              "to electric utility usage over a certain period.", fcolor="red")

    def input_read_new_bill(self):
        print("\nGo to " + str(os.getenv("FI_SUNPOWER_DIR")) + " directory and use template file to create a new solar "
              "bill. Save file in the same directory.")

        return input("Enter solar bill file name (include extension): ", fcolor="blue")

    def display_bills(self, bill_list):
        print("\n********** Solar Bills **********\n")
        for i, bill in enumerate(bill_list):
            print("__________ Solar Bill #" + str(i+1) + " __________")
            self.display_bill(bill)
            print("\n")

    def input_read_new_hourly_data_file_or_skip(self, start_date, end_date):
        return input("\nEnter '1' to read sunpower hourly file with data from " + str(start_date) + " through " +
                     str(end_date) + " (inclusive). Anything else to skip (data in file already inserted to table): ",
                     fcolor="blue")

    def input_read_new_hourly_data_file(self, start_date, end_date):
        print("\nGet sunpower hourly data file with data from " + str(start_date) + " through "
              + str(end_date) + "\nSave file to " + str(os.getenv("FI_SUNPOWER_DIR")) + " directory.\n")

        return input("Enter filename: ", fcolor="blue")