from Database.POPO.ServiceProvider import ServiceProvider
from Services.Electric.View.PSEGViewBase import PSEGViewBase


class PSEGConsoleUI(PSEGViewBase):
    """ Implementation of PSEGViewBase for use with PSEG Console UI """

    def __init__(self):
        """ init function """
        super().__init__()

    @staticmethod
    def input_read_new_or_use_existing_bill_option():
        opt = input("\nEnter '1' to read new electric bill or anything else to use existing electric bill: ")

        return opt

    @staticmethod
    def input_read_new_bill():
        print("\nSave electric bill to Services -> Electric -> PSEGFiles directory.")
        filename = input("Enter electric bill file name (include extension): ")

        return filename

    @staticmethod
    def display_utility_data_found_or_not(found, month_year):
        print("\n" + ("" if found else "No ") + "Electric data found for month-year: " + month_year + ".")

    @staticmethod
    def input_values_for_notes(notes_list):
        el_dict = {}
        for d in notes_list:
            note_type = d["note_type"]
            print("\n" + note_type + "\n" + d["note"])
            inp = input("Input value for " + note_type + ": ")
            el_dict[note_type] = inp

        return el_dict

    @staticmethod
    def input_estimation_data(address, start_date, end_date):
        print("Input estimation data for " + str(ServiceProvider.PSEG.value) + " electric bill at "
              + str(address.value) + " with start date - end date: " + str(start_date) + " - " + str(end_date))
        eh_kwh = input("Electric heater kwh usage: ")
        return {"eh_kwh": int(eh_kwh)}

