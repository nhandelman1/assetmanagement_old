from enum import Enum


class Address(Enum):
    WAGON_LN_10 = "10 Wagon Ln Centereach NY 11720"

    @staticmethod
    def to_address(str_addr):
        """ Try to match str_val to an Address using street number, street name, apt, city, state and zip code

        Args:
            str_addr (str): string address

        Returns:
            Address that matches str_addr

        Raises:
            ValueError if no Address matches str_addr
        """
        str_addr = str_addr.lower()
        if all([x in str_addr for x in ["10", "wagon", "centereach", "ny", "11720"]] +
               [any([x in str_addr for x in ["ln", "la"]])]):
            return Address.WAGON_LN_10
        raise ValueError("No Address matches string address: " + str_addr)


class RealEstate:

    def __init__(self, address, street_num, street_name, city, state, zip_code, apt=None, db_dict=None):
        """

        Args:
            address (Address): real estate address
            street_num (str): street number or id
            street_name (str): street name
            city (str): city
            state (str): 2 letter state code
            zip_code (str): 5 letter zip code
            apt (str, optional): apt name or number
            db_dict (dict): dictionary holding arguments. if an argument is in the dictionary, it will overwrite an
                argument provided explicitly through the argument variable
        """
        self.id = None
        self.address = address
        self.street_num = street_num
        self.street_name = street_name
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.apt = apt

        if isinstance(db_dict, dict):
            self.__dict__.update(pair for pair in db_dict.items() if pair[0] in self.__dict__.keys())
            if isinstance(self.address, str):
                self.address = Address(self.address)