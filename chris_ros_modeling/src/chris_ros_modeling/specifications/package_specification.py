# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Packages and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class PackageSpecification(_EntityMetamodel):
    """
    Metamodel for ROS Package specifications
    """
    yaml_tag = u'!PackageSpecification'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance from keyword arguments

        :param kwargs: the keyword arguments to construct a new instance
        :type kwargs: dict{str: value}
        :return: the constructed instance
        :rtype: PackageMetamodel
        """
        self = super(PackageSpecification, cls).__new__(cls, **kwargs)
        self.directory_path = None
        self.is_metapackage = False
        self.package_version = None
        self.installed_version = None
        self.url = None
        self.dependencies = None
        self.nodes = None
        self.messages = None
        self.services = None
        self.actions = None
        self.launch_files = None     # Standard *.launch files
        self.parameter_files = None
        return self


class PackageSpecificationBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Package specifications
    """
    yaml_tag = u'!PackageSpecBank'
    HUMAN_OUTPUT_NAME = 'PackageSpecs:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments 
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: PackageBankMetamodel
        """
        self = super(PackageSpecificationBank, cls).__new__(cls, **kwargs)
        return self

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  PackageSpecification(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  PackageSpecification
