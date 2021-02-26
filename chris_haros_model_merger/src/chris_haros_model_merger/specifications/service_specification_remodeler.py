# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that contains the Service Specification Remodeler class that holds all of
the specific logic to load the CHRIS and HAROS Service Specification models and
attempt to fill missing CHRIS model data with HAROS model data, if applicable
"""

from chris_haros_model_merger.base_remodeler import _BaseRemodeler
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import BankType


class ServiceSpecificationRemodeler(_BaseRemodeler):
    """
    The `ServiceSpecificationRemodeler` is a `_BaseRemodeler` that provides the
    specific logic necessary to load the CHRIS and HAROS Service Specification
    models, determine which HAROS models are present in the CHRIS models and
    merge them (if applicable), determine which HAROS models are not present
    in the CHRIS models and create them (if applicable)
    """
    TYPE = 'SERVICE_SPECIFICATION'

    @property
    def _haros_model_instances(self):
        """
        Returns the appropriate HAROS Model Instances

        :return: A set of HAROS Service Specifications
        :rtype: set(ServicePrimitive)
        """
        encountered_haros_service_spec_ids = set()
        haros_service_specs = set()
        for haros_service_instance in self._haros_configuration.services:
            haros_service_spec = haros_service_instance.server
            # Handle Error Case Where Service Spec was a `NoneType` - from Acceptance Testing
            # with `chris_rrbot_modeling` demo.
            if haros_service_spec:
                haros_service_spec_id = haros_service_spec.type
                if (haros_service_spec_id not in encountered_haros_service_spec_ids):
                    # Add Required Fields to Allow HAROS Primitive to be Used in Remodeler Structure.
                    haros_service_spec.id = haros_service_spec_id
                    haros_service_spec.name = haros_service_spec_id
                    haros_service_specs.add(haros_service_spec)
                    encountered_haros_service_spec_ids.add(haros_service_spec_id)
            else:
                Logger.get_logger().log(LoggerLevel.ERROR, '[{}] Cannot Locate Service Spec for Service "{}".'.format(
                                        self.__class__.TYPE, haros_service_instance.id))
        return haros_service_specs

    @property
    def _chris_model_banks(self):
        """
        Returns the appropriate CHRIS Model Bank Instances

        :return: the Service Specification Bank Type and Service Specification Model
        :rtype: dict{BankType: ServiceSpecification}
        """
        return {BankType.SERVICE_SPECIFICATION: self._chris_ros_model[BankType.SERVICE_SPECIFICATION]}

    def _helper_merge_haros_model_with_chris_model(self, bank_type, haros_model, chris_model):
        """
        Main merging helper method that handles specific details regarding the
        merging of a specific Service Specification HAROS model with a specific
        Service Specification CHRIS model

        :param bank_type: the corresponding CHRIS Model Bank Type
        :type bank_type: BankType
        :param haros_model: the specific HAROS model to obtain data from
        :type haros_model: ServicePrimitive
        :param chris_model: the specific CHRIS Model to merge data into
        :type chris_model: ServiceSpecification
        """
        model_updated = False
        haros_service_name = haros_model.type
        # Note:
        # There appears to be no feasible or even remotely simple method by which to populate a Service Specification
        # since any traversal into a Service Instance, Service Primitive, or any reference to a Node Instance or Node
        # Specification leads to a dead end with regard to obtaining package names, srv files, etc.
        Logger.get_logger().log(LoggerLevel.INFO, '[{}] No Merge is Possible for Service Spec "{}".'.format(
            self.__class__.TYPE, haros_service_name))
        return model_updated

    def _helper_populate_new_chris_model(self, bank_type, instance_name, haros_model, new_chris_model_instance):
        """
        Helper method to help populate the new Service Specification CHRIS model
        based on the corresponding HAROS model

        :param bank_type: the Bank Type used to create the new CHRIS model
        :type bank_type: BankType
        :param instance_name: the HAROS instance name
        :type instance_name: str
        :param haros_model: the corresponding HAROS model
        :type haros_model: ServicePrimitive
        :param new_chris_model_instance: the new CHRIS model to update/populate
        :type new_chris_model_instance: ServiceSpecification
        """
        Logger.get_logger().log(LoggerLevel.INFO, '[{}] No Additional Population is Possible for Service Spec "{}".'.format(
            self.__class__.TYPE, instance_name))
