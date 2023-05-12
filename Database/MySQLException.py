"""Module for MySQL Exceptions.

"""

class MySQLException(Exception):
    """MySQL database exceptions chainer.

    Chains MySQL database exceptions. These are generally mysql.connector.Error exceptions. The initial purpose of this
    exception class is to prevent multiple logs of the same error.

    Attributes:
        is_logged (boolean): the exception (generally a mysql.connector.Error) chained by an instance of this
            class has already been logged
    """

    def __init__(self, msg, is_logged=True):
        """ init

        Args:
            msg (str): exception message
            is_logged (boolean, optional): chained exception has been logged. Default True
        """
        super(MySQLException, self).__init__(msg)
        self.is_logged = is_logged