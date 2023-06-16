import colorama
from Services.View.SimpleConsoleUIBase import SimpleConsoleUIBase
from Services.Electric.View.SolarViewBase import SolarViewBase


class SolarConsoleUI(SimpleConsoleUIBase, SolarViewBase):
    """ Implementation of SolarBase for use with Console UI """

    def __init__(self):
        """ init function """
        super().__init__()

    def display_bill_preprocess_warning(self):
        print(colorama.Fore.RED,
              "\nConsider if solar bill start and end dates should match with electric bill start and end dates for "
              "the associated property. Since there isn't really a 'bill' for solar, solar usage is typically compared "
              "to electric utility usage over a certain period.")
        print(colorama.Style.RESET_ALL)

    def input_read_new_bill(self):
        print("\nGo to Services -> Electric -> SunpowerFiles directory and use template file to create a new solar "
              "bill. Save file in the same directory.")
        filename = input("Enter solar bill file name (include extension): ")

        return filename

    def input_read_new_hourly_data_file_or_skip(self, start_date, end_date):
        opt = input("\nEnter '1' to read sunpower hourly file with data from " + str(start_date) + " through "
                    + str(end_date) + " (inclusive). Anything else to skip (data in file already inserted to table): ")

        return opt

    def input_read_new_hourly_data_file(self, start_date, end_date):
        print("\nGet sunpower hourly data file with data from " + str(start_date) + " through "
              + str(end_date))
        print("Save file to Services -> Electric -> SunpowerFiles directory.")
        filename = input("Enter filename: ")

        return filename