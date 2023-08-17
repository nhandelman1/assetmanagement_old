from abc import ABC, abstractmethod
from decimal import Decimal


class ClassConstructors(ABC):
    """ Classes that implement this class will provide class methods for instance construction """
    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    def dec_none(val):
        return None if val is None else Decimal(val)

    @classmethod
    @abstractmethod
    def default_constructor(cls):
        """ Create an instance of ClassConstructors subclass

        Instance attributes set to default values specified by subclass (usually None but not guaranteed).

        Returns:
            ClassConstructors: subclass instance with all instance attributes set to default
        """
        raise NotImplementedError("default_constructor() not implemented by subclass")

    @classmethod
    @abstractmethod
    def str_dict_constructor(cls, str_dict):
        """ Create an instance of ClassConstructors subclass with instance attributes set using str_dict values

        This function provides a default implementation that creates an instance using str_dict passed to
        ClassConstructors.db_dict_constructor(). Subclass can call this function or use its own implementation.
        Subclass is responsible for converting instance attribute (str) values to the required type

        Args:
            str_dict (dict): dict with instance variables (str keys) and str values

        Returns:
            ClassConstructors: subclass instance with all instance attributes set with str_dict and the required type
        """
        return ClassConstructors.db_dict_constructor(str_dict)

    @classmethod
    def db_dict_constructor(cls, db_dict):
        """ Create an instance of ClassConstructors subclass with instance attributes set to db_dict values

        Create instance using default_constructor() then update instance attributes with values in db_dict

        Args:
            db_dict (dict): see db_dict_update() db_dict arg

        Returns:
            ClassConstructors: subclass instance with all instance attributes set with db_dict
        """
        obj = cls.default_constructor()
        obj.db_dict_update(db_dict)
        return obj

    def db_dict_update(self, db_dict):
        """ Update instance variables using db_dict

        This function makes no changes to values in db_dict.

        Args:
            db_dict (dict): dict with instance variables (string keys) and values (datatype values)
        """
        # use this method of setting attributes instead of __dict__.update to property set private attributes
        for key, value in db_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)