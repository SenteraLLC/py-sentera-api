import configparser
import os

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

import sentera

environment = os.environ.get('SENTERA_ENV') or 'production'

config_parser = configparser.ConfigParser()
config_str = pkg_resources.read_text(sentera, 'configuration.ini')
config_parser.read_string(config_str)

print(config_parser.sections())
config = config_parser[environment]

def sentera_api_url(path):
  return '{}{}'.format(config['sentera_api_url'], path)
