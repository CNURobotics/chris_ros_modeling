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

import rosgraph

from chris_ros_modeling.metamodels import Parameter
from chris_ros_snapshot.base_builders import _EntityBuilder
from chris_ros_snapshot.ros_utilities import ROSUtilities


class ParameterBuilder(_EntityBuilder):
    """
    Defines a ParameterBuilder, which represents a ROS
    Parameter and is responsible for allowing itself to be
    populated with basic information relevant to a Parameter and then
    further populating itself from that information for the purpose
    of extracting a metamodel instance
    """

    def __init__(self, name):
        """
        Instantiates an instance of the ParameterBuilder

        :param name: the name of the Parameter that this
            ParameterBuilder represents
        :type name: str
        """
        super(ParameterBuilder, self).__init__(name)
        self._setting_node_names = set()
        self._reading_node_names = set()

    @property
    def value(self):
        """
        Returns the value of the Parameter

        :return: the value of the Parameter
        :rtype: str
        """
        try:
            value = ROSUtilities.get_ros_utilities().master.getParam(self.name)
            if isinstance(value, str):
                return value.strip()
            return value
        except rosgraph.masterapi.MasterError:  # as ex:
            #error_message = 'Error: {}'.format(str(ex))
            #print error_message
            return None

    @property
    def python_type(self):
        """
        Returns the Python type of the Parameter's value

        :return: the Python type of the Parameter's value
        :rtype: str
        """
        return str(type(self.value)).replace('<', '').replace('>', '').replace('type', '').replace('\'', '').strip()

    @property
    def construct_type(self):
        """
        Returns the type of the Parameter's value

        :return: the Python type of the Parameter's value
        :rtype: str
        """
        return self.python_type

    @property
    def setting_node_names(self):
        """
        Returns the collection of names of the ROS Nodes that have set
        a value for this Parameter

        :return: the collection of names of the ROS Nodes that have set
            a value for this Parameter
        :rtype: set{str}
        """
        return self._setting_node_names

    @property
    def reading_node_names(self):
        """
        Returns the collection of names of the ROS Nodes that have read
        a value for this Parameter

        :return: the collection of names of the ROS Nodes that have read
            a value for this Parameter
        :rtype: set{str}
        """
        return self._reading_node_names

    def add_setting_node_name(self, node_name):
        """
        Associates the name of a ROS Node that has set a value for this
        Parameter with this Parameter

        :param node_name: the name of the ROS Node that has set a value
            for this Parameter
        :type node_name: str
        """
        self._setting_node_names.add(node_name)

    def add_reading_node_name(self, node_name):
        """
        Associates the name of a ROS Node that has read a value for this
        Parameter with this Parameter

        :param node_name: the name of the ROS Node that has read a value
            for this Parameter
        :type node_name: str
        """
        self._reading_node_names.add(node_name)

    def extract_metamodel(self):
        """
        Allows the ParameterBuilder to create / extract a
        Parameter instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: Parameter
        """
        parameter_metamodel = Parameter(source='ros_snapshot',
                                        name=self.name,
                                        python_type=self.python_type,
                                        value=self.value,
                                        setting_node_names=self.setting_node_names,
                                        reading_node_names=self.reading_node_names)
        return parameter_metamodel
