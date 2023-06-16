from abc import abstractmethod
from Database.POPO.RealEstate import Address
from Services.View.ComplexServiceViewBase import ComplexServiceViewBase


class PSEGViewBase(ComplexServiceViewBase):
    """ Abstract base view class for PSEG data display and input """

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()

    @abstractmethod
    def input_estimation_data(self, address, start_date, end_date):
        """ Input estimation data that isn't available elsewhere for electric bill estimation

        Args:
            address (Address): address of estimation data
            start_date (datetime.date): start date for estimation data
            end_date (datetime.date): end date for estimation data

        Returns:
            dict: with keys "eh_kwh"
        """
        raise NotImplementedError("input_estimation_data() not implemented by subclass")