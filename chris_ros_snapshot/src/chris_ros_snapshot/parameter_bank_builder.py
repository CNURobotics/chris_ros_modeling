# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for ParameterBankBuilders, which are responsible for collecting, maintaining,
and populating ParameterBuilder for the purpose of extracting metamodel
instances
"""

from chris_ros_modeling.metamodels import ParameterBank
from chris_ros_snapshot.base_builders import _BankBuilder
from chris_ros_snapshot.parameter_builder import ParameterBuilder


class ParameterBankBuilder(_BankBuilder):
    """
    Defines a ParameterBankBuilder which is responsible for collecting,
    maintaining, and populating ParameterBuilders for the purpose of
    extracting metamodel instances
    """

    def _create_entity_builder(self, name):
        """
        Creates and returns a new ParameterBuilder instance

        :param name: the name used to instantiate the new ParameterBuilder
        :type name: str
        :return: the newly created ParameterBuilder
        :rtype: ParameterBuilder
        """
        return ParameterBuilder(name)

    def _create_bank_metamodel(self):
        """
        Creates and returns a new ParameterBank instance

        :return: a newly created ParameterBank instance
        :rtype: ParameterBank
        """
        return ParameterBank()
