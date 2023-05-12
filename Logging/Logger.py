"""Logging facility for python projects

Logger is the only class of this module.
"""

import logging
import pathlib
from logging.handlers import TimedRotatingFileHandler


class Logger:
    """Logging facility for python projects

    Attributes:
        logger (logging.logger): logging.logger instance
    """

    def __init__(self, logger_name):
        """Init logging facility

        Create a logger with TimedRotatingFileHandler that creates a new log file at midnight and a detailed output
        format. This logger logs info, warning, error and critical levels, Output file is Python_Log.log in the
        same directory as this module.

        Args:
            logger_name (str): name of the logger. used by %(name)s in formatter
        """
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(funcName)s : line %(lineno)s : "
                                      "%(message)s")

        this_file_path = pathlib.Path(__file__).parent.absolute()
        file_handler = TimedRotatingFileHandler(str(this_file_path) + "/Python_Log.log", when="midnight")
        file_handler.setFormatter(formatter)

        self.logger = logging.getLogger(logger_name)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)