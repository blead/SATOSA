"""
This module contains methods to load, verify and build configurations for the satosa proxy.
"""
import logging
import os

__author__ = 'mathiashedstrom'

LOGGER = logging.getLogger(__name__)


class SATOSAConfig(object):
    """
    A configuration class for the satosa proxy. Verifies that the given config holds all the
    necessary parameters.
    """
    mandatory_dict_keys = ["BASE", "PLUGIN_PATH", "BACKEND_MODULES", "FRONTEND_MODULES",
                           "INTERNAL_ATTRIBUTES", "COOKIE_STATE_NAME", "STATE_ENCRYPTION_KEY"]

    def __init__(self, config):
        """
        Reads a given config and builds the SATOSAConfig.

        :type config: str | dict
        :rtype: satosa.satosa_config.SATOSAConfig

        :param config: Can be a file path, a string (ex. json/yaml), or a dict
        :return: A verified SATOSAConfig
        """
        self.__dict__["_config"] = None
        dict_parsers = [SATOSAConfig._load_dict, SATOSAConfig._load_json, SATOSAConfig._load_yaml]
        for parser in dict_parsers:
            self.__dict__["_config"] = parser(config)
            if self._config is not None:
                break

        self._verify_dict(self._config)
        _internal_attributes = None
        if "INTERNAL_ATTRIBUTES" in self._config:
            internal_attr_file = self._config["INTERNAL_ATTRIBUTES"]
            for parser in dict_parsers:
                _internal_attributes = parser(internal_attr_file)
                if _internal_attributes:
                    break

            self._config["INTERNAL_ATTRIBUTES"] = _internal_attributes
        else:
            self._config["INTERNAL_ATTRIBUTES"] = None

    @staticmethod
    def _verify_dict(conf):
        """
        Raises assertion error if any of the mandatory keys are missing in the conf.

        :type conf: dict
        :rtype: None
        :exception AssertionError

        :param conf: config to verify
        :return: None
        """
        if not (conf is not None and isinstance(conf, dict)):
            msg = "Missing configuration or unknown format"
            LOGGER.critical(msg)
            raise AssertionError(msg)
        for mand_key in SATOSAConfig.mandatory_dict_keys:
            if mand_key not in conf:
                msg = "Missing key '%s' in config" % mand_key
                LOGGER.critical(msg)
                raise AssertionError(msg)

    def __getattr__(self, item):
        """
        Returns data bound to the key 'item'.

        :type item: str
        :rtype object

        :param item: key to data
        :return: data bound to key 'item'
        """
        if self._config is not None and item in self._config:
            return self._config[item]
        raise AttributeError("'module' object has no attribute '%s'" % item)

    def __setattr__(self, key, value):
        """
        Inserts value into internal dict

        :type key: str
        :type value: object

        :param key: key
        :param value: data
        :return: None
        """
        if key != "_config":
            if self._config is not None:
                self._config[key] = value

    def __iter__(self):
        return self._config.__iter__()

    @staticmethod
    def _load_dict(config):
        """
        Load config from dict

        :type config: dict
        :rtype: dict

        :param config: config to load
        :return: Loaded config
        """
        if isinstance(config, dict):
            return config

    @staticmethod
    def _load_json(config):
        """
        Load config from json file or string

        :type config: str
        :rtype: dict

        :param config: config to load. Can be file path or json string
        :return: Loaded config
        """
        try:
            config = SATOSAConfig._readfile(config)
            import json

            return json.loads(config)
        except ValueError as error:  # not a json config
            pass

    @staticmethod
    def _load_yaml(config):
        """
        Load config from yaml file or string

        :type config: str
        :rtype: dict

        :param config: config to load. Can be file path or yaml string
        :return: Loaded config
        """
        try:
            config = SATOSAConfig._readfile(config)
            import yaml
            return yaml.load(config)
        except ImportError:
            LOGGER.warn("No YAML library installed")
        except Exception:
            pass

    @staticmethod
    def _readfile(config):
        """
        Reads a file path and return the data.
        If the path doesn't point to a file, the input will be used as return data.

        :type config: str
        :rtype: str

        :param config: Path to file or config string
        :return: File data
        """
        try:
            if os.path.isfile(config):
                config_file = open(config, "r")
                config = config_file.read()
                config_file.close()
        except Exception:
            pass
        return config
