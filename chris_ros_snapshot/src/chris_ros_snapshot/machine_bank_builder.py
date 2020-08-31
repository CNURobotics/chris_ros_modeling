# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Classes associated with building a bank of machine models
"""

from chris_ros_snapshot.base_builders import _BankBuilder
from chris_ros_snapshot.machine_builder import MachineBuilder
from chris_ros_modeling.metamodels import MachineBank


class MachineBankBuilder(_BankBuilder):
    """
    Defines a MachineBankBuilder which is responsible for collecting,
    maintaining, and populating MachineBuilders for the purpose of
    extracting metamodel instances
    """

    def _create_entity_builder(self, name):
        """
        Creates and returns a new MachineBuilder instance

        :param name: the name used to instantiate the new MachineBuilder
        :type name: str
        :return: the newly created MachineBuilder
        :rtype: MachineBuilder
        """
        return MachineBuilder(name)

    def _create_bank_metamodel(self):
        """
        Creates and returns a new MachineBank instance

        :return: a newly created MachineBank instance
        :rtype: MachineBank
        """
        return MachineBank()

    def prepare(self, **kwargs):
        """
        Prepares the internal MachineBankBuilder based on identified nodes for eventual metamodel
        extraction; internal changes to the state of the *EntityBuilders
        occur for the builders that are stored in the internal bank

        :param kwargs: keyword arguments needed by the underlying
            *EntityBuilders used in the preparation process
        :type kwargs: dict{param: value}
        """
        node_builders = kwargs['node_builders']
        for node_builder in node_builders.names_to_entity_builders.values():
            machine_builder = self.__getitem__(node_builder.machine)
            machine_builder.prepare(node_name=node_builder.name)

        #self._post_prepare()  # Not used by MachineBankBuilder
