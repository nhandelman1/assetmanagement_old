from abc import abstractmethod
from typing import Callable
from decimal import Decimal
from Services.View.SimpleServiceViewBase import SimpleServiceViewBase
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData


class SimpleViewBase(SimpleServiceViewBase):

    @abstractmethod
    def __init__(self):
        """ init function """
        super().__init__()

    @abstractmethod
    def input_choose_input_data_or_read_bill(self):
        """ ask to input bill data manually or read data from file

        Returns:
            str: "1" to input bill data manually or "2" to read data from file
        """
        raise NotImplementedError("input_choose_input_data_or_read_bill() not implemented by subclass")

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