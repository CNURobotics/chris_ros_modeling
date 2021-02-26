# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Base Remodeler class that holds all of the necessary
and main logic to load the CHRIS and HAROS models and attempt to fill missing
CHRIS model data with HAROS model data, if applicable
"""

from abc import ABCMeta, abstractmethod
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class _BaseRemodeler(object):
    """
    The `_BaseRemodeler` is the Abstract Base Class that provides most of the
    logic necessary to load the CHRIS and HAROS models, determine which HAROS
    models are present in the CHRIS models and merge them (if applicable),
    determine which HAROS models are not present in the CHRIS models and create
    them (if applicable)
    """
    _metaclass__ = ABCMeta
    TYPE = ''
    REMODELER_SOURCE_NAME = 'haros_chris_model_merger'

    def __init__(self, haros_configuration, chris_ros_model):
        """
        Creates a new `_BaseRemodeler` instance

        :param haros_configuration: HAROS configuration containing all models
        :type haros_configuration: Configuration
        :param chris_ros_model: CHRIS bank containing specific type of models
        :type chris_ros_model: *Bank
        """
        self._haros_configuration = haros_configuration
        self._chris_ros_model = chris_ros_model

    @staticmethod
    def _adjust_haros_name(haros_name):
        """
        Adjusts the HAROS string name; does nothing unless if overridden

        :param haros_name: the HAROS name
        :type haros_name: str
        :return: the modified HAROS name
        :rtype: str
        """
        return haros_name

    def _check_haros_name_is_complete(self, haros_name, context=''):
        """
        Check if the HAROS name does not hint at an incomplete model (does not
        contain `?` as the last token if it contains `/` or is not `?`)

        :param haros_name: the HAROS string name to check
        :type haros_name: str
        :param context: optional context string for logging, defaults to ''
        :type context: str, optional
        :return: boolean to indicate if most likely complete model (`True`)
            or not (`False`)
        :rtype: boolean
        """
        # VALIDATION AND ERROR HANDLING: Handle HAROS Issue where Models may be Incomplete and thus,
        # Have Incomplete Names and Even Types.
        if '/' in haros_name:
            complete = (haros_name.strip().split('/')[-1] != '?')
        else:
            complete = (haros_name.strip() != '?')
        if not complete:
            if context:
                context = '. [In {}]'.format(context)
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] INCOMPLETE HAROS Model Information Encountered for "{}"{}.'.format(
                                    self.__class__.TYPE, haros_name, context))
        return complete

    @property
    @abstractmethod
    def _haros_model_instances(self):
        """
        Abstract Method to return appropriate HAROS Model Instances
        """
        return

    @property
    @abstractmethod
    def _chris_model_banks(self):
        """
        Abstract Method to return appropriate CHRIS Model Bank Instances
        """
        return

    @property
    def _action_model_bank(self):
        """
        Provides easy access to the CHRIS Action Bank

        :return: the CHRIS Action Bank of Action Models
        :rtype: ActionBank
        """
        return self._chris_ros_model[BankType.ACTION]

    def _topic_is_part_of_action(self, topic_name):
        """
        Checks in the CHRIS Action Bank to determine if the provided Topic name
        corresponds to any Actions

        :param topic_name: the string Topic name
        :type topic_name: str
        :return: `True` if the Topic name corresponded to an Action; `False` if not
        :rtype: boolean
        """
        found = False
        topic_name_tokens = topic_name.split('/')
        topic_name_suffix = '/{}'.format(topic_name_tokens[-1])
        topic_name_base = '/'.join(
            topic_name_tokens[0: (len(topic_name_tokens) - 1)])
        action_models = self._action_model_bank.names_to_metamodels
        Logger.get_logger().log(LoggerLevel.DEBUG,
                                '[{}] Searching in CHRIS Action Banks for HAROS Topic Name "{}"...'.format(self.__class__.TYPE, topic_name))
        if (topic_name_base in action_models.keys()):
            topic_model = action_models[topic_name_base]
            found = (topic_name_suffix in topic_model.suffix_names_to_topics.keys())
        Logger.get_logger().log(LoggerLevel.DEBUG, '[{}] Found: "{}"; HAROS Topic Name "{}" in CHRIS Action Banks?'.format(
            self.__class__.TYPE, found, topic_name))
        return found

    @abstractmethod
    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Abstract helper method that handles specific details regarding the
        merging of a specific HAROS model with a specific CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: varies
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: _EntityMetamodel
        """
        return

    def _merge_haros_model_with_chris_model(self, bank_type, haros_instance_name, haros_model, chris_model):
        """
        Method that handles merging of a specific HAROS model with a specific
        CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_instance_name: the string HAROS model instance name
        :type haros_instance_name: str
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: MetamodelObject
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: _EntityMetamodel
        """
        Logger.get_logger().log(LoggerLevel.INFO, '[{}] Merging HAROS Instance with CHRIS Instance "{}".'.format(
            self.__class__.TYPE, haros_instance_name))
        model_updated = self._helper_merge_haros_model_with_chris_model(
            bank_type, haros_model, chris_model)
        self.__class__._update_chris_model_version(chris_model, model_updated)

    @classmethod
    def _update_chris_model_version(cls, chris_model, model_updated):
        """
        Increments the version and updates the source list for the CHRIS model,
        if it has been updated

        :param chris_model: the CHRIS model to update version and source for
        :type chris_model: _EntityMetamodel
        :param model_updated: `True` if model has been updated; `False` if not
        :type model_updated: boolean
        """
        if model_updated:
            chris_model.version = chris_model.version + 1
            new_sources = set()
            if isinstance(chris_model.source, list):
                for source in chris_model.source:
                    new_sources.add(source)
                new_sources.add(cls.REMODELER_SOURCE_NAME)
                chris_model.source = sorted(new_sources)
            elif isinstance(chris_model.source, str):
                for source in chris_model.source.split(','):
                    new_sources.add(source.strip())
                new_sources.add(cls.REMODELER_SOURCE_NAME)
                chris_model.source = ', '.join(sorted(new_sources))
            else:
                Logger.get_logger().log(LoggerLevel.ERROR,
                                        '[{}] Error Setting Source(s) for CHRIS Model "{}".'.format(cls.TYPE, chris_model.name))

    @classmethod
    def _initialize_chris_model_version(cls, chris_model):
        """
        Sets the version to `0` and sets the source list for the CHRIS model,
        since the CHRIS model is considered newly initialized

        :param chris_model: the CHRIS model to set the initial version and
            source for
        :type chris_model: _EntityMetamodel
        """
        chris_model.version = 0
        chris_model.source = cls.REMODELER_SOURCE_NAME

    def remodel(self):
        """
        Main logic to traverse through the appropriate HAROS models, find the
        corresponding CHRIS models from the correct Banks and update each of
        the found models (if applicable), and find the missing CHRIS models
        so that they can be created from the correct Banks and then populated
        (if applicable); performs validation when practical
        """
        for haros_instance in self._haros_model_instances:
            haros_instance_name = haros_instance.id
            haros_instance_name = self.__class__._adjust_haros_name(
                haros_instance_name)
            if self._check_haros_name_is_complete(haros_instance_name, 'Check for Main Model'):
                Logger.get_logger().log(LoggerLevel.INFO, '[{}] Locating CHRIS Instance for "{}".'.format(
                    self.__class__.TYPE, haros_instance_name))
                found = False
                chris_model_banks = self._chris_model_banks
                for chris_model_bank_type in chris_model_banks.keys():
                    chris_model_bank = chris_model_banks[chris_model_bank_type]
                    if haros_instance_name in chris_model_bank.keys:
                        found = True
                        chris_model = chris_model_bank[haros_instance_name]

                        self._merge_haros_model_with_chris_model(
                            chris_model_bank_type, haros_instance_name, haros_instance, chris_model)
                        break # As soon as we find a match

                if not found:
                    # VALIDATION: By Checking for Presence of HAROS Models in CHRIS Model Banks,
                    #             We are Validating the Model Banks.
                    Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Could not find CHRIS Instance for "{}".'.format(
                        self.__class__.TYPE, haros_instance_name))
                    bank_type, new_chris_model_instance = self._create_new_chris_model(
                        haros_instance_name, haros_instance)
                    self._populate_new_chris_model(
                        bank_type, haros_instance_name, haros_instance, new_chris_model_instance)
                    self.__class__._initialize_chris_model_version(
                        new_chris_model_instance)

    def _create_new_chris_model(self, instance_name, haros_instance):
        """
        Creates a new CHRIS model with the instance name and based on the
        corresponding HAROS instance

        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_instance: the corresponding HAROS model
        :type haros_instance: MetamodelObject
        :return: a tuple containing the Bank Type and new CHRIS model
        :rtype: Tuple(BankType, _EntityMetamodel)
        """
        chosen_chris_model_bank_type = self._chris_model_banks.keys()[0]
        Logger.get_logger().log(LoggerLevel.INFO, '[{}] Create new chris model from base_remodeler type={} "{}"...'.format(
            self.__class__.TYPE, chosen_chris_model_bank_type, instance_name))
        return (chosen_chris_model_bank_type, self._chris_model_banks[chosen_chris_model_bank_type][instance_name])

    def _populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Populates the new CHRIS model based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: MetamodelObject
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: _EntityMetamodel
        """
        Logger.get_logger().log(LoggerLevel.INFO, '[{}] Attempting to Populate New Model "{}"...'.format(
            self.__class__.TYPE, instance_name))
        self._helper_populate_new_chris_model(
            bank_type, instance_name, haros_model, new_chris_model_instance)

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new CHRIS model based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: MetamodelObject
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: _EntityMetamodel
        """
        Logger.get_logger().log(LoggerLevel.INFO, '[{}] Not Populating New Model "{}".'.format(
            self.__class__.TYPE, instance_name))
