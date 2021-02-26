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
import stat
import sys
import time

import apt
import rospkg
from catkin.find_in_workspaces import find_in_workspaces  # noqa: E402

from chris_ros_modeling.ros_model import BankType, ROSModel
from chris_ros_modeling.utilities.logger import Logger, LoggerLevel
from chris_ros_modeling.specifications.package_specification import PackageSpecificationBank
from chris_ros_modeling.specifications.node_specification import NodeSpecificationBank
from chris_ros_modeling.specifications.type_specification import TypeSpecificationEnum, TypeSpecificationBank

class PackageModeler(object):
    """
    Class responsible for crawling ROS workspace and extracting
    package specification information
    """

    source_name = "package_modeler"

    def __init__(self):
        """
        Instantiates an instance of the PackageModeler
        """
        self._package_bank = PackageSpecificationBank()
        self._node_bank = NodeSpecificationBank()
        self._action_bank = TypeSpecificationBank()
        self._message_bank = TypeSpecificationBank()
        self._service_bank = TypeSpecificationBank()
        self._ros_model = None
        self._rospack = rospkg.RosPack()
        self._packages = None
        self._package_paths = None
        self._message_paths = None
        self._service_paths = None
        self._action_paths = None

        self._installed_deb_cache = None

        try:
            cache = apt.Cache()
            self._installed_deb_cache = {pkg.name: pkg for pkg in cache if pkg.is_installed}
        except:
            Logger.get_logger().log(LoggerLevel.ERROR,
                                    'Cannot get installed package version (is this Ubuntu?) ...')

    @property
    def node_specification_bank(self):
        """
        Returns the NodeBankBuilder

        :return: the NodeBankBuilder
        :rtype: NodeBankBuilder
        """
        return self._node_bank

    @property
    def message_specification_bank(self):
        """
        Returns the SpecificationBankBuilder for Message Specifications

        :return: the SpecificationBankBuilder for Message Specifications
        :rtype: SpecificationBankBuilder
        """
        return self._message_bank

    @property
    def service_specification_bank(self):
        """
        Returns the SpecificationBankBuilder for Service Specifications

        :return: the SpecificationBankBuilder for Service Specifications
        :rtype: SpecificationBankBuilder
        """
        return self._service_bank

    @property
    def action_specification_bank(self):
        """
        Returns the SpecificationBankBuilder for Action Specifications

        :return: the SpecificationBankBuilder for Action Specifications
        :rtype: SpecificationBankBuilder
        """
        return self._action_bank

    @property
    def package_specification_bank(self):
        """
        Returns the PackageBankBuilder

        :return: the PackageBankBuilder
        :rtype: PackageBankBuilder
        """
        return self._package_bank

    @property
    def ros_model(self):
        """
        Returns the ROSModel instance

        :return: the ROSModel instance, if called after the probe
            method; Otherwise, None
        :rtype: ROSModel
        """
        return self._ros_model

    def crawl(self):
        """
        Crawl the ROS workspace to populate the ROSModel with the
        details of the ROS Packages in workspace

        :return: True if successful; False if failures were encountered
        :rtype: bool
        """
        try:
            Logger.get_logger().log(LoggerLevel.INFO, 'Collect package information ...')
            self._collect_packages()
            Logger.get_logger().log(LoggerLevel.INFO, 'Collect package specifications for each package ...')
            self._collect_package_specs()
            Logger.get_logger().log(LoggerLevel.INFO, 'Construct ROS Model from metamodel instances...')
            self._ros_model = ROSModel({BankType.PACKAGE_SPECIFICATION : self._package_bank,
                                        BankType.NODE_SPECIFICATION : self._node_bank,
                                        BankType.ACTION_SPECIFICATION : self._action_bank,
                                        BankType.MESSAGE_SPECIFICATION : self._message_bank,
                                        BankType.SERVICE_SPECIFICATION : self._service_bank
                                       })
        except socket.error as ex:
            Logger.get_logger().log(LoggerLevel.ERROR, 'Cannot connect to ROS Master: {}.'.format(ex))
            return False
        return True

    def _collect_packages(self):
        """
        Dictionary of packages to location
        """

        # Retrieve the package information
        self._packages = self._rospack.list()

        self._package_paths = {package: self._rospack.get_path(package) for package in self._packages}

        self._message_paths = {package: [os.path.join(self._rospack.get_path(package), 'msg')]
                               for package in self._packages}
        self._service_paths = {package: [os.path.join(self._rospack.get_path(package), 'srv')]
                               for package in self._packages}
        self._action_paths = {package: [os.path.join(self._rospack.get_path(package), 'action')]
                              for package in self._packages}


        for package_name in self._packages:
            try:

                try:
                    path = self._package_paths[package_name]
                except ValueError:
                    path = "UNKNOWN PATH"

                try:
                    package_dependencies = self._rospack.get_depends(package_name)
                except rospkg.common.ResourceNotFound:
                    #pylint: disable=redefined-variable-type
                    package_dependencies = "NO DEPENDENCIES DEFINED"


                installed_version = self._get_installed_version(package_name)

                package = self._package_bank[package_name]
                package.update_attributes(directory_path=path,
                                          dependencies=package_dependencies,
                                          source=PackageModeler.source_name,
                                          installed_version=installed_version)

            except Exception as ex:
                Logger.get_logger().log(LoggerLevel.ERROR,
                                        "Processing {} {} : {}".format(package_name, type(ex), ex))
                raise ex  # kill for now to debug

    def _get_installed_version(self, package_name):
        """
        Get the installed version of package
        """
        if self._installed_deb_cache is None:
            return None

        for key in self._installed_deb_cache:
            if key.endswith(package_name):
                return self._installed_deb_cache[key].installed.version

            # ROS packages use - instead of _, so check those as well
            if key.endswith(package_name.replace("_", "-")):
                return self._installed_deb_cache[key].installed.version

        return "not installed in OS"

    @staticmethod
    def _get_links(full_path):
        """
        All linked pathes associated with file
        :param full_path: initial path string
        :return single path string, or list of path strings
        """

        if os.path.islink(full_path):
            new_path = os.readlink(full_path)

            # Keep following link until we get to a final file
            new_paths = PackageModeler._get_links(new_path)
            if isinstance(new_paths, str):
                return [full_path, new_path]
            else:
                return [full_path].extend(new_paths)
        else:
            # Just return as string if not symbolic link
            return full_path

    def _find_executable_files(self, child_name, full_path, package_name, executable_flags):
        """ Look in this and sub-folders for executable files
        :param child_name: child of parent directory
        :param full_path: path to current file or directory
        :param package_name: where we are looking
        :param executable_flags: flags indicating permission to execute
        :return : List of strings as potential nodes.
        """
        more_node_names = []
        if os.path.isfile(full_path):
            status = os.stat(full_path)
            mode = status.st_mode
            if mode & executable_flags:
                # Found an executable file, assume it is
                # a ROS node, but not validated as one
                file_base, _ = os.path.splitext(child_name)

                more_node_names.append(file_base)  # add to list of nodes

                # Some catkin builds link to .private folder,
                # or installed by version
                full_path = PackageModeler._get_links(full_path)

                # Store node name with package to ensure uniqueness
                ref_name = "/".join([package_name, file_base])
                node = self._node_bank[ref_name]
                node.update_attributes(package=package_name,
                                       file_path=full_path,
                                       source=PackageModeler.source_name)
        elif os.path.isdir(full_path):
            for child_name in os.listdir(full_path):
                new_path = os.path.join(full_path, child_name)
                more_nodes = self._find_executable_files(child_name, new_path, package_name, executable_flags)
                more_node_names.extend(more_nodes)

        return more_node_names


    def _collect_package_specs(self):
        """
        Process each package to extract specifications
        """

        executable_flags = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH

        for package_name in self._package_bank.keys:
            Logger.get_logger().log(LoggerLevel.INFO,
                                    "     Collecting specifications for {}".format(package_name))

            node_names = []  # List to hold all node names for this package
            launch_file_names = []
            action_names = []
            message_names = []
            service_names = []
            parameter_file_names = []

            results = find_in_workspaces(['libexec', 'share'],  # install folders
                                         package_name,          # project
                                         None,
                                         first_matching_workspace_only=True,
                                         first_match_only=False,
                                         considered_paths=[])
            if not results:
                print "No catkin find results "
                continue  # loop to next package name

            for path in results:
                for child_name in os.listdir(path):
                    full_path = os.path.join(path, child_name)
                    if os.path.isfile(full_path):
                        if child_name in ["package.xml", "CMakeLists.txt", "setup.py", "README.md", "CHANGELOG.rst"]:
                            pass
                        else:
                            more_nodes = self._find_executable_files(child_name,
                                                                     full_path,
                                                                     package_name,
                                                                     executable_flags)
                            node_names.extend(more_nodes)
                    elif os.path.isdir(full_path):
                        # search standard sub-folders for specifications
                        if child_name == "action":
                            actions = self._extract_type_specifications(self._action_bank,
                                                                        full_path,
                                                                        TypeSpecificationEnum.ACTION,
                                                                        package_name,
                                                                        [])
                            action_names.extend(actions)
                        elif child_name == "msg":
                            messages = self._extract_type_specifications(self._message_bank,
                                                                         full_path,
                                                                         TypeSpecificationEnum.MSG,
                                                                         package_name,
                                                                         [])
                            message_names.extend(messages)
                        elif child_name == "srv":
                            services = self._extract_type_specifications(self._service_bank,
                                                                         full_path,
                                                                         TypeSpecificationEnum.SRV,
                                                                         package_name,
                                                                         [])
                            service_names.extend(services)
                        elif child_name == "launch":
                            launches = self._find_files_of_type(".launch",
                                                                full_path, package_name, child_name)
                            launch_file_names.extend(launches)

                            launches = self._find_files_of_type(".launch.xml",
                                                                full_path, package_name, child_name)
                            launch_file_names.extend(launches)

                            param = self._find_files_of_type(".yaml",
                                                             full_path, package_name, child_name)
                            parameter_file_names.extend(param)

                        elif child_name == "config":
                            param = self._find_files_of_type(".yaml",
                                                             full_path, package_name, child_name)
                            parameter_file_names.extend(param)
                        elif child_name == "yaml":
                            param = self._find_files_of_type(".yaml",
                                                             full_path, package_name, child_name)
                            parameter_file_names.extend(param)
                        elif "param" in child_name:
                            param = self._find_files_of_type(".yaml",
                                                             full_path, package_name, child_name)
                            parameter_file_names.extend(param)
                        elif child_name == "bin" or child_name == "scripts":
                            more_nodes = self._find_executable_files(child_name,
                                                                     full_path,
                                                                     package_name,
                                                                     executable_flags)
                            node_names.extend(more_nodes)


            # Add the spec names to package model
            self._package_bank[package_name].update_attributes(nodes=node_names,
                                                               actions=action_names,
                                                               messages=message_names,
                                                               services=service_names,
                                                               launch_files=launch_file_names,
                                                               parameter_files=parameter_file_names)


    def _extract_type_specifications(self, spec_bank, full_path, spec_type, package_name, base_name):
        """
        Extract a specification for action, message, or services given path and type
        """
        spec_names = []  # Name of specifications found

        # file_ext includes the . separator
        spec_ext = ".{}".format(spec_type.name.lower())

        for child_name in os.listdir(full_path):
            #print "     ", spec_type, child_name, full_path
            child_path = os.path.join(full_path, child_name)
            if os.path.isfile(child_path):
                file_base, file_ext = os.path.splitext(child_name)

                if file_ext == spec_ext:
                    #  print "         matching file extension for spec!"
                    try:
                        with open(child_path, 'r') as fin:

                            # pre-pend newline for output formatting
                            spec_text = "\n"+fin.read()

                            # Include base_name for sub folder processing
                            ref_name = "/".join(base_name + [file_base])
                            spec_names.append(ref_name)  # add to list of specs per package

                            # Store specification name with package to ensure uniqueness
                            ref_name = "/".join([package_name] + [ref_name])
                            spec = spec_bank[ref_name]
                            spec.update_attributes(construct_type=spec_ext[1:],
                                                   package=package_name,
                                                   file_path=child_path,
                                                   spec=spec_text,
                                                   source=PackageModeler.source_name)
                    except IOError as ex:
                        print " IOError reading spec:", type(ex), ex
                        print "   ", child_path
                    except Exception as ex:
                        print " Unknown error reading spec:", type(ex), ex
                        print "   ", child_path
                        raise ex

            elif os.path.isdir(child_path):
                # Recurse into sub-folders to see if sub-specifications are defined
                sub_specs = self._extract_type_specifications(spec_bank, child_path,
                                                              spec_type, package_name,
                                                              base_name + [child_name])
                spec_names.extend(sub_specs)

        return spec_names

    def _find_files_of_type(self, target_ext, full_path, package_name, sub_folder=''):
        """
        Find all files of given type in folder
        """
        file_names = []
        for child_name in os.listdir(full_path):
            #print "     ", spec_type, child_name, full_path
            child_path = os.path.join(full_path, child_name)
            if os.path.isfile(child_path):
                _, file_ext = os.path.splitext(child_name)

                if file_ext == target_ext:
                    file_names.append(os.path.join(sub_folder, child_name))

            elif os.path.isdir(child_path):
                sub_file_names = self._find_files_of_type(target_ext,
                                                          child_path,
                                                          package_name,
                                                          sub_folder=os.path.join(sub_folder, child_name))
                file_names.extend(sub_file_names)

        return file_names

    def print_statistics(self):
        """
        Print statistics
        """
        print "     --- Specifications ---"
        for bank_type in ROSModel.SPECIFICATION_TYPES:
            bank = self.ros_model[bank_type]
            print "     {:4d}  items in {}".format(len(bank.keys),
                                                   ROSModel.BANK_TYPES_TO_OUTPUT_NAMES[bank_type])


def get_options(argv):
    """
    Get command line options for package modeler
    :param argv: command line arguments
    """
    #pylint: disable=line-too-long
    #pylint: disable=bad-whitespace
    parser = argparse.ArgumentParser(usage="rosrun chris_package_modeler package_modeler [options]",
                                     description="  Probe ROS deployment to retrieve model of available ROS components \n" +\
                                                 "      and create model using chris_ros_modeling metamodels")

    parser.add_argument("-t", "--target",        dest="target",   default="output",    type=str,       action="store", help="target output directory (default='output')")
    parser.add_argument("-r", "--human",         dest="human",    default=None,        type=str,       action="store", help="output human readable text format to directory (default=None)")
    parser.add_argument("-y", "--yaml",          dest="yaml",     default="yaml",      type=str,       action="store", help="output yaml format to directory (default=`yaml`)")
    parser.add_argument("-p", "--pickle",        dest="pickle",   default="pickle",    type=str,       action="store", help="output pickle format to directory (default='pickle')")
    parser.add_argument("-a", "--all",           dest="all",      default=False,       action="store_true", help="output all possible formats")
    parser.add_argument("-b", "--base",          dest="base",     default="ros_model", type=str,       action="store", help="output base file name (default='ros_model')")
    parser.add_argument("-v", "--version",       dest="version",  default=False,       action="store_true", help="display version information")
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

    return options


def main(argv):
    """
    Main method for the ROS Snapshot tool: the driver that sets up and runs all
    of the Logging, Filtering, Probing, and Model creation
    functionality
    """

    options = get_options(argv)
    #print "ros_snapshot: Loaded options ", options
    if options.version:
        file_name = os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")
        with open(file_name) as fin:
            version = fin.read()
        print "chris_package_modeler version: ", version
        print "   NOTE: Check chris_ros_modeling version using model_loader --version"

        sys.exit(0)

    Logger.LEVEL = options.logger_threshold
    Logger.get_logger().log(LoggerLevel.INFO, 'Initializing ROS package modeler...')

    start_time = time.time()
    modeler = PackageModeler()
    if modeler.crawl():

        if options.yaml is not None:
            modeler.ros_model.save_model_yaml_files(os.path.join(options.target, options.yaml), options.base)

        if options.pickle is not None:
            modeler.ros_model.save_model_pickle_files(os.path.join(options.target, options.pickle), options.base)

        if options.human is not None:
            modeler.ros_model.save_model_info_files(os.path.join(options.target, options.human), options.base)

        Logger.get_logger().log(LoggerLevel.INFO,
                                'Finished package modeling in {:.3f} seconds'.format(time.time()-start_time))
        modeler.print_statistics()

    else:
        Logger.get_logger().log(LoggerLevel.ERROR,
                                'Failed to extract specifications for ROS workspace ...')


if __name__ == '__main__':
    main(sys.argv)
