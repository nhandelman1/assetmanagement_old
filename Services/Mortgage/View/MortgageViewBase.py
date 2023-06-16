from abc import abstractmethod
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase


class MortgageViewBase(SimpleServiceViewBase):

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()
