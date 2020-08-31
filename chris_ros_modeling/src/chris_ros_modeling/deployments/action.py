# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Metamodels used to model ROS Actions and the Banks that
contain them
"""

from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel


class Action(_EntityMetamodel):
    """
    Metamodel for ROS Actions
    """
    yaml_tag = u'!Action'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: ActionMetamodel
        """
        self = super(Action, cls).__new__(cls, **kwargs)
        self.client_node_names = set()
        self.construct_type = None
        self.server_node_names = set()
        self.suffix_names_to_topics = dict()
        return self

    def _add_graph_node_to_dot_graph(self, action_dot_name, graph):
        """
        Private helper method to add an Action DOT Node to the DOT
        Graph, along with all of its Topic names

        :param action_dot_name: the name of the Action's DOT Node
            to create
        :type action_dot_name: str
        :param graph: the current graph instance to add the Action's
            DOT Node to
        :type graph: graphviz.Digraph
        """
        action_dot_label_rows = ['<']
        action_dot_label_rows.append('<TABLE BORDER="0" CELLBORDER="0">')
        action_dot_label_rows.append('<TR><TD>{}</TD></TR>'.format(self.name))
        action_dot_label_rows.append('<TR><TD>')
        action_dot_label_rows.append('<FONT POINT-SIZE="6">')
        action_dot_label_rows.append('<TABLE CELLBORDER="0" CELLPADDING="0" BGCOLOR="GRAY" COLOR="BLACK">')
        action_dot_label_rows.append('<TR><TD><U>action topics:</U></TD></TR>')
        for topic_suffix_name in sorted(self.suffix_names_to_topics.keys()):
            topic_name = self.suffix_names_to_topics[topic_suffix_name].name
            action_dot_label_rows.append('<TR><TD>{}</TD></TR>'.format(topic_name))
        action_dot_label_rows.append('</TABLE>')
        action_dot_label_rows.append('</FONT>')
        action_dot_label_rows.append('</TD></TR>')
        action_dot_label_rows.append('</TABLE>')
        action_dot_label_rows.append('>')
        action_dot_label = '\n'.join(action_dot_label_rows)
        graph.node(action_dot_name, action_dot_label, shape='rectangle', color='purple')

    def _add_graph_edges_to_dot_graph(self, action_dot_name, graph):
        """
        Adds the DOT Edges between an Action DOT Node and ROS Node DOT
        Nodes based on whether the ROS Nodes are Action Servers or
        Clients for the Action

        :param action_dot_name: the Action's DOT Node name
        :type action_dot_name: str
        :param graph: the current graph instance to add the Action's
            DOT Edges to
        :type graph: graphviz.Digraph
        """
        for client_name in sorted(self.client_node_names):
            graph.edge('node-{}'.format(client_name), action_dot_name, arrowhead="vee",
                       arrowsize="2", weight="1", penwidth="3", color='purple')
        for server_name in sorted(self.server_node_names):
            graph.edge(action_dot_name, 'node-{}'.format(server_name), arrowhead="vee",
                       arrowsize="2", weight="1", penwidth="3", color='purple')

    def add_to_dot_graph(self, graph):
        """
        Adds the ROS Entity to a DOT Graph

        :param graph: the DOT Graph to add the ROS Entity to
        :type graph: graphviz.Digraph
        """
        action_dot_name = 'action-{}'.format(self.name)
        self._add_graph_node_to_dot_graph(action_dot_name, graph)
        self._add_graph_edges_to_dot_graph(action_dot_name, graph)


class ActionBank(_BankMetamodel):
    """
    Metamodel for Bank of ROS Actions
    """
    yaml_tag = u'!ActionBank'
    HUMAN_OUTPUT_NAME = 'Actions:'

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: ActionBankMetamodel
        """
        return super(ActionBank, cls).__new__(cls, **kwargs)

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :return: instance of entity
        """
        return  Action(name=name)

    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: instance of entity class definition
        """
        return  Action
