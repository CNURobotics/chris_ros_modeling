# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Node Specification Remodeler class that holds all of
the specific logic to load the CHRIS and HAROS Node Specification models and
attempt to fill missing CHRIS model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class NodeSpecificationRemodeler(_BaseRemodeler):
    """
    The `NodeSpecificationRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Node Specification
    models, determine which HAROS models are present in the CHRIS models and
    merge them (if applicable), determine which HAROS models are not present
    in the CHRIS models and create them (if applicable)
    """
    TYPE = 'NODE_SPECIFICATION'

    @staticmethod
    def _adjust_haros_name(haros_name):
        """
        Adjusts the HAROS string name to match format of desired Node Specification

        :param haros_name: the HAROS name
        :type haros_name: str
        :return: the modified HAROS name
        :rtype: str
        """
        return haros_name.replace('node:', '')

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A set of HAROS Node Specifications
        :rtype: set(Node)
        """
        encountered_haros_node_spec_ids = set()
        haros_node_specs = set()
        for haros_node_instance in self._haros_configuration.nodes:
            haros_node_spec_id = haros_node_instance.node.id
            if (haros_node_spec_id not in encountered_haros_node_spec_ids):
                haros_node_specs.add(haros_node_instance.node)
                encountered_haros_node_spec_ids.add(haros_node_spec_id)
        return haros_node_specs

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Node Specification Bank Type and Node Specification Model
        :rtype: dict{BankType: NodeSpecification}
        """
        return {BankType.NODE_SPECIFICATION: self._chris_ros_model[BankType.NODE_SPECIFICATION]}

    def _merge_haros_node_calls_with_chris_node_services(self, haros_node_model_calls, chris_node_model_services, call_type):
        """
        Helper merging method to merge the HAROS Node Specification Service
        Calls with the CHRIS Node Specification Services

        :param haros_node_model_calls: HAROS Service Server or Client Calls
        :type haros_node_model_calls: list[RosPrimitiveCall]
        :param chris_node_model_services: CHRIS Provided or Client Service Names to Types
        :type chris_node_model_services: dict{str: str}
        :param call_type: Server or Client Call Types (`Provided` or `Client`) for logging
        :type call_type: str
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for haros_call in haros_node_model_calls:
            haros_service_name = haros_call.name
            if self._check_haros_name_is_complete(haros_service_name, 'Check for Node Spec Service'):
                # VALIDATE Service Types to Alert the User of INCONSISTENT / INACCURATE DATA.
                if haros_service_name in chris_node_model_services:
                    haros_service_type = haros_call.type
                    chris_service_type = chris_node_model_services[haros_service_name]
                    if haros_service_type != chris_service_type:
                        Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS "{}" Service Type "{}" for Service "{}" does NOT Match CHRIS Service Type "{}".'.format(
                            self.__class__.TYPE, call_type, haros_service_type, haros_service_name, chris_service_type))
                # elif haros_service_name not in chris_node_model_services:
                else:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Node Spec\'s {} Service "{}" to CHRIS Node Spec.'.format(
                        self.__class__.TYPE, call_type, haros_service_name))
                    chris_node_model_services[haros_service_name] = haros_call.type
                    model_updated = True
        return model_updated

    def _merge_haros_node_calls_with_chris_node_parameters(self, haros_node_model_written_param_calls, haros_node_model_read_param_calls, chris_node_model):
        """
        Helper merging method to merge the HAROS Node Specification Parameter
        Calls with the CHRIS Node Specification Parameters

        :param haros_node_model_written_param_calls: HAROS Written Parameter Calls
        :type haros_node_model_written_param_calls: list[WriteParameterCall]
        :param haros_node_model_read_param_calls: HAROS Read Parameter Calls
        :type haros_node_model_read_param_calls: list[ReadParameterCall]
        :param chris_node_model: CHRIS Node Model
        :type chris_node_model: NodeSpecification
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        haros_node_model_param_calls = list(
            haros_node_model_written_param_calls)
        haros_node_model_param_calls.extend(haros_node_model_read_param_calls)
        for haros_call in haros_node_model_param_calls:
            haros_parameter_name = haros_call.name
            if self._check_haros_name_is_complete(haros_parameter_name, 'Check for Node Spec Parameter'):
                # " VALIDATE Parameter Types to Alert the User of INCONSISTENT / INACCURATE DATA. "

                if chris_node_model.parameters is None:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding parameter dictionary to CHRIS Node Spec.'.format(
                        self.__class__.TYPE, chris_node_model.name))
                    chris_node_model.parameters = dict()

                if haros_parameter_name in chris_node_model.parameters:
                    haros_parameter_type = haros_call.type.replace(
                        'double', 'float').replace('string', 'str')
                    chris_parameter_type = chris_node_model.parameters[haros_parameter_name]
                    if haros_parameter_type != chris_parameter_type:
                        Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Parameter Type "{}" for Parameter "{}" does NOT Match CHRIS Parameter Type "{}".'.format(
                            self.__class__.TYPE, haros_parameter_type, haros_parameter_name, chris_parameter_type))
                # elif haros_parameter_name not in chris_node_model.parameters:
                else:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Node Spec\'s Parameter "{}" to CHRIS Node Spec.'.format(
                        self.__class__.TYPE, haros_parameter_name))
                    chris_node_model.parameters[haros_parameter_name] = haros_call.type.replace(
                        'double', 'float').replace('string', 'str')
                    model_updated = True
        return model_updated

    def _merge_haros_node_calls_with_chris_node_topics(self, haros_node_model, chris_node_model):
        """
        Helper merging method to merge the HAROS Node Specification Topic
        Calls with the CHRIS Node Specification Topics

        :param haros_node_model: the HAROS Node Specification model
        :type haros_node_model: Node
        :param chris_node_model: the CHRIS Node Specification model
        :type chris_node_model: NodeSpecification
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        if haros_node_model.advertise and chris_node_model.published_topics is None:
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Adding published topics to node model "{}".'.format(
                self.__class__.TYPE, chris_node_model.name))
            chris_node_model.published_topics = dict()
        if haros_node_model.subscribe and chris_node_model.subscribed_topics is None:
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Adding subscribed topics to node model "{}".'.format(
                self.__class__.TYPE, chris_node_model.name))
            chris_node_model.subscribed_topics = dict()

        call_types = {'Published': (haros_node_model.advertise, chris_node_model.published_topics),
                      'Subscribed': (haros_node_model.subscribe, chris_node_model.subscribed_topics)}
        for call_type in call_types.keys():
            for haros_call in call_types[call_type][0]:
                haros_topic_name = haros_call.name.split('/')[-1]  # Obtain Parent Name Like Other CHRIS Tools
                if self._check_haros_name_is_complete(haros_topic_name, 'Check for Node Spec Topic'):
                    chris_node_model_topics = call_types[call_type][1]

                    # VALIDATE Topic Types to Alert the User of INCONSISTENT / INACCURATE DATA.
                    if haros_topic_name in chris_node_model_topics:
                        haros_topic_type = haros_call.type
                        chris_topic_type = chris_node_model_topics[haros_topic_name]
                        if haros_topic_type != chris_topic_type:
                            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS "{}" Topic Type "{}" for Topic "{}" does NOT Match CHRIS Topic Type "{}".'.format(
                                self.__class__.TYPE, call_type, haros_topic_type, haros_topic_name, chris_topic_type))
                    else:
                        Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Node Spec\'s {} Topic "{}" to CHRIS Node Spec.'.format(
                            self.__class__.TYPE, call_type, haros_topic_name))
                        chris_node_model_topics[haros_topic_name] = haros_call.type
                        model_updated = True
        return model_updated

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Node Specification HAROS model with a specific
        Node Specification CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: Node
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: NodeSpecification
        """
        model_updated = False
        haros_package_name = haros_model.package.name
        chris_package_name = chris_model.package

        if haros_package_name != chris_package_name:
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Node Spec\'s Package Name "{}" does NOT Match CHRIS Node Spec\'s Package Name "{}".'.format(
                self.__class__.TYPE, haros_package_name, chris_package_name))
        # Note: The `source_files` list and the `source_tree` object would seem like useful starting places to extract
        # values from the HAROS Model to populate the `file_path` field of the CHRIS Model. However, these values
        # never seem to be populated or instantiated, respectively, with any data.
        model_updated |= self._merge_haros_node_calls_with_chris_node_parameters(
            haros_model.write_param, haros_model.read_param, chris_model)
        model_updated |= self._merge_haros_node_calls_with_chris_node_services(
            haros_model.service, chris_model.services_provided, 'Provided')
        chris_model_client_services = dict()
        if self._merge_haros_node_calls_with_chris_node_services(haros_model.client, chris_model_client_services, 'Client'):
            chris_model.client_services = chris_model_client_services
            model_updated = True
        model_updated |= self._merge_haros_node_calls_with_chris_node_topics(
            haros_model, chris_model)
        return model_updated

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Node Specification CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: Node
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: NodeSpecification
        """
        new_chris_model_instance.package = haros_model.package.name
        # Correct Error (Workaround) Where Metamodel does not Initialize Member `parameters`
        # with `dict`.
        #new_chris_model_instance.parameters = dict()
        self._merge_haros_node_calls_with_chris_node_parameters(
            haros_model.write_param, haros_model.read_param, new_chris_model_instance)
        # Correct Error (Workaround) Where Metamodel does not Initialize Member `services_provided`
        # with `dict`.
        new_chris_model_instance.services_provided = dict()
        self._merge_haros_node_calls_with_chris_node_services(
            haros_model.service, new_chris_model_instance.services_provided, 'Provided')
        new_chris_model_instance.client_services = dict()
        self._merge_haros_node_calls_with_chris_node_services(
            haros_model.client, new_chris_model_instance.client_services, 'Client')
        # Correct Error (Workaround) Where Metamodel does not Initialize Members `published_topics`
        # and `subscribed_topics` with `dict`s.
        new_chris_model_instance.published_topics = dict()
        new_chris_model_instance.subscribed_topics = dict()
        self._merge_haros_node_calls_with_chris_node_topics(
            haros_model, new_chris_model_instance)
