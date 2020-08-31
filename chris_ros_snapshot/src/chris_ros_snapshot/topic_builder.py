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

from chris_ros_modeling.utilities import filters
from chris_ros_modeling.metamodels import Topic
from chris_ros_snapshot.base_builders import _EntityBuilder


class TopicBuilder(_EntityBuilder):
    """
    Defines a TopicBuilder, which represents a ROS
    Topic and is responsible for allowing itself to be
    populated with basic information relevant to a Topic and then
    further populating itself from that information for the purpose
    of extracting a metamodel instance
    """

    def __init__(self, name):
        """
        Instantiates an instance of the TopicBuilder

        :param name: the name of the Topic that this TopicBuilder
            represents
        :type name: str
        """
        super(TopicBuilder, self).__init__(name)
        self._construct_type = None
        self._node_names = {'published': set(), 'subscribed': set()}

    @property
    def construct_type(self):
        """
        Returns this Topic's ROS type

        :return: this Topic's ROS type
        :rtype: str
        """
        return self._construct_type

    @construct_type.setter
    def construct_type(self, construct_type):
        """
        Sets this Topic's ROS type

        :param construct_type: the Topic's ROS type
        :type construct_type: str
        """
        self._construct_type = construct_type

    @property
    def publisher_node_names(self):
        """
        Returns the names of the ROS Nodes that have Published the Topic

        :return: the names of Publisher ROS Nodes for this Topic
        :rtype: set{str}
        """
        node_filter = filters.NodeFilter.get_filter()
        return set([name for name in self._node_names['published'] if not node_filter.should_filter_out(name)])

    @property
    def subscriber_node_names(self):
        """
        Returns the names of the ROS Nodes that have Subscribed to the
        Topic

        :return: the names of Subscriber ROS Nodes for this Topic
        :rtype: set{str}
        """
        node_filter = filters.NodeFilter.get_filter()
        return set([name for name in self._node_names['subscribed'] if not node_filter.should_filter_out(name)])

    def add_node_name(self, node_name, status):
        """
        Associates this Topic with a ROS Node name, based on whether it
        was Published by or Subscribed to by the ROS Node

        :param node_name: the name of the associated ROS Node
        :type node_name: str
        :param status: the status or relationship ('published' or
            'subscribed') between the Topic and the ROS Node
        :type status: str
        """
        self._node_names[status].add(node_name)

    def extract_metamodel(self):
        """
        Allows the TopicBuilder to create / extract a Topic
        instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: Topic
        """
        topic_metamodel = Topic(source='ros_snapshot',
                                name=self.name,
                                construct_type=self.construct_type,
                                publisher_node_names=self.publisher_node_names,
                                subscriber_node_names=self.subscriber_node_names)
        return topic_metamodel
