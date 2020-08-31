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

from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.metamodels import Action
from chris_ros_snapshot.base_builders import _EntityBuilder


class ActionBuilder(_EntityBuilder):
    """
    Defines an ActionBuilder, which represents a ROS
    Action and is responsible for allowing itself to be
    populated with basic information relevant to an Action and then
    further populating itself from that information for the purpose
    of extracting a metamodel instance
    """
    CLIENT_PUBLISHED_TOPIC_SUFFIXES = {'/cancel', '/goal'}
    SERVER_PUBLISHED_TOPIC_SUFFIXES = {'/feedback', '/result', '/status'}
    TOPIC_SUFFIXES = CLIENT_PUBLISHED_TOPIC_SUFFIXES | SERVER_PUBLISHED_TOPIC_SUFFIXES
    NUM_TOPIC_SUFFIXES = len(TOPIC_SUFFIXES)
    CORE_TOPIC_SUFFIXES_TO_TYPE_TOKENS = {'/feedback': 'Feedback', '/goal': 'Goal', '/result': 'Result'}

    def __init__(self, name):
        """
        Instantiates an instance of the ActionBuilder

        :param name: the name of the Action that this ActionBuilder
            represents
        :type name: str
        """
        super(ActionBuilder, self).__init__(name)
        self._construct_type = None  # Set during validation
        self._topic_names_to_builders = dict()
        self._topic_name_suffixes_to_builders = dict()
        self._client_node_names = set()
        self._server_node_names = set()

    @property
    def construct_type(self):
        """
        Returns this Action's ROS type

        :return: this Action's ROS type
        :rtype: str
        """
        if self._construct_type is None:
            self._extract_action_construct_type()
        return self._construct_type

    def prepare(self, **kwargs):
        """
        Allows this ActionBuilder to prepare its internal state
        for eventual metamodel extraction; internal changes to the state
        of the class instance occur here

        :param kwargs: keyword arguments used in the preparation process
        :type kwargs: dict{param: value}
        """
        for topic_builder in self.topic_names_to_builders.values():
            topic_builder.prepare()
        self._client_node_names, self._server_node_names = self._gather_action_client_and_server_names()

    @property
    def topic_names_to_builders(self):
        """
        Returns the mapping of Topic names to TopicBuilders that
        represent the Topics that are part of the Action

        :return: the mapping of Topic names to TopicBuilders
        :rtype: dict{str: TopicBuilder}
        """
        return self._topic_names_to_builders

    @property
    def topic_name_suffixes_to_builders(self):
        """
        Returns the mapping of Topic name suffixes (last token) to
        TopicBuilders that represent the Topics that are part of the
        Action

        :return: the mapping of Topic suffix names to TopicBuilders
        :rtype: dict{str: TopicBuilder}
        """
        return self._topic_name_suffixes_to_builders

    def add_topic_builder(self, topic_builder):
        """
        Adds a TopicBuilder that represents the Topic that is part of
        the Action

        :param topic_builder: the TopicBuilder to add to the Action
        :type topic_builder: TopicBuilder
        """
        self._topic_names_to_builders[topic_builder.name] = topic_builder
        self._topic_name_suffixes_to_builders[topic_builder.name_suffix] = topic_builder

    @property
    def client_node_names(self):
        """
        Returns the names of Client ROS Nodes for this Action

        :return: the names of Client ROS Nodes for this Action
        :rtype: set{str}
        """
        return self._client_node_names

    @property
    def server_node_names(self):
        """
        Returns the names of Server ROS Nodes for this Action

        :return: the names of Server ROS Nodes for this Action
        :rtype: set{str}
        """
        return self._server_node_names

    def _count_action_node_appearances(self, publisher_suffixes, subscriber_suffixes, action_node_to_counts):
        """
        Helper method to count the number of appearances or cases in
        which the suspected ROS Nodes, acting in either a Client or
        Server capacity, are found to Publish or Subscribe to Topics
        ending in the expected Topic suffixes

        :param publisher_suffixes: the expected suffixes to check for
            Published Topics by the ROS Nodes
        :type publisher_suffixes: set{str}
        :param subscriber_suffixes: the expected suffixes to check for
            Subscribed Topics by the ROS Nodes
        :type subscriber_suffixes: set{str}
        :param action_node_to_counts: the mapping of Action Server or
            Action Client ROS Node names to appearance counts
        :type action_node_to_counts: dict{str: int}
        """
        for suffix in publisher_suffixes:
            topic_builder = self.topic_name_suffixes_to_builders[suffix]
            for action_node_name in topic_builder.publisher_node_names:
                ActionBuilder._add_or_increment_dictionary_count(action_node_to_counts, action_node_name)
        for suffix in subscriber_suffixes:
            topic_builder = self.topic_name_suffixes_to_builders[suffix]
            for action_node_name in topic_builder.subscriber_node_names:
                ActionBuilder._add_or_increment_dictionary_count(action_node_to_counts, action_node_name)

    @staticmethod
    def _add_or_increment_dictionary_count(counts_dictionary, key):
        """
        Helper method to add an entry for a given key or increment the
        integer value for an entry in a given dictionary of keys to
        counts

        :param counts_dictionary: the mapping of keys to integer counts
        :type counts_dictionary: dict{str: int}
        :param key: the key to add (value of 1) or to increment an entry
            for (by a value of 1)
        :type key: str
        """
        if key not in counts_dictionary:
            counts_dictionary[key] = 0
        counts_dictionary[key] += 1

    @staticmethod
    def _gather_valid_action_node_names_based_on_appearance_counts(action_node_names_to_counts):
        """
        Helper method to create a collection of valid ROS Node names,
        acting in either a Server or Client manner, based on how many
        appearances are found between expected Topics and the ROS Nodes
        Publishing or Subscribing to them

        :param action_node_names_to_counts: the mapping of ROS Node
            names to appearance counts
        :type action_node_names_to_counts: dict{str: int}
        :return: valid Action Server and Client ROS Node names
        :rtype: set{str}
        """
        valid_node_names = set()
        for node_name, appearance_count in action_node_names_to_counts.items():
            if appearance_count == ActionBuilder.NUM_TOPIC_SUFFIXES:
                valid_node_names.add(node_name)
            else:
                Logger.get_logger().log(LoggerLevel.ERROR,
                                        'Node name {} for Action not valid as action client or server.'.format(node_name))
        return valid_node_names

    def _gather_action_client_and_server_names(self):
        """
        Helper method to gather valid Action Client and Action Server
        ROS Node names for this Action

        :return: the tuple of Action Client ROS Node names and Action
            Server ROS Node names
        :rtype: tuple(set{str}, set{str})
        """
        action_client_names_to_counts = dict()
        action_server_names_to_counts = dict()
        self._count_action_node_appearances(ActionBuilder.CLIENT_PUBLISHED_TOPIC_SUFFIXES,
                                            ActionBuilder.SERVER_PUBLISHED_TOPIC_SUFFIXES,
                                            action_client_names_to_counts)
        self._count_action_node_appearances(ActionBuilder.SERVER_PUBLISHED_TOPIC_SUFFIXES,
                                            ActionBuilder.CLIENT_PUBLISHED_TOPIC_SUFFIXES,
                                            action_server_names_to_counts)
        valid_action_client_names = ActionBuilder._gather_valid_action_node_names_based_on_appearance_counts(
            action_client_names_to_counts)
        valid_action_server_names = ActionBuilder._gather_valid_action_node_names_based_on_appearance_counts(
            action_server_names_to_counts)
        return (valid_action_client_names, valid_action_server_names)

    @classmethod
    def test_potential_action_topic_builder(cls, action_topic):
        """
        Verifies whether a potential Action TopicBuilder has a name
        suffix that falls within the set of expected Action Topic
        suffixes

        :param action_topic: the potential Action TopicBuilder to test
        :type action_topic: TopicBuilder
        :return: True if the TopicBuilder's name suffix falls in the
            expected Action Topic suffixes; False if not
        :rtype: bool
        """
        return action_topic.name_suffix in cls.TOPIC_SUFFIXES

    @classmethod
    def _validate_topic_builders_have_required_suffixes(cls, topic_builders):
        """
        Helper method to verify if the provided TopicBuilders meet
        the minimum requirements to potentially make up this Action;
        this means that at least 3 TopicBuilders were provided and
        have name suffixes that are part of the set of expected
        Action Topic suffixes

        :param topic_builders: the collection of TopicBuilders to check
        :type topic_builders: list[TopicBuilder]
        :return: True if the conditions have been met to consider these
            TopicBuilders as valid to be part of an Action; False if
            not
        :rtype: bool
        """
        found_topic_suffixes = {topic_builder.name_suffix for topic_builder in topic_builders}
        return (len(found_topic_suffixes) >= 3) and (found_topic_suffixes.issubset(cls.TOPIC_SUFFIXES))

    @classmethod
    def _validate_core_topic_builders_have_required_types(cls, topic_name_suffixes_to_builders):
        """
        Helper method to verify if the provided TopicBuilders meet more
        specific requirements to make up this Action; this means that
        the expected Core Topic suffixes that make up any Action must
        be found amongst the provided TopicBuilders and they must all
        have ROS Types that include the expected 'Action<Type>' format

        :param topic_name_suffixes_to_builders: the mapping of Topic
            name suffixes to TopicBuilders to check
        :type topic_name_suffixes_to_builders: dict{str: TopicBuilder}
        :return: True if the conditions have been met to consider these
            TopicBuilders as valid to be part of an Action; False if
            not
        :rtype: bool
        """
        for core_topic_name_suffix, core_topic_type_token in cls.CORE_TOPIC_SUFFIXES_TO_TYPE_TOKENS.items():
            if core_topic_name_suffix not in topic_name_suffixes_to_builders.keys():
                return False
            topic_builder_type = topic_name_suffixes_to_builders[core_topic_name_suffix].construct_type
            if not topic_builder_type.endswith('Action{}'.format(core_topic_type_token)):
                return False
        return True

    def validate_action_topic_builders(self):
        """
        Verifies if the TopicBuilders that make up this Action are,
        in fact, valid and should actually make up this Action

        :return: True if the TopicBuilders are valid; False if not
        :rtype: bool
        """
        valid_topic_suffixes = ActionBuilder._validate_topic_builders_have_required_suffixes(
            self.topic_names_to_builders.values())
        valid_core_topic_types = ActionBuilder._validate_core_topic_builders_have_required_types(
            self.topic_name_suffixes_to_builders)
        return valid_topic_suffixes and valid_core_topic_types

    def _extract_suffix_names_to_topic_metamodels(self):
        """
        Helper method to extract and return a mapping of Action Topic
        name suffixes to Topic models from the TopicBuilders that
        make up this Action

        :return: the mapping of Action Topic name suffixes to extracted
            Topics
        :rtype: dict{str: Topic}
        """
        return {key: self.topic_name_suffixes_to_builders[key].extract_metamodel() for key in ActionBuilder.TOPIC_SUFFIXES}

    def _extract_action_construct_type(self):
        """
        Helper method to extract the Action's ROS type based on the
        common prefix of the Core Topic ROS types that make up this
        Action

        :raises ValueError: if an expected Core Topic name suffix does
            not have a corresponding TopicBuilder in the Action; if an
            expected Core Topic name maps to a TopicBuilder that does
            not have a ROS type that follows the 'Action<Type>' format;
            if the expected Core Topic name suffixes map to
            TopicBuilders that have ROS types that have conflicting
            prefixes
        """
        for core_topic_name_suffix, core_topic_type_token in self.CORE_TOPIC_SUFFIXES_TO_TYPE_TOKENS.items():
            if core_topic_name_suffix not in self._topic_name_suffixes_to_builders.keys():
                raise ValueError(" ActionBuilder: Invalid construct type for topics for {} {}".format(
                    self.name, core_topic_name_suffix))

            topic_builder_type = self._topic_name_suffixes_to_builders[core_topic_name_suffix].construct_type
            if not topic_builder_type.endswith('Action{}'.format(core_topic_type_token)):
                raise ValueError(" ActionBuilder: Invalid construct type for {} from {}".format(
                    self.name, topic_builder_type.name))

            # Extract the action construct type
            if self._construct_type is None:
                self._construct_type = topic_builder_type[:-len('Action{}'.format(core_topic_type_token))]
            elif self._construct_type != topic_builder_type[:-len('Action{}'.format(core_topic_type_token))]:
                raise ValueError(" ActionBuilder: Invalid construct type {} for {} - conflicts with {}".format(
                    self._construct_type, self.name, topic_builder_type))

    def extract_metamodel(self):
        """
        Allows the ActionBuilder to create / extract an Action
        instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: Action
        """
        action_metamodel = Action(source='ros_snapshot', name=self.name,
                                  construct_type=self.construct_type,
                                  client_node_names=self.client_node_names,
                                  server_node_names=self.server_node_names,
                                  suffix_names_to_topics=self._extract_suffix_names_to_topic_metamodels())
        return action_metamodel
