from abc import ABC, abstractmethod


class SimpleServiceViewBase(ABC):
    """ Abstract base view class for service data display and input """

    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def input_read_new_bill():
        """ ask for new file name

        Returns:
            str: name of file to read
        """
        raise NotImplementedError("input_read_new_bill() not implemented by subclass")