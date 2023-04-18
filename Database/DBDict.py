
class DBDict:

    def __init__(self, key_list=None, data_list=None, reject_lol=None, val_dict=None):
        self.reject_dict = {}
        self.value_dict = {}

        if key_list is not None:
            self.keys = key_list

            for i in range(len(self.keys)):
                if data_list is None or i >= len(data_list):
                    self.value_dict[self.keys[i]] = None
                else:
                    self.value_dict[self.keys[i]] = data_list[i]

                if reject_lol is None or i >= len(reject_lol):
                    self.reject_dict[self.keys[i]] = []
                else:
                    self.reject_dict[self.keys[i]] = reject_lol[i]
        elif val_dict is not None:
            self.value_dict = val_dict

    def remove_keys(self, *keys):
        if keys is not None:
            for key in keys:
                if self.keys is not None:
                    self.keys.remove(key)
                self.reject_dict.pop(key)
                self.value_dict.pop(key)

    @staticmethod
    def to_list_of_value_dict(db_dict_list):
        dict_list = []
        for db_dict in db_dict_list:
            dict_list.append(db_dict.value_dict)
        return dict_list