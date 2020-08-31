# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Nodes and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class NodeSpecification(_EntityMetamodel):
    """
    Metamodel for ROS Node specifications
    """
    yaml_tag = u'!NodeSpecification'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance from keyword arguments

        :param kwargs: the keyword arguments to construct a new instance
        :type kwargs: dict{str: value}
        :return: the constructed instance
        :rtype: NodeMetamodel
        """
        self = super(NodeSpecification, cls).__new__(cls, **kwargs)
        self.validated = False #  Set to true one confirm ROS Node, not just executable
        self.package = None
        self.file_path = None
        self.action_clients = None
        self.action_servers = None
        self.parameters = None
        self.published_topics = None
        self.subscribed_topics = None
        self.services_provided = None
        return self


class NodeSpecificationBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Node specifications
    """
    yaml_tag = u'!NodeSpecBank'
    HUMAN_OUTPUT_NAME = 'NodeSpecs:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments 
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: NodeBankMetamodel
        """
        self = super(NodeSpecificationBank, cls).__new__(cls, **kwargs)
        return self

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  NodeSpecification(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  NodeSpecification
