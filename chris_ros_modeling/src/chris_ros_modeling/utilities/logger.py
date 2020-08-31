# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details
"""
Basic handler for logging functionality
"""

import logging


class LoggerLevel(object):
    """
    Define different levels of logging output
    """
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class Logger(object):
    """
    Define standard interface to python logging
    """
    INSTANCE = None
    LEVEL = LoggerLevel.DEBUG

    def __init__(self):
        """
        Set up the logger instance
        """
        self._logger = logging.getLogger()

    @staticmethod
    def setup(level):
        """
        Set up the logger at given level
        :param level: logging level to display
        """
        logging.basicConfig(format='[%(asctime)s][%(levelname)s]-> %(message)s',
                            datefmt='%d%b%Y %I:%M:%S %p %Z', level=level)

    def log(self, level, message):
        """
        log message at level
        :param level: logging level
        :param message: text string to log
        """
        self._logger.log(level, message)

    @classmethod
    def get_logger(cls):
        """
        Get logger instance
        """
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
            cls.INSTANCE.setup(cls.LEVEL)
        return cls.INSTANCE
