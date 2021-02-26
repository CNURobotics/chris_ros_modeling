# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Topic Remodeler class that holds all of the specific
logic to load the CHRIS and HAROS Topic models and attempt to fill missing CHRIS
model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class TopicRemodeler(_BaseRemodeler):
    """
    The `TopicRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Topic Specification
    models, determine which HAROS models are present in the CHRIS models and
    merge them (if applicable), determine which HAROS models are not present
    in the CHRIS models and create them (if applicable)
    """
    TYPE = 'TOPIC'

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A collection of HAROS Topics
        :rtype: ResourceCollection<Topic>
        """
        return self._haros_configuration.topics

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Topic Bank Type and Topic Model
        :rtype: dict{BankType: Topic}
        """
        return {BankType.TOPIC: self._chris_ros_model[BankType.TOPIC]}

    def _merge_haros_topic_links_with_chris_topic_nodes(self, haros_topic_model, chris_topic_model):
        """
        Helper merging method to merge the HAROS Topic Node Links with the
        CHRIS Topic Nodes

        :param haros_topic_model: the HAROS Topic model
        :type haros_topic_model: Topic
        :param chris_topic_model: the CHRIS Topic model
        :type chris_topic_model: Topic
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for link in haros_topic_model.publishers:
            haros_node_instance_name = link.node.id
            if self._check_haros_name_is_complete(haros_node_instance_name, 'Check for Topic Nodes'):
                if haros_node_instance_name not in chris_topic_model.publisher_node_names:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Topic\'s Publisher Node "{}" to CHRIS Topic Instance.'.format(
                        self.__class__.TYPE, haros_node_instance_name))
                    chris_topic_model.publisher_node_names.add(
                        haros_node_instance_name)
                    model_updated = True
        for link in haros_topic_model.subscribers:
            haros_node_instance_name = link.node.id
            if self._check_haros_name_is_complete(haros_node_instance_name, 'Check for Topic Nodes'):
                if haros_node_instance_name not in chris_topic_model.subscriber_node_names:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Topic\'s Subscriber Node "{}" to CHRIS Topic Instance.'.format(
                        self.__class__.TYPE, haros_node_instance_name))
                    chris_topic_model.subscriber_node_names.add(
                        haros_node_instance_name)
                    model_updated = True
        return model_updated

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Topic HAROS model with a specific Topic
        CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: Topic
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: Topic
        """
        model_updated = False
        haros_topic_type = haros_model.type
        chris_topic_type = chris_model.construct_type
        # VALIDATE Topic Types to Alert the User of INCONSISTENT / INACCURATE DATA.
        if haros_topic_type != chris_topic_type:
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Topic\'s Type "{}" does NOT Match CHRIS Topic\'s Type "{}".'.format(
                self.__class__.TYPE, haros_topic_type, chris_topic_type))
        model_updated |= self._merge_haros_topic_links_with_chris_topic_nodes(
            haros_model, chris_model)
        return model_updated

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Topic CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: Topic
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: Topic
        """
        new_chris_model_instance.construct_type = haros_model.type
        self._merge_haros_topic_links_with_chris_topic_nodes(
            haros_model, new_chris_model_instance)
