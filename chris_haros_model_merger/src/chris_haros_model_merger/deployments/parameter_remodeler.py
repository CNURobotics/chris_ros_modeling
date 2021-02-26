# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Parameter Remodeler class that holds all of the specific
logic to load the CHRIS and HAROS Parameter models and attempt to fill missing CHRIS
model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class ParameterRemodeler(_BaseRemodeler):
    """
    The `ParameterRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Parameter
    Specification models, determine which HAROS models are present in the CHRIS
    models and merge them (if applicable), determine which HAROS models are not
    present in the CHRIS models and create them (if applicable)
    """
    TYPE = 'PARAMETER'

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A collection of HAROS Parameters
        :rtype: ResourceCollection<Parameter>
        """
        return self._haros_configuration.parameters

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Parameter Bank Type and Parameter Model
        :rtype: dict{BankType: Parameter}
        """
        return {BankType.PARAMETER: self._chris_ros_model[BankType.PARAMETER]}

    def _merge_haros_parameter_links_with_chris_parameter_nodes(self, haros_parameter_model, chris_parameter_model):
        """
        Helper merging method to merge the HAROS Parameter Node Links with the
        CHRIS Parameter Nodes

        :param haros_parameter_model: the HAROS Parameter model
        :type haros_parameter_model: Parameter
        :param chris_parameter_model: the CHRIS Parameter model
        :type chris_parameter_model: Parameter
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for link in haros_parameter_model.writes:
            haros_node_instance_name = link.node.id
            if self._check_haros_name_is_complete(haros_node_instance_name, 'Check for Parameter Nodes'):
                if haros_node_instance_name not in chris_parameter_model.setting_node_names:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Param\'s Setting Node "{}" to CHRIS Param Instance.'.format(
                        self.__class__.TYPE, haros_node_instance_name))
                    chris_parameter_model.setting_node_names.add(
                        haros_node_instance_name)
                    model_updated = True
        for link in haros_parameter_model.reads:
            haros_node_instance_name = link.node.id
            if self._check_haros_name_is_complete(haros_node_instance_name, 'Check for Parameter Nodes'):
                if haros_node_instance_name not in chris_parameter_model.reading_node_names:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Param\'s Reading Node "{}" to CHRIS Param Instance.'.format(
                        self.__class__.TYPE, haros_node_instance_name))
                    chris_parameter_model.reading_node_names.add(
                        haros_node_instance_name)
                    model_updated = True
        return model_updated

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Parameter HAROS model with a specific Parameter
        CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: Parameter
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: Parameter
        """
        model_updated = False
        haros_parameter_value = haros_model.value
        chris_parameter_value = chris_model.value
        if haros_parameter_value:
            # VALIDATE Parameter Values and Types to Alert the User of INCONSISTENT / INACCURATE DATA.
            if str(haros_parameter_value).strip() != str(chris_parameter_value).strip():
                Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Params\'s Value "{}" does NOT Match CHRIS Params\'s Value "{}".'.format(
                    self.__class__.TYPE, haros_parameter_value, chris_parameter_value))
            haros_param_python_type = str(type(haros_parameter_value)).replace(
                '<', '').replace('>', '').replace('type', '').replace('\'', '').strip()
            chris_param_python_type = chris_model.python_type
            if haros_param_python_type != chris_param_python_type:
                Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Params\'s Python Type "{}" does NOT Match CHRIS Params\'s Python Type "{}".'.format(
                    self.__class__.TYPE, haros_param_python_type, chris_param_python_type))
        if haros_model.launch:
            chris_model.launch_file = haros_model.launch.path
            model_updated = True
        # Checking here if node_scope is `True`, not if it exists. Following certain decisions in `ros_snapshot`, this
        # field will only be created if it will have a `True` value.
        if haros_model.node_scope:
            chris_model.is_node_scope = haros_model.node_scope
            model_updated = True
        model_updated |= self._merge_haros_parameter_links_with_chris_parameter_nodes(
            haros_model, chris_model)
        return model_updated

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Parameter CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: Parameter
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: Parameter
        """
        haros_parameter_value = haros_model.value
        if haros_parameter_value:
            new_chris_model_instance.value = str(haros_parameter_value).strip()
            haros_param_python_type = str(type(haros_parameter_value)).replace(
                '<', '').replace('>', '').replace('type', '').replace('\'', '').strip()
            new_chris_model_instance.python_type = haros_param_python_type
        # Prevent Errors Grabbing Path if Launch is `NoneType`.
        if haros_model.launch:
            new_chris_model_instance.launch_file = haros_model.launch.path
        # Checking here if node_scope is `True`, not if it exists. Following certain decisions in `ros_snapshot`, this
        # field will only be created if it will have a `True` value.
        if haros_model.node_scope:
            new_chris_model_instance.is_node_scope = haros_model.node_scope
        # Correct Error (Workaround) Where Metamodel is Initialized with `dict`, but we have to work with
        # `ros_snapshot` model instances that already have a `set` in use.
        new_chris_model_instance.setting_node_names = set()
        new_chris_model_instance.reading_node_names = set()
        self._merge_haros_parameter_links_with_chris_parameter_nodes(
            haros_model, new_chris_model_instance)
