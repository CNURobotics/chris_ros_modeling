# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module for base EntityBuilder and BankBuilder Classes

These define the basic operations used to extract metamodels in the
chris_ros_modeling format.
"""

from abc import ABCMeta, abstractmethod


class _EntityBuilder(object):
    """
    Abstract Base Class for *EntityBuilders, which represent ROS
    Entities and are responsible for allowing themselves to be
    populated with basic information and then further populating
    themselves from that information for the purpose of extracting
    metamodel instances
    """

    __metaclass__ = ABCMeta

    def __init__(self, name):
        """
        Instantiates an instance of the _EntityBuilder base class

        :param name: the name of the ROS Entity to represent
        :type name: str
        """
        self._name = name
        name_tokens = name.split('/')
        self._name_suffix = '/{}'.format(name_tokens[-1])
        self._name_base = '/'.join(name_tokens[0: (len(name_tokens) - 1)])

    def prepare(self, **kwargs):
        """
        Allows a subclass, if applicable, to prepare its internal state
        for eventual metamodel extraction; internal changes to the state
        of the class instance occur here, if applicable

        :param kwargs: keyword arguments used in the preparation process
        :type kwargs: dict{param: value}
        """
        #pylint: disable=unused-argument
        #pylint: disable=no-self-use
        return

    @property
    def name(self):
        """
        Returns the name of the ROS Entity

        :return: the name of the ROS Entity
        :rtype: str
        """
        return self._name

    @property
    def name_suffix(self):
        """
        Returns the last token of the ROS Entity name; tokens are
        created by splitting the name on forward slashes

        :return: the last token of the ROS Entity name
        :rtype: str
        """
        return self._name_suffix

    @property
    def name_base(self):
        """
        Returns the first token of the ROS Entity name; tokens are
        created by splitting the name on forward slashes

        :return: the first token of the ROS Entity name
        :rtype: str
        """
        return self._name_base

    @abstractmethod
    def extract_metamodel(self):
        """
        Abstract method that allows a subclass to implement its unique
        *EntityMetamodel creation and population functionality to
        create / extract a metamodel instance from its internal state

        :return: the created / extracted metamodel instance
        :rtype: *EntityMetamodel
        """
        return


class _BankBuilder(object):
    """
    Abstract base class for *BankBuilders, which are responsible for
    collecting, maintaining, and populating *EntityBuilders for the
    purpose of extracting metamodel instances
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Instantiates an instance of the _BankBuilder base class
        """
        self._names_to_entity_builders = {}

    def __getitem__(self, name):
        """
        Returns the appropriate *EntityBuilder from the bank;
        instantiates a new builder if one is not already present for
        the name

        :param name: the key to identify the desired *EntityBuilder
        :type name: str
        :return: the matching *EntityBuilder, either newly added or
            retrieved
        :rtype: *EntityBuilder
        """
        if name not in self.names_to_entity_builders:
            entity_builder = self._create_entity_builder(name)
            self.add_entity_builder(entity_builder)
        return self.names_to_entity_builders[name]

    @property
    def items(self):
        """
        Get list of key, builder pairs
        """
        return self.names_to_entity_builders.items()

    @property
    def names_to_entity_builders(self):
        """
        Returns the dictionary of entity names to *EntityBuilders

        :return: the dictionary of entity names to *EntityBuilders
        :rtype: dict{str: *EntityBuilder}
        """
        return self._names_to_entity_builders

    def add_entity_builder(self, entity_builder):
        """
        Adds an *EntityBuilder to the internal store of builders

        :param entity_builder: the *EntityBuilder to add
        :type entity_builder: *EntityBuilder
        """
        self._names_to_entity_builders[entity_builder.name] = entity_builder

    def add_entity_builders(self, entity_builders):
        """
        Adds an iterable collection of *EntityBuilders to the internal
        store of builders

        :param entity_builders: an iterable collection of
            *EntityBuilders to add
        :type entity_builders: list[*EntityBuilder]
        """
        for entity_builder in entity_builders:
            self.add_entity_builder(entity_builder)

    def remove_entity_builder(self, name):
        """
        Removes an *EntityBuilder from the internal store of builders,
        which corresponds to a given name key

        :param name: the key to identify the desired *EntityBuilder to
            remove
        :type name: str
        """
        self._names_to_entity_builders.pop(name)

    @abstractmethod
    def _create_entity_builder(self, name):
        """
        Abstract method that allows subclasses to create and return a
        new *EntityBuilder

        :param name: the name used to instantiate the new *EntityBuilder
        :type name: str
        :return: the newly created *EntityBuilder
        :rtype: *EntityBuilder
        """
        return

    def _gather_filtered_names_to_entity_builders(self):
        """
        Gathers and returns a dictionary of names to filtered
        *EntityBuilders; the filter is based on the class's
        implementation of its filtering method

        :return: a dictionary of names to filtered *EntityBuilders
        :rtype: dict{str: *EntityBuilder}
        """
        filtered_names_to_entity_builders = {}
        for name, entity_builder in self.names_to_entity_builders.items():
            if not self._should_filter_out(name, entity_builder):
                filtered_names_to_entity_builders[name] = entity_builder
        return filtered_names_to_entity_builders

    def _should_filter_out(self, name, entity_builder):
        """
        Indicates whether a given *EntityBuilder (which has a name to
        identify it) should be filtered out or not; unless implemented
        by a subclass, this method always returns False

        :param name: the name to identify the *EntityBuilder
        :type name: str
        :param entity_builder: the *EntityBuilder to check
        :type entity_builder: *EntityBuilder
        :return: True if the *EntityBuilder should be filtered out;
            False if not
        :rtype: bool
        """
        #pylint: disable=unused-argument
        #pylint: disable=no-self-use
        return False

    def prepare(self, **kwargs):
        """
        Prepares the internal *EntityBuilders for eventual metamodel
        extraction; internal changes to the state of the *EntityBuilders
        occur for the builders that are stored in the internal bank

        :param kwargs: keyword arguments needed by the underlying
            *EntityBuilders used in the preparation process
        :type kwargs: dict{param: value}
        """
        self._names_to_entity_builders = self._gather_filtered_names_to_entity_builders()
        for name in self.names_to_entity_builders:
            self.names_to_entity_builders[name].prepare(**kwargs)
        self._post_prepare()

    def _post_prepare(self):
        """
        Allows an implementing subclass to either wrap up or begin a
        new set of tasking necessary for eventual metamodel population
        """
        #pylint: disable=unused-argument
        #pylint: disable=no-self-use
        return

    @abstractmethod
    def _create_bank_metamodel(self):
        """
        Abstract method that allows subclasses to create and return
        their appropriate *BankMetamodel

        :return: the appropriate, newly created *BankMetamodel instance
        :rtype: *BankMetamodel
        """
        return

    @property
    def _names_to_entity_builder_metamodels(self):
        """
        Helper method to return a dictionary of names to extracted
        *Metamodel instances from each of their respective
        *EntityBuilder instances in the internal store of
        *EntityBuilders

        :return: a dictionary of names to extracted *Metamodel instances
        :rtype: dict{str: *Metamodel}
        """
        return {name: entity_builder.extract_metamodel() for (name, entity_builder) in self.names_to_entity_builders.items()}

    def extract_metamodel(self):
        """
        Extracts and returns an instance of the *BankMetamodel
        extracted and populated from this builder (built by this
        builder)

        :return: an extracted instance of this builder's *BankMetamodel
        :rtype: *BankMetamodel
        """
        bank_metamodel = self._create_bank_metamodel()
        bank_metamodel.names_to_metamodels = self._names_to_entity_builder_metamodels
        return bank_metamodel
