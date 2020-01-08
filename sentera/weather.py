from enum import Enum
import posixpath

WEATHER_BASE_URL = "https://weather.sentera.com"
WEATHER_HEADER = {'X-API-Key': 'mc049Cu9FJ3lHiQYDYQTd3ZOzsOBt29d2gyi3e0r'}


class WeatherType(Enum):
    Recent = "recent"
    Historical = "historical"
    # Forecast = "forecast"
    # Current = "current"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class WeatherVariable(Enum):
    Temperature = "temperature"
    Humidity = "relative-humidity"
    HighTemperature = "high-temperature"
    LowTemperature = "low-temperature"
    Precipitation = "precipitation"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class WeatherInterval(Enum):
    Hourly = "hourly"
    Daily = "daily"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


TIME_COLUMNS = {WeatherInterval.Hourly: "validTime", WeatherInterval.Daily: "validDate"}
PARAMETER_COMBINATIONS = {
                            WeatherType.Recent:
                            {
                                WeatherInterval.Hourly:
                                    [WeatherVariable.Temperature,
                                     WeatherVariable.Humidity],
                                WeatherInterval.Daily:
                                    [WeatherVariable.HighTemperature,
                                     WeatherVariable.LowTemperature,
                                     WeatherVariable.Precipitation]
                            },
                            WeatherType.Historical:
                            {
                                WeatherInterval.Daily:
                                    [WeatherVariable.HighTemperature,
                                     WeatherVariable.LowTemperature,
                                     WeatherVariable.Precipitation]
                            }
                         }


def build_weather_url(weather_type, weather_variable, weather_interval, lat, long):
    try:
        if weather_variable not in PARAMETER_COMBINATIONS[weather_type][weather_interval]:
            raise KeyError
    except KeyError:
        raise ValueError(f"Parameter combination not allowed: {weather_type}, {weather_variable}, {weather_interval}")

    return posixpath.join(WEATHER_BASE_URL,
                          str(weather_type),
                          f"{weather_interval}-{weather_variable}",
                          str(lat),
                          str(long))


def create_params(weather_type, time_interval):
    param_dict = {}

    if weather_type == WeatherType.Recent:
        param_dict['start'] = time_interval[0]
        param_dict['end'] = time_interval[1]

    if weather_type == WeatherType.Historical:
        param_dict['start'] = "01-01"
        param_dict['end'] = "12-31"
        param_dict['years'] = 10

    return param_dict

