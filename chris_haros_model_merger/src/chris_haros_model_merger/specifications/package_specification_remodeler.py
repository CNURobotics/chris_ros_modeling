# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Package Specification Remodeler class that holds all of
the specific logic to load the CHRIS and HAROS Package Specification models and
attempt to fill missing CHRIS model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class PackageSpecificationRemodeler(_BaseRemodeler):
    """
    The `PackageSpecificationRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Package Specification
    models, determine which HAROS models are present in the CHRIS models and
    merge them (if applicable), determine which HAROS models are not present
    in the CHRIS models and create them (if applicable)
    """
    TYPE = 'PACKAGE_SPECIFICATION'

    @staticmethod
    def _adjust_haros_name(haros_name):
        """
        Adjusts the HAROS string name to match format of desired Package
        Specification

        :param haros_name: the HAROS name
        :type haros_name: str
        :return: the modified HAROS name
        :rtype: str
        """
        return haros_name.replace('package:', '')

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A set of HAROS Package Specifications
        :rtype: set(Package)
        """
        encountered_haros_package_spec_ids = set()
        haros_package_specs = set()
        for haros_node_instance in self._haros_configuration.nodes:
            haros_package_spec_id = haros_node_instance.node.package.id
            if (haros_package_spec_id not in encountered_haros_package_spec_ids):
                haros_package_specs.add(haros_node_instance.node.package)
                encountered_haros_package_spec_ids.add(haros_package_spec_id)
        return haros_package_specs

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Package Specification Bank Type and Package Specification Model
        :rtype: dict{BankType: PackageSpecification}
        """
        return {BankType.PACKAGE_SPECIFICATION: self._chris_ros_model[BankType.PACKAGE_SPECIFICATION]}

    def _helper_merge_haros_dependencies_with_chris_model(self, haros_model, chris_model):
        """
        Helper merging method to merge the HAROS Package Specification Dependencies
        with the CHRIS Package Specification Dependencies

        :param haros_node_model: the HAROS Package Specification model
        :type haros_node_model: Package
        :param chris_node_model: the CHRIS Package Specification model
        :type chris_node_model: PackageSpecification
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for haros_dependency_name in haros_model.dependencies.packages:
            if self._check_haros_name_is_complete(haros_dependency_name, 'Check for Node Spec Dependency'):
                if haros_dependency_name not in chris_model.dependencies:
                    Logger.get_logger().log(LoggerLevel.INFO, '[{}] Adding HAROS Package Spec\'s Dependency "{}" to CHRIS Package Spec.'.format(
                        self.__class__.TYPE, haros_dependency_name))
                    chris_model.dependencies.append(haros_dependency_name)
                    model_updated = True
        return model_updated

    def _helper_merge_haros_nodes_with_chris_model(self, haros_model, chris_model):
        """
        Helper merging method to merge the HAROS Package Specification Nodes
        with the CHRIS Package Specification Nodes

        :param haros_node_model: the HAROS Package Specification model
        :type haros_node_model: Package
        :param chris_node_model: the CHRIS Package Specification model
        :type chris_node_model: PackageSpecification
        :return: boolean indicating if the model was updated (`True`) or not (`False`)
        :rtype: boolean
        """
        model_updated = False
        for haros_node in haros_model.nodes:
            haros_node_name = haros_node.name
            if self._check_haros_name_is_complete(haros_node_name, 'Check for Package Spec Node'):
                if haros_node_name not in chris_model.nodes:
                    Logger.get_logger().log(LoggerLevel.INFO,
                                            '[{}] Adding HAROS Package Spec\'s Node "{}" to CHRIS Package Spec.'.format(self.__class__.TYPE, haros_node_name))
                    chris_model.dependencies.append(haros_node_name)
                    model_updated = True
        return model_updated

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Package Specification HAROS model with a specific
        Package Specification CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: Package
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: PackageSpecification
        """
        model_updated = False
        haros_package_name = haros_model.name
        # VALIDATE Package Directory Path to Alert the User of INCONSISTENT / INACCURATE DATA.
        haros_directory_path = haros_model.path
        chris_directory_path = chris_model.directory_path
        if (haros_directory_path and (haros_directory_path != chris_directory_path)):
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Package Directory Path "{}" for Package "{}" does NOT Match CHRIS Package Directory Path "{}".'.format(
                self.__class__.TYPE, haros_directory_path, haros_package_name, chris_directory_path))
         # VALIDATE Package Version to Alert the User of INCONSISTENT / INACCURATE DATA.
        haros_version = haros_model.version
        chris_installed_version = chris_model.installed_version
        if (haros_version and (haros_version != chris_installed_version)):
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Package Version "{}" for Package "{}" does NOT Match CHRIS Package Installed Version "{}".'.format(
                self.__class__.TYPE, haros_version, haros_package_name, chris_installed_version))
        # VALIDATE Package Metapackage Status to Alert the User of INCONSISTENT / INACCURATE DATA.
        haros_is_metapackage = haros_model.is_metapackage
        chris_is_metapackage = chris_model.is_metapackage
        if (haros_is_metapackage != chris_is_metapackage):
            Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Package Metapackage Status "{}" for Package "{}" does NOT Match CHRIS Package Metapackage Status "{}".'.format(
                self.__class__.TYPE, haros_is_metapackage, haros_package_name, chris_is_metapackage))
        # VALIDATE Package URL to Alert the User of INCONSISTENT / INACCURATE DATA.
        haros_vcs_url = haros_model.vcs_url
        chris_url = chris_model.url
        if haros_vcs_url:
            if (chris_url and (haros_vcs_url != chris_url)):
                Logger.get_logger().log(LoggerLevel.ERROR, '[{}] HAROS Package URL "{}" for Package "{}" does NOT Match CHRIS Package URL "{}".'.format(
                    self.__class__.TYPE, haros_vcs_url, haros_package_name, chris_url))
            else:
                chris_model.url = haros_vcs_url
                model_updated = True
        model_updated |= self._helper_merge_haros_dependencies_with_chris_model(
            haros_model, chris_model)
        model_updated |= self._helper_merge_haros_nodes_with_chris_model(
            haros_model, chris_model)
        haros_description = haros_model.description
        if (haros_description):
            chris_model.description = haros_description.strip()
            model_updated = True
        return model_updated

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Package Specification CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: Package
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: PackageSpecification
        """
        new_chris_model_instance.directory_path = haros_model.path
        new_chris_model_instance.installed_version = haros_model.version
        new_chris_model_instance.is_metapackage = haros_model.is_metapackage
        new_chris_model_instance.url = haros_model.vcs_url
        # Correct Error (Workaround) Where Metamodel does not Initialize Member `dependencies`
        # with `list`.
        new_chris_model_instance.dependencies = list()
        self._helper_merge_haros_dependencies_with_chris_model(
            haros_model, new_chris_model_instance)
        # Correct Error (Workaround) Where Metamodel does not Initialize Member `nodes`
        # with `list`.
        new_chris_model_instance.nodes = list()
        self._helper_merge_haros_nodes_with_chris_model(
            haros_model, new_chris_model_instance)
        # Prevent Errors in Case if the HAROS Package Description is a `NoneType`.
        haros_description = haros_model.description
        if (haros_description):
            new_chris_model_instance.description = haros_description.strip()
