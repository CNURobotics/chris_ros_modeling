# Software License Agreement (BSD License)
#Copyright (c) 2020
#Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
#Christopher Newport University
#
#All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Utility methods
"""
import os

from chris_ros_modeling.utilities.logger import Logger, LoggerLevel

def create_directory_path(directory_path):
    """
    Create directory path if required
    :param directory_path:
    :return: None
    """
    if not os.path.exists(directory_path):
        Logger.get_logger().log(LoggerLevel.DEBUG, 'Creating directory path {}.'.format(directory_path))
        os.makedirs(directory_path)

def find_common_start(str_a, str_b):
    """
    Find common starting string from two strings
    :param sa: string a
    :param sb: string b
    :return: common substring at beginning of two files
    """
    #https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
    def _iter():
        for char_a, char_b in zip(str_a, str_b):
            if char_a == char_b:
                yield char_a
            else:
                return

    return ''.join(_iter())


def get_input_file_type(directory_path):
    """
    Extract the file type and base file name
    :param directory_path: Location of input files (and only input files)
    :return: input type, base file name
    """
    if not os.path.isdir(directory_path):
        raise IOError("Invalid directory path <" + directory_path + ">")


    onlyfiles = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    if len(onlyfiles) < 1:
        raise IOError("Directory path <" + directory_path + "> does not contain ROS model files.")

    file_base_name, file_type = os.path.splitext(onlyfiles[0])

    for file_name in onlyfiles[1:]:
        file_base, file_ext = os.path.splitext(file_name)

        if file_ext != file_type:
            raise ValueError("Invalid file extension in input <" + \
                                    str(file_name) + ", " + onlyfiles[0] + ">")

        file_base_name = find_common_start(file_base_name, file_base)

    file_base_name = file_base_name[:-1]  # drop the trailing underscore
    file_type = file_type[1:]  # skip the period
    Logger.get_logger().log(LoggerLevel.INFO,
                            '  Found input of type {} with base name {} ...'.format(file_type, file_base_name))

    return file_type, file_base_name
