# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for *BankBuilders, which are responsible for collecting, maintaining,
and populating *EntityBuilders for the purpose of extracting metamodel
instances
"""

from chris_ros_modeling.utilities import filters
from chris_ros_modeling.metamodels import ServiceBank
from chris_ros_snapshot.base_builders import _BankBuilder
from chris_ros_snapshot.service_builder import ServiceBuilder


class ServiceBankBuilder(_BankBuilder):
    """
    Defines a ServiceBankBuilder which is responsible for collecting,
    maintaining, and populating ServiceBuilders for the purpose of
    extracting metamodel instances
    """

    def _create_entity_builder(self, name):
        """
        Creates and returns a new ServiceBuilder instance

        :param name: the name used to instantiate the new ServiceBuilder
        :type name: str
        :return: the newly created ServiceBuilder
        :rtype: ServiceBuilder
        """
        return ServiceBuilder(name)

    def _should_filter_out(self, name, entity_builder):
        """
        Indicates whether the given ServiceBuilder (which has a name to
        identify it) should be filtered out or not

        :param name: the name to identify the ServiceBuilder
        :type name: str
        :param entity_builder: the ServiceBuilder to check
        :type entity_builder: ServiceBuilder
        :return: True if the ServiceBuilder should be filtered out;
            False if not
        :rtype: bool
        """
        return filters.ServiceTypeFilter.get_filter().should_filter_out(entity_builder.construct_type)

    def _create_bank_metamodel(self):
        """
        Creates and returns a new ServiceBank instance

        :return: a newly created ServiceBank instance
        :rtype: ServiceBank
        """
        return ServiceBank()
