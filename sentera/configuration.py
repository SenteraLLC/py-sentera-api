"""Evnironment specific configurations."""

import configparser
import os

import sentera

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


environment = os.environ.get("SENTERA_ENV") or "production"
environment = environment.lower()

config_parser = configparser.ConfigParser()
config_str = pkg_resources.read_text(sentera, "configuration.ini")
config_parser.read_string(config_str)

config = config_parser[environment]


def sentera_api_url(path):
    """
    Return a url to the Sentera API for the path supplied.

    :param path: The path to the weather service endpoint you would like to use.
    :return: **url** - A url to the weather service with the path you provided.
    """
    return "{}{}".format(config["sentera_api_url"], path)


def weather_api_url(path):
    """
    Return a url to the weather service for the path supplied.

    :param path: The path to the weather service endpoint you would like to use.
    :return: **url** - A url to the weather service with the path you provided.
    """
    return "{}{}".format(config["weather_api_url"], path)
