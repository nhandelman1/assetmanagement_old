import datetime
from enum import Enum


class QueryWriter:
    """ Formatter for simple single table queries

    Attributes: see __init__ docstring

    """
    def __init__(self, table, fields=None, distinct=False, wheres=(), order_bys=(), limit=0, date_to_int_date=False,
                 fields_extra=None):
        """ init QueryWriter

        Args:
            table (str): a single table name
            fields (str, list, optional): Default None. None, (), [] all assume "*". See select_stmt(). None, (), []
                and "*" not allowed for update statement.
            distinct (boolean, optional): include distinct keyword in query. Default False.
            wheres (str, list, optional): Default () (assumes no WHERE statement). See where_stmt()
            order_bys (str, list, optional): Default () (assumes no ORDER BY statement). See order_by_stmt()
            limit (int, optional): Default 0 (limit not applied)
            date_to_int_date (boolean, optional): table may use INT type with format YYYYMMDD for dates instead of the
                DATE type. True to convert datetime.date elements to int with format YYYYMMDD in select where stmt,
                update parameters (both set and where params) and insert parameters. Default False for no conversions
            fields_extra (str, list, optional): Default None. Certain queries allow for a two sets of fields to be
                applied (e.g. INSERT INTO ... ON DUPLICATE UPDATE ..., possibly others)
        """
        if fields in (None, (), []):
            fields = "*"
        if distinct not in (True, False):
            distinct = False
        if order_bys in (None, (), []):
            order_bys = ""

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
            str SELECT statement

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

    def where_stmt(self):
        """ Compile WHERE statement and parameters

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
            (str query, tuple params)

        Raises:
            TypeError: wheres is not in a valid format
        """
        where_str = ""
        params = ()
        keyword_is_next = False

        if isinstance(self.wheres, str):
            where_str = self.wheres
        elif isinstance(self.wheres, (list, tuple)):
            for clause in self.wheres:
                if isinstance(clause, str):
                    if clause.lower() in ("or", "(", ")"):
                        where_str += (" " + clause.upper())
                    else:
                        where_str += " AND"
                    keyword_is_next = clause == ")"
                elif isinstance(clause, (list, tuple)):
                    if keyword_is_next:
                        where_str += " AND"

                    # avoid 'in' keyword followed by empty list. e.g. 'field in ()'.
                    # mysql syntax does not allow this. logically this always evaluates to false
                    if clause[1].lower() == "in" and len(clause[2]) == 0:
                        where_str += " 1=2 "
                    # avoid 'not in' keyword followed by empty list. e.g. 'field not in ()'.
                    # mysql syntax does not allow this. logically this always evaluates to true
                    elif clause[1].lower() == "not in" and len(clause[2]) == 0:
                        where_str += " 1=1 "
                    elif clause[1].lower() in ("is", "is not"):
                        if clause[2] is not None:
                            raise TypeError("'is' and 'is not' must have val None")
                        if clause[1].lower() == "is":
                            where_str += (" " + clause[0] + " is null ")
                        else:  # clause[1].lower() == "is not"
                            where_str += (" " + clause[0] + " is not null ")
                    else:
                        is_col = False
                        where_str += (" " + clause[0] + " " + clause[1].upper() + " ")
                        if clause[1].lower() in ("in", "not in"):
                            where_str += "(" + ",".join(["%s"] * len(clause[2])) + ")"
                        elif isinstance(clause[2], str) and len(clause[2]) > 2 and clause[2][0] == "^" and \
                                clause[2][-1] == "^":
                            is_col = True
                            where_str += clause[2][1:-1]
                        else:
                            where_str += "%s"

                        if isinstance(clause[2], (list, tuple)):
                            clause_temp = []
                            for el in clause[2]:
                                if self.date_to_int_date and isinstance(el, datetime.date):
                                    clause_temp.append(el.strftime("%Y%m%d"))
                                elif isinstance(el, Enum):
                                    clause_temp.append(el.value)
                                else:
                                    clause_temp.append(el)

                            clause[2] = tuple(clause_temp) if isinstance(clause[2], tuple) else clause_temp
                            params += tuple(clause[2])
                        elif not is_col:
                            if self.date_to_int_date and isinstance(clause[2], datetime.date):
                                clause[2] = clause[2].strftime("%Y%m%d")
                            elif isinstance(clause[2], Enum):
                                clause[2] = clause[2].value

                            params += (str(clause[2]),)

                    keyword_is_next = True
                else:
                    raise TypeError(str(type(clause)) + " is not a valid wheres clause type")
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
            str ORDER BY statement

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

        Returns: (str query, tuple params)
        """
        where_str, params = self.where_stmt()
        query = self.select_stmt() + " FROM " + self.table + " " + where_str + " " + self.order_by_stmt()
        if int(self.limit) > 0:
            query += " LIMIT " + str(self.limit)
        query += ";"

        return query, params

    def write_insert_query(self, insert_list, ignore=False):
        """ Compile insert query

        enum values in insert_list have .value applied
        datetime.date values converted to int if self.date_to_int_date == True

        Args:
            insert_list (list(list)), list(dict)): insert values. if list, each list must have the same number of
                elements as self.fields, if dict, each dict must have the same keys as in self.fields
            ignore (boolean, optional): True to use insert ignore statement. False to use insert. Default False
        Returns:
            (str query or "0" if insert_list is empty, insert_list with changes applied)

        Raises:
            ValueError if any dict or list in insert_list does not match self.fields
            NotImplementedError if self.fields is a str
        """
        if len(insert_list) == 0:
            return "0", []

        if isinstance(self.fields, str):
            raise NotImplementedError("self.fields as str not implemented")

        if isinstance(insert_list[0], list):
            if any([len(lst) != len(self.fields) for lst in insert_list]):
                raise ValueError("Each list in insert_list must have the same number of elements as self.fields")

            insert_values_str = ("%s, " * len(self.fields))[0:-2]
        else:  # isinstance dict
            f_set = set(self.fields)
            if any([set(d) != f_set for d in insert_list]):
                raise ValueError("Each dict in insert_list must have dict.keys() equal to self.fields")

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

    def write_update_query(self, set_params, where_params=None):
        # TODO allow "in" and "not in" in where clause
        """ Compile update query with optional where statement and parameter lists

        If self.wheres is a list of lists, the element at position 2 in each sub list is ignored. Put those elements
        in where_params at the corresponding sub list position.
        "in" and "not in" not allowed in where statement
        any Enum values in set_params and where_params will have .value applied.

        Args:
            set_params (list(list)): list of lists of set values. If where_params is not None, must have same number
                of sub lists as where_params
            where_params (list(list), optional): list of list of where parameters. If not None, must have same number
                of sub lists as set_params

        Returns: (str query, list(list) params)
            If query == "0", then set_params had length 0

        Raises:
            ValueError if self.fields or set_params or where_params are not valid

        Example:
            The following will run the same query twice but with different parameter values
            self.table = "securities", self.fields = ["field1", "field2"]
            self.wheres = [["field1", "=", val_ignored], "or", ["field3", 'like", "val_ignored"]]
            set_params = [["val11", val12], ["val21", val22"]]
            where_params = [[where11, "where12"], [where21, "where22"]]

            query = "UPDATE securities SET field1 = %s, field2 = %s WHERE field1 = %s or field3 like %s;
            params = [["val11", val12, where11, "where12"], ["val21", val22, where21, "where22"]]
        """
        if len(set_params) == 0:
            return "0", ()

        if self.fields in [None, "*", [], ()]:
            raise ValueError("fields must be a list of field names in table " + self.table)

        if where_params is not None and len(set_params) != len(where_params):
            raise ValueError("Number of sub lists in set_params must equal number of sub lists in where_params")

        f_len = self.fields.count(" %s ") if isinstance(self.fields, str) else len(self.fields)
        for lst in set_params:
            if f_len != len(lst):
                raise ValueError("Number of parameters in all set_params sub lists must be " + str(f_len))

        where_str, params = self.where_stmt()
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
                sp = [x.value if isinstance(x, Enum) else x for x in set_params[i] + where_params[i]]
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

        Returns: str query
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

    def write_delete_query(self, allow_delete_all=False):
        """ Compile full delete query as a str and query parameters as a tuple

        Args:
            allow_delete_all (boolean, optional): TRUE to allow empty where statement. Default False.

        Returns: (str query, tuple params). If where clause is empty and allow_delete_all is false, query == "".
        """
        where_str, params = self.where_stmt()
        if where_str == "" and not allow_delete_all:
            return "", None

        query = "DELETE FROM " + self.table + " " + where_str + ";"

        return query, params