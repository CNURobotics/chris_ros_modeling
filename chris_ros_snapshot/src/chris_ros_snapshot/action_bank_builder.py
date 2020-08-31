# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for *BankBuilders, which are responsible for collecting, maintaining,
and populating *EntityBuilders for the purpose of extracting metamodel
instances
"""

from chris_ros_modeling.metamodels import ActionBank
from chris_ros_snapshot.base_builders import _BankBuilder
from chris_ros_snapshot.action_builder import ActionBuilder


class ActionBankBuilder(_BankBuilder):
    """
    Defines an ActionBankBuilder which is responsible for collecting,
    maintaining, and populating ActionBuilders for the purpose of
    extracting metamodel instances
    """

    def _create_entity_builder(self, name):
        """
        Creates and returns a new ActionBuilder instance

        :param name: the name used to instantiate the new ActionBuilder
        :type name: str
        :return: the newly created ActionBuilder
        :rtype: ActionBuilder
        """
        return ActionBuilder(name)

    def _create_bank_metamodel(self):
        """
        Creates and returns a new ActionBank instance

        :return: a newly created ActionBank instance
        :rtype: ActionBank
        """
        return ActionBank()
