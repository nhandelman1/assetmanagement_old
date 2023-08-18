from abc import abstractmethod
from decimal import Decimal
from typing import Callable
from database.popo.simpleservicebilldata import SimpleServiceBillData
from services.view.simpleserviceviewbase import SimpleServiceViewBase


class SimpleViewBase(SimpleServiceViewBase):

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()

    def display_bill_preprocess_warning(self):
        pass

    @abstractmethod
    def input_bill_data(self, re_dict, sp_dict,
                        set_default_tax_related_cost_func:
                        Callable[[list[tuple[SimpleServiceBillData, Decimal]]], list[SimpleServiceBillData]]):
        """ ask to input bill data

        Args:
            re_dict (dict): dict of int real estate ids (keys) to RealEstate (values)
            sp_dict (dict): dict of int service provider ids (keys) to ServiceProvider (values)
            set_default_tax_related_cost_func: should be SimpleServiceModel.set_default_tax_related_cost
                
        Returns:
            SimpleServiceBillData: new instance populated with input data
        """
        raise NotImplementedError("input_bill_data() not implemented by subclass")