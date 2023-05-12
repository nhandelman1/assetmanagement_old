from Utilities.Electric.View.SolarViewBase import SolarViewBase


class SolarConsoleUI(SolarViewBase):
    """ Implementation of SolarBase for use with Console UI """

    def __init__(self):
        super().__init__()

    @staticmethod
    def input_read_new_or_skip(start_date, end_date):
        opt = input("\nEnter '1' to read sunpower hourly file with data from " + str(start_date) + " through "
                    + str(end_date) + ". Anything else to skip (data in file already inserted to table): ")

        return opt

    @staticmethod
    def input_read_new_hourly_data_file(start_date, end_date):
        print("\nGet sunpower hourly data file with data from " + str(start_date) + " through "
              + str(end_date))
        print("Save file to Utilities -> Electric -> MySunpowerFiles directory.")
        filename = input("Enter filename: ")

        return filename