"""
This package contains functions to construct queries against the various Sentera APIs available.

Current functionality is limited to queries made against the Sentera Weather API, via the ``get_weather`` function
within the ``sentera.api`` moddule. However, in the future this library may be extended to include imagery requests
via the Sentera Tile API. The library may also be extended to allow for basic calculations to be run against
queried data, such as band math on requested imagery.
"""
from sentera import api, auth, weather
from sentera._version import __version__

__all__ = ["__version__", "api", "auth", "weather"]
