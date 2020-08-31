# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
 A model of ROS system deployment as
 banks of metamodel instances
"""

import pickle
from functools import partial
from subprocess import CalledProcessError
from enum import Enum, unique
from graphviz import Digraph
from graphviz.backend import ExecutableNotFound, RequiredArgumentError

import yaml

from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.utilities.utility import create_directory_path, get_input_file_type
from chris_ros_modeling.base_metamodel import _BankMetamodel, _EntityMetamodel

#pylint: disable=unused-import
import chris_ros_modeling.metamodels


@unique
class BankType(Enum):
    """
    Enumerated type for Bank identifiers
    """
    NODE = 1
    NODELET = 2
    NODELET_MANAGER = 3
    TOPIC = 4
    ACTION = 5
    SERVICE = 6
    PARAMETER = 7
    MACHINE = 8
    PACKAGE_SPECIFICATION = 9
    NODE_SPECIFICATION = 10
    MESSAGE_SPECIFICATION = 11
    SERVICE_SPECIFICATION = 12
    ACTION_SPECIFICATION = 13


class ROSModel(object):
    """
    The ROS Model class definition
    """

    SPECIFICATION_TYPES = [BankType.PACKAGE_SPECIFICATION,
                           BankType.NODE_SPECIFICATION,
                           BankType.MESSAGE_SPECIFICATION,
                           BankType.SERVICE_SPECIFICATION,
                           BankType.ACTION_SPECIFICATION]

    DEPLOYMENT_TYPES = [bt for bt in BankType if bt not in SPECIFICATION_TYPES]

    BANK_TYPES_TO_OUTPUT_NAMES = {BankType.NODE: 'node_bank',
                                  BankType.NODELET: 'nodelet_bank',
                                  BankType.NODELET_MANAGER: 'nodelet_manager_bank',
                                  BankType.TOPIC: 'topic_bank',
                                  BankType.ACTION: 'action_bank',
                                  BankType.SERVICE: 'service_bank',
                                  BankType.PARAMETER: 'parameter_bank',
                                  BankType.MACHINE: 'machine_bank',
                                  BankType.PACKAGE_SPECIFICATION: 'package_specification_bank',
                                  BankType.NODE_SPECIFICATION: 'node_specification_bank',
                                  BankType.MESSAGE_SPECIFICATION: 'message_specification_bank',
                                  BankType.SERVICE_SPECIFICATION: 'service_specification_bank',
                                  BankType.ACTION_SPECIFICATION: 'action_specification_bank'}

    def __init__(self, bank_dictionary):
        # @todo - not sure this is best way to construct or store,
        #           but requires the least changes to snapshot for now
        self._bank_dictionary = bank_dictionary
        ROSModel.get_yaml_processor()

    @property
    def keys(self):
        """
        Return keys to model bank dictionary
        """
        return self._bank_dictionary.keys()

    @property
    def items(self):
        """
        Return key, value list of model bank dictionary
        """
        return self._bank_dictionary.items()

    def update_bank(self, bank_type, bank_dictionary):
        """
        Add a new bank data to ROS model
        :param bank_type: a BankType
        :param bank_dictionary: dictionary of name to entity instances
        """

        if bank_type not in BankType:
            raise ValueError("Invalid bank type "+str(bank_type))

        if bank_type not in self._bank_dictionary:
            self._bank_dictionary[bank_type] = {}

        # Validate the inputs
        for key, value in bank_dictionary.items():
            if not isinstance(key, str):
                raise KeyError("ROSModel.update_bank: All keys must be strings - not "+str(type(key)))
            if not isinstance(value, self._bank_dictionary[bank_type].entity_class):
                raise ValueError("ROSModel.update_bank: All values must be {} - not {}".format(
                    self._bank_dictionary[bank_type].entity_class.__name__, value.__class__.__name__))

        # Merge dictionarys
        Logger.get_logger().log(LoggerLevel.INFO, "Update {}".format(self.BANK_TYPES_TO_OUTPUT_NAMES[bank_type]))
        self._bank_dictionary[bank_type].update(bank_dictionary)

    def __getitem__(self, key):
        """
        Get specific instance from key
        :return: bank of metamodel instances from key
        """
        if key not in self._bank_dictionary:
            raise KeyError("Invalid key to bank dictionary ["+str(key)+"]")
        return self._bank_dictionary[key]

    @property
    def node_bank(self):
        """
        :return: node bank
        """
        return self._bank_dictionary[BankType.NODE]

    @property
    def topic_bank(self):
        """
        :return: topic bank
        """
        return self._bank_dictionary[BankType.TOPIC]

    @property
    def action_bank(self):
        """
        :return: action bank
        """
        return self._bank_dictionary[BankType.ACTION]

    @property
    def service_bank(self):
        """
        :return: service bank
        """
        return self._bank_dictionary[BankType.SERVICE]

    @property
    def parameter_bank(self):
        """
        :return: parameter bank
        """
        return self._bank_dictionary[BankType.PARAMETER]

    @property
    def machine_bank(self):
        """
        :return: machine bank
        """
        return self._bank_dictionary[BankType.MACHINE]

    @property
    def message_specification_bank(self):
        """
        :return: message specification bank
        """
        return self._bank_dictionary[BankType.MESSAGE_SPECIFICATION]

    @property
    def service_specification_bank(self):
        """
        :return: service specification bank
        """
        return self._bank_dictionary[BankType.SERVICE_SPECIFICATION]

    @property
    def action_specification_bank(self):
        """
        :return: action specification bank
        """
        return self._bank_dictionary[BankType.ACTION_SPECIFICATION]

    @property
    def package_specification_bank(self):
        """
        :return: package specification bank
        """
        return self._bank_dictionary[BankType.PACKAGE_SPECIFICATION]

    @property
    def node_specification_bank(self):
        """
        :return: node specification bank
        """
        return self._bank_dictionary[BankType.NODE_SPECIFICATION]

    def save_model_info_files(self, directory_path, base_file_name):
        """
        Save the ROS model to human-readable files
        :param directory_path : directory to store files
        :param base_file_name: file name string
        :return:
        """
        try:
            Logger.get_logger().log(LoggerLevel.INFO, 'Saving human-readable files for ROS Computation Graph.')
            create_directory_path(directory_path)
            for bank_type, bank in self._bank_dictionary.items():
                rows = []
                rows.append(str(bank))
                bank_output_name = ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[bank_type]
                file_name = '{}/{}_{}.txt'.format(directory_path, base_file_name, bank_output_name)
                with open(file_name, 'w') as fout:
                    fout.write('\n'.join(rows))

        except IOError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to save human-readable files for ROS Computation Graph.')
            print "     ", ex

    def save_model_yaml_files(self, directory_path, base_file_name):
        """
        Save the ROS bank metamodel instances to yaml files
        :param directory_path : directory to store files
        :param base_file_name:
        :return: None
        """
        try:
            Logger.get_logger().log(LoggerLevel.INFO, 'Saving YAML files for ROS Computation Graph.')
            #  ROSModel.get_yaml_processor()
            create_directory_path(directory_path)
            for bank_type, bank in self._bank_dictionary.items():
                bank_output_name = ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[bank_type]
                file_name = '{}/{}_{}.yaml'.format(directory_path, base_file_name, bank_output_name)
                yaml_file = open(file_name, 'w')
                yaml.dump(bank, yaml_file, sort_keys=True)
                yaml_file.close()
        except IOError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to save YAML files for ROS Computation Graph.')
            print "     ", ex

    def save_model_pickle_files(self, directory_path, base_file_name):
        """
        Save the ROS bank metamodel instances to Pickle files
        :param directory_path : directory to store files
        :param base_file_name:
        :return: None
        """
        try:
            Logger.get_logger().log(LoggerLevel.INFO, 'Saving Pickle files for ROS Model.')
            create_directory_path(directory_path)
            for bank_type, bank in self._bank_dictionary.items():
                bank_output_name = ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[bank_type]
                file_name = '{}/{}_{}.pkl'.format(directory_path, base_file_name, bank_output_name)
                with open(file_name, 'wb') as fout:
                    pickle.dump(bank, fout)
        except IOError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to save Pickle files for ROS Model.')
            print "     ", ex

    def save_dot_graph_files(self, directory_path, file_name, show_graph=True):
        """
        Save the ROS model computation graph to DOT file format
        :param directory_path : directory to store files
        :param file_name: file name of the graph data
        :param show_graph: show output when complete
        :return: None
        """
        try:
            Logger.get_logger().log(LoggerLevel.INFO, 'Saving DOT files for ROS Computation Graph.')
            create_directory_path(directory_path)
            dot_graph = Digraph(comment='ROS Computation Graph',
                                engine='dot',
                                graph_attr={'concentrate': 'true'},
                                directory=directory_path)
            for bank in self._bank_dictionary.values():
                bank.add_to_dot_graph(dot_graph)

            Logger.get_logger().log(LoggerLevel.INFO, 'Render ROS Computation Graph. (show_graph='+str(show_graph)+")")
            dot_graph.render('{}.dot'.format(file_name), view=show_graph, quiet=False)

        except IOError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR,
                                    'Failed to write DOT files for ROS Computation Graph.\n' + \
                                    '    IOError for {}/{}'.format(directory_path, file_name))

        except ExecutableNotFound as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to write DOT files for ROS Computation Graph.\n' + \
                                    '             The Graphviz executable is not found.')

        except CalledProcessError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR,
                                    'Failed to write DOT files for ROS Computation Graph.\n' + \
                                    '             The Graphviz render exit status is non-zero')
            print ex

        except RequiredArgumentError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to write DOT files for ROS Computation Graph.\n' + \
                                    '              renderer is none!')
            raise ex  # This should not happen for valid code on our side

        except ValueError as ex:
            Logger.get_logger().log(LoggerLevel.ERROR,
                                    'Failed to write DOT files for ROS Computation Graph.\n' + \
                                    '             Render engine, format, renderer, or formatter are not known.')
            raise ex  # This should not happen for valid code on our side

    @staticmethod
    def yaml_constructor(yaml_class, loader, node):
        """
        Define a constructor for use when loading yaml files
        """

        if node.id == "mapping":
            value = loader.construct_mapping(node)
        else:
            print "  Not mapping ---"
            print "     "+node.id
            print "         "+str(node.value[0:min(20, len(node.value))])
            # print "    dir(node)", dir(node))
            value = loader.construct_scalar(node)
            print "         "+str(type(value))

        if value is None:
            print "yaml constructor gets value = None for ", yaml_class.__name__, node.id

        elif len(value) > 0:
            # print " Calling constructor for ", yaml_class.__name__
            try:
                return yaml_class(**value)
            except yaml.constructor.ConstructorError as ex:
                print "failed:"
                print node.tag
                print node.id
                print node.value
                raise ex
            except Exception as ex:
                print "failed:"
                print node.tag
                print node.id
                print node.value
                raise ex
        else:
            print value
            print " No data, so don't call constructor for ", yaml_class.__name__

    @staticmethod
    def get_yaml_processor():
        """
        Return YAML handler
        """
        Logger.get_logger().log(LoggerLevel.INFO, " Set up YAML processing for meta models ...")
        for sub_class in _BankMetamodel.__subclasses__():
            #  print "adding representor and constructor for ", sub_class.yaml_tag
            yaml.add_representer(sub_class.yaml_tag, sub_class.__repr__)
            partial_func = partial(ROSModel.yaml_constructor, sub_class)
            yaml.add_constructor(sub_class.yaml_tag, partial_func)

        for sub_class in _EntityMetamodel.__subclasses__():
            #  print "adding representor and constructor for ", sub_class.yaml_tag
            yaml.add_representer(sub_class.yaml_tag, sub_class.__repr__)
            partial_func = partial(ROSModel.yaml_constructor, sub_class)
            yaml.add_constructor(sub_class.yaml_tag, partial_func)

    @staticmethod
    def read_model_from_yaml(directory_path, base_file_name, spec_only=False):
        """
        Read model banks from directory containing YAML files
        :param directory_path: file path to YAML files
        :param base_file_name: base file name used in YAML files
        :return : instance of ROSModel
        """

        bank_dict = {}
        Logger.get_logger().log(LoggerLevel.INFO, 'Reading ROS model from yaml files ...')
        #  ROSModel.get_yaml_processor()
        for bank_type, bank_output_name in ROSModel.BANK_TYPES_TO_OUTPUT_NAMES.items():
            if spec_only and bank_type not in ROSModel.SPECIFICATION_TYPES:
                # print "Specifications only - skipping ", bank_output_name
                continue

            file_name = '{}/{}_{}.yaml'.format(directory_path, base_file_name, bank_output_name)
            try:
                with open(file_name, 'r') as fin:
                    bank_data = yaml.load(fin, Loader=yaml.FullLoader)
                    bank_dict[bank_type] = bank_data
            except IOError:
                Logger.get_logger().log(LoggerLevel.ERROR,
                                        'Failed to read YAML data for {} : {}'.format(bank_output_name, file_name))

        # Create instance of the model class
        return ROSModel(bank_dict)

    @staticmethod
    def read_model_from_pickle(directory_path, base_file_name, spec_only=False):
        """
        Read model banks from directory containing YAML files
        :param directory_path: file path to YAML files
        :param base_file_name: base file name used in YAML files
        :return : instance of ROSModel
        """
        bank_dict = {}
        Logger.get_logger().log(LoggerLevel.INFO, 'Reading ROS model from pickle files ...')
        #  ROSModel.get_yaml_processor()
        for bank_type, bank_output_name in ROSModel.BANK_TYPES_TO_OUTPUT_NAMES.items():
            if spec_only and bank_type not in ROSModel.SPECIFICATION_TYPES:
                print "Specifications only - skipping ", bank_output_name
                continue

            file_name = '{}/{}_{}.pkl'.format(directory_path, base_file_name, bank_output_name)
            try:
                with open(file_name, 'rb') as fin:
                    bank_data = pickle.load(fin)
                    bank_dict[bank_type] = bank_data
            except IOError:
                Logger.get_logger().log(LoggerLevel.ERROR,
                                        'Failed to read Pickle data for {} : {}'.format(bank_output_name, file_name))

        # Create instance of the model class
        return ROSModel(bank_dict)

    @staticmethod
    def load_model(input_directory, spec_only=False):
        """
        Load  model from folder
        :param input_directory: the input directory pointing to either yaml or pickle files (e.g. output/yaml)
        :return: ROSModel instance with models stored in dictionary by type
        """
        try:
            input_type, input_base_file_name = get_input_file_type(input_directory)
        except IOError:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to deduce type from '+input_directory+' ...')
            print "                                     Did you specify input folder with yaml or pickle files?"
            return None

        if input_type == 'yaml':
            return ROSModel.read_model_from_yaml(input_directory, input_base_file_name, spec_only)
        elif input_type == 'pkl':
            return ROSModel.read_model_from_pickle(input_directory, input_base_file_name, spec_only)
        else:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Unknown ROS model input type from '+input_directory+' ...')
            return None
