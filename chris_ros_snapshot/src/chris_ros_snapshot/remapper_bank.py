# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Simple class to hold dictionary of name to remapped key

    Use to invert the references from key to data
    Supports a one-to-many re-mapping

"""


class RemapperBank(object):
    """
    Remapper from data to key for various banks
    """
    def __init__(self):
        """
        Instantiates an instance of the RemapperBank
        """
        self._data_to_key_maps = {}

    def __getitem__(self, data_name):
        """
        Returns the appropriate Remapped name
        :param data_name: the key to identify the desired mapping
        :type name: str
        :return: the corresponding string
        """
        return self._data_to_key_maps[data_name]


    @property
    def keys(self):
        """
        :return: the keys for remapper bank
        """
        return self._data_to_key_maps.keys()

    @property
    def items(self):
        """
        :return: the key, value pairs for remapper bank
        """
        return self._data_to_key_maps.items()

    def add_remap(self, data_name, key):
        """
        Adds a remapping from data_name to key

        Supports a one-to-many mapping

        :param data_name: the new key
        :type data_name: str
        :param key: the old key to data
        :type data_name: str
        """
        if data_name not in self._data_to_key_maps or \
           self._data_to_key_maps[data_name] is None:
            # New remap
            self._data_to_key_maps[data_name] = key
        else:
            # remap exists
            if key == self._data_to_key_maps[data_name]:
                return

            if isinstance(self._data_to_key_maps[data_name], list):
                if key not in self._data_to_key_maps[data_name]:
                    print "    Adding ", key, " to existing ", data_name, self._data_to_key_maps[data_name]
                    self._data_to_key_maps[data_name].append(key)
            else:
                print "    Adding ", key, " to existing ", data_name, " as list", self._data_to_key_maps[data_name]
                self._data_to_key_maps[data_name] = [self._data_to_key_maps[data_name]]
                self._data_to_key_maps[data_name].append(key)
