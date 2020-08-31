# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Message, Action, Service Specifications
and the Banks that contain them
"""

from enum import Enum, unique
from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel

@unique
class TypeSpecificationEnum(Enum):
    """
    Enumerated type for SpecificationBuilder identifiers
    """
    MSG = 1
    ACTION = 2
    SRV = 3


class TypeSpecification(_EntityMetamodel):
    """
    Metamodel for ROS Message, Action, or Service Specifications
    """
    yaml_tag = u'!TypeSpecification'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance from keyword arguments

        :param kwargs: the keyword arguments
        :type kwargs: dict{str: str}
        :return: the constructed instance
        :rtype: TypeSpecification
        """
        self = super(TypeSpecification, cls).__new__(cls, **kwargs)
        self.construct_type = None
        self.package = None
        self.file_path = None
        self.spec = None
        return self


class TypeSpecificationBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Message, Service, or Action
    Specifications
    """
    yaml_tag = u'!TypeSpecificationBank'
    HUMAN_OUTPUT_NAME = 'TypeSpecifications:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments
        :type kwargs: dict{str: value}
        :return: the constructed instance
        :rtype: SpecificationBankMetamodel
        """
        return super(TypeSpecificationBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  TypeSpecification(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  TypeSpecification
