import os
from decimal import Decimal
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData
from Services.Simple.View.SimpleViewBase import SimpleViewBase
from Services.View.SimpleConsoleUIBase import SimpleConsoleUIBase
from Util.ConsoleUtil import print, input


class SimpleServiceConsoleUI(SimpleConsoleUIBase, SimpleViewBase):
    """ Implementation of SimpleServiceViewBase for use with simple service console UI """

    def __init__(self):
        super().__init__()

    def input_read_new_bill(self):
        print("\nGo to " + str(os.getenv("FI_SIMPLE_DIR")) + " directory and use template file to create a new simple "
              "bill using actual bill. Save file in the same directory.")

        return input("Enter simple service bill file name (include extension): ", fcolor="blue")

    def input_tax_related_cost(self, bill_list):
        return self.input_tax_related_cost_helper(bill_list, "Simple", "total", "0")

    def input_choose_input_data_or_read_bill(self):
        while True:
            opt = input("\nEnter '1' to input bill data manually or '2' to read data from file: ", fcolor="blue")

            if opt not in ["1", "2"]:
                print(opt + " is not a valid option. Try again.", fcolor="red")
            else:
                break

        return opt

    def input_bill_data(self, re_dict, sp_dict, set_default_tax_related_cost_func):
        re_id = self.input_select_real_estate(re_dict)
        real_estate = re_dict[re_id]
        sp_id = self.input_select_service_provider(sp_dict)
        start_date = self.input_bill_date()
        end_date = self.input_bill_date(is_start=False)

        print_str = "Enter total cost (income, credit, rebates, etc. are negative)."
        total_cost = Decimal(self.input_blank_skip_or_dollar_decimal(print_str, False, False))

        bill = SimpleServiceBillData(real_estate, sp_dict[sp_id], start_date, end_date, total_cost, None)

        bill_trc_list = self.input_tax_related_cost([bill])
        bill = set_default_tax_related_cost_func(bill_trc_list)[0]

        notes = input("\nEnter any notes for this bill (leave blank for no notes): ", fcolor="blue")
        bill.notes = None if notes == "" else notes

        bill_list = self.input_paid_dates([bill])

        return bill if len(bill_list) == 0 else bill_list[0]

    def display_bills(self, bill_list):
        print("\n********** Simple Bills **********\n")
        for i, bill in enumerate(bill_list):
            print("__________ Simple Bill #" + str(i+1) + " __________")
            self.display_bill(bill)
            print("\n")