"""Environment specific configurations."""

import os

ENV_SENTERA_API_URL = "SENTERA_API_URL"
ENV_WEATHER_API_URL = "WEATHER_API_URL"


class Configuration:
    """Class to retrieve configurations from."""

    def __init__(self, environment=None):
        """
        Initialize a configuration object. You can optionally pass in the environment.

        Order precedence for environment:
          environment argument
          SENTERA_ENV environment variable
          defaulting to prod

        :param environment: (optional) The environment you want configuations for.
        :retun: **Configuration instance** - A configuration object for a given environment.
        """
        if environment is None:
            environment = os.environ.get("SENTERA_ENV") or "prod"
            environment = environment.lower()
        self.environment = environment

        if self.environment == "prod":
            self.config = {
                "sentera_api_url": "https://api.sentera.com",
                "weather_api_url": "https://weather.sentera.com",
            }
        else:
            self.config = {
                "sentera_api_url": f"https://api{self.environment}.sentera.com",
                "weather_api_url": f"https://weather{self.environment}.sentera.com",
            }

        if ENV_SENTERA_API_URL in os.environ:
            self.config["sentera_api_url"] = os.environ.get(ENV_SENTERA_API_URL)

        if ENV_WEATHER_API_URL in os.environ:
            self.config["weather_api_url"] = os.environ.get(ENV_WEATHER_API_URL)

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
