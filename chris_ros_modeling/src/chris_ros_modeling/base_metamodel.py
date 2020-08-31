# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Base Metamodels used to model ROS Entities and the Banks that
contain them
"""

import inspect
import yaml
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel


class _BankMetamodel(yaml.YAMLObject):
    """
    Internal Base Metamodel for Banks that contain instances of
    ROS Entity Metamodels
    """
    yaml_tag = u''
    HUMAN_OUTPUT_NAME = ''

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the Bank Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed Bank Metamodel
        :rtype: _BankMetamodel
        """
        #pylint: disable=unused-argument
        self = super(_BankMetamodel, cls).__new__(cls)
        self.names_to_metamodels = {}
        return self

    def __init__(self, **kwargs):
        """
        Creates a new instance of the Bank Metamodel using keyword
        arguments (for the purposes of loading from YAML)

        :param kwargs: the keyword arguments to create a new
            Bank Metamodel from
        :type kwargs: dict{str: str}
        :raises KeyError: if the 'names_to_metamodels' key is missing
        """
        if len(kwargs) > 0:
            if 'names_to_metamodels' in kwargs:
                self.__setattr__('names_to_metamodels', kwargs['names_to_metamodels'])
            else:
                error_message = 'BankMetamodel - failed to get names_to_metamodels from kwargs:\n {}'.format(kwargs)
                raise KeyError(error_message)

    def __getitem__(self, name):
        """
        Returns the appropriate entity from the bank;
        instantiates a new entity if one is not already present for
        the name

        :param name: the key to identify the desired entity
        :type name: str
        :return: the matching entity, either newly added or
            retrieved
        :rtype: entity class for bank
        """
        if name not in self.names_to_metamodels:
            self.names_to_metamodels[name] = self._create_entity(name)
        return self.names_to_metamodels[name]

    @property
    def keys(self):
        """
        Return list of keys
        :return: list of entity keys
        """
        return self.names_to_metamodels.keys()

    @property
    def items(self):
        """
        Return list of key,value tuples
        :return: list of key, value tuples
        """
        return self.names_to_metamodels.items()

    def _create_entity(self, name):
        """
        Create instance of named entity given bank type
        :param name: name of entity
        :return: instance of entity type for bank
        """
        #pylint: disable=unused-argument
        return None

    @property
    def entity_class(self, name):
        """
        Class of entity given bank type
        :return: entity class definition for bank type
        """
        #pylint: disable=unused-argument
        #pylint: disable=no-self-use
        return None

    def add_to_dot_graph(self, graph):
        """
        Adds the Bank's internal ROS Entities to a DOT Graph

        :param graph: the DOT Graph to add ROS Entities to
        :type graph: graphviz.Digraph
        """
        for name in sorted(self.names_to_metamodels.keys()):
            self.names_to_metamodels[name].add_to_dot_graph(graph)

    def __str__(self):
        """
        Returns the human-readable string representation of the Bank
        and its internal ROS Entities

        :return: the string representation of the Bank
        :rtype: str
        """
        rows = [self.__class__.HUMAN_OUTPUT_NAME]
        rows.append('-' * (len(rows[0])))
        rows.append('')
        for name in sorted(self.names_to_metamodels.keys()):
            rows.append(str(self.names_to_metamodels[name]))
            rows.append('')
        return '\n'.join(rows)


class _EntityMetamodel(yaml.YAMLObject):
    """
    Internal Base Metamodel for ROS Entities
    """
    yaml_tag = u''

    def __new__(cls, **kwargs):
        """
        Constructs a new instance of the ROS Entity Metamodel from
        keyword arguments

        :param kwargs: the keyword arguments to construct a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: str}
        :return: the constructed ROS Entity Metamodel
        :rtype: _EntityMetamodel
        """
        #pylint: disable=unused-argument
        self = super(_EntityMetamodel, cls).__new__(cls)
        self.name = None
        self.source = None
        self.version = 0

        return self

    def __init__(self, **kwargs):
        """
        Creates a new instance of the ROS Entity Metamodel using
        keyword arguments (for the purposes of loading from YAML)

        :param kwargs: the keyword arguments to create a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: value}
        """
        for key in kwargs:
            self.__setattr__(key, kwargs[key])

    def update_attributes(self, **kwargs):
        """
        Update attributes for entity
        :param kwargs: the keyword arguments to create a new
            ROS Entity Metamodel from
        :type kwargs: dict{str: value}
        """
        for key in kwargs:
            try:
                val = self.__getattribute__(key)
            except AttributeError:
                # Just means we are adding a new attribute
                Logger.get_logger().log(LoggerLevel.WARNING,
                                        'Adding new attribute {} to {} ({}).'.format(
                                            key, self.name, self.__class__.__name__))
                self.__setattr__(key, kwargs[key])
                continue

            # Handle updating an existing attribute
            if val is None:
                self.__setattr__(key, kwargs[key])
            else:
                if val == kwargs[key] and key != "version":
                    # No need to update if same value
                    # unless version, where we increment if updating
                    continue
                elif kwargs[key] is None:
                    # No need to update if None data provided
                    continue
                elif key == "version":
                    if isinstance(val, int):
                        # Increment integer type
                        try:
                            val2 = int(kwargs[key])
                            val = max(val, val2)
                        except:
                            pass
                        self.__setattr__(key, val+1)
                    else:
                        val = str(val)+"_"+str(kwargs[key])
                        self.__setattr__(key, val)
                else:
                    # Update based on specific types
                    if isinstance(val, list):
                        if isinstance(kwargs[key], list):
                            val.extend(kwargs[key])
                        else:
                            if kwargs[key] not in val:
                                val.append(kwargs[key])
                    elif isinstance(val, dict):
                        val.update(kwargs[key])
                    elif isinstance(val, set):
                        val.update(kwargs[key])
                    elif isinstance(val, str):
                        new_list = [val]  # make into a list
                        if isinstance(kwargs[key], list):
                            new_list.extend(kwargs[key])
                        else:
                            if kwargs[key] not in new_list:
                                new_list.append(kwargs[key])
                        self.__setattr__(key, new_list)
                    else:
                        # By default just update the attribute
                        self.__setattr__(key, kwargs[key])

    def add_to_dot_graph(self, graph):
        """
        Adds the ROS Entity to a DOT Graph

        :param graph: the DOT Graph to add the ROS Entity to
        :type graph: graphviz.Digraph
        """
        #pylint: disable=unused-argument
        return

    def _string_rows(self):
        """
        Helper method that a subclass must implement to create the rows
        of strings (one row per line) needed to create the
        human-readable string representation of the ROS Entity

        :return: the rows of strings to represent the ROS Entity
        :rtype: list[str]
        :raises ValueError: if left unimplemented by a subclass
        """

        rows = []

        # Start with common data for all entities
        rows.append('  ' + (len(self.name)+7)*'-')
        rows.append('   {} : {}'.format("name", self.name))
        rows.append('        {} : {}'.format("source", self.source))
        rows.append('        {} : {}'.format("version", self.version))

        # Get all attributes that are not methods, or private ('_') or yaml specific
        for attr, value in inspect.getmembers(self, lambda a: (not inspect.isroutine(a))):
            if not attr.startswith('_') and not attr.startswith('yaml'):
                #print "  getmembers: ", attr, type(value)
                if attr == 'name' or attr == 'source' or attr == 'version':
                    # put common at the top
                    continue

                if isinstance(value, dict):
                    rows.append('        {} :'.format(attr))
                    for key in value:
                        rows.append('            - {} : {}'.format(key, value[key]))
                elif isinstance(value, set) or isinstance(value, list):
                    rows.append('        {} :'.format(attr))
                    for key in value:
                        rows.append('            - {}'.format(key))
                else:
                    rows.append('        {} : {}'.format(attr, value))
        return rows

    def __str__(self):
        """
        Returns the human-readable string representation of the ROS
        Entity

        :return: the string representation of the ROS Entity
        :rtype: str
        """
        return '\n'.join(self._string_rows())
