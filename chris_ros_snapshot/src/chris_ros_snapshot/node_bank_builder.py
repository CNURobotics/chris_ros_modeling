# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for NodeBankBuilder , which are responsible for collecting, maintaining,
and populating NodeBuilder instances
"""

from chris_ros_modeling.utilities import filters
from chris_ros_modeling import metamodels
from chris_ros_snapshot.base_builders import _BankBuilder
from chris_ros_snapshot.node_builder import NodeBuilder


class NodeBankBuilder(_BankBuilder):
    """
    Defines a NodeBankBuilder which is responsible for collecting,
    maintaining, and populating NodeBuilders for the purpose of
    extracting metamodel instances
    """

    def _create_entity_builder(self, name):
        """
        Creates and returns a new NodeBuilder instance

        :param name: the name used to instantiate the new NodeBuilder
        :type name: str
        :return: the newly created NodeBuilder
        :rtype: NodeBuilder
        """
        return NodeBuilder(name)

    def _should_filter_out(self, name, entity_builder):
        """
        Indicates whether the given NodeBuilder (which has a name to
        identify it) should be filtered out or not

        :param name: the name to identify the NodeBuilder
        :type name: str
        :param entity_builder: the NodeBuilder to check
        :type entity_builder: NodeBuilder
        :return: True if the NodeBuilder should be filtered out;
            False if not
        :rtype: bool
        """
        return filters.NodeFilter.get_filter().should_filter_out(name)

    def _post_prepare(self):
        """
        Allows this class to either wrap up or begin a new set of
        tasking necessary for eventual metamodel population
        """
        self._populate_node_builders_with_nodelet_and_manager_info()

    def _populate_node_builders_with_nodelet_and_manager_info(self):
        """
        Takes the internal store of NodeBuilders, determines which will
        represent / build Nodelets and which will represent / build
        Nodelet Managers, and then associates each with the names of
        their respective Manager and Nodelet counterparts
        """
        for manager_node_name in self.names_to_entity_builders:
            manager_node = self.names_to_entity_builders[manager_node_name]
            if manager_node.is_nodelet_manager:
                bond_topic = None
                for topic_name in manager_node.all_topic_names:
                    if manager_node.topic_names_to_types[topic_name] == 'bond/Status':
                        bond_topic = topic_name
                for nodelet_node_name in self.names_to_entity_builders:
                    nodelet_node = self.names_to_entity_builders[nodelet_node_name]
                    if (nodelet_node.is_nodelet) and (bond_topic in nodelet_node.all_topic_names):
                        nodelet_node.set_nodelet_manager_name(manager_node_name)
                        manager_node.add_nodelet_name(nodelet_node_name)

    def _create_bank_metamodel(self):
        """
        Creates and returns a new NodeBank instance

        :return: a newly created NodeBank instance
        :rtype: NodeBank
        """
        return metamodels.NodeBank()

    def extract_node_bank_metamodel(self):
        """
        Extracts and returns an instance of the NodeBank
        extracted and populated from this builder (built by this
        builder); only pure Node instances (no subtypes)
        are part of this bank

        :return: an extracted instance of this builder's NodeBank
        :rtype: NodeBank
        """
        bank_metamodel = metamodels.NodeBank()
        all_node_metamodels = self._names_to_entity_builder_metamodels
        bank_metamodel.names_to_metamodels = {name: node_metamodel
                                              for (name, node_metamodel) in all_node_metamodels.items()
                                              if not isinstance(node_metamodel,
                                                                (metamodels.Nodelet, metamodels.NodeletManager))}
        return bank_metamodel

    def extract_nodelet_bank_metamodel(self):
        """
        Extracts and returns an instance of the NodeletBank
        extracted and populated from this builder (built by this
        builder); only Nodelet instances are part of this bank

        :return: an extracted instance of this builder's
            NodeletBank
        :rtype: NodeletBank
        """
        bank_metamodel = metamodels.NodeletBank()
        all_node_metamodels = self._names_to_entity_builder_metamodels
        bank_metamodel.names_to_metamodels = {name: node_metamodel
                                              for (name, node_metamodel) in all_node_metamodels.items()
                                              if isinstance(node_metamodel, metamodels.Nodelet)}
        return bank_metamodel

    def extract_nodelet_manager_bank_metamodel(self):
        """
        Extracts and returns an instance of the
        NodeletManagerBank extracted and populated from this
        builder (built by this builder); only NodeletManager
        instances are part of this bank

        :return: an extracted instance of this builder's
            NodeletManagerBank
        :rtype: NodeletManagerBank
        """
        bank_metamodel = metamodels.NodeletManagerBank()
        all_node_metamodels = self._names_to_entity_builder_metamodels
        bank_metamodel.names_to_metamodels = {name: node_metamodel
                                              for (name, node_metamodel) in all_node_metamodels.items()
                                              if isinstance(node_metamodel, metamodels.NodeletManager)}
        return bank_metamodel
