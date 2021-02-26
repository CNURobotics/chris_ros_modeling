#!/usr/bin/python
# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
 A script to load ROS model from yaml and write all output formats
"""
import argparse
import os
import sys

from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.ros_model import ROSModel

def get_options(argv):
    """
    Get the command line arguments
    :param argv: command line arguments
    """
    parser = argparse.ArgumentParser(usage="rosrun chris_ros_modeling model_loader [options]",
                                     description="Read model and generate output formats")

    #pylint: disable=line-too-long
    #pylint: disable=bad-whitespace
    parser.add_argument("-a", "--all",           dest="all",           default=False, action="store_true",          help="output all possible formats")
    parser.add_argument("-t", "--target",        dest="target",        default="model_output", type=str,action="store", help="target output directory (default='model_output')")
    parser.add_argument("-r", "--human",         dest="human",         default=None, type=str,action="store",  help="output human readable text format to directory (default=None)")
    parser.add_argument("-y", "--yaml",          dest="yaml",          default=None, type=str,action="store",  help="output yaml format to directory (default=None)")
    parser.add_argument("-p", "--pickle",        dest="pickle",        default=None, type=str,action="store",  help="output pickle format to directory (default=None)")
    parser.add_argument("-g", "--graph",         dest="graph",         default=None, type=str,action="store",  help="output dot format for computation graph to directory (default=None)")
    parser.add_argument("-d", "--display",       dest="display",       default=False, action="store_true",          help="display computation graph pdf (default=False) (only if output)")
    parser.add_argument("-i", "--input",         dest="input",         default="output/yaml", type=str,action="store", help="source input folder (default='output/yaml')")
    parser.add_argument("-b", "--base",          dest="base",          default="ros_model", type=str,action="store", help="output base file name (default='ros_model')")
    parser.add_argument("-v", "--version",       dest="version",       default=False, action="store_true",          help="display version information")
    parser.add_argument("-s", "--spec-only",     dest="spec_only",     default=False, action="store_true",          help="load only ROS specifications (default=False)")
    parser.add_argument('-lt', '--logger_threshold', dest='logger_threshold',
                        choices={'ERROR': LoggerLevel.ERROR, 'WARNING': LoggerLevel.WARNING,
                                 'INFO': LoggerLevel.INFO, 'DEBUG': LoggerLevel.DEBUG},
                        default='INFO',
                        help='logger threshold (default=`INFO`)')

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
    Load model from yaml and write output files

    Mainly used to test model files and serve as basis for writing additional tools.

    :return: None
    """
    options = get_options(argv)
    #print "Loaded options ", options
    if options.version:
        file_name = os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")
        with open(file_name) as fin:
            version = fin.read()
        print "chris_ros_modeling version: ", version
        sys.exit(0)

    Logger.LEVEL = options.logger_threshold
    Logger.get_logger().log(LoggerLevel.INFO, 'Read ROS model ...')

    input_directory = options.input
    output_base_directory = options.target

    model = None
    try:
        model = ROSModel.load_model(input_directory, options.spec_only)
    except Exception as ex:
        Logger.get_logger().log(LoggerLevel.ERROR,
                                'Failed to load ROS model input type from '+input_directory+'!\n'+str(ex))



    if model is not None:
        if options.yaml is not None:
            model.save_model_yaml_files(os.path.join(output_base_directory, options.yaml), options.base)

        if options.pickle is not None:
            model.save_model_pickle_files(os.path.join(output_base_directory, options.pickle), options.base)

        if options.human is not None:
            model.save_model_info_files(os.path.join(output_base_directory, options.human), options.base)

        if options.graph is not None:
            model.save_dot_graph_files(os.path.join(output_base_directory, options.graph),
                                       options.base, show_graph=options.display)

        Logger.get_logger().log(LoggerLevel.INFO, 'Finished processing ROS model input!')


if __name__ == '__main__':
    main(sys.argv)
