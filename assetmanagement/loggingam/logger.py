"""Logging facility for python projects

Logger is the only class of this module.
"""
from logging.handlers import TimedRotatingFileHandler
import logging
import os
import pathlib


class Logger:
    """Logging facility for python projects

    Attributes:
        logger (logging.logger): logging.logger instance
    """

    def __init__(self, logger_name):
        """Init logging facility

        Create a logger with TimedRotatingFileHandler that creates a new log file at midnight and a detailed output
        format. This logger logs info, warning, error and critical levels, Output file is Python_Log.log in the
        directory specified by FO_LOGGING_DIR in .env

        Args:
            logger_name (str): name of the logger. used by %(name)s in formatter
        """
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(funcName)s : line %(lineno)s : "
                                      "%(message)s")

        log_file = str(pathlib.Path(__file__).parent.parent / (os.getenv("FO_LOGGING_DIR") + "Python_Log.log"))
        file_handler = TimedRotatingFileHandler(log_file, when="midnight")
        file_handler.setFormatter(formatter)

        self.logger = logging.getLogger(logger_name)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)