import datetime
from enum import Enum
from typing import Optional, Union


class QueryWriter:
    """ Formatter for simple single table queries

    Attributes:
        see __init__ docstring
    """
    def __init__(self, table, fields=None, distinct=None, wheres=None, order_bys=None, limit=None,
                 date_to_int_date=None, fields_extra=None):
        """ init QueryWriter

        Args:
            table (str): a single table name
            fields (Optional[str, list[str], list[list[str, str]]]): Default None. None, (), [] all assume "*". See
                self.select_stmt(). None, (), [], "*", str not allowed for update statement.
            distinct (Optional[boolean]): True to include distinct keyword in query. Default None for False.
            wheres (Optional[str, list[Union[list[str, str, str], str]]]): See where_clause().
                Default None for no where clause. str not allowed for update statement
            order_bys (Optional[str, list[str]]): See order_by_stmt(). Default None for no order by statement
            limit (Optional[int]): Default None for no limit statement
            date_to_int_date (Optional[boolean]): table may use INT type with format YYYYMMDD for dates instead of the
                DATE type. True to convert datetime.date elements to int with format YYYYMMDD in select where stmt,
                update parameters (both set and where params) and insert parameters. Default None for no conversions
            fields_extra (Optional[str, list[str]]): Default None. Certain queries allow for two sets of fields to be
                applied (e.g. INSERT INTO ... ON DUPLICATE UPDATE ..., possibly others)
        """
        if fields in (None, (), []):
            fields = "*"
        if distinct not in (True, False):
            distinct = False
        if wheres is None:
            wheres = ()
        if order_bys in (None, (), []):
            order_bys = ""
        if limit is None:
            limit = 0
        if date_to_int_date is None:
            date_to_int_date = False

        self.table = table
        self.fields = fields
        self.distinct = distinct
        self.wheres = wheres
        self.order_bys = order_bys
        self.limit = limit
        self.date_to_int_date = date_to_int_date
        self.fields_extra = fields_extra

    def select_stmt(self):
        """ Compile SELECT statement and return as str

        self.fields can have the following formats:
            str: use fields directly in query. SELECT keyword prepended to this str
            list(str): multiple columns (no AS part). e.g. ["col1", "col2"] yields 'SELECT col1, col2'
            list(list): list of [col, as_col (optional)].
                e.g. [["col1"], ["col2", "c2"]] yields 'SELECT col1, col2 AS c2'

        Returns:
            str: SELECT statement

        Raises:
            TypeError: fields is not in a valid format
        """
        if isinstance(self.fields, str):
            select_str = self.fields
        elif isinstance(self.fields, (list, tuple)):
            select_str = ""
            for field in self.fields:
                if isinstance(field, str):
                    select_str += (field + ", ")
                elif isinstance(field, (list, tuple)):
                    select_str += field[0]
                    if len(field) == 2 and field[1] is not None:
                        select_str += (" AS " + field[1])
                    select_str += ", "
                else:
                    raise TypeError(str(type(field)) + " is not a valid fields element type")

            select_str = select_str[:-2]
        else:
            raise TypeError(str(type(self.fields)) + " is not a valid fields type")

        if self.distinct:
            select_str = "DISTINCT " + select_str

        return "SELECT " + select_str

    def where_clause(self):
        """ Compile WHERE clause and parameters

        self.wheres can have the following formats:
            str: use where_list directly in query. WHERE keyword is prepended to this str. params will return ()
            list(list, str): list alternates with list or str. [["col1", "comp", vals], "kw", ["col2", "comp", vals]]
            "comp": =, <, >, <=, >=, like, in, not in, not like, is, is not (case insensitive)
            vals: Element or list(Element). Element must be of a type that mysql.connector can use directly. If
                Element is a str and the first and last characters are both single ^ caret, both ^ carets are
                dropped and the remaining str is considered a column name. Otherwise, this function does not attempt to
                make any implicit conversion (e.g. str(Element)). It may make explicit conversions as required by this
                class's attributes.
            "kw" (optional): SQL keywords, "and" (default), "or", "(", ")" (case insensitive). ")" can be followed by
                "and" or "or". If ")" is followed by a list, "and" is appended after ")"

        If self.date_to_int_date is True and vals is datetime.date or list/tuple that contains datetime.date elements,
        convert all datetime.date elements to "YYYYMMDD" format
        If vals is an Enum or list/tuple that contains Enum elements, apply .value to each Enum element
        Logically, "in" an empty list is always False and "not in" an empty list is always True

        If comp is "is" or "is not", vals must be None

        Examples: self.wheres -> query str, params tuple
            [["col1", "<", 1], "or", ["col2", "=", "asdf"]] -> "WHERE col1 < %s or col2 = %s", (1, "asdf")
            [["col1", ">=", datetime.date(year=2000, month=1, day=1)]] (self.date_to_int_date == True)
                -> "WHERE col1 <= %s", (20000101,)
            [["col1", "not in", [5,6,7]], ["col2", "in", ()]] ->
                "WHERE col1 not in (%s, %s, %s) and 1=2", (5, 6, 7)
            [["col1", "=", "^col2^"]] -> "WHERE col1 = col2", ()
                in contrast to: [["col1", "=", "col2"]] -> "WHERE col1 = %s", ("col2")
        Returns:
            tuple[str, tuple]: (query, params)

        Raises:
            TypeError: wheres is not in a valid format
        """
        where_str = ""
        params = ()
        keyword_is_next = False

        if isinstance(self.wheres, str):
            where_str = self.wheres
        elif isinstance(self.wheres, (list, tuple)):
            for cond in self.wheres:
                if isinstance(cond, str):
                    if cond.lower() in ("or", "(", ")"):
                        where_str += (" " + cond.upper())
                    else:
                        where_str += " AND"
                    keyword_is_next = cond == ")"
                elif isinstance(cond, (list, tuple)):
                    if keyword_is_next:
                        where_str += " AND"

                    # avoid 'in' keyword followed by empty list. e.g. 'field in ()'.
                    # mysql syntax does not allow this. logically this always evaluates to false
                    if cond[1].lower() == "in" and len(cond[2]) == 0:
                        where_str += " 1=2 "
                    # avoid 'not in' keyword followed by empty list. e.g. 'field not in ()'.
                    # mysql syntax does not allow this. logically this always evaluates to true
                    elif cond[1].lower() == "not in" and len(cond[2]) == 0:
                        where_str += " 1=1 "
                    elif cond[1].lower() in ("is", "is not"):
                        if cond[2] is not None:
                            raise TypeError("'is' and 'is not' must have val None")
                        if cond[1].lower() == "is":
                            where_str += (" " + cond[0] + " is null ")
                        else:  # cond[1].lower() == "is not"
                            where_str += (" " + cond[0] + " is not null ")
                    else:
                        is_col = False
                        where_str += (" " + cond[0] + " " + cond[1].upper() + " ")
                        if cond[1].lower() in ("in", "not in"):
                            where_str += "(" + ",".join(["%s"] * len(cond[2])) + ")"
                        elif isinstance(cond[2], str) and len(cond[2]) > 2 and cond[2][0] == "^" and \
                                cond[2][-1] == "^":
                            is_col = True
                            where_str += cond[2][1:-1]
                        else:
                            where_str += "%s"

                        if isinstance(cond[2], (list, tuple)):
                            cond_temp = []
                            for el in cond[2]:
                                if isinstance(el, bool):
                                    # True and False must be changed to 1 and 0 since mysql does not have bool type
                                    cond_temp.append(int(el))
                                elif self.date_to_int_date and isinstance(el, datetime.date):
                                    cond_temp.append(el.strftime("%Y%m%d"))
                                elif isinstance(el, Enum):
                                    cond_temp.append(el.value)
                                else:
                                    cond_temp.append(el)

                            cond[2] = tuple(cond_temp) if isinstance(cond[2], tuple) else cond_temp
                            params += tuple(cond[2])
                        elif not is_col:
                            if isinstance(cond[2], bool):
                                # True and False must be changed to 1 and 0 since mysql does not have bool type
                                cond[2] = int(cond[2])
                            elif self.date_to_int_date and isinstance(cond[2], datetime.date):
                                cond[2] = cond[2].strftime("%Y%m%d")
                            elif isinstance(cond[2], Enum):
                                cond[2] = cond[2].value

                            params += (str(cond[2]),)

                    keyword_is_next = True
                else:
                    raise TypeError(str(type(cond)) + " is not a valid wheres condition type")
        else:
            raise TypeError(str(type(self.wheres)) + " is not a valid wheres type")

        if where_str != "":
            where_str = "WHERE " + where_str

        return where_str, params

    def order_by_stmt(self):
        """ Compile 'ORDER BY' statement and return as str

        self.order_bys can have the following formats:
            str: use order_bys directly in query. ORDER BY keyword prepended to this str
            list(str): put "DESC" (case insensitive) as next element after column for descending on that column
                e.g. ["col1", "col2", "DESC", "col3"] yields 'ORDER BY col1, col2 DESC, col3'

        Returns:
            str: ORDER BY statement

        Raises:
            TypeError: order_bys is not in a valid format
        """
        if isinstance(self.order_bys, str):
            ob_str = self.order_bys
        elif isinstance(self.order_bys, (list, tuple)):
            ob_str = ""
            for ob in self.order_bys:
                if ob.lower() == "desc":
                    ob_str += " DESC"
                else:
                    ob_str += (", " + ob)
            ob_str = ob_str[2:]
        else:
            raise TypeError(str(type(self.fields)) + " is not a valid fields type")

        if ob_str != "":
            ob_str = "ORDER BY " + ob_str

        return ob_str

    def write_read_query(self):
        """ Compile full read query as a str and query parameters as a tuple

        FROM and LIMIT statements are applied in this function.

        Returns:
            tuple[str, tuple]: (query, params)
        """
        where_str, params = self.where_clause()
        query = self.select_stmt() + " FROM " + self.table + " " + where_str + " " + self.order_by_stmt()
        if int(self.limit) > 0:
            query += " LIMIT " + str(self.limit)
        query += ";"

        return query, params

    def write_insert_query(self, insert_list, ignore=None):
        """ Compile insert query

        enum values in insert_list have .value applied
        datetime.date values converted to int if self.date_to_int_date == True

        Args:
            insert_list (Union[list[list], list[dict]]): insert values. if list, each list must have the same number of
                elements as self.fields, if dict, each dict must have the same keys as in self.fields
            ignore (Optional[boolean]): True to use insert ignore statement. Default None for False to use insert

        Returns:
            tuple[str, Union[list[list], list[dict]]]:
                (str query or "0" if insert_list is empty, insert_list with changes applied)

        Raises:
            ValueError: if any dict or list in insert_list does not match self.fields
            NotImplementedError: if self.fields is a str
        """
        # noinspection PyTypeChecker
        if len(insert_list) == 0:
            return "0", []

        if isinstance(self.fields, str):
            raise NotImplementedError("self.fields as str not implemented")

        if ignore is None:
            ignore = False

        if isinstance(insert_list[0], list):
            # noinspection PyTypeChecker
            if any([len(lst) != len(self.fields) for lst in insert_list]):
                raise ValueError("Each list in insert_list must have the same number of elements as self.fields")
            # noinspection PyTypeChecker
            insert_values_str = ("%s, " * len(self.fields))[0:-2]
        else:  # isinstance dict
            f_set = set(self.fields)
            # noinspection PyTypeChecker
            if any([set(d) != f_set for d in insert_list]):
                raise ValueError("Each dict in insert_list must have dict.keys() equal to self.fields")
            # noinspection PyTypeChecker
            insert_values_str = ", ".join(["%(" + f + ")s" for f in self.fields])

        query = "INSERT " + ("IGNORE" if ignore else "") + " INTO " + self.table + " (" + ", ".join(self.fields) + \
                ") VALUES (" + insert_values_str + ")"

        date_cols = []
        enum_cols = []
        for k, value in enumerate(insert_list[0]) if isinstance(insert_list[0], list) else insert_list[0].items():
            if isinstance(value, datetime.date) and self.date_to_int_date:
                date_cols.append(k)
            if isinstance(value, Enum):
                enum_cols.append(k)

        if len(date_cols) > 0 or len(enum_cols) > 0:
            for l_or_d in insert_list:
                for col in date_cols:
                    try:
                        l_or_d[col] = int(l_or_d[col].strftime("%Y%m%d"))
                    except AttributeError:
                        pass
                for col in enum_cols:
                    try:
                        l_or_d[col] = l_or_d[col].value
                    except AttributeError:
                        pass

        return query, insert_list

    def write_update_query(self, set_params, where_params=None, objects=()):
        # TODO allow "in" and "not in" in where clause
        """ Compile update query with optional where clause and parameter lists

        If self.wheres is a list of lists, the element at position 2 in each sub list is ignored. Put those elements
        in where_params at the corresponding sub list position or use objects
        "in" and "not in" not allowed in where clause
        any Enum values in set_params and where_params will have .value applied.
        objects can be provided as a convenient way to populate set_params and where_params

        Args:
            set_params (list[list]): list of lists of set values. If where_params is not None, must have same number
                of sub lists as where_params
            where_params (Optional[list[list]]): list of list of where parameters. If not None, must have same number
                of sub lists as set_params. Default None
            objects (list[object]): Default (). If length of list is greater than 0:
                Overwrite set_params using data from each object according to values in self.fields.
                Also, if where_params is None, compile where_params from each object according to self.wheres.

        Returns:
            tuple[str, list[list]]: (str query, list(list) params). If query == "0", then set_params and objects both
                had length 0

        Raises:
            AttributeError: if length of objects > 0 and a field in self.fields or self.wheres conditions is not found
                as an instance variable in any object in objects
            ValueError: if self.fields or self.wheres or set_params or where_params are not valid

        Example:
            The following will run the same query twice but with different parameter values
            self.table = "securities", self.fields = ["field1", "field2"]
            self.wheres = [["field1", "=", val_ignored], "or", ["field3", 'like", "val_ignored"]]
            set_params = [["val11", val12], ["val21", val22"]]
            where_params = [[where11, "where12"], [where21, "where22"]]

            query = "UPDATE securities SET field1 = %s, field2 = %s WHERE field1 = %s or field3 like %s;
            params = [["val11", val12, where11, "where12"], ["val21", val22, where21, "where22"]]
        """
        if self.fields in [None, [], ()] or isinstance(self.fields, str):
            raise ValueError("fields must be a list of str field names in table " + self.table)
        if isinstance(self.wheres, str):
            raise ValueError("wheres must use the list format instead of str format")

        if len(objects) > 0:
            set_params = []
            for obj in objects:
                set_params.append([getattr(obj, f) for f in self.fields])

            if where_params is None:
                where_params = []
                for obj in objects:
                    where_params.append([getattr(obj, clause[0]) for clause in self.wheres])

        if len(set_params) == 0:
            return "0", ()

        # noinspection PyTypeChecker
        if where_params is not None and len(set_params) != len(where_params):
            raise ValueError("Number of sub lists in set_params must equal number of sub lists in where_params")

        f_len = self.fields.count(" %s ") if isinstance(self.fields, str) else len(self.fields)
        for lst in set_params:
            if f_len != len(lst):
                raise ValueError("Number of parameters in all set_params sub lists must be " + str(f_len))

        where_str, params = self.where_clause()
        if where_str != "":
            where_str = where_str + " "
        if " in " in where_str:
            raise ValueError("'in' and 'not in' not allowed in where clause")
        w_len = where_str.count(" %s ")
        if where_params is not None and w_len != len(where_params[0]):
            raise ValueError("Number of parameters in all where_params sub lists must be " + str(w_len))

        query = "UPDATE " + self.table + " SET "
        if isinstance(self.fields, str):
            query += (self.fields + " ")
        else:
            for f in self.fields:
                query += (f + " = %s, ")
            query = query[:-2]
        query += (" " + where_str + ";")

        final_params = []
        if where_params is not None:
            for i in range(len(set_params)):
                final_params.append([x.value if isinstance(x, Enum) else x for x in set_params[i] + where_params[i]])

        if self.date_to_int_date:
            # all sub lists in final_params have the same order of data types. get position of datetime.date types
            # from first sub list
            date_cols = []
            for i, value in enumerate(final_params[0]):
                if isinstance(value, datetime.date):
                    date_cols.append(i)

            if len(date_cols) > 0:
                for lst in final_params:
                    for col in date_cols:
                        lst[col] = int(lst[col].strftime("%Y%m%d"))

        return query, final_params

    def write_insert_or_update_query(self):
        """ Compile 'insert into ... on duplicate key update ...' query

        Insert into table if primary key and unique keys are all not found. Update if any are found.
        If self.fields_extra is None, use fields for both the insert and update statements

        Returns:
            str: query
        """
        insert_values_str = ("%s, " * len(self.fields))[0:-2]

        update_fields = self.fields if self.fields_extra is None else self.fields_extra
        update_values_str = ""
        for field in update_fields:
            update_values_str += (field + "=VALUES(" + field + "), ")
        update_values_str = update_values_str[0:-2]

        query = "INSERT INTO " + self.table + " (" + ", ".join(self.fields) + ") VALUES (" + insert_values_str + ") "
        query += ("ON DUPLICATE KEY UPDATE " + update_values_str + ";")

        return query

    def write_delete_query(self, allow_delete_all=None):
        """ Compile full delete query as a str and query parameters as a tuple

        Args:
            allow_delete_all (Optional[boolean]): True to allow empty where clause. Default None for False.

        Returns:
            tuple[str, tuple]: (str query, tuple params). If where clause is empty and allow_delete_all is false,
                query == "".
        """
        if allow_delete_all is None:
            allow_delete_all = False

        where_str, params = self.where_clause()
        if where_str == "" and not allow_delete_all:
            return "", None

        query = "DELETE FROM " + self.table + " " + where_str + ";"

        return query, params