from abc import abstractmethod
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class MortgageViewBase(SimpleServiceViewBase):

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()

    def display_bill_preprocess_warning(self):
        pass

    def input_choose_input_data_or_read_bill(self):
        return "2"