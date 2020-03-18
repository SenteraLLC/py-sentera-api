"""Evnironment specific configurations."""

import configparser
import os

import sentera

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


class Configuration:
    """Class toretrieve configurations from."""

    def __init__(self, environment=None):
        """
        Initialize a configuration object. You can optionally pass in the environment.

        Order precedence for environment:
          environment argument
          SENTERA_ENV environment variable
          defaulting to production

        :param environment: (optional) The environment you want configuations for.
        :retun: **Configuration instance** - A configuration object for a given environment.
        """
        if environment is None:
            environment = os.environ.get("SENTERA_ENV") or "production"
            environment = environment.lower()
        self.environment = environment

        config_parser = configparser.ConfigParser()
        config_str = pkg_resources.read_text(sentera, "configuration.ini")
        config_parser.read_string(config_str)

        self.config = config_parser[environment]

    def sentera_api_url(self, path):
        """
        Return a url to the Sentera API for the path supplied.

        :param path: The path to the weather service endpoint you would like to use.
        :return: **url** - A url to the weather service with the path you provided.
        """
        return "{}{}".format(self.config["sentera_api_url"], path)

    def weather_api_url(self, path):
        """
        Return a url to the weather service for the path supplied.

        :param path: The path to the weather service endpoint you would like to use.
        :return: **url** - A url to the weather service with the path you provided.
        """
        return "{}{}".format(self.config["weather_api_url"], path)
