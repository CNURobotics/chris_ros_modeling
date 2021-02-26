# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Module that is responsible for providing the main, driving functions that load the CHRIS models,
load the HAROS models, and then perform a model merge to create a unified, comprehensive model.
"""

import argparse
import pickle
import os
import sys
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import ROSModel
from chris_haros_model_merger.remodelers import *


def get_options(argv):
    """
    Define command line options and handle user input

    :param argv: command line arguments
    :type argv: list
    :return: argparse command line options with values
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(usage='rosrun haros_chris_model_merger model_merger [options]',
                                     description='Tool for Merging HAROS and CHRIS ROS Modeling Metamodels')
    parser.add_argument('-a', '--all', dest='all', default=False,
                        action='store_true', help='output all possible formats')
    parser.add_argument('-t', '--target', dest='target', default='output',
                        type=str, action='store', help='target output directory (default=`output`)')
    parser.add_argument('-r', '--human', dest='human', default=None, type=str,
                        action='store', help='output human readable text format to directory (default=None)')
    parser.add_argument('-y', '--yaml', dest='yaml', default='yaml', type=str,
                        action='store', help='output yaml format to directory (default=`yaml`)')
    parser.add_argument('-p', '--pickle', dest='pickle', default='pickle', type=str,
                        action='store', help='output pickle format to directory (default=`pickle`)')
    parser.add_argument('-g', '--graph', dest='graph', default=None, type=str, action='store',
                        help='output dot format for computation graph to directory (default=`None`)')
    parser.add_argument('-d', '--display', dest='display', default=False, action='store_true',
                        help='display computation graph pdf (default=`False`) (only if output)')
    parser.add_argument('-b', '--base', dest='base', default='ros_model',
                        type=str, action='store', help='output base file name (default=`ros_model`)')
    parser.add_argument('-cm', '--chris_model_input', dest='chris_model_input', default='output/yaml',
                        type=str, action='store', help='CHRIS ROS model input folder (default=`output/yaml`)')
    parser.add_argument('-hm', '--haros_model_input', dest='haros_model_input', default='haros_output', type=str,
                        action='store', help='HAROS ROS model input folder (default=`haros_output`)')
    parser.add_argument('-v', '--version', dest='version', default=False,
                        action='store_true', help='display version information')
    parser.add_argument('-lt', '--logger_threshold', dest='logger_threshold',
                        choices={'ERROR': LoggerLevel.ERROR, 'WARNING': LoggerLevel.WARNING,
                                 'INFO': LoggerLevel.INFO, 'DEBUG': LoggerLevel.DEBUG},
                        default='INFO',
                        help='logger threshold (default=`INFO`)')
    options, _ = parser.parse_known_args(argv)
    if options.all:
        options.human = 'human'
        options.yaml = 'yaml'
        options.pickle = 'pickle'
        options.graph = 'dot_graph'
    return options


def check_for_version_request(options):
    """
    Checks the command line options for a version request; if present and true,
    shows the version and exits; else, does nothing

    :param options: argparse command line options with `version` boolean present
    :type options: argparse.Namespace
    """
    if options.version:
        file_name = os.path.join(os.path.dirname(
            __file__), '..', '..', 'VERSION')
        with open(file_name) as input_file:
            version = input_file.read().strip()
            Logger.get_logger().log(LoggerLevel.INFO,
                                    'chris_haros_model_merger version: {}.'.format(version))
        sys.exit(0)


def main(argv):
    """
    Main method to parse command line options and dispatch on them accordingly
    to load the CHRIS ROS models, HAROS ROS models, perform a merge using the
    remodeler classes, and then write back to the desired model output formats

    :param argv: command line arguments
    :type argv: list
    """
    options = get_options(argv)
    Logger.LEVEL = options.logger_threshold
    check_for_version_request(options)
    Logger.get_logger().log(LoggerLevel.INFO,
                            'Loading HAROS Models from HAROS Database in {}...'.format(options.haros_model_input))
    haros_database = pickle.load(
        open('{}/projects/default/haros.db'.format(options.haros_model_input), 'rb'))
    haros_configuration = haros_database.configurations[0]
    Logger.get_logger().log(LoggerLevel.INFO,
                            'Loading CHRIS Models from Models in {}...'.format(options.chris_model_input))
    chris_ros_model = ROSModel.load_model(options.chris_model_input)
    remodeler_types = [NodeRemodeler, TopicRemodeler, ServiceRemodeler, ParameterRemodeler,
                       NodeSpecificationRemodeler, PackageSpecificationRemodeler, ServiceSpecificationRemodeler]
    for remodeler_type in remodeler_types:
        remodeler = remodeler_type(haros_configuration, chris_ros_model)
        remodeler.remodel()
    if options.yaml:
        chris_ros_model.save_model_yaml_files(
            os.path.join(options.target, options.yaml), options.base)
        chris_ros_model.save_model_yaml_files(
            os.path.join(options.target, options.yaml), options.base)
    if options.pickle:
        chris_ros_model.save_model_pickle_files(
            os.path.join(options.target, options.pickle), options.base)
        chris_ros_model.save_model_pickle_files(
            os.path.join(options.target, options.pickle), options.base)
    if options.human:
        chris_ros_model.save_model_info_files(
            os.path.join(options.target, options.human), options.base)
        chris_ros_model.save_model_info_files(
            os.path.join(options.target, options.human), options.base)
    if options.graph:
        chris_ros_model.save_dot_graph_files(os.path.join(
            options.target, options.graph), options.base, show_graph=options.display)
    Logger.get_logger().log(LoggerLevel.INFO, 'Done.')


if __name__ == '__main__':
    main(sys.argv)
