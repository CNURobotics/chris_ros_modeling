# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Filter object for processing ROS data
@author William R. Drumheller <william@royalldesigns.com>

"""
class Filter(object):
    """
    Generic filter class
    """
    FILTER_OUT_DEBUG = False
    FILTER_OUT_TF = False
    BASE_EXCLUSIONS = {}
    DEBUG_EXCLUSIONS = {}
    TF_EXCLUSIONS = {}
    INSTANCE = None

    def __init__(self, filter_out_debug, filter_out_tf):
        self._base_exclusions = self.__class__.BASE_EXCLUSIONS
        self._debug_exclusions = {}
        self._tf_exclusions = {}
        if filter_out_debug:
            self._debug_exclusions = self.__class__.DEBUG_EXCLUSIONS
        if filter_out_tf:
            self._tf_exclusions = self.__class__.TF_EXCLUSIONS

    def should_filter_out(self, item):
        """
        Check to see if item is in list of exclusions
        :param item:
        :return: True if we should filter, False otherwise
        """
        return (item in self._base_exclusions) or \
               (item in self._debug_exclusions) or \
               (item in self._tf_exclusions)

    @classmethod
    def get_filter(cls):
        """
        Create an instance of given filter
        :return: filter instance
        """
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(cls.FILTER_OUT_DEBUG, cls.FILTER_OUT_TF)
        return cls.INSTANCE


class NodeFilter(Filter):
    """
    Default filter for Nodes
    """
    BASE_EXCLUSIONS = {'/roslaunch'}
    DEBUG_EXCLUSIONS = {'/rosout'}


class TopicFilter(Filter):
    """Default filter for Topics """
    DEBUG_EXCLUSIONS = {'/rosout', '/rosout_agg', '/statistics'}
    TF_EXCLUSIONS = {'/tf', '/tf_static'}


class ServiceTypeFilter(Filter):
    """Default filter for Services """
    DEBUG_EXCLUSIONS = {'roscpp/GetLoggers', 'roscpp/SetLoggerLevel'}
