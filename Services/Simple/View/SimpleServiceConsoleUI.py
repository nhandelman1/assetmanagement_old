from Services.Simple.View.SimpleViewBase import SimpleViewBase


class SimpleServiceConsoleUI(SimpleViewBase):
    """ Implementation of SimpleServiceViewBase for use with simple service console UI """

    def __init__(self):
        super().__init__()

    @staticmethod
    def input_read_new_bill():
        print("\nGo to Services -> Simple -> SimpleFiles directory and use template file to create a new simple bill "
              "using actual bill. Save file in the same directory.")
        filename = input("Enter simple service bill file name (include extension): ")

        return filename