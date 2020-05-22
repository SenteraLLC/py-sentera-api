"""Environment specific configurations."""

import os

ENVIRONMENT_CONFIGS = {
    "dev": {
        "sentera_api_url": "https://apidev.sentera.com",
        "weather_api_url": "https://weatherdev.sentera.com",
    },
    "prod": {
        "sentera_api_url": "https://api.sentera.com",
        "weather_api_url": "https://weather.sentera.com",
    },
    "staging": {
        "sentera_api_url": "https://apistaging.sentera.com",
        "weather_api_url": "https://weatherstaging.sentera.com",
    },
    "staging2": {
        "sentera_api_url": "https://apistaging2.sentera.com",
        "weather_api_url": "https://weatherstaging2.sentera.com",
    },
    "test": {
        # This environment is intended to be used by tests and is not a real environment.
        "sentera_api_url": "https://apitest.sentera.com",
        "weather_api_url": "https://weathertest.sentera.com",
    },
}


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

        self.config = ENVIRONMENT_CONFIGS[environment]

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
