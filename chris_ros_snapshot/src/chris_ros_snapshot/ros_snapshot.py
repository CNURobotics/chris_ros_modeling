#!/usr/bin/python
# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
ROS Snapshot Driver: a tool for probing active ROS deployments to
discover the ROS Computation Graph and storing as a chris_ros_modeling model
"""
import argparse
import os
import socket
import sys
import time
import traceback

from chris_ros_snapshot.ros_model_builder import ROSModelBuilder
from chris_ros_modeling.ros_model import ROSModel, BankType
from chris_ros_modeling.utilities import filters
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_snapshot.remapper_bank import RemapperBank
from chris_ros_snapshot.ros_utilities import ROSUtilities

class ROSSnapshot(object):
    """
    Class responsible for discovering the main components in the
    ROS Computation Graph, which is needed to extract a ROSModel
    """

    def __init__(self):
        """
        Instantiates an instance of the ROSSnapshot
        """
        self._master = ROSUtilities.get_ros_utilities().master
        self._ros_model_builder = None
        self._ros_deployment_model = None
        self._ros_specification_model = None
        self.specification_update = False

    @property
    def node_bank(self):
        """
        Returns the NodeBankBuilder

        :return: the NodeBankBuilder
        :rtype: NodeBankBuilder
        """
        return self._ros_model_builder.get_bank_builder(BankType.NODE)

    @property
    def topic_bank(self):
        """
        Returns the TopicBankBuilder

        :return: the TopicBankBuilder
        :rtype: TopicBankBuilder
        """
        return self._ros_model_builder.get_bank_builder(BankType.TOPIC)

    @property
    def action_bank(self):
        """
        Returns the ActionBankBuilder

        :return: the ActionBankBuilder
        :rtype: ActionBankBuilder
        """
        return self._ros_model_builder.get_bank_builder(BankType.ACTION)

    @property
    def service_bank(self):
        """
        Returns the ServiceBankBuilder

        :return: the ServiceBankBuilder
        :rtype: ServiceBankBuilder
        """
        return self._ros_model_builder.get_bank_builder(BankType.SERVICE)

    @property
    def parameter_bank(self):
        """
        Returns the ParameterBankBuilder

        :return: the ParameterBankBuilder
        :rtype: ParameterBankBuilder
        """
        return self._ros_model_builder.get_bank_builder(BankType.PARAMETER)

    @property
    def machine_bank(self):
        """
        Returns the MachineBankBuilder

        :return: the MachineBankBuilder
        :rtype: MachineBankBuilder
        """
        return self._ros_model_builder.get_bank_builder(BankType.MACHINE)

    @property
    def message_specification_bank(self):
        """
        Returns the SpecificationBankBuilder for Message Specifications

         :return: the SpecificationBankBuilder for Message Specifications
         :rtype: SpecificationBankBuilder
        """
        return self._ros_specification_model[BankType.MESSAGE_SPECIFICATION]

    @property
    def service_specification_bank(self):
        """
         Returns the SpecificationBankBuilder for Service Specifications

         :return: the SpecificationBankBuilder for Service Specifications
         :rtype: SpecificationBankBuilder
        """
        return self._ros_specification_model[BankType.SERVICE_SPECIFICATION]

    @property
    def action_specification_bank(self):
        """
        Returns the SpecificationBankBuilder for Action Specifications

        :return: the SpecificationBankBuilder for Action Specifications
        :rtype: SpecificationBankBuilder
        """
        return self._ros_specification_model[BankType.ACTION_SPECIFICATION]

    @property
    def package_specification_bank(self):
        """
        Returns the PackageBankBuilder

        :return: the PackageBankBuilder
        :rtype: PackageBankBuilder
        """
        return self._ros_specification_model[BankType.PACKAGE]

    def load_specifications(self, source_folder):
        """
        Load specifcation model from folder
        :param source_folder: the input folder pointing to either yaml or pickle files
        :return: True if successful, false otherwise
        """

        try:
            self._ros_specification_model = ROSModel.load_model(source_folder, True)
        except Exception as ex:
            print type(ex)
            print ex
            return False

        if self._ros_specification_model is None:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Specification model is None !')
            return False

        missing_spec = False
        for spec_type in ROSModel.SPECIFICATION_TYPES:
            try:
                spec = self._ros_specification_model[spec_type]
                if spec is None or len(spec.keys) < 1:
                    Logger.get_logger().log(LoggerLevel.ERROR,
                                            'Specification model {} is invalid !'.format(ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[spec_type]))
                    missing_spec = True
            except KeyError as ex:
                Logger.get_logger().log(LoggerLevel.ERROR,
                                        'Specification model {} is missing !'.format(ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[spec_type]))
                missing_spec = True

        return not missing_spec

    def snapshot(self):
        """
        Probe the ROS deployment to populate the ROSModel with the
        details of the ROS Computation Graph

        :return: True if successful; False if failures were encountered
        :rtype: bool
        """
        try:
            Logger.get_logger().log(LoggerLevel.INFO, 'Getting system state from ROS Master...')
            state = self._master.getSystemState()
            Logger.get_logger().log(LoggerLevel.INFO, 'Getting topics from ROS Master...')
            self._ros_model_builder = ROSModelBuilder(self._master.getTopicTypes())
            Logger.get_logger().log(LoggerLevel.INFO, 'Collect ROS Computation Graph information...')
            self._collect_rosgraph_info(state)
            Logger.get_logger().log(LoggerLevel.INFO, 'Prepare data banks...')
            self._ros_model_builder.prepare()
            Logger.get_logger().log(LoggerLevel.INFO, 'Validate model data ...')
            self._validate_and_update_models()
            Logger.get_logger().log(LoggerLevel.INFO, 'Construct ROS Model from metamodel instances...')
            self._ros_deployment_model = self._ros_model_builder.extract_model()
        except socket.error as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Cannot connect to ROS Master: {}.'.format(ex))
            return False
        return True


    def _create_spec_remappers(self):
        """
        Create dictionary of remappers between spec banks
        """

        # Build dictionary to allow remapping of information
        remappers = {}

        # node exe to package/node data
        node_spec = self.ros_specification_model[BankType.NODE_SPECIFICATION]
        remappers['node_remapper'] = RemapperBank()

        node_remapper = remappers['node_remapper']
        for _, spec in node_spec.items:
            if isinstance(spec.file_path, list):
                for file_name in spec.file_path:
                    node_remapper.add_remap(file_name, spec.name)
            else:
                node_remapper.add_remap(spec.file_path, spec.name)

        return remappers

    def _validate_and_update_models(self):
        """
        Validate node, topic, service, and action information with specs
        Validate node information if needed
        """
        remappers = self._create_spec_remappers()

        node_remapper = remappers['node_remapper']
        for key, node_builder in self.node_bank.items:
            try:
                if node_builder.is_nodelet:
                    # @todo Validate a standard nodelet
                    print "\n\n skipping validation for nodelet ", key, "\n\n"
                elif node_builder.is_nodelet_manager:
                    # @todo Validate a standard nodelet manager
                    print "\n\n skipping validation for nodelet manager ", key, "\n\n"
                else:
                    # Validate a standard node
                    node_spec = None
                    node_spec_remap = None
                    file_name = node_builder.executable_file
                    if node_builder.executable_name[:6] == "python":
                        # Allow for python, python2, or python3 as executable_name
                        try:
                            file_name = node_builder.executable_cmdline[1]
                        except IndexError:
                            pass

                    try:
                        node_spec_remap = node_remapper[file_name]
                    except KeyError:
                        try:
                            # Last ditch try using plain executable_name
                            node_spec_remap = node_remapper[node_builder.executable_name]
                        except KeyError:
                            pass

                    if node_spec_remap is not None:
                        # print "     found node spec ", file_name, node_remapper[file_name]

                        # Update builder with information from specification
                        node_builder.set_node_name(node_spec_remap)

                        try:
                            # Match up the spec info
                            node_spec = self._ros_specification_model[BankType.NODE_SPECIFICATION][node_spec_remap]
                            if node_spec.validated:
                                # Node is identified as valid, so let's try to match up
                                self._validate_node_builder(key, node_builder, node_spec)
                            else:
                                # Node has not been validated, so get spec info from this node
                                self._update_node_specification(node_spec, node_builder)

                        except KeyError as ex:
                            raise ex
                        except Exception as ex:
                            Logger.get_logger().log(LoggerLevel.ERROR, '   Failed to validate node {}  {}  !'.format(key, node_spec_remap))
                            print type(ex)
                            print ex
                            track = traceback.format_exc()
                            print track
                            sys.exit(-1) # debug
                    else:
                        Logger.get_logger().log(LoggerLevel.ERROR, '   Unkown node {} executable {} . Skip validation !'.format(key, file_name))
            except Exception as ex:
                Logger.get_logger().log(LoggerLevel.ERROR, '   Failed to process node {}  {}  !'.format(key, file_name))
                print type(ex)
                print ex
                track = traceback.format_exc()
                print track
                sys.exit(-1) # debug

    @staticmethod
    def _match_token_types(node_name, io_names, io_builders, spec_types):
        """
        Look for matched tokens and/or data types between node and spec
        :param node_name:
        :param io_names: relevant names to process (dict)
        :param io_builders: builder for relevant type
        :param spec_types: corresponding data in specification
        :return: True if all valid, False otherwise
        """
        try:
            if spec_types is None:
                if len(io_names) > 0:
                    # Nothing defined for spec
                    return False
            else:
                # We have action clients to match up in the spec
                available_tokens = set(spec_types)
                io_is_valid = True
                for io_name in sorted(io_names):
                    builder = io_builders[io_name]
                    io_type = builder.construct_type
                    token = io_name.split("/")[-1]

                    if token not in available_tokens or io_type != spec_types[token]:
                        # look from matching item remaining tokens

                        # prefer substring match
                        potential = set([ss for ss in available_tokens if token in ss])
                        remaining = available_tokens - potential
                        for test in sorted(potential):
                            if spec_types[test] == io_type:
                                # found match
                                io_names[io_name] = test
                                available_tokens.remove(test)
                                break
                        if io_names[io_name] is None:
                            for test in sorted(remaining):
                                if spec_types[test] == io_type:
                                    # found match
                                    io_names[io_name] = test
                                    available_tokens.remove(test)
                                    break
                        if io_names[io_name] is None:
                            # If still None, then no match found
                            Logger.get_logger().log(LoggerLevel.WARNING, '      Node {} unmatched data {} !'.format(node_name, io_name))
                            io_is_valid = False
                    else:
                        # Found valid match
                        io_names[io_name] = token
                        available_tokens.remove(token)

                return io_is_valid

        except Exception as ex:
            print type(ex)
            print ex
            track = traceback.format_exc()
            print track
            sys.exit(-1)

    def _validate_node_builder(self, node_name, node_builder, node_spec):
        """
        See if the node builder data matches the node spec
        :param node_name: name of node in question
        :param node_builder: node builder instance
        :param node_spec: instance of node speciciation
        :return: True if all matches up; false if any mismatches
        """
        node_is_valid = True

        Logger.get_logger().log(LoggerLevel.INFO, ' Validating Node {} ...'.format(node_name))
        # Spec should define more parameters than we either read or write
        if len(node_spec.parameters) < len(node_builder.read_parameter_names):
            Logger.get_logger().log(LoggerLevel.WARNING,
                                    '      Node {} incorrect number of parameters to read ({} vs. {})!'.format(
                                        node_name, len(node_builder.read_parameter_names), len(node_spec.parameters.keys())))
            print "     Spec parameters: \n", node_spec.parameters
            print "     Node read parameters:\n", node_builder.read_parameter_names
            node_is_valid = False

        if len(node_spec.parameters) < len(node_builder.set_parameter_names):
            Logger.get_logger().log(LoggerLevel.WARNING,
                                    '      Node {} incorrect number of parameters to set ({} vs. {})!'.format(
                                        node_name, len(node_builder.set_parameter_names), len(node_spec.parameters.keys())))
            print "     Spec parameters: \n", node_spec.parameters
            print "     Node read parameters:\n", node_builder.set_parameter_names
            node_is_valid = False

        # All parameter names once
        parameters = node_spec.parameters # names to types
        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.read_parameter_names,
                                                                  self._ros_model_builder.get_bank_builder(BankType.PARAMETER),
                                                                  parameters)

        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.set_parameter_names,
                                                                  self._ros_model_builder.get_bank_builder(BankType.PARAMETER),
                                                                  parameters)

        # Do we define the proper action clients
        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.action_clients,
                                                                  self._ros_model_builder.get_bank_builder(BankType.ACTION),
                                                                  node_spec.action_clients)

        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.action_servers,
                                                                  self._ros_model_builder.get_bank_builder(BankType.ACTION),
                                                                  node_spec.action_servers)

        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.published_topic_names,
                                                                  self._ros_model_builder.get_bank_builder(BankType.TOPIC),
                                                                  node_spec.published_topics)

        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.subscribed_topic_names,
                                                                  self._ros_model_builder.get_bank_builder(BankType.TOPIC),
                                                                  node_spec.subscribed_topics)

        node_is_valid = node_is_valid and self._match_token_types(node_name,
                                                                  node_builder.service_names_with_remap,
                                                                  self._ros_model_builder.get_bank_builder(BankType.SERVICE),
                                                                  node_spec.services_provided)

        return node_is_valid

    @staticmethod
    def _update_node_specification_data(spec_data, builder_data, item_builders):
        """
        Update node spec data from deployed node if unvalidated spec
        :param spec_data: specification dictionary (name:type)
        :param builder_data: data from node builder
        :param item_builders: builder list for type
        """
        token_map = {name:0 for name in spec_data}
        for spec_name in sorted(builder_data):
            builder = item_builders[spec_name]
            spec_type = builder.construct_type
            spec_token = spec_name.split("/")[-1]

            if spec_token in spec_data:
                # Just store as string unless multiple
                token_map[spec_token] += 1
                spec_token += "_" + str(token_map[spec_token])
            else:
                token_map[spec_token] = 0

            spec_data[spec_token] = spec_type
            builder_data[spec_name] = spec_token


    def _update_node_specification(self, node_spec, node_builder):
        """
        Add details to node specification based on the first deployed node of that type
        :param node_builder: node builder instance
        :param node_spec: instance of node speciciation
        :return: True if all matches up; false if any mismatches
        """
        assert not node_spec.validated
        self.specification_update = True

        # Parameters (merge read and set into single dictionary)
        parameters = node_spec.parameters # names to types
        if parameters is None:
            parameters = {}
        self._update_node_specification_data(parameters, node_builder.read_parameter_names,
                                             self._ros_model_builder.get_bank_builder(BankType.PARAMETER))

        set_parameters = node_spec.parameters # names to types
        if set_parameters is None:
            set_parameters = {}
        self._update_node_specification_data(set_parameters, node_builder.set_parameter_names,
                                             self._ros_model_builder.get_bank_builder(BankType.PARAMETER))
        parameters.update(set_parameters)

        action_clients = node_spec.action_clients
        if action_clients is None:
            action_clients = {}
        self._update_node_specification_data(action_clients, node_builder.action_clients,
                                             self._ros_model_builder.get_bank_builder(BankType.ACTION))

        action_servers = node_spec.action_servers
        if action_servers is None:
            action_servers = {}
        self._update_node_specification_data(action_servers, node_builder.action_servers,
                                             self._ros_model_builder.get_bank_builder(BankType.ACTION))

        published_topics = node_spec.published_topics
        if published_topics is None:
            published_topics = {}
        self._update_node_specification_data(published_topics, node_builder.published_topic_names,
                                             self._ros_model_builder.get_bank_builder(BankType.TOPIC))

        subscribed_topics = node_spec.subscribed_topics
        if subscribed_topics is None:
            subscribed_topics = {}
        self._update_node_specification_data(subscribed_topics, node_builder.subscribed_topic_names,
                                             self._ros_model_builder.get_bank_builder(BankType.TOPIC))

        services_provided = node_spec.services_provided
        if services_provided is None:
            services_provided = {}
        self._update_node_specification_data(services_provided, node_builder.service_names_with_remap,
                                             self._ros_model_builder.get_bank_builder(BankType.SERVICE))

        # Update the specification to include I/O data
        node_spec.update_attributes(validated=True,
                                    source='ros_snapshot',
                                    parameters=parameters,
                                    action_clients=action_clients,
                                    action_servers=action_servers,
                                    published_topics=published_topics,
                                    subscribed_topics=subscribed_topics,
                                    services_provided=services_provided,
                                    version=0) # Version triggers increment
        assert node_spec.validated

    @property
    def ros_deployment_model(self):
        """
        Returns the ROSModel instance of deployment models

        :return: the ROSModel instance, if called after the snapshot
            method; Otherwise, None
        :rtype: ROSModel
        """
        return self._ros_deployment_model

    @property
    def ros_specification_model(self):
        """
        Returns the ROSModel instance of specifications

        :return: the ROSModel instance, if called after the snapshot
            method; Otherwise, None
        :rtype: ROSModel
        """
        return self._ros_specification_model

    def _collect_rosgraph_info(self, state_information):
        """
        Helper method to populate the internal ROSModelBuilder and its
        BankBuilders with details about the ROS Computation Graph

        :param state_information: The tuple of Published Topic names to
            Node names, Subscribed Topic names to Node names, and
            Service names to Node names
        :type state_information: tuple(dict{str: list[str]}, dict{str: list[str]}, dict{str: list[str]})
        """
        publishers, subscribers, services = state_information
        self._collect_node_info(publishers, subscribers)
        self._collect_services_info(services)
        self._collect_parameters_info()

    def _collect_node_info(self, publishers, subscribers):
        """
        Helper method to collect Publisher and Subscriber Node
        information (including Topic names)

        :param publishers: dictionary of Published Topic names to Node
            names
        :type publishers: dict{str: list[str]}
        :param subscribers: dictionary of Subscribed Topic names to Node
            names
        :type subscribers: dict{str: list[str]}
        """
        self._create_nodes_with_topics(publishers, 'published')
        self._create_nodes_with_topics(subscribers, 'subscribed')

    def _create_nodes_with_topics(self, state_information, status):
        """
        Helper method to create NodeBuilders and TopicBuilders within
        the ROSModelBuilder's NodeBankBuilder and TopicBankBuilder,
        respectively

        :param state_information: Topic names to Node names
        :type state_information: dict{str: list[str]}
        :param status: Identifier to indicate whether data are for
            publishers or subscribers
        :type status: str
        """
        for topic_name, node_names in state_information:
            collected_topic = self.topic_bank[topic_name]
            for node_name in node_names:
                collected_topic.add_node_name(node_name, status)
                self.node_bank[node_name].add_topic_name(topic_name, status, collected_topic.construct_type, None)

    def _collect_services_info(self, state_information):
        """
        Helper method to create NodeBuilders and ServiceBuilders within
        the ROSModelBuilder's NodeBankBuilder and ServiceBankBuilder,
        respectively

        :param state_information: Service names to Node names
        :type state_information: dict{str: list[str]}
        """
        for service_name, service_provider_names in state_information:
            collected_service = self.service_bank[service_name]
            for node_name in service_provider_names:
                collected_service.add_service_provider_node_name(node_name)
                self.node_bank[node_name].add_service_name_and_type(service_name, collected_service.construct_type)

    def _collect_parameters_info(self):
        """
        Helper method to create ParameterBuilders within the
        ROSModelBuilder's ParameterBankBuilder and to map parameters to
        associated NodeBuilders (obtained from the ROS Master API)
        """
        for parameter_name in self._master.getParamNames():
            # Initialize parameter bank for each parameter name
            self.parameter_bank[parameter_name]  # pylint: disable=W0104

        try:
            for parameter_name, node_names in self._master.getParamsToSettingCallers().items():
                for node_name in node_names:
                    if (node_name == '/roslaunch') or (not filters.NodeFilter.get_filter().should_filter_out(node_name)):
                        self.parameter_bank[parameter_name].add_setting_node_name(node_name)
                    if not filters.NodeFilter.get_filter().should_filter_out(node_name):
                        self.node_bank[node_name].add_parameter_name(parameter_name, 'set', None)
            for parameter_name, node_names in self._master.getParamsToReadingCallers().items():
                for node_name in node_names:
                    if (node_name == '/roslaunch') or not filters.NodeFilter.get_filter().should_filter_out(node_name):
                        self.parameter_bank[parameter_name].add_reading_node_name(node_name)
                    if not filters.NodeFilter.get_filter().should_filter_out(node_name):
                        self.node_bank[node_name].add_parameter_name(parameter_name, 'read', None)

        except AttributeError:
            msg = '\n  Standard roscore does NOT provide parameter setting/reading information!\n' + \
                    '     Use custom roscore if desired.\n' + \
                    '     See chris_ros_snapshot README for more info!'

            Logger.get_logger().log(LoggerLevel.WARNING, msg)


    def print_statistics(self):
        """
        Print statistics
        """
        print "     --- Specifications ---"
        for bank_type in ROSModel.SPECIFICATION_TYPES:
            bank = self._ros_specification_model[bank_type]
            print "     {:4d}  items in {}".format(len(bank.keys), ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[bank_type])

        print "     --- Deployment ---"
        for bank_type in ROSModel.DEPLOYMENT_TYPES:
            bank = self._ros_deployment_model[bank_type]
            print "     {:4d} items in {}".format(len(bank.keys), ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[bank_type])

def get_options(argv):
    """
    Handle command line options
    :param argv: command arguments
    """
    #pylint: disable=line-too-long
    #pylint: disable=bad-whitespace
    parser = argparse.ArgumentParser(usage="rosrun chris_ros_snapshot ros_snapshot [options]",
                                     description="Probe ROS deployment to retrieve snap of " +\
                                     "ROS computation graph\n and create model using chris_ros_modeling metamodels")
                                    #,
                                    # formatter=argparse.RawTextHelpFormatter)

    parser.add_argument("-a", "--all",        dest="all",     default=False, action="store_true",          help="output all possible formats")
    parser.add_argument("-t", "--target",     dest="target",  default="output", type=str, action="store", help="target output directory (default='output')")
    parser.add_argument("-r", "--human",      dest="human",   default=None, type=str, action="store",  help="output human readable text format to directory (default=None)")
    parser.add_argument("-y", "--yaml",       dest="yaml",    default="yaml", type=str, action="store",  help="output yaml format to directory (default=`yaml`)")
    parser.add_argument("-p", "--pickle",     dest="pickle",  default="pickle", type=str, action="store",  help="output pickle format to directory (default='pickle')")
    parser.add_argument("-g", "--graph",      dest="graph",   default=None, type=str, action="store",  help="output dot format for computation graph to directory (default=None)")
    parser.add_argument("-d", "--display",    dest="display", default=False, action="store_true",          help="display computation graph pdf (default=False) (only if output)")
    parser.add_argument("-b", "--base",       dest="base",    default="ros_model", type=str, action="store", help="output base file name (default='ros_snapshot')")
    parser.add_argument("-s", "--spec-input", dest="spec",    default="output/yaml", type=str, action="store", help="specification model input folder (default='output/yaml')")
    parser.add_argument("-v", "--version",    dest="version", default=False, action="store_true",          help="display version information")

    options, _ = parser.parse_known_args(argv)

    if options.all:
        if options.human is None:
            options.human = "human"
        if options.yaml is None:
            options.yaml = "yaml"
        if options.pickle is None:
            options.pickle = "pickle"
        if options.graph is None:
            options.graph = "dot_graph"


    return options



def main(argv):
    """
    Main method for the ROS Snapshot tool: the driver that sets up and runs all
    of the Logging, Filtering, Probing, and Model creation
    functionality
    """

    options = get_options(argv)
    # print "ros_snapshot: Loaded options ", options
    # print " argv=", argv

    if options.version:
        file_name = os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")
        with open(file_name) as fin:
            version = fin.read()
        print "chris_ros_snapshot version: ", version
        print "   NOTE: Check chris_ros_modeling version using model_loader --version"

        sys.exit(0)

    Logger.LEVEL = LoggerLevel.INFO
    ROSUtilities.get_ros_utilities('/'+options.base)  # initialize with node name
    filters.NodeFilter.BASE_EXCLUSIONS.add(ROSUtilities.get_ros_utilities().node_name)
    filters.Filter.FILTER_OUT_DEBUG = True
    filters.Filter.FILTER_OUT_TF = False

    start_time = time.time()
    Logger.get_logger().log(LoggerLevel.INFO,
                            'Initializing ROS Snapshot tool {} ...'.format(ROSUtilities.get_ros_utilities().node_name))
    snapshot = ROSSnapshot()

    Logger.get_logger().log(LoggerLevel.INFO, 'Load existing specification model ...')

    if not snapshot.load_specifications(options.spec):
        Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to input existing specification model ...')
        print "     Run chris_package_modeler package_modeler to generate specification model"
        print "        use -s or --spec-input option to set the input folder "
        print "        the input code will detect either yaml or pickle file input."
        sys.exit(-1)
    else:
        if snapshot.snapshot():
            if options.yaml is not None:
                snapshot.ros_deployment_model.save_model_yaml_files(os.path.join(options.target, options.yaml), options.base)
                if snapshot.specification_update:
                    snapshot.ros_specification_model.save_model_yaml_files(os.path.join(options.target, options.yaml), options.base)

            if options.pickle is not None:
                snapshot.ros_deployment_model.save_model_pickle_files(os.path.join(options.target, options.pickle), options.base)
                if snapshot.specification_update:
                    snapshot.ros_specification_model.save_model_pickle_files(os.path.join(options.target, options.pickle), options.base)

            if options.human is not None:
                snapshot.ros_deployment_model.save_model_info_files(os.path.join(options.target, options.human), options.base)
                if snapshot.specification_update:
                    snapshot.ros_specification_model.save_model_info_files(os.path.join(options.target, options.human), options.base)

            if options.graph is not None:
                snapshot.ros_deployment_model.save_dot_graph_files(os.path.join(options.target, options.graph), options.base, show_graph=options.display)

            Logger.get_logger().log(LoggerLevel.INFO, 'Finished snapshot in {:.3f} seconds'.format(time.time()-start_time))
            snapshot.print_statistics()

        else:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Failed to extract model of ROS system ...')


if __name__ == '__main__':
    main(sys.argv)
