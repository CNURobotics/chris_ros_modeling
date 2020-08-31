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

import socket

from chris_ros_snapshot.base_builders import _EntityBuilder
from chris_ros_modeling.deployments.machine import Machine


class MachineBuilder(_EntityBuilder):
    """
    Defines a MachineBuilder, which represents a host machine running ROS nodes
     and is responsible for allowing itself to be
    populated with basic information relevant to a Machine and then
    further populating itself from that information for the purpose
    of extracting a metamodel instance
    """

    def __init__(self, name):
        """
        Instantiates an instance of the MachineBuilder

        :param name: the name of the machine that this
            MachineBuilder represents
        :type name: str
        """
        super(MachineBuilder, self).__init__(name)
        self._hostname = None
        self._ip_address = None
        self._node_names = set()

    @property
    def hostname(self):
        """
        Returns the hostname of machine on network

        :return: hostname on network
        :rtype: str
        """
        if self._hostname is None and self._ip_address is None:
            self._gather_hostname_ip()

        return self._hostname

    @property
    def ip_address(self):
        """
        Returns the ip address of given machine on network

        :return: ip address of machine
        :rtype: str
        """
        if self._hostname is None and self._ip_address is None:
            self._gather_hostname_ip()

        return self._ip_address

    def _gather_hostname_ip(self):
        """
        Gather the hostname/IP address data
        """
        try:
            # presume name was hostname and try to get address
            self._ip_address = socket.gethostbyname(self.name)
            self._hostname = self.name
        #pylint: disable=broad-except
        except Exception:
            try:
                # ok, try the reverse
                self._hostname = socket.gethostbyaddr(self.name)
                self._ip_address = self.name
            except Exception:
                # ok, just save and carry on
                nums = self.name.split(".")
                if len(nums) == 4:
                    self._ip_address = self.name  # @todo - validate further
                    self._hostname = "UNKNOWN HOSTNAME"  #@todo - lookup from /etc/hosts
                else:
                    self._hostname = self.name
                    self._ip_address = 'UNKNOWN IP ADDRESS' #@todo - lookup from /etc/hosts

    @property
    def node_names(self):
        """
        Returns the collection of names of the ROS Nodes that have set
        a value for this Parameter

        :return: the collection of names of the ROS Nodes that have set
            a value for this Parameter
        :rtype: set{str}
        """
        return self._node_names

    def add_node_name(self, node_name):
        """
        Associates the name of a ROS Node to this machine

        :param node_name: the name of the ROS Node
        :type node_name: str
        """
        self._node_names.add(node_name)

    def prepare(self, **kwargs):
        """
        Prepares the internal MachineBuilder based on identified nodes for eventual metamodel
        extraction; internal changes to the state of the *EntityBuilders
        occur for the builders that are stored in the internal bank

        :param kwargs: keyword arguments
        :type kwargs: dict{param: value}
        """
        self.add_node_name(kwargs['node_name'])

    def extract_metamodel(self):
        """
        Allows the MachineBuilder to create / extract a
        Machine instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: Machine
        """
        machine_model = Machine(source='ros_snapshot',
                                name=self.name,
                                hostname=self.hostname,
                                ip_address=self.ip_address,
                                node_names=self.node_names)
        return machine_model
