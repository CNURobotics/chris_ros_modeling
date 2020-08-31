#!/usr/bin/python
# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Utility class for accessing ROS Utilities from rosgraph, rospack, ...
@author William R. Drumheller <william.Drumheller.16@cnu.edu>
"""

import os.path

import rospkg
import rosgraph
import rosgraph.network
import rosgraph.names

import genmsg


class ROSUtilities(object):
    """
    Class that handles ROS communication utility interfaces
    """
    INSTANCE = None

    def __init__(self):
        self._node_name = '/ros_model'
        self._master = None
        self._packages = None
        self._rospack = None
        self._message_paths = None
        self._service_paths = None
        self._package_paths = None
        self._action_paths = None
        self._context = None

    def _setup(self, node_name):
        """
        Setup the ROS Utilities instance
        :return:
        """
        print "  Initializing ROS Master with ", node_name
        self._node_name = node_name
        self._master = rosgraph.Master(self._node_name)
        self._rospack = rospkg.RosPack()
        self._packages = self._rospack.list()

        self._package_paths = {package: self._rospack.get_path(package) for package in self._packages}

        self._message_paths = {package: [os.path.join(self._rospack.get_path(package), 'msg')]
                               for package in self._packages}
        self._service_paths = {package: [os.path.join(self._rospack.get_path(package), 'srv')]
                               for package in self._packages}
        self._action_paths = {package: [os.path.join(self._rospack.get_path(package), 'action')]
                              for package in self._packages}
        self._context = genmsg.MsgContext.create_default()

    @property
    def node_name(self):
        """
        name used by ROS node
        :return:
        """
        return self._node_name

    @property
    def master(self):
        """
        Get the ROS master
        :return: master reference
        """
        return self._master

    @property
    def rospack(self):
        """
        Get rospack utility
        :return: rospack instance
        """
        return self._rospack

    @property
    def packages(self):
        """
        Get all packages
        :return: packages dictionary
        """
        return self._packages

    @property
    def package_paths(self):
        """
        Get all package paths
        :return: package paths
        """
        return self._package_paths

    @property
    def message_paths(self):
        """
        Get all message paths
        :return: message paths
        """
        return self._message_paths

    @property
    def service_paths(self):
        """
        Get all service paths
        :return: message paths
        """
        return self._service_paths

    @property
    def action_paths(self):
        """
        Get all service paths
        :return: message paths
        """
        return self._action_paths

    @property
    def context(self):
        """
        Get context
        :return: context
        """
        return self._context

    @classmethod
    def get_ros_utilities(cls, node_name='/ros_modeling'):
        """
        Setup ROS Utilities and return instance
        :param node_name: name of node for ROS access
        :return: instance of ROS Utilities instance
        """
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
            cls.INSTANCE._setup(node_name)
        return cls.INSTANCE
