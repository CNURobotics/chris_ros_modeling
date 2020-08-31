# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for TopicBankBuilders, which are responsible for collecting, maintaining,
and populating TopicBuilders for the purpose of extracting metamodel
instances
"""

from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.utilities import filters
from chris_ros_modeling.metamodels import TopicBank
from chris_ros_snapshot.base_builders import _BankBuilder
from chris_ros_snapshot.topic_builder import TopicBuilder
from chris_ros_snapshot.action_builder import ActionBuilder

class TopicBankBuilder(_BankBuilder):
    """
    Defines a TopicBankBuilder which is responsible for collecting,
    maintaining, and populating TopicBuilders for the purpose of
    extracting metamodel instances
    """

    def __init__(self, topic_types):
        """
        Instantiates an instance of the TopicBankBuilder class

        :param topic_types: the collection or iterable of topic name,
            topic type pairs
        :type topic_types: list[tuple(str, str)]
        """
        super(TopicBankBuilder, self).__init__()
        self._topic_types = topic_types

    def _create_entity_builder(self, name):
        """
        Creates and returns a new TopicBuilder instance

        :param name: the name used to instantiate the new TopicBuilder
        :type name: str
        :return: the newly created TopicBuilder
        :rtype: TopicBuilder
        """
        topic_builder = TopicBuilder(name)
        topic_builder.construct_type = self._find_topic_type(topic_builder.name)
        return topic_builder

    def _should_filter_out(self, name, entity_builder):
        """
        Indicates whether the given TopicBuilder (which has a name to
        identify it) should be filtered out or not

        :param name: the name to identify the TopicBuilder
        :type name: str
        :param entity_builder: the TopicBuilder to check
        :type entity_builder: TopicBuilder
        :return: True if the TopicBuilder should be filtered out;
            False if not
        :rtype: bool
        """
        return filters.TopicFilter.get_filter().should_filter_out(name)

    def _find_topic_type(self, desired_topic):
        """
        Helper method that returns the topic type associated with a
        desired topic

        :param desired_topic: the name of the desired topic
        :type desired_topic: str
        :return: the name of the desired topic's type
        :rtype: str
        """
        obtained_topic_type = 'Error: Unknown'
        for topic, topic_type in self._topic_types:
            if topic == desired_topic:
                obtained_topic_type = topic_type
        return obtained_topic_type

    def _create_bank_metamodel(self):
        """
        Creates and returns a new TopicBank instance

        :return: a newly created TopicBank instance
        :rtype: TopicBank
        """
        return TopicBank()

    def extract_action_builders_from_internal_topic_builders(self):
        """
        Helper method that extracts and returns ActionBuilders from
        a grouping of corresponding TopicBuilders in the internal store;
        removes TopicBuilders from the internal store that happen to be
        part of newly extracted and valid ActionBuilders

        :return: a dictionary of action names to ActionBuilders
        :rtype: dict{str: ActionBuilder}
        """
        names_to_action_builders = dict()
        Logger.get_logger().log(LoggerLevel.INFO, 'Searching topics in topic bank for corresponding actions.')
        for topic_builder in self.names_to_entity_builders.values():
            if ActionBuilder.test_potential_action_topic_builder(topic_builder):
                action_name = topic_builder.name_base
                if action_name not in names_to_action_builders.keys():
                    names_to_action_builders[action_name] = ActionBuilder(action_name)
                names_to_action_builders[action_name].add_topic_builder(topic_builder)
        for action_name, action_builder in dict(names_to_action_builders).items():
            if not action_builder.validate_action_topic_builders():
                log_message = 'Action {} NOT valid. Not removing topics from topic bank.'.format(action_name)
                names_to_action_builders.pop(action_name)
            else:
                log_message = 'Action {} is valid. Removing corresponding topics from topic bank.'.format(action_name)
                self._remove_action_topic_builders(action_builder.topic_names_to_builders.values())
            Logger.get_logger().log(LoggerLevel.INFO, log_message)
        return names_to_action_builders

    def _remove_action_topic_builders(self, action_topic_builders):
        """
        Removes TopicBuilders from the internal store if they are a
        part of the provided ActionBuilders

        :param action_topic_builders: a collection of ActionBuilders
        :type action_topic_builders: list[ActionBuilder]
        """
        for action_topic_builder in action_topic_builders:
            self.names_to_entity_builders.pop(action_topic_builder.name)
