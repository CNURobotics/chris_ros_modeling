# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for the ROSModelBuilder
"""
from chris_ros_modeling.ros_model import ROSModel, BankType

#pylint: disable=wildcard-import
from chris_ros_snapshot.bank_builders import *


class ROSModelBuilder(object):
    """
    Class responsible for creating and preparing BankBuilders such that
    a fully populated ROSModel can be extracted
    """

    def __init__(self, topic_types):
        """
        Instantiates an instance of the ROSModelBuilder

        :param topic_types: the collection or iterable of topic name,
            topic type pairs
        :type topic_types: list[tuple(str, str)]
        """
        self._bank_builders = {BankType.NODE: NodeBankBuilder(),
                               BankType.TOPIC: TopicBankBuilder(topic_types),
                               BankType.ACTION: ActionBankBuilder(),
                               BankType.SERVICE: ServiceBankBuilder(),
                               BankType.PARAMETER: ParameterBankBuilder(),
                               BankType.MACHINE: MachineBankBuilder()
                              }

    def get_bank_builder(self, bank_builder_type):
        """
        Returns a desired BankBuilder

        :param bank_builder_type: the key to retrieve the BankBuilder by
        :type bank_builder_type: BankType
        :return: the desired BankBuilder
        :rtype: BankBuilder
        """
        return self._bank_builders[bank_builder_type]

    def prepare(self):
        """
        Prepares the individual BankBuilders to help build the ROSModel
        """
        topic_bank_builder = self.get_bank_builder(BankType.TOPIC)
        action_bank_builder = self.get_bank_builder(BankType.ACTION)
        names_to_action_builders = topic_bank_builder.extract_action_builders_from_internal_topic_builders()
        action_bank_builder.add_entity_builders(names_to_action_builders.values())
        for bank_builder_type in ROSModel.DEPLOYMENT_TYPES:
            # Process all types except specifications
            if bank_builder_type != BankType.NODE and \
               bank_builder_type != BankType.NODELET and \
               bank_builder_type != BankType.NODELET_MANAGER and \
               bank_builder_type != BankType.MACHINE:
                self.get_bank_builder(bank_builder_type).prepare()

        self.get_bank_builder(BankType.NODE).prepare(
            topic_bank_builder=topic_bank_builder, action_bank_builder=action_bank_builder)
        self.get_bank_builder(BankType.MACHINE).prepare(
            node_builders=self.get_bank_builder(BankType.NODE))

    def _extract_metamodels(self):
        """
        Helper method to extract the individual metamodels from each of
        the BankBuilders

        :return: a dictionary of bank names to *Bank instances
        :rtype: dict{str: *Bank}
        """
        bank_builder_types_to_metamodels = dict()
        for bank_builder_type, instance in self._bank_builders.items():
            if bank_builder_type == BankType.NODE:
                bank_builder_types_to_metamodels[BankType.NODE] = instance.extract_node_bank_metamodel()
                bank_builder_types_to_metamodels[BankType.NODELET] = instance.extract_nodelet_bank_metamodel()
                bank_builder_types_to_metamodels[BankType.NODELET_MANAGER] = instance.extract_nodelet_manager_bank_metamodel(
                )
            else:
                bank_builder_types_to_metamodels[bank_builder_type] = instance.extract_metamodel()

        return bank_builder_types_to_metamodels

    def extract_model(self):
        """
        Extracts the ROSModel instance

        :return: the extracted, populated ROSModel
        :rtype: ROSModel
        """
        return ROSModel(self._extract_metamodels())
