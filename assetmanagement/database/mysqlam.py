from typing import Optional, Union
import os

import pandas as pd

from .mysqlbase import FetchCursor, MySQLBase
from .popo.depreciationbilldata import DepreciationBillData
from .popo.electricbilldata import ElectricBillData
from .popo.electricdata import ElectricData
from .popo.mortgagebilldata import MortgageBillData
from .popo.natgasbilldata import NatGasBillData
from .popo.natgasdata import NatGasData
from .popo.realestate import RealEstate
from .popo.realpropertyvalues import RealPropertyValues
from .popo.serviceprovider import ServiceProvider
from .popo.simpleservicebilldata import SimpleServiceBillData
from .popo.solarbilldata import SolarBillData
from .querywriter import QueryWriter


class MySQLAM(MySQLBase):
    # TODO sub class this class each bill type?
    # TODO use multi table queries instead of making multiple queries to foreign key tables. it is more difficult to do
    # TODO      this than the current way
    """Class for AM MySQL database connections.

    This class contains functionality for AM MySQL database interactions.

    Inherits:
        MySQLBase
    """
    def __init__(self, fetch_cursor=FetchCursor.LIST_DICT):
        """Init MySQLAM """
        super(MySQLAM, self).__init__(host=os.getenv("MYSQL_HOST"), user=os.getenv("MYSQL_USER"),
                                      password=os.getenv("MYSQL_PASSWORD"), db_name=os.getenv("MYSQL_NAME"),
                                      fetch_cursor=fetch_cursor)

    @MySQLBase.fetch_cursor.setter
    def fetch_cursor(self, fetch_cursor):
        """ Set self._fetch_cursor

        Args:
            fetch_cursor (FetchCursor):
        """
        MySQLBase.fetch_cursor.fset(self, fetch_cursor)
    
    def real_estate_read(self, fields="*", wheres=(), order_bys=()):
        """ Read fields from real_estate table

        Args:
            see QueryWriter

        Returns:
            list[RealEstate]: list will be empty if no real estate data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("real_estate", fields=fields, wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)

        return [RealEstate.db_dict_constructor(d) for d in dict_list]

    def service_provider_read(self, fields="*", wheres=(), order_bys=()):
        """ Read fields from service_provider table

        Args:
            see QueryWriter

        Returns:
            list[ServiceProvider]: list will be empty if no service provider data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("service_provider", fields=fields, wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)

        return [ServiceProvider.db_dict_constructor(d) for d in dict_list]

    def real_property_values_read(self, wheres=(), order_bys=()):
        """ Read from real_property_values table

        Args:
            see QueryWriter

        Returns:
            list[RealPropertyValues]: list will be empty if no real property values data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("real_property_values", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [RealPropertyValues.db_dict_constructor(d) for d in dict_list]

    def mysunpower_hourly_data_read(self, distinct=False, wheres=(), order_bys=()):
        """ Read from mysunpower_hourly_data table

        Args:
            see QueryWriter

        Returns:
            Union[list[dict], pd.DataFrame]: depending on self._fetch_cursor. all fields as keys or columns
        """
        qw = QueryWriter("mysunpower_hourly_data", distinct=distinct, wheres=wheres, order_bys=order_bys,)
        query, params = qw.write_read_query()

        return self.execute_fetch(query, params=params)

    def mysunpower_hourly_data_insert(self, data_list):
        """ Insert into mysunpower_hourly_data table

        Args:
            data_list (list[dict]): each dict in the list must have the same keys

        Raises:
            MySQLException: if data_list element dicts do not all have the same keys, or other issue occurs
        """
        if len(data_list) == 0:
            return

        qw = QueryWriter("mysunpower_hourly_data", fields=list(data_list[0].keys()))
        query, data_list = qw.write_insert_query(data_list)

        self.execute_commit(query, params_list=data_list, execute_many=True)

    def _help_read_fk(self, dict_list):
        """ Use this function to get foreign key table data

        Works for real_estate_id, service_provider_id and real_property_values_id fields

        Args:
            dict_list (list[dict]): dicts not required to have real_estate_id or service_provider_id

        Returns:
            list[dict]: dict_list argument with the following key/value pair added to each dict:
                key "real_estate" and values RealEstate instances with data for real_estate_id
                key "service_provider" and values ServiceProvider instances with data for service_provider_id
        """
        if len(dict_list) == 0:
            return dict_list

        has_real_estate = "real_estate_id" in dict_list[0]
        has_service_provider = "service_provider_id" in dict_list[0]
        has_real_property_values = "real_property_values_id" in dict_list[0]

        re_dict, sp_dict, rpv_dict = {}, {}, {}
        if has_real_estate:
            re_dict = self.real_estate_read(
                wheres=[["id", "in", list(set([d["real_estate_id"] for d in dict_list]))]])
            re_dict = {real_estate.id: real_estate for real_estate in re_dict}
        if has_service_provider:
            sp_dict = self.service_provider_read(
                wheres=[["id", "in", list(set([d["service_provider_id"] for d in dict_list]))]])
            sp_dict = {service_provider.id: service_provider for service_provider in sp_dict}
        if has_real_property_values:
            rpv_dict = self.real_property_values_read(
                wheres=[["id", "in", list(set([d["real_property_values_id"] for d in dict_list]))]])
            rpv_dict = {real_property_values.id: real_property_values for real_property_values in rpv_dict}

        if has_real_estate or has_service_provider or has_real_property_values:
            for d in dict_list:
                if has_real_estate:
                    d["real_estate"] = re_dict[d["real_estate_id"]]
                if has_service_provider:
                    d["service_provider"] = sp_dict[d["service_provider_id"]]
                if has_real_property_values:
                    d["real_property_values"] = rpv_dict[d["real_property_values_id"]]

        return dict_list

    def solar_bill_data_read(self, wheres=(), order_bys=(), limit=None):
        """ Read all fields from solar_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[SolarBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("solar_bill_data", wheres=wheres, order_bys=order_bys, limit=limit)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [SolarBillData.db_dict_constructor(d) for d in dict_list]

    def solar_bill_data_insert(self, bill_list, ignore=None):
        """ Insert into solar_bill_data table

        Args:
            bill_list (list[SolarBillData]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("solar_bill_data", bill_list, ignore=ignore)

    def solar_bill_data_update(self, fields, set_params=(), wheres=(), where_params=None, bill_list=()):
        """ Update solar_bill_data table

        See QueryWriter write_update_query() for an example

        Args:
            fields: See QueryWriter __init__ docstring. must be list[str] (not str) if bill_list is not empty
            set_params (list[list]): See QueryWriter write_update_query() docstring. If empty list, bill_list must
                not be empty (set_params will come from bills in this list). Default ()
            wheres: See QueryWriter __init__ docstring. Default ().
            where_params (Optional[list[list]]): See QueryWriter write_update_query() docstring. Default None
            bill_list (list[SolarBillData]): See QueryWriter write_update_query() docstring. bill_list is
                provided as an argument to objects parameter. Default ()

        Raises:
            Union[AttributeError, ValueError]: if sql query and parameters can't be properly compiled
            MySQLException: if update issue occurs
        """
        qw = QueryWriter("solar_bill_data", fields=fields, wheres=wheres)
        query, final_params = qw.write_update_query(set_params, where_params, objects=bill_list)

        if query == "0":  # length of set_params is 0
            return

        self.execute_commit(query, params_list=final_params, execute_many=True)

    def electric_bill_data_read(self, wheres=(), order_bys=(), limit=None):
        """ Read all fields from electric_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[ElectricBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("electric_bill_data", wheres=wheres, order_bys=order_bys, limit=limit)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [ElectricBillData.db_dict_constructor(db_dict=d) for d in dict_list]

    def electric_bill_data_insert(self, bill_list, ignore=None):
        """ Insert into electric_bill_data table

        Args:
            bill_list (list[ElectricBillData]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("electric_bill_data", bill_list, ignore=ignore)

    def electric_bill_data_update(self, fields, set_params=(), wheres=(), where_params=None, bill_list=()):
        """ Update electric_bill_data table

        See QueryWriter write_update_query() for an example

        Args:
            fields: See QueryWriter __init__ docstring. must be list[str] (not str) if bill_list is not empty
            set_params (list[list]): See QueryWriter write_update_query() docstring. If empty list, bill_list must
                not be empty (set_params will come from bills in this list). Default ()
            wheres: See QueryWriter __init__ docstring. Default ().
            where_params (Optional[list[list]]): See QueryWriter write_update_query() docstring. Default None
            bill_list (list[ElectricBillData]): See QueryWriter write_update_query() docstring. bill_list is
                provided as an argument to objects parameter. Default ()

        Raises:
            Union[AttributeError, ValueError]: if sql query and parameters can't be properly compiled
            MySQLException: if update issue occurs
        """
        qw = QueryWriter("electric_bill_data", fields=fields, wheres=wheres)
        query, final_params = qw.write_update_query(set_params, where_params, objects=bill_list)

        if query == "0":  # length of set_params is 0
            return

        self.execute_commit(query, params_list=final_params, execute_many=True)

    def electric_data_read(self, wheres=(), order_bys=()):
        """ Read from electric_data table

        Args:
            see QueryWriter

        Returns:
            list[ElectricData]: list will be empty if no electric data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("electric_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [ElectricData.db_dict_constructor(d) for d in dict_list]

    def electric_data_insert(self, data_list):
        """ Insert into electric_data table

        Args:
            data_list (list[ElectricData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("electric_data", data_list)

    def estimate_notes_read(self, wheres=(), order_bys=()):
        """ Read from estimate_notes table

        Args:
            see QueryWriter

        Returns:
            list[dict]: of records with all fields as dict keys

        Raises:
            MySQLException:
        """
        qw = QueryWriter("estimate_notes", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        notes_list = self.execute_fetch(query, params=params)
        notes_list = self._help_read_fk(notes_list)

        return notes_list

    def natgas_bill_data_read(self, wheres=(), order_bys=(), limit=None):
        """ Read all fields from natgas_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[NatGasBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("natgas_bill_data", wheres=wheres, order_bys=order_bys, limit=limit)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [NatGasBillData.db_dict_constructor(d) for d in dict_list]

    def natgas_bill_data_insert(self, bill_list, ignore=None):
        """ Insert into natgas_bill_data table

        Args:
            bill_list (list[NatGasBillData]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("natgas_bill_data", bill_list, ignore=ignore)

    def natgas_bill_data_update(self, fields, set_params=(), wheres=(), where_params=None, bill_list=()):
        """ Update natgas_bill_data table

        See QueryWriter write_update_query() for an example

        Args:
            fields: See QueryWriter __init__ docstring. must be list[str] (not str) if bill_list is not empty
            set_params (list[list]): See QueryWriter write_update_query() docstring. If empty list, bill_list must
                not be empty (set_params will come from bills in this list). Default ()
            wheres: See QueryWriter __init__ docstring. Default ().
            where_params (Optional[list[list]]): See QueryWriter write_update_query() docstring. Default None
            bill_list (list[NatGasBillData]): See QueryWriter write_update_query() docstring. bill_list is
                provided as an argument to objects parameter. Default ()

        Raises:
            Union[AttributeError, ValueError]: if sql query and parameters can't be properly compiled
            MySQLException: if update issue occurs
        """
        qw = QueryWriter("natgas_bill_data", fields=fields, wheres=wheres)
        query, final_params = qw.write_update_query(set_params, where_params, objects=bill_list)

        if query == "0":  # length of set_params is 0
            return

        self.execute_commit(query, params_list=final_params, execute_many=True)

    def natgas_data_read(self, wheres=(), order_bys=()):
        """ Read from natgas_data table

        Args:
            see QueryWriter

        Returns:
            list[NatGasData]: list will be empty if no natural gas data found matching wheres

        Raises:
            MySQLException if database read issue occurs
        """
        qw = QueryWriter("natgas_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [NatGasData.db_dict_constructor(d) for d in dict_list]

    def natgas_data_insert(self, data_list):
        """ Insert into natgas_data table

        Args:
            data_list (list[NatGasData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("natgas_data", data_list)

    def simple_bill_data_insert(self, bill_list, ignore=None):
        """ Insert into simple_bill_data table

        Args:
            bill_list (list[SimpleServiceBillData]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("simple_bill_data", bill_list, ignore=ignore)

    def simple_bill_data_update(self, fields, set_params=(), wheres=(), where_params=None, bill_list=()):
        """ Update simple_bill_data table

        See QueryWriter write_update_query() for an example

        Args:
            fields: See QueryWriter __init__ docstring. must be list[str] (not str) if bill_list is not empty
            set_params (list[list]): See QueryWriter write_update_query() docstring. If empty list, bill_list must
                not be empty (set_params will come from bills in this list). Default ()
            wheres: See QueryWriter __init__ docstring. Default ().
            where_params (Optional[list[list]]): See QueryWriter write_update_query() docstring. Default None
            bill_list (list[SimpleServiceBillData]): See QueryWriter write_update_query() docstring. bill_list is
                provided as an argument to objects parameter. Default ()

        Raises:
            Union[AttributeError, ValueError]: if sql query and parameters can't be properly compiled
            MySQLException: if update issue occurs
        """
        qw = QueryWriter("simple_bill_data", fields=fields, wheres=wheres)
        query, final_params = qw.write_update_query(set_params, where_params, objects=bill_list)

        if query == "0":  # length of set_params is 0
            return

        self.execute_commit(query, params_list=final_params, execute_many=True)

    def simple_bill_data_read(self, wheres=(), order_bys=(), limit=None):
        """ Read all fields from simple_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[SimpleServiceBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("simple_bill_data", wheres=wheres, order_bys=order_bys, limit=limit)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [SimpleServiceBillData.db_dict_constructor(d) for d in dict_list]

    def mortgage_bill_data_insert(self, bill_list, ignore=None):
        """ Insert into mortgage_bill_data table

        Args:
            bill_list (list[MortgageBillData]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("mortgage_bill_data", bill_list, ignore=ignore)

    def mortgage_bill_data_update(self, fields, set_params=(), wheres=(), where_params=None, bill_list=()):
        """ Update mortgage_bill_data table

        See QueryWriter write_update_query() for an example

        Args:
            fields: See QueryWriter __init__ docstring. must be list[str] (not str) if bill_list is not empty
            set_params (list[list]): See QueryWriter write_update_query() docstring. If empty list, bill_list must
                not be empty (set_params will come from bills in this list). Default ()
            wheres: See QueryWriter __init__ docstring. Default ().
            where_params (Optional[list[list]]): See QueryWriter write_update_query() docstring. Default None
            bill_list (list[MortgageBillData]): See QueryWriter write_update_query() docstring. bill_list is
                provided as an argument to objects parameter. Default ()

        Raises:
            Union[AttributeError, ValueError]: if sql query and parameters can't be properly compiled
            MySQLException: if update issue occurs
        """
        qw = QueryWriter("mortgage_bill_data", fields=fields, wheres=wheres)
        query, final_params = qw.write_update_query(set_params, where_params, objects=bill_list)

        if query == "0":  # length of set_params is 0
            return

        self.execute_commit(query, params_list=final_params, execute_many=True)

    def mortgage_bill_data_read(self, wheres=(), order_bys=(), limit=None):
        """ Read all fields from mortgage_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[MortgageBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("mortgage_bill_data", wheres=wheres, order_bys=order_bys, limit=limit)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [MortgageBillData.db_dict_constructor(d) for d in dict_list]

    def depreciation_bill_data_insert(self, bill_list, ignore=None):
        """ Insert into depreciation_bill_data table

        Args:
            bill_list (list[DepreciationBillData]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("depreciation_bill_data", bill_list, ignore=ignore)

    def depreciation_bill_data_update(self, fields, set_params=(), wheres=(), where_params=None, bill_list=()):
        """ Update depreciation_bill_data table

        See QueryWriter write_update_query() for an example

        Args:
            fields: See QueryWriter __init__ docstring. must be list[str] (not str) if bill_list is not empty
            set_params (list[list]): See QueryWriter write_update_query() docstring. If empty list, bill_list must
                not be empty (set_params will come from bills in this list). Default ()
            wheres: See QueryWriter __init__ docstring. Default ().
            where_params (Optional[list[list]]): See QueryWriter write_update_query() docstring. Default None
            bill_list (list[DepreciationBillData]): See QueryWriter write_update_query() docstring. bill_list is
                provided as an argument to objects parameter. Default ()

        Raises:
            Union[AttributeError, ValueError]: if sql query and parameters can't be properly compiled
            MySQLException: if update issue occurs
        """
        qw = QueryWriter("depreciation_bill_data", fields=fields, wheres=wheres)
        query, final_params = qw.write_update_query(set_params, where_params, objects=bill_list)

        if query == "0":  # length of set_params is 0
            return

        self.execute_commit(query, params_list=final_params, execute_many=True)

    def depreciation_bill_data_read(self, wheres=(), order_bys=(), limit=None):
        """ Read all fields from depreciation_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[DepreciationBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("depreciation_bill_data", wheres=wheres, order_bys=order_bys, limit=limit)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        return [DepreciationBillData.db_dict_constructor(d) for d in dict_list]