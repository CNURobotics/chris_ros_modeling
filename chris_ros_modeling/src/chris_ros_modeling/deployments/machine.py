# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Machines and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class Machine(_EntityMetamodel):
    """
    Metamodel for ROS Machines
    """
    yaml_tag = u'!Machine'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: Machine
        """
        self = super(Machine, cls).__new__(cls, **kwargs)
        self.hostname = None
        self.ip_address = None
        self.node_names = set()  # including nodelet managers
        return self

class MachineBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Machines
    """
    yaml_tag = u'!MachineBank'
    HUMAN_OUTPUT_NAME = 'Machines:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: MachineBank
        """
        return super(MachineBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  Machine(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  Machine
