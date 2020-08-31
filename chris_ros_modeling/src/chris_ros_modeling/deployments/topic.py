# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Topics and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class Topic(_EntityMetamodel):
    """
    Metamodel for ROS Topics
    """
    yaml_tag = u'!Topic'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: Topic
        """
        self = super(Topic, cls).__new__(cls, **kwargs)
        self.construct_type = None
        self.publisher_node_names = set()
        self.subscriber_node_names = set()
        return self

    def add_to_dot_graph(self, graph):
        """
        Adds the ROS Entity to a DOT Graph

        :param graph: the DOT Graph to add the ROS Entity to
        :type graph: graphviz.Digraph
        """
        topic_dot_name = 'topic-{}'.format(self.name)
        topic_dot_label = self.name
        graph.node(topic_dot_name, topic_dot_label, shape='rectangle', color='red')
        for publisher_node_name in sorted(self.publisher_node_names):
            graph.edge('node-{}'.format(publisher_node_name), topic_dot_name)
        for subscriber_node_name in sorted(self.subscriber_node_names):
            graph.edge(topic_dot_name, 'node-{}'.format(subscriber_node_name))


class TopicBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Topics
    """
    yaml_tag = u'!TopicBank'
    HUMAN_OUTPUT_NAME = 'Topics:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: TopicBank
        """
        return super(TopicBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  Topic(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  Topic
