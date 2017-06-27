#!/usr/bin/env python
# -*- coding:utf-8 -*-


class ConfigurationReader:
    """
        Class that manages configuration and secret file
    """

    def __init__(self, filename):
        """
        :param filename: configuration file name
        """

        self.confg_file = filename
        self.secret_dict = {}
        # with manages exception automatically
        with open(filename) as _file:
            for line in _file:
                if line[0] == "#":
                    # i'm a comment
                    pass
                else:
                    key, separator, value = line.partition("=")
                    correct_key = (key.strip()).lower()
                    correct_value = ((value.strip("\n")).strip()).strip("'")

                    # save in a dictionary
                    self.secret_dict.update({correct_key: correct_value})

    def __getitem__(self, key):
        """
        Retrun the value that matches the key in input. Throws an exception if does not exist.

        :param key: key to find
        :return: value binded to key
        """

        if key.lower() in self.secret_dict:
            # key exists
            return self.secret_dict[key.lower()]
        else:
            # key does not exist -> exception
            error_msg = "Either set the env variable '{var}' or place it in your {confg_file} file as {var}='VALUE'"
            raise ConfigurationError(error_msg.format(var=key, confg_file=self.confg_file))

    def __setitem__(self, key, value):
        raise InvalidOperationException('Environment Settings are read-only')

    def __delitem__(self, key):
        raise InvalidOperationException('Environment Settings are read-only')


class ConfigurationError(Exception):
    pass


class InvalidOperationException(Exception):
    pass


# Configuration variable "configuration"
conf = ConfigurationReader("conf/configuration.txt")

# Configuration variable "secret"
secret = ConfigurationReader("conf/confsecret.txt")
