from Utilities.NatGas.View.NGViewBase import NGViewBase


class NGConsoleUI(NGViewBase):
    """ Implementation of NGViewBase for use with NationalGrid Console UI """

    def __init__(self):
        super().__init__()

    @staticmethod
    def input_read_new_or_use_existing_bill_option():
        opt = input("\nEnter '1' to read new natural gas bill or anything else to use existing natural gas bill: ")

        return opt

    @staticmethod
    def input_read_new_bill():
        print("\nSave natural gas bill to Utilities -> NatGas -> NGFiles directory.")
        filename = input("Enter natural gas bill file name (include extension): ")

        return filename

    @staticmethod
    def input_read_existing_bill_start_date():
        start_date = input("\nEnter bill start date (YYYYMMDD, do not include quotes): ")

        return start_date

    @staticmethod
    def display_utility_data_found_or_not(found, month_year):
        print("\n" + ("" if found else "No ") + "Natural gas data found for month-year: " + month_year + ".")

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
    def input_estimation_data(start_date, end_date):
        print("\nInput estimation data for natural gas bill with start date - end date: " + str(start_date) + " - "
              + str(end_date))
        saved_therms = input("Natural gas saved therms: ")
        return {"saved_therms": int(saved_therms)}

