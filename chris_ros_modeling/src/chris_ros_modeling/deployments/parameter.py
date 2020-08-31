# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Parameters and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class Parameter(_EntityMetamodel):
    """
    Metamodel for ROS Parameters
    """
    yaml_tag = u'!Parameter'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: Parameter
        """
        self = super(Parameter, cls).__new__(cls, **kwargs)
        self.python_type = None
        self.value = None
        self.setting_node_names = dict()
        self.reading_node_names = dict()
        return self



class ParameterBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Parameters
    """
    yaml_tag = u'!ParameterBank'
    HUMAN_OUTPUT_NAME = 'Parameters:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: ParameterBank
        """
        return super(ParameterBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  Parameter(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  Parameter
