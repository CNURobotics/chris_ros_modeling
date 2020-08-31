# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for *EntityBuilders, which represent ROS Entities and are
responsible for allowing themselves to be populated with basic
information and then further populating themselves from that
information for the purpose of extracting metamodel instances
"""

import socket
from cStringIO import StringIO as BufferType

import rosgraph

from chris_ros_modeling.utilities import filters
from chris_ros_modeling.metamodels import Service
from chris_ros_snapshot.base_builders import _EntityBuilder
from chris_ros_snapshot.ros_utilities import ROSUtilities


class ServiceBuilder(_EntityBuilder):
    """
    Defines a ServiceBuilder, which represents a ROS
    Service and is responsible for allowing itself to be
    populated with basic information relevant to a Service and then
    further populating itself from that information for the purpose
    of extracting a metamodel instance
    """

    def __init__(self, name):
        """
        Instantiates an instance of the ServiceBuilder

        :param name: the name of the Service that this ServiceBuilder
            represents
        :type name: str
        """
        super(ServiceBuilder, self).__init__(name)
        self._headers = dict()
        self._arguments = None
        self._service_provider_node_names = set()
        self._uri = None
        # self._exe = None

    @property
    def uri(self):
        """
        Returns the Service's URI

        :return: the URI of the Service
        :rtype: str
        """
        if self._uri is None:
            try:
                self._uri = ROSUtilities.get_ros_utilities().master.lookupService(self.name)
            except rosgraph.masterapi.MasterError:
                print "Service URI %s is unavailable " % self._name
                self._uri = "Service URI %s is unavailable " % self._name
        return self._uri

    @property
    def headers(self):
        """
        Returns the Service's XML-RPC handshake headers

        :return: the Service's XML-RPC handshake headers
        :rtype: {str: str}
        """
        destination_address = self.uri[len('rosrpc://'):]
        destination_address, destination_port = destination_address.split(':')
        destination_port = int(destination_port)
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            my_socket.settimeout(5.0)
            my_socket.connect((destination_address, destination_port))
            header = {'probe': '1', 'md5sum': '*', 'callerid': '/rosservice', 'service': self.name}
            rosgraph.network.write_ros_handshake_header(my_socket, header)
            handshake_headers = rosgraph.network.read_ros_handshake_header(my_socket, BufferType(), 2048)
            return handshake_headers
        except socket.error:
            print 'Unable to communicate with service "{}" -> "{}"'.format(self.name, self.uri)
            return None
        finally:
            if my_socket:
                my_socket.close()

    @property
    def construct_type(self):
        """
        Returns the Service's ROS type

        :return: the Service's ROS type
        :rtype: str
        """
        return self.headers['type']

    @property
    def service_provider_node_names(self):
        """
        Returns the names of the ROS Nodes that act as Providers for
        this Service

        :return: the names of the Service Provider ROS Nodes
        :rtype: set{str}
        """
        node_filter = filters.NodeFilter.get_filter()
        return set([name for name in self._service_provider_node_names if not node_filter.should_filter_out(name)])

    def add_service_provider_node_name(self, service_provider_node_name):
        """
        Adds an association between a Service Provider ROS Node's name
        and this Action

        :param service_provider_node_name: the Service Provider ROS
            Node name to associate with this Action
        :type service_provider_node_name: str
        """
        self._service_provider_node_names.add(service_provider_node_name)

    def extract_metamodel(self):
        """
        Allows the ServiceBuilder to create / extract a Service
        instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: Service
        """
        service_metamodel = Service(source='ros_snapshot',
                                    name=self.name,
                                    uri=self.uri,
                                    construct_type=self.construct_type,
                                    headers=self.headers,
                                    service_provider_node_names=self.service_provider_node_names)
        return service_metamodel
