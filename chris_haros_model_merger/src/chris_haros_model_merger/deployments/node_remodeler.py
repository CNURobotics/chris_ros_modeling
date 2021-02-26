# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Node Remodeler class that holds all of the specific
logic to load the CHRIS and HAROS Node models and attempt to fill missing CHRIS
model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class NodeRemodeler(_BaseRemodeler):
    """
    The `NodeRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Node
    models, determine which HAROS models are present in the CHRIS models and
    merge them (if applicable), determine which HAROS models are not present
    in the CHRIS models and create them (if applicable)
    """
    TYPE = 'NODE'

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A collection of HAROS Nodes
        :rtype: ResourceCollection<NodeInstance>
        """
        return self._haros_configuration.nodes

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Node, Nodelet, and Nodelet Manager Bank Types and Node,
            Nodelet, and Nodelet Managers Model
        :rtype: dict{BankType: Node | Nodelet | NodeletManager}
        """
        return {BankType.NODE: self._chris_ros_model[BankType.NODE],
                BankType.NODELET: self._chris_ros_model[BankType.NODELET],
                BankType.NODELET_MANAGER: self._chris_ros_model[BankType.NODELET_MANAGER]}

    def _merge_haros_node_links_with_chris_node_services(self, haros_node_model_links, chris_node_model_services, link_type):
        """
        Helper merging method to merge the HAROS Node Service Links with the
        CHRIS Node Services

        :param haros_node_model_links: HAROS Service Server or Client Links
        :type haros_node_model_links: list[ServicePrimitive]
        :param chris_node_model_services: CHRIS Provided or Client Service Names to Types
        :type chris_node_model_services: dict{str: str}
        :param link_type: Server or Client Link Types (`Provided` or `Client`) for logging
        :type link_type: str
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for haros_link in haros_node_model_links:
            haros_service_instance_name = haros_link.service.id
            if self._check_haros_name_is_complete(haros_service_instance_name, 'Check for Node Services'):
                # VALIDATE Service Parent Types to Alert the User of INCONSISTENT / INACCURATE DATA.
                if haros_service_instance_name in chris_node_model_services:
                    haros_service_parent_type = haros_link.service.name
                    chris_service_parent_type = chris_node_model_services[haros_service_instance_name]
                    if haros_service_parent_type != chris_service_parent_type:
                        Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS "{}" Service Parent\'s Type "{}" for Service "{}" does NOT Match CHRIS Service Parent\'s Type "{}".'.format(
                            self.__class__.TYPE, link_type, haros_service_parent_type, haros_service_instance_name, chris_service_parent_type))
                # elif haros_service_instance_name not in chris_node_model_services:
                else:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Node\'s {} Service "{}" to CHRIS Node Instance.'.format(
                        self.__class__.TYPE, link_type, haros_service_instance_name))
                    chris_node_model_services[haros_service_instance_name] = haros_link.service.name
                    model_updated = True
        return model_updated

    def _merge_haros_node_links_with_chris_node_parameters(self, haros_node_model_links, chris_node_model_parameters, link_type):
        """
        Helper merging method to merge the HAROS Node Parameters Links with the
        CHRIS Node Parameters

        :param haros_node_model_links: HAROS Read or Written Parameter Links
        :type haros_node_model_links: list[ParameterPrimitive]
        :param chris_node_model_parameters: CHRIS Written or Read Parameter Names to Types
        :type chris_node_model_parameters: dict{str: str}
        :param link_type: Read or Written Link Types (`Read` or `Set`) for logging
        :type link_type: str
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for haros_link in haros_node_model_links:
            haros_parameter_instance_name = haros_link.param_name
            if self._check_haros_name_is_complete(haros_parameter_instance_name, 'Check for Node Parameters'):
                # VALIDATE Parameter Parent Types to Alert the User of INCONSISTENT / INACCURATE DATA.
                if haros_parameter_instance_name in chris_node_model_parameters:
                    haros_parameter_parent_type = haros_link.parameter.name
                    chris_parameter_parent_type = chris_node_model_parameters[
                        haros_parameter_instance_name]
                    if haros_parameter_parent_type != chris_parameter_parent_type:
                        Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS "{}" Parameter Parent\'s Type "{}" for Parameter "{}" does NOT Match CHRIS Parameter Parent\'s Type "{}".'.format(
                            self.__class__.TYPE, link_type, haros_parameter_parent_type, haros_parameter_instance_name, chris_parameter_parent_type))
                # elif haros_parameter_instance_name not in chris_node_model_parameters:
                else:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Node\'s {} Parameter "{}" to CHRIS Node Instance.'.format(
                        self.__class__.TYPE, link_type, haros_parameter_instance_name))
                    chris_node_model_parameters[haros_parameter_instance_name] = haros_link.parameter.name
                    model_updated = True
        return model_updated

    def _merge_haros_node_links_with_chris_node_topics(self, bank_type, haros_node_model, chris_node_model):
        """
        Helper merging method to merge the HAROS Node Topic Links with the
        CHRIS Node Topics

        :param bank_type: the corresponding CHRIS model Bank Type
        :type bank_type: BankType
        :param haros_node_model: the HAROS Node model
        :type haros_node_model: NodeInstance
        :param chris_node_model: the CHRIS Node model
        :type chris_node_model: Node
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        link_types = {'Published': (haros_node_model.publishers, chris_node_model.published_topic_names),
                      'Subscribed': (haros_node_model.subscribers, chris_node_model.subscribed_topic_names)}
        for link_type in link_types.keys():
            for haros_link in link_types[link_type][0]:
                haros_topic_instance_name = haros_link.topic_name
                if self._check_haros_name_is_complete(haros_topic_instance_name, 'Check for Node Topics'):
                    chris_node_model_topics = link_types[link_type][1]
                    # VALIDATE Topic Parent Types to Alert the User of INCONSISTENT / INACCURATE DATA.
                    if haros_topic_instance_name in chris_node_model_topics:
                        haros_topic_parent_type = haros_link.topic.name
                        chris_topic_parent_type = chris_node_model_topics[haros_topic_instance_name]
                        if haros_topic_parent_type != chris_topic_parent_type:
                            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS "{}" Topic Parent\'s Type "{}" for Topic "{}" does NOT Match CHRIS Topic Parent\'s Type "{}".'.format(
                                self.__class__.TYPE, link_type, haros_topic_parent_type, haros_topic_instance_name, chris_topic_parent_type))
                    elif ((haros_topic_instance_name not in chris_node_model_topics) and
                          (not self._topic_is_part_of_action(haros_topic_instance_name))):
                        if haros_link.topic.name != 'bond/Status':
                            Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Node\'s "{}" Topic "{}" to CHRIS Node Instance.'.format(
                                self.__class__.TYPE, link_type, haros_topic_instance_name))
                            chris_node_model_topics[haros_topic_instance_name] = haros_link.topic.name
                            model_updated = True
                        else:
                            # DECISION: Since HAROS does not provide full functionality to determine whether Nodelets
                            # exist vs. Nodelet Managers, the ability to determine which Topics are specifically
                            # related to being a Nodelet / Nodelet Manager, and since from sample data / testing,
                            # known Nodelets and Nodelet Managers were not discovered as having a Bond Topic with
                            # HAROS, so we will trust our `chris_ros_snapshot` to provide it. For simplicity,
                            # if we encounter a Bond Topic that is not already associated with a given Node /
                            # Nodelet / Nodelet Manger, then we just print an Error Log Message.
                            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Found HAROS Node\'s "{}" Bond Topic; "{}" NOT added to CHRIS Node Instance (Node Exists in "{}").'.format(
                                self.__class__.TYPE, link_type, haros_topic_instance_name, bank_type))
        return model_updated

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Node HAROS model with a specific Node CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: NodeInstance
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: Node
        """
        model_updated = False
        if not chris_model.node:
            chris_model.node = haros_model.node.node_name
            model_updated = True
        if not chris_model.cmdline:
            chris_model.cmdline = haros_model.argv
            model_updated = True
        if haros_model.launch:
            chris_model.launch_file = haros_model.launch.path
            model_updated = True
        model_updated |= self._merge_haros_node_links_with_chris_node_parameters(
            haros_model.writes, chris_model.set_parameter_names, 'Set')
        model_updated |= self._merge_haros_node_links_with_chris_node_parameters(
            haros_model.reads, chris_model.read_parameter_names, 'Read')
        model_updated |= self._merge_haros_node_links_with_chris_node_services(
            haros_model.servers, chris_model.provided_services, 'Provided')
        chris_model_client_services = dict()
        if self._merge_haros_node_links_with_chris_node_services(haros_model.clients, chris_model_client_services, 'Client'):
            chris_model.client_services = chris_model_client_services
            model_updated = True
        model_updated |= self._merge_haros_node_links_with_chris_node_topics(
            bank_type, haros_model, chris_model)
        # DECISION: Do we want to handle population of CHRIS Node's `action_servers` and `action_clients`?
        # No. Since HAROS does not provide this functionality, we will trust our `chris_ros_snapshot` to
        # provide it.
        return model_updated

    def _create_new_chris_model(self, instance_name, haros_instance):
        """
        Creates a new Node CHRIS model with the instance name and based on the
        corresponding HAROS instance

        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_instance: the corresponding HAROS model
        :type haros_instance: NodeInstance
        :return: a tuple containing the Bank Type and new CHRIS model
        :rtype: Tuple(BankType, Node)
        """
        # DECISION: If HAROS cannot provide the ability to distinguish between a Nodelet and a Nodelet Manager, we will
        # just attempt to populate the newly created model into a Nodelet Bank (if we can tell if the HAROS
        # model represents a Nodelet) or just the Node Bank otherwise (which will catch Nodelet Managers
        # since there is no easy way to tell if it is a Manager). Besides, we should be able to gather all
        # Nodes using our CHRIS ROS Snapshot tool.
        if haros_instance.node.nodelet_class:
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Create new chris nodelet model"{}".'.format(
                self.__class__.TYPE, instance_name))

            return (BankType.NODELET, self._chris_model_banks[BankType.NODELET][instance_name])

        Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Create new chris node model"{}".'.format(
            self.__class__.TYPE, instance_name))
        return (BankType.NODE, self._chris_model_banks[BankType.NODE][instance_name])

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Node CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: NodeInstance
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: Node
        """
        new_chris_model_instance.node = haros_model.node.node_name
        new_chris_model_instance.cmdline = haros_model.argv
        # Prevent Errors Grabbing Path if Launch is `NoneType`.
        if haros_model.launch:
            new_chris_model_instance.launch_file = haros_model.launch.path
        self._merge_haros_node_links_with_chris_node_parameters(
            haros_model.writes, new_chris_model_instance.set_parameter_names, 'Set')
        self._merge_haros_node_links_with_chris_node_parameters(
            haros_model.reads, new_chris_model_instance.read_parameter_names, 'Read')
        self._merge_haros_node_links_with_chris_node_services(
            haros_model.servers, new_chris_model_instance.provided_services, 'Provided')
        new_chris_model_instance.client_services = dict()
        self._merge_haros_node_links_with_chris_node_services(
            haros_model.clients, new_chris_model_instance.client_services, 'Client')
        self._merge_haros_node_links_with_chris_node_topics(
            bank_type, haros_model, new_chris_model_instance)
