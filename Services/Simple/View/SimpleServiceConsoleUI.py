import colorama
import decimal
import os
from Services.View.SimpleConsoleUIBase import SimpleConsoleUIBase
from Services.Simple.View.SimpleViewBase import SimpleViewBase
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData


class SimpleServiceConsoleUI(SimpleConsoleUIBase, SimpleViewBase):
    """ Implementation of SimpleServiceViewBase for use with simple service console UI """

    def __init__(self):
        super().__init__()

    def input_read_new_bill(self):
        print("\nGo to " + str(os.getenv("FI_SIMPLE_DIR")) + " directory and use template file to create a new simple "
              "bill using actual bill. Save file in the same directory.")
        filename = input("Enter simple service bill file name (include extension): ")

        return filename

    def input_choose_input_data_or_read_bill(self):
        while True:
            opt = input("\nEnter '1' to input bill data manually or '2' to read data from file: ")

            if opt not in ["1", "2"]:
                print(colorama.Fore.RED, opt + " is not a valid option. Try again.")
                print(colorama.Style.RESET_ALL)
            else:
                break

        return opt

    def input_bill_data(self, re_dict, sp_dict):
        re_id = self.input_select_real_estate(re_dict)
        sp_id = self.input_select_service_provider(sp_dict)
        start_date = self.input_bill_date()
        end_date = self.input_bill_date(is_start=False)

        while True:
            total_cost = input("\nEnter total cost (income, credit, rebates, etc. are negative) (*.XX format): ")

            try:
                decimal.Decimal(total_cost)
            except decimal.InvalidOperation:
                print(colorama.Fore.RED, "Invalid format. Try again.")
                print(colorama.Style.RESET_ALL)
                continue

            tc_split = total_cost.split(".")
            if len(tc_split) != 2 or len(tc_split[1]) != 2:
                print(colorama.Fore.RED, "Must have 2 decimal places. Try again.")
                print(colorama.Style.RESET_ALL)
                continue

            break

        notes = input("\nEnter any notes for this bill (leave blank for no notes): ")
        notes = None if notes == "" else notes

        bill = SimpleServiceBillData(re_dict[re_id], sp_dict[sp_id], start_date, end_date, decimal.Decimal(total_cost),
                                     notes=notes)

        bill_list = self.input_paid_dates([bill])

        return bill if len(bill_list) == 0 else bill_list[0]