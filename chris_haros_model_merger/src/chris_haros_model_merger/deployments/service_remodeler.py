# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Service Remodeler class that holds all of the specific
logic to load the CHRIS and HAROS Service models and attempt to fill missing CHRIS
model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class ServiceRemodeler(_BaseRemodeler):
    """
    The `ServiceRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Service Specification
    models, determine which HAROS models are present in the CHRIS models and
    merge them (if applicable), determine which HAROS models are not present
    in the CHRIS models and create them (if applicable)
    """
    TYPE = 'SERVICE'

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A collection of HAROS Services
        :rtype: ResourceCollection<Service>
        """
        return self._haros_configuration.services

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Service Bank Type and Service Model
        :rtype: dict{BankType: Service}
        """
        return {BankType.SERVICE: self._chris_ros_model[BankType.SERVICE]}

    def _helper_merge_haros_services_with_chris_model(self, haros_service_model_links, chris_service_model_nodes, link_type):
        """
        Helper merging method to merge the HAROS Service Node Links with the
        CHRIS Service Nodes

        :param haros_service_model_links: HAROS Service Server or Client Node Links
        :type haros_service_model_links: list[ServicePrimitive]
        :param chris_service_model_nodes: CHRIS Server or Client Node Names
        :type chris_service_model_nodes: set{str}
        :param link_type: Server or Client Link Types (`Provided` or `Client`) for logging
        :type link_type: str
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for haros_link in haros_service_model_links:
            # Handle Error Case Where Link was a `NoneType` - from Acceptance Testing with `chris_rrbot_modeling` demo.
            if haros_link:
                haros_node_instance_name = haros_link.node.id
                if self._check_haros_name_is_complete(haros_node_instance_name, 'Check for Service Nodes'):
                    if haros_node_instance_name not in chris_service_model_nodes:
                        Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Service\'s {} Node "{}" to CHRIS Service.'.format(
                            self.__class__.TYPE, link_type, haros_node_instance_name))
                        chris_service_model_nodes.add(haros_node_instance_name)
                        model_updated = True
            else:
                Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Error Checking HAROS Service\'s Link; no Link available.'.format(
                    self.__class__.TYPE, link_type))
        return model_updated

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Service HAROS model with a specific Service
        CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: Service
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: Service
        """
        model_updated = False
        # VALIDATE Service Types to Alert the User of INCONSISTENT / INACCURATE DATA.
        haros_service_type = haros_model.type
        chris_service_type = chris_model.construct_type
        if (haros_service_type != chris_service_type):
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Service\'s Type "{}" does NOT Match CHRIS Service\'s Type "{}".'.format(
                self.__class__.TYPE, haros_service_type, chris_service_type))
        model_updated |= self._helper_merge_haros_services_with_chris_model(
            [haros_model.server], chris_model.service_provider_node_names, 'Provided')
        chris_model_service_clients = set()
        if self._helper_merge_haros_services_with_chris_model(haros_model.clients, chris_model_service_clients, 'Client'):
            chris_model.service_client_node_names = chris_model_service_clients
            model_updated = True
        return model_updated

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Service CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: Service
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: Service
        """
        new_chris_model_instance.construct_type = haros_model.type
        self._helper_merge_haros_services_with_chris_model(
            [haros_model.server], new_chris_model_instance.service_provider_node_names, 'Provided')
        new_chris_model_instance.service_client_node_names = set()
        self._helper_merge_haros_services_with_chris_model(
            haros_model.clients, new_chris_model_instance.service_client_node_names, 'Client')
