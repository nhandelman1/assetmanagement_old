"""Module for base class for MySQL database connections. """
import mysql.connector
import pandas as pd
import traceback
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union
from database.mysqlexception import MySQLException
from database.querywriter import QueryWriter
from logging.Logger import Logger


class DictInsertable(ABC):
    """ Classes that implement this class can call MySQLBase.dictinsertable_insert() function """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def to_insert_dict(self):
        """ Convert class to dict that can be inserted into a table

        Returns:
            dict: copy of self.__dict__ with any changes specified by subclass
        """
        raise NotImplementedError("to_insert_dict() not implemented by subclass")


class FetchCursor(Enum):
    """ Indicate to MySQL API classes how data loaded from tables should be returned

    Very often, data returned from a fetch as a list(list) or list(dict) is converted to a pd.DataFrame. Use this enum
    indicator to have MySQLBase.execute_fetch() return data as specified.

    PD_DF: use pd.read_sql(). data returned as a pd.DataFrame. Empty dataframe will have column headers.
    LIST_DICT: return data as list(dict), directly from dictionary cursor. No data returns empty list.
    LIST_LIST: return data as list(list), directly from cursor. No data returns empty list.
    """
    PD_DF = "pandas_dataframe"
    LIST_DICT = "list_dict"
    LIST_LIST = "list_list"


class MySQLBase(ABC):
    """Base class for MySQL database connections.

    This class contains functionality common to all MySQL database interactions. Init creates a database connection and
    creates a default cursor and a dictionary cursor. This class and subclasses can be instantiated as part of a
    context manager (i.e. with).

    Attributes:
        host (str): database host url.
        user (str): database user name.
        password (str): database password.
        db_name (str): database name.
        _fetch_cursor (FetchCursor): how data loaded from tables is returned. no guarantee that subclasses will handle
            all enums of FetchCursor properly so this variable is "private" to indicate it shouldn't be set directly.
        logger (Logger.logger instance):.
        cursor (mysql.connector.CMySQLCursor): rows returned as list.
        dict_cursor (mysql.connector.CMySQLCursor): rows returned as dictionary.
    """

    def __init__(self, host, user, password, db_name, fetch_cursor, ssl_ca_path=None):
        """Init MySQLBase. Create mysql database connection, cursor and dictionary cursor.

        Args:
            host (str): database host url.
            user (str): database user name.
            password (str): database password.
            db_name (str): database name.
            fetch_cursor (FetchCursor): how data loaded from tables is returned
            ssl_ca_path (Optional[str]): full path to ssl certificate authority file. Default None for no certificate

        Raises:
            MySQLException: database connection or cursor creation error is logged then raised as MySQLException with
                is_logged=True.
        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self._fetch_cursor = fetch_cursor
        self.ssl_ca_path = ssl_ca_path

        self.logger = Logger(self.__class__.__name__).logger

        self._DB = None
        self.cursor = None
        self.dict_cursor = None

        self._db_initialize()

    def __enter__(self):
        """ Context manager __enter__.

        Returns:
            MySQLBase: self instance of MySQLBase
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Context manager __exit__. Close database connection and log exception arguments if not None. """
        self.db_close()

        if exc_type is not None:
            self.logger.error("".join(traceback.format_exception(exc_type, exc_val, exc_tb)))

    def __del__(self):
        """ Close database connection.

        Python does not guarantee that __del__ will be called on "destruction" of the object. User should always call
        db_close explicitly if not using the class instance in a context manager
        """
        self.db_close()

    def _db_initialize(self):
        """ Create db connection and cursors if not already created and connected

        Raises:
            MySQLException: mysql.connector.Error during database connect or cursor create is logged then raised as
                MySQLException with is_logged=True
        """
        create_cursor = False
        if self._DB is None or not self._DB.is_connected():
            try:
                self._DB = mysql.connector.connect(host=self.host, user=self.user, passwd=self.password,
                                                   database=self.db_name, ssl_ca=self.ssl_ca_path,
                                                   ssl_verify_cert=(self.ssl_ca_path is not None))
                create_cursor = True
            except mysql.connector.Error as err:
                self.logger.exception("DB Connect exception")
                raise MySQLException(str(err) + " See log for full trace.") from err

        if create_cursor or self.cursor is None:
            try:
                self.cursor = self._DB.cursor()
            except mysql.connector.Error as err:
                self.logger.exception("Cursor create exception")
                raise MySQLException(str(err) + " See log for full trace.") from err

        if create_cursor or self.dict_cursor is None:
            try:
                self.dict_cursor = self._DB.cursor(dictionary=True)
            except mysql.connector.Error as err:
                self.logger.exception("Dict Cursor create exception")
                raise MySQLException(str(err) + " See log for full trace.") from err

    def build_alias_dict(self, fields, orig_upper: bool = False):
        """ Create dict mapping original fields (to uppercase) to aliases or original field

        Map original fields (tick marks removed, to uppercase) to aliases (if any, tick marks removed) or original
        fields (tick marks removed, if no aliases).

        Args:
            fields (Union[str, list[str], list[list]]): query fields. can either be a str or a list of any combination
                of lists (with exactly 2 str elements) or str
            orig_upper (boolean): True: in the returned dict, if value in each key:value pair is the original
                field, convert it to uppercase. Default False for no change

        Returns:
            dict: mapping original fields (to uppercase) to aliases or original fields
        """
        alias_dict = {}
        if isinstance(fields, (list, tuple)):
            for f in fields:
                if isinstance(f, (list, tuple)):
                    alias_dict[f[0].replace("`", "").upper()] = f[1].replace("`", "")
                else:  # isinstance str
                    fld = f.replace("`", "").upper() if orig_upper else f.replace("`", "")
                    alias_dict[f.replace("`", "").upper()] = fld
        else:  # isinstance str
            fld_list = fields.split(",")
            for f in fld_list:
                as_pos = f.upper().find(" AS ")
                if as_pos > -1:
                    alias_dict[f[0:as_pos].strip().replace("`", "").upper()] = f[as_pos + 4:].strip().replace("`", "")
                else:
                    fld = f.replace("`", "").upper() if orig_upper else f.replace("`", "")
                    alias_dict[f.replace("`", "").upper()] = fld

        return alias_dict

    def db_close(self):
        """Close cursor and dict_cursor and mysql database connection.

        Close cursors then close database connection.
        DB must be connected to close cursors. This usually isn't a problem, but calling this function from __del__
        causes an exception.

        Raises:
            MySQLException: cursor or database close error is logged then raised as MySQLException with
                is_logged=True.
        """
        try:
            if self._DB is not None and self._DB.is_connected():
                if self.cursor is not None:
                    self.cursor.close()
                if self.dict_cursor is not None:
                    self.dict_cursor.close()

                self._DB.close()
        except mysql.connector.Error as err:
            self.logger.exception("DB and cursor close exception")
            raise MySQLException(str(err) + " See log for full trace.") from err

    def execute_fetch(self, query, params=None, cursor=None):
        """Execute read query and return query results

        Args:
            query (str): SQL query.
            params (Optional[tuple, dict]): query parameters. Default None.
            cursor (Optional[boolean]): None to use self.dict_cursor. Any other value to use self.cursor. Default None.

        Returns:
            Union[list[list], list[dict], pd.DataFrame]: Results of the query and fetch depending on self._fetch_cursor

        Raises:
            MySQLException: cursor execute mysql.connector.Error is logged then raised as MySQLException with
                is_logged=True
        """
        # check db connection and cursor creation and recreate if not connected or created
        self._db_initialize()

        try:
            if self._fetch_cursor == FetchCursor.PD_DF:
                df_or_list = pd.read_sql(query, self._DB, params=params)
            else:  # FetchCursor.LIST_DICT or FetchCursor.LIST_LIST
                cursor = self.dict_cursor if cursor is None else self.cursor
                cursor.execute(query, params)
                df_or_list = cursor.fetchall()
        except mysql.connector.Error as err:
            self.logger.exception("Execute fetch exception")
            raise MySQLException(str(err) + " See log for full trace.") from err

        return df_or_list

    def execute_commit(self, query_list, params_list, execute_many: bool = False):
        """Execute one or more insert, update and/or delete then commit.

        Multi-purpose execute and commit function. Can be used to execute and commit the following cases:
            1. a single query and a single element of parameters
            2. a single query and a list of parameter elements
            3. a list of queries corresponding sequentially to list of parameter elements. The ith query corresponds
                to the ith parameter element

        Args:
            query_list (Union[str, list[str]]): a single query str or a list of query strs.
            params_list (Union[tuple, dict, list[tuple], list[dict]]): query parameters.
            execute_many (boolean): True to execute the first query in query_list on every element of params_list.
                False to execute the ith query in query_list on the ith element of params_list.

        Raises:
            ValueError: execute_many is not True but lengths of query_list and params_list are not equal.
            MySQLException: execute or commit error is logged, a rollback is attempted and the mysql.connector.Error is
                wrapped and returned.
        """
        # check db connection and cursor creation and recreate if not connected or created
        self._db_initialize()

        if isinstance(query_list, str):
            query_list = [query_list]
        if isinstance(params_list, (tuple, dict)):
            params_list = [params_list]

        try:
            if execute_many:
                self.cursor.executemany(query_list[0], params_list)
            else:
                if len(query_list) != len(params_list):
                    raise ValueError("Query List and Value List of Dictionaries have different lengths")

                for i in range(len(query_list)):
                    self.cursor.execute(query_list[i], params_list[i])

            self._DB.commit()
        except mysql.connector.Error as err1:
            self.logger.exception("Execute commit exception: ")
            self.db_rollback(err1)

    def db_commit(self):
        """ Convenience function for self._DB.commit() """
        self._DB.commit()

    def db_rollback(self, err1):
        """Rollback database changes that have not been committed.

        Args:
            err1 (Exception): the error warranting the rollback.

        Raises:
            MySQLException: If rollback is successful, a new error containing a rollback success message and err1
                is raised. If rollback is not successful, rollback error is logged and a new error containing err1 and
                the rollback error is raised.
        """
        try:
            self._DB.rollback()
            raise MySQLException("Rollback successful. Error requiring rollback: " + format(err1))
        except mysql.connector.Error as err2:
            self.logger.exception("DB rollback exception")
            raise MySQLException(format(err1) + "\nRollback Failed\n" + format(err2))

    def dictinsertable_insert(self, table, di_list, ignore=None):
        """ Classes that implement DictInsertable can call this function for insert queries

        Args:
            table (str): table to insert into
            di_list (list[DictInsertable]):
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Raises:
            MySQLException: if any required columns are missing or other database issue occurs
        """
        if len(di_list) == 0:
            return

        di_list = [b.to_insert_dict() for b in di_list]

        qw = QueryWriter(table, fields=list(di_list[0].keys()))
        query, di_list = qw.write_insert_query(di_list, ignore=ignore)

        self.execute_commit(query, params_list=di_list, execute_many=True)

    @property
    def fetch_cursor(self):
        return self._fetch_cursor

    @fetch_cursor.setter
    def fetch_cursor(self, fetch_cursor):
        """ Set self._fetch_cursor

        Subclasses should override this function to prevent self._fetch_cursor from being set to a value they do not
        support.

        Args:
            fetch_cursor (FetchCursor):
        """
        self._fetch_cursor = fetch_cursor