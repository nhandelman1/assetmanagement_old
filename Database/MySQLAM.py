import pandas as pd
from enum import Enum
from typing import Union, Optional
from Database.MySQLBase import MySQLBase, FetchCursor
from Database.DBDict import DBDict
from Database.QueryWriter import QueryWriter
from Database.POPO.RealEstate import RealEstate
from Database.POPO.RealPropertyValues import RealPropertyValues
from Database.POPO.ServiceProvider import ServiceProvider
from Database.POPO.SimpleServiceBillData import SimpleServiceBillData
from Database.POPO.ElectricBillData import ElectricBillData
from Database.POPO.ElectricData import ElectricData
from Database.POPO.NatGasBillData import NatGasBillData
from Database.POPO.NatGasData import NatGasData
from Database.POPO.SolarBillData import SolarBillData
from Database.POPO.MortgageBillData import MortgageBillData


class ETFDataTypes(Enum):
    ASSET_CLASS = "etf_asset_class",
    CATEGORIES = "etf_categories",
    ASSET_CLASS_SIZE = "etf_asset_class_size",
    ASSET_CLASS_STYLE = "etf_asset_class_style",
    BOND_TYPE = "etf_bond_type",
    BOND_DURATION = "etf_bond_duration_type",
    COMMODITY_TYPE = "etf_commodity_type",
    COMMODITY = "etf_commodity",
    COMMODITY_EXPOSURE = "etf_commodity_exposure_type",
    CURRENCY_TYPE = "etf_currency_type"

    def __init__(self, db_table):
        self.db_table = db_table


########################################################################################################################
# class Database
# Use id for Update where clause wherever possible. The front end will be programmed with this assumption for simplicity
########################################################################################################################
class MySQLAM(MySQLBase):
    """Class for AM MySQL database connections.

    This class contains functionality for AM MySQL database interactions.

    Inherits:
        MySQLBase
    """
    def __init__(self, fetch_cursor=FetchCursor.LIST_DICT):
        """Init MySQLAM """
        # TODO need to setup to use correct db name for dev and prod
        super(MySQLAM, self).__init__(host="localhost", user="root", password="=a4tUtheWur_n8=udAs_aZ7qeB84w=",
                                      db_name="am_dev", fetch_cursor=fetch_cursor)

    @MySQLBase.fetch_cursor.setter
    def fetch_cursor(self, fetch_cursor):
        """ Set self._fetch_cursor

        Args:
            fetch_cursor (FetchCursor):
        """
        MySQLBase.fetch_cursor.fset(self, fetch_cursor)

    @staticmethod
    def set_where_stmt(key, value, op):
        if value is None:
            return " IS NULL "
        else:
            return " " + op + " %(" + key + ")s "

    ####################################################################################################################
    # Data
    ####################################################################################################################
    @staticmethod
    def data_source_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def data_types_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "db_table_meta", "db_data_table_midfix"], data_list=data_list,
                      reject_lol=reject_lol)

    @staticmethod
    def data_subtypes_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "type_id", "db_table_meta", "db_data_table_prefix"],
                      data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def data_freq_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "freq", "format_str"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def data_subtype_freq_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "subtype_id", "freq_id"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def data_meta_table_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["meta_table", "numeric_only"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    # data_name_dict must contain a key/value pair for the data_id (e.g. securities_id)
    def data_data_table_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["prefix", "midfix", "freq", "column", "data_name_dict", "numeric_only",
                                "data_type_meta_table", "begin_date", "end_date"],
                      data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def data_data_table_db_dict_query_data(data_data_table_db_dict):
        if data_data_table_db_dict is None:
            return None

        data_name_dict = data_data_table_db_dict.value_dict["data_name_dict"]

        id_column = data_data_table_db_dict.value_dict["data_type_meta_table"] + "_id"
        table = data_data_table_db_dict.value_dict["prefix"] + "_" + \
                data_data_table_db_dict.value_dict["midfix"] + "_" + data_data_table_db_dict.value_dict["freq"]
        column = data_data_table_db_dict.value_dict["column"]

        data_data_table_db_dict.remove_keys("data_name_dict")
        data_data_table_db_dict.value_dict["data_id"] = data_name_dict[id_column]

        return id_column, table, column

    def read_data_source(self):
        return self.execute_fetch("SELECT name, notes, id FROM data_source ORDER BY name")

    def insert_data_source(self, data_source_db_dict):
        return self.execute_commit("INSERT INTO data_source (name, notes) VALUES (%(name)s, %(notes)s)",
                                   data_source_db_dict.value_dict)

    def update_data_source(self, data_source_db_dict):
        return self.execute_commit("UPDATE data_source SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                   data_source_db_dict.value_dict)

    def read_data_types(self, data_types_db_dict=None):
        if data_types_db_dict is None:
            data_types_db_dict = MySQLAM.data_types_db_dict()

        query = "SELECT name, db_table_meta, db_data_table_midfix, id FROM data_types"

        if data_types_db_dict.value_dict["name"] is not None:
            query += " WHERE name = %(name)s"

        query += " ORDER BY name"

        return self.execute_fetch(query, data_types_db_dict.value_dict)

    def read_data_subtype_id(self, subtype_name):
        return self.execute_fetch("SELECT id FROM data_subtypes WHERE name = '" + subtype_name + "'")[0]['id']

    def read_data_subtypes(self, data_subtypes_db_dict=None):
        if data_subtypes_db_dict is None:
            data_subtypes_db_dict = MySQLAM.data_subtypes_db_dict()

        query = "SELECT name, type_id, db_table_meta, db_data_table_prefix, id FROM data_subtypes WHERE 1=1"

        if data_subtypes_db_dict.value_dict["type_id"] is not None:
            query += " AND type_id = %(type_id)s"
        if data_subtypes_db_dict.value_dict["id"] is not None:
            query += " AND id = %(id)s"
        if data_subtypes_db_dict.value_dict["name"] is not None:
            query += " AND name = %(name)s"

        query += " ORDER BY name"

        return self.execute_fetch(query, data_subtypes_db_dict.value_dict)

    def read_data_freq(self, data_freq_db_dict=None):
        if data_freq_db_dict is None:
            data_freq_db_dict = MySQLAM.data_freq_db_dict()

        query = "SELECT freq, format_str, id FROM data_freq"

        if data_freq_db_dict.value_dict["id"] is not None:
            query += " WHERE id = %(id)s"

        query += " ORDER BY freq"

        return self.execute_fetch(query, data_freq_db_dict.value_dict)

    def read_data_subtype_freq(self, data_subtype_freq_db_dict=None):
        query = "SELECT ds.id as subtype_id, ds.name, df.id as freq_id, df.freq, df.format_str " \
                "FROM data_subtype_freq AS dsf " \
                "INNER JOIN data_subtypes AS ds ON ds.id = dsf.subtype_id " \
                "INNER JOIN data_freq AS df ON df.id = dsf.freq_id"

        if data_subtype_freq_db_dict is None:
            data_subtype_freq_db_dict = MySQLAM.data_subtype_freq_db_dict()
        elif data_subtype_freq_db_dict.value_dict["subtype_id"] is not None:
            query += " WHERE dsf.subtype_id = %(subtype_id)s ORDER BY df.freq"
        elif data_subtype_freq_db_dict.value_dict["freq_id"] is not None:
            query += " WHERE dsf.freq_id = %(freq_id)s ORDER BY ds.name"

        return self.execute_fetch(query, data_subtype_freq_db_dict.value_dict)

    def read_data_subtype_meta_table(self, data_meta_table_db_dict):
        meta_table = None if data_meta_table_db_dict is None else data_meta_table_db_dict.value_dict["meta_table"]

        if meta_table == "stocks":
            return self.read_stocks()
        elif meta_table == "indices":
            return self.read_indices()
        elif meta_table == "etfs":
            return self.read_etfs()
        else:
            return []

    def read_data_or_meta_table_columns(self, data_data_table_db_dict=None, data_meta_table_db_dict=None):
        if data_data_table_db_dict is not None:
            numeric_only = data_data_table_db_dict.value_dict["numeric_only"]
            dict_list = self.execute_fetch(
                "SHOW columns FROM " + data_data_table_db_dict.value_dict["prefix"] + "_"
                + data_data_table_db_dict.value_dict["midfix"] + "_" + data_data_table_db_dict.value_dict["freq"])
        elif data_meta_table_db_dict is not None:
            numeric_only = data_meta_table_db_dict.value_dict["numeric_only"]
            dict_list = self.execute_fetch("SHOW columns FROM " + data_meta_table_db_dict.value_dict["meta_table"])
        else:
            numeric_only = False
            dict_list = []

        if numeric_only:
            new_list = []
            for d in dict_list:
                if d["Key"] in ["PRI", "MUL", "UNI"]:
                    continue
                if any(x in d["Type"] for x in ["int", "decimal", "numeric", "float", "double"]):
                    new_list.append(d)
            return new_list
        else:
            return dict_list

    def read_data_data_table_min_max_date(self, data_data_table_db_dict):
        if data_data_table_db_dict is None:
            return [None, None]

        id_column, table, column = self.data_data_table_db_dict_query_data(data_data_table_db_dict)

        res_dict_list = self.execute_fetch("SELECT MIN(date_time), MAX(date_time) FROM " + table +
                                           " WHERE " + id_column + " = %(data_id)s AND " + column + " IS NOT NULL",
                                           data_data_table_db_dict.value_dict)
        return list(res_dict_list[0].values())

    def read_data_data_table_count(self, data_data_table_db_dict):
        if data_data_table_db_dict is None:
            return -1

        id_column, table, column = self.data_data_table_db_dict_query_data(data_data_table_db_dict)

        res_dict_list = self.execute_fetch("SELECT COUNT(" + column + ") FROM " + table +
                                           " WHERE " + id_column + " = %(data_id)s AND date_time >= %(begin_date)s" +
                                           " AND date_time <= %(end_date)s", data_data_table_db_dict.value_dict)

        return next(iter(res_dict_list[0].values()))

    def read_data_data_table(self, data_data_table_db_dict):
        id_column, table, column = self.data_data_table_db_dict_query_data(data_data_table_db_dict)

        res_dict_list = self.execute_fetch("SELECT date_time, " + column + " FROM " + table +
                                           " WHERE " + id_column + " = %(data_id)s"
                                           " AND date_time >= %(begin_date)s AND date_time <= %(end_date)s",
                                           data_data_table_db_dict.value_dict)
        return res_dict_list

    ####################################################################################################################
    # Security
    ####################################################################################################################

    @staticmethod
    def security_security_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "sec_id", "sec_under_id", "weight"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def securities_under_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["securities_type", "securities_id"], data_list=data_list, reject_lol=reject_lol)

    def read_security_subtypes(self):
        query = "SELECT ds.name, ds.db_table_meta, ds.db_data_table_prefix, ds.id FROM data_subtypes as ds " \
                "INNER JOIN data_types as dt on dt.id = ds.type_id WHERE dt.name = 'Security' ORDER BY ds.name"
        return self.execute_fetch(query)

    def read_security_components(self, db_dict):
        return self.execute_fetch("SELECT sec_sec.sec_under_id AS securities_id, securities.ticker FROM securities "
                                  "INNER JOIN sec_sec ON securities.id = sec_sec.sec_under_id "
                                  "WHERE sec_sec.sec_id = %(securities_id)s", db_dict.value_dict)

    def read_securities_under(self, su_db_dict):
        security_type = su_db_dict.value_dict["securities_type"]

        if security_type in ["Stocks"]:
            return False

        dict_list = self.execute_fetch("SELECT sec_sec.id, securities.ticker, sec_sec.weight FROM sec_sec "
                                       "INNER JOIN securities ON securities.id = sec_sec.sec_under_id "
                                       "WHERE sec_sec.sec_id = %(securities_id)s ORDER BY weight DESC",
                                       su_db_dict.value_dict)
        dict_list.insert(0, ["ticker", "weight"])
        return dict_list

    def attach_security_security(self, db_dict_list):
        return self.execute_commit("INSERT INTO sec_sec (sec_id, sec_under_id) VALUES (%(sec_id)s, %(sec_under_id)s)",
                                   DBDict.to_list_of_value_dict(db_dict_list), execute_many=True)

    def detach_security_security(self, db_dict_list):
        return self.execute_commit("DELETE FROM sec_sec WHERE sec_id = %(sec_id)s AND sec_under_id = %(sec_under_id)s",
                                   DBDict.to_list_of_value_dict(db_dict_list), execute_many=True)

    def update_security_security_weight(self, db_dict_list):
        return self.execute_commit("UPDATE sec_sec SET weight = %(weight)s WHERE id = %(id)s",
                                   DBDict.to_list_of_value_dict(db_dict_list), execute_many=True)

    ####################################################################################################################
    # region country
    ####################################################################################################################
    @staticmethod
    def region_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def country_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def region_country_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "region_id", "country_id"], data_list=data_list, reject_lol=reject_lol)

    def read_region(self, country_db_dict=None):
        if country_db_dict is None:
            return self.execute_fetch("SELECT name, notes, id FROM region ORDER BY name")
        else:
            return self.execute_fetch(
                "SELECT region.name FROM region, region_country WHERE region_country.country_id = %(id)s AND "
                "region_country.region_id = region.id ORDER BY region.name", country_db_dict.value_dict)

    def read_country(self, region_db_dict=None):
        if region_db_dict is None:
            return self.execute_fetch("SELECT name, notes, id FROM country ORDER BY name")
        else:
            return self.execute_fetch(
                "SELECT country.name, region_country.id FROM country, region_country "
                "WHERE region_country.region_id = %(id)s AND region_country.country_id = country.id "
                "ORDER BY country.name", region_db_dict.value_dict)

    def insert_region(self, db_dict):
        return self.execute_commit("INSERT INTO region (name, notes) VALUES (%(name)s, %(notes)s)", db_dict.value_dict)

    def insert_country(self, db_dict):
        return self.execute_commit("INSERT INTO country (name, notes) VALUES (%(name)s, %(notes)s)", db_dict.value_dict)

    def attach_region_country(self, db_dict):
        return self.execute_commit("INSERT INTO region_country (region_id, country_id) "
                                   "VALUES (%(region_id)s, %(country_id)s)", db_dict.value_dict)

    def detach_region_country(self, db_dict):
        return self.execute_commit("DELETE FROM region_country "
                                   "WHERE region_id = %(region_id)s AND country_id = %(country_id)s", db_dict.value_dict)

    def update_region(self, db_dict):
        return self.execute_commit("UPDATE region SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                   db_dict.value_dict)

    def update_country(self, db_dict):
        return self.execute_commit("UPDATE country SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                   db_dict.value_dict)

    ####################################################################################################################
    # business meta
    ####################################################################################################################
    @staticmethod
    def sector_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def industry_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "sector_id", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def company_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def company_industry_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "company_id", "industry_id"], data_list=data_list, reject_lol=reject_lol)

    def read_sector(self):
        return self.execute_fetch("SELECT name, notes, id FROM sector ORDER BY name")

    def read_sector_hier(self, db_dict):
        return self.execute_fetch("SELECT sector.name, industry.name AS industry_name, company.name AS company_name "
                                  "FROM sector LEFT OUTER JOIN industry ON sector.id = industry.sector_id "
                                  "LEFT OUTER JOIN company_industry ON industry.id = company_industry.industry_id "
                                  "LEFT OUTER JOIN company ON company_industry.company_id = company.id "
                                  "WHERE sector.id = %(id)s", db_dict.value_dict)

    def read_industry(self, sector_db_dict=None):
        if sector_db_dict is None:
            return self.execute_fetch("SELECT id, name, sector_id, notes FROM industry ORDER BY name")
        else:
            return self.execute_fetch(
                "SELECT id, name, sector_id, notes FROM industry WHERE sector_id " +
                self.set_where_stmt("id", sector_db_dict.value_dict["id"], "=") + " ORDER BY name",
                sector_db_dict.value_dict)

    def read_industry_hier(self, db_dict):
        return self.execute_fetch("SELECT sector.name, industry.name AS industry_name, company.name AS company_name "
                                  "FROM sector RIGHT OUTER JOIN industry ON sector.id = industry.sector_id "
                                  "LEFT OUTER JOIN company_industry ON industry.id = company_industry.industry_id "
                                  "LEFT OUTER JOIN company ON company_industry.company_id = company.id "
                                  "WHERE industry.id = %(id)s", db_dict.value_dict)

    def read_company(self):
        return self.execute_fetch("SELECT name, notes, id FROM company ORDER BY name")

    def read_company_hier(self, db_dict):
        return self.execute_fetch("SELECT sector.name, industry.name AS industry_name, company.name AS company_name "
                                  "FROM sector RIGHT OUTER JOIN industry ON sector.id = industry.sector_id "
                                  "LEFT OUTER JOIN company_industry ON industry.id = company_industry.industry_id "
                                  "RIGHT OUTER JOIN company ON company_industry.company_id = company.id "
                                  "WHERE company.id = %(id)s", db_dict.value_dict)

    def insert_sector(self, db_dict):
        return self.execute_commit("INSERT INTO sector (name, notes) VALUES (%(name)s, %(notes)s)", db_dict.value_dict)

    def insert_industry(self, db_dict):
        return self.execute_commit("INSERT INTO industry (name, sector_id, notes) "
                                   "VALUES (%(name)s, %(sector_id)s, %(notes)s)", db_dict.value_dict)

    def insert_company(self, db_dict):
        return self.execute_commit("INSERT INTO company (name, notes) VALUES (%(name)s, %(notes)s)", db_dict.value_dict)

    def attach_industry_company(self, db_dict):
        return self.execute_commit("INSERT INTO company_industry (industry_id, company_id) "
                                   "VALUES (%(industry_id)s, %(company_id)s)", db_dict.value_dict)

    def detach_industry_company(self, db_dict):
        return self.execute_commit("DELETE FROM company_industry "
                                   "WHERE industry_id = %(industry_id)s AND company_id = %(company_id)s",
                                   db_dict.value_dict)

    def update_sector(self, db_dict):
        return self.execute_commit("UPDATE sector SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                   db_dict.value_dict)

    def update_industry(self, db_dict):
        if db_dict.value_dict["name"] is None and db_dict.value_dict["notes"] is None:
            return self.execute_commit("UPDATE industry SET sector_id = %(sector_id)s WHERE id = %(id)s",
                                       db_dict.value_dict)
        else:
            return self.execute_commit("UPDATE industry SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                       db_dict.value_dict)

    def update_company(self, db_dict):
        return self.execute_commit("UPDATE company SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                   db_dict.value_dict)

    ####################################################################################################################
    # index meta
    ####################################################################################################################
    @staticmethod
    def index_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "ticker", 'name', "issue_company_id", "securities_id"],
                      data_list=data_list, reject_lol=reject_lol)

    def read_indices(self):
        return self.execute_fetch("SELECT indices.id, securities.ticker, indices.name, company.name AS company_name, "
                                  "indices.securities_id FROM securities "
                                  "INNER JOIN indices ON indices.securities_id = securities.id "
                                  "LEFT OUTER JOIN company ON indices.issue_company_id = company.id "
                                  "ORDER BY securities.ticker")

    def insert_index(self, db_dict):
        subtype_id = self.read_data_subtype_id("Indices")
        return self.execute_commit(["INSERT INTO securities (ticker, type_id) VALUES (%(ticker)s, " + str(subtype_id) +
                                    ")",
                                    "INSERT INTO indices (securities_id, name, issue_company_id) VALUES "
                                    "((SELECT id FROM securities WHERE ticker = %(ticker)s), "
                                    "%(name)s, %(issue_company_id)s)"],
                                   [db_dict.value_dict, db_dict.value_dict])

    def update_index(self, db_dict):
        return self.execute_commit(["UPDATE securities SET ticker = %(ticker)s WHERE id = "
                                    "(SELECT securities_id FROM indices WHERE id = %(id)s)",
                                    "UPDATE indices SET name = %(name)s, "
                                    "issue_company_id = %(issue_company_id)s WHERE id = %(id)s"],
                                   [db_dict.value_dict, db_dict.value_dict])

    ####################################################################################################################
    # stock meta
    ####################################################################################################################
    @staticmethod
    def stock_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "ticker", "company_id"], data_list=data_list, reject_lol=reject_lol)

    def read_stocks(self):
        return self.execute_fetch("SELECT stocks.id, securities.ticker, company.name, securities.id AS securities_id "
                                  "FROM securities INNER JOIN stocks ON stocks.securities_id = securities.id "
                                  "LEFT OUTER JOIN company ON stocks.company_id = company.id "
                                  "ORDER BY securities.ticker")

    def insert_stock(self, db_dict):
        subtype_id = self.read_data_subtype_id("Stocks")
        return self.execute_commit(["INSERT INTO securities (ticker, type_id) VALUES (%(ticker)s, " + str(subtype_id) +
                                    ")",
                                    "INSERT INTO stocks (securities_id, company_id) VALUES "
                                    "((SELECT id FROM securities WHERE ticker = %(ticker)s), %(company_id)s)"],
                                   [db_dict.value_dict, db_dict.value_dict])

    def update_stock(self, db_dict):
        return self.execute_commit(["UPDATE securities SET ticker = %(ticker)s WHERE id = "
                                    "(SELECT securities_id FROM stocks WHERE id = %(id)s)",
                                    "UPDATE stocks SET company_id = %(company_id)s WHERE id = %(id)s"],
                                   [db_dict.value_dict, db_dict.value_dict])

    ####################################################################################################################
    # ETF meta
    ####################################################################################################################

    @staticmethod
    def etf_category_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    def read_etf_categories(self):
        return self.execute_fetch("SELECT name, notes, id FROM etf_categories ORDER BY name")

    def insert_etf_category(self, db_dict):
        return self.execute_commit("INSERT INTO etf_categories (name, notes) VALUES (%(name)s, %(notes)s)",
                                   db_dict.value_dict)

    def update_etf_category(self, db_dict):
        return self.execute_commit("UPDATE etf_categories SET name = %(name)s, notes = %(notes)s WHERE id = %(id)s",
                                   db_dict.value_dict)

    # etf_asset_class_db_dict
    # etf_categories_db_dict
    # etf_asset_class_size_db_dict
    # etf_asset_class_style_db_dict
    # etf_bond_type_db_dict
    # etf_bond_duration_type_db_dict
    # etf_commodity_type_db_dict
    # etf_commodity_db_dict
    # etf_commodity_exposure_type_db_dict
    # etf_currency_type_db_dict
    @staticmethod
    def etf_data_type_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "name", "notes"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def etf_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "securities_id", "ticker", 'name', "asset_class_id", "issue_company_id",
                                "index_id", "lev", "fee", "inception", "category_id", "region_country_id",
                                "industry_id", "asset_class_size_id", "asset_class_style_id", "bond_type_id",
                                "bond_duration_type_id", "commodity_type_id", "commodity_id",
                                "commodity_exposure_type_id", "currency_type_id"],
                      data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def etf_search_db_dict(data_list=None):
        return DBDict(key_list=["asset_class_id", "issue_company_id", "index_id", "lev_less", "lev_greater", "fee_less",
                                "fee_greater", "inception_less", "inception_greater", "category_id",
                                "region_country_id", "industry_id", "asset_class_size_id", "asset_class_style_id",
                                "bond_type_id", "bond_duration_type_id", "commodity_type_id", "commodity_id",
                                "commodity_exposure_type_id", "currency_type_id"], data_list=data_list,
                      reject_lol=[[None]])

    def read_etf_data_type(self, etf_data_type):
        return self.execute_fetch("SELECT id, name, notes FROM " + etf_data_type.db_table + " ORDER BY name")

    def update_etf(self, db_dict):
        query_list = [
            "UPDATE securities SET ticker = %(ticker)s WHERE id = (SELECT securities_id FROM etfs WHERE id = %(id)s)",
            "UPDATE etfs SET name = %(name)s, asset_class_id = %(asset_class_id)s, "
            "issue_company_id = %(issue_company_id)s, index_id = %(index_id)s, lev = %(lev)s, fee = %(fee)s, "
            "inception = %(inception)s, category_id = %(category_id)s, region_country_id = %(region_country_id)s, "
            "industry_id = %(industry_id)s, asset_class_size_id = %(asset_class_size_id)s, "
            "asset_class_style_id = %(asset_class_style_id)s, bond_type_id = %(bond_type_id)s, "
            "bond_duration_type_id = %(bond_duration_type_id)s, commodity_type_id = %(commodity_type_id)s, "
            "commodity_id = %(commodity_id)s, commodity_exposure_type_id = %(commodity_exposure_type_id)s, "
            "currency_type_id = %(currency_type_id)s WHERE id = %(id)s"]

        return self.execute_commit(query_list, [db_dict.value_dict, db_dict.value_dict])

    def insert_etf(self, db_dict):
        subtype_id = self.read_data_subtype_id("ETFs")
        query_list = [
            "INSERT INTO securities (ticker, type_id) VALUES (%(ticker)s, " + str(subtype_id) + ")",
            "INSERT INTO etfs (securities_id, name, asset_class_id, issue_company_id, index_id, lev, fee, inception, "
            "category_id, region_country_id, industry_id, asset_class_size_id, asset_class_style_id, bond_type_id, "
            "bond_duration_type_id, commodity_type_id, commodity_id, commodity_exposure_type_id, currency_type_id) "
            "VALUES ((SELECT id FROM securities WHERE ticker = %(ticker)s), %(name)s, %(asset_class_id)s, "
            "%(issue_company_id)s, %(index_id)s, %(lev)s, %(fee)s, %(inception)s, %(category_id)s, "
            "%(region_country_id)s, %(industry_id)s, %(asset_class_size_id)s, %(asset_class_style_id)s, "
            "%(bond_type_id)s, %(bond_duration_type_id)s, %(commodity_type_id)s, %(commodity_id)s, "
            "%(commodity_exposure_type_id)s, %(currency_type_id)s)"]

        return self.execute_commit(query_list, [db_dict.value_dict, db_dict.value_dict])

    def read_etfs(self, search_db_dict=None):
        query = \
            "SELECT etfs.id, securities.ticker, etfs.name, etf_asset_class.name AS asset_class, " \
            "company.name AS company_name, securities_index.ticker as index_ticker, etfs.lev, etfs.fee, etfs.inception, " \
            "etf_categories.name AS category, region.name AS region, country.name AS country, sector.name AS sector, " \
            "industry.name AS industry, etf_asset_class_size.name AS asset_class_size, " \
            "etf_asset_class_style.name AS asset_class_style, etf_bond_type.name AS bond_type, " \
            "etf_bond_duration_type.name AS bond_duration_type, etf_commodity_type.name AS commodity_type, " \
            "etf_commodity.name AS commodity, etf_commodity_exposure_type.name AS commodity_exposure_type, " \
            "etf_currency_type.name AS currency_type, etfs.securities_id FROM etfs " \
            "INNER JOIN securities ON etfs.securities_id = securities.id " \
            "INNER JOIN etf_asset_class ON etfs.asset_class_id = etf_asset_class.id " \
            "LEFT OUTER JOIN company ON etfs.issue_company_id = company.id " \
            "LEFT OUTER JOIN indices ON etfs.index_id = indices.id " \
            "LEFT OUTER JOIN securities AS securities_index ON securities_index.id = indices.securities_id " \
            "LEFT OUTER JOIN etf_categories ON etfs.category_id = etf_categories.id " \
            "LEFT OUTER JOIN region_country ON etfs.region_country_id = region_country.id " \
            "LEFT OUTER JOIN region ON region.id = region_country.region_id " \
            "LEFT OUTER JOIN country ON country.id = region_country.country_id " \
            "LEFT OUTER JOIN industry ON etfs.industry_id = industry.id " \
            "LEFT OUTER JOIN sector ON industry.sector_id = sector.id " \
            "LEFT OUTER JOIN etf_asset_class_size ON etfs.asset_class_size_id = etf_asset_class_size.id " \
            "LEFT OUTER JOIN etf_asset_class_style ON etfs.asset_class_style_id = etf_asset_class_style.id " \
            "LEFT OUTER JOIN etf_bond_type ON etfs.bond_type_id = etf_bond_type.id " \
            "LEFT OUTER JOIN etf_bond_duration_type ON etfs.bond_duration_type_id = etf_bond_duration_type.id " \
            "LEFT OUTER JOIN etf_commodity_type ON etfs.commodity_type_id = etf_commodity_type.id " \
            "LEFT OUTER JOIN etf_commodity ON etfs.commodity_id = etf_commodity.id " \
            "LEFT OUTER JOIN etf_commodity_exposure_type ON etfs.commodity_exposure_type_id = etf_commodity_exposure_type.id " \
            "LEFT OUTER JOIN etf_currency_type ON etfs.currency_type_id = etf_currency_type.id " \

        if search_db_dict is None:
            query += "ORDER BY securities.ticker "
            return self.execute_fetch(query)
        else:
            query += "WHERE 1=1 "

            for k in search_db_dict.keys:
                if search_db_dict.value_dict[k] not in search_db_dict.reject_dict[k]:
                    if k[-5:] == "_less":
                        query += "AND etfs." + k[0:-5] + self.set_where_stmt(k, search_db_dict.value_dict[k], "<=")
                    elif k[-8:] == "_greater":
                        query += "AND etfs." + k[0:-8] + self.set_where_stmt(k, search_db_dict.value_dict[k], ">=")
                    else:
                        query += "AND etfs." + k + self.set_where_stmt(k, search_db_dict.value_dict[k], "=")
            query += "ORDER BY securities.ticker "

            return self.execute_fetch(query, search_db_dict.value_dict)

    ####################################################################################################################
    # SEI Data
    ####################################################################################################################
    @staticmethod
    def sei_data_price_data_read_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["securities_type", "freq", "securities_id", "begin_time", "end_time"], data_list=data_list,
                      reject_lol=reject_lol)

    @staticmethod
    def sei_data_price_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "securities_type", "securities_id", "freq", "date_time", "open", "high", "low",
                                "close", "adj_close", "volume"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def sei_data_data_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["id", "securities_id", "date_time", "dividend", "splits", "shares_float",
                                "shares_short", "shares_outstanding", "aum"], data_list=data_list, reject_lol=reject_lol)

    @staticmethod
    def time_interval_check(db_dict_list, freq):
        if freq in ["1D"]:
            return True

        for db_dict in db_dict_list:
            if int(db_dict.value_dict["date_time"][-4]) % 5 != 0:
                return False

        return True

    def get_sei_table_volume(self, sec_type, freq, isUpdate=False):
        midfix = self.read_data_types(MySQLAM.data_types_db_dict([None, "Security"]))[0]["db_data_table_midfix"]
        prefix = self.read_data_subtypes(self.data_subtypes_db_dict([None, sec_type]))[0]["db_data_table_prefix"]

        if sec_type == "Stocks":
            volume = ", volume = %(volume)s" if isUpdate else ", volume "
        elif sec_type == "ETFs":
            volume = ", volume = %(volume)s" if isUpdate else ", volume "
        elif sec_type == "Indices":
            volume = " "
        else:
            volume = None

        return prefix + "_" + midfix + "_" + freq, volume

    def read_price_frequency(self):
        return self.execute_fetch("SELECT freq FROM price_freq")

    def read_sei_price(self, price_db_dict):
        begin_time = price_db_dict.value_dict["begin_time"]
        end_time = price_db_dict.value_dict["end_time"]
        security_type = price_db_dict.value_dict["securities_type"]
        table, volume = self.get_sei_table_volume(security_type, price_db_dict.value_dict["freq"])

        if table is None or volume is None:
            return []

        query = "SELECT id, securities_id, date_time, open, high, low, close, adj_close" + volume + \
                "FROM " + table + " WHERE securities_id = %(securities_id)s "
        if begin_time is not None:
            query += "AND date_time >= %(begin_time)s "
        if end_time is not None:
            query += "AND date_time <= %(end_time)s "
        query += "ORDER BY date_time DESC"

        dict_list = self.execute_fetch(query, price_db_dict.value_dict)
        data_keys = ["date_time", "open", "high", "low", "close", "adj_close"]
        if security_type not in ["Indices"]:
            data_keys.append("volume")
        dict_list.insert(0, data_keys)
        return dict_list

    def read_sei_data(self, data_db_dict):
        security_type = data_db_dict.value_dict["securities_type"]

        if security_type in ["Indices"]:
            return False

        begin_time = data_db_dict.value_dict["begin_time"]
        end_time = data_db_dict.value_dict["end_time"]

        query = "SELECT id, securities_id, date_time, dividend, splits, shares_float, shares_short, " \
                "shares_outstanding, aum FROM se_market_data WHERE securities_id = %(securities_id)s "
        if begin_time is not None:
            query += "AND date_time >= %(begin_time)s "
        if end_time is not None:
            query += "AND date_time <= %(end_time)s "
        query += "ORDER BY date_time DESC"

        dict_list = self.execute_fetch(query, data_db_dict.value_dict)

        data_keys = ["date_time", "dividend", "splits", "shares_float", "shares_short"]
        if security_type == "Stocks":
            data_keys.append("shares_outstanding")
        elif security_type == "ETFs":
            data_keys.append("aum")

        dict_list.insert(0, data_keys)
        return dict_list

    '''
    Special purpose function for "insert on duplicate key update" for possibly large amount of data
    Data common to all rows is passed as parameter instead of copied in each dict
    '''
    # TODO check for duplicate date_time
    # TODO check time intervals are appropriate. 1D and higher have database date types. Under 1D have datetime types
    def insert_or_update_sei_price(self, dict_list, freq, securities_type, securities_id):
        table, volume = self.get_sei_table_volume(securities_type, freq)
        vol_key = ")" if volume == " " else ", %(volume)s)"

        return self.execute_commit(
            "INSERT INTO " + table + " (securities_id, date_time, open, high, low, close, adj_close" + volume +
            ") VALUES (" + str(securities_id) + ", %(date_time)s, %(open)s, %(high)s, %(low)s, %(close)s, %(adj_close)s"
            + vol_key + " ON DUPLICATE KEY UPDATE open = %(open)s, high = %(high)s, low = %(low)s, close = %(close)s, "
            "adj_close = %(adj_close)s", dict_list, execute_many=True)

    def insert_sei_price(self, db_dict):
        freq = db_dict.value_dict["freq"]

        if self.time_interval_check([db_dict], freq):
            table, volume = self.get_sei_table_volume(db_dict.value_dict["securities_type"], freq)
            vol_key = ")" if volume == " " else ", %(volume)s)"

            return self.execute_commit("INSERT INTO " + table + " (securities_id, date_time, open, high, low, close, "
                                        "adj_close" + volume + ") VALUES (%(securities_id)s, %(date_time)s, %(open)s, "
                                       "%(high)s, %(low)s, %(close)s, %(adj_close)s" + vol_key, db_dict.value_dict)
        else:
            return "The insert date time field is not a " + freq + " interval."

    def insert_sei_data(self, db_dict):
        return self.execute_commit("INSERT INTO se_market_data (securities_id, date_time, dividend, splits, "
                                   "shares_float, shares_short, shares_outstanding, aum) "
                                   "VALUES (%(securities_id)s, %(date_time)s, %(dividend)s, %(splits)s, "
                                   "%(shares_float)s, %(shares_short)s, %(shares_outstanding)s, %(aum)s)",
                                   db_dict.value_dict)

    def update_sei_price(self, db_dict_list):
        freq = db_dict_list[0].value_dict["freq"]

        if self.time_interval_check(db_dict_list, freq):
            table, volume = self.get_sei_table_volume(db_dict_list[0].value_dict["securities_type"], freq, True)

            return self.execute_commit(
                "UPDATE " + table + " SET date_time = %(date_time)s, open = %(open)s, high = %(high)s, low = %(low)s, "
                "close = %(close)s, adj_close = %(adj_close)s" + volume + " WHERE id = %(id)s",
                DBDict.to_list_of_value_dict(db_dict_list), execute_many=True)
        else:
            return "One or more date time fields is not a " + freq + " interval."

    def update_sei_data(self, db_dict_list):
        return self.execute_commit(
            "UPDATE se_market_data SET date_time = %(date_time)s, dividend = %(dividend)s, splits = %(splits)s, "
            "shares_float = %(shares_float)s, shares_short = %(shares_short)s, "
            "shares_outstanding = %(shares_outstanding)s, aum = %(aum)s WHERE id = %(id)s",
            DBDict.to_list_of_value_dict(db_dict_list), execute_many=True)

    ####################################################################################################################
    # IEX Cloud
    ####################################################################################################################
    @staticmethod
    def iex_cloud_token_db_dict(data_list=None, reject_lol=None):
        return DBDict(key_list=["token", "type", "env"], data_list=data_list, reject_lol=reject_lol)

    def read_iex_api_tokens(self, db_dict=None):
        if db_dict is None:
            return self.execute_fetch("SELECT token, type, env FROM iex_api_tokens")
        else:
            return self.execute_fetch("SELECT token, type, env FROM iex_api_tokens "
                                      "WHERE type = %(type)s and env = %(env)s", db_dict.value_dict)

    def update_iex_api_tokens(self, db_dict_list):
        return self.execute_commit("UPDATE iex_api_tokens SET token = %(token)s WHERE type = %(type)s AND env = %(env)s",
                                   DBDict.to_list_of_value_dict(db_dict_list), execute_many=True)

    '''
        major_endpoints; ["Stock", "Corporate Actions", "Market Info", "Treasuries", "Commodities", "Economic Data",
         "Reference Data"] 
    '''
    def save_iex_data_to_db(self, major_endpoint, endpoint, data_list):
        res = False

        if major_endpoint == "Stock":
            pass
        elif major_endpoint == "Corporate Actions":
            pass
        elif major_endpoint == "Market Info":
            pass
        elif major_endpoint == "Treasuries":
            pass
        elif major_endpoint == "Commodities":
            pass
        elif major_endpoint == "Economic Data":
            pass
        elif major_endpoint == "Reference Data":
            pass

        if res is False:
            return major_endpoint + ", " + endpoint + " save function not set."
        else:
            return res
    
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

        return [RealEstate(None, None, None, None, None, None, db_dict=d) for d in dict_list]

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

        return [ServiceProvider(None, None, db_dict=d) for d in dict_list]

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

        data_list = []
        for d in dict_list:
            data_list.append(RealPropertyValues(None, None, None, None, None, db_dict=d))

        return data_list

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

        Works for real_estate_id and service_provider_id fields

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

        re_dict, sp_dict = {}, {}
        if has_real_estate:
            re_dict = self.real_estate_read(
                wheres=[["id", "in", list(set([d["real_estate_id"] for d in dict_list]))]])
            re_dict = {real_estate.id: real_estate for real_estate in re_dict}
        if has_service_provider:
            sp_dict = self.service_provider_read(
                wheres=[["id", "in", list(set([d["service_provider_id"] for d in dict_list]))]])
            sp_dict = {service_provider.id: service_provider for service_provider in sp_dict}

        if has_real_estate or has_service_provider:
            for d in dict_list:
                if has_real_estate:
                    d["real_estate"] = re_dict[d["real_estate_id"]]
                if has_service_provider:
                    d["service_provider"] = sp_dict[d["service_provider_id"]]

        return dict_list

    def solar_bill_data_read(self, wheres=(), order_bys=()):
        """ Read all fields from solar_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[SolarBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("solar_bill_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        bill_list = []
        for d in dict_list:
            bill_list.append(SolarBillData(None, None, None, None, None, None, None, None, None, None, None, None,
                                           db_dict=d))

        return bill_list

    def solar_bill_data_insert(self, bill_list):
        """ Insert into solar_bill_data table

        Args:
            bill_list (list[SolarBillData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("solar_bill_data", bill_list)

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

    def electric_bill_data_read(self, wheres=(), order_bys=()):
        """ Read all fields from electric_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[ElectricBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("electric_bill_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        bill_list = []
        for d in dict_list:
            bill_list.append(ElectricBillData(None, None, None, None, None, None, None, None, None, None, None, None,
                                              None, db_dict=d))

        return bill_list

    def electric_bill_data_insert(self, bill_list):
        """ Insert into electric_bill_data table

        Args:
            bill_list (list[ElectricBillData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("electric_bill_data", bill_list)

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

        data_list = []
        for d in dict_list:
            data_list.append(ElectricData(None, None, None, None, None, None, None, db_dict=d))

        return data_list

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

    def natgas_bill_data_read(self, wheres=(), order_bys=()):
        """ Read all fields from natgas_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[NatGasBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("natgas_bill_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        bill_list = []
        for d in dict_list:
            bill_list.append(NatGasBillData(None, None, None, None, None, None, None, None, None, None, None, None,
                                            None, None, None, None, None, None, db_dict=d))

        return bill_list

    def natgas_bill_data_insert(self, bill_list):
        """ Insert into natgas_bill_data table

        Args:
            bill_list (list[NatGasBillData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("natgas_bill_data", bill_list)

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

        data_list = []
        for d in dict_list:
            data_list.append(NatGasData(None, None, None, None, None, None, None, None, None, None, db_dict=d))

        return data_list

    def natgas_data_insert(self, data_list):
        """ Insert into natgas_data table

        Args:
            data_list (list[NatGasData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("natgas_data", data_list)

    def simple_bill_data_insert(self, bill_list):
        """ Insert into simple_bill_data table

        Args:
            bill_list (list[SimpleServiceBillData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("simple_bill_data", bill_list)

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

    def simple_bill_data_read(self, wheres=(), order_bys=()):
        """ Read all fields from simple_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[SimpleServiceBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("simple_bill_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        bill_list = []
        for d in dict_list:
            bill_list.append(SimpleServiceBillData(None, None, None, None, None, db_dict=d))

        return bill_list

    def mortgage_bill_data_insert(self, bill_list):
        """ Insert into mortgage_bill_data table

        Args:
            bill_list (list[MortgageBillData]):

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        self.dictinsertable_insert("mortgage_bill_data", bill_list)

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

    def mortgage_bill_data_read(self, wheres=(), order_bys=()):
        """ Read all fields from mortgage_bill_data table

        Args:
            see QueryWriter

        Returns:
            list[MortgageBillData]: list will be empty if no bill data found matching wheres

        Raises:
            MySQLException: if database read issue occurs
        """
        qw = QueryWriter("mortgage_bill_data", wheres=wheres, order_bys=order_bys)
        query, params = qw.write_read_query()

        dict_list = self.execute_fetch(query, params=params)
        dict_list = self._help_read_fk(dict_list)

        bill_list = []
        for d in dict_list:
            bill_list.append(MortgageBillData(None, None, None, None, None, None, None, None, None, None, None,
                                              db_dict=d))

        return bill_list