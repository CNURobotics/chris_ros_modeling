# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Nodelet Managers and the Banks that
contain them
"""

from chris_ros_modeling.deployments.node import NodeBank, Node


class NodeletManager(Node):
    """
    Metamodel for ROS Nodelet Managers
    """
    yaml_tag = u'!NodeletManager'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: NodeletManager
        """
        self = super(NodeletManager, cls).__new__(cls, **kwargs)
        self.nodelet_names = set()
        self.published_nodelet_manager_topic_names = dict()
        self.subscribed_nodelet_manager_topic_names = dict()
        return self


class NodeletManagerBank(NodeBank):
    """
    Metamodel for Bank of ROS Nodelet Managers
    """
    yaml_tag = u'!NodeletManagerBank'
    HUMAN_OUTPUT_NAME = 'Nodelet Managers:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: NodeletManagerBank
        """
        return super(NodeletManagerBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  NodeletManager(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  NodeletManager
