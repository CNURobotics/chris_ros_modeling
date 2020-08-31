# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Nodelets and the Banks that
contain them
"""

from chris_ros_modeling.deployments.node import NodeBank, Node


class Nodelet(Node):
    """
    Metamodel for ROS Nodelets
    """
    yaml_tag = u'!Nodelet'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: Nodelet
        """
        self = super(Nodelet, cls).__new__(cls, **kwargs)
        self.nodelet_manager_name = ''
        self.published_nodelet_topic_names = dict()
        self.subscribed_nodelet_topic_names = dict()
        return self

class NodeletBank(NodeBank):
    """
    Metamodel for Bank of ROS Nodelets
    """
    yaml_tag = u'!NodeletBank'
    HUMAN_OUTPUT_NAME = 'Nodelets:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: NodeletBank
        """
        return super(NodeletBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  Nodelet(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  Nodelet
