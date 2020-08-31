# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for *EntityBuilders, which represent ROS Entities and are
responsible for allowing themselves to be populated with basic
information and then further populating themselves from that
information for the purpose of extracting metamodel instances
"""

import xmlrpclib
import psutil
import rosgraph
from chris_ros_modeling.utilities import filters
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.metamodels import Node, Nodelet, NodeletManager
from chris_ros_snapshot.base_builders import _EntityBuilder
from chris_ros_snapshot.topic_builder import TopicBuilder
from chris_ros_snapshot.action_builder import ActionBuilder
from chris_ros_snapshot.ros_utilities import ROSUtilities


class NodeBuilder(_EntityBuilder):
    """
    Defines a NodeBuilder, which represents a ROS
    Node and is responsible for allowing itself to be
    populated with basic information relevant to a Node and then
    further populating itself from that information for the purpose
    of extracting a metamodel instance
    """

    def __init__(self, name):
        """
        Instantiates an instance of the NodeBuilder

        :param name: the name of the Node that this NodeBuilder
            represents
        :type name: str
        """

        super(NodeBuilder, self).__init__(name)
        self._all_topic_names = dict()
        self._topic_names = {'published': dict(), 'subscribed': dict()}
        self._topic_names_to_types = dict()
        self._service_names_to_types = dict()
        self._service_names_to_remap = None
        self._parameter_names = {'set': dict(), 'read': dict()}
        self._node = None
        self._uri = None
        self._process_dict = None
        self._machine = None
        self._is_nodelet = False
        self._is_nodelet_manager = False
        self._nodelet_manager_name = None
        self._nodelet_names = set()
        self._nodelet_or_manager_topic_names = {'published': dict(), 'subscribed': dict()}
        self._action_names = {'server': dict(), 'client': dict()}

    def prepare(self, **kwargs):
        """
        Allows this NodeBuilder to prepare its internal state
        for eventual metamodel extraction; internal changes to the state
        of the class instance occur here

        :param topic_bank_builder: the TopicBankBuilder to use for
            Action-related Topic name removal (from kwargs)
        :type topic_bank_builder: TopicBankBuilder
        :param action_bank_builder: the ActionBankBuilder to use for
            Action-related Topic name removal and Action Server / Client
            reference
        :type action_bank_builder: ActionBankBuilder
        """
        #Logger.get_logger().log(LoggerLevel.INFO, 'Preparing instance of builder for node {}.'.format(self.name))
        self._uri = self._gather_uri()
        self._gather_process_info('exe')  # Needs to be called after having URI set
        self._is_nodelet_manager = self._gather_nodelet_manager_status()
        self._is_nodelet = self._gather_nodelet_status()  # Needs to be called after having Nodelet Manager value set
        if self.is_nodelet or self.is_nodelet_manager:
            self._nodelet_or_manager_topic_names = NodeBuilder._extract_topics_for_nodelet_or_manager(
                self._topic_names, self.topic_names_to_types)
        self._action_names = self._extract_action_names_and_remove_corresponding_topics(
            kwargs['topic_bank_builder'], kwargs['action_bank_builder'])

    @property
    def node(self):
        """
        Returns the package/node name of this node
        :return: package/node name
        :rtype: string
        """
        return self._node

    def set_node_name(self, name):
        """
        Sets the package/node name for this node
        :param name: package/node name
        """
        self._node = name


    @property
    def uri(self):
        """
        Returns the ROS Node URI

        :return: the ROS Node URI
        :rtype: str
        """
        if self._uri is None:
            self._uri = self._gather_uri()

        return self._uri

    @property
    def machine(self):
        """
        Extracts the machine ID from the uri information
        :return: machine ID as string
        """
        if self._machine is None:
            self._machine = "UNKNOWN MACHINE"  # initialize

            if "UNKNOWN" in self._uri:
                # Abandon if uri is unknown
                return self._machine

            tokens = self.uri.split("/")
            if len(tokens) < 2:
                # expect at least one / in uri
                Logger.get_logger().log(LoggerLevel.ERROR, '{}: {}.'.format("UNKNOWN MACHINE", tokens))
            else:
                if tokens[-1] == "":
                    # Assumes last token is empty after trailing /
                    address = tokens[-2]
                else:
                    address = tokens[-1]

                # Assumes machine : pid  format of uri
                self._machine = address.split(":")[0]

        return self._machine

    def _gather_uri(self):
        """
        Helper method to gather the ROS Node URI from the ROS Master

        :return: the gathered ROS Node URI from the ROS Master
        :rtype: str
        """
        try:
            return ROSUtilities.get_ros_utilities().master.lookupNode(self.name)
        except rosgraph.masterapi.MasterError as ex:
            error_message = 'URI for node {} cannot be retrieved from ROS Master'.format(self.name)
            Logger.get_logger().log(LoggerLevel.ERROR, '{}: {}.'.format(error_message, ex))
            return "UNKNOWN URI FOR {}".format(self.name)

    @property
    def executable_file(self):
        """
        Returns the ROS Node executable

        :return: the ROS Node executable
        :rtype: str
        """
        return self._gather_process_info('exe')

    @property
    def executable_name(self):
        """
        Returns the ROS Node executable name

        :return: the ROS Node executable
        :rtype: str
        """
        return self._gather_process_info('name')

    @property
    def executable_cmdline(self):
        """
        Returns the ROS Node executable command line

        :return: the ROS Node executable command line
        :rtype: str
        """
        return self._gather_process_info('cmdline')


    @property
    def executable_num_threads(self):
        """
        Returns the ROS Node executable number threads

        :return: the ROS Node executable number threads
        :rtype: str
        """
        return self._gather_process_info('num_threads')

    @property
    def executable_cpu_percent(self):
        """
        Returns the ROS Node executable cpu percent

        :return: the ROS Node executable cpu percent
        :rtype: str
        """
        return self._gather_process_info('cpu_percent')

    @property
    def executable_memory_percent(self):
        """
        Returns the ROS Node executable memory percent

        :return: the ROS Node executable memory percent
        :rtype: str
        """
        return self._gather_process_info('memory_percent')

    @property
    def executable_memory_info(self):
        """
        Returns the ROS Node executable memory_info

        :return: the ROS Node executable memory_info
        :rtype: str
        """
        return str(self._gather_process_info('memory_info'))

    def _gather_process_info(self, key):
        """
        Helper method to gather the ROS Node executable based on
        information from the ROS Master and system

        :return: the gathered ROS Node process data by key
        :rtype: str
        """
        try:
            if self._process_dict is None:
                try:
                    if "UNKNOWN" in self._uri:
                        self._process_dict = {}
                        return "INVALID URI - CANNOT RETRIEVE {} FOR {}".format(key.upper(), self.name)

                    _, _, process_id = xmlrpclib.ServerProxy(self.uri).getPid('/NODEINFO')
                    process = psutil.Process(process_id)

                    self._process_dict = process.as_dict()
                except IOError as ex:
                    error_message = 'Executable for node {} and URI {} cannot be retrieved from ROS Master'.format(
                        self.name, self.uri)
                    Logger.get_logger().log(LoggerLevel.ERROR, '{}: {}.'.format(error_message, ex))
                    self._process_dict = {}
                except psutil.NoSuchProcess as ex:
                    error_message = 'Executable for node {} and URI {} cannot be retrieved from ROS Master'.format(
                        self.name, self.uri)
                    Logger.get_logger().log(LoggerLevel.ERROR, '{}: {}.'.format(error_message, ex))
                    self._process_dict = {}

            return self._process_dict[key]
        except KeyError as ex:
            #error_message = 'Process information for {} of node {} and URI {} cannot be retrieved '.format(
            #    key.upper(), self.name, self.uri)
            #Logger.get_logger().log(LoggerLevel.ERROR, '{}: {}.'.format(error_message, ex))
            #print self._process_dict.keys()
            # This error is expected if we cannot retrieve the process dictionary
            return "UNKNOWN {} FOR {}".format(key.upper(), self.name)
        except Exception as ex:
            error_message = 'Process information for {} of node {} and URI {} cannot be retrieved '.format(
                key.upper(), self.name, self.uri)
            Logger.get_logger().log(LoggerLevel.ERROR, '{}: {}.'.format(error_message, ex))
            return "UNKNOWN ERROR: CANNOT RETRIEVE {} FOR {}".format(key.upper(), self.name)

    @property
    def set_parameter_names(self):
        """
        Obtain the names of Parameters for which a value was set by the
        ROS Node

        :return: set Parameter names
        :rtype: set{str}
        """
        return self._parameter_names['set']

    @property
    def read_parameter_names(self):
        """
        Obtain the names of Parameters for which a value was read by the
        ROS Node

        :return: read Parameter names
        :rtype: set{str}
        """
        return self._parameter_names['read']

    def add_parameter_name(self, parameter_name, status, remap):
        """
        Associates a 'read' or 'set' Parameter name with the ROS Node

        :param parameter_name: the name of the Parameter
        :type parameter_name: str
        :param status: the relationship or status ('read' or 'set') of
            the Parameter to the ROS Node
        :type status: str
        :param remap: name used in node specification
        :type remap: str:
        """
        self._parameter_names[status][parameter_name] = remap

    @property
    def published_topic_names(self):
        """
        Returns the names of the Topics published by the ROS Node

        :return: published Topic names
        :rtype: dict{name:remap}
        """
        return self._topic_names['published']

    @property
    def subscribed_topic_names(self):
        """
        Returns the names of the Topics subscribed to by the ROS Node

        :return: subscribed Topic names
        :rtype: set{str}
        """
        return self._topic_names['subscribed']

    @property
    def all_topic_names(self):
        """
        Returns the name of all Topics either published or subscribed
        to by the ROS Node, including those that were removed from the
        basic Published / Subscribed store since they were related to
        either a Nodelet / Nodelet Manager interaction or an Action

        :return: all Topic names
        :rtype: set{str}
        """
        return self._all_topic_names

    def add_topic_name(self, topic_name, status, topic_type, remap):
        """
        Associates a 'published' or 'subscribed' Topic with a ROS Node

        :param topic_name: the name of the Topic
        :type topic_name: str
        :param status: the relationship or status ('subscribed' or
            'published') of the Topic to the ROS Node
        :type status: str
        :param topic_type: the ROS Topic Type
        :type topic_type: str
        :param remap: name used by node specificiation
        "type remap: str"
        """
        topic_filter = filters.TopicFilter.get_filter()
        if not topic_filter.should_filter_out(topic_name):
            self._all_topic_names[topic_name] = remap
            self._topic_names[status][topic_name] = remap
            self._topic_names_to_types[topic_name] = topic_type

    def remove_topic_name(self, topic_name, status):
        """
        Removes either a 'published' or 'subscribed' association
        between a Topic name and the ROS Node

        :param topic_name: the name of the Topic
        :type topic_name: str
        :param status: the relationship or status ('subscribed' or
            'published') of the Topic to the ROS Node
        :type status: str
        """
        self._topic_names[status].pop(topic_name, None)

    @property
    def topic_names_to_types(self):
        """
        Returns the mapping of all added Topic names (including those
        tied to Nodelet / Nodelet Manager interactions and Actions) to
        their ROS Topic type

        :return: all Topic names to their mapped ROS Topic Type
        :rtype: dict{str: str}
        """
        return self._topic_names_to_types

    @property
    def service_names_to_types(self):
        """
        Returns the mapping of all Service names to their ROS Service
        type

        :return: all Service names to their mapped ROS Service Type
        :rtype: dict{str: str}
        """
        return self._service_names_to_types

    @property
    def service_names(self):
        """
        Returns the name of all Services associated with the ROS Node

        :return: associated Service names
        :rtype: set{str}
        """
        return set(self.service_names_to_types.keys())

    @property
    def service_names_with_remap(self):
        """
        Returns the name of all Services associated with the ROS Node
        as dictionary to remapped service id (None at this point)

        :return: associated Service names
        :rtype: dict{str:str}
        """
        if self._service_names_to_remap is None:
            self._service_names_to_remap = {a:None for a in self.service_names_to_types}

        return self._service_names_to_remap

    def add_service_name_and_type(self, service_name, service_type):
        """
        Associates the name of a Service with the ROS Node

        :param service_name: the name of the associated Service
        :type service_name: str
        :param service_type: the ROS Service type
        :type service_type: str
        """
        service_filter = filters.ServiceTypeFilter.get_filter()
        if not service_filter.should_filter_out(service_type):
            self._service_names_to_types[service_name] = service_type

    @property
    def is_nodelet_manager(self):
        """
        Indicates whether the ROS Node is a Nodelet Manager or not

        :return: True if the ROS Node is a Nodelet Manager; False if not
        :rtype: bool
        """
        return self._is_nodelet_manager

    def _gather_nodelet_manager_status(self):
        """
        Helper method to determine whether the ROS Node is a Nodelet
        Manager based on its ROS Topic types and its ROS Service types

        :return: True if the ROS Node is a Nodelet Manager; False if not
        :rtype: bool
        """
        for topic_name in self.all_topic_names:
            if self.topic_names_to_types[topic_name] == 'bond/Status':
                service_types = set([self.service_names_to_types[service_name] for service_name in self.service_names])
                return ('nodelet/NodeletList' in service_types and
                        'nodelet/NodeletLoad' in service_types and
                        'nodelet/NodeletUnload' in service_types)
        return False

    @property
    def is_nodelet(self):
        """
        Indicates whether the ROS Node is a Nodelet or not

        :return: True if the ROS Node is a Nodelet; False if not
        :rtype: bool
        """
        return self._is_nodelet

    def _gather_nodelet_status(self):
        """
        Helper method to determine whether the ROS Node is a Nodelet
        based on its ROS Topic types and whether it is not a Nodelet
        Manager

        :return: True if the ROS Node is a Nodelet; False if not
        :rtype: bool
        """
        for topic_name in self.all_topic_names:
            if self.topic_names_to_types[topic_name] == 'bond/Status':
                return not self.is_nodelet_manager
        return False

    @property
    def nodelet_manager_name(self):
        """
        Returns the ROS Node's associated Nodelet Manager name, if
        applicable

        :return: associated Nodelet Manager name, if applicable
        :rtype: str
        """
        return self._nodelet_manager_name

    def set_nodelet_manager_name(self, nodelet_manager_name):
        """
        Associates a Nodelet Manager name with the ROS Node, assuming
        that it is a Nodelet at this point

        :param nodelet_manager_name: the name of the Nodelet Manager
        :type nodelet_manager_name: str
        """
        self._nodelet_manager_name = nodelet_manager_name

    @property
    def nodelet_names(self):
        """
        Returns the ROS Node's associated Nodelet names, if applicable

        :return: names of the associated Nodelets
        :rtype: set{str}
        """
        return self._nodelet_names

    def add_nodelet_name(self, nodelet_name):
        """
        Associates a Nodelet name with the ROS Node, assuming that it is
        a Nodelet Manager at this point

        :param nodelet_name: the name of the Nodelet to associate
        :type nodelet_name: str
        """
        self._nodelet_names.add(nodelet_name)

    @property
    def published_nodelet_or_manager_topic_names(self):
        """
        Returns the names of published Nodelet / Nodelet Manager
        Topics

        :return: the names of published Nodelet / Nodelet Manager
            Topics
        :rtype: set{str}
        """
        return self._nodelet_or_manager_topic_names['published']

    @property
    def subscribed_nodelet_or_manager_topic_names(self):
        """
        Returns the names of subscribed Nodelet / Nodelet Manager
        Topics

        :return: the names of subscribed Nodelet / Nodelet Manager
            Topics
        :rtype: set{str}
        """
        return self._nodelet_or_manager_topic_names['subscribed']

    @staticmethod
    def _extract_topics_for_nodelet_or_manager(topic_names, topic_names_to_types):
        """
        Helper method to extract Topics used by the ROS Node in a Nodelet or
        Nodelet Manager role

        :param topic_names: the mutable mapping of roles ('published'
            or 'subscribed') to Topic names from which to extract
            Nodelet / Nodelet Manager Topics from
        :type topic_names: dict{str: set{str}}
        :param topic_names_to_types: the mapping of Topic names to
            the corresponding ROS Topic type
        :type topic_names_to_types: dict{str: str}
        :return: the mapping of roles ('published' or 'subscribed') to
            extracted Nodelet / Nodelet Manager Topic names
        :rtype: dict{str: set{str}}
        """
        bond_topic_type = 'bond/Status'
        nodelet_or_manager_topic_names = {'published': dict(), 'subscribed': dict()}
        for topic_name in set(topic_names['published'].keys()):
            if topic_names_to_types[topic_name] == bond_topic_type:
                nodelet_or_manager_topic_names['published'][topic_name] = topic_names['published'][topic_name]
                topic_names['published'].pop(topic_name, None)
        for topic_name in set(topic_names['subscribed'].keys()):
            if topic_names_to_types[topic_name] == bond_topic_type:
                nodelet_or_manager_topic_names['subscribed'][topic_name] = topic_names['subscribed'][topic_name]
                topic_names['subscribed'].pop(topic_name, None)
        return nodelet_or_manager_topic_names

    def _extract_action_names_and_remove_corresponding_topics(self, topic_bank_builder, action_bank_builder):
        """
        Associates the ROS Node with Action Server / Client related
        Action names from the ActionBankBuilder and removes the
        Action-related Topics from the ROS Node's Topic store

        :param topic_bank_builder: the TopicBankBuilder to use for
            Action-related Topic name removal
        :type topic_bank_builder: TopicBankBuilder
        :param action_bank_builder: the ActionBankBuilder to use for
            Action-related Topic name removal and Action Server / Client
            reference
        :type action_bank_builder: ActionBankBuilder
        :return: the mapping of Action Server / Client roles ('server'
            or 'client') to extracted Action names
        :rtype: dict{str: dict{str:str}}
        """
        extracted_action_names = {'server': dict(), 'client': dict()}
        valid_topic_names = [topic_name for topic_name in topic_bank_builder.names_to_entity_builders.keys()]
        for status, topic_name_dict in {'published': self.published_topic_names,
                                        'subscribed': self.subscribed_topic_names}.items():
            #Logger.get_logger().log(LoggerLevel.INFO,
            #                        'Searching for {} action topics for node {}.'.format(status, self.name))
            for topic_name in set(topic_name_dict.keys()):
                if topic_name not in valid_topic_names:
                    topic_builder = TopicBuilder(topic_name)
                    name_base, name_suffix = topic_builder.name_base, topic_builder.name_suffix
                    if (name_base in action_bank_builder.names_to_entity_builders) and \
                        (name_suffix in ActionBuilder.TOPIC_SUFFIXES):
                        action_builder = action_bank_builder[name_base]
                        log_message = 'Found action {}. Removing topic {} from node {}.'.format(
                            name_base, topic_name, self.name)
                        if self.name in action_builder.client_node_names:
                            extracted_action_names['client'][name_base] = None
                            self.remove_topic_name(topic_name, status)
                        elif self.name in action_builder.server_node_names:
                            extracted_action_names['server'][name_base] = None
                            self.remove_topic_name(topic_name, status)
                        else:
                            log_message = 'Failed to find action {}. Will NOT remove topic {} from node {}.'.format(
                                name_base, topic_name, self.name)
                        Logger.get_logger().log(LoggerLevel.INFO, log_message)
        return extracted_action_names

    @property
    def action_servers(self):
        """
        Returns the set of Action names for which this ROS Node is a
        Server

        :return: Action names where this ROS Node is a Server
        :rtype: set{str}
        """
        return self._action_names['server']

    @property
    def action_clients(self):
        """
        Returns the set of Action names for which this ROS Node is a
        Client

        :return: Action names where this ROS Node is a Client
        :rtype: set{str}
        """
        return self._action_names['client']

    def _populate_metamodel_with_common_info(self, node_metamodel):
        """
        Helper method to populate a Node-based metamodel with all of
        the common fields that a Node has

        :param node_metamodel: the Node to populate
        :type node_metamodel: Node
        :return: the same Node reference (for chained calls)
        :rtype: Node
        """
        node_metamodel.update_attributes(name=self.name,
                                         node=self.node,
                                         uri=self.uri,
                                         executable_name=self.executable_name,
                                         executable_file=self.executable_file,
                                         cmdline=self.executable_cmdline,
                                         num_threads=self.executable_num_threads,
                                         cpu_percent=self.executable_cpu_percent,
                                         memory_percent=self.executable_memory_percent,
                                         memory_info=self.executable_memory_info,
                                         published_topic_names=self.published_topic_names,
                                         subscribed_topic_names=self.subscribed_topic_names,
                                         action_servers=self.action_servers,
                                         action_clients=self.action_clients,
                                         provided_services=self.service_names_with_remap,
                                         set_parameter_names=self.set_parameter_names,
                                         read_parameter_names=self.read_parameter_names)
        return node_metamodel

    def _populate_metamodel_with_nodelet_info(self, nodelet_metamodel):
        """
        Helper method to populate a Nodelet with Nodelet
        related information

        :param nodelet_metamodel: the Nodelet to populate
        :type nodelet_metamodel: Nodelet
        :return: the same Nodelet reference (for chained calls)
        :rtype: Nodelet
        """
        nodelet_metamodel.nodelet_manager_name = self.nodelet_manager_name
        nodelet_metamodel.published_nodelet_topic_names = self.published_nodelet_or_manager_topic_names
        nodelet_metamodel.subscribed_nodelet_topic_names = self.subscribed_nodelet_or_manager_topic_names
        return nodelet_metamodel

    def _populate_metamodel_with_nodelet_manager_info(self, nodelet_manager_metamodel):
        """
        Helper method to populate a NodeletManager with Nodelet
        Manager related information

        :param nodelet_manager_metamodel: the NodeletManager to
            populate
        :type nodelet_manager_metamodel: NodeletManager
        :return: the same NodeletManager reference (for chained
            calls)
        :rtype: NodeletManager
        """
        nodelet_manager_metamodel.nodelet_names = self.nodelet_names
        nodelet_manager_metamodel.published_nodelet_manager_topic_names = self.published_nodelet_or_manager_topic_names
        nodelet_manager_metamodel.subscribed_nodelet_manager_topic_names = self.subscribed_nodelet_or_manager_topic_names
        return nodelet_manager_metamodel

    def extract_metamodel(self):
        """
        Allows the NodeBuilder to create / extract either a
        Node, Nodelet, or NodeletManager
        instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: Node or Nodelet or NodeletManager
        """
        #Logger.get_logger().log(LoggerLevel.INFO, 'Extracting Node for {}...'.format(self.name))
        if self.is_nodelet:
            node_metamodel = self._populate_metamodel_with_nodelet_info(Nodelet(source='ros_snapshot'))
        elif self.is_nodelet_manager:
            node_metamodel = self._populate_metamodel_with_nodelet_manager_info(NodeletManager(source='ros_snapshot'))
        else:
            node_metamodel = Node(source='ros_snapshot')
        return self._populate_metamodel_with_common_info(node_metamodel)
