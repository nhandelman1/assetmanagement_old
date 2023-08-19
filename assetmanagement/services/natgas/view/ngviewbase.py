from abc import abstractmethod

from ...view.complexserviceviewbase import ComplexServiceViewBase
from assetmanagement.database.popo.realestate import Address


class NGViewBase(ComplexServiceViewBase):
    """ Abstract base view class for NationalGrid data display and input """

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()

    def display_bill_preprocess_warning(self):
        pass

    @abstractmethod
    def input_estimation_data(self, address, start_date, end_date):
        """ Input estimation data that isn't available elsewhere for natural gas bill estimation

        Args:
            address (Address): address of estimation data
            start_date (datetime.date): start date for estimation data
            end_date (datetime.date): end date for estimation data

        Returns:
            dict: with keys "saved_therms"
        """
        raise NotImplementedError("input_estimation_data() not implemented by subclass")