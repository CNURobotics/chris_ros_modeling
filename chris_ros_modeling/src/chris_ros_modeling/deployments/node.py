# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Nodes and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class Node(_EntityMetamodel):
    """
    Metamodel for ROS Nodes
    """
    yaml_tag = u'!Node'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: Node
        """
        self = super(Node, cls).__new__(cls, **kwargs)
        self.node = None
        self.uri = None
        self.executable_name = None
        self.executable_file = None
        self.cmdline = None
        self.num_threads = None
        self.cpu_percent = None
        self.memory_percent = None
        self.memory_info = None
        self.action_servers = dict()
        self.action_clients = dict()
        self.published_topic_names = dict()
        self.subscribed_topic_names = dict()
        self.provided_services = dict()
        self.set_parameter_names = dict()
        self.read_parameter_names = dict()
        return self

    def add_to_dot_graph(self, graph):
        """
        Adds the ROS Entity to a DOT Graph

        :param graph: the DOT Graph to add the ROS Entity to
        :type graph: graphviz.Digraph
        """
        graph.node('node-{}'.format(self.name), self.name, color='blue')

    @staticmethod
    def _add_categorized_topic_information_to_rows_string(rows, topics, status, category):
        """
        Private helper method to add categorized Topic information to a
        collection of rows of strings

        :param rows: the rows of strings to add to
        :type rows: list[str]
        :param topics: the names of Topics to add to the rows
        :type topics: set{str}
        :param status: the status of the Topics (e.g. 'published' or
            'subscribed')
        :type status: str
        :param category: the category to further describe the Topics
        :type category: str
        :return: the same rows, appended to with Topic information
        :rtype: list[str]
        """
        rows.append('        {} {} topics:'.format(status, category))
        for topic in sorted(topics):
            rows.append('            - "{}"'.format(topic))
        return rows




class NodeBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Nodes
    """
    yaml_tag = u'!NodeBank'
    HUMAN_OUTPUT_NAME = 'Nodes:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: NodeBank
        """
        return super(NodeBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  Node(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  Node
