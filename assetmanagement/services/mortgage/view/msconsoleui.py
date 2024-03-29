import os

from ...view.simpleconsoleuibase import SimpleConsoleUIBase
from .mortgageviewbase import MortgageViewBase
from assetmanagement.util.consoleutil import print, input


class MSConsoleUI(SimpleConsoleUIBase, MortgageViewBase):
    """ Implementation of SimpleServiceViewBase for use with Morgan Stanley mortgage console UI """

    def __init__(self):
        super().__init__()

    def input_read_new_bill(self):
        print("\nSave mortgage bill to " + str(os.getenv("DI_MORGANSTANLEY_DIR")) + " directory.")

        return input("Enter mortgage bill file name (include extension): ", fcolor="blue")

    def input_tax_related_cost(self, bill_list):
        return self.input_tax_related_cost_helper(bill_list, "Mortgage", "interest payment", "0")

    def display_bills(self, bill_list):
        print("\n********** Mortgage Bills **********\n")
        for i, bill in enumerate(bill_list):
            print("__________ Mortgage Bill #" + str(i+1) + " __________")
            self.display_bill(bill)
            print("\n")